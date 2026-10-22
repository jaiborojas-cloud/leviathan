#!/usr/bin/env python3
"""Integridad de v1 preservada, errata y reproducción científica de Q v2."""
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
import mpmath as mp
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def rows(name,version='run_v2'):return list(csv.DictReader((ROOT/'results'/version/name).open()))
def main():
    cfg=json.loads((ROOT/'config.json').read_text())
    for name in ['freeze_manifest.csv','implementation_manifest_v2.csv','manifest.csv']:
        for row in csv.DictReader((ROOT/name).open()):assert sha(ROOT/row['path'])==row['sha256'],row['path']
    for row in csv.DictReader((ROOT/'implementation_manifest.csv').open()):
        source=ROOT/('scripts/run_v1_snapshot.py' if row['path']=='scripts/run.py' else row['path']);assert sha(source)==row['sha256']
    for name in ['config.json','groups.json','DESIGN_FROZEN.md','freeze_manifest.csv']:
        assert git('show',f'9d06ad5:experiments/E16/Q/{name}')==(ROOT/name).read_bytes(),name
    assert git('show','03071d3:experiments/E16/Q/ERRATA_IMPLEMENTACION_v1.md')==(ROOT/'ERRATA_IMPLEMENTACION_v1.md').read_bytes()
    assert git('show','a3e41b9:experiments/E16/Q/implementation_manifest_v2.csv')==(ROOT/'implementation_manifest_v2.csv').read_bytes()
    assert git('show','094bc25:experiments/E16/Q/scripts/run.py')==(ROOT/'scripts/run_v1_snapshot.py').read_bytes()
    for p in (ROOT/'results/run_v1').iterdir():assert git('show',f'03071d3:experiments/E16/Q/results/run_v1/{p.name}')==p.read_bytes(),p.name
    for p,h in cfg['sources'].items():assert sha(ROOT.parent/p)==h,p
    allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'}
    changed=git('diff','--name-only',cfg['base_commit'],'--').decode().splitlines();assert all(p.startswith('experiments/E16/Q/') or p in allowed for p in changed),changed
    assert not git('diff',cfg['base_commit'],'--','experiments/T2_A','experiments/E16/P','experiments/E16/O')
    oldpaths=rows('paths.csv','run_v1');oldnames={z['path'] for z in oldpaths};newpaths=rows('paths.csv');assert len(oldpaths)==4
    for old in oldpaths:
        new=next(z for z in newpaths if z['path']==old['path'])
        for key in old:
            if key not in ['kkt_energy','gradient_energy_error']:assert old[key]==new[key],(old['path'],key)
    assert rows('vertices.csv','run_v1')==[z for z in rows('vertices.csv') if z['path'] in oldnames]
    for name in ['energies.csv','spectra.csv','hessian_directions.csv','segments.csv']:
        old=rows(name,'run_v1');new=rows(name);assert new[:len(old)]==old,name
    spec=importlib.util.spec_from_file_location('kernel_q_verify',ROOT/'scripts/kernel.py');k=importlib.util.module_from_spec(spec);spec.loader.exec_module(k)
    z=np.array([[0.,0.],[.2,.1],[.6,-.1],[1.,0.]])
    obj=k.Objective(np.array([1.,1.]),np.array([2.,1.]),'free',z[:,0],'sum',np.eye(2),np.zeros((2,2)),target='energy')
    direct=len(z[:-1])/2*np.sum(np.diff(z,axis=0)**2);assert abs(obj.value(k.pack(z,'free'))-direct)<1e-12
    fine=k.subdivide(z);fineobj=k.Objective(obj.a,obj.a+obj.v,'free',fine[:,0],'sum',np.eye(2),np.zeros((2,2)),target='energy')
    assert abs(fineobj.value(k.pack(fine,'free'))-direct)<1e-12
    vertices=rows('vertices.csv');grads=rows('gradients.csv')
    for path in newpaths:
        rr=sorted([z for z in vertices if z['path']==path['path']],key=lambda z:int(z['index']));m=int(path['segments']);assert len(rr)==m+1
        zz=np.array([[float(z['t']),float(z['s'])] for z in rr]);assert np.array_equal(zz[[0,-1]],[[0,0],[1,0]])
        assert np.all((zz[:,0]>=0)&(zz[:,0]<=1)&(abs(zz[:,1])<=.25))
        for target in ['length','energy']:
            gg=[z for z in grads if z['path']==path['path']+'/'+target]
            assert len(gg)==2*(m-1) and {z['coordinate'] for z in gg}=={'t','s'}
    with mp.workdps(80):
        for r in rows('energies.csv'):
            ee,ed,ea=(mp.mpf(r[z]) for z in ['energy','duration_energy','arc_energy'])
            # CSV stores 40 significant digits; allow their rounding for this readback only.
            assert ee+mp.mpf('1e-38')>=ed and ed+mp.mpf('1e-38')>=ea,r['point']
    spectra=rows('spectra.csv');assert len(spectra)==27
    for r in spectra:assert int(r['negative'])+int(r['near_zero'])+int(r['positive'])==int(r['inactive_dimension'])
    assert len(rows('hessian_directions.csv'))==36
    summary=json.loads((ROOT/'results/run_v2/summary.json').read_text());assert summary['paths']==len(newpaths)==12 and summary['conditioning_points']==9
    assert sum(z['status']=='PASS_NUMERICAL' for z in newpaths)==summary['validated_paths']
    out=ROOT/'results/run_v2';names=[p.name for p in sorted(out.iterdir()) if p.suffix in ['.csv','.json'] and p.name!='resources.json'];assert len(names)==15
    with tempfile.TemporaryDirectory(prefix='e16q-') as tmp:
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
        subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',tmp],env=env,check=True,timeout=cfg['budget_seconds'])
        for name in names:assert (Path(tmp)/name).read_bytes()==(out/name).read_bytes(),name
        assert json.loads((Path(tmp)/'resources.json').read_text())['within_budget']
    assert json.loads((out/'resources.json').read_text())['within_budget']
    print('PASS_REPRODUCTION: 15 salidas v2 idénticas; v1 intacta, errata, objetivos, coordenadas y condicionamiento verificados. P/O/T2-A sin cambios.')
if __name__=='__main__':main()
