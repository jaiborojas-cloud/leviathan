"""Validación sintética A1. Nunca abre tablas reales ni ejecuta productores."""
import ast
import copy
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback
import types

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / 'pruebas/results_v1_1'
EXT = ROOT.parent / 'work/din-robusta-pruebas-v1_1'
SCRIPT = HERE / 'analisis_robusta_v1.py'
C1_PATH = ROOT / 'experiments/DIN_borde/C1/analisis_C1_v2.py'
C1_SHA = '8711f468d0df110a94c9cfdf6a1d0777f495537546cdce516929f0cb129858d5'


def load_module(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


M = load_module('robusta_borrador_v1', SCRIPT)


def write(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write('\n')


def guard():
    def audit(event, args):
        if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        p = Path(os.fsdecode(args[0])).resolve()
        if p.is_relative_to(HERE) or p.is_relative_to(EXT) or p == C1_PATH:
            return
        if p.is_relative_to(ROOT/'experiments') or p.is_relative_to(ROOT/'docs/archive') or p.suffix.lower() in ('.csv', '.pt', '.pth', '.npy', '.npz'):
            raise PermissionError('Solo fixtures sintéticos y código C1 por SHA: ' + str(p))
    sys.addaudithook(audit)


def fixture(seed=20261102, n=40, k=5, general=False, gain=.6):
    rng = np.random.default_rng(seed)
    split = np.repeat(np.arange(n), k)
    X = -2 + .2*rng.normal(size=n*k)
    L = rng.normal(size=n*k) if general else np.tile(np.linspace(-1, 1, k), n)
    Y = .3*L + .1*L**2 + gain*(X-X.reshape(n,k).mean(1).repeat(k)) + .08*rng.normal(size=n*k)
    ids = [f'syn_s{s:04d}_k{j}' for s in range(n) for j in range(k)]
    plan = dict(protocolo='DIN-PRIMARIA-ROBUSTA-v1', estado='BORRADOR', tipo_datos='PRUEBA_SINTETICA', n_clases=3,
                universo=[dict(trajectory=t, split=int(s)) for t,s in zip(ids,split)])
    rows = [dict(trajectory=t, split=int(s), estado_10='MEDIDA', estado_final='MEDIDA', error='', X10=float(x),
                 rho_caras_10=float(np.exp(l)), rho_caras_250=float(np.exp(y)), acc_train_final=.9)
            for t,s,x,l,y in zip(ids,split,X,L,Y)]
    return rows, plan


def arrays(rows, plan):
    by = {r['trajectory']:r for r in rows}
    used = [r['trajectory'] for r in plan['universo']]
    sp = np.array([r['split'] for r in plan['universo']], dtype=np.int64)
    return used, sp, np.array([by[t]['X10'] for t in used]), np.log([by[t]['rho_caras_10'] for t in used]), np.log([by[t]['rho_caras_250'] for t in used])


def independent(sp, X, L, Y, B=39, clip=True):
    def center(v, labels):
        out = np.array(v,float).copy()
        for s in sorted(set(labels.tolist())):
            out[labels==s] -= out[labels==s].mean()
        return out
    us = np.unique(sp)
    folds = {s:i%10 for i,s in enumerate(np.random.default_rng(260010).permutation(us))}
    fo = np.array([folds[s] for s in sp])
    z = (L-L.mean())/L.std()
    yc = center(Y,sp)
    def stat(x):
        xc = center(x,sp)
        eb,ef = np.empty(len(x)),np.empty(len(x))
        sb=sf=0.
        for f in range(10):
            tr,te = fo!=f,fo==f
            ztr = z[tr]; zte = np.clip(z[te],ztr.min(),ztr.max()) if clip else z[te]
            train = np.column_stack([center(ztr**p,sp[tr]) for p in (1,2,3)])
            test = np.column_stack([center(zte**p,sp[te]) for p in (1,2,3)])
            fulltrain = np.column_stack([train,xc[tr]])
            fulltest = np.column_stack([test,xc[te]])
            eb[te] = yc[te]-test@np.linalg.lstsq(train,yc[tr],rcond=None)[0]
            ef[te] = yc[te]-fulltest@np.linalg.lstsq(fulltrain,yc[tr],rcond=None)[0]
            sb+=float((eb[te]**2).sum());sf+=float((ef[te]**2).sum())
        return 1-sf/sb,eb,ef
    d,eb,ef=stat(X);rng=np.random.default_rng(260001);null=[]
    for _ in range(B):
        xp=X.copy()
        for s in us:
            ii=np.flatnonzero(sp==s);xp[ii]=X[rng.permutation(ii)]
        null.append(stat(xp)[0])
    return dict(D=d,p=float((1+sum(v>=d-1e-15 for v in null))/(1+B)),e_base=eb,e_completo=ef)


def csv_write(path, rows):
    with path.open('x', encoding='utf-8', newline='') as f:
        writer=csv.DictWriter(f,fieldnames=M.COLUMNS,lineterminator='\n');writer.writeheader();writer.writerows(rows)


def cli_fixture(rows,plan):
    d=EXT/'cli';d.mkdir()
    csv_write(d/'tabla.csv',rows);write(d/'plan.json',plan)
    producer=hashlib.sha256(b'synthetic_producer_only').hexdigest()
    write(d/'gate.json',dict(PASA=True,script_sha256=producer))
    expected=dict(tabla_sha256=M.sha(d/'tabla.csv'),plan_sha256=M.sha(d/'plan.json'),compuerta_sha256=M.sha(d/'gate.json'),productor_sha256=producer)
    write(d/'summary.json',expected)
    fields=dict(tabla=str(d/'tabla.csv'),tabla_sha=expected['tabla_sha256'],plan=str(d/'plan.json'),plan_sha=expected['plan_sha256'],
                compuerta=str(d/'gate.json'),compuerta_sha=expected['compuerta_sha256'],resumen=str(d/'summary.json'),productor_sha=producer)
    return d,fields


def run_cli(d,name,fields,race=False):
    out=d/name
    cmd=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--race-child'] if race else [sys.executable,'-I','-B',str(SCRIPT)]
    for k,v in dict(fields,out=str(out)).items():cmd+=['--'+k.replace('_','-'),v]
    proc=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
    with (d/(name+'_stdout.txt')).open('x') as f:f.write(proc.stdout)
    with (d/(name+'_stderr.txt')).open('x') as f:f.write(proc.stderr)
    return proc,out


def main():
    if len(sys.argv)>1 and sys.argv[1]=='--race-child':
        original=M.analizar
        target=Path(sys.argv[sys.argv.index('--out')+1])/'RESULTADO_ROBUSTA_v1.json'
        def race(*args,**kwargs):
            result=original(*args,**dict(kwargs,B=39));target.parent.mkdir()
            with target.open('x') as f:f.write('RACE_MARKER')
            return result
        M.analizar=race;sys.argv=[str(SCRIPT)]+sys.argv[2:];return M.main()
    for p in [SCRIPT,Path(__file__).resolve(),HERE/'config_BORRADOR_v1.json']:
        assert p.read_bytes()==subprocess.check_output(['git','show','HEAD:'+p.relative_to(ROOT).as_posix()],cwd=ROOT)
    OUT.mkdir(parents=True,exist_ok=False);EXT.mkdir(parents=True,exist_ok=False);guard()
    assert M.sha(C1_PATH)==C1_SHA
    C1=load_module('C1_reference_code_only',C1_PATH)
    base,plan=fixture();csv_write(EXT/'fixture_base.csv',base);write(EXT/'fixture_plan.json',plan)
    records=[]
    def test(name,fn):
        try:r=dict(case=name,ok=True,result=fn())
        except BaseException as e:r=dict(case=name,ok=False,error=f'{type(e).__name__}: {e}',traceback=traceback.format_exc())
        write(OUT/(name+'.json'),r);records.append(r);print(json.dumps(dict(case=name,ok=r['ok'])),flush=True)
    def analyze(rows=base,p=plan):return M.analizar(rows,p,B=39)
    def extract(r):return dict(veredicto=r['veredicto'],faltantes=r['faltantes'],no_aprendio=r['no_aprendio'],motivos=r['motivos_inconclusive'],primaria=r['primaria'],id_max=r['influencia']['id_max'] if r['influencia'] else None,D_sin_max=r['influencia']['D_sin_max'] if r['influencia'] else None)
    baseline=analyze()
    def positive():
        assert baseline['veredicto']=='PASS' and baseline['faltantes']==0 and baseline['n_recortadas']==0
        return extract(baseline)
    test('positivo',positive)
    for i in range(20):
        def equivalence(i=i):
            rows,p=fixture(20261200+i,gain=(i%3-1)*.4)
            ids,sp,X,L,Y=arrays(rows,p)
            np.savez(EXT/f'equivalencia_{i:02d}.npz',sp=sp,X=X,L=L,Y=Y)
            actual,prep=M.primaria(sp,X,L,Y,B=39)
            frozen=C1.primaria(sp,X,L,Y,3,260001,39)
            assert not any(len(r['indices']) for r in prep['recortes'])
            for key in ('D','p','pendiente_X','D_nulo_q95'):assert actual[key]==frozen[key],(key,actual[key],frozen[key])
            own=independent(sp,X,L,Y)
            assert abs(actual['D']-own['D'])<=1e-10 and actual['p']==own['p']
            return dict(C1_exact=True,D_error_independent=abs(actual['D']-own['D']),p_independent_equal=True,
                        D=actual['D'],p=actual['p'],C1_sha256=C1_SHA)
        test(f'equivalencia_C1_{i:02d}',equivalence)
    def general_no_clip():
        rows,p=fixture(20261103,general=True);ids,sp,X,L,Y=arrays(rows,p)
        actual,_=M.primaria(sp,X,L,Y,B=39,recorte=False);old=C1.primaria(sp,X,L,Y,3,260001,39)
        assert all(actual[k]==old[k] for k in ('D','p','pendiente_X','D_nulo_q95'))
        return dict(exact=True,diagnostico_sin_recorte=True)
    test('C1_general_sin_recorte',general_no_clip)
    def learner():
        rows=copy.deepcopy(base);rows[0]['acc_train_final']=.49;rows[0]['rho_caras_10']=0.;rows[0]['error']='SYNTHETIC_FAILURE'
        csv_write(EXT/'no_aprendio.csv',rows)
        with np.errstate(invalid='raise',divide='raise'):r=analyze(rows)
        entry=r['libro_motivos'][rows[0]['trajectory']]
        assert r['faltantes']==1 and r['no_aprendio']==1 and 'NO_APRENDIO' in entry['motivos'] and len(entry['motivos'])==3
        assert rows[0]['trajectory'] not in r['ids_usados'] and len(r['ids_usados'])==199
        return dict(summary=extract(r),entry=entry)
    test('no_aprendio_multiples_causas',learner)
    def boundary():
        counts=[]
        for value in [.5,np.nextafter(.5,0.)]:
            rows=copy.deepcopy(base);rows[0]['acc_train_final']=float(value);r=analyze(rows);counts.append(r['faltantes'])
        assert counts==[0,1]
        return dict(valores=[.5,float(np.nextafter(.5,0.))],faltantes=counts)
    test('umbral_05_exacto',boundary)
    for n in [10,11]:
        def missing(n=n):
            rows=copy.deepcopy(base)
            for row in rows[:n]:row['acc_train_final']=.49
            r=analyze(rows);assert r['faltantes']==n
            assert ('FALTANTES_MAYORES_5_POR_CIENTO' in r['motivos_inconclusive'])==(n==11)
            return extract(r)
        test(f'faltantes_{n}',missing)
    def split_threshold():
        # Universo heterogéneo permite probar el 80 % sin superar el 5 % de faltantes.
        rows,p=fixture(n=40,k=25)
        out=[]
        for nbad in [8,9]:
            remove={r['trajectory'] for r in rows if r['split']<nbad and int(r['trajectory'].rsplit('k',1)[1])>=2}
            # Para que la compuerta de splits se pruebe aislada, esos splits planifican solo tres IDs.
            selected=[r for r in rows if r['split']>=nbad or int(r['trajectory'].rsplit('k',1)[1])<3]
            plan2=dict(p,universo=[dict(trajectory=r['trajectory'],split=r['split']) for r in selected])
            for row in selected:
                if row['trajectory'] in remove:row['acc_train_final']=.49
            r=M.analizar(selected,plan2,B=39)
            assert r['splits_validos']==40-nbad and r['faltantes']==nbad
            assert ('SPLITS_VALIDOS_MENORES_80_POR_CIENTO' in r['motivos_inconclusive'])==(nbad==9)
            out.append(dict(faltantes=r['faltantes'],planificadas=r['planificadas'],splits_validos=r['splits_validos'],motivos=r['motivos_inconclusive']))
        return out
    test('splits_80_por_ciento',split_threshold)
    def extreme():
        rows=copy.deepcopy(base);rows[0]['rho_caras_10']=float(np.exp(-25.))
        csv_write(EXT/'L_extrema.csv',rows)
        r=analyze(rows);assert r['max_abs_z_L']>10 and rows[0]['trajectory'] in r['ids_usados']
        ids,sp,X,L,Y=arrays(rows,plan);_,prepared=M.punto(sp,X,L,Y)
        clip=next(v for v in prepared['recortes'] if 0 in v['indices']);f=clip['bloque']
        tr,te,basis=prepared['cache'][f]
        zc=prepared['z'].copy();zc[te]=np.clip(zc[te],zc[tr].min(),zc[tr].max())
        expected=np.column_stack([M.centrar(zc**p,sp) for p in (1,2,3)])
        assert np.array_equal(basis,expected)
        assert not np.array_equal(basis,M.preparar(sp,X,L,Y,recorte=False)['cache'][f][2])
        own=independent(sp,X,L,Y);actual=r['primaria']
        assert abs(actual['D']-own['D'])<=1e-10 and actual['p']==own['p']
        changed=M.preparar(sp,X[::-1].copy(),L,Y[::-1].copy())
        assert all(np.array_equal(a[2],b[2]) for a,b in zip(prepared['cache'],changed['cache']))
        for trace in prepared['recortes']:
            assert all(trace['z_train_min']<=v<=trace['z_train_max'] for v in trace['z_despues'])
        return dict(max_abs_z_L=r['max_abs_z_L'],n_recortadas=r['n_recortadas'],trace=clip,
                    D_error_independent=abs(actual['D']-own['D']),p_equal=True,base_independiente_de_X_Y=True,conserva_ID=True)
    test('L_extrema_mayor_10',extreme)
    def contribution():
        ids,sp,X,L,Y=arrays(base,plan);actual,prep=M.primaria(sp,X,L,Y,B=39)
        own=independent(sp,X,L,Y);g=own['e_base']**2-own['e_completo']**2
        inf=M.influencia(ids,prep,actual);top=int(np.argmax(g));keep=np.arange(len(X))!=top
        minus=independent(sp[keep],X[keep],L[keep],Y[keep],B=0)
        assert inf['id_max']==ids[top] and abs(inf['D_sin_max']-minus['D'])<=1e-10
        assert np.allclose([r['g'] for r in inf['contribuciones']],g,rtol=0,atol=1e-10)
        assert abs(inf['fraccion_max']-float(g.max()/g.sum()))<=1e-10
        return dict(id_max=inf['id_max'],fraccion=inf['fraccion_max'],D_sin_max=inf['D_sin_max'],max_error_g=float(np.max(np.abs(g-np.array([r['g'] for r in inf['contribuciones']])))))
    test('influencia_independiente',contribution)
    def tie_and_fraction():
        ids,sp,X,L,Y=arrays(base,plan);observed,prep=M.punto(sp,X,L,Y)
        eb=np.zeros(len(X));ef=np.zeros(len(X));eb[:2]=1.
        tie=M.influencia(ids,prep,dict(observed,e_base=eb,e_completo=ef))
        assert tie['id_max']==ids[0] and tie['ids_empatados']==ids[:2]
        eb[:2]=[2.,0.];ef[1]=np.sqrt(3.)
        ratio=M.influencia(ids,prep,dict(observed,e_base=eb,e_completo=ef));assert ratio['fraccion_max']>1
        zero=M.influencia(ids,prep,dict(observed,e_base=np.zeros(len(X)),e_completo=np.zeros(len(X))))
        negative=M.influencia(ids,prep,dict(observed,e_base=np.zeros(len(X)),e_completo=np.ones(len(X))))
        assert zero['fraccion_max'] is None and negative['fraccion_max'] is None
        return dict(tipo='unitario_con_residuos_construidos_no_estadistico_de_cohorte',empates=tie['ids_empatados'],fraccion_mayor_uno=ratio['fraccion_max'],suma_no_positiva_null=True)
    test('empates_fraccion_no_truncada',tie_and_fraction)
    def two_remaining():
        rows,p=fixture(k=3);ids,sp,X,L,Y=arrays(rows,p);observed,prep=M.punto(sp,X,L,Y)
        eb=np.zeros(len(X));eb[0]=1.;ef=np.zeros(len(X))
        inf=M.influencia(ids,prep,dict(observed,e_base=eb,e_completo=ef))
        assert inf['id_max']==ids[0] and ids[1] in inf['ids_sin_max'] and ids[2] in inf['ids_sin_max']
        direct,_=M.punto(sp[1:],X[1:],L[1:],Y[1:]);assert direct['D']==inf['D_sin_max']
        return dict(omision_solo_un_ID=True,n_sin_max=inf['n_sin_max'],D_sin_max=inf['D_sin_max'],split_original_conserva_dos=True)
    test('influencia_conserva_split_con_dos',two_remaining)
    def decision_table():
        cases=[(.1,.01,1.,.01,'PASS'),(.1,.01,1.,0.,'NO_ROBUSTO'),(.1,.01,1.,-.1,'NO_ROBUSTO'),
               (.1,.05,1.,.01,'NOT_MET'),(-.1,.01,1.,.01,'NOT_MET'),(.1,.01,-1.,.01,'NOT_MET'),
               (.1,.01,0.,.01,'NOT_MET'),(.1,.01,1.,None,'INCONCLUSIVE'),(.1,float('nan'),1.,.01,'INCONCLUSIVE')]
        result=[]
        for d,p,b,dm,expected in cases:
            got=M.decidir(d,p,b,dm);assert got==expected;result.append(dict(D=d,p=p if np.isfinite(p) else 'NaN_input',beta=b,D_sin_max=dm,veredicto=got))
        return dict(tipo='casos_minimos_de_regla_no_cohorte',cases=result)
    test('regla_PASS_NO_ROBUSTO',decision_table)
    def degenerate_minus():
        original=M.punto
        def injected(split,X,L,Y,**kwargs):
            if len(X)==len(base)-1:
                raise FloatingPointError('FALLO_NUMERICO_INYECTADO_SOLO_D_SIN_MAX')
            return original(split,X,L,Y,**kwargs)
        M.punto=injected
        try:r=analyze()
        finally:M.punto=original
        assert r['influencia']['D_sin_max'] is None and r['veredicto']=='INCONCLUSIVE'
        assert r['primaria']==baseline['primaria'] and 'FALLO_NUMERICO_INYECTADO' in r['influencia']['error_sin_max']
        return dict(tipo='inyeccion_unitaria_de_fallo_numerico_no_degeneracion_de_cohorte',summary=extract(r),error=r['influencia']['error_sin_max'])
    test('D_sin_max_fallo_inyectado_conservado',degenerate_minus)
    def gate_pipeline():
        original=M.influencia;out=[]
        assert baseline['triple_condicion_original'] is True
        for value in [0.,-.01]:
            def injected(*args,**kwargs):
                result=original(*args,**kwargs)
                assert result['error_sin_max'] is None
                result['D_sin_max']=value
                return result
            M.influencia=injected
            try:r=analyze()
            finally:M.influencia=original
            assert r['veredicto']=='NO_ROBUSTO' and r['primaria']==baseline['primaria']
            assert r['triple_condicion_original'] is True and r['compuerta_influencia'] is False
            out.append(dict(D_sin_max=value,veredicto=r['veredicto'],primaria_identica=True))
        return dict(tipo='inyeccion_unitaria_solo_de_D_sin_max_no_cohorte',cases=out)
    test('NO_ROBUSTO_propagacion_pipeline',gate_pipeline)
    for kind in ['X','L','Y']:
        def constant(kind=kind):
            rows=copy.deepcopy(base)
            for r in rows:
                if kind=='X':r['X10']=-2.
                if kind=='L':r['rho_caras_10']=1.
                if kind=='Y':r['rho_caras_250']=1.
            result=analyze(rows);assert result['veredicto']=='INCONCLUSIVE'
            return extract(result)
        test('constante_'+kind,constant)
    def domain():
        rows=copy.deepcopy(base);rows[0].update(X10='NaN',rho_caras_10=0.,rho_caras_250='inf',acc_train_final=True)
        with np.errstate(divide='raise',invalid='raise'):r=analyze(rows)
        ledger=r['libro_motivos'][rows[0]['trajectory']]
        assert r['faltantes']==1 and len(ledger['motivos'])==4 and r['no_aprendio']==0
        return dict(summary=extract(r),ledger=ledger)
    test('dominio_antes_log_multiples',domain)
    def missing_states():
        rows=copy.deepcopy(base[1:]);rows[0].update(estado_10='INVALID_RHO',error='BUDGET');rows[1]['estado_final']='FALLIDA'
        r=analyze(rows);assert r['faltantes']==3 and all(t not in r['ids_usados'] for t in [base[i]['trajectory'] for i in range(3)])
        return extract(r)
    test('ausentes_y_fallidas',missing_states)
    def csv_order():
        r=analyze(list(reversed(base)));assert r==baseline
        return dict(resultado_exacto=True,orden_universo_preservado=True)
    test('orden_CSV_invariante',csv_order)
    def expect_abort(fn):
        try:fn()
        except M.Aborta as e:return dict(expected='ABORTA',reason=str(e))
        raise AssertionError('Se esperaba ABORTA')
    test('duplicado',lambda:expect_abort(lambda:analyze(base+[base[0]])))
    test('ID_ajeno',lambda:expect_abort(lambda:analyze([dict(base[0],trajectory='foreign')]+base[1:])))
    test('split_distinto',lambda:expect_abort(lambda:analyze([dict(base[0],split=999)]+base[1:])))
    for name,value in [('n_clases',2),('n_clases',True),('universo',[]),('estado','otro')]:
        test('plan_'+name+'_'+str(value),lambda name=name,value=value:expect_abort(lambda:analyze(base,dict(plan,**{name:value}))))
    test('plan_ID_duplicado',lambda:expect_abort(lambda:analyze(base,dict(plan,universo=plan['universo']+[plan['universo'][0]]))))
    d,fields=cli_fixture(base,plan)
    def cli_nominal():
        proc,out=run_cli(d,'nominal',fields);assert proc.returncode==0,proc.stderr
        r=M.json_read(out/'RESULTADO_ROBUSTA_v1.json')
        assert r['veredicto']=='PASS' and r['primaria']['permutaciones']==5000 and r['primaria']['permutaciones_completadas']==5000
        assert r['tipo_datos']=='PRUEBA_SINTETICA'
        return dict(returncode=0,permutations=5000,sha256=M.sha(out/'RESULTADO_ROBUSTA_v1.json'))
    test('CLI_nominal_5000',cli_nominal)
    def marker():
        target=d/'marker'/'RESULTADO_ROBUSTA_v1.json';target.parent.mkdir();target.write_text('PRESERVE_ME')
        proc,_=run_cli(d,'marker',fields);assert proc.returncode==3 and target.read_text()=='PRESERVE_ME'
        return dict(returncode=3,preservado=True)
    test('CLI_salida_exclusiva',marker)
    def race():
        proc,out=run_cli(d,'race',fields,True)
        assert proc.returncode==3 and (out/'RESULTADO_ROBUSTA_v1.json').read_text()=='RACE_MARKER'
        return dict(returncode=3,preservado=True,injection_unitaria=True)
    test('CLI_colision_final',race)
    for name,changes in [('ausente',dict(tabla=str(d/'MISSING'))),('directorio',dict(plan=str(d))),('sha',dict(tabla_sha='0'*64))]:
        def bad(name=name,changes=changes):
            proc,_=run_cli(d,name,dict(fields,**changes));assert proc.returncode==3 and proc.stderr.startswith('ABORTA:')
            return dict(returncode=3)
        test('CLI_'+name,bad)
    def badjson():
        path=d/'invalid.json';path.write_text('{invalid');proc,_=run_cli(d,'badjson',dict(fields,resumen=str(path)))
        assert proc.returncode==3 and proc.stderr.startswith('ABORTA:');return dict(returncode=3)
    test('CLI_JSON_invalido',badjson)
    def real_block():
        p=d/'real_plan.json';write(p,dict(plan,estado='CONGELADO',tipo_datos='COHORTE_NUEVA'))
        proc,_=run_cli(d,'real',dict(fields,plan=str(p),plan_sha=M.sha(p)))
        assert proc.returncode==3 and 'solo pruebas sintéticas' in proc.stderr
        return dict(returncode=3,cohorte_real_bloqueada=True)
    test('CLI_bloquea_real',real_block)
    def bad_link():
        path=d/'bad_summary.json';write(path,dict(M.json_read(d/'summary.json'),tabla_sha256='0'*64))
        proc,out=run_cli(d,'badlink',dict(fields,resumen=str(path)));assert proc.returncode==0
        r=M.json_read(out/'RESULTADO_ROBUSTA_v1.json');assert r['veredicto']=='INCONCLUSIVE' and r['primaria'] is None
        return dict(returncode=0,motivos=r['motivos_inconclusive'])
    test('CLI_enlace_invalido_no_ajusta',bad_link)
    def no_nan_json():
        p=d/'nan_summary.json';p.write_text('{"value":NaN}');proc,_=run_cli(d,'nanjson',dict(fields,resumen=str(p)))
        assert proc.returncode==3 and 'JSON no finito' in proc.stderr;return dict(returncode=3)
    test('CLI_JSON_no_finito',no_nan_json)
    failed=[r['case'] for r in records if not r['ok']]
    write(OUT/'summary.json',dict(status='PASS' if not failed else 'FAIL',cases=len(records),failures=failed,
                                analyst_sha256=M.sha(SCRIPT),tests_sha256=M.sha(Path(__file__)),C1_sha256=C1_SHA,
                                real_data_used=False,training_updates=0,geometry_executed=False))
    with (OUT/'external_manifest.csv').open('x',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['path','bytes','sha256'],lineterminator='\n');writer.writeheader()
        for p in sorted(EXT.rglob('*')):
            if p.is_file():writer.writerow(dict(path=str(p),bytes=p.stat().st_size,sha256=M.sha(p)))
    print(json.dumps(dict(status='PASS' if not failed else 'FAIL',cases=len(records),failures=failed)),flush=True)
    return bool(failed)


if __name__=='__main__':
    sys.exit(main())
