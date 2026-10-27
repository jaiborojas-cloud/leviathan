"""Casos adversariales y trazas,exclusivamente sintéticos."""
import collections
import copy
import json
from pathlib import Path
import traceback
import warnings
import numpy as np
from support import STAGE,CFG,write,code_guard,guard,target,fixture,execute


def trace(m):
    n=20;rows=fixture(n)
    for i,r in enumerate(rows):r['c250']+=(-1)**m.NOMBRES.index(r['nivel'])*.0005*r['split']+.00001*r['k']
    calls=[];slopes=[];old_d=m.Q.D_punto;old_b=m.DR.pendiente
    def d(sp,X,L,Y,fo=None):
        answer=old_d(sp,X,L,Y,fo);calls.append(dict(sp=sp.copy(),X=X.copy(),fo=fo.copy(),D=answer));return answer
    def b(D,c):
        answer=old_b(D,c);slopes.append(dict(D=np.array(D),c=np.array(c),beta=answer));return answer
    m.Q.D_punto=d;m.DR.pendiente=b
    try:result=execute(m,rows,n,NB=CFG['trace_NB'])
    finally:m.Q.D_punto=old_d;m.DR.pendiente=old_b
    assert len(calls)==12*CFG['trace_NB'] and len(slopes)==2+2*CFG['trace_NB']
    origin={r['X10']:r['split'] for r in rows};fold=m.Q.bloques(np.arange(n));paired=True;blocks=True;A0same=True;recomputed=True;error=0.;draws=[]
    lookup={(r['nivel'],r['split'],r['k']):r['c250'] for r in rows}
    for i in range(CFG['trace_NB']):
        batch=calls[12*i:12*(i+1)];ds=[[origin[float(z['X'][j*5])] for j in range(n)] for z in batch]
        paired=paired and all(z==ds[0] for z in ds)
        blocks=blocks and all(np.array_equal(z['fo'],np.repeat([fold[s] for s in ds[0]],5)) for z in batch)
        A0same=A0same and all(np.array_equal(batch[0][k],batch[6][k]) for k in ('sp','X','fo')) and batch[0]['D']==batch[6]['D']
        for j,arm in enumerate(('LP','WD')):
            actual=slopes[2+2*i+j];nvs=m.MANIP[arm]
            cs=[np.median([lookup[nv,s,k] for s in ds[0] for k in range(5)]) for nv in nvs]
            dd=[z['D'] for z in batch[6*j:6*(j+1)]]
            recomputed=recomputed and np.array_equal(actual['c'],cs) and np.array_equal(actual['D'],dd)
            oracle=np.linalg.lstsq(np.column_stack([np.ones(6),cs]),dd,rcond=None)[0][1];error=max(error,abs(oracle-actual['beta']))
        draws.append(ds[0])
    ci={}
    for j,arm in enumerate(('LP','WD')):
        bb=[slopes[2+2*i+j]['beta'] for i in range(CFG['trace_NB'])]
        expected=np.quantile(bb,[.0125,.9875]);actual=result['por_manipulador'][arm]['IC975_beta']
        ci[arm]=dict(expected=expected,actual=actual,exact=bool(np.array_equal(expected,actual)))
    return dict(target_result=result,same_draws_all_levels=paired,copies_original_fold=blocks,A0_exactly_shared=A0same,D_c_beta_recomputed=recomputed,
                max_beta_OLS_error=error,draws=draws,draws_match_seed=bool(np.array_equal(draws,np.random.default_rng(960001).choice(n,size=(CFG['trace_NB'],n),replace=True))),
                ci975=ci,c_changes_in_bootstrap=any(not np.array_equal(x['c'],slopes[j%2]['c']) for j,x in enumerate(slopes[2:])))


def ls_synthetic(m,NB=64,sparse=False,point_bad=False):
    rows=fixture(200);mapping={m.NOMBRES[i]:i for i in range(6)};out={}
    for r in rows:
        if r['nivel'] not in mapping:continue
        l=mapping[r['nivel']];q=dict(r,trajectory=f"q13dr_L{l}_s{r['split']:04d}_k{r['k']}")
        if l==3 and sparse:q['rho_caras_10']=float(np.e) if r['split']==0 else 1.
        if l==3 and point_bad:q['rho_caras_10']=1.
        out[q['trajectory']]=q
    return m.referencia_ls(out,NB)


def compatibility_trace(m):
    nb=64;ls=dict(beta=.077,replicas=np.linspace(.02,.13,nb),fallos=[]);calls=[];old=m.compatibilidad
    def f(bm,bl,bm0,bl0):
        answer=old(bm,bl,bm0,bl0);calls.append(dict(bm=np.array(bm),bl=np.array(bl),same_reference_object=bl is ls['replicas'],result=answer,
              oracle=np.quantile(np.array(bm)-np.array(bl),[.025,.975])));return answer
    m.compatibilidad=f
    try:r=execute(m,fixture(),20,ls=ls,NB=nb)
    finally:m.compatibilidad=old
    return dict(target_result=r,calls=calls,same_LS_in_both=len(calls)==2 and all(x['same_reference_object'] for x in calls),
                differences_correct=all(np.array_equal(x['result']['IC95_dbeta'],x['oracle']) for x in calls))


