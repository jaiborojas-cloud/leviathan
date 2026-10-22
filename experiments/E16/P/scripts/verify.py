#!/usr/bin/env python3
"""Integridad, dominio, familias y reproducción del contraste E16-P."""
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def rows(name):return list(csv.DictReader((ROOT/'results/run_v1'/name).open()))
def main():
    cfg=json.loads((ROOT/'config.json').read_text())
    for name in ['freeze_manifest.csv','implementation_manifest.csv','manifest.csv']:
        for row in csv.DictReader((ROOT/name).open()):assert sha(ROOT/row['path'])==row['sha256'],row['path']
    for name in ['config.json','groups.json','DESIGN_FROZEN.md','freeze_manifest.csv']:
        assert git('show',f'4f9e8e6:experiments/E16/P/{name}')==(ROOT/name).read_bytes(),name
    assert git('show','5a8d52f:experiments/E16/P/implementation_manifest.csv')==(ROOT/'implementation_manifest.csv').read_bytes()
    for p,h in cfg['sources'].items():assert sha(ROOT.parent/p)==h,p
    allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'}
    changed=git('diff','--name-only',cfg['base_commit'],'--').decode().splitlines()
    assert all(p.startswith('experiments/E16/P/') or p in allowed for p in changed),changed
    assert not git('diff',cfg['base_commit'],'--','experiments/T2_A','experiments/E16/O','experiments/E16/N')
    spec=importlib.util.spec_from_file_location('kernel_verify',ROOT/'scripts/kernel.py');k=importlib.util.module_from_spec(spec);spec.loader.exec_module(k)
    # Parameter curves include vertical edges and backtracking; coordinate order is preserved.
    example=np.array([[0.,0.],[.5,.1],[.5,.2],[.4,.1],[1.,0.]])
    assert np.array_equal(k.coords(k.pack(example,'free'),'free',example[:,0]),example)
    fine=k.subdivide(example);assert np.array_equal(fine[::2],example)
    assert np.array_equal(k.coords(k.pack(example,'fixed'),'fixed',example[:,0]),example)
    obj=k.Objective(np.array([1.,1.]),np.array([2.,1.]),'free',np.array([0.,.5,1.]),'sum',np.eye(2),np.zeros((2,2)))
    # Duplicate adjacent endpoint is rejected, with an explicit counter.
    assert np.isinf(obj.fun(np.array([0.,0.]))) and obj.rejections['zero_edge']==1
    vertices=rows('vertices.csv');paths=rows('paths.csv');source=list(csv.DictReader((ROOT.parent/'O/results/run_v1/vertices.csv').open()))
    for lin in ['Q0','Q1','C0']:
        old=sorted([z for z in source if z['lineage']==lin and int(z['round'])==cfg['source_round'][lin]],key=lambda z:int(z['index']))
        base=np.array([[0.,0.]]+[[float(z['t']),float(z['s'])] for z in old]+[[1.,0.]])
        if lin=='C0':base=np.array([item for j in range(len(base)-1) for item in ([base[j],(base[j]+base[j+1])/2] if j<4 else [base[j]])]+[base[-1]])
        assert len(base)==133
        for arm in cfg['arms']:
            for m in cfg['segments']:
                rr=sorted([z for z in vertices if z['lineage']==lin and z['arm']==arm and int(z['segments'])==m],key=lambda z:int(z['index']))
                assert len(rr)==m+1
                zz=np.array([[float(z['t']),float(z['s'])] for z in rr])
                assert np.array_equal(zz[[0,-1]],[[0,0],[1,0]])
                assert np.all((zz[:,0]>=0)&(zz[:,0]<=1)&(abs(zz[:,1])<=.25))
                if arm=='fixed':assert np.array_equal(zz[:,0],(base if m==132 else k.subdivide(base))[:,0])
    for path in paths:
        gradient=[z for z in rows('gradients.csv') if z['path']==path['path']]
        if path['gradient_error']:
            expected=(int(path['segments'])-1)*(1 if path['arm']=='fixed' else 2)
            assert len(gradient)==expected
            assert {z['coordinate'] for z in gradient}==({'s'} if path['arm']=='fixed' else {'t','s'})
    result=ROOT/'results/run_v1';summary=json.loads((result/'summary.json').read_text())
    assert len(paths)==summary['paths']==12 and len(rows('refinements.csv'))==summary['refinements']==6
    assert len(rows('comparisons.csv'))==summary['comparisons']==10
    assert sum(z['status']=='PASS_NUMERICAL' for z in paths)==summary['validated_paths']
    names=[p.name for p in sorted(result.iterdir()) if p.suffix in ['.csv','.json'] and p.name!='resources.json']
    assert len(names)==13
    with tempfile.TemporaryDirectory(prefix='e16p-') as tmp:
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
        subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',tmp],env=env,check=True,timeout=cfg['budget_seconds'])
        for name in names:assert (Path(tmp)/name).read_bytes()==(result/name).read_bytes(),name
        assert json.loads((Path(tmp)/'resources.json').read_text())['within_budget']
    assert json.loads((result/'resources.json').read_text())['within_budget']
    print('PASS_REPRODUCTION: 13 salidas idénticas; congelación, familias, coordenadas, controles y alcance verificados. O/N/T2-A intactos.')
if __name__=='__main__':main()
