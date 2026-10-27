"""Acceso limitado: piloto G3, correlación Q13 autorizada y fuentes por SHA."""
import ast
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import types
import numpy as np

ROOT=Path(__file__).resolve().parents[6]
STAGE=ROOT/'experiments/DIN_borde/Q13DR/cohorte'
CFG=json.loads((STAGE/'config_potencia_v1.json').read_text())
OUT=STAGE/'potencia/results_v1'
EXTERNAL=Path(CFG['arrays_dir'])


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(p,value):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')


def code_guard():
    paths=list((STAGE/'potencia/scripts').glob('*.py'))+[STAGE/'config_potencia_v1.json',STAGE/'PROCEDIMIENTO_POTENCIA_v1_CONGELADO.md']
    for p in paths:
        if p.read_bytes()!=subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(ROOT))],cwd=ROOT):raise RuntimeError('Código sin comprometer:'+str(p))
    for s in CFG['sources'].values():
        if sha(ROOT/s['path'])!=s['sha256']:raise RuntimeError('SHA fuente alterado:'+s['path'])


def guard():
    allowed={(ROOT/s['path']).resolve() for s in CFG['sources'].values()}
    roots=[STAGE.resolve(),EXTERNAL.resolve()]
    def audit(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
        p=Path(os.fsdecode(args[0])).resolve()
        if p in allowed or any(p.is_relative_to(r) for r in roots):return
        if p.is_relative_to(ROOT/'experiments') or p.is_relative_to(ROOT/'docs/archive') or p.suffix.lower() in ('.csv','.npz','.npy','.pt','.pth'):
            raise PermissionError('DIN-Q13DR potencia: acceso no autorizado:'+str(p))
    sys.addaudithook(audit)


def functions(key,names,env):
    p=ROOT/CFG['sources'][key]['path'];tree=ast.parse(p.read_text(encoding='utf-8'))
    nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names]
    if {n.name for n in nodes}!=set(names):raise RuntimeError('Funciones fuente ausentes')
    for n in nodes:exec(compile(ast.get_source_segment(p.read_text(encoding='utf-8'),n),str(p),'exec'),env)
    return env


def engine():
    e=functions('C2_engine',('cen','pinv','BatchedC1'),dict(np=np))
    e=functions('Q13_power',('grouped_bootstrap',),e)
    return e['BatchedC1'],e['cen'],e['grouped_bootstrap']


def analyst():
    e=functions('C1',('cen','D_cv','primaria'),dict(np=np))
    A=types.SimpleNamespace(**{k:e[k] for k in ('cen','D_cv','primaria')})
    e=functions('Q13',('bloques','D_punto'),dict(np=np,A=A))
    Q=types.SimpleNamespace(**{k:e[k] for k in ('bloques','D_punto')})
    e=functions('DR',('pendiente','clasificar_beta','equivalencia','clasificar_extremo','rango_c'),dict(np=np,math=math))
    return A,Q,types.SimpleNamespace(**{k:e[k] for k in ('pendiente','clasificar_beta','equivalencia','clasificar_extremo','rango_c')})
