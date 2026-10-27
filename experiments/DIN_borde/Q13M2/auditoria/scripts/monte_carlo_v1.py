"""Tamaño nominal M2,N320,D constante; álgebra independiente validada."""
import collections
import concurrent.futures as cf
import datetime as dt
import json
import math
import platform
import subprocess
import time
import traceback
import numpy as np
import kernels as K
from support import ROOT,STAGE,CFG,EXT,write,sha,code_guard,guard,target,wilson

OUT=STAGE/'results/monte_carlo_v1'
INDICES=None;DRAWS=None


def classify(m,D,p,slope,boot):
    c=np.array(CFG['c']);passed=bool(p[0]<.05 and D[0]>0 and slope[0]>0);labels={};bb={};ci={}
    for arm,nvs in m.MANIP.items():
        ix=[m.NOMBRES.index(nv) for nv in nvs];cc=c[ix]-c[ix].mean();block=boot[:,ix]
        bb[arm]=np.sum(cc[None,:]*(block-block.mean(axis=1,keepdims=True)),axis=1)/np.sum(cc*cc)
        ci[arm]=m.q(bb[arm],m.Q_PRI)
        labels[arm]='INCONCLUSIVE_SIN_SENAL_CONTROL' if not passed else 'MODULA' if ci[arm][0]>0 else 'NO_CONCLUYENTE'
    return dict(labels=labels,beta=bb,ci=ci,control_PASS=passed)


def controls():
    m=target();records=[]
    for j,n in enumerate((20,40)):
        g=np.random.default_rng(CFG['control_seed']+j);X=-4+.25*g.normal(size=5*n);L=g.normal(size=5*n);sp=np.repeat(np.arange(n),5)
        base=K.basis(L);signal=K.center(X)-base@np.linalg.lstsq(base,K.center(X),rcond=None)[0]
        amps=np.array([.8,.6,.45,.25,.1,0,.6,.45,.25,.1,.01])
        if j:amps[6:]=.8
        Y=.2*base[:,0,None]+signal[:,None]*amps[None,:]+.04*K.center(g.normal(size=(5*n,11)))
        pri=K.primary(X,L,Y,K.permutation_indices(n,499));draw=np.random.default_rng(960001).choice(n,size=(64,n),replace=True)
        boot=K.bootstrap(X,L,Y,draw);got=classify(m,pri['D'],pri['p'],pri['slope'],boot)
        rows=[]
        for l,nv in enumerate(m.NOMBRES):
            for s in range(n):
                for k in range(5):
                    i=5*s+k;rows.append(dict(trajectory=f'q13m2_{nv}_s{s:04d}_k{k}',X10=float(X[i]),rho_caras_10=float(np.exp(L[i])),
                        rho_caras_250=float(np.exp(Y[i,l])),c250=CFG['c'][l],q250=.001,acc_panel250=.93,error=''))
        ref=m.analizar(rows,n,True,'',B=499,NB=64)
        err=max(abs(pri['D'][l]-ref['primaria'][nv]['D']) for l,nv in enumerate(m.NOMBRES))
        samep=all(pri['p'][l]==ref['primaria'][nv]['p'] for l,nv in enumerate(m.NOMBRES))
        cierr=max(abs(got['ci'][arm][q]-ref['por_manipulador'][arm]['IC975_beta'][q]) for arm in ('LP','WD') for q in (0,1))
        same_labels=all(got['labels'][arm]==ref['por_manipulador'][arm]['veredicto'] for arm in ('LP','WD'))
        # Nominal permutation count and nominal bootstrap count, against originals.
        nominal=K.primary(X,L,Y[:,:1],K.permutation_indices(n,5000));original=m.A.primaria(sp,X,L,Y[:,0],3,260001,5000)
        nomerr=abs(nominal['D'][0]-original['D']);nomp=nominal['p'][0]==original['p']
        ds=np.random.default_rng(960001).choice(n,size=(2000,n),replace=True);bn=K.bootstrap(X,L,Y,ds);blq=m.Q.bloques(np.arange(n));berr=0.
        for b in range(8):
            ii=(ds[b,:,None]*5+np.arange(5)).ravel();ns=np.repeat(np.arange(n),5);fo=np.repeat([blq[s] for s in ds[b]],5)
            for l in range(11):berr=max(berr,abs(m.Q.D_punto(ns,X[ii],L[ii],Y[ii,l],fo)-bn[b,l]))
        records.append(dict(N=n,max_D_error=float(err),p_identical=bool(samep),max_IC_error=float(cierr),labels_same=same_labels,
             nominal_D_error=float(nomerr),nominal_p_identical=bool(nomp),nominal_boot_error=float(berr),
             pass_test=bool(err<=1e-10 and samep and cierr<=1e-10 and same_labels and nomerr<=1e-10 and nomp and berr<=1e-10)))
    result=dict(status='PASS' if all(r['pass_test'] for r in records) else 'FAIL',records=records,independent_kernel=True)
    write(OUT/'controls.json',result);print(json.dumps(dict(phase='controls',status=result['status'])),flush=True)
    if result['status']!='PASS':raise RuntimeError('Control nominal no coincide')


def caches():
    global INDICES,DRAWS
    if INDICES is None:INDICES=K.permutation_indices(320,5000)
    if DRAWS is None:DRAWS=np.random.default_rng(960001).choice(320,size=(2000,320),replace=True)
    return INDICES,DRAWS


