#!/usr/bin/env python3
"""Verifica sorteos sin selección, método intacto y reproducción E16-H."""
import argparse
import ast
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import numpy as np

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def functions(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef)}

def main(reproduce=True):
    cfg=json.loads((ROOT/'config.json').read_text());data=json.loads((ROOT/'data.json').read_text())
    for name in ['freeze_manifest.csv','manifest.csv']:
        for row in csv.DictReader((ROOT/name).open()):
            assert sha(ROOT/row['path'])==row['sha256'],row['path']
    for name in ['config.json','data.json','DESIGN_FROZEN.md','freeze_manifest.csv']:
        assert git('show',f'3c96c95:experiments/E16/H/{name}')==(ROOT/name).read_bytes(),name
    allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'}
    scope_base=json.loads((ROOT/'integration.json').read_text())['upstream_scope_base']
    subprocess.run(['git','merge-base','--is-ancestor',cfg['base_commit'],scope_base],cwd=REPO,check=True)
    assert not git('diff',cfg['base_commit'],scope_base,'--','experiments/E16/G','experiments/E16/F','experiments/T2_A')
    changed=git('diff','--name-only',scope_base,'--').decode().splitlines()
    assert all(p.startswith('experiments/E16/H/') or p in allowed for p in changed),changed
    assert not git('diff',cfg['base_commit'],'--','experiments/T2_A','experiments/E16/G','experiments/E16/F')
    def draw(seed,shape,low,high):return np.round(np.random.Generator(np.random.PCG64(seed)).uniform(low,high,shape),6).tolist()
    assert list(data['states'].values())==draw(data['seeds']['weights'],(12,9),-.8,.8)
    assert data['inputs']==draw(data['seeds']['inputs'],(12,2),-1.2,1.2)
    assert data['perspectives']==draw(data['seeds']['perspectives'],(3,2),-1.2,1.2)
    old=json.loads((ROOT.parent/'D/config.json').read_text())
    for key in ['states','inputs','perspectives']:
        fresh=list(data[key].values()) if key=='states' else data[key]
        previous=list(old[key].values()) if key=='states' else old[key]
        assert not {tuple(x) for x in fresh}&{tuple(x) for x in previous},key
    for name in ['weights','inputs']:assert data['seeds'][name]!=old['seeds'][name]
    assert data['rho']==old['rho'] and not data['trained']
    source=ROOT.parent/'G/scripts/run.py'
    assert sha(source)==cfg['source_G_sha256']
    gcfg=json.loads((ROOT.parent/'G/config.json').read_text())
    for key in set(gcfg)-{'base_commit','source_config_sha256','F_lengths_sha256'}:
        assert cfg[key]==gcfg[key],key
    gf=functions(source);hf=functions(ROOT/'scripts/run.py')
    for key in set(gf)-{'main'}:assert gf[key]==hf[key],key
    spec=importlib.util.spec_from_file_location('adapter_h',ROOT/'scripts/adapt_from_G.py')
    adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
    assert adapter.adapt(source.read_text())==(ROOT/'scripts/run.py').read_text()
    result=ROOT/'results/run_v1';s=json.loads((result/'summary.json').read_text())
    assert s['status']=='PASS_NUMERICAL' and s['lengths']==324 and s['paired']==216
    assert s['counts']=={'PASS_NUMERICAL':324,'FAIL':0,'INCONCLUSIVE':0}
    assert s['check_counts']=={'PASS':13102,'FAIL':0,'INCONCLUSIVE':0}
    assert json.loads((result/'resources.json').read_text())['within_budget']
    if not reproduce:
        print('PASS_INTEGRITY: sorteos, fuentes, AST, adaptación, congelación y alcance tras integrar actualización remota. No se ejecutó experimento.')
        return
    with tempfile.TemporaryDirectory(prefix='e16h-') as temp:
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
        subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',temp],env=env,check=True,timeout=cfg['budget_seconds'])
        for name in ['lengths.csv','checks.csv','paired_ratios.csv','summary.json','provenance.json']:
            assert (Path(temp)/name).read_bytes()==(result/name).read_bytes(),name
        assert json.loads((Path(temp)/'resources.json').read_text())['within_budget']
    assert json.loads((result/'resources.json').read_text())['within_budget']
    print('PASS_REPRODUCTION: sorteos sin selección, novedad frente a D, 14 funciones G idénticas, adaptación exacta y cinco salidas reproducidas; evidencia previa intacta.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--integrity-only',action='store_true')
    main(reproduce=not parser.parse_args().integrity_only)
