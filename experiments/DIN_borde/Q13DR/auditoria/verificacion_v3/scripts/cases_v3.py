"""Regresiones literales v1 y casos nuevos: sólo datos sintéticos."""
import copy
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import traceback
import warnings
import numpy as np
from scipy.stats import spearmanr
from support import STAGE,CFG,EXTERNAL,write,sha,code_guard,guard,target,v1_functions,clean

R=None;ENV=None;OUT=STAGE/'results/cases'


def execute(rows,n,**kw):
    params=dict(B=39,NB=16,B2=19,BQ=19);params.update(kw)
    return R.analizar(rows,n,True,'',**params)


def median_capture(rows,n):
    old=R.pendiente;calls=[]
    def capture(D,c):calls.append(dict(D=np.array(D),c=np.array(c)));return old(D,c)
    R.pendiente=capture
    try:result=execute(rows,n)
    finally:R.pendiente=old
    val={l:{} for l in range(6)}
    for row in rows:
        if R.valida(row):val[row['nivel']].setdefault(row['split'],[]).append(row)
    common=[s for s in range(n) if all(len(val[l].get(s,[]))>=3 for l in range(6))]
    expected=[float(np.median([r['c250'] for s in common for r in val[l][s]])) for l in range(6)] if common else []
    return dict(target_result=result,common=common,reached_point=bool(calls),point_c=calls[0]['c'] if calls else None,
        expected_common_c=expected,point_c_equals_common=bool(calls and np.array_equal(calls[0]['c'],expected)))


