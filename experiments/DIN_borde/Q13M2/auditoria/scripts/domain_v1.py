"""Dominio heredado e integración de filas inválidas en once niveles."""
import copy
import json
from support import STAGE,write,code_guard,guard,target,fixture,execute


def main():
    code_guard();guard();m=target();out=STAGE/'results/domain';out.mkdir(parents=True,exist_ok=False);base=fixture(1)[0]
    values={'q250':[(-.1,False),(0.,True),(1.,True),(1.1,False),(float('nan'),False),(float('inf'),False)],
            'acc_panel250':[(-.1,False),(0.,True),(1.,True),(1.1,False)],
            'c250':[(-.1,False),(0.,False),(.01,True),(1.,True),(1.1,False)],
            'rho_caras_10':[(-.1,False),(0.,False),(1e-300,True),(float('inf'),False)],
            'rho_caras_250':[(-.1,False),(0.,False),(1e-300,True),(float('nan'),False)],
            'X10':[(float('nan'),False),(float('inf'),False),(float('-inf'),False),(-2.,True)]}
    checks=[]
    for key,vs in values.items():
        for value,expected in vs:
            r=copy.deepcopy(base);r[key]=value;actual=m.DR.valida(r)
            checks.append(dict(field=key,value=str(value),expected=expected,actual=actual,ok=expected==actual))
    assert all(r['ok'] for r in checks)
    rows=fixture();bad=next(r for r in rows if r['nivel']=='WD3');bad['q250']=-.1
    integrated=execute(m,rows,20);assert integrated['faltantes']['WD3']==1 and integrated['splits_comunes']==20
    # Same outcome at all levels should not manufacture a trend.
    rows=fixture();outcome={(r['split'],r['k']):r['rho_caras_250'] for r in rows if r['nivel']=='A0'}
    for r in rows:r['rho_caras_250']=outcome[r['split'],r['k']]
    identical=execute(m,rows,20)
    write(out/'domain.json',dict(status='PASS',checks=checks,integrated_invalid_row=integrated,identical_levels=identical))
    print(json.dumps(dict(domain_status='PASS',checks=len(checks),identical_levels=identical['veredicto_conjunto'])),flush=True)


if __name__=='__main__':main()
