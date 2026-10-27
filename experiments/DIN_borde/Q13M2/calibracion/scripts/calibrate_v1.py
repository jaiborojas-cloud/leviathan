"""DIN-Q13-M2: 7000 calibraciones, solo c250/q250/precisión."""
import concurrent.futures as cf
import csv
import datetime as dt
import hashlib
import json
import multiprocessing as mp
import platform
import subprocess
import time
import traceback
import warnings
import numpy as np
from recipe_v1 import dataset,initialize,metric
from recipe_m2 import update_m2
from support_m2 import ROOT,STAGE,CFG,OUT,EXTERNAL,sha,write,archive,frozen,guard,code_guard
from controls_v1 import controls
from summarize_v1 import summarize

CORE=None


def identity(task):
    a,d,s,k=task;return f'm2_{a}_d{d:g}_s{s:03d}_k{k}'


def trajectory(task):
    global CORE
    import torch
    torch.set_num_threads(1)
    if CORE is None:
        torch.set_num_interop_threads(1);guard();CORE=frozen('core')
    arm,dose,s,k=task;name=identity(task);start=time.perf_counter()
    rec=dict(id=name,brazo=arm,dosis=dose,split=s,k=k,status='FAILED',error='')
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter('always')
        try:
            Z,y,tr,va=dataset(CFG['split_seed_base']+s)
            rec['data_sha256']=hashlib.sha256(Z.tobytes()+y.tobytes()).hexdigest()
            model,opt,initial=initialize(CFG['init_seed_base']+5*s+k,arm,dose,torch)
            rec['initial_weights_sha256']=initial;rng=np.random.default_rng(CFG['batch_seed_base']+5*s+k);batches=hashlib.sha256()
            xt,yt=torch.tensor(Z[tr]),torch.tensor(y[tr],dtype=torch.long)
            for step in range(250):update_m2(model,opt,xt,yt,rng,batches,arm,dose,torch)
            c,q,acc,M,f=metric(model,Z,y,va,CORE,torch)
            if not all(np.isfinite(v) for v in (c,q,acc)):raise FloatingPointError('Medida no finita')
            weights={'weight_'+key:value.detach().numpy() for key,value in model.state_dict().items()}
            rec.update(c250=c,q250=q,acc_panel250=acc,batch_sha256=batches.hexdigest(),status='MEASURED',
                       array=archive(name,M=M,f=f,Z=Z,y=y,panel_ids=va,**weights))
        except Exception:rec['error']=traceback.format_exc()
        rec['warnings']=[dict(category=w.category.__name__,message=str(w.message)) for w in captured]
    rec['seconds']=time.perf_counter()-start;write(OUT/'records'/(name+'.json'),rec);return rec


def bounded(pool,tasks,deliver):
    it=iter(tasks);pending=set()
    for _ in range(min(CFG['workers'],len(tasks))):pending.add(pool.submit(trajectory,next(it)))
    try:
        while pending:
            done,_=cf.wait(pending,return_when=cf.FIRST_COMPLETED)
            for f in done:
                r=f.result();pending.remove(f);deliver(r)
            for _ in done:
                task=next(it,None)
                if task is not None:pending.add(pool.submit(trajectory,task))
    except BaseException:
        for f in pending:f.cancel()
        pool.shutdown(wait=True,cancel_futures=True);raise


def main():
    versions=code_guard();OUT.mkdir(exist_ok=False);(OUT/'records').mkdir();EXTERNAL.mkdir(exist_ok=False)
    write(OUT/'environment.json',dict(utc=dt.datetime.now(dt.timezone.utc).isoformat(),python=platform.python_version(),platform=platform.platform(),
        versions=versions,workers=CFG['workers'],BLAS_threads=1,code_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()))
    guard();start=time.perf_counter()
    try:
        control=controls();write(OUT/'controls.json',control)
        if control['status']!='PASS':raise RuntimeError('Controles previos fallidos; no medir')
        conditions=[('A0',0.)]+[(a,d) for a in ('LP','WD') for d in CFG[a]]
        tasks=[(a,d,s,k) for a,d in conditions for s in range(CFG['splits']) for k in range(5)]
        assert len(tasks)==7000 and len({identity(t) for t in tasks})==7000
        count=0
        def deliver(r):
            nonlocal count
            count+=1
            if count%100==0 or r['status']!='MEASURED':print(json.dumps(dict(done=count,total=7000,id=r['id'],status=r['status'],minutes=(time.perf_counter()-start)/60)),flush=True)
        interrupted=None
        try:
            with cf.ProcessPoolExecutor(max_workers=CFG['workers'],mp_context=mp.get_context('spawn')) as pool:bounded(pool,tasks,deliver)
        except BaseException:
            interrupted=traceback.format_exc();write(OUT/'RUN_INTERRUPTION.json',dict(error=interrupted))
        records=[]
        for task in tasks:
            p=OUT/'records'/(identity(task)+'.json')
            if not p.exists():
                a,d,s,k=task;write(p,dict(id=identity(task),brazo=a,dosis=d,split=s,k=k,status='FAILED',error='INTERRUPTED_BEFORE_RESULT; ver RUN_INTERRUPTION.json'))
            records.append(json.loads(p.read_text()))
        pairing=[]
        for s in range(CFG['splits']):
            for k in range(5):
                rr=[r for r in records if r['split']==s and r['k']==k]
                errors=[key for key in ('data_sha256','initial_weights_sha256','batch_sha256') if len({r[key] for r in rr if key in r})>1]
                pairing.append(dict(split=s,k=k,pass_test=not errors,errors=errors))
        fields=['id','brazo','dosis','split','k','c250','q250','acc_panel250','status','error']
        with (OUT/'calibracion.csv').open('x',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(records)
        result,draws=summarize(records,conditions)
        result.update(status='CALIBRACION_COMPLETA' if all(r['status']=='MEASURED' for r in records) else 'CALIBRACION_CON_FALLOS',
            planned=7000,measured=sum(r['status']=='MEASURED' for r in records),failed=sum(r['status']!='MEASURED' for r in records),
            tabla_sha256=sha(OUT/'calibracion.csv'),protocol_sha256=CFG['sources']['protocol']['sha256'],
            data_initial_batches_paired=all(r['pass_test'] for r in pairing),X_computed=False,rho_computed=False,D_computed=False,associations_computed=False,
            confirmatory_cohort_started=False,seconds=time.perf_counter()-start)
        if not result['data_initial_batches_paired']:result['status']='INTEGRITY_FAILURE';result['elegibilidad_confiable']=False
        boot=archive('bootstrap_splits_904001',draws=draws)
        write(OUT/'pairing.json',dict(status='PASS' if all(r['pass_test'] for r in pairing) else 'FAIL',pairs=pairing))
        write(OUT/'bootstrap.json',boot);write(OUT/'summary.json',result)
        print(json.dumps({k:v for k,v in result.items() if k!='conditions'},ensure_ascii=False),flush=True)
    except BaseException:
        write(OUT/'FAILURE.json',dict(error=traceback.format_exc(),calibration_started=True));raise


if __name__=='__main__':main()
