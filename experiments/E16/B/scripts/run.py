#!/usr/bin/env python3
"""E16-B: red sintética fija; autodiff, cadena y NumPy FD independientes."""
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
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT/'config.json').read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def logits(theta, inputs, xp):
    w = xp.reshape(theta[:4], (2, 2))
    hidden = xp.tanh(xp.dot(inputs, w.T)+theta[4:6])
    return xp.dot(hidden, theta[6:8])+theta[8]


def basis(theta, inputs, labels, xp):
    f = logits(theta, inputs, xp)
    logs = labels*f-xp.logaddexp(0., f)
    weights = xp.stack([xp.ones(len(inputs)), inputs[:,0], inputs[:,1], inputs[:,0]*inputs[:,1]])
    return xp.dot(weights, logs)/len(inputs)


def components(theta, p, inputs, labels, xp):
    v = basis(theta, inputs, labels, xp)
    return xp.stack([xp.dot(p,v[:2]),xp.dot(p,v[2:])])


def scalar(theta, p, inputs, labels, kind, xp):
    s = components(theta,p,inputs,labels,xp)
    if kind == 'sum':
        return s[0]+s[1]
    if kind == 'product':
        return s[0]*s[1]
    if kind == 'quadratic':
        return xp.dot(s,s)/2
    raise ValueError(kind)


def direct(s, theta, p):
    w = grad(s,0)(theta,p)
    b = jacobian(grad(s,0),1)(theta,p).T
    return np.asarray(w),np.asarray(b)


