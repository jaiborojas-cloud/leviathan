"""Único acceso LS real: reproducción y traza de referencia, sin cambiar su cierre."""
import csv
import json
import numpy as np
from support import STAGE,CFG,PROV,EXT,LS,sha,write,code_guard,guard,target


def main():
    code_guard();assert sha(LS)==PROV['LS_reference']['sha256'];guard(True);out=STAGE/'results/reference_LS';out.mkdir(parents=True,exist_ok=False);EXT.mkdir(exist_ok=True)
    with LS.open(newline='') as f:rows={r['trajectory']:r for r in csv.DictReader(f)}
    m=target();old_rng=np.random.default_rng;old_slope=m.DR.pendiente;draws=[];calls=[]
    class Spy:
        def __init__(self,g):self.g=g
        def choice(self,*a,**kw):r=self.g.choice(*a,**kw);draws.append(r.copy());return r
    def rng(seed=None,*a,**kw):
        g=old_rng(seed,*a,**kw);return Spy(g) if seed==960002 else g
    def slope(D,c):
        b=old_slope(D,c);calls.append(dict(D=np.array(D),c=np.array(c),beta=b));return b
    np.random.default_rng=rng;m.DR.pendiente=slope
    try:result=m.referencia_ls(rows,CFG['LS_bootstrap'])
    finally:np.random.default_rng=old_rng;m.DR.pendiente=old_slope
    expected=old_rng(960002).choice(np.arange(200),size=(2000,200),replace=True)
    assert np.array_equal(draws,expected) and len(calls)==2001
    error=0.
    for c in calls:
        b=np.linalg.lstsq(np.column_stack([np.ones(6),c['c']]),c['D'],rcond=None)[0][1];error=max(error,abs(b-c['beta']))
    p=EXT/'reference_LS_bootstrap.npz'
    with p.open('xb') as f:np.savez_compressed(f,beta=result['replicas'],draws=np.array(draws),D=np.array([c['D'] for c in calls]),c=np.array([c['c'] for c in calls]))
    output=dict(beta=result['beta'],expected_exact=0.07692466151365258,exact_reproduction=result['beta']==0.07692466151365258,
        splits_comunes=result['splits_comunes'],bootstrap=2000,seed=960002,all_draws_match_seed=True,failed=result['fallos'],
        max_beta_OLS_error=error,CI95=np.quantile(result['replicas'],[.025,.975]).tolist() if not result['fallos'] else None,
        source_sha256=sha(LS),archive=dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size),
        old_scientific_status_unchanged=True,new_cohort_analysis=False)
    write(out/'reference.json',output);print(json.dumps(output),flush=True)


if __name__=='__main__':main()
