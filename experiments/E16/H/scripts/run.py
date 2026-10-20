#!/usr/bin/env python3
"""E16-H: transferencia prospectiva del método G a configuraciones nuevas."""
import argparse
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import resource
import statistics
import sys
import time
import mpmath as mp

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config.json').read_text())
D=ROOT.parent/'D';G=ROOT.parent/'G'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fmt(x):return mp.nstr(x,40)
def err(a,b):return abs(a-b)/max(1,abs(a),abs(b))
def dump(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
def writecsv(p,rows):
    if not rows:return
    with p.open('w') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def poly(c,t):return mp.fsum(x*t**i for i,x in enumerate(c))
def conv(a,b):return [mp.fsum(a[i]*b[k-i] for i in range(len(a)) if 0<=k-i<len(b)) for k in range(len(a)+len(b)-1)]

def bernstein(coeff):
    n=len(coeff)-1
    return [mp.fsum(coeff[k]*mp.mpf(math.comb(i,k))/math.comb(n,k) for k in range(i+1)) for i in range(n+1)]

def split(b):
    triangle=[list(b)]
    while len(triangle[-1])>1:
        prev=triangle[-1];triangle.append([(a+c)/2 for a,c in zip(prev,prev[1:])])
    return [row[0] for row in triangle],[row[-1] for row in reversed(triangle)]

def certify_polynomial(coeff):
    b=bernstein(coeff);scale=max(1,max(abs(x) for x in b));threshold=mp.mpf(CFG['positivity_margin'])*scale
    stack=[(b,0)];margins=[];nodes=0;depth=0
    while stack:
        bb,level=stack.pop();nodes+=1;depth=max(depth,level)
        if nodes>CFG['bernstein_max_nodes']:
            return {'ok':False,'margin':min(bb)/scale,'depth':depth,'nodes':nodes,'reason':'node_budget'}
        if min(bb)>threshold:
            margins.append(min(bb)/scale);continue
        if level>=CFG['bernstein_max_depth']:
            return {'ok':False,'margin':min(bb)/scale,'depth':depth,'nodes':nodes,'reason':'depth_budget'}
        left,right=split(bb);stack.append((right,level+1));stack.append((left,level+1))
    return {'ok':True,'margin':min(margins),'depth':depth,'nodes':nodes,'reason':'positive_leaves'}

def positive(h):
    aa=[x[0,0] for x in h];bb=[x[0,1] for x in h];cc=[x[1,1] for x in h]
    det=[a-b for a,b in zip(conv(aa,cc),conv(bb,bb))]
    return certify_polynomial(aa),certify_polynomial(det)

def geometry(q):
    c,b,a=q
    if a==0 and b==0 and c>0:return {'constant':True,'points':[mp.mpf(0),mp.mpf(1)]}
    if a<=0:raise ValueError('a_not_positive')
    center=-b/(2*a);delta=c-b*b/(4*a)
    if delta<=0:raise ValueError('delta_not_positive')
    width=mp.sqrt(delta/a);points={mp.mpf(0),mp.mpf(1)}
    if 0<center<1:points.add(center)
    for k in CFG['width_exponents']:
        for sign in [-1,1]:
            t=center+sign*width*2**k
            if 0<t<1:points.add(t)
    return {'constant':False,'center':center,'delta':delta,'width':width,'points':sorted(points)}

def primitive(q):
    geo=geometry(q)
    if geo['constant']:return mp.sqrt(q[0])
    a=q[2];delta=geo['delta'];width=geo['width'];center=geo['center']
    def p(x):return (x*mp.sqrt(a*x*x+delta)+delta/mp.sqrt(a)*mp.asinh(x/width))/2
    return p(1-center)-p(-center)

def quadrature(q,geo,rule,square=False):
    nodes,weights=rule;points=geo['points']
    if square:points=[mp.sqrt(t) for t in points]
    total=mp.mpf(0)
    for lo,hi in zip(points,points[1:]):
        mid=(lo+hi)/2;half=(hi-lo)/2
        for x,w in zip(nodes,weights):
            u=mid+half*x;t=u*u if square else u
            value=poly(q,t)
            if value<0:raise ValueError('negative_speed_squared')
            total+=half*w*mp.sqrt(value)*(2*u if square else 1)
    return total

def method_rho():
    return json.loads((D/'config.json').read_text())['rho']

def main(out):
    started=time.monotonic();out.mkdir(parents=True,exist_ok=True)
    assert sha(ROOT/'data.json')==CFG['source_config_sha256']
    assert sha(D/'scripts/run.py')==CFG['source_method_sha256']
    assert sha(G/'scripts/run.py')==CFG['source_G_sha256']
    source=json.loads((ROOT/'data.json').read_text())
    assert source['rho']==method_rho()
    spec=importlib.util.spec_from_file_location('method_d',D/'scripts/run.py')
    method=importlib.util.module_from_spec(spec);spec.loader.exec_module(method)
    rows=[];checks=[];lower={};pairedvalues={}
    dump(out/'summary.json',{'status':'INCOMPLETE','reason':'running; not a scientific outcome'})

    def check(name,a,b,tolerance,category='identity'):
        error=err(a,b);ok=error<=mp.mpf(tolerance)
        checks.append({'name':name,'category':category,'error':fmt(error),'status':'PASS' if ok else ('FAIL' if category=='identity' else 'INCONCLUSIVE')})
        return ok
    def checkpoint():
        writecsv(out/'lengths.csv',rows);writecsv(out/'checks.csv',checks)
        if time.monotonic()-started>CFG['budget_seconds']:
            dump(out/'summary.json',{'status':'INCONCLUSIVE','reason':'time_budget','completed':len(rows)})
            raise TimeoutError('budget; partial tables preserved')

    for digits in CFG['precision']:
        with mp.workdps(digits):
            rules={n:mp.gauss_quadrature(n,'legendre') for n in CFG['gauss_orders']}
            # Mathematical controls, separate from the 324 scientific cases.
            for ci,q in enumerate([[mp.mpf(5),mp.mpf(0),mp.mpf(0)],
                                    [mp.mpf(20),mp.mpf(0),mp.mpf(0)],
                                    [mp.mpf('0.25')+mp.mpf('1e-12'),mp.mpf(-1),mp.mpf(1)]]):
                geo=geometry(q);ref=primitive(q);qs=[quadrature(q,geo,rules[n]) for n in CFG['gauss_orders']]
                if ci<2:check(f'control/{digits}/constant{ci}',ref,mp.sqrt(q[0]),CFG['identity_tolerance'])
                check(f'control/{digits}/{ci}/coarse',qs[0],qs[1],CFG['coarse_tolerance'])
                check(f'control/{digits}/{ci}/fine',qs[1],qs[2],CFG['fine_tolerance'])
                check(f'control/{digits}/{ci}/primitive',ref,qs[2],CFG['fine_tolerance'])
                check(f'control/{digits}/{ci}/reparam',ref,quadrature(q,geo,rules[64],True),CFG['fine_tolerance'])
            for ci,(epsilon,expected) in enumerate([(mp.mpf('1e-12'),1),(mp.mpf(0),0),(-mp.mpf('1e-6'),0)]):
                h=[mp.matrix([[1,0],[0,mp.mpf('0.25')+epsilon]]),mp.matrix([[0,0],[0,-1]]),mp.matrix([[0,0],[0,1]])]
                pa,pd=positive(h);check(f'control/{digits}/positivity{ci}',int(pa['ok'] and pd['ok']),expected,CFG['identity_tolerance'])
            for state,tv in source['states'].items():
                theta=[mp.mpf(str(x)) for x in tv]
                for panel,indices in source['panels'].items():
                    inputs=[[mp.mpf(str(v)) for v in source['inputs'][i]] for i in indices]
                    cv,jc,c,_=method.analytic_mp(theta,inputs)
                    for path,(ia,ib) in enumerate(CFG['paths']):
                        a=mp.matrix([mp.mpf(str(x)) for x in source['perspectives'][ia]])
                        endpoint=mp.matrix([mp.mpf(str(x)) for x in source['perspectives'][ib]]);v=endpoint-a
                        for kind in CFG['compositions']:
                            key=f'{state}/{panel}/{path}/{kind}';begin=len(checks)
                            b0=method.analytic_B(cv,jc,list(a),kind)[0]
                            db=method.analytic_B(cv,jc,list(endpoint),kind)[0]-b0
                            h=[b0*c*b0.T,db*c*b0.T+b0*c*db.T,db*c*db.T]
                            q=[(v.T*hh*v)[0] for hh in h];pa,pd=positive(h)
                            try:
                                geo=geometry(q);length=primitive(q)
                                qs=[quadrature(q,geo,rules[n]) for n in CFG['gauss_orders']]
                                square=quadrature(q,geo,rules[64],True)
                                reverse=primitive([q[0]+q[1]+q[2],-q[1]-2*q[2],q[2]])
                                admissible=True;reason=''
                            except ValueError as ex:
                                admissible=False;reason=str(ex);length=None;qs=[];square=None;reverse=None
                            if digits==CFG['precision'][0]:
                                lower[key]={'length':length,'quadrature':qs,'margins':[pa['margin'],pd['margin']]};continue
                            if admissible and lower[key]['length'] is not None:
                                check(key+'/precision/primitive',length,lower[key]['length'],CFG['precision_tolerance'],'precision')
                                for i in range(3):check(key+f'/precision/quadrature{i}',qs[i],lower[key]['quadrature'][i],CFG['precision_tolerance'],'precision')
                                check(key+'/precision/h00',pa['margin'],lower[key]['margins'][0],CFG['precision_tolerance'],'precision')
                                check(key+'/precision/det',pd['margin'],lower[key]['margins'][1],CFG['precision_tolerance'],'precision')
                                check(key+'/quadrature/coarse',qs[0],qs[1],CFG['coarse_tolerance'],'integration')
                                check(key+'/quadrature/fine',qs[1],qs[2],CFG['fine_tolerance'],'integration')
                                check(key+'/quadrature/primitive',length,qs[2],CFG['fine_tolerance'],'integration')
                                check(key+'/quadrature/reparam',length,square,CFG['fine_tolerance'],'integration')
                                check(key+'/reverse',length,reverse,CFG['identity_tolerance'])
                                if kind=='sum':check(key+'/constant',length,mp.sqrt(q[0]),CFG['identity_tolerance'])
                            elif admissible:
                                reason='lower_precision_inadmissible';admissible=False
                            for t in [mp.mpf(i)/4 for i in range(5)]:
                                bt=method.analytic_B(cv,jc,list(a+t*v),kind)[0];hh=bt*c*bt.T
                                for i in range(2):
                                    for j in range(2):check(key+f'/tensor/{t}/{i}/{j}',hh[i,j],poly([x[i,j] for x in h],t),CFG['identity_tolerance'])
                            for ji,j in enumerate(CFG['charts']):
                                j=mp.matrix(j);vq=j**-1*v
                                for k,hh in enumerate(h):check(key+f'/chart{ji}/{k}',q[k],(vq.T*(j.T*hh*j)*vq)[0],CFG['identity_tolerance'])
                            local=checks[begin:]
                            status='FAIL' if any(x['status']=='FAIL' for x in local) else ('INCONCLUSIVE' if not admissible or not pa['ok'] or not pd['ok'] or any(x['status']=='INCONCLUSIVE' for x in local) else 'PASS_NUMERICAL')
                            row={'state':state,'panel':panel,'path':path,'composition':kind,'status':status,'formula_admissible':admissible,'reason':reason,
                                'q_c':fmt(q[0]),'q_b':fmt(q[1]),'q_a':fmt(q[2]),'length':fmt(length) if length is not None else '',
                                **{f'GL{n}':fmt(z) for n,z in zip(CFG['gauss_orders'],qs)},
                                'reparam_length':fmt(square) if square is not None else '',
                                'segments':len(geo['points'])-1 if admissible else 0,
                                'h00_positive':pa['ok'],'h00_margin':fmt(pa['margin']),'h00_depth':pa['depth'],'h00_nodes':pa['nodes'],
                                'det_positive':pd['ok'],'det_margin':fmt(pd['margin']),'det_depth':pd['depth'],'det_nodes':pd['nodes']}
                            # Fixed columns even if a formula becomes inadmissible.
                            for n in CFG['gauss_orders']:row.setdefault(f'GL{n}','')
                            rows.append(row);pairedvalues[(state,panel,path,kind)]=(length,status)
                checkpoint()
    paired=[]
    with mp.workdps(CFG['precision'][-1]):
        for (state,panel,path,kind),(length,status) in pairedvalues.items():
            if kind=='sum':continue
            base,bs=pairedvalues[(state,panel,path,'sum')]
            paired.append({'state':state,'panel':panel,'path':path,'composition':kind,
                'ratio':fmt(length/base) if length is not None and base else '',
                'valid':status=='PASS_NUMERICAL' and bs=='PASS_NUMERICAL'})
    desc={}
    for kind in ['product','quadratic']:
        for panel in ['ALL']+list(source['panels']):
            rr=[r for r in paired if r['composition']==kind and (panel=='ALL' or r['panel']==panel)]
            vals=[float(r['ratio']) for r in rr if r['valid']];tol=float(CFG['ratio_separation'])
            desc[kind+'/'+panel]={'total':len(rr),'valid':len(vals),'unvalidated':len(rr)-len(vals),
                'min':min(vals) if vals else None,'median':statistics.median(vals) if vals else None,'max':max(vals) if vals else None,
                'shorter':sum(x<1-tol for x in vals),'longer':sum(x>1+tol for x in vals)}
    counts={s:sum(r['status']==s for r in rows) for s in ['PASS_NUMERICAL','FAIL','INCONCLUSIVE']}
    cc={s:sum(c['status']==s for c in checks) for s in ['PASS','FAIL','INCONCLUSIVE']}
    status='FAIL' if counts['FAIL'] or cc['FAIL'] else ('INCONCLUSIVE' if counts['INCONCLUSIVE'] or cc['INCONCLUSIVE'] else 'PASS_NUMERICAL')
    summary={'status':status,'lengths':len(rows),'counts':counts,'checks':len(checks),'check_counts':cc,
        'paired':len(paired),'descriptive':desc}
    writecsv(out/'lengths.csv',rows);writecsv(out/'checks.csv',checks)
    writecsv(out/'paired_ratios.csv',paired);dump(out/'summary.json',summary)
    dump(out/'provenance.json',{'D_method_sha256':sha(D/'scripts/run.py'),'G_method_sha256':sha(G/'scripts/run.py'),
        'H_data_sha256':sha(ROOT/'data.json'),'H_config_sha256':sha(ROOT/'config.json'),
        'H_script_sha256':sha(Path(__file__)),'design_commit':'3c96c95','python':sys.version.split()[0],'mpmath':mp.__version__,
        'analysis':'transferencia prospectiva instrumental; no validación predictiva'})
    elapsed=time.monotonic()-started;rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
    budget=elapsed<=CFG['budget_seconds'] and rss<=CFG['memory_target_mib']
    dump(out/'resources.json',{'seconds':elapsed,'max_rss_mib':rss,'within_budget':budget})
    print(json.dumps({'status':status,'counts':counts,'checks':cc,'seconds':elapsed,'budget':budget}))
    return int(status=='FAIL' or not budget)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    raise SystemExit(main(p.parse_args().out))
