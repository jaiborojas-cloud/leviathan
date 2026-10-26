"""DIN-Q13 v2: productor Windows/Linux aislado; nunca ejecuta análisis de asociación."""
from __future__ import annotations
import argparse
import ast
import base64
import concurrent.futures as cf
import csv
import datetime as dt
import hashlib
import importlib.metadata
import io
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import platform
import sys
import time
import traceback
import types
import uuid
import warnings

RECIPE_SOURCE = r'''"""Receta G3/C2: únicamente cambia la pérdida o el optimizador por brazo."""
import hashlib
import math
import numpy as np


def network(torch):
    class Network(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.l1 = torch.nn.Linear(13, 64)
            self.l2 = torch.nn.Linear(64, 32)
            self.l3 = torch.nn.Linear(32, 3)
        def forward(self, x):
            return self.l3(torch.relu(self.l2(torch.relu(self.l1(x)))))
    return Network().double()


def dataset(seed):
    from sklearn.preprocessing import StandardScaler
    means = np.zeros((3, 13))
    means[:, :2] = [[2., 0.], [-1., math.sqrt(3)], [-1., -math.sqrt(3)]]
    y = np.repeat(np.arange(3), 39)
    tr = np.array([39*c+i for c in range(3) for i in range(30)], dtype=np.int64)
    va = np.array([39*c+i for c in range(3) for i in range(30, 39)], dtype=np.int64)
    epsilon = np.random.default_rng(seed).normal(size=(117, 13))
    raw = means[y]+.8*epsilon
    scaler = StandardScaler().fit(raw[tr])
    Z = scaler.transform(raw)
    return Z, y, tr, va


def initialize(init_seed, arm, dose, torch):
    torch.manual_seed(init_seed)
    model = network(torch)
    initial = hashlib.sha256(b''.join(p.detach().numpy().tobytes() for p in model.parameters())).hexdigest()
    optimizer = (torch.optim.AdamW(model.parameters(), lr=.006, weight_decay=dose) if arm == 'WD'
                 else torch.optim.Adam(model.parameters(), lr=.006))
    return model, optimizer, initial


def update(model, optimizer, xt, yt, rng, batches, arm, dose, torch):
    ids = rng.choice(len(xt), size=64, replace=False)
    batches.update(np.asarray(ids, dtype=np.int64).tobytes())
    optimizer.zero_grad()
    loss = torch.nn.functional.cross_entropy(model(xt[ids]), yt[ids], label_smoothing=dose if arm == 'LS' else 0.)
    if not torch.isfinite(loss):
        raise RuntimeError('Pérdida no finita')
    loss.backward()
    optimizer.step()


def metric(model, Z, y, va, core, torch):
    Rb, Ub, fp = core.make_geom_state(model, torch.tensor(Z[va]), torch.tensor(y[va]))
    M = core.subset_M(Rb, Ub, [0, 1, 2]).numpy()
    f = fp.numpy()
    diag = np.diag(M)
    trace = float(np.trace(M))
    norm = float(np.linalg.norm(M))
    if not np.isfinite(M).all() or trace <= 0 or norm <= 0:
        raise RuntimeError('M inválida')
    c = float(diag.max()/trace)
    q = float(np.linalg.norm(M-np.diag(diag))/norm)
    with torch.no_grad():
        acc = float((model(torch.tensor(Z[va])).argmax(1) == torch.tensor(y[va])).double().mean())
    return c, q, acc, M, f
'''

