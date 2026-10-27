"""Matriz F01 y nuevas rutas LS/compatibilidad del diff; sintéticos."""
import copy
import json
import traceback
import numpy as np
from support import STAGE,write,code_guard,guard,target,fixture,execute


def main():
    code_guard();guard();out=STAGE/'results/changed_cases';out.mkdir(parents=True,exist_ok=False);m=target();base=fixture(20);baseline=execute(m,base,20)
    records=[]
    def run(name,fn):
        try:r=dict(case=name,status='RETURNED',result=fn())
        except BaseException as e:r=dict(case=name,status='EXCEPTION',exception=type(e).__name__,message=str(e),traceback=traceback.format_exc())
        write(out/(name+'.json'),r);records.append(r);print(json.dumps(dict(case=name,status=r['status'])),flush=True);return r
    def altered(changes,ls=None):
        rows=copy.deepcopy(base)
        for nv,key,value in changes:
            for r in rows:
                if r['nivel']==nv:r[key]=value
        return execute(m,rows,20,ls=ls)
    for nv in ['WD3','LP3','A0']:
        for kind,key,value in [('Y','rho_caras_250',1.),('X','X10',-2.),('L','rho_caras_10',1.)]:
            def fn(nv=nv,key=key,value=value):
                r=altered([(nv,key,value)])
                if nv=='A0':return dict(target_result=r,global_inconclusive=r['veredicto_conjunto']=='INCONCLUSIVE')
                bad,healthy=('WD','LP') if nv.startswith('WD') else ('LP','WD')
                return dict(target_result=r,healthy_identical=r['por_manipulador'].get(healthy)==baseline['por_manipulador'][healthy],
                    localized=r['por_manipulador'].get(bad,{}).get('veredicto')=='INCONCLUSIVE' and r['veredicto_conjunto']=='INCONCLUSIVE_PARCIAL')
            run(f'F01_{nv}_{kind}',fn)
    run('both_exclusive_bad',lambda:altered([('WD3','X10',-2.),('LP3','rho_caras_10',1.)]))
    run('two_primary_failures_WD',lambda:altered([('WD2','rho_caras_250',1.),('WD3','rho_caras_250',1.)]))
    run('two_malo_levels_WD',lambda:altered([('WD2','X10',-2.),('WD3','rho_caras_10',1.)]))
    run('bad_level_and_bad_gate_WD',lambda:altered([('WD3','X10',-2.),('WD4','c250',.8)]))
    def ls_error():
        r=altered([],dict(error='FloatingPointError: SYNTHETIC_LS_POINT_FAILURE'))
        return dict(target_result=r,primaries_identical=r['por_manipulador']==baseline['por_manipulador'] and r['primaria']==baseline['primaria'],
                    LP_WD_identical=r['secundarios']['LP_menos_WD']==baseline['secundarios']['LP_menos_WD'])
    run('LS_error_does_not_contaminate',ls_error)
    for a,b in [(64,63),(64,1),(64,64)]:
        run(f'compatibility_{a}_{b}',lambda a=a,b=b:m.compatibilidad(np.linspace(.01,.1,a),np.linspace(.02,.09,b),.05,.06))
    def ls_bad_size():return altered([],dict(beta=.077,replicas=np.zeros(63),fallos=[]))
    run('bad_size_analyzar_API',ls_bad_size)
    for shape in [(2,32),(0,)]:
        run('compatibility_equal_shape_'+str(shape),lambda shape=shape:m.compatibilidad(np.zeros(shape),np.zeros(shape),.05,.06))
    write(out/'summary.json',dict(cases=records,synthetic_only=True))


if __name__=='__main__':main()
