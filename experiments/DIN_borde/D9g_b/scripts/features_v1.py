"""Covariables panel/pesos u30. Nunca regenera ni evalúa test; nunca entrena."""
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
from support_v1 import ROOT,STAGE,RUN,ARRAYS,G3,CFG,sha,write,csv_write,array,code_guard,guard
from network_v1 import network,scores


def main():
    code_guard();guard()
    if json.loads((RUN/'controls.json').read_text())['status']!='PASS':raise RuntimeError('Controles antes de medir')
    import torch
    torch.set_default_dtype(torch.float64);torch.set_num_threads(1);torch.set_num_interop_threads(1)
    rows=list(csv.DictReader((STAGE/'sources/D9g/results/run_v1/trajectories.csv').open()))
    expected={f'S{l:02}_s{s:02}_k{k}' for l in range(3) for s in range(100) for k in range(5)}
    if len(rows)!=1500 or {r['id'] for r in rows}!=expected:raise RuntimeError('Universo D9g distinto')
    refs={r['path']:r for r in csv.DictReader((STAGE/'sources/D9g/input_manifest.csv').open())}
    selected=[r for r in refs.values() if Path(r['path']).name.startswith('data_') or '_u030_checkpoint.npz' in r['path']]
    if len(selected)!=1800:raise RuntimeError('Inventario u30 distinto')
    for r in selected:
        if sha(r['path'])!=r['sha256']:raise RuntimeError('SHA input '+r['path'])
    csv_write(STAGE/'input_manifest.csv',selected,['path','sha256','bytes'])
    model=network(torch);model.eval();cache={};outputs=[];details=[];start=time.perf_counter()
    for n,r in enumerate(rows):
        record=dict(id=r['id'],level=int(r['level']),s=float(r['s']),split=int(r['split']),k=int(r['k']),c30=float(r['c_30']),Y=float(r['test_loss_250']),
            train_loss=float(r['train_loss_30']),val_loss=float(r['val_loss_30']),val_acc=float(r['val_acc_30']),X=float(r['X_30']),status='FAILED',error='',margin=None,entropy=None,weight_norm=None)
        info=dict(id=r['id']);level,split=record['level'],record['split']
        try:
            if (level,split) not in cache:
                path=G3/f'data_S{level:02}_s{split:02}.npz'
                with np.load(path,allow_pickle=False) as z:cache[level,split]=(z['Z'][z['panel_ids']].copy(),z['y'][z['panel_ids']].copy())
            panel,y=cache[level,split];checkpoint=G3/(r['id']+'_u030_checkpoint.npz')
            with np.load(checkpoint,allow_pickle=False) as z:
                weights={key[7:]:z[key].copy() for key in z.files if key.startswith('weight_')}
                if len(weights)!=6 or int(z['update'])!=30:raise RuntimeError('Checkpoint no corresponde a u30')
            model.load_state_dict({key:torch.tensor(value) for key,value in weights.items()})
            metric,sc=scores(model,torch.tensor(panel),torch.tensor(y),torch)
            got=dict(val_loss=metric['loss'],val_acc=metric['acc'],X=float(sc['log1m'].max()))
            errs={key:abs(value-record[key]) for key,value in got.items()}
            good=all(err<= (1e-14 if key=='val_acc' else 1e-10+1e-10*abs(record[key])) for key,err in errs.items())
            logits=sc['logits'];wrong=logits.copy();wrong[np.arange(27),y]=-np.inf
            margins=logits[np.arange(27),y]-np.max(wrong,axis=1)
            with torch.no_grad():
                lp=torch.log_softmax(torch.tensor(logits),1).numpy();prob=np.exp(lp)
            entropies=-np.sum(prob*lp,axis=1)
            norm=float(math.sqrt(sum(float(np.sum(v*v)) for v in weights.values())))
            record.update(margin=float(np.mean(margins)),entropy=float(np.mean(entropies)),weight_norm=norm,status='MEASURED' if good else 'REPRODUCTION_FAIL')
            info.update(checkpoint=refs[str(checkpoint)],reproduction_errors=errs,weights_keys=sorted(weights),array=array(r['id']+'_panel30',logits=logits,y=y,margins=margins,entropies=entropies))
        except Exception:record['error']=traceback.format_exc();info['error']=record['error']
        outputs.append(record);details.append(info)
        if (n+1)%100==0:print(json.dumps(dict(done=n+1,total=1500,failures=sum(x['status']!='MEASURED' for x in outputs))),flush=True)
    csv_write(RUN/'features.csv',outputs);write(RUN/'feature_details.json',details)
    write(RUN/'features_summary.json',dict(status='PASS' if all(r['status']=='MEASURED' for r in outputs) else 'FAIL',rows=len(outputs),failed=sum(r['status']!='MEASURED' for r in outputs),
        seconds=time.perf_counter()-start,test_regenerated=False,test_reevaluated=False,new_training=False,C2_data_read=False,torch=torch.__version__))
    if any(r['status']=='REPRODUCTION_FAIL' for r in outputs):raise RuntimeError('Panel no reproduce D9g')

if __name__=='__main__':main()
