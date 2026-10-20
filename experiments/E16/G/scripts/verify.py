#!/usr/bin/env python3
"""Comprueba integridad, congelación, alcance y reproducción diagnóstica G."""
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
        for row in csv.DictReader((ROOT/name).open()):
            assert sha(ROOT/row['path'])==row['sha256'],row['path']
    for name in ['config.json','DESIGN_FROZEN.md','freeze_manifest.csv']:
        assert git('show',f'7049807:experiments/E16/G/{name}')==(ROOT/name).read_bytes(),name
    allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'}
    changed=git('diff','--name-only',cfg['base_commit'],'--').decode().splitlines()
    assert all(p.startswith('experiments/E16/G/') or p in allowed for p in changed),changed
    assert not git('diff',cfg['base_commit'],'--','experiments/T2_A','experiments/E16/F'), 'F or T2_A modified'
    result=ROOT/'results/run_v1';summary=json.loads((result/'summary.json').read_text())
    assert summary['status']=='PASS_NUMERICAL'
    assert summary['lengths']==324 and summary['paired']==216
    assert summary['counts']=={'PASS_NUMERICAL':324,'FAIL':0,'INCONCLUSIVE':0}
    assert summary['transitions_from_F']=={'INCONCLUSIVE->PASS_NUMERICAL':85,'PASS_NUMERICAL->PASS_NUMERICAL':239}
    assert summary['checks']==13102 and summary['check_counts']['PASS']==13102
    with tempfile.TemporaryDirectory(prefix='e16g-') as temp:
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
        subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',temp],env=env,check=True,timeout=cfg['budget_seconds'])
        for name in ['lengths.csv','checks.csv','paired_ratios.csv','comparison_F.csv','summary.json','provenance.json']:
            assert (Path(temp)/name).read_bytes()==(result/name).read_bytes(),name
        assert json.loads((Path(temp)/'resources.json').read_text())['within_budget']
    assert json.loads((result/'resources.json').read_text())['within_budget']
    print('PASS_REPRODUCTION: seis salidas idénticas, hashes y diseño previo; F y T2_A intactos. G es diagnóstico.')

if __name__=='__main__':main()
