"""N200,11 niveles,A0 único; potencia individual y conjunta solo simulada."""
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
from support import ROOT,STAGE,CFG,SOURCES,OUT,EXTERNAL,source_path,sha,write,code_guard,guard,engine,analyst


def wilson(k,n=400):
    z=1.959963984540054;p=k/n;den=1+z*z/n;mid=(p+z*z/(2*n))/den;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return dict(success=int(k),n=n,rate=p,lower=mid-h,upper=mid+h)


def scenario(M):
    c=np.array(CFG['c']);d=np.array(CFG['target']);raw=np.array(CFG['target_raw']);result=[]
    for name in CFG['levels']:
        i=CFG['levels'].index(name);result.append(dict(level=name,c=float(c[i]),raw=float(raw[i]),target=float(d[i]),truncated=bool(raw[i]<0)))
    effective={}
    for m,nvs in M.MANIP.items():
        ids=[CFG['levels'].index(nv) for nv in nvs];beta=M.DR.pendiente(d[ids],c[ids]);r=M.DR.rango_c(c[ids])
        effective[m]=dict(beta_nominal=.077,beta_effective=beta,c_range=r,linear_contrast=beta*r,endpoint_D_difference=float(d[ids[0]]-d[ids[-1]]))
    return dict(formula='max(0,-0.038434071244996953+0.077*c)',points=result,effective=effective,
                D_estimates_never_clipped=True,piecewise_linear_not_globally_linear=True)


def pilot():
    p=source_path('pilot')
    with p.open() as f:rows=sorted([r for r in csv.DictReader(f) if int(r['level'])==2],key=lambda r:(int(r['split']),int(r['k'])))
    assert len(rows)==500 and all(r['pair_valid']=='True' for r in rows)
    assert {(int(r['split']),int(r['k'])) for r in rows}=={(s,k) for s in range(100) for k in range(5)}
    _,cen,_=engine();sp=np.repeat(np.arange(100),5)
    X=np.array([float(r['X10']) for r in rows]);L=np.log([float(r['rho_caras_10']) for r in rows]);Y=np.log([float(r['rho_caras_250']) for r in rows])
    z=(L-L.mean())/L.std();B=np.column_stack([cen(z**k,sp) for k in (1,2,3)])
    alpha=np.linalg.lstsq(B,cen(Y,sp),rcond=None)[0];res=cen(Y,sp)-B@alpha;df=500-100-np.linalg.matrix_rank(B)
    variance=float(res@res/df)
    write(OUT/'pilot.json',dict(source_sha256=sha(p),rows=500,s=.8,sigma2=variance,df=int(df),alpha=alpha.tolist(),
                               real_D_computed=False,real_X_Y_association_computed=False))
    return dict(X=X,L=L,alpha=alpha,sigma2=variance)


def statistics(M,D,p,slopes,boot):
    """All inputs are SIMULATED statistics; uses the draft's quantiles and labels."""
    R=D.shape[1];c=np.array(CFG['c']);passed=(D>0)&(p<.05)&(slopes>0)
    betas={};ci={};labels={};point={}
    for m,nvs in M.MANIP.items():
        ix=[CFG['levels'].index(nv) for nv in nvs];cc=c[ix]-c[ix].mean();block=boot[:,ix,:]
        b=np.sum(cc[None,:,None]*(block-block.mean(axis=1,keepdims=True)),axis=1)/np.sum(cc*cc)
        betas[m]=b;ci[m]=np.array([M.q(b[:,r],M.Q_PRI) for r in range(R)]).T
        point[m]=np.array([M.DR.pendiente(D[ix,r],c[ix]) for r in range(R)])
        labels[m]=['INCONCLUSIVE_SIN_SENAL_CONTROL' if not passed[0,r] else 'MODULA' if ci[m][0,r]>0 else 'NO_CONCLUYENTE' for r in range(R)]
    joint=[]
    for r in range(R):
        joint.append(M.conjunto({m:labels[m][r] for m in M.MANIP}) if passed[0,r] else 'INCONCLUSIVE_SIN_SENAL_CONTROL')
    return dict(passed=passed,beta_boot=betas,ci=ci,labels=labels,joint=joint,point_beta=point)