def degenerate(m,nv):
    rows=fixture(320)
    for r in rows:
        if r['nivel']==nv:r['rho_caras_10']=float(np.e) if r['split']==0 else 1.
    old=np.random.default_rng;draws=[]
    class Spy:
        def __init__(self,g):self.g=g
        def choice(self,*a,**kw):d=self.g.choice(*a,**kw);draws.append(d.copy());return d
    def factory(seed=None,*a,**kw):
        g=old(seed,*a,**kw);return Spy(g) if seed==960001 else g
    np.random.default_rng=factory
    try:r=execute(m,rows,320,NB=CFG['degenerate_NB'])
    finally:np.random.default_rng=old
    expected=[i for i,d in enumerate(draws) if 0 not in d]
    return dict(target_result=r,draw_count=len(draws),expected_failed_indices=expected,
                saved={arm:[f['replica'] for f in r['por_manipulador'][arm].get('fallos',[])] for arm in ('LP','WD')})


def balanced(m,constant=False):
    rows=fixture(320);limits=np.cumsum([0]+[6]*9+[5]*2);heights=[.9,.70,.61,.56,.50,.38,.69,.61,.56,.50,.44]
    for r in rows:
        l=m.NOMBRES.index(r['nivel']);s,k=r['split'],r['k']
        if limits[l]<=s<limits[l+1] and k<3:r['error']='SYNTHETIC_EXCLUDED_SPLIT'
        mid=.1 if r['nivel']=='A0' or constant and r['nivel'].startswith('LP') else CFG['c'][l]
        r['c250']=[.04,.04,mid,.95,.95][k] if s>=64 else heights[l]
    return execute(m,rows,320)


def main():
    code_guard();guard();out=STAGE/'results/cases';out.mkdir(parents=True,exist_ok=False);m=target();base=fixture();cases=[('baseline',lambda:execute(m,base,20)),('bootstrap_trace',lambda:trace(m)),('compatibility_trace',lambda:compatibility_trace(m))]
    changes=[('WD3_X_constant','WD3','X10',-2.),('WD3_L_constant','WD3','rho_caras_10',1.),('WD3_Y_constant','WD3','rho_caras_250',1.),
             ('LP3_Y_constant','LP3','rho_caras_250',1.),('WD_bad_gate','WD3','c250',.72),('LP_bad_gate','LP3','c250',.72),
             ('A0_bad_gate','A0','c250',.79),('A0_X_constant','A0','X10',-2.),('WD5_acc_loss011','WD5','acc_panel250',.82)]
    for name,nv,key,value in changes:
        rows=copy.deepcopy(base)
        for r in rows:
            if r['nivel']==nv:r[key]=value
        cases.append((name,lambda rows=rows:execute(m,rows,20)))
    cases.extend([('WD4_bootstrap_degenerate',lambda:degenerate(m,'WD4')),('A0_bootstrap_degenerate',lambda:degenerate(m,'A0')),
                  ('common_c_LP_decimal_constant',lambda:balanced(m,True)),('common_range_reversed',lambda:balanced(m,False)),
                  ('LS_sparse_bootstrap_result',lambda:ls_synthetic(m,64,True)),('LS_point_degenerate_API',lambda:ls_synthetic(m,64,False,True))])
    def failed_ls():
        ls=ls_synthetic(m,64,True);r=execute(m,base,20,ls=ls,NB=64);plain=execute(m,base,20,NB=64)
        return dict(target_result=r,LS_failed=len(ls['fallos']),primaries_unchanged=r['por_manipulador']==plain['por_manipulador'],full_LS_errors_saved=r['secundarios']['compatibilidad_LS']['fallos_LS']==ls['fallos'])
    cases.append(('LS_failures_do_not_change_primaries',failed_ls))
    cases.extend([('duplicate_ID',lambda:execute(m,base+[base[0]],20)),('foreign_ID',lambda:execute(m,base+[dict(base[0],trajectory='outside')],20))])
    for count in (5,6):
        rows=copy.deepcopy(base);ix=[i for i,r in enumerate(rows) if r['nivel']=='WD2']
        for i in ix[:count]:rows[i]['error']='SYNTHETIC_MISSING'
        cases.append((f'missing_{count}_of100',lambda rows=rows:execute(m,rows,20)))
    records=[]
    for name,fn in cases:
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('always')
            try:r=dict(case=name,status='RETURNED',result=fn())
            except BaseException as e:r=dict(case=name,status='EXCEPTION',exception=type(e).__name__,message=str(e),traceback=traceback.format_exc())
            r['warnings']=[dict(type=w.category.__name__,message=str(w.message)) for w in ws]
        write(out/(name+'.json'),r);records.append(r);print(json.dumps(dict(case=name,status=r['status'])),flush=True)
    write(out/'summary.json',dict(cases=records,synthetic_only=True))


if __name__=='__main__':main()
