#!/usr/bin/env python3
"""E16-J: refinamiento finito y estacionariedad discreta, sin certificado geodésico."""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time
import autograd.numpy as anp
from autograd import grad
import mpmath as mp
import numpy as np
import scipy
from scipy.optimize import minimize

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config.json').read_text())

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fmt(x):return mp.nstr(x,40)
def error(a,b):return abs(a-b)/max(1,abs(a),abs(b))
def dump(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
def table(p,rows):
    if not rows:return
    with p.open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def objective(a,b,n,kind,ux,uy,order):
    nodes,weights=np.polynomial.legendre.leggauss(order);tt=(nodes+1)/2;ww=weights/2
    times=np.linspace(0,1,n+2);v=b-a;normal=np.array([-v[1],v[0]])
    base=a+times[:,None]*v
    def length(s):
        ss=anp.concatenate([anp.zeros(1),s,anp.zeros(1)])
        p=base+ss[:,None]*normal;dv=p[1:]-p[:-1]
        if kind=='sum':
            u=anp.dot(dv,ux)
            return anp.sum(anp.sqrt(anp.sum(u*u,axis=1)))
        up=p[:,0,None,None]*ux+p[:,1,None,None]*uy
        u0=anp.einsum('ej,ejk->ek',dv,up[:-1]);u1=anp.einsum('ej,ejk->ek',dv,up[1:])
        u=u0[:,None,:]+tt[None,:,None]*(u1-u0)[:,None,:]
        speeds=anp.sqrt(anp.sum(u*u,axis=2))
        return anp.sum(speeds*ww[None,:])
    return length

def points_mp(a,b,s):
    v=b-a;normal=mp.matrix([-v[1],v[0]]);n=len(s)
    return [a]+[a+mp.mpf(k+1)/(n+1)*v+mp.mpf(repr(float(z)))*normal for k,z in enumerate(s)]+[b]

def main(out):
    start=time.monotonic();out.mkdir(parents=True,exist_ok=True)
    for p,k in [('H/data.json','H_data_sha256'),('D/scripts/run.py','D_method_sha256'),('G/scripts/run.py','G_method_sha256'),('I/results/run_v1/cases.csv','I_cases_sha256')]:assert sha(ROOT.parent/p)==CFG[k]
    data=json.loads((ROOT.parent/'H/data.json').read_text());d=load('d_j',ROOT.parent/'D/scripts/run.py');g=load('g_j',ROOT.parent/'G/scripts/run.py')
    assert data['rho']==d.CFG['rho']
    old={r['case']:r for r in csv.DictReader((ROOT.parent/'I/results/run_v1/cases.csv').open())}
    checks=[];segments=[];searches=[];vertices=[];resolutions=[];cases=[]
    dump(out/'summary.json',{'status':'INCOMPLETE'})
    def check(name,a,b,tol,category='identity'):
        e=error(a,b);ok=bool(mp.isfinite(e) and e<=mp.mpf(tol))
        checks.append({'name':name,'category':category,'error':fmt(e),'status':'PASS' if ok else ('FAIL' if category=='identity' else 'INCONCLUSIVE')})
    def checkpoint():
        for name,rr in [('checks',checks),('segments',segments),('searches',searches),('vertices',vertices),('resolutions',resolutions),('cases',cases)]:table(out/(name+'.csv'),rr)
        if time.monotonic()-start>CFG['budget_seconds']:
            dump(out/'summary.json',{'status':'INCONCLUSIVE','reason':'time_budget','completed_cases':len(cases)})
            raise TimeoutError('time budget; partial evidence preserved')
    def optimize_all(a,b,n,kind,ux,uy,key):
        f=objective(a,b,n,kind,ux,uy,32);df=grad(f);f64=objective(a,b,n,kind,ux,uy,64)
        zero=np.zeros(n);base=float(f(zero));runs=[]
        for which,amplitude in enumerate(CFG['initial_amplitudes']):
            initial=amplitude*np.sin(np.pi*np.arange(1,n+1)/(n+1))
            opt=minimize(f,initial,jac=df,bounds=[tuple(CFG['s_bounds'])]*n,method='L-BFGS-B',options=CFG['optimizer']|{})
            s=np.asarray(opt.x,dtype=float);val=float(f(s));val64=float(f64(s))
            searches.append({'case':key,'nodes':n,'start':which,'amplitude':amplitude,'success':bool(opt.success),'message':str(opt.message),'iterations':int(opt.nit),'nfev':int(opt.nfev),'L32':repr(val),'L64':repr(val64)})
            for j,z in enumerate(s):vertices.append({'case':key,'nodes':n,'source':'start'+str(which),'index':j,'t':repr((j+1)/(n+1)),'s':repr(float(z))})
            runs.append((val,s,bool(opt.success),val64))
        best=min(runs+[(base,zero,True,float(f64(zero)))],key=lambda r:r[0] if np.isfinite(r[0]) else np.inf)
        if not np.isfinite(best[0]) or base-best[0]<=float(CFG['selection_margin'])*max(1,base):best=(base,zero,True,float(f64(zero)))
        return best[1],f,f64,runs
    # Independent flat controls, all prescribed starts and resolutions.
    ux=np.zeros((2,9));ux[:,:2]=np.eye(2)
    for n in CFG['interior_nodes']:
        s,f,f64,runs=optimize_all(np.array([0.,0.]),np.array([1.,0.]),n,'sum',ux,ux,'euclidean_control')
        for k,(val,z,ok,v64) in enumerate(runs):
            check(f'control/{n}/{k}/success',int(ok),1,'1e-10')
            check(f'control/{n}/{k}/length',v64,1,'1e-10')
            check(f'control/{n}/{k}/nodes',float(np.max(np.abs(z))),0,'1e-5')
    # Method remains G; only matrices and finite paths are supplied here.
    rules={}
    for digits in CFG['precision']:
        with mp.workdps(digits):rules[digits]={n:mp.gauss_quadrature(n,'legendre') for n in [16,32,64]}
    def validate_path(key,n,s,ia,ib,kind,prepared,full):
        snapshots={};valid=True;total=None
        for digits in CFG['precision']:
            with mp.workdps(digits):
                cv,jc,c,_=prepared[digits]
                a=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ia]]);b=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ib]])
                pts=points_mp(a,b,s);values=[]
                for k,(x,y) in enumerate(zip(pts,pts[1:])):
                    v=y-x;b0=d.analytic_B(cv,jc,list(x),kind)[0];db=d.analytic_B(cv,jc,list(y),kind)[0]-b0
                    h=[b0*c*b0.T,db*c*b0.T+b0*c*db.T,db*c*db.T];q=[(v.T*hh*v)[0] for hh in h]
                    pa,pd=g.positive(h);label=f'{key}/{n}/{digits}/{k}';reason=''
                    try:
                        length=g.primitive(q)
                        if full:
                            geo=g.geometry(q);qq=[g.quadrature(q,geo,rules[digits][order]) for order in [16,32,64]]
                            check(label+'/coarse',qq[0],qq[1],CFG['coarse_tolerance'],'integration')
                            check(label+'/fine',qq[1],qq[2],CFG['fine_tolerance'],'integration')
                            check(label+'/primitive',length,qq[2],CFG['fine_tolerance'],'integration')
                            check(label+'/reparam',length,g.quadrature(q,geo,rules[digits][64],True),CFG['fine_tolerance'],'integration')
                    except ValueError as ex:length=None;reason=str(ex)
                    ok=length is not None and pa['ok'] and pd['ok'];valid=valid and ok
                    segments.append({'case':key,'nodes':n,'digits':digits,'segment':k,'length':fmt(length) if length is not None else '',
                        'admissible':length is not None,'reason':reason,'h00_positive':pa['ok'],'det_positive':pd['ok'],
                        'h00_margin':fmt(pa['margin']),'det_margin':fmt(pd['margin']),'h00_depth':pa['depth'],'det_depth':pd['depth']})
                    if digits==80:snapshots[k]=(length,pa['margin'],pd['margin'])
                    else:
                        lo=snapshots[k]
                        if length is not None and lo[0] is not None:check(label+'/precision/length',lo[0],length,CFG['precision_tolerance'],'precision')
                        check(label+'/precision/h00',lo[1],pa['margin'],CFG['precision_tolerance'],'precision')
                        check(label+'/precision/det',lo[2],pd['margin'],CFG['precision_tolerance'],'precision')
                    values.append(length)
                total=sum(values) if all(z is not None for z in values) else None
        return total,valid
    for state in CFG['states']:
        prepared={}
        for digits in CFG['precision']:
            with mp.workdps(digits):
                theta=[mp.mpf(str(x)) for x in data['states'][state]]
                inputs=[[mp.mpf(str(x)) for x in data['inputs'][i]] for i in data['panels'][CFG['panel']]]
                prepared[digits]=d.analytic_mp(theta,inputs)
        for path,(ia,ib) in enumerate(CFG['paths']):
            af=np.array(data['perspectives'][ia],float);bf=np.array(data['perspectives'][ib],float)
            for kind in CFG['compositions']:
                key=f'{state}/{path}/{kind}';case_begin=len(checks);case_res=[]
                baseline,basevalid=validate_path(key,0,[],ia,ib,kind,prepared,False)
                with mp.workdps(120):
                    cv,jc,c,l=prepared[120];lf=np.array(l.tolist(),float)
                    ux=np.array(d.analytic_B(cv,jc,[1,0],kind)[0].tolist(),float)@lf
                    uy=np.array(d.analytic_B(cv,jc,[0,1],kind)[0].tolist(),float)@lf
                for n in CFG['interior_nodes']:
                    begin=len(checks);s,f,f64,runs=optimize_all(af,bf,n,kind,ux,uy,key)
                    check(f'{key}/{n}/bounds',float(max(0,np.max(np.abs(s))-.25)),0,CFG['identity_tolerance'])
                    # Endpoints fixed by construction; record selected parameters separately.
                    for j,z in enumerate(s):vertices.append({'case':key,'nodes':n,'source':'selected','index':j,'t':repr((j+1)/(n+1)),'s':repr(float(z))})
                    lval,valid=validate_path(key,n,s,ia,ib,kind,prepared,True)
                    gradient32=np.asarray(grad(f)(s),float);gradient64=np.asarray(grad(f64)(s),float)
                    scale=max(1,float(lval)) if lval is not None else max(1,float(f64(s)))
                    agreement=float(np.max(np.abs(gradient32-gradient64)))/scale
                    check(f'{key}/{n}/gradient_orders',agreement,0,CFG['gradient_agreement_tolerance'],'stationarity')
                    for step in CFG['fd_steps']:
                        fd=[]
                        for j in range(n):
                            unit=np.zeros(n);unit[j]=step
                            fd.append((float(f64(s+unit))-float(f64(s-unit)))/(2*step))
                        check(f'{key}/{n}/gradient_fd/{step}',float(np.max(np.abs(np.asarray(fd)-gradient64)))/scale,0,CFG['fd_tolerance'],'stationarity')
                    residual=float(np.max(np.abs(s-np.clip(s-gradient64,-.25,.25))))/scale
                    free=float(np.max(np.abs(gradient64)))/scale
                    check(f'{key}/{n}/kkt',residual,0,CFG['gradient_tolerance'],'stationarity')
                    start_values=[r[3] for r in runs];spread=(max(start_values)-min(start_values))/scale
                    check(f'{key}/{n}/starts',spread,0,CFG['start_stability_tolerance'],'stability')
                    with mp.workdps(120):
                        if lval is not None and baseline is not None:
                            check(f'{key}/{n}/objective',lval,mp.mpf(float(f(s))),CFG['objective_tolerance'],'integration')
                            check(f'{key}/{n}/nonworse',max(mp.mpf(0),lval-baseline)/max(1,baseline),0,CFG['nonworse_tolerance'])
                            gain=(baseline-lval)/baseline
                            if kind=='sum':
                                check(f'{key}/{n}/sum_params',float(np.max(np.abs(s))),0,CFG['nonworse_tolerance'])
                                check(f'{key}/{n}/sum_length',lval,baseline,CFG['nonworse_tolerance'])
                        else:gain=None
                    active=int(np.sum(np.minimum(abs(s+.25),abs(s-.25))<=float(CFG['boundary_tolerance'])))
                    local=checks[begin:]
                    status='FAIL' if any(r['status']=='FAIL' for r in local) else ('INCONCLUSIVE' if not basevalid or not valid or not all(r[2] for r in runs) or any(r['status']=='INCONCLUSIVE' for r in local) else 'PASS_NUMERICAL')
                    row={'case':key,'state':state,'path':path,'composition':kind,'nodes':n,'status':status,
                        'length':fmt(lval) if lval is not None else '','straight_length':fmt(baseline) if baseline is not None else '',
                        'relative_gain':fmt(gain) if gain is not None else '','optimizer_successes':sum(r[2] for r in runs),
                        'active_nodes':active,'kkt_residual':repr(residual),'free_gradient':repr(free),'gradient_order_difference':repr(agreement),'start_spread':repr(spread)}
                    resolutions.append(row);case_res.append((row,lval));checkpoint()
                refine=[]
                with mp.workdps(120):
                    for j,tol in enumerate([CFG['refinement_2_4_tolerance'],CFG['refinement_4_8_tolerance']]):
                        a,b=case_res[j][1],case_res[j+1][1]
                        e=error(a,b) if a is not None and b is not None else mp.inf
                        check(key+f'/refinement/{j}',e,0,tol,'refinement');refine.append(e)
                # Check above compares a dimensionless error to zero; infinity remains inconclusive.
                local=checks[case_begin:];rr=[r[0] for r in case_res];last=rr[-1]
                status='FAIL' if any(r['status']=='FAIL' for r in local) or any(r['status']=='FAIL' for r in rr) else ('INCONCLUSIVE' if any(r['status']=='INCONCLUSIVE' for r in local) or any(r['status']=='INCONCLUSIVE' for r in rr) else 'PASS_NUMERICAL')
                geometry='BOUNDARY_LIMITED' if last['active_nodes'] else ('INTERIOR_STABLE_DISCRETE' if status=='PASS_NUMERICAL' and float(last['free_gradient'])<=float(CFG['gradient_tolerance']) else 'UNRESOLVED')
                with mp.workdps(120):
                    il=mp.mpf(old[key]['candidate_length']);new=case_res[-1][1]
                    difference=(il-new)/il if new is not None else None
                cases.append({'case':key,'composition':kind,'status':status,'geometry':geometry,'error_2_4':fmt(refine[0]),'error_4_8':fmt(refine[1]),
                    'I_length':old[key]['candidate_length'],'J8_length':last['length'],'relative_change_from_I':fmt(difference) if difference is not None else ''})
                checkpoint()
    cc={s:sum(r['status']==s for r in checks) for s in ['PASS','FAIL','INCONCLUSIVE']}
    counts={s:sum(r['status']==s for r in cases) for s in ['PASS_NUMERICAL','FAIL','INCONCLUSIVE']}
    elapsed=time.monotonic()-start;rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024;budget=elapsed<=CFG['budget_seconds'] and rss<=CFG['memory_target_mib']
    status='FAIL' if cc['FAIL'] or counts['FAIL'] else ('INCONCLUSIVE' if cc['INCONCLUSIVE'] or counts['INCONCLUSIVE'] or not budget else 'PASS_NUMERICAL')
    desc={}
    for n in CFG['interior_nodes']:
        rr=[r for r in resolutions if r['nodes']==n]
        desc[str(n)]={'total':len(rr),'counts':{s:sum(r['status']==s for r in rr) for s in ['PASS_NUMERICAL','FAIL','INCONCLUSIVE']},'boundary_cases':sum(r['active_nodes']>0 for r in rr)}
    summary={'status':status,'cases':len(cases),'counts':counts,'resolutions':len(resolutions),'by_resolution':desc,'checks':len(checks),'check_counts':cc,
        'geometry_counts':{s:sum(r['geometry']==s for r in cases) for s in ['BOUNDARY_LIMITED','INTERIOR_STABLE_DISCRETE','UNRESOLVED']}}
    dump(out/'summary.json',summary)
    dump(out/'provenance.json',{'config_sha256':sha(ROOT/'config.json'),'script_sha256':sha(Path(__file__)),'design_commit':'c2cd4a8',
        'sources':{p:sha(ROOT.parent/p) for p in ['H/data.json','D/scripts/run.py','G/scripts/run.py','I/results/run_v1/cases.csv']},
        'python':sys.version.split()[0],'numpy':np.__version__,'scipy':scipy.__version__,'mpmath':mp.__version__})
    dump(out/'resources.json',{'seconds':elapsed,'max_rss_mib':rss,'within_budget':budget})
    print(json.dumps(summary|{'seconds':elapsed,'budget':budget}))
    return int(status=='FAIL' or not budget)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    raise SystemExit(main(parser.parse_args().out))