SUPPORT_SOURCE = r'''"""IO exclusivo y acceso limitado del generador de Q13."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import types
import numpy as np

ROOT = Path(__file__).resolve().parents[5]
STAGE = ROOT/'experiments/DIN_borde/Q13/cohorte'
CFG = json.loads((STAGE/'config_v1.json').read_text())
EXTERNAL = Path(CFG['arrays_root'])


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    with Path(path).open('x') as file:
        json.dump(value, file, ensure_ascii=False, indent=2, allow_nan=False)
        file.write('\n')


def archive(name, **values):
    path = EXTERNAL/(name+'.npz')
    with path.open('xb') as file:
        np.savez_compressed(file, **values)
    return dict(path=str(path), sha256=sha(path), bytes=path.stat().st_size)


def frozen(name):
    s = CFG['sources'][name]
    p = ROOT/s['path']
    data = p.read_bytes()
    if hashlib.sha256(data).hexdigest() != s['sha256']:
        raise RuntimeError('Fuente modificada: '+name)
    mod = types.ModuleType('q13_frozen_'+name)
    mod.__file__ = str(p)
    exec(compile(data, str(p), 'exec'), mod.__dict__)
    return mod


def code_guard():
    paths = sorted((STAGE/'scripts').glob('*.py'))+[STAGE/'config_v1.json', STAGE/'PROCEDIMIENTO_v1.md']
    for p in paths:
        rel = str(p.relative_to(ROOT))
        if p.read_bytes() != subprocess.check_output(['git', 'show', 'HEAD:'+rel], cwd=ROOT):
            raise RuntimeError('Código sin comprometer: '+rel)
    for s in CFG['sources'].values():
        if sha(ROOT/s['path']) != s['sha256']:
            raise RuntimeError('Fuente no intacta: '+s['path'])
    base = ROOT/'experiments/DIN_borde'
    for line in (base/'Q13/MANIFIESTO_DIN_Q13_v1_CONGELADO.sha256').read_text().splitlines():
        expected, rel = line.split(maxsplit=1)
        if sha(base/rel) != expected:
            raise RuntimeError('Archivo congelado modificado: '+rel)


def guard():
    allowed = {str((ROOT/CFG['sources'][k]['path']).resolve()) for k in ('core','geometry','rho_v2')}
    roots = [str(STAGE.resolve())+'/', str(EXTERNAL.resolve())+'/']
    def audit(event, args):
        if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        p = str(Path(os.fsdecode(args[0])).resolve())
        if p in allowed or any(p.startswith(r) for r in roots):
            return
        if (p.startswith(str(ROOT/'experiments')+'/') or '/docs/archive/' in p or
            ('/sklearn/datasets/data/' in p and not p.endswith(('.py','.pyc'))) or
            ('/sklearn/datasets/descr/' in p and not p.endswith(('.py','.pyc'))) or
            p.endswith(('.csv','.npz','.npy','.pt','.pth'))):
            raise PermissionError('Q13 cohorte: lectura no autorizada: '+p)
    sys.addaudithook(audit)
'''



PLAN_SHA = 'e66b81aabe4c05361c2d8c9461fd5dea7c5de049fb5b3411378b76ff2d3669c3'
RECIPE_SHA = '3e3a7653889afde63a379ef2390a7b14faea0187358fe814348af70418d311b6'
SUPPORT_SHA = '29158f316c8a4b982e206a6588ad49702af8f3d0710326bfac190ebdc52285c1'
SOURCES = {
    'core': {'path': 'docs/archive/import-2026-10-17/extracted/j7_update25_execution_sources/core.py',
             'sha256': 'b5251d2f1f082ae014596574e9ab827dde04aec785bf76091005f8149ba31ffd'},
    'geometry': {'path': 'docs/archive/import-2026-10-17/extracted/j7_update25_execution_sources/instrument/geometry.py',
                 'sha256': 'b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3'},
    'rho_v2': {'path': 'experiments/DIN_borde/I2/rho_borde_v2.py',
               'sha256': '2ac015a263afb44616de0fceebd3b1d2a36ad0a76cd466adcdcc7e3adb8b8df0'}}
VERSIONS = {'torch': '2.9.1+cpu', 'numpy': '2.3.5', 'scipy': '1.17.0', 'scikit-learn': '1.8.0'}
COLUMNS = ['trajectory','brazo','split','k','X10','R250','c250','q250',
           'rho_caras_10','rho_caras_250','rho_vert_10','rho_vert_250',
           'acc_panel250','acc_train250','error']
VISITS = (5,10,30,250)
FORMAT = 'DIN-Q13-v2-portable-1'
CTX = None


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=True,separators=(',',':'),allow_nan=False).encode('utf-8')


