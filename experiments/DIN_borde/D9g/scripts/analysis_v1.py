"""Once candidatos preespecificados sobre test G3 nuevo; exclusivamente exploratorio."""
import concurrent.futures as cf
import json
import math
import time
import traceback
import numpy as np
from support_v1 import STAGE,RUN,CFG,write,csv_write,array,code_guard,guard
from statistics_v1 import engine,centered


def finite(v):return isinstance(v,(int,float)) and math.isfinite(v)


def collect():
    trajectories=[];states=[];failures=[]
    for level,s in enumerate(CFG['levels']):
        for split in CFG['splits']:
            for k in CFG['initializations']:
                identity=f'S{level:02}_s{split:02}_k{k}'
                path=RUN/'records'/(identity+'.json')
                data=json.loads(path.read_text()) if path.exists() else dict(id=identity,level=level,split=split,k=k,status='MISSING',visits={})
                row=dict(id=identity,level=level,s=s,split=split,k=k,status=data['status'],reproduction_ok=data.get('reproduction_ok'),error=data.get('errors',[]))
                test=data.get('test',{})
                row.update(test_loss_250=test.get('loss'),test_accuracy_250=test.get('accuracy'),gap_loss_250=test.get('gap'),test_loss_SE=test.get('loss_SE_stratified'))
                for t in CFG['updates']:
                    v=data['visits'].get(str(t),{})
                    cheap=v.get('cheap',{});geo=v.get('geometry',{})
                    row['visit_status_'+str(t)]=v.get('status','MISSING')
                    for name in ['train_loss','train_acc','val_loss','val_acc','X']:row[name+'_'+str(t)]=cheap.get(name)
                    for name in ['c','trace','rho_caras']:row[name+'_'+str(t)]=geo.get(name)
                    row['geometry_valid_'+str(t)]=bool(geo.get('rho_valid') and geo.get('archived_status')=='MEASURED')
                    states.append(dict(id=identity,level=level,s=s,split=split,k=k,update=t,status=v.get('status','MISSING'),**cheap,**geo,reproduction_errors=v.get('reproduction_errors'),error=v.get('error')))
                if data['status']!='MEASURED':failures.append(data)
                trajectories.append(row)
    csv_write(RUN/'trajectories.csv',trajectories);csv_write(RUN/'states.csv',states);write(RUN/'measurement_failures.json',failures)
    return trajectories,states,failures


def candidate(row,c):
    t=c['time']
    if row.get('visit_status_'+str(t))!='MEASURED' or not row.get('geometry_valid_'+str(t)):return None
    if c['kind']=='delta_c':
        a=row.get('c_'+str(c['from']));b=row.get('c_'+str(t))
        return b-a if finite(a) and finite(b) and row.get('visit_status_'+str(c['from']))=='MEASURED' else None
    key={'c':'c','log_trace':'trace','log_rho_caras':'rho_caras'}[c['kind']]
    value=row.get(key+'_'+str(t))
    if not finite(value):return None
    return value if key=='c' else math.log(value) if value>0 else None


def task(item):
    dataset,rows,c=item;start=time.perf_counter();guard()
    planned=1500 if dataset=='aggregate' else 500
    subset=rows if dataset=='aggregate' else [r for r in rows if r['level']==dataset]
    valid=[];missing=[];t=c['time']
    for r in subset:
        x=candidate(r,c)
        base=[r.get(name+'_'+str(t)) for name in ['train_loss','val_loss','val_acc','X']]
        y=[r.get(outcome) for outcome in CFG['outcomes']]
        if finite(x) and all(finite(v) for v in base+y):valid.append((r,x,base,y))
        else:missing.append(r['id'])
    # Grupos de cinco por (nivel,split), también en el agregado.
    counts={}
    for r,_,_,_ in valid:counts[r['level'],r['split']]=counts.get((r['level'],r['split']),0)+1
    eligible={g for g,n in counts.items() if n>=3}
    adjusted=[v for v in valid if (v[0]['level'],v[0]['split']) in eligible]
    expected_groups=300 if dataset=='aggregate' else 100
    complete_splits={s for s in range(100) if all((l,s) in eligible for l in (range(3) if dataset=='aggregate' else [dataset]))}
    reasons=[]
    if planned-len(valid)>.05*planned:reasons.append('Faltantes>5%')
    if len(complete_splits)<80:reasons.append('Splits válidos<80%')
    if len(adjusted)<.95*planned:reasons.append('Filas ajustadas<95%')
    answer=dict(dataset=dataset,candidate=c['name'],index=c['index'],time=t,planned=planned,valid=len(valid),adjusted=len(adjusted),
        missing=missing,eligible_groups=len(eligible),complete_splits=len(complete_splits),gate_reasons=reasons,results={})
    if reasons:
        for outcome in CFG['outcomes']:answer['results'][outcome]=dict(status='INCONCLUSIVE',reasons=reasons)
    else:
        sp=np.array([r['split'] for r,_,_,_ in adjusted]);gr=np.array([100*r['level']+r['split'] for r,_,_,_ in adjusted])
        X=np.array([x for _,x,_,_ in adjusted]);B=np.array([b for _,_,b,_ in adjusted]);Y=np.array([y for _,_,_,y in adjusted])
        result=engine(gr,sp,B,X,Y,c['index'])
        answer['array']=array(f'analysis_{dataset}_{c["index"]:02}',all_D=result['all_D'],SSE_full=result['SSE_full'],SSE_base=result['SSE_base'],SSE_null=result['SSE_null'],p=result['p'])
        answer['numerics']=dict(base_scale=result['base_scale'],candidate_scale=result['candidate_scale'],alias=result['alias'],fallbacks=result['fallbacks'])
        for k,outcome in enumerate(CFG['outcomes']):
            halves=[dict(parity=h['parity'],n=h['n'],D=float(h['D'][k]) if finite(float(h['D'][k])) else None,beta=float(h['beta'][k]),alias=h['alias']) for h in result['halves']]
            value=dict(D=float(result['D'][k]) if finite(float(result['D'][k])) else None,p_exploratorio=float(result['p'][k]),beta=float(result['beta'][k]),
                D_base=float(result['D_base'][k]) if finite(float(result['D_base'][k])) else None,
                D_candidate_alone=float(result['D_candidate_alone'][k]) if finite(float(result['D_candidate_alone'][k])) else None,
                halves=halves,permutations=2000)
            if result['SSE_null'][k]<=np.finfo(float).tiny:
                value.update(status='NO_VARIACION_DESENLACE',D=None,p_exploratorio=None,beta=None,half_sign_stable=False,meets_reference_rule=False)
            elif result['candidate_constant'] or result['alias']:
                value.update(status='NO_IDENTIFICABLE',D=None,p_exploratorio=None,beta=None,half_sign_stable=False,meets_reference_rule=False)
            else:
                same=not any(h['alias'] for h in halves) and halves[0]['beta']*halves[1]['beta']>0 and halves[0]['beta']*value['beta']>0
                meets=value['D'] is not None and value['D']>.02 and value['p_exploratorio']<.05/12 and same
                value.update(status='ESTIMATED',half_sign_stable=bool(same),meets_reference_rule=bool(meets))
            value['propose_to_responsible']=bool(dataset==2 and outcome=='test_loss_250' and value['meets_reference_rule'])
            answer['results'][outcome]=value
    answer['seconds']=time.perf_counter()-start
    write(RUN/f'analysis_{dataset}_{c["index"]:02}.json',answer)
    return answer


