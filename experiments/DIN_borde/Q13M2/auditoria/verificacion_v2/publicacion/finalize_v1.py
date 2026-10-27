"""Verifica entrega y crea manifests exclusivos, sin mediciones adicionales."""
import ast
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

S=Path(__file__).resolve().parents[1]
ROOT=S.parents[4]
EXCLUDE={'manifest.csv','manifest.sha256','PUBLICACION_v1.sha256'}


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
    def bad(x):raise ValueError(x)
    return json.loads(p.read_text(),parse_constant=bad)
def function(p,n):return ast.dump(next(x for x in ast.parse(p.read_text()).body if isinstance(x,ast.FunctionDef) and x.name==n),include_attributes=False)


def main():
    rel=Path(__file__).resolve().relative_to(ROOT).as_posix()
    assert Path(__file__).read_bytes()==subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT)
    prov=load(S/'sources/provenance.json');cfg=load(S/'config.json')
    assert all(sha(S/x['snapshot'])==x['sha256'] for x in prov['sources'])
    assert sha(ROOT/prov['LS_reference']['path'])==prov['LS_reference']['sha256']
    assert sha(S/'sources/analista_v1_v2.diff')==prov['diff_sha256']
    changes=subprocess.check_output(['git','diff','--name-only',prov['base_main']],cwd=ROOT,text=True).splitlines()
    assert all(x.startswith(S.relative_to(ROOT).as_posix()+'/') for x in changes)
    v=load(S/'verification.json');assert v['checks_count']==63 and all(v['checks'].values())
    assert v['MC_repeated'] is False and v['reference_array_SHA_identical_v1']
    for name in ['fixture','execute']:
        assert function(S/'scripts/support.py',name)==function(S/'sources/auditoria_v1/scripts/support.py',name)
    baseline=load(S/'results/cases/baseline.json')['result'];healthy_checks=[]
    for nv,healthy in [('WD3','LP'),('LP3','WD')]:
        for kind in ['Y','X','L']:
            r=load(S/f'results/changed_cases/F01_{nv}_{kind}.json')['result']['target_result']
            names=['A0']+[healthy+str(i) for i in range(1,6)]
            assert all(r['primaria'][n]==baseline['primaria'][n] for n in names)
            healthy_checks.append(f'{nv}_{kind}')
    external=Path(cfg['external_root'])
    with (S/'external_manifest.csv').open() as f:members=list(csv.DictReader(f))
    for x in members:
        p=external/x['path']
        if x['kind']=='symlink':
            assert p.is_symlink() and os.readlink(p)==x['target'] and hashlib.sha256(os.readlink(p).encode()).hexdigest()==x['sha256']
        else:assert sha(p)==x['sha256']
    files=[x for x in S.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x.suffix!='.pyc']
    assert not [x for x in files if x.suffix.lower() in ['.npz','.npy','.pt','.pth','.zip']]
    for p in files:
        if p.suffix=='.json':load(p)
    result=dict(status='PASS_PUBLICATION_INTEGRITY',target_commit=prov['target_revision'],analyst_unchanged=True,only_new_verification_files=True,
        previous_63_checks_PASS=True,healthy_primary_dictionaries_exact=healthy_checks,fixture_execute_AST_unchanged=True,
        external_members_verified=len(members),MC_repeated=False,new_findings_preserved=['N01','N02'],not_an_approval_to_freeze=True)
    with (S/'verification_publicacion.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
    files=sorted(x for x in S.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x.suffix!='.pyc' and x.name not in EXCLUDE)
    rows=[dict(path=x.relative_to(S).as_posix(),bytes=x.stat().st_size,sha256=sha(x)) for x in files]
    with (S/'manifest.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['path','bytes','sha256'],lineterminator='\n');w.writeheader();w.writerows(rows)
    with (S/'manifest.sha256').open('x') as f:
        for r in rows:f.write(r['sha256']+'  '+r['path']+'\n')
    with (S/'PUBLICACION_v1.sha256').open('x') as f:
        for name in ['manifest.csv','manifest.sha256']:f.write(sha(S/name)+'  '+name+'\n')
    assert all(sha(S/r['path'])==r['sha256'] for r in rows)
    broken=[]
    for p in S.glob('*.md'):
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' in link:continue
            dest=link.split('#')[0]
            if dest and not (p.parent/dest).exists():broken.append([p.name,link])
    assert not broken,broken
    print(json.dumps(dict(status='PASS',members=len(rows),external_members=len(members),local_links_checked=True)))


if __name__=='__main__':main()
