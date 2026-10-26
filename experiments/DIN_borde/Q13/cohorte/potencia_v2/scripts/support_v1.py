"""Sólo fuentes congeladas, piloto G3 permitido y nuevas simulaciones."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import types

ROOT=Path(__file__).resolve().parents[6]
STAGE=ROOT/'experiments/DIN_borde/Q13/cohorte/potencia_v2'
CFG=json.loads((STAGE/'config_v1.json').read_text())
OUT=STAGE/'results_v1'
EXTERNAL=Path(CFG['arrays_dir'])


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,value):
    with Path(path).open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False)
        f.write('\n')


def code_guard():
    for path in list((STAGE/'scripts').glob('*.py'))+[STAGE/'config_v1.json',STAGE/'PROCEDIMIENTO_CONGELADO_v1.md']:
        if subprocess.check_output(['git','show','HEAD:'+str(path.relative_to(ROOT))],cwd=ROOT)!=path.read_bytes():
            raise RuntimeError('Código/configuración no comprometidos: '+str(path))
    for s in CFG['sources'].values():
        if sha(ROOT/s['path'])!=s['sha256']:
            raise RuntimeError('SHA fuente incorrecto: '+s['path'])


def guard():
    allowed={str((ROOT/s['path']).resolve()) for s in CFG['sources'].values()}
    roots=[str(STAGE.resolve())+'/',str(EXTERNAL.resolve())+'/']
    def audit(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
        p=str(Path(os.fsdecode(args[0])).resolve())
        if p in allowed or any(p.startswith(r) for r in roots):return
        if p.startswith(str(ROOT/'experiments')+'/') or '/docs/archive/' in p or p.endswith(('.csv','.npz','.npy','.pt','.pth')):
            raise PermissionError('Potencia Q13: datos no autorizados: '+p)
    sys.addaudithook(audit)


def analyst():
    source=ROOT/CFG['sources']['Q13']['path']
    module=types.ModuleType('q13_simulation_only')
    module.__file__=str(source)
    exec(compile(source.read_bytes(),str(source),'exec'),module.__dict__)
    return module
