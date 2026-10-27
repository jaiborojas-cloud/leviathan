"""Potencia preparatoria: fuentes por SHA y solo piloto G3 como tabla."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[5]
STAGE=ROOT/'experiments/DIN_borde/Q13M2/potencia_preparacion'
CFG=json.loads((STAGE/'config_v1.json').read_text())
SOURCES={s['key']:s for s in CFG['sources']}
OUT=STAGE/'results_v1'
EXTERNAL=Path(CFG['arrays_root'])


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def source_path(key):
    s=SOURCES[key];return STAGE/s['snapshot'] if 'snapshot' in s else ROOT/s['path']


def write(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')


def code_guard():
    files=list((STAGE/'scripts').glob('*.py'))+[STAGE/'config_v1.json',STAGE/'PROCEDIMIENTO_v1_CONGELADO.md',STAGE/'DECISION_TRUNCAMIENTO.md']
    for p in files:
        if p.read_bytes()!=subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(ROOT))],cwd=ROOT):raise RuntimeError('Código/config sin comprometer:'+str(p))
    for k,s in SOURCES.items():
        if sha(source_path(k))!=s['sha256']:raise RuntimeError('SHA fuente incorrecto:'+k)


def guard():
    allowed={source_path(k).resolve() for k in SOURCES}
    def audit(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
        p=Path(os.fsdecode(args[0])).resolve()
        if p in allowed or p.is_relative_to(STAGE) or p.is_relative_to(EXTERNAL):return
        if p.is_relative_to(ROOT/'experiments') or p.is_relative_to(ROOT/'docs/archive') or p.suffix.lower() in ('.csv','.npz','.npy','.pt','.pth'):
            raise PermissionError('Potencia M2: acceso no autorizado:'+str(p))
    sys.addaudithook(audit)


def functions(key,names,env):
    p=source_path(key);text=p.read_text();tree=ast.parse(text)
    nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names]
    assert {n.name for n in nodes}==set(names)
    for n in nodes:exec(compile(ast.get_source_segment(text,n),str(p),'exec'),env)
    return env


def engine():
    e=functions('engine',('cen','pinv','BatchedC1'),dict(np=np))
    e=functions('bootstrap_engine',('grouped_bootstrap',),e)
    return e['BatchedC1'],e['cen'],e['grouped_bootstrap']


def analyst():
    p=source_path('M2');spec=importlib.util.spec_from_file_location('m2_preparation_only',p)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    assert tuple(CFG['primary_quantiles'])==m.Q_PRI
    assert CFG['levels']==m.NOMBRES
    return m
