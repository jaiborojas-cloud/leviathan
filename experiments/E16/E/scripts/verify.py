#!/usr/bin/env python3
"""Verifica integridad, congelación, alcance y reproducción de E16-E."""
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

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(*args):
    return subprocess.check_output(['git',*args],cwd=REPO)

def main():
    for filename in ['freeze_manifest.csv','manifest.csv']:
        for row in csv.DictReader((ROOT/filename).open()):
            assert sha(ROOT/row['path'])==row['sha256'],row['path']
    for name in ['DESIGN_FROZEN.md','config.json','freeze_manifest.csv']:
        assert git('show',f'f9a1b58:experiments/E16/E/{name}')==(ROOT/name).read_bytes(),name
    allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'}
    changed=git('diff','--name-only','47f0eff','--').decode().splitlines()
    assert all(p.startswith('experiments/E16/E/') or p in allowed for p in changed),changed
    assert not git('diff','47f0eff','--','experiments/T2_A'), 'T2_A modified'
    result=ROOT/'results/run_v1'
    s=json.loads((result/'summary.json').read_text())
    assert s['status']=='PASS_NUMERICAL' and s['comparisons']==216 and s['checks']==10176
    with tempfile.TemporaryDirectory(prefix='e16e-') as temp:
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
        subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',temp],env=env,check=True,timeout=120)
        for name in ['comparisons.csv','checks.csv','summary.json','provenance.json']:
            assert (Path(temp)/name).read_bytes()==(result/name).read_bytes(),name
        assert json.loads((Path(temp)/'resources.json').read_text())['within_budget']
    assert json.loads((result/'resources.json').read_text())['within_budget']
    print('PASS: hashes, diseño congelado, alcance, T2_A intacto y cuatro salidas reproducidas.')

if __name__=='__main__':main()
