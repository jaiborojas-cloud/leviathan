#!/usr/bin/env python3
"""E16-L: acuerdo finito de longitud y forma, conservando el resultado K."""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time
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
def err(a,b):return abs(a-b)/max(1,abs(a),abs(b))
def dump(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
def table(p,rows):
    if not rows:return
    with p.open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def main(out):
    start=time.monotonic();out.mkdir(parents=True,exist_ok=True)
    for p,value in CFG['sources'].items():assert sha(ROOT.parent/p)==value,p
    data=json.loads((ROOT.parent/'H/data.json').read_text());d=load('d_l',ROOT.parent/'D/scripts/run.py');g=load('g_l',ROOT.parent/'G/scripts/run.py');k=load('k_l',ROOT.parent/'K/scripts/run.py')
    legacy={r['case']:r for r in csv.DictReader((ROOT.parent/'K/results/run_v1/cases.csv').open())}
    legacy_vertices=list(csv.DictReader((ROOT.parent/'K/results/run_v1/vertices.csv').open()))
    checks=[];searches=[];vertices=[];gradients=[];segments=[];resolutions=[];shapes=[];cases=[]
    dump(out/'summary.json',{'status':'INCOMPLETE'})
    def check(name,e,tol,category='identity'):
        ok=bool(mp.isfinite(e) and abs(e)<=mp.mpf(tol))
        checks.append({'name':name,'category':category,'error':fmt(e),'status':'PASS' if ok else ('FAIL' if category=='identity' else 'INCONCLUSIVE')})
    def checkpoint():
        for name,rr in [('checks',checks),('searches',searches),('vertices',vertices),('gradients',gradients),('segments',segments),('resolutions',resolutions),('shapes',shapes),('cases',cases)]:table(out/(name+'.csv'),rr)
        if time.monotonic()-start>CFG['budget_seconds']:
            dump(out/'summary.json',{'status':'INCONCLUSIVE','reason':'time_budget','completed_cases':len(cases)})
            raise TimeoutError('time budget; partial tables preserved')
    prepared={};rules={}
    for digits in CFG['precision']:
        with mp.workdps(digits):
            theta=[mp.mpf(str(x)) for x in data['states']['h00']]
            inputs=[[mp.mpf(str(x)) for x in data['inputs'][i]] for i in data['panels'][CFG['panel']]]
            cv,jc,c,l=d.analytic_mp(theta,inputs);prepared[digits]=(cv,jc,l)
            rules[digits]={n:mp.gauss_quadrature(n,'legendre') for n in [16,32,64]}
    def spd(a,b,s,kind,ux,uy):
        ok=True;minimum=mp.inf
        for u0,du,u,dd in k.mp_edges(a,b,s,kind,ux,uy):
            h=[u0*u0.T,du*u0.T+u0*du.T,du*du.T];pa,pd=g.positive(h)
            ok=ok and pa['ok'] and pd['ok'];minimum=min(minimum,pa['margin'],pd['margin'])
        return ok,minimum
    def diagnose(case,m,label,s,success,f,df,a,b,kind,ux,uy):
        begin=len(checks)
        with mp.workdps(80):
            smp=[mp.mpf(repr(float(z))) for z in s];value=None
            try:
                value=k.reference_length(a,b,smp,kind,ux,uy);scale=max(1,abs(value));ok_spd,margin=spd(a,b,smp,kind,ux,uy)
                pts=k.points(a,b,smp);normal=mp.matrix([-(b-a)[1],(b-a)[0]]);fd1=[];fd2=[]
                for j in range(len(smp)):
                    pair=[]
                    for step in CFG['mp_fd_steps']:
                        step=mp.mpf(step);left=pts[j+1]-step*normal;right=pts[j+1]+step*normal
                        plus=k.reference_length(pts[j],right,[],kind,ux,uy)+k.reference_length(right,pts[j+2],[],kind,ux,uy)
                        minus=k.reference_length(pts[j],left,[],kind,ux,uy)+k.reference_length(left,pts[j+2],[],kind,ux,uy)
                        pair.append((plus-minus)/(2*step))
                    fd1.append(pair[0]);fd2.append(pair[1])
                gad=np.asarray(df(s),float)
                ad_error=max(abs(mp.mpf(float(z))-r) for z,r in zip(gad,fd2))/scale
                fd_error=max(abs(z-r) for z,r in zip(fd1,fd2))/scale
                check(f'{case}/{m}/{label}/gradient_ad',ad_error,CFG['gradient_agreement_tolerance'],'gradient')
                check(f'{case}/{m}/{label}/gradient_steps',fd_error,CFG['mp_fd_agreement_tolerance'],'gradient')
                check(f'{case}/{m}/{label}/objective',err(value,mp.mpf(float(f(s)))),CFG['objective_tolerance'],'integration')
                gm=np.array([float(z) for z in fd2]);residual=float(np.max(np.abs(s-np.clip(s-gm,-.25,.25))))/float(scale);free=float(np.max(np.abs(gm)))/float(scale)
                check(f'{case}/{m}/{label}/kkt',residual,CFG['gradient_tolerance'],'stationarity')
                for j,(z,x,y) in enumerate(zip(gad,fd1,fd2)):gradients.append({'case':case,'segments':m,'source':label,'index':j,'autograd':repr(float(z)),'mp_fd_1':fmt(x),'mp_fd_2':fmt(y)})
                valid=bool(success and ok_spd and all(z['status']=='PASS' for z in checks[begin:]))
            except (ValueError,ZeroDivisionError):
                valid=False;ok_spd=False;margin=mp.nan;residual=free=float('inf');ad_error=fd_error=mp.inf;fd1=fd2=[]
            return {'value':value,'valid':valid,'spd':ok_spd,'margin':margin,'kkt':residual,'free':free,'ad_error':ad_error,'fd_error':fd_error,
                    'active':int(np.sum(np.minimum(abs(s+.25),abs(s-.25))<=float(CFG['boundary_tolerance']))),'fd1':fd1,'fd2':fd2}
    def validate(case,m,s,ia,ib,kind):
        low={};valid=True;totals={}
        for digits in CFG['precision']:
            with mp.workdps(digits):
                cv,jc,l=prepared[digits];ux=d.analytic_B(cv,jc,[1,0],kind)[0]*l;uy=d.analytic_B(cv,jc,[0,1],kind)[0]*l
                a=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ia]]);b=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ib]])
                smp=[mp.mpf(repr(float(z))) for z in s];total=mp.mpf(0)
                for index,(u0,du,u,dd) in enumerate(k.mp_edges(a,b,smp,kind,ux,uy)):
                    h=[u0*u0.T,du*u0.T+u0*du.T,du*du.T];pa,pd=g.positive(h)
                    q=[mp.fsum(z*z for z in u),2*mp.fsum(x*y for x,y in zip(u,dd)),mp.fsum(z*z for z in dd)]
                    name=f'{case}/{m}/{digits}/{index}';reason=''
                    try:
                        value=g.primitive(q);geo=g.geometry(q);qq=[g.quadrature(q,geo,rules[digits][n]) for n in [16,32,64]]
                        check(name+'/coarse',err(qq[0],qq[1]),CFG['coarse_tolerance'],'integration')
                        check(name+'/fine',err(qq[1],qq[2]),CFG['fine_tolerance'],'integration')
                        check(name+'/primitive',err(value,qq[2]),CFG['fine_tolerance'],'integration')
                        check(name+'/reparam',err(value,g.quadrature(q,geo,rules[digits][64],True)),CFG['fine_tolerance'],'integration');total+=value
                    except (ValueError,ZeroDivisionError) as ex:value=None;valid=False;reason=str(ex)
                    valid=valid and pa['ok'] and pd['ok']
                    segments.append({'case':case,'mesh_segments':m,'digits':digits,'index':index,'length':fmt(value) if value is not None else '',
                        'reason':reason,'h00_positive':pa['ok'],'det_positive':pd['ok'],'h00_margin':fmt(pa['margin']),'det_margin':fmt(pd['margin']),'h00_depth':pa['depth'],'det_depth':pd['depth']})
                    if digits==80:low[index]=(value,pa['margin'],pd['margin'])
                    else:
                        previous=low[index]
                        if value is not None and previous[0] is not None:check(name+'/precision_length',err(value,previous[0]),CFG['precision_tolerance'],'precision')
                        check(name+'/precision_h00',err(pa['margin'],previous[1]),CFG['precision_tolerance'],'precision')
                        check(name+'/precision_det',err(pd['margin'],previous[2]),CFG['precision_tolerance'],'precision')
                totals[digits]=total
                check(f'{case}/{m}/{digits}/reference',err(total,k.reference_length(a,b,smp,kind,ux,uy)),CFG['precision_tolerance'],'precision')
        return totals[120],valid
    for case in CFG['cases']:
        state,path,kind=case.split('/');ia,ib=CFG['paths'][int(path)];case_begin=len(checks);chosen=[]
        with mp.workdps(120):
            cv,jc,l=prepared[120];uxf=np.array((d.analytic_B(cv,jc,[1,0],kind)[0]*l).tolist(),float);uyf=np.array((d.analytic_B(cv,jc,[0,1],kind)[0]*l).tolist(),float)
        with mp.workdps(80):
            cv,jc,l=prepared[80];ux=d.analytic_B(cv,jc,[1,0],kind)[0]*l;uy=d.analytic_B(cv,jc,[0,1],kind)[0]*l
            a=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ia]]);b=mp.matrix([mp.mpf(str(x)) for x in data['perspectives'][ib]])
        af=np.array(data['perspectives'][ia],float);bf=np.array(data['perspectives'][ib],float)
        legacy_rows=sorted([r for r in legacy_vertices if r['case']==case and r['segments']=='16' and r['source']=='selected'],key=lambda r:int(r['index']))
        previous=np.array([float(r['s']) for r in legacy_rows]);assert len(previous)==15
        with mp.workdps(80):previous_value=k.reference_length(a,b,[mp.mpf(repr(float(z))) for z in previous],kind,ux,uy)
        baseline,basevalid=validate(case,1,[],ia,ib,kind)
        for m in CFG['segments']:
            begin=len(checks);t=np.arange(1,m)/m;oldtimes=np.linspace(0,1,len(previous)+2);incumbent=np.interp(t,oldtimes,np.r_[0,previous,0])
            with mp.workdps(80):
                inherited=k.reference_length(a,b,[mp.mpf(repr(float(z))) for z in incumbent],kind,ux,uy)
                check(f'{case}/{m}/embedding',err(inherited,previous_value),CFG['embedding_tolerance'])
            f=k.make_objective(af,bf,m,kind,uxf,uyf);df=grad(f);starts=[amplitude*np.sin(harmonic*np.pi*t) for amplitude,harmonic in CFG['starts']]+[incumbent.copy()]
            runs=[];options={key:v for key,v in CFG['optimizer'].items() if key!='method'}
            for index,initial in enumerate(starts):
                opt=minimize(f,initial,jac=df,bounds=[tuple(CFG['s_bounds'])]*(m-1),method=CFG['optimizer']['method'],options=options)
                s=np.asarray(opt.x,float);value=float(f(s));di=diagnose(case,m,'start'+str(index),s,bool(opt.success),f,df,a,b,kind,ux,uy)
                searches.append({'case':case,'segments':m,'start':index,'success':bool(opt.success),'message':str(opt.message),'iterations':int(opt.nit),'nfev':int(opt.nfev),
                    'length_float':repr(value),'length_mp':fmt(di['value']) if di['value'] is not None else '',
                    'validated':di['valid'],'spd':di['spd'],'minimum_spd_margin':fmt(di['margin']),'kkt':repr(di['kkt']),'free_gradient':repr(di['free']),
                    'active_nodes':di['active'],'gradient_error':fmt(di['ad_error']),'fd_consistency':fmt(di['fd_error'])})
                for j,z in enumerate(s):vertices.append({'case':case,'segments':m,'source':'start'+str(index),'index':j,'t':repr((j+1)/m),'s':repr(float(z))})
                runs.append((value,s,bool(opt.success),di))
            inherited_float=float(f(incumbent));best=min(runs+[(inherited_float,incumbent,True,None)],key=lambda r:r[0] if np.isfinite(r[0]) else np.inf)
            if not np.isfinite(best[0]) or inherited_float-best[0]<=float(CFG['selection_margin'])*max(1,inherited_float):best=(inherited_float,incumbent,True,None)
            selected=best[1];di=best[3] if best[3] is not None else diagnose(case,m,'selected_incumbent',selected,True,f,df,a,b,kind,ux,uy)
            if m==16 and di['fd1']:
                with mp.workdps(80):
                    smp=[mp.mpf(repr(float(z))) for z in selected];step=mp.mpf(CFG['mp_fd_steps'][0]);scale=max(1,abs(di['value']))
                    for j in [0,m-2]:
                        left=list(smp);right=list(smp);left[j]-=step;right[j]+=step
                        full=(k.reference_length(a,b,right,kind,ux,uy)-k.reference_length(a,b,left,kind,ux,uy))/(2*step)
                        check(f'{case}/{m}/local_full_gradient/{j}',abs(full-di['fd1'][j])/scale,CFG['local_gradient_identity_tolerance'])
            for j,z in enumerate(selected):vertices.append({'case':case,'segments':m,'source':'selected','index':j,'t':repr((j+1)/m),'s':repr(float(z))})
            check(f'{case}/{m}/bounds',max(0,float(np.max(np.abs(selected)))-.25),CFG['identity_tolerance'])
            value,valid=validate(case,m,selected,ia,ib,kind)
            with mp.workdps(120):
                allvalues=[r[3]['value'] for r in runs]
                spread=(max(allvalues)-min(allvalues))/max(1,value) if all(v is not None for v in allvalues) else mp.inf
                check(f'{case}/{m}/length_starts',spread,CFG['branch_length_tolerance'],'stability')
                check(f'{case}/{m}/nonworse_straight',max(0,value-baseline)/max(1,baseline),CFG['nonworse_tolerance'])
                check(f'{case}/{m}/nonworse_inherited',max(0,value-inherited)/max(1,inherited),CFG['nonworse_tolerance'])
                if kind=='sum':
                    check(f'{case}/{m}/sum_params',float(np.max(np.abs(selected))),CFG['nonworse_tolerance'])
                    check(f'{case}/{m}/sum_length',err(value,baseline),CFG['nonworse_tolerance'])
            shape_spread=max(float(np.max(np.abs(r[1]-q[1]))) for r in runs for q in runs)
            check(f'{case}/{m}/shape_starts',shape_spread,CFG['branch_shape_tolerance'],'shape')
            allvalid=all(r[2] and r[3]['valid'] for r in runs);local=checks[begin:]
            status='FAIL' if any(r['status']=='FAIL' for r in local) else ('INCONCLUSIVE' if not basevalid or not valid or not allvalid or not di['valid'] or any(r['status']=='INCONCLUSIVE' for r in local) else 'PASS_NUMERICAL')
            row={'case':case,'segments':m,'status':status,'length':fmt(value),'validated_starts':sum(r[3]['valid'] for r in runs),'length_spread':fmt(spread),'shape_spread':repr(shape_spread),
                 'kkt':repr(di['kkt']),'free_gradient':repr(di['free']),'active_nodes':di['active']}
            resolutions.append(row);chosen.append((selected.copy(),value,row));previous=selected.copy();previous_value=value;checkpoint()
        refine=[];shape_max=[]
        for j in [0,1]:
            s0,l0,r0=chosen[j];s1,l1,r1=chosen[j+1];fine_t=np.arange(1,len(s1)+1)/(len(s1)+1)
            lifted=np.interp(fine_t,np.linspace(0,1,len(s0)+2),np.r_[0,s0,0]);delta=np.abs(s1-lifted);shape=float(np.max(delta))
            for index,z in enumerate(delta):shapes.append({'case':case,'coarse_segments':len(s0)+1,'fine_segments':len(s1)+1,'index':index,'t':repr(float(fine_t[index])),'normalized_difference':repr(float(z))})
            with mp.workdps(120):e=err(l0,l1)
            check(f'{case}/length_refinement/{j}',e,CFG['length_refinement_tolerance'],'refinement')
            check(f'{case}/shape_refinement/{j}',shape,CFG['shape_refinement_tolerances'][j],'shape')
            refine.append(e);shape_max.append(shape)
        local=checks[case_begin:]
        status='FAIL' if any(r['status']=='FAIL' for r in local) or any(z[2]['status']=='FAIL' for z in chosen) else ('INCONCLUSIVE' if any(r['status']=='INCONCLUSIVE' for r in local) or any(z[2]['status']=='INCONCLUSIVE' for z in chosen) else 'PASS_NUMERICAL')
        with mp.workdps(120):change=(mp.mpf(legacy[case]['K16_length'])-chosen[-1][1])/mp.mpf(legacy[case]['K16_length'])
        cases.append({'case':case,'control':kind=='sum','K_status':legacy[case]['K_status'],'L_status':status,'L64_length':fmt(chosen[-1][1]),
                      'length_error_16_32':fmt(refine[0]),'length_error_32_64':fmt(refine[1]),'shape_error_16_32':repr(shape_max[0]),'shape_error_32_64':repr(shape_max[1]),
                      'relative_change_from_K16':fmt(change),'boundary':bool(chosen[-1][2]['active_nodes'])})
        checkpoint()
    cc={s:sum(r['status']==s for r in checks) for s in ['PASS','FAIL','INCONCLUSIVE']}
    counts={s:sum(r['L_status']==s for r in cases) for s in ['PASS_NUMERICAL','FAIL','INCONCLUSIVE']}
    elapsed=time.monotonic()-start;rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024;budget=elapsed<=CFG['budget_seconds'] and rss<=CFG['memory_target_mib']
    status='FAIL' if counts['FAIL'] or cc['FAIL'] else ('INCONCLUSIVE' if counts['INCONCLUSIVE'] or cc['INCONCLUSIVE'] or not budget else 'PASS_NUMERICAL')
    summary={'status':status,'cases':len(cases),'counts':counts,'resolutions':len(resolutions),'searches':len(searches),'validated_searches':sum(r['validated'] for r in searches),
             'checks':len(checks),'check_counts':cc,'resolved_pending_case':next(r['L_status']=='PASS_NUMERICAL' for r in cases if not r['control'])}
    dump(out/'summary.json',summary)
    dump(out/'provenance.json',{'design_commit':'0212bcf','config_sha256':sha(ROOT/'config.json'),'script_sha256':sha(Path(__file__)),'sources':CFG['sources'],
                              'python':sys.version.split()[0],'numpy':np.__version__,'scipy':scipy.__version__,'mpmath':mp.__version__})
    dump(out/'resources.json',{'seconds':elapsed,'max_rss_mib':rss,'within_budget':budget})
    print(json.dumps(summary|{'seconds':elapsed,'budget':budget}))
    return int(status=='FAIL' or not budget)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    raise SystemExit(main(parser.parse_args().out))
