"""Calibración Q13: sólo c250, q250 y precisión; no X ni rho ni asociaciones."""
import concurrent.futures as cf
import csv
import datetime
import hashlib
import json
import platform
import subprocess
import sys
import time
import traceback
import warnings
import numpy as np
from support_v1 import ROOT, STAGE, CFG, EXTERNAL, sha, write, archive, frozen, guard, code_guard
from recipe_v1 import dataset, initialize, update, metric

OUT = STAGE/'calibracion_v1'
CORE = None


def trajectory(task):
    global CORE
    import torch
    torch.set_num_threads(1)
    if CORE is None:
        torch.set_num_interop_threads(1)
        guard()
        CORE = frozen('core')
    arm, dose, split, k = task
    identity = f'cal_{arm}_d{dose:g}_s{split:02d}_k{k}'
    beginning = time.perf_counter()
    rec = dict(id=identity, brazo=arm, dosis=dose, split=split, k=k, status='FAILED', error=None)
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter('always')
        try:
            cfg = CFG['calibration']
            Z, y, tr, va = dataset(cfg['split_seed_base']+split)
            rec['data_sha256'] = hashlib.sha256(Z.tobytes()+y.tobytes()).hexdigest()
            model, optimizer, initial = initialize(cfg['init_seed_base']+5*split+k, arm, dose, torch)
            rec['initial_weights_sha256'] = initial
            rng = np.random.default_rng(cfg['batch_seed_base']+5*split+k)
            xt, yt = torch.tensor(Z[tr]), torch.tensor(y[tr], dtype=torch.long)
            batches = hashlib.sha256()
            for step in range(1,251):
                update(model, optimizer, xt, yt, rng, batches, arm, dose, torch)
            c, q, acc, M, f = metric(model, Z, y, va, CORE, torch)
            weights = {'weight_'+key:value.detach().numpy() for key,value in model.state_dict().items()}
            rec.update(c250=c, q250=q, acc_panel250=acc, batch_sha256=batches.hexdigest(), status='MEASURED',
                       array=archive(identity, M=M, f=f, Z=Z, y=y, panel_ids=va, **weights))
        except Exception:
            rec['error'] = traceback.format_exc()
        rec['warnings'] = [dict(category=w.category.__name__,message=str(w.message)) for w in captured]
    rec['seconds'] = time.perf_counter()-beginning
    write(OUT/'records'/(identity+'.json'),rec)
    return rec


def main():
    code_guard()
    OUT.mkdir(exist_ok=False)
    (OUT/'records').mkdir()
    EXTERNAL.mkdir(exist_ok=False)
    import torch, scipy, sklearn
    write(OUT/'environment.json', dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        python=sys.version,numpy=np.__version__,torch=torch.__version__,scipy=scipy.__version__,
        sklearn=sklearn.__version__,platform=platform.platform(),workers=2,BLAS_threads=1,
        code_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()))
    guard()
    for blocked in (ROOT/'experiments/DIN_borde/C2/cohorte/c2_cohorte.csv',ROOT/'experiments/T2_A1/baseline/probe.csv',ROOT/'experiments/DIN_borde/Q13/analisis_Q13.py'):
        try:
            blocked.open()
        except PermissionError:
            continue
        raise RuntimeError('Guarda no bloquea '+str(blocked))
    conditions = [('A0',0.)]+[(a,d) for a in ('LS','WD') for d in CFG['calibration'][a]]
    tasks = [(a,d,s,k) for a,d in conditions for s in range(20) for k in range(5)]
    start = time.perf_counter()
    records = []
    with cf.ProcessPoolExecutor(max_workers=2) as pool:
        for rec in pool.map(trajectory,tasks,chunksize=1):
            records.append(rec)
            if len(records)%25 == 0 or rec['error']:
                print(json.dumps(dict(done=len(records),total=900,id=rec['id'],status=rec['status'],minutes=(time.perf_counter()-start)/60)),flush=True)
    assert len(records) == 900
    for s in range(20):
        for k in range(5):
            pair = [r for r in records if r['split']==s and r['k']==k]
            assert len({r.get('data_sha256') for r in pair})==1
            assert len({r.get('initial_weights_sha256') for r in pair})==1
            if all(r['status']=='MEASURED' for r in pair):
                assert len({r['batch_sha256'] for r in pair})==1
    fields=['id','brazo','dosis','split','k','c250','q250','acc_panel250','status','error']
    with (OUT/'calibracion.csv').open('x',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=fields,extrasaction='ignore',lineterminator='\n')
        writer.writeheader();writer.writerows(records)
    summaries=[]
    for a,d in conditions:
        rows=[r for r in records if r['brazo']==a and r['dosis']==d]
        good=[r for r in rows if r['status']=='MEASURED']
        summaries.append(dict(brazo=a,dosis=d,planned=100,measured=len(good),
            **({key:float(np.median([r[key] for r in good])) for key in ('c250','q250','acc_panel250')} if len(good)==100 else {})))
    complete=all(r['status']=='MEASURED' for r in records)
    selected={}
    if complete:
        a0=summaries[0]['acc_panel250']
        for arm in ('LS','WD'):
            candidates=[r for r in summaries if r['brazo']==arm and .55<=r['c250']<=.70 and abs(r['acc_panel250']-a0)<.05]
            selected[arm]=min((r['dosis'] for r in candidates),default=None)
    result=dict(status=('CALIBRACION_COMPLETA' if any(d is not None for d in selected.values()) else 'INCONCLUSIVE_MANIPULACION') if complete else 'STOP_CALIBRATION_FAILURE',
        conditions=summaries,dosis_elegida=selected,all_900_preserved=True,paired_initial_data_batches=True,
        X_computed=False,rho_computed=False,associations_computed=False,cohort_started=False,
        tabla_sha256=sha(OUT/'calibracion.csv'),seconds=time.perf_counter()-start)
    write(OUT/'summary.json',result)
    print(json.dumps(result,ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
