#!/usr/bin/env python3
"""E16-C: referencia explícita, autodiff y FD4 con error transportado."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import resource
import sys
import time

import autograd.numpy as anp
from autograd import grad, jacobian
import mpmath as mp
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config.json').read_text())


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def mm(a):
    """Promoción exacta de los floats representados, sin redondear vía decimal."""
    a=np.asarray(a)
    return mp.matrix([[mp.mpf(float(v)) for v in row] for row in a])


def norm(a):return mp.sqrt(mp.fsum(v*v for v in a))


def maximum(a):return max(abs(v) for v in a)


def scalar_cv(cv,p,kind):
    s1=p[0]*cv[0]+p[1]*cv[1]
    s2=p[0]*cv[2]+p[1]*cv[3]
    if kind=='sum':return s1+s2
    if kind=='product':return s1*s2
    if kind=='quadratic':return (s1*s1+s2*s2)/2
    if kind=='duplicate':return (p[0]+p[1])*cv[0]
    if kind=='constant':return cv[0]
    raise ValueError(kind)


def forward_mp(theta,inputs):
    """Sólo escalares del forward; no devuelve ni usa derivadas."""
    result=[mp.mpf(0)]*4
    for z1,z2 in inputs:
        a=mp.tanh(theta[0]*z1+theta[1]*z2+theta[4])
        b=mp.tanh(theta[2]*z1+theta[3]*z2+theta[5])
        f=theta[6]*a+theta[7]*b+theta[8]
        label=int(z1+z2>0)
        ell=label*f-mp.log(1+mp.exp(f))
        for k,w in enumerate([1,z1,z2,z1*z2]):result[k]+=w*ell/len(inputs)
    return result


def analytic_mp(theta,inputs):
    """Derivadas explícitas de la especificación, sin autodiff ni FD."""
    cv=mp.matrix(4,1);jc=mp.matrix(4,9);fisher=mp.matrix(9,9)
    for z1,z2 in inputs:
        a=mp.tanh(theta[0]*z1+theta[1]*z2+theta[4])
        b=mp.tanh(theta[2]*z1+theta[3]*z2+theta[5])
        f=theta[6]*a+theta[7]*b+theta[8]
        sig=1/(1+mp.exp(-f));label=int(z1+z2>0)
        ell=label*f-mp.log(1+mp.exp(f))
        t1=theta[6]*(1-a*a);t2=theta[7]*(1-b*b)
        rr=mp.matrix([t1*z1,t1*z2,t2*z1,t2*z2,t1,t2,a,b,1])
        weights=[1,z1,z2,z1*z2]
        for k,w in enumerate(weights):
            cv[k]+=w*ell/len(inputs)
            for i in range(9):jc[k,i]+=w*(label-sig)*rr[i]/len(inputs)
        fisher+=sig*(1-sig)*(rr*rr.T)/len(inputs)
    g=fisher+mp.mpf(str(CFG['rho']))*mp.eye(9)
    c=g**-1;l=mp.cholesky(c)
    return cv,jc,c,l


def analytic_B(cv,jc,p,kind):
    j1=jc[:2,:];j2=jc[2:,:]
    s1=p[0]*cv[0]+p[1]*cv[1];s2=p[0]*cv[2]+p[1]*cv[3]
    v1=p[0]*jc[0,:]+p[1]*jc[1,:]
    v2=p[0]*jc[2,:]+p[1]*jc[3,:]
    c1=mp.matrix([cv[0],cv[1]]);c2=mp.matrix([cv[2],cv[3]])
    if kind=='sum':return j1+j2,j1+j2
    if kind=='product':return s2*j1+s1*j2+c2*v1+c1*v2,s2*j1+s1*j2
    if kind=='quadratic':return s1*j1+s2*j2+c1*v1+c2*v2,s1*j1+s2*j2
    if kind=='duplicate':return mp.matrix([list(jc[0,:]),list(jc[0,:])]),None
    if kind=='constant':return mp.zeros(2,9),None
    raise ValueError(kind)


def fd_cache(theta,inputs,step):
    result={}
    for i in range(9):
        for offset in [-2,-1,1,2]:
            shifted=list(theta);shifted[i]+=offset*step
            result[i,offset]=forward_mp(shifted,inputs)
    return result


def finite_B(cache,p,step,kind):
    # Producto tensorial de dos stencils; sólo consulta escalares forward.
    offsets=[-2,-1,1,2];weights=[1,-8,8,-1]
    b=mp.matrix(2,9)
    for a in range(2):
        for i in range(9):
            terms=[]
            for ot,wt in zip(offsets,weights):
                cv=cache[i,ot]
                for op,wp in zip(offsets,weights):
                    pp=list(p);pp[a]+=op*step
                    terms.append(wt*wp*scalar_cv(cv,pp,kind))
            b[a,i]=mp.fsum(terms)/(144*step*step)
    return b


def logits_ad(theta,inputs):
    w=anp.reshape(theta[:4],(2,2))
    return anp.dot(anp.tanh(anp.dot(inputs,w.T)+theta[4:6]),theta[6:8])+theta[8]


def scalar_ad(theta,p,inputs,kind):
    f=logits_ad(theta,inputs)
    labels=(np.sum(inputs,axis=1)>0).astype(float)
    ell=labels*f-anp.logaddexp(0.,f)
    weights=anp.stack([anp.ones(len(inputs)),inputs[:,0],inputs[:,1],inputs[:,0]*inputs[:,1]])
    cv=anp.dot(weights,ell)/len(inputs)
    if kind=='constant':return cv[0]+0.*anp.sum(p)
    return scalar_cv(cv,p,kind)


def ad_setup(theta,inputs):
    rr=jacobian(lambda th:logits_ad(th,inputs))(theta)
    f=np.asarray(logits_ad(theta,inputs));prob=1/(1+np.exp(-f))
    fisher=rr.T@((prob*(1-prob))[:,None]*rr)/len(inputs)
    g=fisher+CFG['rho']*np.eye(9)
    c=np.linalg.solve(g,np.eye(9));l=np.linalg.cholesky(c)
    return l


def singulars(u):return [mp.mpf(s) for s in mp.svd(u,compute_uv=False)]


def fmt(v):return mp.nstr(v,35) if isinstance(v,mp.mpf) else v


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--progress',action='store_true');args=parser.parse_args()
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    start=time.perf_counter();checks=[];ranks=[];negatives=[];timings=[]
    group='setup';key=''
    env={'started_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,
         'numpy':np.__version__,'autograd':version('autograd'),'mpmath':mp.__version__,
         'platform':platform.platform(),'dps':[80,120],'fd_steps':CFG['fd_steps'],
         'threads':{v:os.environ.get(v) for v in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS']},
         'script_sha256':sha(Path(__file__)),'config_sha256':sha(ROOT/'config.json'),
         'design_sha256':sha(ROOT/'DESIGN_FROZEN.md'),'training_steps':0,'seed':None}
    (out/'environment.json').write_text(json.dumps(env,indent=2)+'\n')

    def table(name,rows):
        if rows:
            with (out/name).open('w') as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
                w.writeheader();w.writerows(rows)

    def check(name,value,threshold,status=None,relative=''):
        if status is None:status='PASS' if value<=threshold else 'INCONCLUSIVE'
        checks.append({'group':group,'config':key,'check':name,'value':fmt(value),
                       'relative':fmt(relative),'threshold':fmt(threshold),'status':status})

    def finish():
        for name,rows in [('checks.csv',checks),('ranks.csv',ranks),('negative_controls.csv',negatives)]:table(name,rows)
        elapsed=time.perf_counter()-start
        statuses=[r['status'] for r in checks if r['group']==group]
        status='FAIL' if 'FAIL' in statuses else ('INCONCLUSIVE' if 'INCONCLUSIVE' in statuses else 'PASS')
        timings.append({'group':group,'status':status,'elapsed_seconds':elapsed})
        (out/'timing.json').write_text(json.dumps(timings,indent=2)+'\n')
        if args.progress:
            with (ROOT/'progress.md').open('a') as f:
                f.write(f'\n- {out.name}, {group}: {status}, {elapsed:.3f} s acumulados; '
                        f'tablas en `{out.relative_to(ROOT)}`.\n')
        print(group,status,flush=True)
        if elapsed>120:raise TimeoutError('Presupuesto 120 s excedido; salida parcial conservada')

    inputs_all=CFG['inputs']
    for state,tv in CFG['states'].items():
        for panel,indices in CFG['panels'].items():
            group=f'{state}_{panel}'
            inputs=[inputs_all[i] for i in indices]
            # Datos mpmath de literales decimales antes de operar.
            with mp.workdps(80):
                theta80=[mp.mpf(str(v)) for v in tv]
                reference80=analytic_mp(theta80,inputs)
                caches=[fd_cache(theta80,inputs,mp.mpf(str(step))) for step in CFG['fd_steps']]
                forward80=forward_mp(theta80,inputs)
            theta_np=np.array(tv,dtype=float);inputs_np=np.array(inputs,dtype=float)
            lad_np=ad_setup(theta_np,inputs_np)
            with mp.workdps(120):
                theta=[mp.mpf(str(v)) for v in tv]
                cv,jc,c,l=analytic_mp(theta,inputs)
                cv80,jc80,c80,l80=reference80
                key=f'{state}/{panel}/referencia'
                forward_error=maximum(mp.matrix(forward80)-cv80)
                check('forward_independiente',forward_error,mp.mpf('1e-70'),
                      status='PASS' if forward_error<=mp.mpf('1e-70') else 'FAIL')
                # Negativos y controles se procesan bajo el mismo criterio de error.
                configurations=[(index,kind,p) for index,p in enumerate(CFG['perspectives']) for kind in CFG['compositions']]
                configurations += [('control','constant',[1,1]),('control','duplicate',[1,1])]
                for point,kind,pv in configurations:
                    key=f'{state}/{panel}/p{point}/{kind}'
                    p=[mp.mpf(str(v)) for v in pv]
                    bref,trunc=analytic_B(cv,jc,p,kind)
                    uref=bref*l;sref=singulars(uref)
                    tau=mp.mpf('1e-8')*max(1,sref[0]);target=tau/10
                    scale=max(1,norm(uref))
                    with mp.workdps(80):
                        p80=[mp.mpf(str(v)) for v in pv]
                        b80,_=analytic_B(cv80,jc80,p80,kind)
                        u80=b80*l80
                        fd=[finite_B(cache,p80,mp.mpf(str(step)),kind) for cache,step in zip(caches,CFG['fd_steps'])]
                    precision=norm(u80-uref)
                    check('precision_80_120',precision,mp.mpf('1e-50')*scale)
                    p_np=np.array(pv,dtype=float)
                    bad_np=jacobian(grad(lambda th,pp:scalar_ad(th,pp,inputs_np,kind),0),1)(theta_np,p_np).T
                    bad=mm(bad_np);lad=mm(lad_np)
                    uad=bad*lad
                    term1=(bad-bref)*l;term2=bad*(lad-l)
                    err_direct=norm(uad-uref)
                    triangle=norm(term1)+norm(term2)
                    residual=norm((uad-uref)-(term1+term2))
                    tolerance=mp.mpf('1e-60')*scale
                    check('identidad_error_transportado',residual,tolerance,
                          status='PASS' if residual<=tolerance else 'FAIL')
                    check('cota_triangular',max(0,err_direct-triangle),tolerance,
                          status='PASS' if err_direct<=triangle+tolerance else 'FAIL')
                    check('AD_error_transportado',triangle,target)
                    berror=maximum(bad-bref);bscale=maximum(bref)
                    check('AD_B_absoluto',berror,mp.mpf('1e-10')+mp.mpf('1e-9')*bscale,
                          relative=berror/bscale if bscale else '')
                    methods=[('analytic80',u80,precision),('autodiff',uad,triangle)]
                    fd_errors=[]
                    for step,bfd in zip(CFG['fd_steps'],fd):
                        error=norm((bfd-bref)*l);fd_errors.append(error)
                        check(f'FD4_error_transportado_{step}',error,target)
                        eb=maximum(bfd-bref)
                        # Descriptores: no cambian decisión ni añaden umbrales.
                        check(f'FD4_B_absoluto_{step}',eb,'',status='DESCRIPTIVE',relative=eb/bscale if bscale else '')
                        hb=bfd*c*bfd.T;hr=bref*c*bref.T
                        eh=maximum(hb-hr);hscale=maximum(hr)
                        check(f'FD4_h_absoluto_{step}',eh,'',status='DESCRIPTIVE',relative=eh/hscale if hscale else '')
                        methods.append((f'FD4_{step}',bfd*l,error))
                    ambiguous=any(tau/10<=s<=10*tau for s in sref)
                    reference_rank=sum(s>tau for s in sref)
                    known={'constant':0,'duplicate':1}.get(kind)
                    known_bad=known is not None and reference_rank!=known
                    # Margen por método respecto de la referencia computada, no certificado exacto.
                    robust=True;different=False;method_ranks={}
                    for name,u,error in methods:
                        sv=singulars(u);r=sum(s>tau for s in sv);method_ranks[name]=r
                        if r!=reference_rank:different=True
                        for i,s in enumerate(sv):
                            if reference_rank>i:robust &= bool(s-error>tau)
                            else:robust &= bool(s+error<tau)
                    current=[r['status'] for r in checks if r['config']==key]
                    if known_bad or (different and not ambiguous):status='FAIL'
                    elif ambiguous or not robust or 'INCONCLUSIVE' in current:status='INCONCLUSIVE'
                    elif 'FAIL' in current:status='FAIL'
                    else:status='PASS_NUMERICAL'
                    check('decision_rango',0 if status=='PASS_NUMERICAL' else 1,0,
                          status='PASS' if status=='PASS_NUMERICAL' else status)
                    ranks.append({'state':state,'panel':panel,'point':point,'composition':kind,
                                  'sigma_max':fmt(sref[0]),'sigma_min':fmt(sref[1]),'tau':fmt(tau),
                                  'rank_reference':reference_rank,'rank_methods':json.dumps(method_ranks,sort_keys=True),
                                  'precision_80_120':fmt(precision),'AD_B_transport':fmt(norm(term1)),
                                  'AD_L_transport':fmt(norm(term2)),'AD_triangle':fmt(triangle),
                                  'FD4_error_0.002':fmt(fd_errors[0]),'FD4_error_0.001':fmt(fd_errors[1]),
                                  'expected_rank_control':known if known is not None else '',
                                  'status':status})
                    if trunc is not None and kind in ['product','quadratic']:
                        error=norm((trunc-bref)*l)
                        ns='PASS' if error>tau else 'INCONCLUSIVE'
                        check('negativo_omision_mixto',error,tau,status=ns)
                        negatives.append({'state':state,'panel':panel,'point':point,'composition':kind,
                                          'transported_error':fmt(error),'threshold':fmt(tau),'status':ns})
            finish()
    elapsed=time.perf_counter()-start
    rank_status=[r['status'] for r in ranks]
    counted=[r['status'] for r in checks if r['status']!='DESCRIPTIVE']
    result={'status':'FAIL' if 'FAIL' in counted else ('INCONCLUSIVE' if 'INCONCLUSIVE' in counted else 'PASS_NUMERICAL'),
            'rank_configurations':len(ranks),'main_configurations':sum(r['point']!='control' for r in ranks),
            'known_rank_controls':sum(r['point']=='control' for r in ranks),
            'rank_pass':rank_status.count('PASS_NUMERICAL'),'rank_fail':rank_status.count('FAIL'),
            'rank_inconclusive':rank_status.count('INCONCLUSIVE'),
            'main_rank_values':sorted(set(r['rank_reference'] for r in ranks if r['point']!='control')),
            'negative_controls':len(negatives),'negative_pass':sum(r['status']=='PASS' for r in negatives),
            'checks':len(checks),'checks_pass':counted.count('PASS'),'checks_fail':counted.count('FAIL'),
            'checks_inconclusive':counted.count('INCONCLUSIVE'),'descriptive_checks':sum(r['status']=='DESCRIPTIVE' for r in checks),
            'max_AD_triangle':fmt(max(mp.mpf(r['AD_triangle']) for r in ranks)),
            'max_FD4_error_0.002':fmt(max(mp.mpf(r['FD4_error_0.002']) for r in ranks)),
            'max_FD4_error_0.001':fmt(max(mp.mpf(r['FD4_error_0.001']) for r in ranks)),
            'max_precision_difference':fmt(max(mp.mpf(r['precision_80_120']) for r in ranks)),
            'prior_E16_B_status_unchanged':'INCONCLUSIVE','rigorous_certificate':False,'training_steps':0}
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    (out/'resources.json').write_text(json.dumps({'elapsed_seconds':elapsed,'budget_seconds':120,
        'budget_pass':elapsed<=120,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return 1 if result['status']=='FAIL' else 0


if __name__=='__main__':raise SystemExit(main())