def finite(s, theta, p, step):
    """Sólo evaluaciones escalares NumPy: no usa jacobianos/autodiff."""
    w = np.zeros(len(theta))
    b = np.zeros((len(p),len(theta)))
    for i in range(len(theta)):
        dt=np.zeros(len(theta));dt[i]=step
        w[i]=(s(theta+dt,p)-s(theta-dt,p))/(2*step)
        for a in range(len(p)):
            dp=np.zeros(len(p));dp[a]=step
            b[a,i]=(s(theta+dt,p+dp)-s(theta+dt,p-dp)-s(theta-dt,p+dp)+s(theta-dt,p-dp))/(4*step**2)
    return w,b


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--progress',action='store_true')
    args=parser.parse_args()
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    start=time.perf_counter()
    checks=[];ranks=[];panel_rows=[];kernel_rows=[];groups=[]
    group='setup';key=''
    env={'started_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,
         'numpy':np.__version__,'autograd':version('autograd'),'platform':platform.platform(),
         'threads':{n:os.environ.get(n) for n in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS']},
         'config_sha256':sha(ROOT/'config.json'),'design_sha256':sha(ROOT/'DESIGN_FROZEN.md'),
         'script_sha256':sha(Path(__file__)),'seed':None,'trained':False}
    (out/'environment.json').write_text(json.dumps(env,indent=2)+'\n')

    def table(name,rows):
        if rows:
            with (out/name).open('w') as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
                w.writeheader();w.writerows(rows)

    def compare(name,a,b,fd=False):
        a,b=np.asarray(a),np.asarray(b)
        error=float(np.max(np.abs(a-b)))
        scale=float(np.max(np.abs(b)))
        tol=(2e-5+2e-4*scale) if fd else (1e-10+1e-9*scale)
        checks.append({'group':group,'config':key,'check':name,'method':'FD' if fd else 'autodiff_identity',
                       'abs_error':error,'rel_error':error/scale if scale else '',
                       'tolerance':tol,'status':'PASS' if error<=tol and np.isfinite(error) else 'FAIL'})
        return error

    def predicate(name,status,value,threshold):
        checks.append({'group':group,'config':key,'check':name,'method':'diagnostic',
                       'abs_error':value,'rel_error':'','tolerance':threshold,'status':status})

    def complete():
        relevant=[r['status'] for r in checks if r['group']==group]
        status='FAIL' if 'FAIL' in relevant else ('INCONCLUSIVE' if 'INCONCLUSIVE' in relevant else 'PASS')
        elapsed=time.perf_counter()-start
        groups.append({'group':group,'status':status,'elapsed_seconds':elapsed})
        for name,rows in [('checks.csv',checks),('spectra.csv',ranks),('kernel.csv',kernel_rows)]:table(name,rows)
        (out/'timing.json').write_text(json.dumps(groups,indent=2)+'\n')
        if args.progress:
            with (ROOT/'progress.md').open('a') as f:
                f.write(f'\n- {out.name}: {group}, {status}; {elapsed:.3f} s acumulados. '
                        f'Tablas en `{out.relative_to(ROOT)}`.\n')
        print(group,status,flush=True)
        if elapsed>CONFIG['budget_seconds']:
            raise TimeoutError('Presupuesto congelado excedido; salidas parciales conservadas')

    xs=np.array(CONFIG['inputs'],dtype=float)
    ys=(xs.sum(axis=1)>0).astype(float)
    tmap=np.eye(9);tmap[0,1]=.5;tmap[2,2]=2
    j=np.array(CONFIG['perspective_chart'],dtype=float)
    group='01_datos'
    predicate('config_sin_entrenamiento','PASS' if not CONFIG['trained'] else 'FAIL',int(CONFIG['trained']),0)
    predicate('estados_3_paneles_3','PASS' if len(CONFIG['states'])==len(CONFIG['panels'])==3 else 'FAIL',len(CONFIG['states']),3)
    complete()
    observations=[]
    for state,tv in CONFIG['states'].items():
        theta=np.array(tv,dtype=float)
        for panel,indices in CONFIG['panels'].items():
            group=f'{state}_{panel}'
            inputs=xs[indices];labels=ys[indices]
            rr=np.asarray(jacobian(lambda th:logits(th,inputs,anp))(theta))
            logit=logits(theta,inputs,np)
            prob=1/(1+np.exp(-logit))
            fisher=rr.T@((prob*(1-prob))[:,None]*rr)/len(inputs)
            g=fisher+CONFIG['rho']*np.eye(9)
            c=np.linalg.solve(g,np.eye(9));l=np.linalg.cholesky(c)
            condition=float(np.linalg.cond(g))
            key=f'{state}/{panel}'
            compare('simetria_g',g,g.T)
            predicate('condicion_g','PASS' if condition<=1e5 else 'INCONCLUSIVE',condition,1e5)
            vals=np.linalg.eigvalsh(g)
            predicate('g_SPD','PASS' if vals[0]>0 else 'FAIL',float(vals[0]),0)
            coeff=np.asarray(basis(theta,inputs,labels,anp))
            jac_basis=np.asarray(jacobian(lambda th:basis(th,inputs,labels,anp))(theta))
            _,sing,vh=np.linalg.svd(rr,full_matrices=True)
            cutoff=1e-10*max(1.,float(sing[0]))
            ambiguous=bool(np.any((sing>=cutoff/10)&(sing<=cutoff*10)))
            rank_r=int(np.sum(sing>cutoff));kernel=vh[rank_r:].T
            kernel_rows.append({'state':state,'panel':panel,'singular_values_R':json.dumps(sing.tolist()),
                               'cutoff':cutoff,'rank_R':rank_r,'kernel_dimension':9-rank_r,
                               'ambiguous':ambiguous,'condition_g':condition,
                               'min_eigenvalue_g':float(vals[0]),'max_eigenvalue_g':float(vals[-1])})
            predicate('kernel_gap','INCONCLUSIVE' if ambiguous else 'PASS',min(abs(sing-cutoff)),cutoff)
            for index,pv in enumerate(CONFIG['perspectives']):
                p=np.array(pv,dtype=float)
                ss=components(theta,p,inputs,labels,np)
                wl=np.stack([p@jac_basis[:2],p@jac_basis[2:]])
                bl=np.stack([jac_basis[:2],jac_basis[2:]])
                dp=np.stack([coeff[:2],coeff[2:]])
                for kind in CONFIG['compositions']:
                    key=f'{state}/{panel}/p{index}/{kind}'
                    s=lambda th,pp:scalar(th,pp,inputs,labels,kind,anp)
                    sn=lambda th,pp:scalar(th,pp,inputs,labels,kind,np)
                    omega,b=direct(s,theta,p)
                    if kind=='sum':gl=np.ones(2);hes=np.zeros((2,2))
                    elif kind=='product':gl=ss[::-1];hes=np.array([[0.,1.],[1.,0.]])
                    else:gl=ss;hes=np.eye(2)
                    truncated=np.einsum('l,lai->ai',gl,bl)
                    extra=np.einsum('lr,ra,li->ai',hes,dp,wl)
                    compare('omega_cadena',omega,gl@wl)
                    compare('B_cadena_completa',b,truncated+extra)
                    h=b@c@b.T
                    compare('h_simetria',h,h.T)
                    compare('admisibilidad_omega',omega@kernel,np.zeros(kernel.shape[1]))
                    compare('admisibilidad_B',b@kernel,np.zeros((2,kernel.shape[1])))
                    fd_errors=[]
                    for step in CONFIG['fd_steps']:
                        wf,bf=finite(sn,theta,p,step)
                        compare(f'omega_FD_{step}',wf,omega,True)
                        fd_errors.append(compare(f'B_FD_{step}',bf,b,True))
                        compare(f'h_FD_{step}',bf@c@bf.T,h,True)
                    # Ambas cartas y restricción se derivan directamente del escalar compuesto.
                    q=np.linalg.solve(j,p)
                    _,bq=direct(lambda th,qq:s(th,anp.dot(j,qq)),theta,q)
                    compare('B_carta_p',bq,j.T@b)
                    compare('h_carta_p',bq@c@bq.T,j.T@h@j)
                    eta=np.linalg.solve(tmap,theta)
                    _,be=direct(lambda et,pp:s(anp.dot(tmap,et),pp),eta,p)
                    # Fisher calculada del Jacobiano de logits en la carta eta; H transportada.
                    re=np.asarray(jacobian(lambda et:logits(anp.dot(tmap,et),inputs,anp))(eta))
                    fe=re.T@((prob*(1-prob))[:,None]*re)/len(inputs)
                    ge=fe+CONFIG['rho']*(tmap.T@tmap)
                    ce=np.linalg.solve(ge,np.eye(9))
                    compare('g_carta_theta',ge,tmap.T@g@tmap)
                    compare('B_carta_theta',be,b@tmap)
                    compare('h_carta_theta',be@ce@be.T,h)
                    vector=np.array([1.,-2.])
                    compare('norma_carta_p',vector@(bq@c@bq.T)@vector,(j@vector)@h@(j@vector))
                    direction=np.array(CONFIG['restriction']['direction'],dtype=float)
                    u=np.array([CONFIG['restriction']['point']],dtype=float)
                    _,bu=direct(lambda th,uu:s(th,uu[0]*direction),theta,u)
                    _,atline=direct(s,theta,u[0]*direction)
                    compare('restriccion_h',bu@c@bu.T,(direction@atline@c@atline.T@direction).reshape(1,1))
                    # Registro de rango con corte prefijado y estabilidad FD independiente.
                    singular=np.linalg.svd(b@l,compute_uv=False)
                    tau=1e-8*max(1.,float(singular[0]))
                    uncertain=bool(np.any((singular>=tau/10)&(singular<=10*tau)))
                    rank=int(np.sum(singular>tau))
                    fd_stable=max(fd_errors)<=tau/10
                    status='INCONCLUSIVE' if uncertain or not fd_stable else 'PASS'
                    ranks.append({'state':state,'panel':panel,'point':index,'composition':kind,
                                  'rank_autodiff':rank,'singular_values_BL':json.dumps(singular.tolist()),
                                  'eigenvalues_h':json.dumps(np.linalg.eigvalsh(h).tolist()),'tau':tau,
                                  'ambiguous_spectrum':uncertain,'max_B_FD_error':max(fd_errors),
                                  'fd_stable':fd_stable,'rank_status':status,
                                  'norm_B_linear':float(np.linalg.norm(truncated)),
                                  'norm_B_mixed':float(np.linalg.norm(extra)),
                                  'truncated_B_error':float(np.max(np.abs(b-truncated)))})
                    observations.append(ranks[-1])
                    predicate('rango_estabilidad_FD',status,max(fd_errors),tau/10)
            key=f'{state}/{panel}/descenso'
            p=np.array([1.,1.])
            sag=lambda th,pp:(pp[0]+pp[1])*basis(th,inputs,labels,anp)[0]
            wa,ba=direct(sag,theta,p)
            gamma=jac_basis[0]@c@jac_basis[0]
            ha=ba@c@ba.T
            compare('descenso_h',ha,gamma*np.ones((2,2)))
            compare('descenso_vertical',ha@np.array([1.,-1.]),np.zeros(2))
            compare('descenso_representante',direct(sag,theta,np.array([2.,0.]))[1]@c@direct(sag,theta,np.array([2.,0.]))[1].T,ha)
            one=lambda th,pp:components(th,pp,inputs,labels,anp)[0]
            _,bone=direct(one,theta,p)
            vertical=float((bone@c@bone.T)[1,1])
            threshold=1e-10+1e-9*float(np.max(np.abs(bone@c@bone.T)))
            predicate('no_descenso_vertical','PASS' if vertical>threshold else 'INCONCLUSIVE',vertical,threshold)
            complete()
    group='11_paneles';key=''
    for state in CONFIG['states']:
        for point in range(3):
            for kind in CONFIG['compositions']:
                selected=[r for r in observations if r['state']==state and r['point']==point and r['composition']==kind]
                rr=[r['rank_autodiff'] for r in selected]
                reliable=all(r['rank_status']=='PASS' for r in selected)
                panel_rows.append({'state':state,'point':point,'composition':kind,
                                   'ranks_by_panel':json.dumps({r['panel']:r['rank_autodiff'] for r in selected}),
                                   'min_rank':min(rr),'max_rank':max(rr),
                                   'sensitivity':'SENSITIVE' if len(set(rr))>1 else 'STABLE',
                                   'fd_validation':'PASS' if reliable else 'INCONCLUSIVE'})
    table('panel_sensitivity.csv',panel_rows)
    predicate('configuraciones_81','PASS' if len(ranks)==81 else 'FAIL',len(ranks),81)
    complete()
    group='12_presupuesto'
    elapsed=time.perf_counter()-start
    predicate('tiempo','PASS' if elapsed<=120 else 'INCONCLUSIVE',elapsed,120)
    complete()
    identity=[r for r in checks if r['method']!='diagnostic']
    failed=[r for r in checks if r['status']=='FAIL']
    inc=[r for r in checks if r['status']=='INCONCLUSIVE']
    summary={'status':'FAIL' if failed else ('INCONCLUSIVE' if inc else 'PASS'),
             'identity_status':'PASS' if all(r['status']=='PASS' for r in identity) else 'FAIL',
             'checks':len(checks),'pass':sum(r['status']=='PASS' for r in checks),
             'fail':len(failed),'inconclusive':len(inc),'configurations':len(ranks),
             'rank_validated_FD':sum(r['rank_status']=='PASS' for r in ranks),
             'max_FD_absolute_error':max(r['abs_error'] for r in checks if r['method']=='FD'),
             'max_B_chain_error':max(r['abs_error'] for r in checks if r['check']=='B_cadena_completa'),
             'failures':failed,'training_steps':0}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (out/'resources.json').write_text(json.dumps({'elapsed_seconds':time.perf_counter()-start,
                                                'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    return 1 if failed else 0


if __name__=='__main__':
    raise SystemExit(main())