def controls():
    M=analyst();Engine,cen,bootstrap=engine();records=[]
    for j,n in enumerate((20,40)):
        g=np.random.default_rng(954000+j);sp=np.repeat(np.arange(n),5);L=g.normal(size=5*n);X=-4+.25*g.normal(size=5*n)
        e=Engine(sp,X,L,B=1999);sig=e.residual_X
        amps=np.array([.8,.6,.45,.25,.1,0,.6,.45,.25,.1,.01])
        if j==1:amps[6:]=.8
        Y=.2*e.base[:,0,None]+sig[:,None]*amps[None,:]+.04*cen(g.normal(size=(5*n,11)),sp)
        batch=e.calculate(Y,np.zeros(5*n),[0.]);D,p,slopes=batch['D'][0,:,None],batch['p'][0,:,None],batch['slopes'][0,:,None]
        draws=np.random.default_rng(960001).choice(n,size=(500,n),replace=True)
        boot=bootstrap(e,Y,np.zeros(5*n),[0.],draws)[0][:,:,None]
        got=statistics(M,D,p,slopes,boot);rows=[]
        for l,nv in enumerate(CFG['levels']):
            for s in range(n):
                for k in range(5):
                    i=5*s+k;rows.append(dict(trajectory=f'q13m2_{nv}_s{s:04d}_k{k}',X10=float(X[i]),rho_caras_10=float(np.exp(L[i])),
                        rho_caras_250=float(np.exp(Y[i,l])),c250=CFG['c'][l],q250=.001,acc_panel250=.93,error=''))
        ref=M.analizar(rows,n,True,'',ls=None,B=1999,NB=500)
        maxD=max(abs(ref['primaria'][nv]['D']-float(D[l,0])) for l,nv in enumerate(CFG['levels']))
        samep=all(ref['primaria'][nv]['p']==float(p[l,0]) for l,nv in enumerate(CFG['levels']))
        maxci=max(abs(ref['por_manipulador'][m]['IC975_beta'][a]-float(got['ci'][m][a,0])) for m in M.MANIP for a in range(2))
        labelok=all(ref['por_manipulador'][m]['veredicto']==got['labels'][m][0] for m in M.MANIP)
        jointok=ref['veredicto_conjunto']==got['joint'][0]
        arr={nv:dict(sp=sp,X=X,L=L,Y=Y[:,l],c=np.repeat(CFG['c'][l],5*n)) for l,nv in enumerate(CFG['levels'])}
        idx={nv:{s:np.flatnonzero(sp==s) for s in range(n)} for nv in CFG['levels']};blq=M.Q.bloques(np.arange(n));err=0.
        for b in range(12):
            direct,cs=M.replica(arr,CFG['levels'],idx,draws[b],blq)
            for l,nv in enumerate(CFG['levels']):err=max(err,abs(direct[nv]-float(boot[b,l,0])))
        records.append(dict(N=n,max_D_error=maxD,p_identical=bool(samep),max_IC975_error=maxci,
            same_individual_labels=labelok,same_joint_label=jointok,max_replica_error=err,reference_labels={m:ref['por_manipulador'][m]['veredicto'] for m in M.MANIP},
            pass_test=bool(maxD<=1e-10 and samep and maxci<=1e-10 and labelok and jointok and err<=1e-10)))
    result=dict(status='PASS' if all(r['pass_test'] for r in records) else 'FAIL',records=records,
                full_draft_analyst_executed_only_on_synthetic_controls=True,real_LS_reference_called=False)
    write(OUT/'controls.json',result);print(json.dumps(dict(phase='controls',status=result['status'])),flush=True)
    if result['status']!='PASS':raise RuntimeError('Controles fallidos; detener y preservar')


