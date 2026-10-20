#!/usr/bin/env python3
"""E16-F: longitudes de segmentos fijados, sin minimización geodésica."""
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
D=ROOT.parent/'D'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def error(a,b):return abs(a-b)/max(1,abs(a),abs(b))
def fmt(a):return mp.nstr(a,35)
def poly(c,t):return mp.fsum(v*t**i for i,v in enumerate(c))
def conv(a,b):return [mp.fsum(a[i]*b[k-i] for i in range(len(a)) if 0<=k-i<len(b)) for k in range(len(a)+len(b)-1)]
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def csvwrite(p,rows,fields):
    with p.open('w') as h:
        w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(rows)

def bernstein_bounds(coeff):
    """Bounds from all fixed subintervals; no adaptive refinement or clipping."""
    n=len(coeff)-1;values=[];count=CFG['positivity_subintervals'];width=mp.mpf(1)/count
    for j in range(count):
        u=mp.mpf(j)/count
        shifted=[mp.fsum(coeff[k]*math.comb(k,i)*u**(k-i)*width**i for k in range(i,n+1)) for i in range(n+1)]
        values.extend(mp.fsum(shifted[k]*mp.mpf(math.comb(i,k))/math.comb(n,k) for k in range(i+1)) for i in range(n+1))
    return min(values),max(abs(v) for v in values)

def positive(h):
    aa=[v[0,0] for v in h];bb=[v[0,1] for v in h];cc=[v[1,1] for v in h]
    ac=conv(aa,cc);b2=conv(bb,bb);det=[a-b for a,b in zip(ac,b2)]
    a,sa=bernstein_bounds(aa);d,sd=bernstein_bounds(det)
    na=a/max(1,sa);nd=d/max(1,sd)
    return na,nd,na>mp.mpf(CFG['positivity_margin']) and nd>mp.mpf(CFG['positivity_margin'])

def integrate(q,n,nodes,weights,mode='normal'):
    total=mp.mpf(0)
    for panel in range(n):
        for x,w in zip(nodes,weights):
            u=(panel+(x+1)/2)/n
            if mode=='reverse':t=1-u;factor=1
            elif mode=='square':t=u*u;factor=2*u
            else:t=u;factor=1
            value=poly(q,t)
            if value<0:raise ValueError('negative speed squared')
            total+=w*factor*mp.sqrt(value)/(2*n)
    return total

