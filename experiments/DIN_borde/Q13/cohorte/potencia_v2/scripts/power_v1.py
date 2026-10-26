"""Potencia Q13: sólo simulaciones, sin leer la cohorte C2 ni datos Q13 reales."""
import ast
import concurrent.futures as cf
import csv
import datetime
import json
import math
import platform
import subprocess
import sys
import time
import traceback
import numpy as np
from support_v1 import ROOT,STAGE,CFG,OUT,EXTERNAL,write,sha,guard,code_guard,analyst


def engine_class():
    source=ROOT/CFG['sources']['C2_engine']['path']
    tree=ast.parse(source.read_text())
    tree.body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in ('cen','pinv','BatchedC1')]
    assert len(tree.body)==3
    env={'np':np}
    exec(compile(tree,str(source),'exec'),env)
    return env['BatchedC1'],env['cen']


def wilson(k,n=400):
    z=1.959963984540054;p=k/n
    c=(p+z*z/(2*n))/(1+z*z/n)
    h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return dict(success=int(k),n=n,rate=p,lower=c-h,upper=c+h)


def grouped_bootstrap(engine,Y0,signal,betas,draws):
    """OLS CV exacto por multiplicidades de split; mantiene su bloque original."""
    n=len(engine.sp)//5; nb=len(draws); R=Y0.shape[1]
    q,_=np.linalg.qr(engine.base)
    base=q*np.sqrt(5*n)
    x=engine.residual_X/np.sqrt(np.mean(engine.residual_X**2))
    C=np.column_stack([base,x]).reshape(n,5,4)
    y=Y0.reshape(n,5,R); s=signal.reshape(n,5)
    gram=np.einsum('nki,nkj->nij',C,C)
    h=np.einsum('nki,nkr->nir',C,y)
    hs=np.einsum('nki,nk->ni',C,s)
    yy=np.sum(y*y,axis=1);ys=np.sum(y*s[:,:,None],axis=1);ss=np.sum(s*s,axis=1)
    weights=np.zeros((nb,n))
    for b,draw in enumerate(draws):weights[b]=np.bincount(draw,minlength=n)
    fold=engine.fold.reshape(n,5)[:,0]
    all_sse=[]
    for d in (3,4):
        total=np.zeros((len(betas),nb,R))
        for f in range(10):
            te=weights*(fold==f)[None,:];tr=weights-te
            gt=(tr@gram.reshape(n,16)).reshape(nb,4,4)[:,:d,:d]
            ge=(te@gram.reshape(n,16)).reshape(nb,4,4)[:,:d,:d]
            ht=(tr@h.reshape(n,4*R)).reshape(nb,4,R)[:,:d]
            he=(te@h.reshape(n,4*R)).reshape(nb,4,R)[:,:d]
            hst=(tr@hs)[:,:d];hse=(te@hs)[:,:d]
            b0=np.linalg.solve(gt,ht)
            bs=np.linalg.solve(gt,hst[:,:,None])[:,:,0]
            e0=te@yy-2*np.sum(b0*he,axis=1)+np.einsum('bir,bij,bjr->br',b0,ge,b0)
            es=te@ys-np.sum(b0*hse[:,:,None],axis=1)-np.einsum('bi,bir->br',bs,he)+np.einsum('bir,bij,bj->br',b0,ge,bs)
            ess=te@ss-2*np.sum(bs*hse,axis=1)+np.einsum('bi,bij,bj->b',bs,ge,bs)
            for j,beta in enumerate(betas):total[j]+=e0+2*beta*es+beta*beta*ess[:,None]
        all_sse.append(total)
    if np.any(all_sse[0]<=0):raise FloatingPointError('SSE bootstrap base no positiva')
    return 1-all_sse[1]/all_sse[0]


