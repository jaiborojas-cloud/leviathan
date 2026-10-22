#!/usr/bin/env python3
"""Congelación, rachas independientes, banderas nativas y reproducción de S."""
import csv
import hashlib
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
def point_hash(z):return hashlib.sha256(json.dumps(np.asarray(z,float).tolist(),separators=(',',':'),allow_nan=False).encode()).hexdigest()
def main():
    cfg=json.loads((ROOT/'config.json').read_text())
    for name in ['freeze_manifest.csv','implementation_manifest.csv','manifest.csv']:
        for row in csv.DictReader((ROOT/name).open()):assert sha(ROOT/row['path'])==row['sha256'],row['path']
    for name in ['config.json','groups.json','DESIGN_FROZEN.md','freeze_manifest.csv']:
        assert git('show',f'3b04bbc:experiments/E16/S/{name}')==(ROOT/name).read_bytes(),name
    assert git('show','0310ab7:experiments/E16/S/implementation_manifest.csv')==(ROOT/'implementation_manifest.csv').read_bytes()
    for p,h in cfg['sources'].items():assert sha(ROOT.parent/p)==h,p
    allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'}
    changed=git('diff','--name-only',cfg['base_commit'],'--').decode().splitlines();assert all(p.startswith('experiments/E16/S/') or p in allowed for p in changed),changed
    assert not git('diff',cfg['base_commit'],'--','experiments/T2_A','experiments/E16/R','experiments/E16/Q')
    assert not git('diff','origin/main','--','experiments/T2_A')
    rscales=list(csv.DictReader((ROOT.parent/'R/results/run_v1/scales.csv').open()));cache={}
    for lin in ['Q0','Q1','C0']:
        for m in cfg['segments']:
            r=[z for z in rscales if z['reference']==f'{lin}/{m}'];d=np.array([float(z['scale']) for z in r]);assert len(d)==2*(m-1) and np.all(d>0) and np.all(np.frexp(d)[0]==.5);cache[(lin,m)]=d
            row=next(z for z in rows('cached_preconditioners.csv') if z['reference']==f'{lin}/{m}')
            assert row['scale_sha256']==hashlib.sha256(json.dumps(d.tolist(),separators=(',',':')).encode()).hexdigest() and row['new_hessian_calls']=='0'
    paths=rows('paths.csv');audits=rows('audits.csv');vertices=rows('vertices.csv');grads=rows('gradients.csv');costs=rows('costs.csv')
    for path in paths:
        name=path['path'];m=int(path['segments']);ar=[z for z in audits if z['path']==name];assert ar and int(ar[0]['iteration'])==0 and ar[0]['initial']=='True'
        streak=0;last=None;requested=False
        for j,z in enumerate(ar):
            assert int(z['audit_number'])==j+1 and not requested
            it=int(z['iteration']);verified=z['verified']=='True';kkt=float(z['physical_kkt'])
            if verified:
                assert float(z['gradient_error'])<=float(cfg['gradient_agreement_tolerance']) and float(z['fd_consistency'])<=float(cfg['mp_fd_agreement_tolerance'])
                expected_state='STATIONARY' if kkt<=float(cfg['gradient_tolerance']) else 'NONSTATIONARY'
                assert int(z['MP_local_reference_calls'])==4*2*(m-1) and z['MP_global_reference_calls']=='1'
            else:expected_state='UNVERIFIED'
            assert z['state']==expected_state
            if it==0:assert j==0 and z['initial']=='True' and z['stop_requested']=='False'
            else:
                assert it%cfg['monitor_interval']==0 and z['initial']=='False'
                if last is not None and it-last!=cfg['monitor_interval']:streak=0
                streak=streak+1 if expected_state=='STATIONARY' else 0;last=it
                requested=streak>=cfg['monitor_required_successes']
            assert streak==int(z['streak']) and (z['stop_requested']=='True')==requested
        assert len(ar)==int(path['monitor_audits']) and int(path['iterations'])==int(path['callback_calls'])
        rr=sorted([z for z in vertices if z['path']==name],key=lambda z:int(z['index']));assert len(rr)==m+1
        z=np.array([[float(q['t']),float(q['s'])] for q in rr]);assert point_hash(z)==path['final_point_sha256'];assert np.array_equal(z[[0,-1]],[[0,0],[1,0]])
        assert np.all((z[:,0]>=0)&(z[:,0]<=1)&(abs(z[:,1])<=.25))
        gg=[z for z in grads if z['path']==name+'/final'];assert len(gg)==2*(m-1)
        gm=np.array([float(q['mp_fd_2']) for q in gg]);x=z[1:-1].reshape(-1);box=np.array([bb for j in range(m-1) for bb in [cfg['t_bounds'],cfg['s_bounds']]])
        physical=float(np.max(abs(x-np.clip(x-gm,box[:,0],box[:,1]))))/max(1,abs(float(path['length'])))
        assert abs(physical-float(path['physical_kkt']))<1e-12
        route=path['termination_route']
        if route=='PHYSICAL_SUSTAINED':
            assert requested and path['native_success']=='False' and path['native_status']=='99'
            assert ar[-1]['point_sha256']==path['final_point_sha256'] and int(ar[-1]['iteration'])==int(path['iterations'])
            assert all(q['state']=='STATIONARY' for q in ar[-cfg['monitor_required_successes']:])
        elif route in ['NATIVE_VERIFIED','NATIVE_CONTROL']:assert path['native_success']=='True'
        else:assert path['status']!='PASS_NUMERICAL'
        if path['status']=='PASS_NUMERICAL':assert physical<=float(cfg['gradient_tolerance']) and int(path['unverified_audits'])==0
        if path['lineage']=='C0' and path['iterations']=='0':assert len(ar)==1 and route=='NATIVE_CONTROL'
        c=next(q for q in costs if q['path']==name);assert int(c['monitor_full_gradients'])==len(ar) and c['new_hessian_calls']=='0'
        assert int(c['monitor_MP_local_reference_calls'])==sum(int(q['MP_local_reference_calls']) for q in ar)
        assert int(c['monitor_MP_global_reference_calls'])==sum(int(q['MP_global_reference_calls']) for q in ar)
        assert c['solver_function_evaluations']==path['nfev'] and c['solver_gradient_evaluations']==path['njev']
    rp=list(csv.DictReader((ROOT.parent/'R/results/run_v1/paths.csv').open()))
    for h in rows('historical.csv'):
        name=h['comparison'].removesuffix('_R_S');old=next(z for z in rp if z['path']==name)
        assert h['R_status']==old['status'] and h['R_success']==old['success'] and h['R_iterations']==old['iterations'] and h['R_physical_kkt']==old['physical_kkt']
    out=ROOT/'results/run_v1';s=json.loads((out/'summary.json').read_text());assert s['paths']==len(paths)==12 and s['audits']==len(audits)
    assert s['validated_paths']==sum(z['status']=='PASS_NUMERICAL' for z in paths);assert len(rows('refinements.csv'))==6 and len(rows('comparisons.csv'))==10 and len(rows('historical.csv'))==12
    names=[p.name for p in sorted(out.iterdir()) if p.suffix in ['.csv','.json'] and p.name!='resources.json'];assert len(names)==16
    with tempfile.TemporaryDirectory(prefix='e16s-') as tmp:
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
        subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',tmp],env=env,check=True,timeout=cfg['budget_seconds'])
        for name in names:assert (Path(tmp)/name).read_bytes()==(out/name).read_bytes(),name
        assert json.loads((Path(tmp)/'resources.json').read_text())['within_budget']
    resources=json.loads((out/'resources.json').read_text());assert resources['within_budget'] and len(resources['timings']['monitor'])==len(audits)
    print('PASS_REPRODUCTION: 16 salidas idénticas; rachas, hashes, banderas nativas, KKT físico, costes e historia R verificados. R/Q/T2-A intactos.')
if __name__=='__main__':main()
