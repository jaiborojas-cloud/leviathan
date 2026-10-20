#!/usr/bin/env python3
"""Integridad, protocolo previo, alcance y reproducción de E16-F."""
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

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)

def main():
    cfg=json.loads((ROOT/'config.json').read_text())
    for manifest in ['freeze_manifest.csv','manifest.csv']:
        for row in csv.DictReader((ROOT/manifest).open()):
            assert sha(ROOT/row['path'])==row['sha256'],row['path']
    for name in ['config.json','DESIGN_FROZEN.md','freeze_manifest.csv']:
        assert git('show',f'7717db2:experiments/E16/F/{name}')==(ROOT/name).read_bytes(),name
    base=cfg['base_commit']
    allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'}
    changed=git('diff','--name-only',base,'--').decode().splitlines()
    assert all(p.startswith('experiments/E16/F/') or p in allowed for p in changed),changed
    assert not git('diff',base,'--','experiments/T2_A'), 'T2_A modified'
    result=ROOT/'results/run_v1'
    s=json.loads((result/'summary.json').read_text())
    assert s['lengths']==324 and s['paired']==216
    assert sum(s['counts'].values())==324
    assert sum(s['check_counts'].values())==s['checks']
    with tempfile.TemporaryDirectory(prefix='e16f-') as temp:
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
        subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',temp],env=env,check=True,timeout=cfg['budget_seconds'])
        for name in ['lengths.csv','paired_ratios.csv','checks.csv','summary.json','provenance.json']:
            assert (Path(temp)/name).read_bytes()==(result/name).read_bytes(),name
        assert json.loads((Path(temp)/'resources.json').read_text())['within_budget']
    assert json.loads((result/'resources.json').read_text())['within_budget']
    print('PASS_REPRODUCTION: hashes, protocolo previo, alcance, T2_A intacto y cinco salidas idénticas. Estado científico:',s['status'])

if __name__=='__main__':main()
