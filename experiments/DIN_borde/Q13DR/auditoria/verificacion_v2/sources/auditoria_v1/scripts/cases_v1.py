"""Casos mínimos y trazas independientes. Todas las filas son sintéticas."""
import argparse
import copy
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import traceback
import warnings
import numpy as np
from support import ROOT,STAGE,CFG,EXTERNAL,write,sha,code_guard,guard,target,clean

R=None
C=CFG['levels_c']


def fixture(n=20):
    rng=np.random.default_rng(CFG['case_seed'])
    X=-4+.25*rng.normal(size=(n,5));L=rng.normal(size=(n,5));Y=.2*L+2*X+.001*rng.normal(size=(n,5))
    rows=[]
    for l in range(6):
        for s in range(n):
            for k in range(5):
                rows.append(dict(trajectory=f'q13dr_L{l}_s{s:04d}_k{k}',nivel=l,split=s,k=k,X10=float(X[s,k]),R250=-1.,
                    c250=C[l],q250=.001,rho_caras_10=float(np.exp(L[s,k])),rho_caras_250=float(np.exp(Y[s,k])),
                    rho_vert_10='',rho_vert_250='',acc_panel250=.93,acc_train250=1.,error=''))
    return rows


def execute(rows,n,**kw):
    return R.analizar(rows,n,True,'',B=39,NB=16,B2=19,BQ=19,**kw)


def trace(rows,n):
    calls=[];slopes=[];old_d=R.Q.D_punto;old_s=R.pendiente
    def d(sp,X,L,Y,fo=None):
        answer=old_d(sp,X,L,Y,fo)
        calls.append(dict(sp=sp.copy(),X=X.copy(),fo=fo.copy(),D=answer));return answer
    def slope(D,c):
        answer=old_s(D,c);slopes.append(dict(D=np.array(D),c=np.array(c),beta=answer));return answer
    R.Q.D_punto=d;R.pendiente=slope
    try:result=execute(rows,n)
    finally:R.Q.D_punto=old_d;R.pendiente=old_s
    assert len(calls)==16*6 and len(slopes)==17
    ids={float(r['X10']):r['split'] for r in rows}
    blocks=R.Q.bloques(np.arange(n));paired=True;folded=True;recomputed=True;beta_error=0.
    all_draw=[]
    for b in range(16):
        batch=calls[b*6:(b+1)*6]
        draws=[]
        for item in batch:
            draw=[ids[float(item['X'][j*5])] for j in range(n)];draws.append(draw)
            folded=folded and item['fo'].tolist()==np.repeat([blocks[s] for s in draw],5).tolist()
        paired=paired and all(draw==draws[0] for draw in draws)
        expected=[]
        for l in range(6):
            lookup={(r['split'],r['k']):r['c250'] for r in rows if r['nivel']==l}
            expected.append(np.median([lookup[(s,k)] for s in draws[l] for k in range(5)]))
        item=slopes[b+1]
        recomputed=recomputed and np.array_equal(item['c'],expected) and np.array_equal(item['D'],[x['D'] for x in batch])
        oracle=np.linalg.lstsq(np.column_stack([np.ones(6),expected]),item['D'],rcond=None)[0][1]
        beta_error=max(beta_error,abs(oracle-item['beta']));all_draw.append(draws[0])
    return dict(target_result=result,same_paired_draws=paired,copies_in_original_fold=folded,D_c_recomputed=recomputed,
        c_changed_in_bootstrap=any(not np.array_equal(x['c'],slopes[0]['c']) for x in slopes[1:]),beta_OLS_max_error=beta_error,
        draws=all_draw,actual_arguments=dict(B=39,NB=16))


def median_mismatch(rows,n):
    old=R.pendiente;calls=[]
    def capture(D,c):calls.append(dict(D=np.array(D),c=np.array(c)));return old(D,c)
    R.pendiente=capture
    try:result=execute(rows,n)
    finally:R.pendiente=old
    valid={l:{} for l in range(6)}
    for row in rows:
        if not row['error']:valid[row['nivel']].setdefault(row['split'],[]).append(row)
    common=[s for s in range(n) if all(len(valid[l].get(s,[]))>=3 for l in range(6))]
    med=[np.median([r['c250'] for s in common for r in valid[l][s]]) for l in range(6)]
    return dict(target_result=result,common=common,observed_c=calls[0]['c'],common_sample_c=med,
        different=not np.array_equal(calls[0]['c'],med),observed_beta=old(calls[0]['D'],calls[0]['c']),
        beta_same_D_common_c=old(calls[0]['D'],med))