def controls():
    Q=analyst();Engine,cen=engine_class();records=[]
    for j in range(3):
        rng=np.random.default_rng(754000+j);n=40;sp=np.repeat(np.arange(n),5)
        L=rng.normal(size=5*n);X=rng.normal(size=5*n)+.3*L
        engine=Engine(sp,X,L,B=1999)
        signal=engine.residual_X;betas=[0.,.08,.15]
        Y0=cen(rng.normal(size=(5*n,3)),sp)+(.2*engine.base[:,0])[:,None]
        batch=engine.calculate(Y0,signal,betas)
        max_D=0.;same_p=True
        for a,beta in enumerate(betas):
            yy=Y0[:,0]+beta*signal
            original=Q.A.primaria(sp,X,L,yy,3,260001,1999)
            max_D=max(max_D,abs(original['D']-float(batch['D'][a,0])))
            same_p=same_p and original['p']==float(batch['p'][a,0])
        draws=np.random.default_rng(760001).choice(n,size=(500,n),replace=True)
        boot=grouped_bootstrap(engine,Y0,signal,betas,draws)
        block=Q.bloques(np.arange(n));max_boot=0.
        for b in range(12):
            ii=(draws[b,:,None]*5+np.arange(5)).ravel();spnew=np.repeat(np.arange(n),5)
            fo=np.repeat([block[s] for s in draws[b]],5)
            for a,beta in enumerate(betas):
                for rep in range(3):
                    exact=Q.D_punto(spnew,X[ii],L[ii],(Y0[:,rep]+beta*signal)[ii],fo)
                    max_boot=max(max_boot,abs(exact-float(boot[a,b,rep])))
        records.append(dict(case=j,max_D_error=max_D,p_identical=bool(same_p),max_bootstrap_error=max_boot,
            pass_test=bool(max_D<=1e-10 and same_p and max_boot<=1e-10)))
    result=dict(status='PASS' if all(r['pass_test'] for r in records) else 'FAIL',records=records,
        real_cohort_access=False,Q13_main_or_analizar_executed=False)
    write(OUT/'controls.json',result)
    print(json.dumps(dict(phase='controls',status=result['status'])),flush=True)
    if result['status']!='PASS':raise RuntimeError('Motor no coincide con funciones congeladas; detener')


def pilot():
    p=ROOT/CFG['sources']['pilot']['path']
    rows=sorted([r for r in csv.DictReader(p.open()) if int(r['level'])==2],key=lambda r:(int(r['split']),int(r['k'])))
    assert len(rows)==500 and all(r['pair_valid']=='True' for r in rows)
    assert {(int(r['split']),int(r['k'])) for r in rows}=={(s,k) for s in range(100) for k in range(5)}
    _,cen=engine_class();sp=np.repeat(np.arange(100),5)
    X=np.array([float(r['X10']) for r in rows]);L=np.log([float(r['rho_caras_10']) for r in rows]);Y=np.log([float(r['rho_caras_250']) for r in rows])
    z=(L-L.mean())/L.std();B=np.column_stack([cen(z**k,sp) for k in (1,2,3)])
    alpha=np.linalg.lstsq(B,cen(Y,sp),rcond=None)[0];res=cen(Y,sp)-B@alpha
    df=500-100-np.linalg.matrix_rank(B)
    write(OUT/'pilot.json',dict(source_sha256=sha(p),s=.8,rows=500,sigma2=float(res@res/df),alpha=alpha.tolist(),df=int(df),
        actual_signal_association_estimated=False))
    return dict(X=X,L=L,alpha=alpha,sigma2=float(res@res/df))


