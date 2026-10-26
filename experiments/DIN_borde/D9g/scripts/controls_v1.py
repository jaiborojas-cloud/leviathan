"""Controles artificiales antes de mirar los desenlaces D9g."""
import ast
import json
import numpy as np
from support_v1 import ROOT,STAGE,RUN,CFG,ARRAYS,write,array,code_guard,guard,frozen_C1
from statistics_v1 import engine,direct_null,setup


def main():
    code_guard();guard();source=frozen_C1();records=[]
    for j in range(4):
        rng=np.random.default_rng(722000+j)
        split=np.tile(np.repeat(np.arange(20),5),2 if j==1 else 1)
        group=split.copy() if j!=1 else np.repeat(np.arange(40),5)
        n=len(split);B=rng.normal(size=(n,4));X=.5*B[:,0]+rng.normal(size=n)
        if j==2:B[:,2]=1.
        Y=np.column_stack([.3*B[:,0]-.2*B[:,1]+k*.17*X+rng.normal(size=n)*(1+.2*j*(split%3)) for k in range(1,4)])
        got=engine(group,split,B,X,Y,j,2000);ind=direct_null(group,split,B,X,Y,j,2000)
        error=float(np.max(np.abs(got['all_D']-ind['all_D'])))
        sse_error=float(np.max(np.abs(got['SSE_full']-ind['SSE_full'])/np.maximum(np.abs(ind['SSE_full']),np.finfo(float).tiny)))
        yc,bc,xc,fo,_,sx,_=setup(group,split,B,X,Y)
        idx=[np.flatnonzero(group==s) for s in np.unique(group)];r=np.random.default_rng(CFG['permutation_seed_base']+j)
        compare=[]
        for b in range(2001):
            xp=X.copy()
            if b:
                for ix in idx:xp[ix]=X[r.permutation(ix)]
            if b in [0,1,2,17,2000]:
                xx=source.cen(xp,group)/sx
                ds=[source.D_cv(yc[:,k],bc,xx,fo) for k in range(3)]
                compare.append(dict(permutation=b,source_D=ds,max_absolute_error=float(np.max(np.abs(got['all_D'][b]-ds)))))
        p_same=bool(np.array_equal(got['p'],ind['p']))
        passed=error<=1e-10 and sse_error<=1e-10 and p_same and all(r['max_absolute_error']<=1e-10 for r in compare)
        arrays=array(f'control_statistics_{j}',D_engine=got['all_D'],D_independent=ind['all_D'],SSE_engine=got['SSE_full'],SSE_independent=ind['SSE_full'],p_engine=got['p'],p_independent=ind['p'])
        records.append(dict(case=j,n=n,aggregate_paired=j==1,constant_base_column=j==2,D_max_error=error,SSE_relative_max_error=sse_error,p_identical=p_same,source=compare,array=arrays,pass_test=passed))
    # Los casos no identificables no deben transformarse en evidencia.
    rng=np.random.default_rng(722100);sp=np.repeat(np.arange(20),5);B=rng.normal(size=(100,4));Y=rng.normal(size=(100,3))
    a=engine(sp,sp,B,B[:,0],Y,0,20)
    constant=engine(sp,sp,B,np.ones(100),Y,0,20)
    degenerate_ok=bool(a['alias'] and constant['alias'] and constant['candidate_constant'])
    blocked=[]
    for rel in ['experiments/DIN_borde/C2/cohorte/c2_cohorte.csv','experiments/DIN_borde/C2/analisis_C2.py','experiments/T2_A1/baseline/__NO_LEER__.csv']:
        try:
            with (ROOT/rel).open('rb'):pass
            raise RuntimeError('Guarda no bloqueó '+rel)
        except PermissionError:blocked.append(rel)
    status='PASS' if all(r['pass_test'] for r in records) and degenerate_ok and len(blocked)==3 else 'FAIL'
    write(RUN/'controls.json',dict(status=status,records=records,degenerate_identified=degenerate_ok,blocked_before_read=blocked,C2_data_read=False))
    print(json.dumps(dict(status=status,controls=len(records),max_D_error=max(r['D_max_error'] for r in records),all_p_identical=all(r['p_identical'] for r in records))))
    if status!='PASS':raise RuntimeError('Controles fallidos: no medir/interpetar')

if __name__=='__main__':main()
