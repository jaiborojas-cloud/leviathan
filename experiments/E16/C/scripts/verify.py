#!/usr/bin/env python3
"""Integridad, congelación, alcance y reproducción E16-C."""
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]


def sha(b):return hashlib.sha256(b).hexdigest()


def main():
    for name in ['freeze_manifest.csv','manifest.csv']:
        for row in csv.DictReader((ROOT/name).open()):
            b=(ROOT/row['path']).read_bytes()
            assert len(b)==int(row['bytes']) and sha(b)==row['sha256'],row['path']
    for name in ['DESIGN_FROZEN.md','mathematical_spec.md','config.json','requirements.txt']:
        original=subprocess.check_output(['git','show',f'1b68c4e:experiments/E16/C/{name}'],cwd=REPO)
        assert original==(ROOT/name).read_bytes(),name
    assert (ROOT/'config.json').read_bytes()==(ROOT.parent/'B/config.json').read_bytes()
    # A y B conservan todos sus hashes; no se ejecutan sus scripts.
    for prior in [ROOT.parent,ROOT.parent/'B']:
        for row in csv.DictReader((prior/'manifest.csv').open()):
            b=(prior/row['path']).read_bytes()
            assert len(b)==int(row['bytes']) and sha(b)==row['sha256'],row['path']
    for p in ROOT.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' not in target:assert (p.parent/target.split('#')[0]).exists(),(p,target)
    with tempfile.TemporaryDirectory(prefix='e16c-') as tmp:
        out=Path(tmp)/'replica'
        subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--output',str(out)],check=True)
        subprocess.run([sys.executable,str(ROOT/'scripts/summarize.py'),str(out),'--output',str(out/'descriptive.json')],check=True)
        for name in ['checks.csv','ranks.csv','negative_controls.csv','summary.json','descriptive.json']:
            assert (out/name).read_bytes()==(ROOT/'results/run_v1'/name).read_bytes(),name
        assert json.loads((out/'resources.json').read_text())['budget_pass']
    changed=subprocess.check_output(['git','diff','50a991c','--name-only'],cwd=REPO,text=True).splitlines()
    allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'}
    assert all(p.startswith('experiments/E16/C/') or p in allowed for p in changed),changed
    print('PASS: hashes A/B/C, diseño congelado, enlaces, tablas reproducidas y alcance sin T2-A')


if __name__=='__main__':main()
