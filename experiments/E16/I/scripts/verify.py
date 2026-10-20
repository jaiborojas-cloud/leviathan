#!/usr/bin/env python3
"""Integridad, alcance y reproducción de E16-I; no recalcula fases anteriores."""
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
        assert git('show',f'acab94e:experiments/E16/I/{name}')==(ROOT/name).read_bytes(),name
    for path,key in [('H/data.json','H_data_sha256'),('D/scripts/run.py','D_method_sha256'),('G/scripts/run.py','G_method_sha256')]:
        assert sha(ROOT.parent/path)==cfg[key],path
    data=json.loads((ROOT.parent/'H/data.json').read_text())
    assert cfg['states']==list(data['states'])[:3] and cfg['panel']=='P0' and not data['trained']
    gcfg=json.loads((ROOT.parent/'G/config.json').read_text())
    for key in ['precision','precision_tolerance','identity_tolerance','fine_tolerance','coarse_tolerance']:
        assert cfg[key]==gcfg[key],key
    changed=git('diff','--name-only',cfg['base_commit'],'--').decode().splitlines()
    allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'}
    assert all(x.startswith('experiments/E16/I/') or x in allowed for x in changed),changed
    assert not git('diff',cfg['base_commit'],'--','experiments/T2_A','experiments/E16/G','experiments/E16/H')
    result=ROOT/'results/run_v1';s=json.loads((result/'summary.json').read_text())
    assert s['cases']==27 and s['counts']=={'PASS_NUMERICAL':27,'FAIL':0,'INCONCLUSIVE':0}
    assert s['check_counts']=={'PASS':5533,'FAIL':0,'INCONCLUSIVE':0}
    assert s['descriptive']['sum']['improved']==0
    assert s['descriptive']['product']['improved']==s['descriptive']['quadratic']['improved']==9
    assert len(list(csv.DictReader((result/'segments.csv').open())))==216
    assert len(list(csv.DictReader((result/'optimizers.csv').open())))==54
    with tempfile.TemporaryDirectory(prefix='e16i-') as temp:
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
        subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',temp],env=env,check=True,timeout=cfg['budget_seconds'])
        for name in ['cases.csv','checks.csv','optimizers.csv','search_trace.csv','segments.csv','summary.json','provenance.json']:
            assert (Path(temp)/name).read_bytes()==(result/name).read_bytes(),name
        assert json.loads((Path(temp)/'resources.json').read_text())['within_budget']
    assert json.loads((result/'resources.json').read_text())['within_budget']
    print('PASS_REPRODUCTION: siete salidas idénticas, fuentes, congelación y alcance verificados; T2-A y evidencia previa intactos.')

if __name__=='__main__':main()