def main():
    code_guard();guard()
    if json.loads((RUN/'controls.json').read_text())['status']!='PASS':raise RuntimeError('Controles fallidos')
    begin=time.perf_counter();rows,states,failures=collect()
    bad=[r['id'] for r in rows if r['reproduction_ok'] is False]
    if bad:
        write(RUN/'analysis.json',dict(status='INVALIDA_REPRODUCCION',mismatched=bad,cohort='G3 solamente'))
        raise RuntimeError('No interpretar: discrepancias de reproducción')
    window=json.loads((RUN/'execution_window.json').read_text())
    if time.perf_counter()>window['start']+window['budget_seconds']:raise TimeoutError('Presupuesto antes de análisis')
    jobs=[(dataset,rows,c) for dataset in [0,1,2,'aggregate'] for c in CFG['candidates']]
    records=[]
    with cf.ProcessPoolExecutor(max_workers=2) as pool:
        for result in pool.map(task,jobs):
            records.append(result);a=result['results']['test_loss_250']
            print(json.dumps(dict(done=len(records),total=len(jobs),dataset=result['dataset'],candidate=result['candidate'],primary=a)),flush=True)
    flat=[]
    for r in records:
        for outcome,v in r['results'].items():
            flat.append(dict(dataset=r['dataset'],candidate=r['candidate'],time=r['time'],outcome=outcome,n=r['adjusted'],splits=r['complete_splits'],status=v['status'],
                D=v.get('D'),p_exploratorio=v.get('p_exploratorio'),beta=v.get('beta'),D_base=v.get('D_base'),D_candidate_alone=v.get('D_candidate_alone'),
                beta_even=v.get('halves',[{},{}])[0].get('beta'),beta_odd=v.get('halves',[{},{}])[1].get('beta'),
                D_even=v.get('halves',[{},{}])[0].get('D'),D_odd=v.get('halves',[{},{}])[1].get('D'),
                half_sign_stable=v.get('half_sign_stable'),meets_reference_rule=v.get('meets_reference_rule'),propose=v.get('propose_to_responsible',False)))
    csv_write(RUN/'estimates.csv',flat)
    proposed=[r['candidate'] for r in flat if r['propose']]
    primary08=[r for r in flat if r['dataset']==2 and r['outcome']=='test_loss_250']
    valid=all(r['status']=='ESTIMATED' for r in primary08)
    verdict='PROPONER_CONFIRMATORIO_EXPLORATORIO' if proposed else 'NINGUNO_CUMPLE_REGLA' if valid else 'INCONCLUSIVE'
    write(RUN/'analysis.json',dict(nature='EXPLORATORIO',verdict=verdict,proposed_candidates=proposed,candidate_count=11,family_denominator=12,
        cells=len(flat),complete_trajectories=len(rows),measurement_failures=len(failures),seconds=time.perf_counter()-begin,records=records,
        C2_data_used=False,new_training=False,new_rho_measurements=False))
    print(json.dumps(dict(verdict=verdict,proposed_candidates=proposed,cells=len(flat))),flush=True)

if __name__=='__main__':main()