def cli(name,rows,n,plan_mod=None,levels=None,mode=None):
    out=EXTERNAL/'cases'/name;out.mkdir(parents=True,exist_ok=False)
    table=out/'table.csv';fields=list(ENV['fixture'](1)[0])
    with table.open('x',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
    plan=dict(n_splits=n,niveles=levels if levels is not None else [dict(nivel=l,eps=e) for l,e in enumerate(R.EPS)],ids_sha256=hashlib.sha256('\n'.join(R.universo(int(n))).encode()).hexdigest())
    plan.update(plan_mod or {});write(out/'plan.json',plan)
    write(out/'summary.json',dict(tabla_sha256=sha(table),plan_sha256=sha(out/'plan.json')))
    args_table=out/'absent.csv' if mode=='missing_table' else out if mode=='table_directory' else table
    args_plan=out/'absent.json' if mode=='missing_plan' else out if mode=='plan_directory' else out/'plan.json'
    args_summary=out/'absent_summary.json' if mode=='missing_summary' else out/'summary.json'
    script=STAGE/'sources/v3/Q13DR/analisis_Q13DR.py'
    run=subprocess.run([sys.executable,'-I',str(script),'--tabla',str(args_table),'--tabla-sha',sha(table),'--plan',str(args_plan),'--plan-sha',sha(out/'plan.json'),
        '--resumen',str(args_summary),'--out',str(out/'result')],capture_output=True,text=True)
    (out/'stdout.txt').write_text(run.stdout);(out/'stderr.txt').write_text(run.stderr)
    abort=run.returncode==3 and run.stderr.startswith('ABORTA:') and 'Traceback' not in run.stderr
    result=json.loads((out/'result/RESULTADO_Q13DR.json').read_text()) if run.returncode==0 else None
    return dict(returncode=run.returncode,status=result['veredicto'] if result else 'ABORTA' if abort else 'CRASH',result=result,stderr=run.stderr,
        strict_JSON_no_NaN=bool(result is not None and 'NaN' not in run.stdout and 'Infinity' not in run.stdout),fixture_dir=str(out))


def balanced(mids):
    rows=ENV['fixture'](200);limits=[0,7,14,21,28,34,40];heights=[.9,.70,.61,.54,.42,.04]
    for r in rows:
        l,s,k=r['nivel'],r['split'],r['k']
        if limits[l]<=s<limits[l+1] and k<3:r['error']='SYNTHETIC_EXCLUDED_SPLIT'
        r['c250']=[.04,.04,mids[l],.95 if mids!=[.1]*6 else .9,.95 if mids!=[.1]*6 else .9][k] if s>=40 else heights[l]
    return rows


def constant_c_rules():
    answer=[]
    for c in (.1,.2,.3,.4,.5,.7,.9):
        try:b=R.pendiente([.1,.2,.3,.4,.5,.6],[c]*6);item=dict(c=c,raised=False,beta=b)
        except FloatingPointError as e:item=dict(c=c,raised=True,message=str(e))
        item['true_range']=0.;answer.append(item)
    return dict(cases=answer,all_rejected=all(r['raised'] for r in answer))


def degenerate_logging():
    rows=ENV['fixture'](200)
    for r in rows:r.update(rho_caras_10=float(np.e) if r['split']==0 else 1.,rho_caras_250=float(np.exp(2*r['X10'])))
    old=np.random.default_rng;draws=[]
    class Spy:
        def __init__(self,rng):self.rng=rng
        def choice(self,*a,**kw):
            value=self.rng.choice(*a,**kw);draws.append(value.copy());return value
    def factory(seed=None,*a,**kw):
        rng=old(seed,*a,**kw);return Spy(rng) if seed==860001 else rng
    np.random.default_rng=factory
    try:result=execute(rows,200,NB=300)
    finally:np.random.default_rng=old
    full_indices=[i for i,d in enumerate(draws) if 0 not in d]
    return dict(target_result=result,draw_calls=len(draws),expected_draws=300,no_redraw=len(draws)==300,
        full_failed_indices_by_input=full_indices,output_error_records=len(result.get('bootstrap',{}).get('fallos',[])),
        output_failed_count=result.get('bootstrap',{}).get('replicas_fallidas'),
        all_failed_indices_saved=full_indices==[f['replica'] for f in result.get('bootstrap',{}).get('fallos',[])])


def main():
    global R,ENV
    code_guard();guard();OUT.mkdir(parents=True,exist_ok=False);EXTERNAL.mkdir(parents=True,exist_ok=True)
    R=target();ENV=dict(np=np,copy=copy,CFG=CFG,C=CFG['levels_c'],R=R,execute=execute,cli=cli,median_mismatch=median_capture)
    v1_functions(('fixture','trace','build_cases'),ENV)
    cases=[('v1_'+name,fn) for name,fn in ENV['build_cases']()]
    # Literal v1 extension and scale case: now rejected by the common-split gate.
    oldscale=ENV['fixture'](200)
    for r in oldscale:
        if 16*r['nivel']<=r['split']<16*(r['nivel']+1) and r['k']<3:r['error']='SYNTHETIC_DISJOINT_LOSS'
        r['c250']=.04+.92*((r['split']-96)*5+r['k'])/519 if r['split']>=96 else [.99,.70,.61,.54,.42,.04][r['nivel']]
    cases.append(('v1_singular_beta_N200',lambda:execute(oldscale,200)))
    oldL=ENV['fixture'](200)
    for r in oldL:r.update(rho_caras_10=float(np.e) if r['split']==0 else 1.,rho_caras_250=float(np.exp(2*r['X10'])))
    cases.append(('v1_L_bootstrap_constant_N200',lambda:execute(oldL,200)))
    valid=ENV['fixture']()
    for r in valid:
        r['c250']=CFG['levels_c'][r['nivel']]+(-1)**r['nivel']*.002*r['split']
        if r['nivel']==5 and r['split']==0 and r['k']<3:r['error']='SYNTHETIC_SINGLE_LOSS'
    cases.append(('F01_valid_95percent_common',lambda:median_capture(valid,20)))
    cases.extend([
        ('new_constant_decimal_c_rules',constant_c_rules),
        ('new_constant_decimal_c_common80',lambda:execute(balanced([.1]*6),200)),
        ('new_reversed_common_c_range',lambda:execute(balanced([.3,.35,.4,.45,.5,.6]),200)),
        ('new_degenerate_logging_300',degenerate_logging),
    ])
    base=ENV['fixture']();constant=copy.deepcopy(base)
    for r in constant:r['X10']=-2.
    cases.extend([
        ('new_CLI_complete',lambda:cli('new_complete',base,20)),
        ('new_plan_huge_integer_eps',lambda:cli('new_huge_eps',constant,20,levels=[dict(nivel=l,eps=10**400 if l==1 else R.EPS[l]) for l in range(6)])),
        ('new_plan_missing_file',lambda:cli('new_missing_plan',constant,20,mode='missing_plan')),
        ('new_plan_directory',lambda:cli('new_plan_directory',constant,20,mode='plan_directory')),
        ('new_table_missing_file',lambda:cli('new_missing_table',constant,20,mode='missing_table')),
        ('new_summary_missing_file',lambda:cli('new_missing_summary',constant,20,mode='missing_summary')),
        ('new_plan_bool',lambda:cli('new_n_bool',constant,20,plan_mod=dict(n_splits=True))),
        ('new_plan_401',lambda:cli('new_n_401',constant,20,plan_mod=dict(n_splits=401))),
        ('new_plan_nivel_bool',lambda:cli('new_level_bool',constant,20,levels=[dict(nivel=True if l==1 else l,eps=R.EPS[l]) for l in range(6)])),
    ])
    for name,level,accuracy in [('L5_drop009',5,.84),('L5_drop011',5,.82),('L4_gain007',4,1.),('L2_gain007',2,1.)]:
        rows=copy.deepcopy(base)
        for r in rows:
            if r['nivel']==level:r['acc_panel250']=accuracy
        cases.append((name,lambda rows=rows:execute(rows,20)))
    results=[]
    for name,fn in cases:
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter('always')
            try:answer=fn();record=dict(case=name,status='RETURNED',result=answer)
            except BaseException as e:record=dict(case=name,status='EXCEPTION',exception=type(e).__name__,message=str(e),traceback=traceback.format_exc())
            record['warnings']=[dict(type=w.category.__name__,message=str(w.message)) for w in captured]
        write(OUT/(name+'.json'),record);results.append(record)
        print(json.dumps(dict(case=name,status=record['status'],exception=record.get('exception'))),flush=True)
    rules=dict(primary=R.clasificar_beta([.001,.01]),secondary=R.equivalencia([.001,.01]),endpoint_PASS_priority=R.clasificar_extremo(True,[-.001,.004]),
        constant_D_spearman=R.spearman([1]*6,CFG['levels_c']),tie_spearman=R.spearman([.05,.04,.04,.02,.01,0],CFG['levels_c']),
        tie_spearman_oracle=float(spearmanr([.05,.04,.04,.02,.01,0],CFG['levels_c']).statistic),
        cleaned_JSON=json.dumps(R.limpio(dict(a=float('nan'),b=float('inf'),c=np.int64(2),d=np.bool_(True))),allow_nan=False))
    write(OUT/'rules.json',rules);write(OUT/'summary.json',dict(cases=results,rules=rules,synthetic_only=True,original_suite_executed=False))


if __name__=='__main__':main()
