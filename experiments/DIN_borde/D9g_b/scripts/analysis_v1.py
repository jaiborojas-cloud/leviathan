"""Robustez prefijada B1-B4: no busca bases ni usa C2."""
import concurrent.futures as cf
import csv
import json
import math
import time
import traceback
import numpy as np
from support_v1 import STAGE,RUN,CFG,write,csv_write,array,code_guard,guard
from statistics_v1 import estimate,compute


def finite(x):
    try:return math.isfinite(float(x))
    except (ValueError,TypeError):return False


def cell(job):
    dataset,base,rows=job;guard();start=time.perf_counter()
    selected=rows if dataset=='aggregate' else [r for r in rows if int(r['level'])==dataset]
    required=['train_loss','val_loss','val_acc','X','c30','Y']+(['margin','entropy','weight_norm'] if base==4 else [])
    valid=[r for r in selected if all(finite(r.get(key)) for key in required) and (base!=4 or r['status']=='MEASURED')]
    counts={}
    for r in valid:counts[int(r['level']),int(r['split'])]=counts.get((int(r['level']),int(r['split'])),0)+1
    eligible={key for key,n in counts.items() if n>=3};adjusted=[r for r in valid if (int(r['level']),int(r['split'])) in eligible]
    complete={s for s in range(100) if all((l,s) in eligible for l in (range(3) if dataset=='aggregate' else [dataset]))}
    reasons=[]
    if len(selected)-len(valid)>.05*len(selected):reasons.append('Faltantes>5%')
    if len(complete)<80:reasons.append('Splits válidos<80%')
    if len(adjusted)<.95*len(selected):reasons.append('Ajustados<95%')
    answer=dict(dataset=dataset,base=base,planned=len(selected),valid=len(valid),adjusted=len(adjusted),complete_splits=len(complete),gate_reasons=reasons)
    if reasons:answer.update(status='INCONCLUSIVE',meets=False)
    else:
        split=np.array([int(r['split']) for r in adjusted]);group=np.array([100*int(r['level'])+int(r['split']) for r in adjusted])
        cheap=np.array([[float(r[k]) for k in ['train_loss','val_loss','val_acc','X']] for r in adjusted])
        extra=np.array([[float(r[k]) if finite(r.get(k)) else 0. for k in ['margin','entropy','weight_norm']] for r in adjusted])
        X=np.array([float(r['c30']) for r in adjusted]);Y=np.array([float(r['Y']) for r in adjusted])
        value=estimate(group,split,cheap,extra,X,Y,base)
        negative=compute(group,split,cheap,extra,X,Y,base,0,negative=True)
        neg_ok=abs(negative['D'])<=CFG['negative_D_atol']
        answer.update({k:v for k,v in value.items() if k not in ['all_D','SSE_full']})
        answer.update(status='ESTIMATED' if not value['full_alias'] else 'NO_IDENTIFICABLE',negative_control_D=negative['D'],negative_control_alias_by_fold=negative['aliases'],negative_control_pass=neg_ok)
        if value['full_alias']:answer.update(p=None,beta=None,meets=False)
        answer['array']=array(f'analysis_{dataset}_B{base}',all_D=value['all_D'],SSE_full=value['SSE_full'],SSE_base=np.array(value['SSE_base']))
        if base==1:
            ref=next(r for r in csv.DictReader((STAGE/'sources/D9g/results/run_v1/estimates.csv').open()) if r['dataset']==str(dataset) and r['candidate']=='c_30' and r['outcome']=='test_loss_250')
            answer['reference_D9g']=dict(D=float(ref['D']),p=float(ref['p_exploratorio']),D_error=abs(value['D']-float(ref['D'])),p_identical=value['p']==float(ref['p_exploratorio']))
    answer['seconds']=time.perf_counter()-start;write(RUN/f'analysis_{dataset}_B{base}.json',answer);return answer


def main():
    code_guard();guard()
    if json.loads((RUN/'controls.json').read_text())['status']!='PASS':raise RuntimeError('Controles antes de interpretar')
    feature_summary=json.loads((RUN/'features_summary.json').read_text())
    if feature_summary['status']!='PASS':raise RuntimeError('Fallo de características: conservar antes de interpretar')
    start=time.perf_counter();rows=list(csv.DictReader((RUN/'features.csv').open()));results=[]
    jobs=[(d,b,rows) for d in [0,1,2,'aggregate'] for b in [1,2,3,4]]
    with cf.ProcessPoolExecutor(max_workers=2) as pool:
        for r in pool.map(cell,jobs):
            results.append(r);print(json.dumps({k:r.get(k) for k in ['dataset','base','D','p','beta','half_sign_stable','negative_control_D','status']}),flush=True)
    bad=[r for r in results if r.get('negative_control_pass') is False or (r['base']==1 and (r.get('reference_D9g',{}).get('D_error',1)>1e-10 or not r.get('reference_D9g',{}).get('p_identical')))]
    primary=[r for r in results if r['dataset']==2 and r['base']>=2]
    if bad:verdict='INVALIDA_CONTROLES_O_REPRODUCCION'
    elif any(r['status']=='INCONCLUSIVE' for r in primary):verdict='INCONCLUSIVE'
    elif all(r['meets'] for r in primary):verdict='ROBUSTO_EXPLORATORIO'
    elif all(next(r for r in primary if r['base']==b)['D']<=0 for b in [3,4]):verdict='ARTEFACTO_DE_BASE_LINEAL_EXPLORATORIO'
    else:verdict='FRAGIL_EXPLORATORIO'
    flat=[]
    for r in results:
        hs=r.get('halves',[{},{}]);frames=r.get('frames',[])
        flat.append(dict(dataset=r['dataset'],base=r['base'],n=r['adjusted'],splits=r['complete_splits'],status=r['status'],D=r.get('D'),p_exploratorio=r.get('p'),beta=r.get('beta'),D_base=r.get('D_base'),
            beta_even=hs[0].get('beta'),beta_odd=hs[1].get('beta'),D_even=hs[0].get('D'),D_odd=hs[1].get('D'),half_sign_stable=r.get('half_sign_stable'),meets=r.get('meets'),
            negative_D=r.get('negative_control_D'),negative_pass=r.get('negative_control_pass'),rank_min=min((f['rank'] for f in frames),default=None),rank_max=max((f['rank'] for f in frames),default=None)))
    csv_write(RUN/'estimates.csv',flat)
    write(RUN/'analysis.json',dict(nature='EXPLORATORIO',verdict=verdict,records=results,seconds=time.perf_counter()-start,bases=[1,2,3,4],B5_included=False,C2_data_used=False,test_regenerated=False))
    print(json.dumps(dict(verdict=verdict,invalid_cells=len(bad))),flush=True)
    if bad:raise RuntimeError('Corrida inválida: preservar, no interpretar robustez')

if __name__=='__main__':main()
