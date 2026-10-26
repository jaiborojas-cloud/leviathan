"""Ridge anidado sobre tablas D9g-b inmutables. No test/red nueva ni C2."""
import concurrent.futures as cf
import csv
import json
import math
import time
import numpy as np
from support_v1 import STAGE,RUN,CFG,write,csv_write,array,code_guard,guard
from statistics_v1 import estimate


def cell(item):
    dataset,rows=item;guard();begin=time.perf_counter()
    subset=rows if dataset=='aggregate' else [r for r in rows if int(r['level'])==dataset]
    keys=['Y','c30','train_loss','val_loss','val_acc','X','margin','entropy','weight_norm']
    valid=[]
    for r in subset:
        try:
            if r['status']=='MEASURED' and all(math.isfinite(float(r[k])) for k in keys):valid.append(r)
        except (ValueError,TypeError):pass
    counts={}
    for r in valid:counts[int(r['level']),int(r['split'])]=counts.get((int(r['level']),int(r['split'])),0)+1
    good={key for key,n in counts.items() if n>=3};selected=[r for r in valid if (int(r['level']),int(r['split'])) in good]
    complete={s for s in range(100) if all((l,s) in good for l in (range(3) if dataset=='aggregate' else [dataset]))}
    reasons=[]
    if len(valid)<.95*len(subset):reasons.append('Faltantes>5%')
    if len(complete)<80:reasons.append('Splits válidos<80%')
    if len(selected)<.95*len(subset):reasons.append('Ajustados<95%')
    record=dict(dataset=dataset,planned=len(subset),valid=len(valid),adjusted=len(selected),complete_splits=len(complete),gate_reasons=reasons)
    if reasons:record.update(status='NO_CONCLUYENTE_DATOS',verdict='NO_CONCLUYENTE_EXPLORATORIO')
    else:
        sp=np.array([int(r['split']) for r in selected]);g=np.array([100*int(r['level'])+int(r['split']) for r in selected])
        q=np.array([[float(r[k]) for k in ['train_loss','val_loss','val_acc','X']] for r in selected]);e=np.array([[float(r[k]) for k in ['margin','entropy','weight_norm']] for r in selected])
        X=np.array([float(r['c30']) for r in selected]);Y=np.array([float(r['Y']) for r in selected])
        est=estimate(g,sp,q,e,X,Y);cv=est['cv'];name=est['reading'];read=est['models'][name]
        verdict='ROBUSTO_EXPLORATORIO' if read['meets'] else 'REDUNDANTE_EXPLORATORIO' if name=='BR' and read['D']<=0 else 'NO_CONCLUYENTE_EXPLORATORIO'
        references=list(csv.DictReader((STAGE/'sources/D9g/results/run_v1/estimates.csv').open()))
        ref=next(r for r in references if r['dataset']==str(dataset) and r['candidate']=='c_30' and r['outcome']=='test_loss_250')
        difference=abs(cv['D']['B1']-float(ref['D']))
        if difference>1e-10:verdict='INVALIDA_REPRODUCCION'
        record.update(status='VALIDA' if difference<=1e-10 else 'INVALIDA_REPRODUCCION',verdict=verdict,reading=name,models=est['models'],
            reading_D=read['D'],reading_p=cv['p']['reading'],base_adequate=bool(cv['adequate_all'][0]),
            adequacy_repeated_identical=bool(np.all(cv['adequate_all']==cv['adequate_all'][0])),
            lambda_repeated_identical=bool(np.all(cv['lambda_choices']==cv['lambda_choices'][:,:1])),
            reference_B1_D=float(ref['D']),B1_D_error=difference,frames=cv['frames'],outer_selection_calls=cv['selection_calls'],
            array=array(f'analysis_{dataset}',D_B1=cv['all_D']['B1'],D_BR=cv['all_D']['BR'],D_reading=cv['all_D']['reading'],
                SSE_B1_base=cv['SSE_base']['B1'],SSE_BR_base=cv['SSE_base']['BR'],SSE_B1_full=cv['SSE_full']['B1'],SSE_BR_full=cv['SSE_full']['BR'],
                lambda_choices=cv['lambda_choices'],lambda_scores=cv['lambda_scores'],adequate=cv['adequate_all'],
                B1_base_predictions=cv['base_predictions']['B1'][:,0],BR_base_predictions=cv['base_predictions']['BR'][:,0],
                B1_full_predictions=cv['full_predictions']['B1'],BR_full_predictions=cv['full_predictions']['BR']))
    record['seconds']=time.perf_counter()-begin;write(RUN/f'analysis_{dataset}.json',record);return record


def main():
    code_guard();guard()
    if json.loads((RUN/'controls.json').read_text())['status']!='PASS':raise RuntimeError('Controles obligatorios primero')
    rows=list(csv.DictReader((STAGE/'sources/D9g_b/results/run_v1/features.csv').open()))
    ids={f'S{l:02}_s{s:02}_k{k}' for l in range(3) for s in range(100) for k in range(5)}
    if len(rows)!=1500 or {r['id'] for r in rows}!=ids:raise RuntimeError('Universo de tablas distinto')
    start=time.perf_counter();records=[]
    with cf.ProcessPoolExecutor(max_workers=2) as pool:
        for r in pool.map(cell,[(d,rows) for d in [0,1,2,'aggregate']]):
            records.append(r);print(json.dumps({k:r.get(k) for k in ['dataset','verdict','reading','reading_D','reading_p','base_adequate','B1_D_error','seconds']}),flush=True)
    primary=next(r for r in records if r['dataset']==2);verdict=primary['verdict'];next_step='PROPONER_CONFIRMATORIO_C2_AL_RESPONSABLE' if verdict=='ROBUSTO_EXPLORATORIO' else 'PROPONER_Q13_AL_RESPONSABLE'
    flat=[]
    for r in records:
        for name,m in r.get('models',{}).items():
            flat.append(dict(dataset=r['dataset'],model=name,n=r['adjusted'],splits=r['complete_splits'],D=m['D'],p=m['p'],D_base=m['D_base'],beta=m['coefficient']['beta'],
                beta_even=m['halves'][0]['beta'],beta_odd=m['halves'][1]['beta'],D_even=m['halves'][0]['D'],D_odd=m['halves'][1]['D'],
                half_sign_stable=m['half_sign_stable'],meets=m['meets'],base_reading=r['reading'],selected=name==r['reading'],verdict=r['verdict']))
    csv_write(RUN/'estimates.csv',flat)
    write(RUN/'analysis.json',dict(nature='EXPLORATORIO',verdict=verdict,next_step_proposed=next_step,records=records,seconds=time.perf_counter()-start,
        permutations=999,p_resolution=.001,C2_data_read=False,test_regenerated=False,test_reevaluated=False,new_training=False))
    print(json.dumps(dict(verdict=verdict,next_step_proposed=next_step)),flush=True)

if __name__=='__main__':main()
