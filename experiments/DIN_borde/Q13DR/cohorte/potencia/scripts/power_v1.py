"""Dimensionamiento congelado DIN-Q13DR; jamás analiza la cohorte nueva."""
import collections
import concurrent.futures as cf
import csv
import datetime as dt
import json
import math
import platform
import subprocess
import time
import traceback
import numpy as np
from support import ROOT,STAGE,CFG,OUT,EXTERNAL,sha,write,code_guard,guard,engine,analyst


def wilson(k,n=400):
    z=1.959963984540054;p=k/n;den=1+z*z/n;mid=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return dict(success=int(k),n=n,rate=p,lower=mid-half,upper=mid+half)


def pilot():
    p=ROOT/CFG['sources']['pilot']['path']
    rows=sorted([r for r in csv.DictReader(p.open()) if int(r['level'])==2],key=lambda r:(int(r['split']),int(r['k'])))
    assert len(rows)==500 and all(r['pair_valid']=='True' for r in rows)
    assert {(int(r['split']),int(r['k'])) for r in rows}=={(s,k) for s in range(100) for k in range(5)}
    _,cen,_=engine();sp=np.repeat(np.arange(100),5)
    X=np.array([float(r['X10']) for r in rows]);L=np.log([float(r['rho_caras_10']) for r in rows]);Y=np.log([float(r['rho_caras_250']) for r in rows])
    z=(L-L.mean())/L.std();B=np.column_stack([cen(z**k,sp) for k in (1,2,3)])
    alpha=np.linalg.lstsq(B,cen(Y,sp),rcond=None)[0];res=cen(Y,sp)-B@alpha;df=500-100-np.linalg.matrix_rank(B)
    result=dict(X=X,L=L,alpha=alpha,sigma2=float(res@res/df))
    write(OUT/'pilot.json',dict(source_sha256=sha(p),s=.8,rows=500,sigma2=result['sigma2'],alpha=alpha.tolist(),df=int(df),X_Y_association_estimated=False))
    return result


def sensitivity_correlation():
    p=ROOT/CFG['sources']['sensitivity']['path'];arms={'A0':{},'LS':{}}
    with p.open(encoding='utf-8',newline='') as f:
        for r in csv.DictReader(f):
            arm=r['brazo']
            if arm not in arms:continue
            # Only these columns are accessed: no X10, rho10, R, c, q or accuracy.
            key=int(r['split']),int(r['k'])
            if key in arms[arm]:raise RuntimeError('Par duplicado Q13 en sensibilidad')
            try:v=float(r['rho_caras_250'])
            except ValueError:v=float('nan')
            arms[arm][key]=math.log(v) if not r['error'] and math.isfinite(v) and v>0 else None
    pairs=sorted(k for k in set(arms['A0'])&set(arms['LS']) if arms['A0'][k] is not None and arms['LS'][k] is not None)
    counts=collections.Counter(s for s,k in pairs);pairs=[(s,k) for s,k in pairs if counts[s]>=3]
    if not pairs:raise RuntimeError('Sensibilidad Q13 sin pares válidos')
    sp=np.array([s for s,k in pairs]);a=np.array([arms['A0'][k] for k in pairs]);b=np.array([arms['LS'][k] for k in pairs])
    _,cen,_=engine();a,b=cen(a,sp),cen(b,sp)
    rho=float(np.corrcoef(a,b)[0,1])
    if not math.isfinite(rho) or not 0<=rho<=1:raise RuntimeError('Correlación no utilizable sin cambiar el modelo predeclarado')
    write(OUT/'sensitivity_Q13_correlation.json',dict(source_sha256=sha(p),rho=rho,pairs=len(pairs),splits=len(np.unique(sp)),
        definition='Pearson de log rho_caras250 A0/LS, centrados dentro de cada split pareado',
        no_other_real_association=True,used_for_size=False,conditional_noise_not_identified=True))
    return rho