def cli(name,rows,n,plan_mod=None,levels=None):
    out=EXTERNAL/'cases_v1'/name;out.mkdir(parents=True,exist_ok=False)
    table=out/'table.csv';fields=list(fixture(1)[0])
    with table.open('x',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
    plan=dict(n_splits=n,niveles=levels if levels is not None else [dict(nivel=l,eps=e) for l,e in enumerate([0,.002,.005,.01,.02,.05])],
        ids_sha256=hashlib.sha256('\n'.join(R.universo(int(n))).encode()).hexdigest())
    plan.update(plan_mod or {});write(out/'plan.json',plan)
    write(out/'summary.json',dict(tabla_sha256=sha(table),plan_sha256=sha(out/'plan.json')))
    script=STAGE/'sources/Q13DR/analisis_Q13DR.py'
    p=subprocess.run([sys.executable,'-I',str(script),'--tabla',str(table),'--tabla-sha',sha(table),
        '--plan',str(out/'plan.json'),'--plan-sha',sha(out/'plan.json'),'--resumen',str(out/'summary.json'),'--out',str(out/'result')],capture_output=True,text=True)
    (out/'stdout.txt').write_text(p.stdout);(out/'stderr.txt').write_text(p.stderr)
    result=json.loads((out/'result/RESULTADO_Q13DR.json').read_text()) if p.returncode==0 else None
    return dict(returncode=p.returncode,status=result['veredicto'] if result else 'ABORTA' if 'ABORTA' in p.stdout+p.stderr else 'CRASH',
        result=result,stderr=p.stderr[-4000:],fixture_dir=str(out),table_sha256=sha(table),plan_sha256=sha(out/'plan.json'),
        nominal_CLI_arguments=True)


def build_cases():
    cases=[];base=fixture()
    cases.append(('complete_identical_levels',lambda:execute(copy.deepcopy(base),20)))
    for name,field,value in [('tie_c','c250',C[2]),('q0_boundary','q250',.05),('q0_above','q250',.05001),
        ('c0_below','c250',.79999),('L2_accuracy_low','acc_panel250',.85),('L5_accuracy_extreme_loss','acc_panel250',.1),
        ('L4_accuracy_extreme_loss','acc_panel250',.1),('L4_X_constant','X10',-2.),('L4_L_constant','rho_caras_10',1.),
        ('L4_invalid_rho','rho_caras_250',0.),('q0_negative','q250',-.2),('accuracy_above_one','acc_panel250',1.1)]:
        rows=copy.deepcopy(base)
        level=3 if name=='tie_c' else 0 if name.startswith(('q0','c0')) else 2 if name.startswith('L2') else 5 if name.startswith('L5') else 4 if name.startswith('L4') else None
        for r in rows:
            if level is None or r['nivel']==level:r[field]=value
        cases.append((name,lambda rows=rows:execute(rows,20)))
    for name,count in [('missing_5percent',5),('missing_over_5percent',6)]:
        rows=copy.deepcopy(base);idx=[i for i,r in enumerate(rows) if r['nivel']==3]
        for i in idx[:count]:rows[i]['error']='SYNTHETIC_MISSING'
        cases.append((name,lambda rows=rows:execute(rows,20)))
    for name,rows in [('duplicate_ID',base+[dict(base[0])]),('foreign_ID',base+[dict(base[0],trajectory='q13dr_L6_s0000_k0')])]:
        cases.append((name,lambda rows=rows:execute(rows,20)))
    fingerprint=fixture()
    for r in fingerprint:
        r['X10']=-10-.1*r['split']-.001*r['k'];r['rho_caras_250']=float(np.exp(2*r['X10']+.1*np.log(r['rho_caras_10'])))
        r['c250']=C[r['nivel']]+.0005*(r['split']-10)+.00001*r['k']
    cases.append(('bootstrap_trace_pairing_folds_D_c_beta',lambda:trace(fingerprint,20)))
    unequal=fixture()
    for r in unequal:
        r['c250']=C[r['nivel']]+(-1)**r['nivel']*.002*r['split']
        if r['split']==r['nivel'] and r['k']<3:r['error']='SYNTHETIC_DIFFERENT_MISSING_SPLIT'
    cases.append(('different_observed_and_bootstrap_c_samples',lambda:median_mismatch(unequal,20)))
    common=fixture(12)
    for r in common:
        if r['split']==r['nivel'] and r['k']<3:r['error']='SYNTHETIC_DISJOINT_LOSS'
    cases.append(('common_splits_only_half',lambda:execute(common,12)))
    boot=fixture()
    for r in boot:r.update(rho_caras_10=float(np.e) if r['split']==0 else 1.,rho_caras_250=float(np.exp(2*r['X10'])))
    cases.append(('L_degenerate_in_bootstrap_only',lambda:execute(boot,20)))
    for name,low in [('range_decimal_030',.56),('range_binary_030',.5)]:
        rows=fixture();cs=np.linspace(.86 if low==.56 else .8,low,6)
        for r in rows:r['c250']=float(cs[r['nivel']])
        cases.append((name,lambda rows=rows,cs=cs:dict(computed_range=float(cs[0]-cs[-1]),target=execute(rows,20))))
    for name,acc0,acc2 in [('acc_exact_decimal_005',.95,.9),('acc_exact_decimal_005_other',.93,.88)]:
        rows=fixture()
        for r in rows:r['acc_panel250']=acc2 if r['nivel']==2 else acc0
        cases.append((name,lambda rows=rows,a=acc0,b=acc2:dict(computed_difference=abs(a-b),target=execute(rows,20))))
    fixed=fixture()
    for r in fixed:r['X10']=-2.
    cases.extend([
        ('plan_zero_crash',lambda:cli('plan_zero',[],0)),
        ('plan_fractional_n_accepted',lambda:cli('fractional_n',fixed,20.9)),
        ('plan_wrong_eps_accepted',lambda:cli('wrong_eps',base,20,levels=[dict(nivel=l,eps=0.) for l in range(6)])),
        ('plan_missing_eps_accepted',lambda:cli('missing_eps',fixed,20,levels=[dict(nivel=l) for l in range(6)])),
        ('plan_missing_nivel_crash',lambda:cli('missing_nivel',fixed,20,levels=[dict(eps=0.) for l in range(6)])),
        ('plan_wrong_levels_rejected',lambda:cli('wrong_levels',fixed,20,levels=[dict(nivel=l,eps=0.) for l in (0,1,2,3,4,4)])),
    ])
    return cases


def main():
    global R
    parser=argparse.ArgumentParser();parser.add_argument('--only');parser.add_argument('--out',type=Path,default=STAGE/'results/cases_v1')
    args=parser.parse_args();code_guard();guard(args.out);args.out.mkdir(parents=True,exist_ok=False);EXTERNAL.mkdir(parents=True,exist_ok=True)
    R=target();cases=build_cases();results=[]
    if args.only:cases=[case for case in cases if case[0]==args.only]
    for name,fn in cases:
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('always')
            try:
                result=fn();rec=dict(case=name,status='RETURNED',result=result)
            except BaseException as e:rec=dict(case=name,status='EXCEPTION',exception=type(e).__name__,message=str(e),traceback=traceback.format_exc())
            rec['warnings']=[dict(type=w.category.__name__,message=str(w.message)) for w in ws]
        write(args.out/(name+'.json'),rec);results.append(rec)
        print(json.dumps(dict(case=name,status=rec['status'],exception=rec.get('exception'))),flush=True)
    rules=dict(beta_overlap=R.clasificar_beta([.001,.01]),beta_inside_negative=R.clasificar_beta([-.0199,-.019]),
        endpoint_PASS_priority=R.clasificar_extremo(True,[-.001,.004]),endpoint_disappears=R.clasificar_extremo(False,[-.001,.005]),
        margin_range=.02*(C[0]-C[-1]),nonmonotonic_D=[.05,.01,.04,.005,.03,.01])
    rules['nonmonotonic_slope']=R.pendiente(rules['nonmonotonic_D'],C)
    write(args.out/'rules.json',rules);write(args.out/'summary.json',dict(cases=results,rules=rules,synthetic_only=True,original_suite_executed=False))


if __name__=='__main__':main()
