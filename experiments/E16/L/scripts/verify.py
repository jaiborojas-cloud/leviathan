#!/usr/bin/env python3
"""Integridad y reproducción E16-L; conserva el desacuerdo de forma."""
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
        assert git('show',f'0212bcf:experiments/E16/L/{name}')==(ROOT/name).read_bytes(),name
    for p,expected in cfg['sources'].items():assert sha(ROOT.parent/p)==expected,p
    previous={r['case']:r for r in csv.DictReader((ROOT.parent/'K/results/run_v1/cases.csv').open())}
    assert previous['h00/0/quadratic']['K_status']=='INCONCLUSIVE'
    assert cfg['cases']==['h00/0/quadratic','h00/0/sum']
    assert cfg['segments']==[16,32,64] and cfg['length_refinement_tolerance']=='1e-3'
    allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'}
    changed=git('diff','--name-only',cfg['base_commit'],'--').decode().splitlines()
    assert all(p.startswith('experiments/E16/L/') or p in allowed for p in changed),changed
    assert not git('diff',cfg['base_commit'],'--','experiments/T2_A','experiments/E16/K','experiments/E16/J','experiments/E16/H','experiments/E16/G')
    result=ROOT/'results/run_v1';s=json.loads((result/'summary.json').read_text())
    assert s['status']=='INCONCLUSIVE' and s['cases']==2 and s['resolutions']==6
    assert s['counts']=={'PASS_NUMERICAL':1,'FAIL':0,'INCONCLUSIVE':1}
    assert s['searches']==s['validated_searches']==36 and not s['resolved_pending_case']
    assert s['check_counts']=={'PASS':2712,'FAIL':0,'INCONCLUSIVE':4}
    assert len(list(csv.DictReader((result/'segments.csv').open())))==452
    assert len(list(csv.DictReader((result/'shapes.csv').open())))==188
    with tempfile.TemporaryDirectory(prefix='e16l-') as temp:
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
        subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',temp],env=env,check=True,timeout=cfg['budget_seconds'])
        for name in ['checks.csv','searches.csv','vertices.csv','gradients.csv','segments.csv','resolutions.csv','shapes.csv','cases.csv','summary.json','provenance.json']:
            assert (Path(temp)/name).read_bytes()==(result/name).read_bytes(),name
        assert json.loads((Path(temp)/'resources.json').read_text())['within_budget']
    assert json.loads((result/'resources.json').read_text())['within_budget']
    print('PASS_REPRODUCTION: diez salidas idénticas, congelación, fuentes y alcance. L conserva INCONCLUSIVE; K y T2-A intactos.')

if __name__=='__main__':main()
