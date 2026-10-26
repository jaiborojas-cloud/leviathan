"""Reevaluación forward de pesos G3 y test sintético independiente; no entrenar."""
import argparse
import concurrent.futures as cf
import csv
import datetime
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback
import numpy as np
from support_v1 import ROOT,STAGE,CFG,RUN,ARRAYS,G3,sha,write,array,csv_write,code_guard,guard
from network_v1 import network,scores
CACHE=None


def reference_map():
    return {r['path']:r for r in csv.DictReader((ROOT/CFG['sources']['G3_external_manifest']['path']).open())}


def checked(path,reference):
    p=Path(path)
    if sha(p)!=reference['sha256'] or p.stat().st_size!=int(reference['bytes']):raise RuntimeError('SHA input:'+str(p))
    return np.load(p,allow_pickle=False)


def prepare():
    import torch,scipy,sklearn
    RUN.mkdir(parents=True,exist_ok=False);ARRAYS.mkdir(parents=True,exist_ok=False)
    (RUN/'records').mkdir()
    write(RUN/'environment.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=sys.version,
        numpy=np.__version__,torch=torch.__version__,scipy=scipy.__version__,sklearn=sklearn.__version__,platform=platform.platform(),
        code_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),workers=CFG['workers'],threads=1))
    write(RUN/'execution_window.json',dict(start=time.perf_counter(),budget_seconds=CFG['budget_seconds']))
    refs=reference_map();selected=[]
    for r in refs.values():
        p=Path(r['path'])
        if p.parent==G3 and (p.name.startswith('data_') or ('_checkpoint.npz' in p.name and any(f'_u{u:03}_' in p.name for u in CFG['updates']))):
            if sha(p)!=r['sha256'] or p.stat().st_size!=int(r['bytes']):raise RuntimeError('SHA fuente archivada:'+str(p))
            selected.append(dict(path=str(p),sha256=r['sha256'],bytes=int(r['bytes'])))
    if len(selected)!=7800:raise RuntimeError('Inventario de inputs incompleto')
    csv_write(STAGE/'input_manifest.csv',selected,['path','sha256','bytes'])
    old=json.loads((ROOT/CFG['sources']['G3_config']['path']).read_text())
    old_seeds=set(range(old['split_seed_base'],old['split_seed_base']+100))|set(range(old['init_seed_base'],old['init_seed_base']+500))|set(range(old['batch_seed_base'],old['batch_seed_base']+500))
    seeds=set(range(CFG['test_seed_base'],CFG['test_seed_base']+100))
    if seeds & old_seeds:raise RuntimeError('Semillas test no nuevas')
    means=np.zeros((3,13));means[:,:2]=[[2.,0.],[-1.,np.sqrt(3)],[-1.,-np.sqrt(3)]]
    ytest=np.repeat(np.arange(3),CFG['test_per_class']);metadata=[]
    for s in CFG['splits']:
        epsilon=np.random.default_rng(CFG['test_seed_base']+s).normal(size=(3000,13))
        noise=array(f'test_noise_s{s:02}',epsilon=epsilon,y=ytest,means=means)
        for level,scale in enumerate(CFG['levels']):
            source=G3/f'data_S{level:02}_s{s:02}.npz'
            with checked(source,refs[str(source)]) as data:
                Z=(means[ytest]+scale*epsilon-data['scaler_mean'])/data['scaler_scale']
                reference=dict(path=str(source),sha256=refs[str(source)]['sha256'],bytes=int(refs[str(source)]['bytes']))
            output=array(f'test_S{level:02}_s{s:02}',Z=Z,y=ytest)
            metadata.append(dict(level=level,s=scale,split=s,test_seed=CFG['test_seed_base']+s,noise=noise,array=output,train_scaler_source=reference,n=3000,classes=[1000]*3))
    write(RUN/'test_datasets.json',metadata)
    print(json.dumps(dict(status='PREPARED',input_files=len(selected),test_panels=len(metadata),test_seeds_new=True)),flush=True)


