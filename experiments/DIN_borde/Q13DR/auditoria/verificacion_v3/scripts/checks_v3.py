"""Comprobaciones funcionales de dominio/reglas previstas en el protocolo."""
import json
import copy
import math
import numpy as np
from scipy.stats import spearmanr
from support import STAGE,CFG,write,code_guard,guard,target,v1_functions


def main():
    code_guard();guard();m=target();out=STAGE/'results/checks';out.mkdir(parents=True,exist_ok=False)
    env=dict(np=np,CFG=CFG,C=CFG['levels_c']);v1_functions(('fixture',),env);base=env['fixture'](1)[0]
    inputs={
        'q250':[(-.1,False),(0.,True),(1.,True),(1.1,False),(float('nan'),False),(float('inf'),False)],
        'acc_panel250':[(-.1,False),(0.,True),(1.,True),(1.1,False)],
        'c250':[(-.1,False),(0.,False),(.01,True),(1.,True),(1.1,False)],
        'rho_caras_10':[(-.1,False),(0.,False),(1e-300,True),(float('inf'),False)],
        'rho_caras_250':[(-.1,False),(0.,False),(1e-300,True),(float('nan'),False)],
        'X10':[(float('nan'),False),(float('inf'),False),(float('-inf'),False),(-2.,True)]}
    rows=[]
    for field,values in inputs.items():
        for value,expected in values:
            r=copy.deepcopy(base);r[field]=value;actual=m.valida(r)
            rows.append(dict(field=field,value=str(value),expected=expected,actual=actual,pass_test=actual==expected))
    assert all(r['pass_test'] for r in rows)
    plan=dict(n_splits=400,niveles=[dict(nivel=l,eps=e) for l,e in enumerate(m.EPS)],ids_sha256='0'*64)
    assert m.validar_plan(plan)==400
    spearman=[]
    for a in [[1]*6,[.1]*6,[.05,.04,.04,.02,.01,0],[1,1,2,2,3,3]]:
        actual=m.spearman(a,CFG['levels_c']);expected=None if len(set(a))==1 else float(spearmanr(a,CFG['levels_c']).statistic)
        spearman.append(dict(a=a,actual=actual,expected=expected,pass_test=actual==expected or actual is not None and abs(actual-expected)<1e-14))
    assert all(r['pass_test'] for r in spearman)
    both=dict(primary=m.clasificar_beta([.001,.01]),secondary=m.equivalencia([.001,.01]))
    assert both==dict(primary='MODULA',secondary='NO_MODULA')
    cleaned=m.limpio(dict(a=float('nan'),b=float('inf'),c=np.int64(2),d=np.bool_(True)))
    assert json.loads(json.dumps(cleaned,allow_nan=False))==dict(a=None,b=None,c=2,d=True)
    write(out/'domain_and_rules.json',dict(status='PASS',domain=rows,plan_N400_valid=True,spearman=spearman,coexistence=both,strict_JSON=True,
        no_tolerance_added=True,physical_domain_as_declared=True))
    print(json.dumps(dict(status='PASS',domain_cases=len(rows),spearman_cases=len(spearman))),flush=True)


if __name__=='__main__':main()
