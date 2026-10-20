#!/usr/bin/env python3
"""Verifica hashes, enlaces propios y reproducción de tablas E16."""
import csv
import hashlib
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify():
    for table, root in [(ROOT/'manifest.csv',ROOT), (ROOT/'results/source_hashes.csv',REPO)]:
        for row in csv.DictReader(table.open()):
            path = root/row['path']
            assert path.stat().st_size == int(row['bytes']), path
            assert sha(path) == row['sha256'], path
    for path in ROOT.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if '://' not in target:
                assert (path.parent/target.split('#')[0]).exists(), (path,target)
    # Original failed versions are reconstructible from explicit commits, not overwritten.
    for run, commit in [('run_v1','6efaacc'),('run_v2','36f71c5')]:
        content = subprocess.check_output(['git','show',f'{commit}:experiments/E16/scripts/run_controls.py'],cwd=REPO)
        import json
        env = json.loads((ROOT/'results'/run/'environment.json').read_text())
        assert hashlib.sha256(content).hexdigest() == env['script_sha256']
    frozen = subprocess.check_output(['git','show','7db497d:experiments/E16/DESIGN_FROZEN.md'],cwd=REPO)
    assert frozen == (ROOT/'DESIGN_FROZEN.md').read_bytes()
    with tempfile.TemporaryDirectory(prefix='e16-') as tmp:
        target = Path(tmp)/'replica'
        subprocess.run([sys.executable,str(ROOT/'scripts/run_controls.py'),'--output',str(target)],check=True)
        for name in ['checks.csv','spectra.csv','summary.json']:
            assert (target/name).read_bytes() == (ROOT/'results/run_v3'/name).read_bytes(), name
    changed = subprocess.check_output(['git','diff','--name-only','12e849e','--'],cwd=REPO,text=True).splitlines()
    allowed = {'README.md','docs/experiment-index.md','docs/roadmap.md','docs/research-directions.md','experiments/README.md'}
    assert all(p.startswith('experiments/E16/') or p in allowed for p in changed), changed
    assert not any('T2_A' in p for p in changed)
    print('PASS: hashes, fuentes, enlaces E16, diseño intacto, versiones fallidas, tablas reproducidas y alcance sin T2-A')


if __name__ == '__main__':
    verify()
