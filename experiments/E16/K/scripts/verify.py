#!/usr/bin/env python3
"""Integridad y reproducción del diagnóstico K, conservando su inconcluso."""
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)

def main():
    cfg=json.loads((ROOT/'config.json').read_text())
    for name in ['freeze_manifest.csv','manifest.csv']:
        for row in csv.DictReader((ROOT/name).open()):assert sha(ROOT/row['path'])==row['sha256'],row['path']
    for name in ['config.json','DESIGN_FROZEN.md','freeze_manifest.csv']:
        assert git('show',f'2a1a9d3:experiments/E16/K/{name}')==(ROOT/name).read_bytes(),name
    for p,value in cfg['sources'].items():assert sha(ROOT.parent/p)==value,p
    old={r['case']:r for r in csv.DictReader((ROOT.parent/'J/results/run_v1/cases.csv').open())}
    expected={k for k,r in old.items() if r['status']=='INCONCLUSIVE'}
    assert set(cfg['cases'][:3])==expected
    assert cfg['cases'][3:]==['h00/0/sum','h01/1/sum']
    allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'}
    changed=git('diff','--name-only',cfg['base_commit'],'--').decode().splitlines()
    assert all(x.startswith('experiments/E16/K/') or x in allowed for x in changed),changed
    assert not git('diff',cfg['base_commit'],'--','experiments/T2_A','experiments/E16/J','experiments/E16/H','experiments/E16/G')
    result=ROOT/'results/run_v1';s=json.loads((result/'summary.json').read_text())
    assert s['status']=='INCONCLUSIVE' and s['cases']==5 and s['resolutions']==15
    assert s['counts']=={'PASS_NUMERICAL':4,'FAIL':0,'INCONCLUSIVE':1}
    assert s['searches']==s['validated_searches']==85
    assert s['resolved_J_cases']==2 and s['diagnostic_cases']==3
    assert s['check_counts']=={'PASS':2085,'FAIL':0,'INCONCLUSIVE':1}
    assert s['branch_counts']=={'AGREEMENT':15,'DISTINCT_STATIONARY_CANDIDATES':0,'NUMERICAL_OR_OPTIMIZATION_LIMIT':0}
    assert len(list(csv.DictReader((result/'segments.csv').open())))==290
    with tempfile.TemporaryDirectory(prefix='e16k-') as temp:
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
        subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',temp],env=env,check=True,timeout=cfg['budget_seconds'])
        for name in ['checks.csv','searches.csv','vertices.csv','gradients.csv','segments.csv','resolutions.csv','cases.csv','summary.json','provenance.json']:
            assert (Path(temp)/name).read_bytes()==(result/name).read_bytes(),name
        assert json.loads((Path(temp)/'resources.json').read_text())['within_budget']
    assert json.loads((result/'resources.json').read_text())['within_budget']
    print('PASS_REPRODUCTION: nueve salidas idénticas, congelación, fuentes y alcance verificados; J y T2-A intactos. K sigue INCONCLUSIVE global.')

if __name__=='__main__':main()