def controls():
    A,Q,R=analyst();Engine,cen,bootstrap=engine();records=[]
    for j,n in enumerate((20,40)):
        g=np.random.default_rng(854000+j);sp=np.repeat(np.arange(n),5);L=g.normal(size=5*n);X=.3*L+g.normal(size=5*n)
        e=Engine(sp,X,L,B=1999);signal=e.residual_X
        beta=np.linspace(.1,0,6);Y=cen(g.normal(size=(5*n,6)),sp)+.2*e.base[:,0,None]+signal[:,None]*beta
        got=e.calculate(Y,np.zeros(5*n),[0.]);draws=np.random.default_rng(860001).choice(n,size=(500,n),replace=True)
        boot=bootstrap(e,Y,np.zeros(5*n),[0.],draws)[0];blocks=Q.bloques(np.arange(n))
        err=0.;berr=0.;psame=True
        for l in range(6):
            ref=A.primaria(sp,X,L,Y[:,l],3,260001,1999)
            err=max(err,abs(ref['D']-float(got['D'][0,l])));psame=psame and ref['p']==float(got['p'][0,l])
        for d in range(12):
            ix=(draws[d,:,None]*5+np.arange(5)).ravel();ns=np.repeat(np.arange(n),5);fo=np.repeat([blocks[s] for s in draws[d]],5)
            for l in range(6):berr=max(berr,abs(Q.D_punto(ns,X[ix],L[ix],Y[ix,l],fo)-float(boot[d,l])))
        c=np.array(CFG['c']);cc=c-c.mean();D=got['D'][0];bs=np.sum(cc*(D-D.mean()))/np.sum(cc*cc)
        beta_error=abs(bs-R.pendiente(D,c))
        records.append(dict(n=n,max_D_error=err,p_identical=bool(psame),max_bootstrap_error=berr,beta_error=beta_error,
                            pass_test=bool(err<=1e-10 and psame and berr<=1e-10 and beta_error<=1e-10)))
    result=dict(status='PASS' if all(r['pass_test'] for r in records) else 'FAIL',records=records,simulated_only=True)
    write(OUT/'controls.json',result);print(json.dumps(dict(phase='controls',status=result['status'])),flush=True)
    if result['status']!='PASS':raise RuntimeError('Control del instrumento estadístico fallido')


def frame_task(task):
    n,p,frame,rho,label=task;start=time.perf_counter();guard();A,Q,R=analyst();Engine,cen,bootstrap=engine()
    g=np.random.default_rng(np.random.SeedSequence([412000,2,n,frame]));draw=g.choice(100,n,replace=True)
    ix=(draw[:,None]*5+np.arange(5)).ravel();X,L=p['X'][ix],p['L'][ix];sp=np.repeat(np.arange(n),5);e=Engine(sp,X,L,B=1999)
    signal=e.residual_X;var=float(np.mean(signal*signal));c=np.array(CFG['c']);targets=np.maximum(0,.039+(.031/.26)*(c-.86))
    betas=np.sqrt(targets/(1-targets)*.8*p['sigma2']/var)
    g=np.random.default_rng(np.random.SeedSequence([413000,2,n,frame]));z=g.normal(size=(5*n,7,100))
    noises=math.sqrt(rho)*z[:,0:1,:]+math.sqrt(1-rho)*z[:,1:,:]
    Y=np.empty((5*n,6,100));base=e.base@p['alpha']
    for l in range(6):Y[:,l,:]=base[:,None]+betas[l]*signal[:,None]+math.sqrt(p['sigma2'])*cen(noises[:,l,:],sp)
    yy=Y.reshape(5*n,600);result=e.calculate(yy,np.zeros(5*n),[0.])
    D=result['D'][0].reshape(6,100);ps=result['p'][0].reshape(6,100);slopes=result['slopes'][0].reshape(6,100)
    passed=(D>0)&(ps<.05)&(slopes>0)
    draws=np.random.default_rng(860001).choice(n,size=(500,n),replace=True)
    boot=bootstrap(e,yy,np.zeros(5*n),[0.],draws)[0].reshape(500,6,100)
    if not np.isfinite(boot).all() or not np.isfinite(D).all():raise FloatingPointError('Réplica no finita; no sustituir')
    cc=c-c.mean();bb=np.sum(cc[None,:,None]*(boot-boot.mean(axis=1,keepdims=True)),axis=1)/np.sum(cc*cc)
    ic=np.quantile(bb,[.025,.975],axis=0);icD=np.quantile(boot,[.025,.975],axis=0)
    primary=[];secondary=[];extreme=[]
    for r in range(100):
        if not passed[0,r]:primary.append('INCONCLUSIVE_SIN_SENAL_CONTROL');secondary.append('NO_EVALUADO');extreme.append('NO_EVALUADO');continue
        primary.append(R.clasificar_beta(ic[:,r]));secondary.append(R.equivalencia(ic[:,r]));extreme.append(R.clasificar_extremo(bool(passed[5,r]),icD[:,5,r]))
    maxerr=0.
    for l in range(6):maxerr=max(maxerr,abs(Q.D_punto(sp,X,L,Y[:,l,0])-float(D[l,0])))
    if maxerr>1e-10:raise RuntimeError('D_punto no coincide en marco simulado')
    name=f'{label}_N{n}_frame{frame}';path=EXTERNAL/(name+'.npz')
    with path.open('xb') as f:
        np.savez_compressed(f,D=D,p=ps,slopes=slopes,all_D=result['all_D'],bootstrap_D=boot,bootstrap_beta=bb,IC95_beta=ic,IC95_D=icD,
            pilot_draw=draw,bootstrap_draw=draws,normal_noise=z,c=c,effects=targets,multipliers=betas,
            primary=np.array(primary),secondary=np.array(secondary),extreme=np.array(extreme))
    rec=dict(N=n,frame=frame,rho=rho,scenario=label,replicates=100,primary=dict(collections.Counter(primary)),secondary=dict(collections.Counter(secondary)),
             extreme=dict(collections.Counter(extreme)),control_PASS=int(passed[0].sum()),seconds=time.perf_counter()-start,max_D_punto_error=maxerr,
             array=dict(path=str(path),bytes=path.stat().st_size,sha256=sha(path)))
    write(OUT/(name+'.json'),rec);return rec


