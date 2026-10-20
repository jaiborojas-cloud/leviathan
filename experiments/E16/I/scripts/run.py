#!/usr/bin/env python3
"""E16-I: búsqueda en una familia de caminos; no minimización geodésica global."""
import argparse
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import resource
import sys
import time
import mpmath as mp
import numpy as np
import scipy
from scipy.optimize import minimize_scalar

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config.json').read_text())

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fmt(x):return mp.nstr(x,40)
def err(a,b):return abs(a-b)/max(1,abs(a),abs(b))
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
def table(p,rows):
    if not rows:return
    with p.open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def bend(a,b,s):
    v=b-a
    return (a+b)/2+s*mp.matrix([-v[1],v[0]])

def search(objective,case,resolution,trace):
    def evaluated(s):
        value=objective(float(s))
        trace.append({'case':case,'resolution':resolution,'evaluation':sum(r['case']==case and r['resolution']==resolution for r in trace),
                      's':repr(float(s)),'objective':repr(value) if math.isfinite(value) else '',
                      'finite':math.isfinite(value)})
        return value
    lo,hi=CFG['s_bounds'];base=evaluated(0);vlo=evaluated(lo);vhi=evaluated(hi)
    opt=minimize_scalar(evaluated,bounds=(lo,hi),method='bounded',options={'xatol':CFG['xatol'][resolution],'maxiter':CFG['maxiter']})
    vx=evaluated(opt.x)
    candidates=[(base,0.),(vlo,lo),(vhi,hi),(vx,float(opt.x))]
    value,s=min(candidates,key=lambda item:item[0])
    if not math.isfinite(value) or not (base-value>float(CFG['selection_absolute_scaled_margin'])*max(1,base)):
        value,s=base,0.
    return {'s':float(s),'objective':value,'success':bool(opt.success),'message':str(opt.message),'nfev':int(opt.nfev),'optimizer_s':float(opt.x)}

def fast_integral(u,du):
    c=float(u@u);b=2*float(u@du);a=float(du@du)
    if a==0 and b==0:return math.sqrt(c) if c>0 else math.inf
    if a<=0:return math.inf
    delta=c-b*b/(4*a)
    if delta<=0:return math.inf
    center=-b/(2*a);width=math.sqrt(delta/a);sa=math.sqrt(a)
    def primitive(x):return (x*math.sqrt(a*x*x+delta)+delta/sa*math.asinh(x/width))/2
    return primitive(1-center)-primitive(-center)