def frame_task(task):
    N,p,frame=task;begin=time.perf_counter();guard()
    Engine,cen=engine_class();Q=analyst()
    rng=np.random.default_rng(np.random.SeedSequence([412000,2,N,frame]))
    draw=rng.choice(100,N,replace=True);ids=(draw[:,None]*5+np.arange(5)).ravel()
    X,L=p['X'][ids],p['L'][ids];sp=np.repeat(np.arange(N),5)
    engine=Engine(sp,X,L,B=1999);signal=engine.residual_X
    variance=float(np.mean(signal**2))
    betas=[math.sqrt(d/(1-d)*.8*p['sigma2']/variance) for d in CFG['targets']]
    rng=np.random.default_rng(np.random.SeedSequence([413000,2,N,frame]))
    noise=rng.normal(size=(5*N,100))
    Y0=(engine.base@p['alpha'])[:,None]+math.sqrt(p['sigma2'])*cen(noise,sp)
    result=engine.calculate(Y0,signal,betas)
    passed=(result['D']>0)&(result['p']<.05)&(result['slopes']>0)
    # Exact functions on simulated point outcomes; never real Q13 or C2 data.
    max_point=0.
    for j,beta in enumerate(betas):
        exact=Q.D_punto(sp,X,L,Y0[:,0]+beta*signal)
        max_point=max(max_point,abs(float(result['D'][j,0])-exact))
    if max_point>1e-10:raise RuntimeError('D_punto no coincide en simulación')
    boot_draw=np.random.default_rng(760001).choice(N,size=(500,N),replace=True)
    boot=grouped_bootstrap(engine,Y0,signal,betas,boot_draw)
    ci=np.quantile(boot,[.025,.975],axis=1)
    delta=boot[2]-boot[0];ci_delta=np.quantile(delta,[.025,.975],axis=0)
    labels=[Q.clasificar(float(result['D'][0,j]),bool(passed[0,j]),ci[:,0,j].tolist(),ci_delta[:,j].tolist()) for j in range(100)]
    cae=np.array([s=='CAE' for s in labels])
    name=f'N{N}_frame{frame}';path=EXTERNAL/(name+'.npz')
    with path.open('xb') as f:
        np.savez_compressed(f,D=result['D'],p=result['p'],slopes=result['slopes'],all_D=result['all_D'],baseline_SSE=result['baseline_SSE'],
            bootstrap_D=boot,bootstrap_draw=boot_draw,pilot_draw=draw,noise=noise,beta=np.array(betas),effects=np.array(CFG['targets']),
            passed=passed,cae=cae,ci_D=ci,ci_delta=ci_delta)
    rec=dict(N=N,frame=frame,replicates=100,PASS_counts=passed.sum(axis=1).tolist(),CAE_count=int(cae.sum()),
        target_values=CFG['targets'],max_D_punto_error=max_point,bootstrap=500,seconds=time.perf_counter()-begin,
        array=dict(path=str(path),sha256=sha(path),bytes=path.stat().st_size))
    write(OUT/(name+'.json'),rec)
    return rec


def main():
    code_guard();guard();OUT.mkdir(exist_ok=False);EXTERNAL.mkdir(exist_ok=False)
    write(OUT/'environment.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=sys.version,numpy=np.__version__,
        platform=platform.platform(),code_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),workers=2,BLAS_threads=1))
    try:
        controls();p=pilot();candidates=[];chosen=None;start=time.perf_counter()
        for N in CFG['candidates']:
            records=[]
            with cf.ProcessPoolExecutor(max_workers=2) as pool:
                for rec in pool.map(frame_task,[(N,p,f) for f in range(4)]):
                    records.append(rec)
                    print(json.dumps(dict(phase='simulation',N=N,frame=rec['frame'],complete=100,seconds=rec['seconds'])),flush=True)
            counts=np.sum([rec['PASS_counts'] for rec in records],axis=0)
            rates=[dict(target=t,**wilson(int(k))) for t,k in zip(CFG['targets'],counts)]
            cae=wilson(sum(rec['CAE_count'] for rec in records))
            eligible=rates[2]['lower']>=.8 and cae['lower']>=.8
            row=dict(N=N,PASS_estimates=rates,CAE_estimate=cae,eligible=bool(eligible),frames=records)
            write(OUT/f'candidate_{N}.json',row);candidates.append(row)
            print(json.dumps(dict(phase='candidate_complete',N=N,eligible=bool(eligible),PASS_lower=rates[2]['lower'],CAE_lower=cae['lower'])),flush=True)
            if eligible:chosen=N;break
        final=dict(status='NO_ELIGIBLE_N' if chosen is None else 'REQUIRES_CONFIRMATION' if chosen>400 else 'SIZE_SELECTED',
            selected_splits=chosen,candidates=candidates,replicates_per_N=400,bootstrap=500,permutations=1999,
            cohort_started=False,real_cohort_associations=False,seconds=time.perf_counter()-start)
        write(OUT/'summary.json',final)
        print(json.dumps({k:v for k,v in final.items() if k!='candidates'}),flush=True)
    except Exception:
        write(OUT/'FAILURE.json',dict(error=traceback.format_exc(),cohort_started=False))
        raise


if __name__=='__main__':main()
