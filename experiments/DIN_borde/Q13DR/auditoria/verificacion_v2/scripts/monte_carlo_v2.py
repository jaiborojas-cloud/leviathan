"""Repetición nominal v2: mismas semillas/datos sintéticos, políticas v2."""
import concurrent.futures as cf
import datetime
import json
import platform
import subprocess
import sys
import time
import traceback
import numpy as np
from support import ROOT,STAGE,CFG,EXTERNAL,write,sha,code_guard,guard,target,wilson
from kernels import center,basis,primary,bootstrap,permutation_indices

OUT=STAGE/'results/monte_carlo_v2';ARRAYS=EXTERNAL/'monte_carlo_v2'
R=None;INDEX={};DRAWS={}


def controls():
    m=target();records=[]
    for case in range(3):
        rng=np.random.default_rng(CFG['controls_seed']+case);n=30
        X=-4+.25*rng.normal(size=5*n);L=rng.normal(size=5*n);Y=rng.normal(size=(5*n,6))+.2*center(X)[:,None]
        count=5000 if case==0 else 199;out=primary(X,L,Y,permutation_indices(n,count));sp=np.repeat(np.arange(n),5)
        err=0.;same=True
        for l in range(6):
            a=m.A.primaria(sp,X,L,Y[:,l],3,260001,count)
            err=max(err,abs(out['D'][l]-a['D']));same=same and out['p'][l]==a['p']
        draws=np.random.default_rng(860001).choice(n,size=(64,n),replace=True);bb=bootstrap(X,L,Y,draws);be=0.;blq=m.Q.bloques(np.arange(n))
        for b in range(16):
            ix=(draws[b,:,None]*5+np.arange(5)).ravel();fo=np.repeat([blq[s] for s in draws[b]],5)
            for l in range(6):be=max(be,abs(m.Q.D_punto(sp,X[ix],L[ix],Y[ix,l],fo)-bb[b,l]))
        records.append(dict(case=case,permutations=count,max_D_error=err,p_identical=bool(same),max_bootstrap_error=be,pass_test=bool(err<=1e-10 and same and be<=1e-10)))
    result=dict(status='PASS' if all(r['pass_test'] for r in records) else 'FAIL',records=records)
    write(OUT/'controls.json',result)
    if result['status']!='PASS':raise RuntimeError('Motor no coincide con v2')


def worker(task):
    global R
    ci,rep=task;cell=CFG['cells'][ci];n=cell['N'];start=time.perf_counter()
    if R is None:guard();R=target()
    if n not in INDEX:INDEX[n]=permutation_indices(n,CFG['permutations'])
    if n not in DRAWS:DRAWS[n]=np.random.default_rng(860001).choice(n,size=(CFG['bootstrap'],n),replace=True)
    # Índice de la celda ORIGINAL: la positiva sigue siendo 3, no 2.
    rng=np.random.default_rng(np.random.SeedSequence([CFG['seed_base'],cell['seed_index_v1'],rep]))
    X=-4+.25*rng.normal(size=5*n);L=rng.normal(size=5*n)+np.repeat(.3*rng.normal(size=n),5)
    B=basis(L);sig=center(X)-B@np.linalg.lstsq(B,center(X),rcond=None)[0];sig/=np.sqrt(np.mean(sig*sig))
    c=np.array(CFG['levels_c']);effects=cell['D_center']+cell['beta']*(c-c.mean());beta=np.sqrt(effects/(1-effects)*.8)
    noise=rng.normal(size=(5*n,6));Y=(B@np.array([.3,-.05,.02]))[:,None]+sig[:,None]*beta[None,:]+center(noise)
    actual=primary(X,L,Y,INDEX[n]);passed=(actual['D']>0)&(actual['p']<.05)&(actual['slope']>0)
    boot=bootstrap(X,L,Y,DRAWS[n]);bpoint=R.pendiente(actual['D'],c);bboot=np.array([R.pendiente(row,c) for row in boot]);ic=np.quantile(bboot,[.025,.975]);ic5=np.quantile(boot[:,5],[.025,.975])
    label=R.clasificar_beta(ic) if passed[0] else 'INCONCLUSIVE_SIN_SENAL_CONTROL'
    eq=R.equivalencia(ic) if passed[0] else 'NOT_EVALUATED'
    extreme=R.clasificar_extremo(bool(passed[5]),ic5) if passed[0] else 'NOT_EVALUATED'
    oldpath=Path(CFG['old_synthetic_arrays'])/f'{cell["name"]}_r{rep:04d}.npz'
    with np.load(oldpath,allow_pickle=False) as old:
        same_data=all(np.array_equal(old[k],v) for k,v in [('X',X),('L',L),('Y',Y)])
        same_math=all(np.array_equal(old[k],v) for k,v in [('D',actual['D']),('p',actual['p']),('bootstrap_beta',bboot)])
    if not (same_data and same_math):raise RuntimeError('Semillas o álgebra discrepan de v1; no sustituir réplicas')
    p=ARRAYS/f'{cell["name"]}_r{rep:04d}.npz'
    with p.open('xb') as f:np.savez_compressed(f,X=X,L=L,Y=Y,effects=effects,D=actual['D'],p=actual['p'],slope=actual['slope'],all_D=actual['all_D'],bootstrap_D=boot,bootstrap_beta=bboot,IC_beta=ic,IC_D5=ic5,c=c)
    return dict(cell=cell['name'],rep=rep,N=n,seed_index_v1=cell['seed_index_v1'],true_beta=cell['beta'],D_center=cell['D_center'],control_PASS=bool(passed[0]),
        verdict=label,equivalence_secondary=eq,extreme=extreme,beta_point=bpoint,IC_beta=ic.tolist(),D=actual['D'].tolist(),p=actual['p'].tolist(),
        data_identical_v1=same_data,math_identical_v1=same_math,old_array_sha256=sha(oldpath),seconds=time.perf_counter()-start,
        array=dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size))