def json_bytes(value):
    return (json.dumps(value,ensure_ascii=True,indent=2,allow_nan=False)+'\n').encode('utf-8')


def exclusive_bytes(path, data):
    """Publicar completo sin reemplazar: enlace atómico; fallback exclusivo conservador."""
    path=Path(path)
    temp=path.with_name(path.name+'.tmp.'+uuid.uuid4().hex)
    with temp.open('xb') as f:
        f.write(data);f.flush();os.fsync(f.fileno())
    try:
        try:
            os.link(temp,path)
        except FileExistsError:
            raise
        except OSError:
            # En un FS sin enlaces, un corte deja un archivo incompleto que se
            # conserva como fallo; nunca se sobreescribe ni se reentrena su ID.
            with path.open('xb') as f:
                f.write(data);f.flush();os.fsync(f.fileno())
    except BaseException:
        # Preservar temporal en fallo; no tocar ninguna salida previa.
        raise
    else:
        temp.unlink()


def exclusive_json(path,value):
    exclusive_bytes(path,json_bytes(value))


class FileLock:
    """Bloqueo del SO, liberado incluso al morir el proceso; Windows usa msvcrt."""
    def __init__(self,path):
        self.path=Path(path);self.file=None

    def __enter__(self):
        try:
            with self.path.open('xb') as f:f.write(b'1')
        except FileExistsError:
            pass
        self.file=self.path.open('r+b');self.file.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(self.file.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError:
            self.file.close();self.file=None
            raise RuntimeError('Hay otro proceso activo sobre '+str(self.path))
        return self

    def __exit__(self,*args):
        if self.file is not None:
            self.file.seek(0)
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(self.file.fileno(),msvcrt.LK_UNLCK,1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(),fcntl.LOCK_UN)
            self.file.close()


def universe(plan):
    return [(f'q13_{arm}_s{s:04d}_k{k}',arm,s,k)
            for arm in plan['brazos'] for s in range(plan['n_splits']) for k in range(5)]


def preflight(out):
    root=Path(__file__).resolve().parents[5]
    stage=root/'experiments/DIN_borde/Q13/cohorte'
    plan_path=stage/'q13_plan.json'
    if sha(plan_path)!=PLAN_SHA:raise RuntimeError('SHA del plan incorrecto; conservar bytes LF del repositorio')
    plan=json.loads(plan_path.read_text(encoding='utf-8'))
    if plan['n_splits']!=800 or plan['brazos']!=['A0','LS','WD'] or plan['dosis']!={'LS':.005,'WD':.2}:
        raise RuntimeError('Plan no coincide con tamaño/dosis autorizados')
    ids=[r[0] for r in universe(plan)]
    if len(ids)!=12000 or hashlib.sha256('\n'.join(ids).encode()).hexdigest()!=plan['ids_sha256']:
        raise RuntimeError('Universo del plan incorrecto')
    for name,source in SOURCES.items():
        if sha(root/source['path'])!=source['sha256']:raise RuntimeError('SHA incorrecto: '+name+'; no normalizar ni modificar el instrumento')
    for text,h in [(RECIPE_SOURCE,RECIPE_SHA),(SUPPORT_SOURCE,SUPPORT_SHA)]:
        if hashlib.sha256(text.encode('utf-8')).hexdigest()!=h:raise RuntimeError('Fuente embebida alterada')
    for name,h in [('recipe_v1.py',RECIPE_SHA),('support_v1.py',SUPPORT_SHA)]:
        if sha(stage/'scripts'/name)!=h:raise RuntimeError('Fuente original alterada: '+name)
    sidecar=stage/'scripts/cohorte_v2.sha256'
    script_sha=sha(Path(__file__).resolve())
    if script_sha!=sidecar.read_text(encoding='utf-8').split()[0]:raise RuntimeError('SHA del generador incorrecto; comprobar checkout LF')
    versions={k:importlib.metadata.version(k) for k in VERSIONS}
    if versions!=VERSIONS:raise RuntimeError('Versiones distintas: '+json.dumps(versions)+'; instalar requirements_windows_v2.txt')
    out=Path(out).expanduser().resolve()
    if out.is_relative_to(root):raise RuntimeError('--out debe estar fuera del checkout Git')
    return dict(root=str(root),stage=str(stage),out=str(out),plan=plan,plan_sha256=PLAN_SHA,
                script_sha256=script_sha,versions=versions)


def binding(ctx):
    return dict(formato=FORMAT,plan_sha256=PLAN_SHA,script_sha256=ctx['script_sha256'],
                fuentes=SOURCES,recipe_sha256=RECIPE_SHA,support_sha256=SUPPORT_SHA,versiones=ctx['versions'])


def bind_output(ctx):
    out=Path(ctx['out']);out.mkdir(parents=True,exist_ok=True)
    p=out/'VINCULO_q13.json';expected=binding(ctx)
    if p.exists():
        if json.loads(p.read_text(encoding='utf-8'))!=expected:raise RuntimeError('Carpeta vinculada a otro script/plan/entorno; no mezclar versiones')
    else:
        if any(out.iterdir()):raise RuntimeError('Carpeta no vacía sin vínculo Q13; usar una carpeta nueva')
        exclusive_json(p,expected)
    for name in ('claims','trajectories','arrays','gate_arrays','sessions'):(out/name).mkdir(exist_ok=True)


def portable_guard(ctx):
    root=Path(ctx['root']);out=Path(ctx['out'])
    allowed={(root/s['path']).resolve() for s in SOURCES.values()}
    def audit(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
        p=Path(os.fsdecode(args[0])).resolve()
        if p in allowed or p.is_relative_to(out):return
        if p.is_relative_to(root/'experiments') or p.is_relative_to(root/'docs/archive') or p.suffix.lower() in ('.csv','.npz','.npy','.pt','.pth'):
            raise PermissionError('Q13 productor: lectura no autorizada: '+str(p))
        parts={s.lower() for s in p.parts}
        if 'datasets' in parts and ('data' in parts or 'descr' in parts) and p.suffix.lower() not in ('.py','.pyc'):
            raise PermissionError('Q13: datos externos prohibidos: '+str(p))
    sys.addaudithook(audit)


def initialize_worker(ctx):
    global CTX
    for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[key]='1'
    import numpy as np
    import torch
    torch.set_num_threads(1);torch.set_num_interop_threads(1)
    root=Path(ctx['root'])
    # Un spawn independiente verifica las mismas fuentes antes de usarlas.
    for source in SOURCES.values():
        if sha(root/source['path'])!=source['sha256']:raise RuntimeError('SHA de fuente cambió en worker')
    env=dict(np=np,Path=Path,hashlib=hashlib,json=json,os=os,subprocess=None,sys=sys,types=types,
             ROOT=root,CFG={'sources':SOURCES},EXTERNAL=Path(ctx['out'])/'gate_arrays')
    exec(compile(RECIPE_SOURCE,'<recipe_v1.py intacta>','exec'),env)
    tree=ast.parse(SUPPORT_SOURCE)
    for node in tree.body:
        if isinstance(node,ast.FunctionDef) and node.name in ('sha','write','archive','frozen'):
            exec(compile(ast.get_source_segment(SUPPORT_SOURCE,node),'<support_v1.py intacto>','exec'),env)
    portable_guard(ctx)
    env['core']=env['frozen']('core') # establece float64 como en G3/C2
    env['rho']=env['frozen']('rho_v2')
    if env['rho'].IMPLEMENTATION_VERSION!='r3':raise RuntimeError('Instrumento no es r3')
    CTX=dict(ctx,env=env,torch=torch,np=np)


def clean(value):
    np=CTX['np']
    if isinstance(value,dict):return {str(k):clean(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [clean(v) for v in value]
    if isinstance(value,np.ndarray):return clean(value.tolist())
    if isinstance(value,np.generic):return clean(value.item())
    if isinstance(value,float) and not math.isfinite(value):return None
    return value


def reconstruct(j):
    env=CTX['env'];torch=CTX['torch'];np=CTX['np'];out=Path(CTX['out'])
    rec=dict(control=j,pass_test=False)
    try:
        Z,y,tr,va=env['dataset'](751000+j)
        torch.manual_seed(752000+j);model=env['network'](torch)
        R,U,f=env['core'].make_geom_state(model,torch.tensor(Z[va]),torch.tensor(y[va]))
        M=env['core'].subset_M(R,U,[0,1,2]).numpy()
        weights={'weight_'+k:v.detach().numpy() for k,v in model.state_dict().items()}
        saved=env['archive'](f'control_{j}',M=M,f=f.numpy(),Z=Z,y=y,panel_ids=va,**weights)
        restored=env['network'](torch)
        with np.load(saved['path'],allow_pickle=False) as data:
            restored.load_state_dict({k[7:]:torch.tensor(data[k]) for k in data.files if k.startswith('weight_')})
            r2,u2,f2=env['core'].make_geom_state(restored,torch.tensor(data['Z'][data['panel_ids']]),torch.tensor(data['y'][data['panel_ids']]))
            m2=env['core'].subset_M(r2,u2,[0,1,2]).numpy()
            err=float(np.linalg.norm(m2-data['M'])/max(np.linalg.norm(data['M']),np.finfo(float).tiny))
            same=bool(np.array_equal(f2.numpy(),data['f']))
        rec.update(relative_M_error=err,f_identical=same,pass_test=bool(err==0 and same),array=saved)
    except Exception:rec['error']=traceback.format_exc()
    return clean(rec)


def gate(ctx,processes):
    out=Path(ctx['out']);target=out/'COMPUERTA_q13.json'
    if target.exists():
        read_gate(ctx)
        print(json.dumps(dict(compuerta='PASA',reutilizada=True)),flush=True);return
    if any((out/'gate_arrays').iterdir()):raise RuntimeError('Compuerta interrumpida sin salida final; conservar y reportar, no sustituir')
    with cf.ProcessPoolExecutor(max_workers=min(processes,3),mp_context=mp.get_context('spawn'),initializer=initialize_worker,initargs=(ctx,)) as pool:
        records=list(pool.map(reconstruct,range(3)))
    result=dict(PASA=all(r['pass_test'] for r in records),script_sha256=ctx['script_sha256'],plan_sha256=PLAN_SHA,
                reconstrucciones=records,versiones=ctx['versions'],plataforma=platform.platform(),entrenamientos=0)
    exclusive_json(target,result)
    print(json.dumps(dict(PASA=result['PASA'],script_sha256=ctx['script_sha256'],reconstrucciones=len(records))),flush=True)
    if not result['PASA']:raise RuntimeError('Compuerta fallida: no entrenar')


def read_gate(ctx):
    p=Path(ctx['out'])/'COMPUERTA_q13.json';g=json.loads(p.read_text(encoding='utf-8'))
    if g.get('PASA') is not True or g.get('script_sha256')!=ctx['script_sha256'] or g.get('plan_sha256')!=PLAN_SHA:
        raise RuntimeError('Compuerta no válida o de otro script/plan')
    if len(g.get('reconstrucciones',[]))!=3:raise RuntimeError('Faltan reconstrucciones')
    for r in g['reconstrucciones']:
        if r.get('relative_M_error')!=0 or r.get('f_identical') is not True:raise RuntimeError('Reconstrucción no exacta')
        if sha(r['array']['path'])!=r['array']['sha256']:raise RuntimeError('Array de compuerta alterado')
    return g


def empty_row(task,error=''):
    identity,arm,s,k=task
    row={key:'' for key in COLUMNS};row.update(trajectory=identity,brazo=arm,split=s,k=k,error=error)
    return row


def seal_record(record):
    record['record_sha256']=hashlib.sha256(canonical(record)).hexdigest()
    return record


def read_record(ctx,task):
    p=Path(ctx['out'])/'trajectories'/(task[0]+'.json')
    if not p.exists():return None
    try:
        data=json.loads(p.read_text(encoding='utf-8'))
    except (ValueError,UnicodeError):return dict(row=empty_row(task,'RECORD_INCOMPLETE_PRESERVED'),seconds=0)
    if data.get('script_sha256')!=ctx['script_sha256'] or data.get('plan_sha256')!=PLAN_SHA:
        raise RuntimeError('Registro de otro plan/script: '+task[0])
    saved=data.get('record_sha256');body={k:v for k,v in data.items() if k!='record_sha256'}
    if saved!=hashlib.sha256(canonical(body)).hexdigest():raise RuntimeError('SHA del registro alterado: '+task[0])
    if data.get('row',{}).get('trajectory')!=task[0]:raise RuntimeError('ID de registro incorrecto')
    return data


def checkpoint(identity,model,optimizer,rng,step):
    env=CTX['env'];np=CTX['np'];torch=CTX['torch']
    values=dict(update=np.array(step),rng_state_utf8=np.frombuffer(json.dumps(rng.bit_generator.state).encode(),dtype=np.uint8))
    for k,v in model.state_dict().items():values['weight_'+k]=v.detach().numpy()
    for i,(_,p) in enumerate(model.named_parameters()):
        for k,v in optimizer.state[p].items():values[f'optimizer_{i}_{k}']=v.detach().numpy() if torch.is_tensor(v) else np.array(v)
    return env['archive'](f'u{step:03}_checkpoint',**values)


def measure(model,optimizer,rng,Z,y,tr,va,step):
    env=CTX['env'];torch=CTX['torch'];np=CTX['np']
    result=dict(update=step,status='FAILED')
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter('always')
        try:
            result['checkpoint']=checkpoint('',model,optimizer,rng,step)
            c,q,acc,M,f=env['metric'](model,Z,y,va,env['core'],torch)
            with torch.no_grad():
                logits=model(torch.tensor(Z[va]));logp=torch.log_softmax(logits,1)
                wrong=logits.clone();wrong[torch.arange(len(va)),torch.tensor(y[va])]=-torch.inf
                log1m=torch.logsumexp(wrong,1)-torch.logsumexp(logits,1)
                acc_train=float((model(torch.tensor(Z[tr])).argmax(1)==torch.tensor(y[tr])).double().mean())
            star=int(np.argmax(np.diag(M)))
            result['metrics']=dict(c=c,q=q,acc_panel=acc,acc_train=acc_train,X=float(log1m.max()),R=float(log1m[star]),k_star=star)
            result['array']=env['archive'](f'u{step:03}_state',M=M,f=f,logits=logits.numpy(),logpy=logp.numpy(),
                log1m=log1m.numpy(),labels=y[va],panel_ids=va)
            full=env['rho'].rho_borde_v2(M,f)
            diagnostic=Path(env['EXTERNAL'])/f'u{step:03}_rho.json'
            exclusive_json(diagnostic,clean(full))
            result['rho_diagnostic']=dict(path=str(diagnostic),sha256=sha(diagnostic),bytes=diagnostic.stat().st_size)
            result['rho']={key:full.get(key) for key in ('status','rho_caras','rho_vert','implementation_version','reason')}
            values=[full.get('rho_caras'),full.get('rho_vert')]
            valid=full.get('status')=='VALID_NUMERICAL_ESTIMATE' and full.get('implementation_version')=='r3' and all(
                isinstance(v,(int,float)) and math.isfinite(v) and v>0 for v in values)
            if valid:
                valid=values[0]<=values[1]
                for key in ('rho_caras_winner','rho_vert_winner'):
                    w=full[key];valid=valid and w['quad_error']<=1e-6*w['length'] and w['prefix_bound']+w['tail_bound']<=1e-6*w['length']
            result['status']='MEASURED' if valid else 'INVALID_RHO'
        except Exception:result['error']=traceback.format_exc()
        result['warnings']=[dict(category=w.category.__name__,message=str(w.message)) for w in captured]
    return clean(result)


def run_trajectory(task):
    identity,arm,s,k=task;ctx=CTX;out=Path(ctx['out']);start=time.perf_counter()
    target=out/'trajectories'/(identity+'.json')
    with FileLock(out/'claims'/(identity+'.lock')):
        old=read_record(ctx,task)
        if old is not None:return dict(id=identity,skipped=True,error=bool(old['row']['error']),seconds=0)
        claim=out/'claims'/(identity+'.json')
        row=empty_row(task);record=dict(script_sha256=ctx['script_sha256'],plan_sha256=PLAN_SHA,row=row,states=[])
        if claim.exists():
            row['error']='INTERRUPTED_CLAIM_PRESERVED_NO_RETRAIN'
        else:
            exclusive_json(claim,dict(trajectory=identity,script_sha256=ctx['script_sha256'],plan_sha256=PLAN_SHA,
                pid=os.getpid(),utc=dt.datetime.now(dt.timezone.utc).isoformat()))
            env=ctx['env'];torch=ctx['torch'];np=ctx['np']
            try:
                env['EXTERNAL']=out/'arrays'/identity;env['EXTERNAL'].mkdir(exist_ok=False)
                Z,y,tr,va=env['dataset'](711000+s)
                record['data_sha256']=hashlib.sha256(Z.tobytes()+y.tobytes()).hexdigest()
                dose=0. if arm=='A0' else ctx['plan']['dosis'][arm]
                model,opt,initial=env['initialize'](721000+5*s+k,arm,dose,torch)
                record['initial_weights_sha256']=initial
                rng=np.random.default_rng(731000+5*s+k);batches=hashlib.sha256()
                xt,yt=torch.tensor(Z[tr]),torch.tensor(y[tr],dtype=torch.long)
                for step in range(1,251):
                    env['update'](model,opt,xt,yt,rng,batches,arm,dose,torch)
                    if step in VISITS:record['states'].append(measure(model,opt,rng,Z,y,tr,va,step))
                record['batch_sha256']=batches.hexdigest()
            except Exception:row['error']=traceback.format_exc()
        by={r['update']:r for r in record['states']}
        for step in VISITS:
            if step not in by or by[step]['status']!='MEASURED':row['error']+=f' | u{step:03}:MISSING_OR_INVALID'
        early=by.get(10,{});last=by.get(250,{})
        row['X10']=early.get('metrics',{}).get('X','')
        for col,key in [('R250','R'),('c250','c'),('q250','q'),('acc_panel250','acc_panel'),('acc_train250','acc_train')]:
            row[col]=last.get('metrics',{}).get(key,'')
        for step,state in [(10,early),(250,last)]:
            for key in ('rho_caras','rho_vert'):row[f'{key}_{step}']=state.get('rho',{}).get(key,'')
        for key in COLUMNS[4:-1]:
            v=row[key]
            if not isinstance(v,(int,float)) or not math.isfinite(v):row['error']+=' | MISSING_OR_NONFINITE:'+key
            if key.startswith('rho_') and isinstance(v,(int,float)) and v<=0:row['error']+=' | NONPOSITIVE:'+key
        row['error']=row['error'].strip(' |')
        record['seconds']=time.perf_counter()-start
        exclusive_json(target,seal_record(clean(record)))
        return dict(id=identity,skipped=False,error=bool(row['error']),seconds=record['seconds'])


def pending_tasks(ctx,limit=None):
    out=Path(ctx['out']);all_tasks=universe(ctx['plan']);allowed={t[0] for t in all_tasks}
    if any(p.stem not in allowed for p in (out/'trajectories').glob('*.json')):raise RuntimeError('ID ajeno en carpeta de trayectorias')
    done={t[0] for t in all_tasks if read_record(ctx,t) is not None}
    # Ejecución pareada; el hash del universo y la tabla mantienen brazo→split→k.
    schedule=[(f'q13_{b}_s{s:04d}_k{k}',b,s,k) for s in range(800) for k in range(5) for b in ctx['plan']['brazos']]
    remaining=[t for t in schedule if t[0] not in done]
    return remaining if limit is None else remaining[:limit],len(done),len(remaining)


def cohort(ctx,processes,limit):
    read_gate(ctx);out=Path(ctx['out'])
    if (out/'q13_cohorte.csv').exists():raise RuntimeError('Tabla ya publicada; no añadir entrenamientos después de publicación')
    tasks,done,remaining=pending_tasks(ctx,limit)
    print(json.dumps(dict(trayectorias=12000,ya_escritas=done,pendientes=remaining,a_ejecutar=len(tasks),
                         procesos=processes,script_sha256=ctx['script_sha256'])),flush=True)
    start=time.perf_counter();results=[];session=out/'sessions'/('sesion_'+uuid.uuid4().hex+'.json')
    try:
        if tasks:
            with cf.ProcessPoolExecutor(max_workers=min(processes,len(tasks)),mp_context=mp.get_context('spawn'),
                    initializer=initialize_worker,initargs=(ctx,)) as pool:
                futures=[pool.submit(run_trajectory,t) for t in tasks]
                for f in cf.as_completed(futures):
                    rec=f.result();results.append(rec)
                    if len(results)%500==0 or len(results)==len(tasks):
                        print(f'[{len(results)}/{len(tasks)}] {rec["id"]} '+('error' if rec['error'] else 'ok')+
                              f' ({(time.perf_counter()-start)/60:.1f} min)',flush=True)
    except BaseException:
        exclusive_json(session,dict(status='INTERRUPTED',error=traceback.format_exc(),completed=results,
            script_sha256=ctx['script_sha256'],plan_sha256=PLAN_SHA,seconds=time.perf_counter()-start))
        raise
    elapsed=time.perf_counter()-start
    report=dict(status='COMPLETED_INVOCATION',plan_sha256=PLAN_SHA,script_sha256=ctx['script_sha256'],
        realizadas=len(results),errores=sum(r['error'] for r in results),ya_escritas=done,segundos_pared=elapsed,
        media_segundos_trayectoria=sum(r['seconds'] for r in results)/len(results) if results else None,
        segundos_pared_por_trayectoria=elapsed/len(results) if results else None,procesos=processes,
        limite=limit,resultados=results,plataforma=platform.platform(),versiones=ctx['versions'])
    exclusive_json(session,report)
    print(json.dumps({k:v for k,v in report.items() if k!='resultados'}),flush=True)


def table(ctx):
    read_gate(ctx);out=Path(ctx['out']);rows=[];failures={b:0 for b in ctx['plan']['brazos']}
    for task in universe(ctx['plan']):
        record=read_record(ctx,task)
        row=empty_row(task,'TRAJECTORY_MISSING') if record is None else record['row']
        if set(row)!=set(COLUMNS) or [str(row[k]) for k in ('trajectory','brazo','split','k')]!=[str(v) for v in task]:
            raise RuntimeError('Columnas o identidad incorrectas: '+task[0])
        failures[task[1]]+=bool(row['error']);rows.append(row)
    stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=COLUMNS,lineterminator='\n')
    writer.writeheader();writer.writerows(rows);data=stream.getvalue().encode('utf-8')
    p=out/'q13_cohorte.csv'
    if p.exists():
        if p.read_bytes()!=data:raise RuntimeError('Tabla previa distinta: preservar y reportar; no sobrescribir')
    else:exclusive_bytes(p,data)
    summary=dict(tabla_sha256=sha(p),plan_sha256=PLAN_SHA,script_sha256=ctx['script_sha256'])
    q=out/'RESUMEN_q13.json'
    if q.exists():
        if json.loads(q.read_text(encoding='utf-8'))!=summary:raise RuntimeError('Resumen previo distinto')
    else:exclusive_json(q,summary)
    print(json.dumps(dict(**summary,filas=len(rows),filas_con_error_por_brazo=failures)),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parte',choices=('compuerta','cohorte','tabla'),required=True)
    parser.add_argument('--procesos',type=int,default=12)
    parser.add_argument('--limite',type=int)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    if args.procesos<1 or (args.limite is not None and (args.limite<0 or args.parte!='cohorte')):
        parser.error('Procesos positivos; limite no negativo sólo para cohorte')
    ctx=preflight(args.out);bind_output(ctx)
    with FileLock(Path(ctx['out'])/'COORDINADOR.lock'):
        if args.parte=='compuerta':gate(ctx,args.procesos)
        elif args.parte=='cohorte':cohort(ctx,args.procesos,args.limite)
        else:table(ctx)


if __name__=='__main__':
    mp.freeze_support()
    main()
