#!/usr/bin/env python3
"""Integridad, controles geométricos y reproducción de E16-N."""
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def main():
    cfg=json.loads((ROOT/'config.json').read_text())
    for manifest in ['freeze_manifest.csv','implementation_manifest.csv','manifest.csv']:
        for row in csv.DictReader((ROOT/manifest).open()):assert sha(ROOT/row['path'])==row['sha256'],row['path']
    for name in ['config.json','groups.json','DESIGN_FROZEN.md','freeze_manifest.csv']:
        assert git('show',f'e21d2f6:experiments/E16/N/{name}')==(ROOT/name).read_bytes(),name
    assert git('show','e6af3bd:experiments/E16/N/implementation_manifest.csv')==(ROOT/'implementation_manifest.csv').read_bytes()
    for p,h in cfg['sources'].items():assert sha(ROOT.parent/p)==h,p
    allowed={'docs/experiment-index.md','docs/roadmap.md','experiments/README.md'}
    changed=git('diff','--name-only',cfg['base_commit'],'--').decode().splitlines()
    assert all(p.startswith('experiments/E16/N/') or p in allowed for p in changed),changed
    assert not git('diff',cfg['base_commit'],'--','experiments/T2_A','experiments/E16/M','experiments/E16/K')
    spec=importlib.util.spec_from_file_location('hd_verify',ROOT/'scripts/hausdorff.py');hd=importlib.util.module_from_spec(spec);spec.loader.exec_module(hd)
    controls=hd.controls();assert len(controls)==3
    spec=importlib.util.spec_from_file_location('kernel_verify',ROOT/'scripts/grid_kernel.py');kernel=importlib.util.module_from_spec(spec);spec.loader.exec_module(kernel)
    import numpy as np
    for m in [32,64]:assert np.array_equal(kernel.grid(m),kernel.grid(2*m)[::2])
    out=ROOT/'results/run_v1';s=json.loads((out/'summary.json').read_text())
    assert s['status']=='INCONCLUSIVE' and s['validated_trajectories']==s['trajectories']==9 and s['optimizations']==9
    assert s['check_counts']=={'PASS':7503,'FAIL':0,'INCONCLUSIVE':8}
    failed=[r for r in csv.DictReader((out/'checks.csv').open()) if r['status']!='PASS']
    assert len(failed)==8 and all(r['category'] in ['shape','hausdorff'] for r in failed)
    assert all(r['spd']=='True' for r in csv.DictReader((out/'trajectories.csv').open()))
    comparisons=list(csv.DictReader((out/'hausdorff.csv').open()));assert len(comparisons)==21
    assert all(float(r['upper'])>=float(r['lower']) and float(r['gap'])<=1e-5 for r in comparisons)
    names=[p.name for p in sorted(out.iterdir()) if p.suffix in ['.csv','.json'] and p.name!='resources.json']
    assert len(names)==14
    with tempfile.TemporaryDirectory(prefix='e16n-') as tmp:
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
        subprocess.run([sys.executable,str(ROOT/'scripts/run.py'),'--out',tmp],env=env,check=True,timeout=cfg['budget_seconds'])
        for name in names:assert (Path(tmp)/name).read_bytes()==(out/name).read_bytes(),name
        assert json.loads((Path(tmp)/'resources.json').read_text())['within_budget']
    assert json.loads((out/'resources.json').read_text())['within_budget']
    print('PASS_REPRODUCTION: 14 salidas idénticas; cotas y controles Hausdorff, anidamiento y protocolo verificados; M/T2-A intactos.')
if __name__=='__main__':main()