def frame_task(task):
    pilot,frame,rho=task;start=time.perf_counter();guard();M=analyst();Engine,cen,bootstrap=engine();n=200
    g=np.random.default_rng(np.random.SeedSequence([412000,2,n,frame]));draw=g.choice(100,n,replace=True)
    ix=(draw[:,None]*5+np.arange(5)).ravel();X,L=pilot['X'][ix],pilot['L'][ix];sp=np.repeat(np.arange(n),5)
    e=Engine(sp,X,L,B=1999);signal=e.residual_X;variance=float(np.mean(signal*signal));d=np.array(CFG['target'])
    amps=np.sqrt(d/(1-d)*.8*pilot['sigma2']/variance)
    g=np.random.default_rng(np.random.SeedSequence([413000,2,n,frame]));normals=g.normal(size=(5*n,12,100))
    noise=math.sqrt(rho)*normals[:,0:1,:]+math.sqrt(1-rho)*normals[:,1:,:]
    Y=np.empty((5*n,11,100));base=e.base@pilot['alpha']
    for l in range(11):Y[:,l,:]=base[:,None]+amps[l]*signal[:,None]+math.sqrt(pilot['sigma2'])*cen(noise[:,l,:],sp)
    yy=Y.reshape(5*n,1100);batch=e.calculate(yy,np.zeros(5*n),[0.]);D=batch['D'][0].reshape(11,100);p=batch['p'][0].reshape(11,100);slopes=batch['slopes'][0].reshape(11,100)
    draws=np.random.default_rng(960001).choice(n,size=(500,n),replace=True)
    boot=bootstrap(e,yy,np.zeros(5*n),[0.],draws)[0].reshape(500,11,100)
    if not np.isfinite(boot).all() or not np.isfinite(D).all():raise FloatingPointError('Estadístico no finito; preservar sin sustituir')
    result=statistics(M,D,p,slopes,boot)
    maxD=max(abs(M.Q.D_punto(sp,X,L,Y[:,l,0])-float(D[l,0])) for l in range(11))
    if maxD>1e-10:raise RuntimeError('D_punto no coincide en marco')
    name=f'rho{rho:g}_N200_frame{frame}';path=EXTERNAL/(name+'.npz')
    with path.open('xb') as f:
        np.savez_compressed(f,D=D,p=p,slopes=slopes,all_D=batch['all_D'],bootstrap_D=boot,
            bootstrap_beta_LP=result['beta_boot']['LP'],bootstrap_beta_WD=result['beta_boot']['WD'],
            IC975_beta_LP=result['ci']['LP'],IC975_beta_WD=result['ci']['WD'],
            labels_LP=np.array(result['labels']['LP']),labels_WD=np.array(result['labels']['WD']),joint=np.array(result['joint']),
            pilot_draw=draw,bootstrap_draw=draws,normal_noise=normals,c=np.array(CFG['c']),targets=d,multipliers=amps)
    rec=dict(N=200,rho=rho,frame=frame,replicates=100,
             LP=dict(collections.Counter(result['labels']['LP'])),WD=dict(collections.Counter(result['labels']['WD'])),
             joint_labels=dict(collections.Counter(result['joint'])),
             both_MODULA=sum(a==b=='MODULA' for a,b in zip(result['labels']['LP'],result['labels']['WD'])),
             control_PASS=int(result['passed'][0].sum()),A0_unique=True,max_D_error=maxD,seconds=time.perf_counter()-start,
             array=dict(path=str(path),bytes=path.stat().st_size,sha256=sha(path)))
    write(OUT/(name+'.json'),rec);return rec


def main():
    code_guard();guard();OUT.mkdir(exist_ok=False);EXTERNAL.mkdir(parents=True,exist_ok=False);start=time.perf_counter()
    write(OUT/'environment.json',dict(utc=dt.datetime.now(dt.timezone.utc).isoformat(),python=platform.python_version(),numpy=np.__version__,platform=platform.platform(),
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),workers=2,BLAS_threads=1))
    try:
        M=analyst();write(OUT/'scenario.json',scenario(M));controls();p=pilot();scenarios=[]
        for rho in CFG['rhos']:
            records=[]
            with cf.ProcessPoolExecutor(max_workers=2) as pool:
                for rec in pool.map(frame_task,[(p,f,rho) for f in range(4)]):
                    records.append(rec);print(json.dumps(dict(phase='frame',rho=rho,frame=rec['frame'],seconds=rec['seconds'])),flush=True)
            total=lambda key:dict(sum((collections.Counter(r[key]) for r in records),collections.Counter()))
            lp,wd=total('LP'),total('WD');lpr,wdr=wilson(lp.get('MODULA',0)),wilson(wd.get('MODULA',0));joint=wilson(sum(r['both_MODULA'] for r in records))
            r=dict(rho=rho,N=200,replicates=400,LP=lpr,WD=wdr,both_MODULA=joint,counts_LP=lp,counts_WD=wd,joint_labels=total('joint_labels'),
                   used_for_decision=rho==0,meets_individual_rule=bool(lpr['lower']>=.8 and wdr['lower']>=.8),joint_required=False,frames=records)
            write(OUT/f'scenario_rho{rho:g}.json',r);scenarios.append(r)
            print(json.dumps({k:v for k,v in r.items() if k!='frames'}),flush=True)
        final=dict(status='PREPARACION_COMPLETA',N=200,replicates_per_rho=400,bootstrap=500,permutations=1999,primary_interval=.975,
                   scenarios=scenarios,meets_primary_individual_rule=scenarios[0]['meets_individual_rule'],seconds=time.perf_counter()-start,
                   target_analyst_sha256=SOURCES['M2']['sha256'],analyst_not_frozen=True,requires_frozen_SHA_check_or_repeat=True,
                   real_D_computed=False,plan_generated=False,cohort_generated=False)
        write(OUT/'summary.json',final);print(json.dumps({k:v for k,v in final.items() if k!='scenarios'}),flush=True)
    except Exception:
        write(OUT/'FAILURE.json',dict(error=traceback.format_exc(),plan_generated=False,cohort_generated=False));raise


if __name__=='__main__':main()
