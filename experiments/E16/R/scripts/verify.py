#!/usr/bin/env python3
"""Integridad, escalas, KKT físico, costes y reproducción científica de R."""
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
        assert git('show',f'49029d8:experiments/E16/R/{name}')==(ROOT/name).read_bytes(),name
    assert git('show','243e8c6:experiments/E16/R/implementation_manifest.csv')==(ROOT/'implementation_manifest.csv').read_bytes()
    for p,h in cfg['sources'].items():assert sha(ROOT.parent/p)==h,p
    allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'}
    changed=git('diff','--name-only',cfg['base_commit'],'--').decode().splitlines();assert all(p.startswith('experiments/E16/R/') or p in allowed for p in changed),changed
    assert not git('diff',cfg['base_commit'],'--','experiments/T2_A','experiments/E16/Q','experiments/E16/P')
    spec=importlib.util.spec_from_file_location('preconditioner_verify',ROOT/'scripts/preconditioning.py');pc=importlib.util.module_from_spec(spec);spec.loader.exec_module(pc)
    diagonal=np.diag([-4.,0.,16.,256.]);dd,exponent,mu,_=pc.scales_from_hessian(diagonal,cfg)
    assert mu==16. and np.array_equal(exponent,[1,7,0,-2]) and np.array_equal(dd,[2.,128.,1.,.25])
    source=list(csv.DictReader((ROOT.parent/'Q/results/run_v2/paths.csv').open()));refs=rows('source_references.csv')
    for r in refs:
        old=next(z for z in source if z['lineage']==r['lineage'] and z['arm']=='length' and z['segments']=='132')
        assert old['status']==r['source_status'] and old['length']==r['archived_length']
    scales=rows('scales.csv');spectra=rows('spectra.csv');scale_map={}
    for lin in ['Q0','Q1','C0']:
        for m in cfg['segments']:
            ref=f'{lin}/{m}';r=[z for z in scales if z['reference']==ref];assert len(r)==2*(m-1)
            diag=np.array([float(z['diagonal']) for z in r]);absolute=abs(diag);positive=absolute[absolute>0];median=float(np.median(positive)) if len(positive) else 1.
            e=np.clip(np.rint(np.log2(np.sqrt(median/np.maximum(absolute,cfg['preconditioner_floor_relative']*median)))),*cfg['scale_exponent_bounds']).astype(int)
            d=np.exp2(e.astype(float));assert np.array_equal(e,[int(z['exponent']) for z in r]);assert np.array_equal(d,[float(z['scale']) for z in r]);assert all(float(z['median_positive_abs_diagonal'])==median for z in r)
            assert np.all(np.frexp(d)[0]==.5);scale_map[ref]=d
    assert len(spectra)==12
    for r in spectra:assert sum(int(r[k]) for k in ['negative','near_zero','positive'])==int(r['inactive_dimension'])
    paths=rows('paths.csv');vertices=rows('vertices.csv');gradients=rows('gradients.csv');costs=rows('costs.csv')
    for path in paths:
        m=int(path['segments']);rr=sorted([z for z in vertices if z['path']==path['path']],key=lambda z:int(z['index']));assert len(rr)==m+1
        z=np.array([[float(q['t']),float(q['s'])] for q in rr]);assert np.array_equal(z[[0,-1]],[[0,0],[1,0]])
        assert np.all((z[:,0]>=0)&(z[:,0]<=1)&(abs(z[:,1])<=.25))
        gg=[q for q in gradients if q['path']==path['path']];assert len(gg)==2*(m-1)
        assert {q['coordinate'] for q in gg}=={'t','s'}
        gm=np.array([float(q['mp_fd_2']) for q in gg]);gad=np.array([float(q['autograd']) for q in gg]);x=z[1:-1].reshape(-1)
        bounds=np.array([bb for j in range(m-1) for bb in [cfg['t_bounds'],cfg['s_bounds']]],float);normalizer=max(1,abs(float(path['length'])))
        physical=np.max(abs(x-np.clip(x-gm,bounds[:,0],bounds[:,1])))/normalizer
        assert abs(physical-float(path['physical_kkt']))<=1e-12
        d=np.ones_like(x) if path['arm']=='reference' else scale_map[f"{path['lineage']}/{m}"]
        y=x/d;yb=bounds/d[:,None];gy=d*gad;solver=np.max(abs(y-np.clip(y-gy,yb[:,0],yb[:,1])))/normalizer
        assert abs(solver-float(path['solver_kkt']))<=1e-12
        if path['status']=='PASS_NUMERICAL':assert path['success']=='True' and physical<=float(cfg['gradient_tolerance'])
        c=next(q for q in costs if q['path']==path['path']);assert int(c['algorithm_initial_hessians'])==(path['arm']=='scaled')
        assert c['function_evaluations']==path['nfev'] and c['gradient_evaluations']==path['njev'] and c['iterations']==path['iterations']
    out=ROOT/'results/run_v1';s=json.loads((out/'summary.json').read_text());assert s['paths']==len(paths)==12 and s['common_preconditioners']==6
    assert s['validated_paths']==sum(z['status']=='PASS_NUMERICAL' for z in paths);assert len(rows('refinements.csv'))==6 and len(rows('comparisons.csv'))==10
    names=[p.name for p in sorted(out.iterdir()) if p.suffix in ['.csv','.json'] and p.name!='resources.json'];assert len(names)==15
    with tempfile.TemporaryDirectory(prefix='e16r-') as tmp:
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
        subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',tmp],env=env,check=True,timeout=cfg['budget_seconds'])
        for name in names:assert (Path(tmp)/name).read_bytes()==(out/name).read_bytes(),name
        assert json.loads((Path(tmp)/'resources.json').read_text())['within_budget']
    resource=json.loads((out/'resources.json').read_text());assert resource['within_budget']
    assert len(resource['timings']['preparation'])==6 and len(resource['timings']['optimization'])==12
    assert all(z['algorithm_preparation_seconds']==0 for z in resource['timings']['optimization'] if '/reference/' in z['path'])
    print('PASS_REPRODUCTION: 15 salidas idénticas; escalas, KKT físico, coordenadas, costes y congelación verificados. Q/P/T2-A intactos.')
if __name__=='__main__':main()
