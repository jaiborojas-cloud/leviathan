"""Dos mecanismos a N=200, sin cambiar fuentes ni estimando Monte Carlo."""
import json
import traceback
import warnings
import numpy as np
from support import STAGE,write,code_guard,guard,target
import cases_v1 as old


def main():
    code_guard();guard();old.R=target();out=STAGE/'results/scale_N200';out.mkdir(parents=True,exist_ok=False)
    for name in ('L_bootstrap_constant','beta_bootstrap_singular'):
        rows=old.fixture(200)
        if name=='L_bootstrap_constant':
            for r in rows:r.update(rho_caras_10=float(np.e) if r['split']==0 else 1.,rho_caras_250=float(np.exp(2*r['X10'])))
        else:
            heights=[.99,.70,.61,.54,.42,.04]
            for r in rows:
                if 16*r['nivel']<=r['split']<16*(r['nivel']+1) and r['k']<3:r['error']='SYNTHETIC_DISJOINT_LOSS'
                r['c250']=.04+.92*((r['split']-96)*5+r['k'])/519 if r['split']>=96 else heights[r['nivel']]
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter('always')
            try:
                res=old.execute(rows,200)
                try:json.dumps(res,allow_nan=False);valid=True
                except ValueError:valid=False
                rec=dict(status='RETURNED',result=res,strict_JSON_finite=valid)
            except BaseException as e:rec=dict(status='EXCEPTION',exception=type(e).__name__,traceback=traceback.format_exc())
            rec['warnings']=[dict(type=w.category.__name__,message=str(w.message)) for w in captured]
        write(out/(name+'.json'),rec)
        print(json.dumps(dict(case=name,status=rec['status'],exception=rec.get('exception'),strict_JSON_finite=rec.get('strict_JSON_finite'))),flush=True)


if __name__=='__main__':main()