def main(out):
    started=time.monotonic();out.mkdir(parents=True,exist_ok=True)
    for path,key in [('H/data.json','H_data_sha256'),('D/scripts/run.py','D_method_sha256'),('G/scripts/run.py','G_method_sha256')]:
        assert sha(ROOT.parent/path)==CFG[key]
    data=json.loads((ROOT.parent/'H/data.json').read_text());d=load('method_d_i',ROOT.parent/'D/scripts/run.py');g=load('method_g_i',ROOT.parent/'G/scripts/run.py')
    assert d.CFG['rho']==data['rho']
    checks=[];trace=[];rows=[];segments=[];optimizers=[]
    dump(out/'summary.json',{'status':'INCOMPLETE'})
    def check(name,a,b,tol,category='identity'):
        error=err(a,b);ok=error<=mp.mpf(tol)
        checks.append({'name':name,'category':category,'error':fmt(error),'status':'PASS' if ok else ('FAIL' if category=='identity' else 'INCONCLUSIVE')})
    def coefficients(cv,jc,c,a,b,kind):
        v=b-a;b0=d.analytic_B(cv,jc,list(a),kind)[0];db=d.analytic_B(cv,jc,list(b),kind)[0]-b0
        h=[b0*c*b0.T,db*c*b0.T+b0*c*db.T,db*c*db.T]
        return h,[(v.T*hh*v)[0] for hh in h]
    def segment(cv,jc,c,a,b,kind,key,digits,rules,full=True):
        h,q=coefficients(cv,jc,c,a,b,kind);pa,pd=g.positive(h)
        try:
            length=g.primitive(q);geo=g.geometry(q)
            if full:
                qs=[g.quadrature(q,geo,rules[n]) for n in [16,32,64]]
                check(key+'/coarse',qs[0],qs[1],CFG['coarse_tolerance'],'integration')
                check(key+'/fine',qs[1],qs[2],CFG['fine_tolerance'],'integration')
                check(key+'/primitive',length,qs[2],CFG['fine_tolerance'],'integration')
                check(key+'/reparam',length,g.quadrature(q,geo,rules[64],True),CFG['fine_tolerance'],'integration')
                v=b-a
                for t in [mp.mpf(i)/4 for i in range(5)]:
                    bt=d.analytic_B(cv,jc,list(a+t*v),kind)[0];direct=bt*c*bt.T
                    for i in range(2):
                        for j in range(2):check(key+f'/tensor/{t}/{i}/{j}',direct[i,j],g.poly([hh[i,j] for hh in h],t),CFG['identity_tolerance'])
                for ji,j in enumerate(g.CFG['charts']):
                    j=mp.matrix(j);vq=j**-1*v
                    for k,hh in enumerate(h):check(key+f'/chart{ji}/{k}',q[k],(vq.T*(j.T*hh*j)*vq)[0],CFG['identity_tolerance'])
            reason='';admissible=True
        except ValueError as ex:
            length=None;reason=str(ex);admissible=False
        record={'segment':key,'digits':digits,'full_validation':full,'formula_admissible':admissible,'reason':reason,
                'length':fmt(length) if length is not None else '',
                'h00_positive':pa['ok'],'h00_margin':fmt(pa['margin']),'h00_depth':pa['depth'],
                'det_positive':pd['ok'],'det_margin':fmt(pd['margin']),'det_depth':pd['depth']}
        segments.append(record)
        return length,pa,pd

    for resolution in [0,1]:
        result=search(lambda s:2*math.sqrt(.25+s*s),'euclidean_control',resolution,trace)
        check(f'control/euclidean/search{resolution}',result['s'],0,CFG['nonworse_tolerance'])
        check(f'control/euclidean/success{resolution}',int(result['success']),1,CFG['nonworse_tolerance'])
    check('control/euclidean/straight',1,1,CFG['identity_tolerance'])
    with mp.workdps(120):
        for sign in [-1,1]:check(f'control/euclidean/bend{sign}',2*mp.sqrt(mp.mpf('.25')+mp.mpf('.25')**2),mp.sqrt(5)/2,CFG['identity_tolerance'])

    for state in CFG['states']:
        tv=data['states'][state];indices=data['panels'][CFG['panel']]
        with mp.workdps(120):
            theta=[mp.mpf(str(x)) for x in tv];inputs=[[mp.mpf(str(x)) for x in data['inputs'][i]] for i in indices]
            cv,jc,c,l=d.analytic_mp(theta,inputs)
            cfloat=np.array(c.tolist(),float);lfloat=np.array(l.tolist(),float)
            for path,(ia,ib) in enumerate(CFG['paths']):
                a=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ia]]);b=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ib]])
                af=np.array(list(a),float);bf=np.array(list(b),float);vf=bf-af;normal=np.array([-vf[1],vf[0]])
                for kind in CFG['compositions']:
                    case=f'{state}/{path}/{kind}';begin=len(checks);segment_begin=len(segments)
                    bx=np.array(d.analytic_B(cv,jc,[1,0],kind)[0].tolist(),float)@lfloat
                    by=np.array(d.analytic_B(cv,jc,[0,1],kind)[0].tolist(),float)@lfloat
                    def ub(p):return bx if kind=='sum' else p[0]*bx+p[1]*by
                    def edge(x,y):
                        vv=y-x;u=vv@ub(x);du=vv@(ub(y)-ub(x))
                        return fast_integral(u,du)
                    def objective(s):
                        middle=(af+bf)/2+s*normal
                        return edge(af,middle)+edge(middle,bf)
                    found=[search(objective,case,resolution,trace) for resolution in [0,1]]
                    for resolution,z in enumerate(found):optimizers.append({'case':case,'resolution':resolution,**z})
                    s=mp.mpf(repr(found[0]['s']));sfine=mp.mpf(repr(found[1]['s']))
                    for digits in CFG['precision']:
                        with mp.workdps(digits):
                            th=[mp.mpf(str(x)) for x in tv];zz=[[mp.mpf(str(x)) for x in data['inputs'][i]] for i in indices]
                            cvp,jcp,cp,_=d.analytic_mp(th,zz)
                            aa=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ia]]);bb=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ib]])
                            middle=bend(aa,bb,s);rules={n:mp.gauss_quadrature(n,'legendre') for n in [16,32,64]}
                            values=[]
                            for label,x,y in [('straight',aa,bb),('left',aa,middle),('right',middle,bb)]:
                                value,pa,pd=segment(cvp,jcp,cp,x,y,kind,case+'/'+label,digits,rules)
                                values.append(value)
                            if digits==80:
                                low=values
                            else:
                                for k,(lo,hi) in enumerate(zip(low,values)):
                                    if lo is not None and hi is not None:check(case+f'/precision/{k}',lo,hi,CFG['precision_tolerance'],'precision')
                                if all(x is not None for x in values):
                                    straight=values[0];candidate=values[1]+values[2]
                                    zero=bend(aa,bb,mp.mpf(0));q1=coefficients(cvp,jcp,cp,aa,zero,kind)[1];q2=coefficients(cvp,jcp,cp,zero,bb,kind)[1]
                                    check(case+'/zero_split',straight,g.primitive(q1)+g.primitive(q2),CFG['identity_tolerance'])
                                    fine_mid=bend(aa,bb,sfine)
                                    fine_values=[segment(cvp,jcp,cp,x,y,kind,case+'/'+label,120,rules,False)[0] for label,x,y in [('fine_left',aa,fine_mid),('fine_right',fine_mid,bb)]]
                                    stable=all(x is not None for x in fine_values)
                                    if stable:check(case+'/stability',candidate,sum(fine_values),CFG['stability_tolerance'],'stability')
                                    check(case+'/nonworse',max(mp.mpf(0),candidate-straight)/max(1,straight),0,CFG['nonworse_tolerance'])
                                    if kind=='sum':
                                        check(case+'/sum_s',s,0,CFG['nonworse_tolerance'])
                                        check(case+'/sum_length',candidate,straight,CFG['nonworse_tolerance'])
                                    gain=(straight-candidate)/straight
                                else:
                                    straight=candidate=gain=None;stable=False
                    local=checks[begin:];sr=segments[segment_begin:]
                    status='FAIL' if any(x['status']=='FAIL' for x in local) else ('INCONCLUSIVE' if not stable or not all(z['success'] for z in found) or any(not x['formula_admissible'] or not x['h00_positive'] or not x['det_positive'] for x in sr) or any(x['status']=='INCONCLUSIVE' for x in local) else 'PASS_NUMERICAL')
                    rows.append({'case':case,'state':state,'path':path,'composition':kind,'status':status,'s':repr(found[0]['s']),'s_fine':repr(found[1]['s']),
                        'straight_length':fmt(straight) if straight is not None else '',
                        'candidate_length':fmt(candidate) if candidate is not None else '',
                        'relative_gain':fmt(gain) if gain is not None else '',
                        'improved':status=='PASS_NUMERICAL' and gain is not None and gain>mp.mpf(CFG['improvement_relative_threshold']),
                        'boundary_active':min(abs(s-mp.mpf(str(z))) for z in CFG['s_bounds'])<=mp.mpf(CFG['boundary_tolerance'])})
                    table(out/'cases.csv',rows);table(out/'segments.csv',segments);table(out/'checks.csv',checks);table(out/'search_trace.csv',trace)
                    if time.monotonic()-started>CFG['budget_seconds']:raise TimeoutError('time budget; partial tables preserved')
    counts={s:sum(r['status']==s for r in rows) for s in ['PASS_NUMERICAL','FAIL','INCONCLUSIVE']}
    cc={s:sum(r['status']==s for r in checks) for s in ['PASS','FAIL','INCONCLUSIVE']}
    elapsed=time.monotonic()-started;rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024;budget=elapsed<=CFG['budget_seconds'] and rss<=CFG['memory_target_mib']
    status='FAIL' if counts['FAIL'] or cc['FAIL'] else ('INCONCLUSIVE' if counts['INCONCLUSIVE'] or cc['INCONCLUSIVE'] or not budget else 'PASS_NUMERICAL')
    desc={}
    for kind in CFG['compositions']:
        rr=[r for r in rows if r['composition']==kind]
        desc[kind]={'total':len(rr),'validated':sum(r['status']=='PASS_NUMERICAL' for r in rr),'improved':sum(r['improved'] for r in rr),'boundary_active':sum(r['boundary_active'] for r in rr),
                    'min_gain':min(float(r['relative_gain']) for r in rr if r['relative_gain']),
                    'max_gain':max(float(r['relative_gain']) for r in rr if r['relative_gain'])}
    table(out/'optimizers.csv',optimizers)
    dump(out/'summary.json',{'status':status,'cases':len(rows),'counts':counts,'checks':len(checks),'check_counts':cc,'descriptive':desc})
    dump(out/'provenance.json',{'H_data_sha256':sha(ROOT.parent/'H/data.json'),'D_method_sha256':sha(ROOT.parent/'D/scripts/run.py'),'G_method_sha256':sha(ROOT.parent/'G/scripts/run.py'),
        'I_config_sha256':sha(ROOT/'config.json'),'I_script_sha256':sha(Path(__file__)),'design_commit':'acab94e','python':sys.version.split()[0],'numpy':np.__version__,'scipy':scipy.__version__,'mpmath':mp.__version__})
    dump(out/'resources.json',{'seconds':elapsed,'max_rss_mib':rss,'within_budget':budget})
    print(json.dumps({'status':status,'counts':counts,'checks':cc,'descriptive':desc,'seconds':elapsed}))
    return int(status=='FAIL' or not budget)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    raise SystemExit(main(p.parse_args().out))
