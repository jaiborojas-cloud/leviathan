#!/usr/bin/env python3
"""Congelación D, procedencia C, integridad anterior y reproducción de tablas."""
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
BASE='93b8686be1bfba5ad3dcc23a6080610278750acf'
FREEZE='c360f56'


def sha(b):return hashlib.sha256(b).hexdigest()


def main():
    for name in ['freeze_manifest.csv','manifest.csv']:
        for row in csv.DictReader((ROOT/name).open()):
            b=(ROOT/row['path']).read_bytes()
            assert len(b)==int(row['bytes']) and sha(b)==row['sha256'],row['path']
    for row in csv.DictReader((ROOT/'freeze_manifest.csv').open()):
        b=subprocess.check_output(['git','show',f'{FREEZE}:experiments/E16/D/{row["path"]}'],cwd=REPO)
        assert b==(ROOT/row['path']).read_bytes(),row['path']
    provenance=json.loads((ROOT/'provenance.json').read_text())
    for source in provenance['sources']:
        b=subprocess.check_output(['git','show',provenance['source_C_commit']+':'+source['path']],cwd=REPO)
        assert sha(b)==source['sha256'],source['path']
    for prior in [ROOT.parent,ROOT.parent/'B']:
        for row in csv.DictReader((prior/'manifest.csv').open()):
            b=(prior/row['path']).read_bytes()
            assert len(b)==int(row['bytes']) and sha(b)==row['sha256'],row['path']
    # Nuevos pesos y entradas frente a la fuente B/C; no se calcula la red.
    config=json.loads((ROOT/'config.json').read_text())
    old=json.loads((ROOT.parent/'B/config.json').read_text())
    assert all(t not in old['states'].values() for t in config['states'].values())
    assert all(z not in old['inputs'] for z in config['inputs'])
    assert all(p not in old['perspectives'] for p in config['perspectives'])
    assert len(config['states'])==12 and len(config['inputs'])==12 and not config['trained']
    for p in ROOT.glob('*.md'):
        for t in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' not in t:assert (p.parent/t.split('#')[0]).exists(),(p,t)
    with tempfile.TemporaryDirectory(prefix='e16d-') as temp:
        out=Path(temp)/'replica'
        subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--output',str(out)],check=True)
        subprocess.run([sys.executable,str(ROOT/'scripts/summarize.py'),str(out),'--output',str(out/'descriptive.json')],check=True)
        subprocess.run([sys.executable,str(ROOT/'scripts/compare_compositions.py'),str(out)],check=True)
        for name in ['checks.csv','ranks.csv','negative_controls.csv','summary.json','descriptive.json',
                     'paired_compositions.csv','panel_sensitivity.csv','secondary_summary.json']:
            assert (out/name).read_bytes()==(ROOT/'results/run_v1'/name).read_bytes(),name
        assert json.loads((out/'resources.json').read_text())['budget_pass']
    changed=subprocess.check_output(['git','diff',BASE,'--name-only'],cwd=REPO,text=True).splitlines()
    allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'}
    assert all(p.startswith('experiments/E16/D/') or p in allowed for p in changed),changed
    assert not subprocess.check_output(['git','diff',BASE,'--','experiments/T2_A'],cwd=REPO)
    print('PASS: congelación y novedad de datos, procedencia, hashes A/B/C, ocho tablas/reportes y alcance sin T2-A')


if __name__=='__main__':main()