def main(out):
    start=time.monotonic();out.mkdir(parents=True,exist_ok=True)
    assert sha(D/'config.json')==CFG['source_config_sha256']
    assert sha(D/'scripts/run.py')==CFG['source_method_sha256']
    spec=importlib.util.spec_from_file_location('method_d',D/'scripts/run.py')
    method=importlib.util.module_from_spec(spec);spec.loader.exec_module(method)
    data=json.loads((D/'config.json').read_text());checks=[];rows=[];prior={};internal={}
    def check(name,a,b,tol,category='identity'):
        e=error(a,b);ok=e<=mp.mpf(tol)
        checks.append({'name':name,'category':category,'error':fmt(e),'status':'PASS' if ok else ('FAIL' if category=='identity' else 'INCONCLUSIVE')})
        return ok
    for digits in CFG['precision']:
        with mp.workdps(digits):
            nodes,weights=mp.gauss_quadrature(CFG['gauss_order'],'legendre')
            for state,theta in data['states'].items():
                theta=[mp.mpf(str(v)) for v in theta]
                for panel,indices in data['panels'].items():
                    inputs=[[mp.mpf(str(v)) for v in data['inputs'][i]] for i in indices]
                    cv,jc,c,_=method.analytic_mp(theta,inputs)
                    for path,(ia,ib) in enumerate(CFG['paths']):
                        a=mp.matrix([mp.mpf(str(v)) for v in data['perspectives'][ia]])
                        b=mp.matrix([mp.mpf(str(v)) for v in data['perspectives'][ib]]);v=b-a
                        for kind in CFG['compositions']:
                            key=f'{state}/{panel}/{path}/{kind}';begin=len(checks)
                            b0=method.analytic_B(cv,jc,list(a),kind)[0]
                            db=method.analytic_B(cv,jc,list(b),kind)[0]-b0
                            h=[b0*c*b0.T,db*c*b0.T+b0*c*db.T,db*c*db.T]
                            q=[(v.T*hh*v)[0] for hh in h]
                            na,nd,spd=positive(h)
                            lengths=[integrate(q,n,nodes,weights) for n in CFG['quadrature_panels']]
                            if digits==CFG['precision'][0]:
                                prior[key]=[lengths,na,nd];continue
                            for i,(lo,hi) in enumerate(zip(prior[key][0],lengths)):
                                check(key+f'/precision/L{i}',lo,hi,CFG['precision_tolerance'],'precision')
                            check(key+'/precision/positive_a',prior[key][1],na,CFG['precision_tolerance'],'precision')
                            check(key+'/precision/positive_det',prior[key][2],nd,CFG['precision_tolerance'],'precision')
                            for i in [0,1]:check(key+f'/quadrature/{i}',lengths[i],lengths[i+1],CFG['quadrature_tolerance'],'quadrature')
                            for t in [mp.mpf(i)/4 for i in range(5)]:
                                bt=method.analytic_B(cv,jc,list(a+t*v),kind)[0];direct=bt*c*bt.T
                                for i in range(2):
                                    for j in range(2):check(key+f'/polynomial/{t}/{i}/{j}',direct[i,j],poly([hh[i,j] for hh in h],t),CFG['identity_tolerance'])
                            for ji,j in enumerate(CFG['charts']):
                                j=mp.matrix(j);vq=j**-1*v
                                for k,hh in enumerate(h):check(key+f'/chart{ji}/{k}',q[k],(vq.T*(j.T*hh*j)*vq)[0],CFG['identity_tolerance'])
                            reverse=integrate(q,CFG['quadrature_panels'][-1],nodes,weights,'reverse')
                            square=integrate(q,CFG['quadrature_panels'][-1],nodes,weights,'square')
                            check(key+'/reverse',lengths[-1],reverse,CFG['quadrature_tolerance'],'quadrature')
                            check(key+'/reparam',lengths[-1],square,CFG['quadrature_tolerance'],'quadrature')
                            if kind=='sum':check(key+'/constant_metric',lengths[-1],mp.sqrt(q[0]),CFG['identity_tolerance'])
                            local=checks[begin:]
                            status='FAIL' if any(x['status']=='FAIL' for x in local) else ('INCONCLUSIVE' if not spd or any(x['status']=='INCONCLUSIVE' for x in local) else 'PASS_NUMERICAL')
                            row={'state':state,'panel':panel,'path':path,'composition':kind,'status':status,'positive_global':spd,
                                 'positive_h00_margin':fmt(na),'positive_det_margin':fmt(nd),
                                 'L4':fmt(lengths[0]),'L8':fmt(lengths[1]),'L16':fmt(lengths[2]),
                                 'reverse_L16':fmt(reverse),'reparam_L16':fmt(square)}
                            rows.append(row);internal[(state,panel,path,kind)]=(lengths[-1],status)
            q=[mp.mpf(5),mp.mpf(0),mp.mpf(0)]
            for scale in [1,4]:check(f'control/{digits}/constant/{scale}',integrate([scale*x for x in q],16,nodes,weights),mp.sqrt(5*scale),CFG['identity_tolerance'])
            negative=[mp.matrix([[1,0],[0,mp.mpf(1)/4]]),mp.matrix([[0,0],[0,-1]]),mp.matrix([[0,0],[0,1]])]
            check(f'control/{digits}/interior_singularity_detected',int(positive(negative)[2]),0,CFG['identity_tolerance'])
    paired=[]
    with mp.workdps(CFG['precision'][-1]):
        for (state,panel,path,kind),(length,status) in internal.items():
            if kind=='sum':continue
            baseline,bs=internal[(state,panel,path,'sum')]
            paired.append({'state':state,'panel':panel,'path':path,'composition':kind,'ratio':fmt(length/baseline),
                'valid':status=='PASS_NUMERICAL' and bs=='PASS_NUMERICAL'})
    counts={s:sum(r['status']==s for r in rows) for s in ['PASS_NUMERICAL','FAIL','INCONCLUSIVE']}
    desc={}
    for kind in ['product','quadratic']:
        for panel in ['ALL']+list(data['panels']):
            rr=[r for r in paired if r['composition']==kind and (panel=='ALL' or r['panel']==panel)]
            val=[float(r['ratio']) for r in rr if r['valid']];tol=float(CFG['ratio_separation'])
            desc[kind+'/'+panel]={'total':len(rr),'valid':len(val),'inconclusive_or_failed':len(rr)-len(val),
                'min':min(val) if val else None,'median':statistics.median(val) if val else None,'max':max(val) if val else None,
                'shorter':sum(v<1-tol for v in val),'longer':sum(v>1+tol for v in val),'within_threshold':sum(abs(v-1)<=tol for v in val)}
    failure=any(c['status']=='FAIL' for c in checks);inc=any(c['status']=='INCONCLUSIVE' for c in checks)
    status='FAIL' if failure or counts['FAIL'] else ('INCONCLUSIVE' if inc or counts['INCONCLUSIVE'] else 'PASS_NUMERICAL')
    csvwrite(out/'lengths.csv',rows,list(rows[0]))
    csvwrite(out/'paired_ratios.csv',paired,list(paired[0]))
    csvwrite(out/'checks.csv',checks,['name','category','error','status'])
    dump(out/'summary.json',{'status':status,'lengths':len(rows),'counts':counts,'paired':len(paired),'checks':len(checks),
         'check_counts':{s:sum(c['status']==s for c in checks) for s in ['PASS','FAIL','INCONCLUSIVE']},'descriptive':desc})
    dump(out/'provenance.json',{'D_config_sha256':sha(D/'config.json'),'D_method_sha256':sha(D/'scripts/run.py'),
        'F_script_sha256':sha(Path(__file__)),'F_config_sha256':sha(ROOT/'config.json'),'design_commit':'7717db2',
        'python':sys.version.split()[0],'mpmath':mp.__version__,'analysis':'exploratorio; reutiliza datos D'})
    elapsed=time.monotonic()-start;rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
    budget=elapsed<=CFG['budget_seconds'] and rss<=CFG['memory_target_mib']
    dump(out/'resources.json',{'seconds':elapsed,'max_rss_mib':rss,'within_budget':budget})
    print(json.dumps({'status':status,'counts':counts,'checks':len(checks),'seconds':elapsed,'budget':budget}))
    return int(status=='FAIL' or not budget)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    raise SystemExit(main(p.parse_args().out))