def run_scenario(n,p,rho,label):
    records=[]
    with cf.ProcessPoolExecutor(max_workers=2) as pool:
        for rec in pool.map(frame_task,[(n,p,f,rho,label) for f in range(4)]):
            records.append(rec);print(json.dumps(dict(phase='frame',N=n,rho=rho,frame=rec['frame'],seconds=rec['seconds'])),flush=True)
    def total(key):return dict(sum((collections.Counter(r[key]) for r in records),collections.Counter()))
    primary=total('primary');secondary=total('secondary');extreme=total('extreme');rate=wilson(primary.get('MODULA',0))
    result=dict(N=n,rho=rho,scenario=label,MODULA=rate,primary=primary,secondary=secondary,extreme=extreme,
                eligible=bool(rate['lower']>=.8),used_for_size=rho==0,frames=records)
    write(OUT/f'{label}_candidate_{n}.json',result)
    print(json.dumps(dict(phase='scenario_complete',N=n,rho=rho,MODULA=rate,used_for_size=rho==0)),flush=True);return result


def main():
    code_guard();guard();OUT.mkdir(parents=True,exist_ok=False);EXTERNAL.mkdir(parents=True,exist_ok=False)
    write(OUT/'environment.json',dict(utc=dt.datetime.now(dt.timezone.utc).isoformat(),python=platform.python_version(),numpy=np.__version__,
        platform=platform.platform(),commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),workers=2,BLAS_threads=1))
    start=time.perf_counter()
    try:
        controls();p=pilot();rhohat=sensitivity_correlation();chosen=None;candidates=[]
        for n in CFG['candidates']:
            rec=run_scenario(n,p,0.,'primary_rho0');candidates.append(rec)
            if rec['eligible']:chosen=n;break
        n=chosen or 400
        sensitivity=[run_scenario(n,p,r,l) for r,l in [(.3,'sensitivity_rho03'),(.6,'sensitivity_rho06'),(rhohat,'sensitivity_Q13')]]
        final=dict(status='SIZE_SELECTED' if chosen else 'NO_ELIGIBLE_N',selected_splits=chosen,candidates=candidates,sensitivity=sensitivity,
                   seconds=time.perf_counter()-start,bootstrap=500,permutations=1999,replicates=400,cohort_trained=False,real_X_Y_associations=False)
        write(OUT/'summary.json',final);print(json.dumps({k:v for k,v in final.items() if k not in ('candidates','sensitivity')}),flush=True)
    except Exception:
        write(OUT/'FAILURE.json',dict(error=traceback.format_exc(),cohort_trained=False));raise


if __name__=='__main__':main()
