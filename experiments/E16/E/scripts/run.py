#!/usr/bin/env python3
"""Comparación exploratoria E16-E; no modifica ni ejecuta las corridas D."""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time
import statistics
import mpmath as mp

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT/'config.json').read_text())
D = ROOT.parent/'D'
KEYS = ['lambda_min','lambda_max','mu','distance','shape','kappa','metric_scale','length_scale','area_ratio','length_min','length_max']


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def observables(g, h):
    lg = mp.cholesky(g)
    mp.cholesky(h)  # No repair of a non-SPD tensor.
    w = lg**-1 * h * (lg.T**-1)
    vals = mp.eigsy((w+w.T)/2, eigvals_only=True)
    if min(vals) <= 0:
        raise ValueError('nonpositive generalized eigenvalue')
    logs = [mp.log(v) for v in vals]
    mu = sum(logs)/2
    return dict(zip(KEYS, [vals[0],vals[1],mu,mp.sqrt(sum(v*v for v in logs)),
        mp.sqrt(sum((v-mu)**2 for v in logs)),vals[1]/vals[0],mp.exp(mu),
        mp.exp(mu/2),mp.sqrt(mp.det(h)/mp.det(g)),mp.sqrt(vals[0]),mp.sqrt(vals[1])]))


def err(a,b):
    return abs(a-b)/max(1,abs(a),abs(b))


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True)+'\n')


def main(out):
    start=time.monotonic();out.mkdir(parents=True,exist_ok=True)
    assert sha(D/'config.json') == CFG['source_config_sha256']
    assert sha(D/'scripts/run.py') == CFG['source_method_sha256']
    spec=importlib.util.spec_from_file_location('e16d_method',D/'scripts/run.py')
    method=importlib.util.module_from_spec(spec);spec.loader.exec_module(method)
    data=json.loads((D/'config.json').read_text())
    checks=[]; rows=[]; precision={}; unavailable=[]

    def check(name,a,b,tolerance=None):
        e=err(a,b);tol=mp.mpf(tolerance or CFG['relative_tolerance'])
        checks.append({'name':name,'error':mp.nstr(e,30),'status':'PASS' if e<=tol else 'FAIL'})

    for digits in CFG['precision']:
        with mp.workdps(digits):
            for state,theta in data['states'].items():
                theta=[mp.mpf(str(v)) for v in theta]
                for panel,indices in data['panels'].items():
                    inputs=[[mp.mpf(str(v)) for v in data['inputs'][i]] for i in indices]
                    cv,jc,c,_=method.analytic_mp(theta,inputs)
                    for pi,p in enumerate(data['perspectives']):
                        p=[mp.mpf(str(v)) for v in p]
                        bs=method.analytic_B(cv,jc,p,'sum')[0];g=bs*c*bs.T
                        for kind in CFG['comparisons']:
                            key=f'{state}/{panel}/{pi}/{kind}'
                            b=method.analytic_B(cv,jc,p,kind)[0];h=b*c*b.T
                            try:
                                o=observables(g,h)
                            except (ValueError,ZeroDivisionError) as ex:
                                unavailable.append({'case':key,'digits':digits,'reason':str(ex)});continue
                            if digits==CFG['precision'][0]:
                                precision[key]=o
                                continue
                            if key not in precision:
                                unavailable.append({'case':key,'digits':digits,'reason':'missing lower precision'});continue
                            for k in KEYS: check(key+'/precision/'+k,o[k],precision[key][k])
                            check(key+'/decomposition',o['distance']**2,2*o['mu']**2+o['shape']**2)
                            check(key+'/shape_kappa',o['shape'],mp.log(o['kappa'])/mp.sqrt(2))
                            check(key+'/area',o['area_ratio'],o['metric_scale'])
                            for ji,j in enumerate(CFG['charts']):
                                j=mp.matrix(j);oq=observables(j.T*g*j,j.T*h*j)
                                for k in KEYS:check(key+f'/chart{ji}/'+k,o[k],oq[k],CFG['chart_tolerance'])
                            rows.append({'state':state,'panel':panel,'perspective':pi,'composition':kind,
                                         **{k:mp.nstr(v,35) for k,v in o.items()}})
            g=mp.matrix([[2,1],[1,3]]);l=mp.cholesky(g)
            controls=[('equal',g,0,0,0),('scale',4*g,mp.log(4),mp.sqrt(2)*mp.log(4),0),
                      ('shape',l*mp.diag([4,mp.mpf(1)/4])*l.T,0,mp.sqrt(2)*mp.log(4),mp.sqrt(2)*mp.log(4))]
            for name,h,mu,dist,shape in controls:
                o=observables(g,h)
                for k,v in [('mu',mu),('distance',dist),('shape',shape)]:check(f'control/{digits}/{name}/{k}',o[k],v)
            h=mp.diag([1,4]);j=mp.diag([2,1]);g=mp.eye(2)
            check(f'negative/{digits}/raw_before',4,4)
            eig=mp.eigsy(j.T*h*j,eigvals_only=True)
            check(f'negative/{digits}/raw_after',eig[1]/eig[0],1)
            check(f'negative/{digits}/relative',observables(j.T*g*j,j.T*h*j)['kappa'],4)
    with (out/'comparisons.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=['state','panel','perspective','composition']+KEYS);w.writeheader();w.writerows(rows)
    with (out/'checks.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=['name','error','status']);w.writeheader();w.writerows(checks)
    desc={}
    for kind in CFG['comparisons']:
        for panel in ['ALL']+list(data['panels']):
            rr=[r for r in rows if r['composition']==kind and (panel=='ALL' or r['panel']==panel)]
            desc[kind+'/'+panel]={'n':len(rr),'statistics':{k:{'min':min(v),'median':statistics.median(v),'max':max(v)} for k in KEYS if (v:=[float(r[k]) for r in rr])},
              'shape_above_threshold':sum(float(r['shape'])>float(CFG['separation_threshold']) for r in rr),
              'distance_above_threshold':sum(float(r['distance'])>float(CFG['separation_threshold']) for r in rr)}
    failed=sum(c['status']=='FAIL' for c in checks)
    dump(out/'summary.json',{'status':'FAIL' if failed else ('INCONCLUSIVE' if unavailable else 'PASS_NUMERICAL'),
        'comparisons':len(rows),'checks':len(checks),'failed_checks':failed,'unavailable':unavailable,'descriptive':desc})
    dump(out/'provenance.json',{'D_config_sha256':sha(D/'config.json'),'D_method_sha256':sha(D/'scripts/run.py'),
        'E_config_sha256':sha(ROOT/'config.json'),'E_script_sha256':sha(Path(__file__)),'python':sys.version.split()[0],
        'mpmath':mp.__version__,'design_commit':'f9a1b58','analysis':'exploratorio, reutiliza datos D'})
    elapsed=time.monotonic()-start;rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
    dump(out/'resources.json',{'seconds':elapsed,'max_rss_mib':rss,'within_budget':elapsed<=CFG['budget_seconds'] and rss<=CFG['memory_target_mib']})
    print(json.dumps({'comparisons':len(rows),'checks':len(checks),'failed':failed,'unavailable':len(unavailable),'seconds':elapsed}))
    return 1 if failed or unavailable or elapsed>CFG['budget_seconds'] or rss>CFG['memory_target_mib'] else 0

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    raise SystemExit(main(parser.parse_args().out))
