"""Inventario portable r2; resultados científicos previos de solo lectura."""
import csv
import json
import shutil
import subprocess
from support import ROOT, STAGE, EXTERNAL, write, sha, code_guard


def main():
    code_guard()
    cached=[]
    for p in sorted(STAGE.rglob('*.pyc')):
        dest=EXTERNAL/'cache_r1'/p.relative_to(STAGE)
        dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('xb') as f:f.write(p.read_bytes())
        assert sha(dest)==sha(p)
        cached.append(dict(original=str(p.relative_to(STAGE)),archive=str(dest),sha256=sha(dest)))
    write(STAGE/'cache_r1_archive.json',dict(note='Cachés locales incluidas en r1, preservadas fuera de Git; excluidas del manifiesto portable.',files=cached))
    with (STAGE/'external_manifest_r2.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['path','bytes','sha256'],lineterminator='\n');w.writeheader()
        for p in sorted(EXTERNAL.rglob('*')):
            if p.is_file():w.writerow(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
    r=json.loads((STAGE/'verification.json').read_text())
    r.update(inventory_version=2,inventory_corrected=True,excluded_local_cache_files=len(cached),
             canonical_manifest='manifest_v2.sha256',r1_results_unchanged=True,
             r1_manifest_scope='Historical commit 51ada0ad and local cache; preserved, not canonical at current HEAD')
    write(STAGE/'verification_r2.json',r)
    files=[p for p in sorted(STAGE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.name not in ('manifest_v2.csv','manifest_v2.sha256')]
    versionable=set(subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard',str(STAGE.relative_to(ROOT))],cwd=ROOT,text=True).splitlines())
    assert all(str(p.relative_to(ROOT)) in versionable for p in files)
    assert not any(p.suffix in ('.npy','.npz','.pt','.pth','.zip') for p in files)
    with (STAGE/'manifest_v2.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['path','bytes','sha256'],lineterminator='\n');w.writeheader()
        for p in files:w.writerow(dict(path=str(p.relative_to(STAGE)),bytes=p.stat().st_size,sha256=sha(p)))
    with (STAGE/'manifest_v2.sha256').open('x') as f:
        for p in files+[STAGE/'manifest_v2.csv']:f.write(sha(p)+'  '+str(p.relative_to(STAGE))+'\n')
    print(json.dumps(dict(status=r['status'],portable_manifest_files=len(files)+1,caches_preserved=len(cached),scientific_results_unchanged=True)))


if __name__=='__main__':main()
