"""Controles fijados: negativos polinómicos, señal grande/pequeña y pipeline directo."""
import datetime
import json
import platform
import subprocess
import sys
import time
import numpy as np
from support_v1 import ROOT,STAGE,RUN,ARRAYS,CFG,code_guard,guard,write,array
from statistics_v1 import estimate,run_cv


def summarize(r):
    return dict(reading=r['reading'],models=r['models'])


def artifact(name,cv):
    return array(name,D_B1=cv['all_D']['B1'],D_BR=cv['all_D']['BR'],D_reading=cv['all_D']['reading'],lambda_choices=cv['lambda_choices'],lambda_scores=cv['lambda_scores'])


def covariates(seed,splits=100):
    rng=np.random.default_rng(seed);sp=np.repeat(np.arange(splits),5)
    q=rng.normal(size=(5*splits,7))+np.repeat(rng.normal(size=(splits,7)),5,axis=0)
    return rng,sp,q


def main():
    code_guard();guard();RUN.mkdir(parents=True,exist_ok=False);ARRAYS.mkdir(parents=True,exist_ok=False)
    write(RUN/'environment.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=sys.version,numpy=np.__version__,platform=platform.platform(),
        code_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),BLAS_threads=1,permutations=999))
    begin=time.perf_counter();records=[]
    for label,theta in [('large',.2),('small',.02)]:
        rng,sp,q=covariates(CFG['controls_seeds'][label]);n=len(sp)
        latent=rng.normal(size=n);noise=rng.normal(size=n);xi=rng.normal(size=n)
        beta=np.sqrt(theta*1.04/(1-theta*1.04));X=latent+.2*xi
        Y=.5*q[:,0]-.2*q[:,1]**2+.1*q[:,2]*q[:,3]+beta*latent+noise
        est=estimate(sp,sp,q[:,:4],q[:,4:],X,Y)
        br=est['models']['BR'];detected=br['meets'] and br['coefficient']['beta']>0
        passed=bool(br['D']>.05 and detected) if label=='large' else True
        record=dict(label=label,oracle_D=theta,detects_small_rule=bool(detected),pass_validity=passed,**summarize(est),array=artifact('control_'+label,est['cv']))
        records.append(record);write(RUN/('control_'+label+'.json'),record)
        print(json.dumps(dict(control=label,D_BR=br['D'],p_BR=br['p'],detected=detected,validity_pass=passed)),flush=True)
    for label in ['quadratic','product']:
        rng,sp,q=covariates(CFG['controls_seeds'][label]);X=q[:,0]**2 if label=='quadratic' else q[:,1]*q[:,2];Y=X+.5*rng.normal(size=len(sp))
        cv=run_cv(sp,sp,q[:,:4],q[:,4:],X,Y,0)
        r=dict(label=label,D_BR=cv['D']['BR'],D_B1=cv['D']['B1'],alias_folds_BR=int(cv['alias_counts']['BR'][0]),pass_validity=bool(abs(cv['D']['BR'])<=1e-8),array=artifact('control_'+label,cv))
        records.append(r);write(RUN/('control_'+label+'.json'),r)
        print(json.dumps({k:v for k,v in r.items() if k!='array'}),flush=True)
    rng,sp,q=covariates(CFG['controls_seeds']['numeric'],20);q[:,2]=1.
    X=rng.normal(size=len(sp));Y=.2*q[:,0]**2+.3*X+rng.normal(size=len(sp))
    fast=run_cv(sp,sp,q[:,:4],q[:,4:],X,Y,999,check_uncached=True)
    exact=run_cv(sp,sp,q[:,:4],q[:,4:],X,Y,999,direct=True)
    errors={name:float(np.max(np.abs(fast['all_D'][name]-exact['all_D'][name]))) for name in ['B1','BR','reading']}
    same=fast['p']==exact['p'];uncached=fast['uncached_checks'];choices_same=bool(np.array_equal(fast['lambda_choices'],exact['lambda_choices']))
    passed=max(errors.values())<=1e-9 and same and choices_same and all(r['lambda_equal'] and r['max_relative_score_error']<=1e-10 for r in uncached)
    numeric=dict(label='numeric',max_D_errors=errors,p_identical=same,lambda_choices_equal=choices_same,uncached_checks=uncached,pass_validity=bool(passed),array=array('control_numeric',D_fast=fast['all_D']['reading'],D_direct=exact['all_D']['reading'],lambda_choices=fast['lambda_choices'],lambda_scores=fast['lambda_scores']))
    records.append(numeric);write(RUN/'control_numeric.json',numeric)
    blocked=[]
    for rel in ['experiments/DIN_borde/C2/cohorte/c2_cohorte.csv','experiments/T2_A1/baseline/__NO_LEER__.csv','experiments/DIN_borde/C1/__NO_LEER__.csv']:
        try:
            with (ROOT/rel).open('rb'):pass
            raise RuntimeError('Guarda no bloqueó '+rel)
        except PermissionError:blocked.append(rel)
    ok=all(r['pass_validity'] for r in records) and len(blocked)==3
    write(RUN/'controls.json',dict(status='PASS' if ok else 'FAIL',records=records,blocked_before_read=blocked,seconds=time.perf_counter()-begin))
    print(json.dumps(dict(status='PASS' if ok else 'FAIL',max_D_error=max(errors.values()),p_identical=same)),flush=True)
    if not ok:raise RuntimeError('Control obligatorio fallido: no interpretar')

if __name__=='__main__':main()
