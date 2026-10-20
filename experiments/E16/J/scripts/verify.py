#!/usr/bin/env python3
"""Integridad y reproducción; no convierte INCONCLUSIVE en validación global."""
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
        assert git('show',f'c2cd4a8:experiments/E16/J/{name}')==(ROOT/name).read_bytes(),name
    for p,k in [('H/data.json','H_data_sha256'),('D/scripts/run.py','D_method_sha256'),('G/scripts/run.py','G_method_sha256'),('I/results/run_v1/cases.csv','I_cases_sha256')]:assert sha(ROOT.parent/p)==cfg[k],p
    allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'}
    changed=git('diff','--name-only',cfg['base_commit'],'--').decode().splitlines()
    assert all(x.startswith('experiments/E16/J/') or x in allowed for x in changed),changed
    assert not git('diff',cfg['base_commit'],'--','experiments/T2_A','experiments/E16/I','experiments/E16/G','experiments/E16/H')
    result=ROOT/'results/run_v1';s=json.loads((result/'summary.json').read_text())
    assert s['status']=='INCONCLUSIVE' and s['cases']==27 and s['resolutions']==81
    assert s['counts']=={'PASS_NUMERICAL':24,'FAIL':0,'INCONCLUSIVE':3}
    assert s['check_counts']=={'PASS':5907,'FAIL':0,'INCONCLUSIVE':6}
    searches=list(csv.DictReader((result/'searches.csv').open()))
    assert len(searches)==252 and sum(r['case']!='euclidean_control' for r in searches)==243
    assert len(list(csv.DictReader((result/'segments.csv').open())))==972
    assert s['geometry_counts']=={'BOUNDARY_LIMITED':2,'INTERIOR_STABLE_DISCRETE':22,'UNRESOLVED':3}
    with tempfile.TemporaryDirectory(prefix='e16j-') as temp:
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
        subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',temp],env=env,check=True,timeout=cfg['budget_seconds'])
        for name in ['checks.csv','segments.csv','searches.csv','vertices.csv','resolutions.csv','cases.csv','summary.json','provenance.json']:
            assert (Path(temp)/name).read_bytes()==(result/name).read_bytes(),name
        assert json.loads((Path(temp)/'resources.json').read_text())['within_budget']
    assert json.loads((result/'resources.json').read_text())['within_budget']
    print('PASS_REPRODUCTION: ocho salidas idénticas, congelación, fuentes y alcance; T2-A intacto. Resultado científico global: INCONCLUSIVE.')

if __name__=='__main__':main()
