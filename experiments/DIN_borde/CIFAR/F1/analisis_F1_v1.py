"""DIN-CIFAR F1 BORRADOR v1: analista exploratorio; no entrena ni lee imágenes.

Primaria C1 exacta por SHA. Las pruebas usan exclusivamente filas sintéticas.
CLI: presupuestos fijos, plan BORRADOR solo con PRUEBA_SINTETICA, salida exclusiva.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import types
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
TEMPLATE_SHA='b120fb62adb6dea9f7878a12ef5625d7fafbf9caf9ad8038b6ec381e7cac6e36'
C1_SHA='8711f468d0df110a94c9cfdf6a1d0777f495537546cdce516929f0cb129858d5'
VISITS=(5,10,30,250)
COLUMNS=('trajectory,split,k,update,estado,error,X,R,c,q,tr_M,acc_train,acc_panel,acc_test,ce_train,ce_panel,ce_test,k_star,k_star_wrong,frac_panel_wrong,'
         'rho_caras,rho_vert,rho_status,rho_reason,rho_caras_quad_error,rho_caras_prefix_bound,rho_caras_tail_bound,rho_vert_quad_error,rho_vert_prefix_bound,rho_vert_tail_bound,'
         'rho_evaluations,rho_seconds,model_sha256,f_sha256,split_sha256,diagnostic_sha256').split(',')
GATE_CHECKS=('equivalencia_wine_<=1e-12','rho_valido_en_ambos','estado_cercano_al_borde_p_min<1e-3',
             'control_negativo_cabeza_completa_>1e-9','cnn_probabilidades_invariantes','cnn_M_reducida_invariante',
             'cnn_reducida_vs_completa_difieren_>1e-9','pca_determinista','pca_signo')
_REFERENCE=None


class Aborta(ValueError):pass
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return isinstance(x,str) and re.fullmatch('[0-9a-f]{64}',x) is not None
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)
def json_read(p):
    def bad(x):raise Aborta('JSON no finito: '+x)
    return json.loads(Path(p).read_text(encoding='utf-8'),parse_constant=bad)
def number(x):
    if isinstance(x,(bool,np.bool_)):return None
    try:v=float(x)
    except (TypeError,ValueError,OverflowError):return None
    return v if math.isfinite(v) else None
def integer(x,lo,hi):
    if isinstance(x,bool):raise Aborta('entero booleano')
    if isinstance(x,int):v=x
    elif isinstance(x,str) and len(x)<=6 and re.fullmatch('[0-9]+',x):v=int(x)
    else:raise Aborta('entero inválido')
    if not lo<=v<=hi:raise Aborta('entero fuera de rango')
    return v
def clean(x):
    if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [clean(v) for v in x]
    if isinstance(x,np.ndarray):return clean(x.tolist())
    if isinstance(x,np.generic):return clean(x.item())
    if isinstance(x,float) and not math.isfinite(x):return None
    return x
def reference():
    global _REFERENCE
    if _REFERENCE is None:
        p=ROOT/'experiments/DIN_borde/C1/analisis_C1_v2.py'
        if sha(p)!=C1_SHA:raise Aborta('SHA de C1 modificado')
        m=types.ModuleType('cifar_f1_C1_frozen');m.__file__=str(p)
        exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);_REFERENCE=m
    return _REFERENCE
def universe():return [f'cifar_f1_s{s:04d}_k{k}' for s in range(100) for k in range(5)]
def validar_plan(plan):
    p=HERE/'plan_F1_BORRADOR_v1.json'
    if sha(p)!=TEMPLATE_SHA:raise Aborta('Plantilla del diseño modificada')
    if not isinstance(plan,dict) or plan.get('estado') not in ('BORRADOR','CONGELADO'):raise Aborta('Plan/estado inválidos')
    normalized=dict(plan,estado='BORRADOR')
    try:same=canonical(normalized)==canonical(json_read(p))
    except (TypeError,ValueError,OverflowError):same=False
    if not same:raise Aborta('Plan diferente del diseño F1 v1 propuesto')
    if hashlib.sha256('\n'.join(universe()).encode()).hexdigest()!=plan['ids_sha256']:raise Aborta('Universo no vinculado')
    return plan


def integrity(plan,resumen,gate,expected):
    """Devuelve todos los motivos; no considera la transcripción F0 como compuerta."""
    out=[]
    if not isinstance(resumen,dict):return ['resumen no es objeto']
    for key in ('tabla_sha256','plan_sha256','productor_sha256','compuerta_sha256','dataset_sha256'):
        if not digest(expected.get(key)) or resumen.get(key)!=expected[key]:out.append('enlace inválido: '+key)
    if resumen.get('fuentes')!={k:v['sha256'] for k,v in plan['fuentes'].items()}:out.append('fuentes de productor no vinculadas')
    if resumen.get('versiones')!=plan['versiones']:out.append('versiones de productor distintas')
    if resumen.get('tipo_datos') not in ('PRUEBA_SINTETICA','CIFAR3_DESCUBRIMIENTO'):out.append('tipo de datos no declarado')
    if plan['estado']=='BORRADOR' and resumen.get('tipo_datos')!='PRUEBA_SINTETICA':raise Aborta('Borrador: solo pruebas sintéticas antes de congelar')
    if not isinstance(gate,dict):return out+['compuerta no es objeto']
    checks=gate.get('checks')
    if not isinstance(checks,dict) or set(checks)!=set(GATE_CHECKS) or any(v is not True for v in checks.values()):out.append('checks de compuerta no válidos')
    worst=number(gate.get('peor_error_relativo'))
    if gate.get('veredicto')!='PASA' or worst is None or not 0<=worst<=1e-12:out.append('compuerta no PASA o error fuera de tolerancia')
    if gate.get('fuentes')!={'core':plan['fuentes']['core']['sha256'],'rho_v2':plan['fuentes']['rho']['sha256']}:out.append('fuentes de compuerta distintas')
    versions=gate.get('versiones',{})
    if not isinstance(versions,dict) or any(versions.get(k)!=v for k,v in plan['versiones'].items()):out.append('versiones de compuerta distintas')
    return out


def validate_visit(row,u):
    """No modifica estado ni datos. Se conservan TODOS los motivos de la fila."""
    reasons=[];values={k:number(row.get(k)) for k in ('X','R','c','q','tr_M','acc_train','acc_panel','acc_test','ce_train','ce_panel','ce_test','frac_panel_wrong')}
    for k,v in values.items():
        if v is None:reasons.append(k+': no finito/ausente')
    for k in ('X','R'):
        if values[k] is not None and values[k]>1e-12:reasons.append(k+': positivo fuera de tolerancia')
    if values['X'] is not None and values['R'] is not None and values['R']>values['X']+1e-12:reasons.append('R mayor que X')
    if values['c'] is not None and not 0<values['c']<=1:reasons.append('c fuera de (0,1]')
    if values['tr_M'] is not None and not values['tr_M']>0:reasons.append('tr_M no positiva')
    for k in ('q','acc_train','acc_panel','acc_test','frac_panel_wrong'):
        if values[k] is not None and not 0<=values[k]<=1:reasons.append(k+': fuera de [0,1]')
    for k in ('ce_train','ce_panel','ce_test'):
        if values[k] is not None and values[k]<0:reasons.append(k+': negativa')
    if values['acc_panel'] is not None and values['frac_panel_wrong'] is not None and abs(values['acc_panel']+values['frac_panel_wrong']-1)>1e-12:reasons.append('fracción mal clasificada incoherente')
    for k,hi in [('k_star',26),('k_star_wrong',1)]:
        try:integer(row.get(k),0,hi)
        except Aborta:reasons.append(k+': entero fuera de dominio')
    for k in ('model_sha256','f_sha256','split_sha256'):
        if not digest(row.get(k)):reasons.append(k+': digest inválido')
    metric_ok=not reasons
    state=row.get('estado')
    if state!='MEDIDA':reasons.append('estado declarado: '+str(state))
    if state=='MEDIDA' and row.get('error'):reasons.append('MEDIDA con error no vacío')
    if state in ('FALLIDA','INVALID_RHO') and not (row.get('error') or row.get('rho_reason')):reasons.append('fallo sin motivo')
    if u in (10,250):
        if row.get('rho_status')!='VALID_NUMERICAL_ESTIMATE':reasons.append('rho_status: '+str(row.get('rho_status')))
        rho={k:number(row.get(k)) for k in ('rho_caras','rho_vert')}
        for key,v in rho.items():
            if v is None or v<=0:reasons.append(key+': no positiva/finita')
            terms=[number(row.get(key+'_'+t)) for t in ('quad_error','prefix_bound','tail_bound')]
            if any(t is None or t<0 for t in terms):reasons.append(key+': auditoría no válida')
            elif v is not None and v>0 and (terms[0]>1e-6*v or terms[1]+terms[2]>1e-6*v):reasons.append(key+': auditoría excedida')
        if all(v is not None and v>0 for v in rho.values()) and rho['rho_caras']>rho['rho_vert']:reasons.append('rho_caras mayor que rho_vert')
        try:integer(row.get('rho_evaluations'),0,4096)
        except Aborta:reasons.append('evaluaciones rho inválidas')
        sec=number(row.get('rho_seconds'))
        if sec is None or not 0<=sec<=120:reasons.append('tiempo rho inválido')
        if not digest(row.get('diagnostic_sha256')):reasons.append('diagnóstico rho sin SHA')
    else:
        if state=='INVALID_RHO':reasons.append('INVALID_RHO en visita sin rho')
        if row.get('rho_status')!='NO_SOLICITADA':reasons.append('rho no prevista en visita')
        fields=[k for k in COLUMNS if k.startswith('rho_') and k not in ('rho_status','rho_reason')]+['diagnostic_sha256']
        if any(row.get(k) not in ('',None) for k in fields):reasons.append('medida rho extra no planificada')
    return dict(valid=not reasons,metric_ok=metric_ok,reasons=reasons,values=values,state=state)


def prepare(rows):
    planned=set(universe());mapping={};hashes={};states={str(u):{k:0 for k in ('MEDIDA','INVALID_RHO','FALLIDA','AUSENTE')} for u in VISITS}
    for r in rows:
        if not isinstance(r,dict) or r.get('trajectory') not in planned:raise Aborta('ID ajeno o fila inválida')
        t=r['trajectory'];s=int(t.split('_')[2][1:]);k=int(t.split('_')[3][1:])
        if integer(r.get('split'),0,99)!=s or integer(r.get('k'),0,4)!=k:raise Aborta('Identidad split/k incompatible: '+t)
        u=integer(r.get('update'),0,250)
        if u not in VISITS:raise Aborta('Visita no planificada')
        if r.get('estado') not in ('MEDIDA','INVALID_RHO','FALLIDA'):raise Aborta('Estado no reconocido')
        if (t,u) in mapping:raise Aborta('ID/visita duplicados: '+t)
        mapping[t,u]=r
        for key in ('f_sha256','split_sha256'):
            value=r.get(key)
            if digest(value):
                if (s,key) in hashes and hashes[s,key]!=value:raise Aborta('Hash distinto dentro del split: '+key)
                hashes[s,key]=value
    valid={};ledger={};metric_rows={};eligible=[];missing=[]
    for t in universe():
        ledger[t]={}
        for u in VISITS:
            row=mapping.get((t,u))
            if row is None:
                states[str(u)]['AUSENTE']+=1;ledger[t][str(u)]=dict(estado='AUSENTE',valida=False,motivos=['visita ausente']);continue
            v=validate_visit(row,u);valid[t,u]=v;states[str(u)][row['estado']]+=1
            ledger[t][str(u)]=dict(estado=row['estado'],valida=v['valid'],motivos=v['reasons'])
            if v['metric_ok']:metric_rows[t,u]=row
        if all((t,u) in valid and valid[t,u]['valid'] for u in (10,250)):eligible.append(t)
        else:missing.append(t)
    return dict(mapping=mapping,valid=valid,metric_rows=metric_rows,ledger=ledger,states=states,eligible=eligible,missing=missing)


def describe(values):
    a=np.array([v for v in values if v is not None],float)
    return dict(n=len(a),quantiles=dict(zip(('min','p10','p25','p50','p75','p90','max'),np.quantile(a,[0,.1,.25,.5,.75,.9,1]).tolist())) if len(a) else None)
def in_interval(c,lo,hi):return lo<=c and (c<hi or hi==1 and c==1)
def arrays(ids,mapping,measure='rho_caras',visit=10):
    return dict(sp=np.array([int(t.split('_')[2][1:]) for t in ids]),X=np.array([float(mapping[t,visit]['X']) for t in ids]),
                L=np.log([float(mapping[t,10][measure]) for t in ids]),Y=np.log([float(mapping[t,250][measure]) for t in ids]))
def subset_ids(ids,minimum=3):
    counts={s:sum(t.startswith(f'cifar_f1_s{s:04d}_') for t in ids) for s in range(100)}
    splits=[s for s,n in counts.items() if n>=minimum]
    return [t for t in ids if int(t.split('_')[2][1:]) in splits],splits
def point(a,grade=3):
    A=reference();sp,X,L,Y=(a[k] for k in ('sp','X','L','Y'))
    if not len(sp) or np.allclose(A.cen(X,sp),0,atol=1e-8):raise FloatingPointError('X no identificable')
    if not np.ptp(L)>0:raise FloatingPointError('L constante')
    fold={s:i%10 for i,s in enumerate(np.random.default_rng(260010).permutation(np.unique(sp)))}
    z=(L-L.mean())/L.std();B=np.column_stack([A.cen(z**g,sp) for g in range(1,grade+1)])
    xc,yc=A.cen(X,sp),A.cen(Y,sp);fo=np.array([fold[s] for s in sp])
    d=A.D_cv(yc,B,xc,fo);beta=float(np.linalg.lstsq(np.column_stack([B,xc]),yc,rcond=None)[0][-1])
    if not math.isfinite(d) or not math.isfinite(beta):raise FloatingPointError('ajuste no finito')
    return dict(D=float(d),pendiente_X=beta,grado_base=grade,sin_permutaciones=True)
def secondary(ids,mapping,grade=3,measure='rho_caras',visit=10):
    use,splits=subset_ids(ids);out=dict(n_entrada=len(ids),n_usadas=len(use),splits=len(splits),estado='NO_DEFINIDO')
    if len(splits)<20:return dict(out,motivo='menos de20 splits con>=3')
    try:out.update(point(arrays(use,mapping,measure,visit),grade),estado='DESCRIPTIVO')
    except Exception as e:out['motivo']=f'{type(e).__name__}: {e}'
    return out


def analizar(rows,plan,gate_reasons=(),B=5000):
    validar_plan(plan)
    if isinstance(B,bool) or not isinstance(B,int) or B<1:raise Aborta('B de prueba inválido')
    p=prepare(rows);m=p['mapping'];use,splits=subset_ids(p['eligible']);inc=list(gate_reasons)
    if len(p['missing'])>25:inc.append(f'faltantes {len(p["missing"])} >25 de500')
    if len(splits)<80:inc.append(f'splits elegibles {len(splits)} <80 de100')
    distributions={}
    for u in VISITS:
        rr=[r for (t,v),r in p['metric_rows'].items() if v==u]
        distributions[str(u)]={k:describe([number(r[k]) for r in rr]) for k in ('X','R','c','q','tr_M','acc_train','acc_panel','acc_test','ce_train','ce_panel','ce_test')}
        distributions[str(u)]['X_saturadas_atol1e8']=sum(float(r['X'])>=-1e-8 for r in rr)
        distributions[str(u)]['k_star_mal_clasificado']=sum(integer(r['k_star_wrong'],0,1) for r in rr)
    profiles={}
    for name,lo,hi in [('c<.4',0,.4),('.4<=c<.8',.4,.8),('c>=.8',.8,1),('c>=.95',.95,1)]:
        for u in (10,250):
            rr=[(t,r) for (t,v),r in p['metric_rows'].items() if v==u and in_interval(float(r['c']),lo,hi)]
            profiles[f'{name}_u{u}']=dict(n_metricas=len(rr),rho_no_valida=sum(not p['valid'][t,u]['valid'] for t,r in rr))
    out=dict(modo='DESCUBRIMIENTO_DIN_CIFAR_F1',estado_plan=plan['estado'],veredicto='INCONCLUSIVE',motivos_inconclusive=inc,
        planificadas=500,visitas_planificadas=2000,filas_recibidas=len(rows),elegibles_extremos=len(p['eligible']),faltantes=len(p['missing']),
        ids_faltantes=p['missing'],splits_usados=splits,ids_usados=use,elegibles_no_usados_por_split=len(p['eligible'])-len(use),
        estados_por_visita=p['states'],libro_motivos=p['ledger'],distribuciones=distributions,perfil_fallos_rho=profiles,
        primaria=None,secundarios={},propuesta_F2='RESOLVER_LIMITACIONES_SIN_REEMPLAZAR_COHORTE',alcance='Exploratorio: mejora sobre base cúbica concreta; no confirmación, causalidad ni validez frente a toda función de L.')
    if use:
        a=arrays(use,m);A=reference()
        if np.allclose(A.cen(a['X'],a['sp']),0,atol=1e-8):inc.append('X sin variación intra-split: NO_IDENTIFICABLE')
        if np.ptp(a['L'])==0:inc.append('L constante')
        if np.ptp(a['Y'])==0:inc.append('Y constante')
        out['variacion_intra']={k:float(np.sqrt(np.mean(A.cen(a[k],a['sp'])**2))) for k in ('X','L','Y')}
        out['bloques']={str(s):i%10 for i,s in enumerate(np.random.default_rng(260010).permutation(np.array(splits)))}
    if inc:return out
    try:
        prim=A.primaria(a['sp'],a['X'],a['L'],a['Y'],3,260001,B)
        if any(not math.isfinite(float(prim[k])) for k in ('D','p','pendiente_X')):raise FloatingPointError('primaria no finita')
        out['primaria']=prim;out['veredicto']='PASS_DESCRIPTIVO' if prim['p']<.05 and prim['D']>0 and prim['pendiente_X']>0 else 'NOT_MET_DESCRIPTIVO'
    except Exception as e:inc.append(f'primaria no definida: {type(e).__name__}: {e}');return out
    sec=out['secundarios'];sec['rho_vert']=secondary(use,m,measure='rho_vert');sec['base_grado5']=secondary(use,m,grade=5)
    for v in (5,30):sec[f'X{v}']=secondary([t for t in use if p['valid'].get((t,v),{}).get('valid')],m,visit=v)
    for parity in (0,1):sec['pares' if parity==0 else 'impares']=secondary([t for t in use if int(t.split('_')[2][1:])%2==parity],m)
    sec['estratos_c250']={}
    for name,lo,hi in [('bajo',0,.4),('intermedio',.4,.8),('alto',.8,1)]:
        ids=[t for t in use if in_interval(float(m[t,250]['c']),lo,hi)];r=secondary(ids,m)
        cs=describe([float(m[t,250]['c']) for t in ids]);qs=describe([float(m[t,250]['q']) for t in ids])
        r.update(mediana_c=cs['quantiles']['p50'] if cs['n'] else None,mediana_q=qs['quantiles']['p50'] if qs['n'] else None,seleccion_posterior=True)
        sec['estratos_c250'][name]=r
    out['propuesta_F2']='CONSIDERAR_F2_GLOBAL_CON_POTENCIA_Y_AUDITORIA' if out['veredicto']=='PASS_DESCRIPTIVO' else 'NO_ACTIVAR_F2_AUTOMATICAMENTE_NI_DECLARAR_AUSENCIA'
    return out


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('tabla','tabla-sha','plan','plan-sha','resumen','compuerta','compuerta-sha','productor-sha','dataset-sha','out'):parser.add_argument('--'+name,required=True)
    args=parser.parse_args()
    try:
        target=Path(args.out)/'RESULTADO_CIFAR_F1.json'
        if target.exists():raise Aborta('Salida ya existe; no sobrescribir')
        expected=dict(tabla_sha256=args.tabla_sha,plan_sha256=args.plan_sha,compuerta_sha256=args.compuerta_sha,productor_sha256=args.productor_sha,dataset_sha256=args.dataset_sha)
        if any(not digest(v) for v in expected.values()):raise Aborta('SHA de entrada inválido')
        for path,key in [(args.tabla,'tabla_sha256'),(args.plan,'plan_sha256'),(args.compuerta,'compuerta_sha256')]:
            if sha(path)!=expected[key]:raise Aborta('SHA distinto: '+key)
        plan=validar_plan(json_read(args.plan));resumen=json_read(args.resumen);gate=json_read(args.compuerta)
        if not isinstance(resumen,dict):raise Aborta('Resumen no es objeto')
        with open(args.tabla,encoding='utf-8',newline='') as f:
            reader=csv.DictReader(f)
            if reader.fieldnames!=COLUMNS:raise Aborta('Columnas distintas del esquema F1')
            rows=list(reader)
            if any(None in r for r in rows):raise Aborta('Fila CSV con columnas extra')
        result=analizar(rows,plan,integrity(plan,resumen,gate,expected),B=5000)
        result.update(entradas=expected,analisis_C1_sha256=C1_SHA,script_sha256=sha(Path(__file__)),tipo_datos=resumen.get('tipo_datos'))
        text=json.dumps(clean(result),indent=2,ensure_ascii=False,allow_nan=False)+'\n'
        target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('x',encoding='utf-8') as f:f.write(text)
        print(json.dumps(dict(modo=result['modo'],veredicto=result['veredicto'],faltantes=result['faltantes'],salida=str(target)),ensure_ascii=False))
    except (Aborta,OSError,ValueError,TypeError,OverflowError) as e:
        print('ABORTA: '+str(e),file=sys.stderr);return 3
    return 0


if __name__=='__main__':sys.exit(main())
