#!/usr/bin/env python3
"""Integridad, marcado determinista, conservación de nodos y reproducción O."""
import csv
import hashlib
import importlib.util
import json
import os
import re
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
def scalar(text):
    # NumPy 2 conserva su tipo en repr; admitir sólo este envoltorio numérico.
    match=re.fullmatch(r"np\.float64\(([-+0-9.eE]+)\)",text)
    return float(match.group(1) if match else text)

def main():
    cfg=json.loads((ROOT/'config.json').read_text())
    for name in ['freeze_manifest.csv','implementation_manifest.csv','manifest.csv']:
        for row in csv.DictReader((ROOT/name).open()):assert sha(ROOT/row['path'])==row['sha256'],row['path']
    for name in ['config.json','groups.json','DESIGN_FROZEN.md','freeze_manifest.csv']:
        assert git('show',f'6a6c21e:experiments/E16/O/{name}')==(ROOT/name).read_bytes(),name
    assert git('show','681a804:experiments/E16/O/implementation_manifest.csv')==(ROOT/'implementation_manifest.csv').read_bytes()
    for p,h in cfg['sources'].items():assert sha(ROOT.parent/p)==h,p
    allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'}
    changed=git('diff','--name-only',cfg['base_commit'],'--').decode().splitlines()
    assert all(p.startswith('experiments/E16/O/') or p in allowed for p in changed),changed
    assert not git('diff',cfg['base_commit'],'--','experiments/T2_A','experiments/E16/N','experiments/E16/M')
    spec=importlib.util.spec_from_file_location('adaptive_verify',ROOT/'scripts/adaptive.py');ad=importlib.util.module_from_spec(spec);spec.loader.exec_module(ad);assert ad.controls()
    pp=rows('probes.csv');vv=rows('vertices.csv');mm=rows('marking.csv');tt=rows('trajectories.csv')
    source=list(csv.DictReader((ROOT.parent/'N/results/run_v1/vertices.csv').open()))
    def nodes(lin,round_id):
        r=sorted([z for z in vv if z['lineage']==lin and int(z['round'])==round_id],key=lambda z:int(z['index']))
        return np.r_[0,[float(z['t']) for z in r],1]
    for lin in ['Q0','Q1','C0']:
        a=sorted([z for z in source if z['lineage']==lin and z['segments']=='128'],key=lambda z:int(z['index']))
        b=sorted([z for z in vv if z['lineage']==lin and z['round']=='0'],key=lambda z:int(z['index']))
        assert [(z['t'],z['s']) for z in a]==[(z['t'],z['s']) for z in b]
    for row in mm:
        lin=row['lineage'];round_id=int(row['round']);probes=sorted([z for z in pp if z['lineage']==lin and int(z['round'])==round_id],key=lambda z:int(z['index']))
        scores=np.array([float(z['score']) for z in probes]);m=int(row['segments']);assert len(probes)==m
        for z in probes:
            score=max(scalar(z['displacement'])/float(cfg['probe_shape_tolerance']),np.sqrt(float(z['gain'])/float(cfg['probe_gain_tolerance'])))
            assert score==float(z['score'])
        chosen,mass=ad.mark(scores,cfg['marking_fraction'],min(cfg['max_additions_per_round'],cfg['max_segments']-m))
        if row['reason']=='refine':
            assert chosen==json.loads(row['marked_indices']) and mass==float(row['captured_fraction'])
            t0=nodes(lin,round_id);t1=nodes(lin,round_id+1)
            expected=np.unique(np.r_[t0,[(t0[j]+t0[j+1])/2 for j in chosen]])
            assert np.array_equal(t1,expected) and len(t1)-1<=cfg['max_segments']
        else:assert not json.loads(row['marked_indices'])
    s=json.loads((ROOT/'results/run_v1/summary.json').read_text())
    assert len(tt)==s['trajectories'] and len(pp)==s['probes']
    assert sum(z['valid']=='False' for z in pp)==s['invalid_probes']
    assert sum(z['status']=='PASS_NUMERICAL' for z in tt)==s['validated_trajectories']
    out=ROOT/'results/run_v1';names=[p.name for p in sorted(out.iterdir()) if p.suffix in ['.csv','.json'] and p.name!='resources.json']
    with tempfile.TemporaryDirectory(prefix='e16o-') as tmp:
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
        subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',tmp],env=env,check=True,timeout=cfg['budget_seconds'])
        for name in names:assert (Path(tmp)/name).read_bytes()==(out/name).read_bytes(),name
        assert json.loads((Path(tmp)/'resources.json').read_text())['within_budget']
    assert json.loads((out/'resources.json').read_text())['within_budget']
    print(f'PASS_REPRODUCTION: {len(names)} salidas idénticas; fuente, marcado, anidamiento, hashes y alcance verificados. N/M/T2-A intactos.')
if __name__=='__main__':main()
