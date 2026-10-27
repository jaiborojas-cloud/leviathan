"""Fuentes por SHA,datos sintéticos y referencia LS explícita únicamente."""
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[6]
STAGE=ROOT/'experiments/DIN_borde/Q13M2/auditoria/verificacion_v2'
CFG=json.loads((STAGE/'config.json').read_text())
PROV=json.loads((STAGE/'sources/provenance.json').read_text())
EXT=Path(CFG['external_root'])
LS=ROOT/PROV['LS_reference']['path']


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def clean(x):
    if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v) for v in x]
    if isinstance(x,np.ndarray):return clean(x.tolist())
    if isinstance(x,np.generic):return clean(x.item())
    if isinstance(x,float) and not math.isfinite(x):return str(x)
    return x


def write(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(clean(x),f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')


def code_guard():
    for p in list((STAGE/'scripts').glob('*.py'))+[STAGE/'config.json',STAGE/'DESIGN_FROZEN.md']:
        if p.read_bytes()!=subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(ROOT))],cwd=ROOT):raise RuntimeError('Código no comprometido:'+str(p))
    for s in PROV['sources']:
        if sha(STAGE/s['snapshot'])!=s['sha256']:raise RuntimeError('Snapshot alterado:'+s['snapshot'])


def guard(allow_LS=False):
    def audit(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
        p=Path(os.fsdecode(args[0])).resolve()
        if p.is_relative_to(STAGE) or p.is_relative_to(EXT) or allow_LS and p==LS.resolve():return
        if p.is_relative_to(ROOT/'experiments') or p.is_relative_to(ROOT/'docs/archive') or p.suffix.lower() in ('.csv','.npz','.npy','.pt','.pth'):
            raise PermissionError('Auditoría M2: acceso prohibido:'+str(p))
    sys.addaudithook(audit)


def target(version='v2'):
    p=STAGE/('sources/'+version+'/Q13M2/analisis_Q13M2.py');spec=importlib.util.spec_from_file_location('m2_audit_target_'+version,p)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def fixture(n=20):
    g=np.random.default_rng(CFG['case_seed']);X=-4+.25*g.normal(size=(n,5));L=g.normal(size=(n,5));rows=[]
    amps=[.8,.6,.45,.25,.10,0,.6,.45,.25,.10,.01]
    for l,nv in enumerate(['A0']+[f'LP{i}' for i in range(1,6)]+[f'WD{i}' for i in range(1,6)]):
        Y=.2*L+amps[l]*(X-X.mean(axis=1,keepdims=True))+.04*g.normal(size=(n,5))
        for s in range(n):
            for k in range(5):rows.append(dict(trajectory=f'q13m2_{nv}_s{s:04d}_k{k}',nivel=nv,split=s,k=k,X10=float(X[s,k]),
                rho_caras_10=float(np.exp(L[s,k])),rho_caras_250=float(np.exp(Y[s,k])),c250=CFG['c'][l],q250=.001,acc_panel250=.93,error=''))
    return rows


def execute(m,rows,n,**kw):
    args=dict(B=CFG['case_B'],NB=CFG['case_NB']);args.update(kw)
    return m.analizar(rows,n,True,'',**args)


def wilson(k,n):
    if not n:return dict(k=0,n=0,rate=None,lower=None,upper=None)
    z=1.959963984540054;p=k/n;den=1+z*z/n;mid=(p+z*z/(2*n))/den;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return dict(k=int(k),n=int(n),rate=p,lower=mid-h,upper=mid+h)
