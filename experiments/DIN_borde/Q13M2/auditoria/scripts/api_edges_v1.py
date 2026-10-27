"""Límites de API previstos en el diseño; no son entradas CLI de SHA válido."""
import json
import numpy as np
from support import STAGE,code_guard,guard,target,fixture,write


def main():
    code_guard();guard();m=target();out=STAGE/'results/api_edges';out.mkdir(exist_ok=False)
    cases=[]
    try:
        m.compatibilidad(np.zeros(64),np.zeros(63),.1,.1)
        cases.append(dict(case='LS_length_mismatch_API',exception=None))
    except Exception as e:
        cases.append(dict(case='LS_length_mismatch_API',exception=type(e).__name__,message=str(e),reachable_with_fixed_CLI=False))
    rows=[r for r in fixture(20) if r['nivel'] in m.MANIP['LP']]
    arr={};idx={}
    for nv in m.MANIP['LP']:
        rr=[r for r in rows if r['nivel']==nv];sp=np.array([r['split'] for r in rr])
        arr[nv]=dict(sp=sp,X=np.array([r['X10'] for r in rr]),L=np.log([r['rho_caras_10'] for r in rr]),Y=np.log([r['rho_caras_250'] for r in rr]),c=np.full(len(rr),.1))
        idx[nv]={s:np.where(sp==s)[0] for s in range(20)}
    dd,cc=m.replica(arr,m.MANIP['LP'],idx,np.arange(20),m.Q.bloques(np.arange(20)))
    try:
        m.DR.pendiente(list(dd.values()),list(cc.values()))
        cases.append(dict(case='decimal_constant_c_replica',exception=None))
    except Exception as e:
        cases.append(dict(case='decimal_constant_c_replica',exception=type(e).__name__,message=str(e),c=list(cc.values())))
    passed=cases[0]['exception']=='ValueError' and cases[1]['exception']=='FloatingPointError'
    write(out/'results.json',dict(status='PASS_EXPECTED_API_BEHAVIOR' if passed else 'UNEXPECTED',cases=cases,real_data_used=False))
    print(json.dumps(dict(status='PASS_EXPECTED_API_BEHAVIOR' if passed else 'UNEXPECTED')))


if __name__=='__main__':main()