def run_rep(task):
    cell,rho,rep=task;guard();start=time.perf_counter();n=320;g=np.random.default_rng(np.random.SeedSequence([CFG['MC_seed'],cell,rep]));m=target()
    X=-4+.25*g.normal(size=5*n);L=g.normal(size=5*n)+.3*np.repeat(g.normal(size=n),5)
    base=K.basis(L);signal=K.center(X)-base@np.linalg.lstsq(base,K.center(X),rcond=None)[0];signal/=np.sqrt(np.mean(signal*signal))
    d=CFG['MC_D_constant'];amp=math.sqrt(d/(1-d)*.8)
    noise=math.sqrt(rho)*g.normal(size=(5*n,1))+math.sqrt(1-rho)*g.normal(size=(5*n,11))
    Y=(base@np.array([.3,-.05,.02]))[:,None]+amp*signal[:,None]+K.center(noise)
    indices,draws=caches();pri=K.primary(X,L,Y,indices);boot=K.bootstrap(X,L,Y,draws)
    if not np.isfinite(pri['D']).all() or not np.isfinite(boot).all():raise FloatingPointError('Estadístico no finito')
    r=classify(m,pri['D'],pri['p'],pri['slope'],boot);fp={a:r['labels'][a]=='MODULA' for a in ('LP','WD')}
    name=f'null_rho{rho:g}_N320_r{rep:04d}';path=EXT/'monte_carlo_v1'/(name+'.npz')
    with path.open('xb') as f:np.savez_compressed(f,X=X,L=L,Y=Y,D=pri['D'],p=pri['p'],slopes=pri['slope'],all_D=pri['all_D'],
        bootstrap_D=boot,beta_LP=r['beta']['LP'],beta_WD=r['beta']['WD'])
    rec=dict(cell=cell,rho=rho,replica=rep,N=320,D_constant=.02,beta_true=0,control_PASS=r['control_PASS'],
         labels=r['labels'],IC975=r['ci'],false_MODULA_LP=fp['LP'],false_MODULA_WD=fp['WD'],family_error=fp['LP'] or fp['WD'],both_false=fp['LP'] and fp['WD'],
         seconds=time.perf_counter()-start,array=dict(path=str(path),sha256=sha(path),bytes=path.stat().st_size))
    write(OUT/(name+'.json'),rec);return rec


def bounded(tasks,deliver):
    with cf.ProcessPoolExecutor(max_workers=2) as pool:
        it=iter(tasks);pending=set()
        for _ in range(2):pending.add(pool.submit(run_rep,next(it)))
        try:
            while pending:
                done,_=cf.wait(pending,return_when=cf.FIRST_COMPLETED)
                for f in done:r=f.result();pending.remove(f);deliver(r)
                for _ in done:
                    t=next(it,None)
                    if t is not None:pending.add(pool.submit(run_rep,t))
        except BaseException:
            for f in pending:f.cancel()
            pool.shutdown(wait=True,cancel_futures=True);raise


def main():
    code_guard();guard();OUT.mkdir(parents=True,exist_ok=False);(EXT/'monte_carlo_v1').mkdir(parents=True,exist_ok=False);start=time.perf_counter()
    write(OUT/'environment.json',dict(utc=dt.datetime.now(dt.timezone.utc).isoformat(),python=platform.python_version(),numpy=np.__version__,platform=platform.platform(),
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),workers=2,BLAS_threads=1))
    try:
        controls();summaries=[]
        for cell,rho in enumerate(CFG['MC_rhos']):
            rows=[]
            def deliver(r):
                rows.append(r)
                if len(rows)%50==0:print(json.dumps(dict(phase='null',rho=rho,completed=len(rows),total=400,seconds=time.perf_counter()-start)),flush=True)
            bounded([(cell,rho,r) for r in range(400)],deliver)
            conditional=[r for r in rows if r['control_PASS']]
            def rates(rr):return {k:wilson(sum(bool(r[k]) for r in rr),len(rr)) for k in ('false_MODULA_LP','false_MODULA_WD','family_error','both_false')}
            global_rates=rates(rows);conditional_rates=rates(conditional)
            fam=global_rates['family_error'];reading='COMPATIBLE_EN_MODELO' if fam['upper']<=.05 else 'INFLACION' if fam['lower']>.05 else 'INCONCLUSIVE_TAMANO'
            result=dict(rho=rho,N=320,replicates=400,control_PASS=len(conditional),control_fail=400-len(conditional),global_rates=global_rates,
                         conditional_on_control_PASS=conditional_rates,family_reading_vs_005=reading,
                         labels={arm:dict(collections.Counter(r['labels'][arm] for r in rows)) for arm in ('LP','WD')})
            write(OUT/f'cell_rho{rho:g}.json',result);summaries.append(result);print(json.dumps(dict(phase='cell_complete',**result)),flush=True)
        write(OUT/'summary.json',dict(status='COMPLETED',cells=summaries,replicates=800,seconds=time.perf_counter()-start,permutations=5000,bootstrap=2000,
              primary_quantiles=[.0125,.9875],real_data_used=False,universal_error_control_certified=False))
    except BaseException:
        write(OUT/'FAILURE.json',dict(error=traceback.format_exc(),replicates_not_replaced=True));raise


if __name__=='__main__':main()