def main():
    code_guard();guard();OUT.mkdir(parents=True,exist_ok=False);EXTERNAL.mkdir(parents=True,exist_ok=True);ARRAYS.mkdir(exist_ok=False)
    write(OUT/'environment.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=sys.version,numpy=np.__version__,platform=platform.platform(),workers=2,commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()))
    controls();print(json.dumps(dict(controls='PASS')),flush=True);start=time.perf_counter();cells=[]
    try:
        with cf.ProcessPoolExecutor(max_workers=2) as pool:
            for ci,cell in enumerate(CFG['cells']):
                records=[]
                for r in pool.map(worker,[(ci,j) for j in range(cell['reps'])],chunksize=1):
                    records.append(r);write(OUT/f'{cell["name"]}_{r["rep"]:04d}.json',r)
                    if len(records)%25==0:print(json.dumps(dict(cell=cell['name'],done=len(records),planned=cell['reps'],seconds=time.perf_counter()-start)),flush=True)
                selected=[r for r in records if r['control_PASS']]
                def rates(field,names):
                    return {name:dict(all=wilson(sum(r[field]==name for r in records),len(records)),conditional_control=wilson(sum(r[field]==name for r in selected),len(selected))) for name in names}
                result=dict(cell=cell,replicates=len(records),control_PASS=len(selected),
                    rates=rates('verdict',('MODULA','NO_CONCLUYENTE','INCONCLUSIVE_SIN_SENAL_CONTROL')),
                    secondary_rates=rates('equivalence_secondary',('NO_MODULA','NO_ESTABLECIDA')),
                    extreme_rates=rates('extreme',('PERSISTE','DESAPARECE','INDETERMINADO')),
                    all_data_and_math_identical_v1=all(r['data_identical_v1'] and r['math_identical_v1'] for r in records))
                write(OUT/(cell['name']+'_summary.json'),result);cells.append(result);print(json.dumps(dict(cell=cell['name'],complete=True)),flush=True)
        write(OUT/'summary.json',dict(status='COMPLETE',cells=cells,bootstrap=CFG['bootstrap'],permutations=CFG['permutations'],seconds=time.perf_counter()-start,real_data_read=False))
    except BaseException:write(OUT/'FAILURE.json',dict(error=traceback.format_exc(),seconds=time.perf_counter()-start));raise


if __name__=='__main__':main()
