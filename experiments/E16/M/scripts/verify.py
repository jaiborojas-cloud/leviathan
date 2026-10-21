#!/usr/bin/env python3
"""Verifica agrupamiento, errata conservada y reproducción M v2."""
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import mpmath as mp
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)

def rebuild_groups(cfg):
    starts=list(csv.DictReader((ROOT.parent/'L/results/run_v1/searches.csv').open()))
    vertices=list(csv.DictReader((ROOT.parent/'L/results/run_v1/vertices.csv').open()));groups=[]
    for case,prefix in [('h00/0/quadratic','Q'),('h00/0/sum','C')]:
        clusters=[]
        for r in sorted([x for x in starts if x['case']==case and x['segments']=='32'],key=lambda x:int(x['start'])):
            index=int(r['start']);s=np.array([float(x['s']) for x in sorted([x for x in vertices if x['case']==case and x['segments']=='32' and x['source']=='start'+str(index)],key=lambda x:int(x['index']))])
            with mp.workdps(80):
                length=mp.mpf(r['length_mp']);target=None
                for cluster in clusters:
                    if all(abs(length-x[1])/max(1,abs(length),abs(x[1]))<=mp.mpf(cfg['group_length_tolerance']) and np.max(np.abs(s-x[2]))<=float(cfg['group_shape_tolerance']) for x in cluster):target=cluster;break
                if target is None:target=[];clusters.append(target)
                target.append((index,length,s))
        for i,c in enumerate(clusters):groups.append({'lineage':prefix+str(i),'case':case,'representative_start':c[0][0],'members':[x[0] for x in c],'source_segments':32})
    return groups

def main():
    cfg=json.loads((ROOT/'config.json').read_text())
    for name in ['freeze_manifest.csv','implementation_manifest.csv','manifest.csv']:
        for row in csv.DictReader((ROOT/name).open()):assert sha(ROOT/row['path'])==row['sha256'],row['path']
    for name in ['config.json','groups.json','DESIGN_FROZEN.md','freeze_manifest.csv']:
        assert git('show',f'eacfa4d:experiments/E16/M/{name}')==(ROOT/name).read_bytes(),name
    assert git('show','456aa57:experiments/E16/M/ERRATA_IMPLEMENTACION_v1.md')==(ROOT/'ERRATA_IMPLEMENTACION_v1.md').read_bytes()
    assert git('show','4dfbcdc:experiments/E16/M/implementation_manifest.csv')==(ROOT/'implementation_manifest.csv').read_bytes()
    assert git('show','1486ef1:experiments/E16/M/scripts/run.py')==(ROOT/'scripts/run_v1_snapshot.py').read_bytes()
    for p,h in cfg['sources'].items():assert sha(ROOT.parent/p)==h,p
    assert rebuild_groups(cfg)==json.loads((ROOT/'groups.json').read_text())['groups']
    allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'}
    changed=git('diff','--name-only',cfg['base_commit'],'--').decode().splitlines()
    assert all(p.startswith('experiments/E16/M/') or p in allowed for p in changed),changed
    assert not git('diff',cfg['base_commit'],'--','experiments/T2_A','experiments/E16/L','experiments/E16/K')
    v1=ROOT/'results/run_v1';v2=ROOT/'results/run_v2'
    for p in v1.iterdir():
        if p.is_file():assert git('show',f'1486ef1:experiments/E16/M/results/run_v1/{p.name}')==p.read_bytes(),p.name
    for name in ['vertices.csv','gradients.csv','segments.csv','transitions.csv','shape_nodes.csv','localization.csv','cross_candidates.csv']:
        assert (v1/name).read_bytes()==(v2/name).read_bytes(),name
    s=json.loads((v2/'summary.json').read_text())
    assert s['status']=='INCONCLUSIVE' and s['lineages']==3
    assert s['counts']=={'PASS_NUMERICAL':1,'FAIL':0,'INCONCLUSIVE':2}
    assert s['trajectories']==s['validated_trajectories']==9 and s['optimizations']==6
    assert s['check_counts']=={'PASS':7492,'FAIL':0,'INCONCLUSIVE':4}
    assert s['cross_candidate_diagnoses']=={'32':'DIFFERENT_CANDIDATES','64':'NUMERICAL_AGREEMENT','128':'NUMERICAL_AGREEMENT'}
    assert len(list(csv.DictReader((v2/'segments.csv').open())))==1344
    names=['checks.csv','trajectories.csv','vertices.csv','gradients.csv','segments.csv','transitions.csv','shape_nodes.csv','localization.csv','cross_candidates.csv','lineages.csv','source_reference_intervals.csv','summary.json','provenance.json']
    with tempfile.TemporaryDirectory(prefix='e16m-') as temp:
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
        subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',temp],env=env,check=True,timeout=cfg['budget_seconds'])
        for name in names:assert (Path(temp)/name).read_bytes()==(v2/name).read_bytes(),name
        assert json.loads((Path(temp)/'resources.json').read_text())['within_budget']
    assert json.loads((v2/'resources.json').read_text())['within_budget']
    print('PASS_REPRODUCTION: trece salidas v2 idénticas; v1 conservada, geometría intacta, agrupamiento y congelación verificados. L/T2-A sin cambios.')

if __name__=='__main__':main()
