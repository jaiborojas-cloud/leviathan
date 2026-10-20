#!/usr/bin/env python3
"""Comprueba congelación, hashes, enlaces, alcance y reproducción E16-B."""
import csv
import hashlib
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
    for name in ['DESIGN_FROZEN.md','config.json','mathematical_spec.md','requirements.txt']:
        frozen=subprocess.check_output(['git','show',f'd05f31b:experiments/E16/B/{name}'],cwd=REPO)
        assert frozen==(ROOT/name).read_bytes(),name
    for p in ROOT.glob('*.md'):
        for t in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' not in t:assert (p.parent/t.split('#')[0]).exists(),(p,t)
    with tempfile.TemporaryDirectory(prefix='e16b-') as tmp:
        out=Path(tmp)/'replica'
        subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--output',str(out)],check=True)
        subprocess.run([sys.executable,str(ROOT/'scripts/summarize.py'),str(out),'--output',str(out/'descriptive.json')],check=True)
        for name in ['spectra.csv','kernel.csv','panel_sensitivity.csv','summary.json','descriptive.json']:
            assert (out/name).read_bytes()==(ROOT/'results/run_v1'/name).read_bytes(),name
        original=list(csv.DictReader((ROOT/'results/run_v1/checks.csv').open()))
        replica=list(csv.DictReader((out/'checks.csv').open()))
        assert len(original)==len(replica)==1615
        for a,b in zip(original,replica):
            if a['check']=='tiempo':
                assert b['check']=='tiempo' and a['status']==b['status']=='PASS'
                assert a['tolerance']==b['tolerance']=='120'
                assert 0<float(b['abs_error'])<=120
            else:assert a==b,(a['config'],a['check'])
    changed=subprocess.check_output(['git','diff','21b7b2a','--name-only'],cwd=REPO,text=True).splitlines()
    allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'}
    assert all(p.startswith('experiments/E16/B/') or p in allowed for p in changed),changed
    print('PASS: congelación, hashes, enlaces, reproducción de cinco tablas/reportes y 1614 checks, tiempo validado aparte y alcance sin T2-A ni cambios a E16-A')


if __name__=='__main__':main()
