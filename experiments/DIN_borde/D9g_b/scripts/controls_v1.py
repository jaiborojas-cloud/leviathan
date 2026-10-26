"""Controles fijados antes de covariables nuevas y asociaciones flexibles G3."""
import argparse
import datetime
import json
import platform
import subprocess
import sys
import time
import numpy as np
from support_v1 import ROOT,STAGE,RUN,ARRAYS,CFG,code_guard,guard,write,array
from statistics_v1 import compute,estimate


def main():
    code_guard();guard();RUN.mkdir(parents=True,exist_ok=False);ARRAYS.mkdir(parents=True,exist_ok=False)
    write(RUN/'environment.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=sys.version,numpy=np.__version__,platform=platform.platform(),commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()))
    begin=time.perf_counter();rng=np.random.default_rng(CFG['positive_seed']);split=np.repeat(np.arange(100),5);group=split.copy();n=500
    cov=rng.normal(size=(n,7))+np.repeat(rng.normal(size=(100,7)),5,axis=0)
    cheap,extra=cov[:,:4],cov[:,4:];latent=rng.normal(size=n)
    Y=.5*cheap[:,0]-.2*cheap[:,1]**2+.1*cheap[:,2]*cheap[:,3]+latent+.2*rng.normal(size=n)
    X=latent+.2*rng.normal(size=n);records=[]
    for base in [1,2,3,4]:
        pos=estimate(group,split,cheap,extra,X,Y,base)
        neg=compute(group,split,cheap,extra,X,Y,base,0,negative=True)
        passed=pos['D']>.1 and pos['p']<.05/4 and pos['half_sign_stable'] and pos['beta']>0 and abs(neg['D'])<=1e-8
        records.append(dict(base=base,positive={k:pos[k] for k in ['D','p','beta','halves','half_sign_stable']},negative_D=neg['D'],pass_test=bool(passed),array=array(f'positive_B{base}',all_D=pos['all_D'],SSE_full=pos['SSE_full'],SSE_base=np.array(pos['SSE_base']))))
    rng=np.random.default_rng(CFG['controls_seed']);sp=np.repeat(np.arange(20),5);g=sp.copy();q=rng.normal(size=(100,7));q[:,2]=1.
    xx=rng.normal(size=100);yy=.2*q[:,0]+.7*xx+rng.normal(size=100);numeric=[]
    for base in [1,2,3,4]:
        fast=compute(g,sp,q[:,:4],q[:,4:],xx,yy,base)
        exact=compute(g,sp,q[:,:4],q[:,4:],xx,yy,base,direct=True)
        err=float(np.max(np.abs(fast['all_D']-exact['all_D'])))
        numeric.append(dict(base=base,max_D_error=err,p_identical=fast['p']==exact['p'],pass_test=bool(err<=1e-9 and fast['p']==exact['p']),array=array(f'numeric_B{base}',fast_D=fast['all_D'],direct_D=exact['all_D'])))
    rng=np.random.default_rng(CFG['controls_seed']+1);q=rng.normal(size=(500,7));sp=split;xx=q[:,0]**2;yy=xx+.1*rng.normal(size=500);nonlinear=[]
    for base in [1,2,3,4]:
        r=compute(sp,sp,q[:,:4],q[:,4:],xx,yy,base,0)
        nonlinear.append(dict(base=base,D=r['D'],alias=r['full_alias'],pass_test=bool(r['D']>.1 if base==1 else abs(r['D'])<=1e-8)))
    blocked=[]
    for rel in ['experiments/DIN_borde/C2/cohorte/c2_cohorte.csv','experiments/DIN_borde/C2/analisis_C2.py','experiments/T2_A1/baseline/__NO_LEER__.csv']:
        try:
            with (ROOT/rel).open('rb'):pass
            raise RuntimeError('Guarda no bloqueó '+rel)
        except PermissionError:blocked.append(rel)
    passed=all(r['pass_test'] for r in records+numeric+nonlinear) and len(blocked)==3
    result=dict(status='PASS' if passed else 'FAIL',positive_negative=records,numeric=numeric,nonlinear=nonlinear,blocked_before_read=blocked,seconds=time.perf_counter()-begin)
    write(RUN/'controls.json',result);print(json.dumps(result,default=lambda x:x.tolist() if isinstance(x,np.ndarray) else str(x)),flush=True)
    if not passed:raise RuntimeError('Controles fallidos; no analizar cohorte')

if __name__=='__main__':main()
