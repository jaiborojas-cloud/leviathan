"""Cierre exclusivo de manifests, sin nuevas mediciones ni cambios de fuentes."""
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess

S=Path(__file__).resolve().parents[1]
ROOT=S.parents[3]
EXCLUDE={'manifest.csv','manifest.sha256','PUBLICACION_v1.sha256'}


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(),parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s)))


def main():
    rel=Path(__file__).resolve().relative_to(ROOT).as_posix()
    assert Path(__file__).read_bytes()==subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT)
    p=load(S/'sources/provenance.json')
    assert all(sha(S/x['snapshot'])==x['sha256'] for x in p['sources'])
    assert sha(ROOT/p['LS_reference']['path'])==p['LS_reference']['sha256']
    changes=subprocess.check_output(['git','diff','--name-only',p['base_main']],cwd=ROOT,text=True).splitlines()
    assert all(x.startswith(S.relative_to(ROOT).as_posix()+'/') for x in changes)
    assert load(S/'verification.json')['status']=='PASS_AUDIT_INTEGRITY'
    assert load(S/'results/api_edges/results.json')['status']=='PASS_EXPECTED_API_BEHAVIOR'
    files=[x for x in S.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x.suffix!='.pyc']
    forbidden=[x for x in files if x.suffix.lower() in ['.npz','.npy','.pt','.pth','.zip']]
    assert not forbidden,forbidden
    for x in files:
        if x.suffix=='.json':load(x)
    with (S/'external_manifest.csv').open() as f:
        ext=list(csv.DictReader(f))
    cfg=load(S/'config.json');e=Path(cfg['external_root'])
    assert all(sha(e/x['path_relative_to_external_root'])==x['sha256'] for x in ext)
    result=dict(status='PASS_PUBLICATION_INTEGRITY',audited_commit=p['target_revision'],sources_unchanged=True,
        only_new_audit_files=True,external_members=len(ext),no_arrays_in_git_delivery=True,api_supplement_PASS=True,
        not_an_approval_to_freeze=True,analyst_or_design_modified=False)
    with (S/'verification_publicacion.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
    files=sorted(x for x in S.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x.suffix!='.pyc' and x.name not in EXCLUDE)
    members=[dict(path=x.relative_to(S).as_posix(),bytes=x.stat().st_size,sha256=sha(x)) for x in files]
    with (S/'manifest.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);w.writeheader();w.writerows(members)
    with (S/'manifest.sha256').open('x') as f:
        for x in members:f.write(x['sha256']+'  '+x['path']+'\n')
    with (S/'PUBLICACION_v1.sha256').open('x') as f:
        for name in ['manifest.csv','manifest.sha256']:f.write(sha(S/name)+'  '+name+'\n')
    assert all(sha(S/x['path'])==x['sha256'] for x in members)
    broken=[]
    docs=list(S.glob('*.md'))
    for doc in docs:
        for link in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
            if '://' in link:continue
            dest=link.split('#')[0]
            if dest and not (doc.parent/dest).exists():broken.append([doc.name,link])
    assert not broken,broken
    print(json.dumps(dict(status='PASS',members=len(members),external_members=len(ext),local_links_checked=True)))


if __name__=='__main__':main()