def trajectory(task):
    import torch
    torch.set_num_threads(1)
    global CACHE
    if CACHE is None:
        torch.set_num_interop_threads(1);torch.set_default_dtype(torch.float64);guard()
        archived={(int(r['level']),int(r['split']),int(r['k']),int(r['update'])):r for r in csv.DictReader((ROOT/CFG['sources']['G3_states']['path']).open())}
        CACHE=reference_map(),archived
    refs,archived=CACHE
    level,split,k,deadline=task;start=time.perf_counter();identity=f'S{level:02}_s{split:02}_k{k}'
    result=dict(id=identity,level=level,s=CFG['levels'][level],split=split,k=k,status='FAILED',visits={},errors=[],reproduction_ok=True)
    try:
        data_path=G3/f'data_S{level:02}_s{split:02}.npz'
        with checked(data_path,refs[str(data_path)]) as data:
            Z,y,tr,va=[data[x].copy() for x in ['Z','y','train_ids','panel_ids']]
        model=network(torch);model.eval()
        for step in CFG['updates']:
            if time.perf_counter()>deadline:raise TimeoutError('Presupuesto D9g agotado; no sustitución')
            checkpoint=G3/f'{identity}_u{step:03}_checkpoint.npz'
            visit=dict(update=step,status='FAILED',checkpoint=dict(path=str(checkpoint),sha256=refs[str(checkpoint)]['sha256'],bytes=int(refs[str(checkpoint)]['bytes'])))
            try:
                with checked(checkpoint,refs[str(checkpoint)]) as data:
                    if int(data['update'])!=step:raise RuntimeError('Update de checkpoint distinto')
                    model.load_state_dict({key[7:]:torch.tensor(data[key]) for key in data.files if key.startswith('weight_')})
                train,_=scores(model,torch.tensor(Z[tr]),torch.tensor(y[tr]),torch)
                panel,sc=scores(model,torch.tensor(Z[va]),torch.tensor(y[va]),torch)
                ref=archived[level,split,k,step]
                got=dict(train_loss=train['loss'],train_acc=train['acc'],val_loss=panel['loss'],val_acc=panel['acc'],X=float(sc['log1m'].max()))
                errors={key:abs(value-float(ref[key])) for key,value in got.items()}
                good=all(err <= (CFG['accuracy_atol'] if 'acc' in key else CFG['reproduction_atol']+CFG['reproduction_rtol']*abs(float(ref[key]))) for key,err in errors.items())
                visit.update(status='MEASURED' if good else 'REPRODUCTION_FAIL',cheap=got,reproduction_errors=errors,reproduction_ok=good,
                    geometry=dict(c=float(ref['c']),trace=float(ref['trace']),rho_caras=float(ref['rho_caras']),rho_valid=ref['rho_valid']=='True',archived_status=ref['status']))
                result['reproduction_ok']=result['reproduction_ok'] and good
                if step==250:
                    test_path=ARRAYS/f'test_S{level:02}_s{split:02}.npz'
                    with np.load(test_path,allow_pickle=False) as data:xt,yt=data['Z'].copy(),data['y'].copy()
                    metric,sc_test=scores(model,torch.tensor(xt),torch.tensor(yt),torch)
                    losses=-sc_test['logpy'];correct=(sc_test['pred']==yt).astype(float)
                    loss_se=math.sqrt(sum(np.var(losses[yt==c],ddof=1) for c in range(3))/(9*1000))
                    acc_se=math.sqrt(sum(np.var(correct[yt==c],ddof=1) for c in range(3))/(9*1000))
                    result['test']=dict(loss=metric['loss'],accuracy=metric['acc'],gap=metric['loss']-train['loss'],loss_SE_stratified=loss_se,accuracy_SE_stratified=acc_se,n=3000)
                    result['test_array']=array(identity+'_test_predictions',logits=sc_test['logits'],logpy=sc_test['logpy'],losses=losses,pred=sc_test['pred'],y=yt)
            except Exception:
                visit['error']=traceback.format_exc();result['errors'].append(dict(update=step,error=visit['error']))
            result['visits'][str(step)]=visit
        result['status']='MEASURED' if not result['errors'] and result['reproduction_ok'] else 'FAILED'
    except Exception:result['errors'].append(dict(error=traceback.format_exc()))
    result['seconds']=time.perf_counter()-start
    write(RUN/'records'/(identity+'.json'),result)
    return dict(id=identity,status=result['status'],visits=len(result['visits']),reproduction_ok=result['reproduction_ok'],errors=len(result['errors']),seconds=result['seconds'])


def cohort():
    if json.loads((RUN/'controls.json').read_text())['status']!='PASS':raise RuntimeError('Controles primero')
    begin=time.perf_counter();window=json.loads((RUN/'execution_window.json').read_text());deadline=window['start']+window['budget_seconds']
    tasks=[(l,s,k,deadline) for s in CFG['splits'] for k in CFG['initializations'] for l in range(3)]
    records=[]
    with cf.ProcessPoolExecutor(max_workers=CFG['workers']) as pool:
        futures={pool.submit(trajectory,t):t for t in tasks}
        for future in cf.as_completed(futures):
            try:record=future.result()
            except Exception:record=dict(task=futures[future],status='WORKER_FAILED',error=traceback.format_exc())
            records.append(record)
            print(json.dumps(dict(done=len(records),total=len(tasks),**record)),flush=True)
    write(RUN/'execution.json',dict(records=records,seconds=time.perf_counter()-begin,code_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--part',choices=['prepare','evaluate'],required=True);args=parser.parse_args()
    code_guard();guard()
    prepare() if args.part=='prepare' else cohort()

if __name__=='__main__':main()
