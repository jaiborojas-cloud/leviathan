"""Pruebas sintéticas del borrador F1; sin CIFAR/Wine, entrenamiento o geometría."""
import argparse
import ast
import re
import contextlib
import copy
import csv
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OUT=HERE/'revision_v2/pruebas'
EXT=ROOT.parent/'work/din-cifar-f1-pruebas-v2'
SCRIPT=HERE/'analisis_F1_v2.py'
spec=importlib.util.spec_from_file_location('cifar_f1_analyst',SCRIPT)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)


def h(s):return hashlib.sha256(str(s).encode()).hexdigest()
def write(p,x):
    with p.open('x',encoding='utf-8') as f:json.dump(M.clean(x),f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
def guard():
    allowed={ROOT/'experiments/DIN_borde/C1/analisis_C1_v2.py',HERE/'analisis_F1_v1.py',HERE/'plan_F1_BORRADOR_v1.json'}
    def audit(event,args):
        if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
        p=Path(os.fsdecode(args[0])).resolve()
        if p.is_relative_to(HERE) or p.is_relative_to(EXT) or p in allowed:return
        if p.is_relative_to(ROOT/'experiments') or p.is_relative_to(ROOT/'docs/archive') or p.suffix.lower() in ('.csv','.npz','.npy','.pt','.pth'):
            raise PermissionError('Prueba F1: solo sintéticos y código C1 por SHA: '+str(p))
    sys.addaudithook(audit)
def fixture(seed=2010001,gain=.75):
    rng=np.random.default_rng(seed);X=-3+.3*rng.normal(size=(100,5));L=rng.normal(size=(100,5));Y=.4*L+.1*L**2+gain*(X-X.mean(1,keepdims=True))+.08*rng.normal(size=(100,5));rows=[]
    for s in range(100):
        for k in range(5):
            for u in M.VISITS:
                r={key:'' for key in M.COLUMNS};x=float(X[s,k]-(.1 if u==5 else .2 if u==30 else 0))
                r.update(trajectory=f'cifar_f1_s{s:04d}_k{k}',split=s,k=k,update=u,estado='MEDIDA',X=x,R=x-.25,
                    c=.2 if s<33 else .6 if s<67 else .9,q=.01,tr_M=1.,acc_train=.9,acc_panel=15/27,acc_test=14/27,
                    ce_train=.1,ce_panel=.9,ce_test=1.,k_star=k,k_star_wrong=k%2,frac_panel_wrong=12/27,
                    model_sha256=h(f'm_{s}_{k}_{u}'),f_sha256=h(f'f_{s}'),split_sha256=h(f's_{s}'),rho_status='NO_SOLICITADA')
                if u in (10,250):
                    rho=float(np.exp(L[s,k] if u==10 else Y[s,k]));set_rho(r,rho)
                rows.append(r)
    return rows
def set_rho(r,value):
    r.update(rho_caras=value,rho_vert=1.1*value,rho_status='VALID_NUMERICAL_ESTIMATE',rho_evaluations=100,rho_seconds=.1,diagnostic_sha256=h('diag_'+r['trajectory']+'_'+str(r['update'])))
    for key in ('rho_caras','rho_vert'):
        for term in ('quad_error','prefix_bound','tail_bound'):r[key+'_'+term]=abs(float(r[key]))*1e-9
def independent(sp,X,L,Y,B):
    def center(a):
        b=np.array(a,float).copy()
        for s in sorted(set(sp.tolist())):b[sp==s]-=b[sp==s].mean(axis=0)
        return b
    us=np.unique(sp);fold={s:i%10 for i,s in enumerate(np.random.default_rng(260010).permutation(us))};fo=np.array([fold[s] for s in sp])
    z=(L-L.mean())/np.std(L);C=center(np.column_stack([z,z*z,z*z*z]));yc=center(Y)
    def stat(x):
        xc=center(x);F=np.column_stack([C,xc]);sb=sf=0.
        for k in range(10):
            train=fo!=k;test=~train
            b=np.linalg.lstsq(C[train],yc[train],rcond=None)[0];f=np.linalg.lstsq(F[train],yc[train],rcond=None)[0]
            sb+=np.square(yc[test]-C[test]@b).sum();sf+=np.square(yc[test]-F[test]@f).sum()
        return float(1-sf/sb)
    D=stat(X);rng=np.random.default_rng(260001);null=[]
    for b in range(B):
        xp=X.copy()
        for s in us:
            ii=np.flatnonzero(sp==s);xp[ii]=X[rng.permutation(ii)]
        null.append(stat(xp))
    return dict(D=D,p=float((1+np.sum(np.array(null)>=D-1e-15))/(1+B)))
def metadata(plan):
    expected={k:h(k) for k in ('tabla_sha256','plan_sha256','productor_sha256','compuerta_sha256','dataset_sha256')}
    summary=dict(expected,fuentes={k:v['sha256'] for k,v in plan['fuentes'].items()},versiones=plan['versiones'],tipo_datos='PRUEBA_SINTETICA')
    gate=dict(veredicto='PASA',checks={k:True for k in M.GATE_CHECKS},peor_error_relativo=0.,fuentes={'core':plan['fuentes']['core']['sha256'],'rho_v2':plan['fuentes']['rho']['sha256']},versiones=dict(plan['versiones'],python=sys.version.split()[0]))
    return expected,summary,gate
def cli_fixture(rows,plan):
    d=EXT/'cli';d.mkdir();table=d/'table.csv';p=d/'plan.json';g=d/'gate.json';rs=d/'summary.json'
    with table.open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=M.COLUMNS,lineterminator='\n');w.writeheader();w.writerows(rows)
    e,summary,gate=metadata(plan);write(p,plan);write(g,gate);e.update(tabla_sha256=M.sha(table),plan_sha256=M.sha(p),compuerta_sha256=M.sha(g));summary.update(e);write(rs,summary)
    return d,dict(tabla=str(table),tabla_sha=e['tabla_sha256'],plan=str(p),plan_sha=e['plan_sha256'],resumen=str(rs),compuerta=str(g),compuerta_sha=e['compuerta_sha256'],productor_sha=e['productor_sha256'],dataset_sha=e['dataset_sha256'])
def run_cli(d,name,fields,child=False):
    out=d/name;args=[]
    for k,v in dict(fields,out=str(out)).items():args+=['--'+k.replace('_','-'),v]
    command=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--race-child'] if child else [sys.executable,'-I','-B',str(SCRIPT)]
    proc=subprocess.run(command+args,cwd=ROOT,text=True,capture_output=True)
    path=d/(name+'_stdout.txt');path.write_text(proc.stdout);(d/(name+'_stderr.txt')).write_text(proc.stderr)
    return proc,out


def main():
    if len(sys.argv)>1 and sys.argv[1]=='--race-child':
        original=M.analizar;out=Path(sys.argv[sys.argv.index('--out')+1]);out.mkdir()
        def race(*a,**kw):
            r=original(*a,**dict(kw,B=39))
            with (out/'RESULTADO_CIFAR_F1.json').open('x') as f:f.write('RACE_MARKER')
            return r
        M.analizar=race;sys.argv=[str(SCRIPT)]+sys.argv[2:];sys.exit(M.main())
    for p in [SCRIPT,Path(__file__).resolve(),HERE/'plan_F1_BORRADOR_v2.json']:
        assert p.read_bytes()==subprocess.check_output(['git','show','HEAD:'+p.relative_to(ROOT).as_posix()],cwd=ROOT)
    OUT.mkdir(parents=True,exist_ok=False);EXT.mkdir(parents=True,exist_ok=False);guard()
    plan=M.json_read(HERE/'plan_F1_BORRADOR_v2.json');base=fixture();records=[]
    def test(name,fn):
        try:r=dict(case=name,ok=True,result=fn())
        except BaseException as e:r=dict(case=name,ok=False,error=f'{type(e).__name__}: {e}',traceback=traceback.format_exc())
        safe=re.sub('[^A-Za-z0-9_.-]+','_',name)[:72]+'_'+h(name)[:10]
        write(OUT/(safe+'.json'),r);records.append(r);print(json.dumps(dict(case=name,ok=r['ok'])),flush=True)
    def analyze(rows):return M.analizar(rows,plan,B=39)
    def expect_error(fn):
        try:fn()
        except M.Aborta as e:return dict(expected_exception='Aborta',message=str(e))
        raise AssertionError('Se esperaba Aborta')
    def changed(predicate,fn):
        rr=copy.deepcopy(base)
        for r in rr:
            if predicate(r):fn(r)
        return rr
    def summary(r):return {k:r[k] for k in ('veredicto','faltantes','elegibles_extremos','primaria','motivos_inconclusive')}
    old_spec=importlib.util.spec_from_file_location('cifar_f1_v1_reference',HERE/'analisis_F1_v1.py')
    OLD=importlib.util.module_from_spec(old_spec);old_spec.loader.exec_module(OLD)
    old_plan=OLD.json_read(HERE/'plan_F1_BORRADOR_v1.json')
    baseline=analyze(base)
    previous=OLD.analizar(base,old_plan,B=39)
    assert baseline['primaria']==previous['primaria']
    def positive():
        assert baseline['veredicto']=='PASS_DESCRIPTIVO' and baseline['faltantes']==0 and len(baseline['ids_usados'])==500
        assert all(r['estado']=='DESCRIPTIVO' for r in baseline['secundarios']['estratos_c250'].values())
        return summary(baseline)
    test('positivo',positive)
    for i in range(20):
        def compare(i=i):
            rows=fixture(2010100+i,gain=(i%3-1)*.5);r=analyze(rows);p=M.prepare(rows);a=M.arrays(p['eligible'],p['mapping']);own=independent(a['sp'],a['X'],a['L'],a['Y'],39)
            assert r['primaria'] is not None and abs(own['D']-r['primaria']['D'])<=1e-10 and own['p']==r['primaria']['p']
            old=OLD.analizar(rows,old_plan,B=39)
            assert old['primaria']==r['primaria'] and old['veredicto']==r['veredicto']
            return dict(primary_v1_identical=True,D_error=abs(own['D']-r['primaria']['D']),p_equal=True,veredicto_observado=r['veredicto'],null_or_alternative='sin promesa de veredicto inferencial para una muestra aleatoria')
        test(f'equivalencia_{i:02d}',compare)
    def direct():
        p=M.prepare(base);a=M.arrays(p['eligible'],p['mapping']);x=M.reference().primaria(a['sp'],a['X'],a['L'],a['Y'],3,260001,39)
        assert x==baseline['primaria'];return dict(reference_SHA=M.C1_SHA,exact=True)
    test('C1_directo',direct)
    def negative():
        r=analyze(fixture(gain=-.75));assert r['primaria']['D']>0 and r['primaria']['pendiente_X']<0 and r['veredicto']=='NOT_MET_DESCRIPTIVO';return summary(r)
    test('pendiente_negativa',negative)
    for kind in ['X','L','Y','saturada']:
        def constant(kind=kind):
            rows=copy.deepcopy(base)
            for r in rows:
                if kind in ['X','saturada'] and r['update']==10:r.update(X=-2.-.001*r['split'] if kind=='X' else 0.,R=-3.)
                if kind=='L' and r['update']==10:set_rho(r,1.)
                if kind=='Y' and r['update']==250:set_rho(r,1.)
            q=analyze(rows);assert q['veredicto']=='INCONCLUSIVE' and q['primaria'] is None;return summary(q)
        test('constante_'+kind,constant)
    for n in [25,26]:
        def missing(n=n):
            selected=set(M.universe()[:n]);rows=changed(lambda r:r['trajectory'] in selected and r['update']==10,lambda r:r.update(estado='INVALID_RHO',error='SYNTHETIC_BUDGET',rho_status='INCONCLUSIVE_BUDGET',rho_reason='SEARCH_BUDGET_EXHAUSTED'))
            q=analyze(rows);assert q['faltantes']==n
            assert (q['veredicto']=='INCONCLUSIVE')==(n==26)
            assert all(q['libro_motivos'][t]['10']['estado']=='INVALID_RHO' for t in selected)
            return summary(q)
        test(f'faltantes_{n}',missing)
    def only5():
        rows=changed(lambda r:r['update']==5,lambda r:r.update(estado='FALLIDA',error='SYNTHETIC_VISIT5_FAILURE'))
        q=analyze(rows);assert q['primaria']==baseline['primaria'] and q['faltantes']==0 and q['secundarios']['X5']['estado']=='NO_DEFINIDO';return summary(q)
    test('fallo5_no_contamina',only5)
    def physical():
        rows=changed(lambda r:True,lambda r:r.update(c=1.,q=0.,acc_panel=0.,frac_panel_wrong=1.,k_star_wrong=1))
        q=analyze(rows);assert q['primaria']==baseline['primaria'] and q['faltantes']==0;return summary(q)
    test('c1_panel_erroneo_sin_filtro',physical)
    def bad_domains():
        rows=copy.deepcopy(base)
        for r in rows:
            if r['trajectory']=='cifar_f1_s0000_k0' and r['update']==10:r.update(X='NaN',c=1.1,q=-1.,rho_caras=0.,rho_vert=float('inf'))
        with np.errstate(divide='raise',invalid='raise'):q=analyze(rows)
        reasons=q['libro_motivos']['cifar_f1_s0000_k0']['10']['motivos'];assert q['faltantes']==1 and len(reasons)>=5
        return dict(reasons=reasons,primary_defined=q['primaria'] is not None)
    test('dominios_multiples_sin_log_invalido',bad_domains)
    def audit_failure():
        rows=changed(lambda r:r['update']==10,lambda r:r.update(rho_caras_tail_bound=float(r['rho_caras'])*.01))
        q=analyze(rows);assert q['faltantes']==500 and q['primaria'] is None;return summary(q)
    test('auditoria_rho_no_rescata',audit_failure)
    def timeout():
        rows=changed(lambda r:r['update']==250,lambda r:r.update(estado='INVALID_RHO',error='OUTER_TIMEOUT_120S',rho_reason='OUTER_TIMEOUT',rho_status='INCONCLUSIVE_BUDGET'))
        q=analyze(rows);assert q['faltantes']==500 and q['primaria'] is None;return summary(q)
    test('timeout_no_imputa',timeout)
    def smallstrata():
        rows=changed(lambda r:True,lambda r:r.update(c=.9 if r['k']<2 else .2))
        q=analyze(rows);assert q['primaria']==baseline['primaria'] and q['secundarios']['estratos_c250']['alto']['estado']=='NO_DEFINIDO';return dict(primary_same=True,alto=q['secundarios']['estratos_c250']['alto'])
    test('estrato_pequeno_no_contamina',smallstrata)
    def straddling():
        values=([.1,.2,.3,.85,.95],[.1,.2,.5,.85,.95],[.1,.2,.8,.9,1.])
        rows=changed(lambda r:True,lambda r:r.update(c=values[0 if r['split']<33 else 1 if r['split']<67 else 2][r['k']]))
        q=analyze(rows);strata=q['secundarios']['estratos_c250'];assignment=q['secundarios']['asignacion_estratos_c250']
        assert q['primaria']==baseline['primaria']
        assert [strata[n]['n_splits'] for n in ['bajo','intermedio','alto']]==[33,34,33]
        assert [strata[n]['n_usadas'] for n in ['bajo','intermedio','alto']]==[165,170,165]
        independent_groups={s:[r for r in rows if r['split']==s and r['update']==250] for s in range(100)}
        independent_assignment={str(s):'bajo' if np.median([r['c'] for r in rr])<.4 else 'intermedio' if np.median([r['c'] for r in rr])<.8 else 'alto' for s,rr in independent_groups.items()}
        assert assignment['estrato_por_split']==independent_assignment
        all_ids=[];all_splits=[]
        for name,r in strata.items():
            assert r['splits']==r['n_splits']==len(r['ids_splits'])
            expected=[t for t in M.universe() if independent_assignment[str(int(t.split('_')[2][1:]))]==name]
            assert r['ids_trayectorias']==expected
            assert all(n==5 for n in r['n_elegibles_por_split'].values())
            own=M.point(M.arrays(expected,M.prepare(rows)['mapping']))
            assert r['D']==own['D'] and r['pendiente_X']==own['pendiente_X']
            all_ids+=r['ids_trayectorias'];all_splits+=r['ids_splits']
        assert len(all_ids)==len(set(all_ids))==500 and len(all_splits)==len(set(all_splits))==100
        return dict(primary_unchanged=True,estratos=strata,asignacion=assignment,independent_assignment_equal=True)
    test('v2_splits_atraviesan_cortes',straddling)
    def boundaries():
        rows=changed(lambda r:True,lambda r:r.update(c=.4 if r['split']<33 else .8 if r['split']<67 else 1.))
        q=analyze(rows);s=q['secundarios']['estratos_c250']
        assert q['primaria']==baseline['primaria'] and s['bajo']['n_splits']==0
        assert s['intermedio']['ids_splits']==list(range(33)) and s['alto']['ids_splits']==list(range(33,100))
        assert s['bajo']['estado']=='NO_DEFINIDO' and s['bajo']['ids_trayectorias']==[]
        return dict(estratos=s,primary_unchanged=True)
    test('v2_mediana_empates_y_uno',boundaries)
    def incomplete():
        rows=changed(lambda r:True,lambda r:r.update(c=.1 if r['split']==0 else .6))
        for r in rows:
            if r['split']==0 and r['update']==250:r['c']=[1.,.1,.3,.5,.9][r['k']]
            if r['split']==1 and r['update']==250:r['c']=[.1,.2,.8,.9,1.][r['k']]
            if r['update']==10 and ((r['split']==0 and r['k']==0) or (r['split']==1 and r['k']>=3) or (r['split']==2 and r['k']>=2)):
                r.update(estado='INVALID_RHO',error='SYNTHETIC',rho_status='INCONCLUSIVE_BUDGET')
        q=analyze(rows);s=q['secundarios']['estratos_c250'];a=q['secundarios']['asignacion_estratos_c250']
        assert q['faltantes']==6 and q['primaria'] is not None and q['primaria']==OLD.analizar(rows,old_plan,B=39)['primaria']
        assert s['intermedio']['mediana_c_por_split']['0']==.4 and s['intermedio']['n_elegibles_por_split']['0']==4
        assert s['bajo']['mediana_c_por_split']['1']==.2 and s['bajo']['n_elegibles_por_split']['1']==3
        assert a['splits_fuera_primaria']==[2] and '2' not in a['estrato_por_split']
        kept=[t for r in s.values() for t in r['ids_trayectorias']]
        assert set(kept)==set(q['ids_usados']) and len(kept)==492
        return dict(faltantes=q['faltantes'],ids_usados=len(kept),estratos=s,asignacion=a)
    test('v2_mediana_elegibles_3_4_sin_imputar',incomplete)
    for count in [19,20]:
        def threshold(count=count):
            rows=changed(lambda r:True,lambda r:r.update(c=.2 if r['split']<count else .6))
            q=analyze(rows);r=q['secundarios']['estratos_c250']['bajo']
            assert q['primaria']==baseline['primaria'] and r['n_splits']==count and r['n_usadas']==5*count
            assert r['ids_splits']==list(range(count)) and len(r['ids_trayectorias'])==5*count
            assert r['estado']==('NO_DEFINIDO' if count==19 else 'DESCRIPTIVO')
            return dict(primary_unchanged=True,estrato_bajo=r)
        test(f'v2_estrato_{count}_splits',threshold)
    for winner in ['rho_caras','rho_vert']:
        for invalid in [None,'','NaN','inf',-1.]:
            def invalid_quad(winner=winner,invalid=invalid):
                rows=changed(lambda r:r['trajectory']=='cifar_f1_s0000_k0' and r['update']==10,lambda r:r.update({winner+'_quad_error':invalid}))
                q=analyze(rows);r=q['libro_motivos']['cifar_f1_s0000_k0']['10']
                assert q['faltantes']==1 and not r['valida'] and winner+': auditoría no válida' in r['motivos']
                assert q['primaria']==OLD.analizar(rows,old_plan,B=39)['primaria']
                return dict(winner=winner,invalid=invalid,motivos=r['motivos'],primary_v1_identical=True)
            test('v2_quad_'+winner+'_'+str(invalid),invalid_quad)
    def own_lengths():
        r=next(copy.deepcopy(r) for r in base if r['update']==10)
        r.update(rho_caras=1.,rho_vert=10.,rho_caras_quad_error=1e-6,rho_caras_prefix_bound=1e-6,rho_caras_tail_bound=0.,
            rho_vert_quad_error=1e-6*10.,rho_vert_prefix_bound=1e-6*10.,rho_vert_tail_bound=0.)
        assert M.validate_visit(r,10)['valid']
        accepted=M.validate_visit(r,10)
        for key in ['rho_caras_quad_error','rho_caras_prefix_bound','rho_vert_quad_error','rho_vert_prefix_bound']:
            bad=copy.deepcopy(r);bad[key]=np.nextafter(float(r[key]),np.inf)
            assert not M.validate_visit(bad,10)['valid']
        # Entre longitudes: no comparar el error de vértices con caras ni viceversa.
        assert M.validate_visit(dict(r,rho_vert_quad_error=5e-6),10)['valid']
        assert not M.validate_visit(dict(r,rho_caras_quad_error=5e-6),10)['valid']
        return dict(limite_aceptado=accepted,exceso_ulp_invalido=True,longitud_de_cada_ganador=True)
    test('v2_tolerancia_longitud_ganador',own_lengths)
    def ast_regression():
        def functions(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef)}
        old=functions(HERE/'analisis_F1_v1.py');new=functions(SCRIPT)
        allowed={'validar_plan','analizar'}
        changed_functions=[k for k in old if old[k]!=new[k]]
        assert set(changed_functions)==allowed and set(new)-set(old)=={'strata_split'}
        before=ast.parse((HERE/'analisis_F1_v1.py').read_text());after=ast.parse(SCRIPT.read_text())
        def primary_body(tree):
            f=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='analizar')
            # Todo hasta los secundarios permanece idéntico, incluida primaria e inclusión.
            result=[]
            for n in f.body:
                if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='sec' for t in n.targets):break
                result.append(ast.dump(n,include_attributes=False))
            return result
        assert primary_body(before)==primary_body(after)
        return dict(changed_functions=changed_functions,new_function='strata_split',all_other_functions_identical=True,primary_and_gates_identical=True,
            v1_sha256=M.sha(HERE/'analisis_F1_v1.py'),v2_sha256=M.sha(SCRIPT))
    test('v2_AST_primaria_validacion_sin_cambios',ast_regression)
    test('duplicado',lambda:expect_error(lambda:analyze(base+[base[0]])))
    test('ID_ajeno',lambda:expect_error(lambda:analyze(base+[dict(base[0],trajectory='foreign')])) )
    test('visita_ajena',lambda:expect_error(lambda:analyze([dict(base[0],update=11)]+base[1:])))
    test('identidad_split',lambda:expect_error(lambda:analyze([dict(base[0],split=9)]+base[1:])))
    test('hash_f_discordante',lambda:expect_error(lambda:analyze([dict(base[0],f_sha256=h('different'))]+base[1:])))
    for field,value in [('n_splits',True),('n_splits',101),('seed_bases',{}),('estado','FREEZE'),('entrenamiento',dict(plan['entrenamiento'],lr=.001))]:
        test('plan_'+field+'_'+str(value)[:12],lambda field=field,value=value:expect_error(lambda:M.validar_plan(dict(plan,**{field:value}))))
    def links():
        e,s,g=metadata(plan);assert M.integrity(plan,s,g,e)==[]
        reasons=M.integrity(plan,dict(s,tabla_sha256=h('other')),dict(g,veredicto='NO_PASA'),e)
        assert len(reasons)>=2
        q=M.analizar(base,plan,reasons,B=39);assert q['primaria'] is None;return dict(reasons=reasons)
    test('enlaces_y_compuerta',links)
    def real_block():
        e,s,g=metadata(plan);s['tipo_datos']='CIFAR3_DESCUBRIMIENTO';return expect_error(lambda:M.integrity(plan,s,g,e))
    test('borrador_bloquea_datos_reales',real_block)
    d,fields=cli_fixture(base,plan)
    def cli_ok():
        proc,out=run_cli(d,'valid',fields);assert proc.returncode==0,proc.stderr
        value=M.json_read(out/'RESULTADO_CIFAR_F1.json');assert value['modo']=='DESCUBRIMIENTO_DIN_CIFAR_F1' and value['primaria']['permutaciones']==5000 and value['veredicto']=='PASS_DESCRIPTIVO'
        return dict(returncode=0,permutations=5000,output_sha256=M.sha(out/'RESULTADO_CIFAR_F1.json'),fixture=str(out))
    test('CLI_nominal_5000',cli_ok)
    def marker():
        out=d/'marker';out.mkdir();target=out/'RESULTADO_CIFAR_F1.json';target.write_text('PRESERVE_ME');before=M.sha(target)
        proc,_=run_cli(d,'marker',fields);assert proc.returncode==3 and proc.stderr.startswith('ABORTA:') and M.sha(target)==before
        return dict(returncode=3,marker_preserved=True)
    test('CLI_marker',marker)
    def race():
        proc,out=run_cli(d,'race',fields,child=True);assert proc.returncode==3 and proc.stderr.startswith('ABORTA:') and (out/'RESULTADO_CIFAR_F1.json').read_text()=='RACE_MARKER'
        return dict(returncode=3,marker_preserved=True,in_memory_injection=True,B_operational=39)
    test('CLI_colision_final',race)
    for name,changes in [('tabla_ausente',dict(tabla=str(d/'MISSING'))),('plan_directorio',dict(plan=str(d))),('SHA_distinto',dict(tabla_sha=h('wrong')))]:
        def bad_input(name=name,changes=changes):
            proc,out=run_cli(d,name,dict(fields,**changes));assert proc.returncode==3 and proc.stderr.startswith('ABORTA:') and 'Traceback' not in proc.stderr
            return dict(returncode=3)
        test('CLI_'+name,bad_input)
    def badjson():
        p=d/'bad.json';p.write_text('{invalid');proc,out=run_cli(d,'bad_json',dict(fields,resumen=str(p)))
        assert proc.returncode==3 and proc.stderr.startswith('ABORTA:');return dict(returncode=3)
    test('CLI_JSON_invalido',badjson)
    failures=[r['case'] for r in records if not r['ok']]
    write(OUT/'summary.json',dict(status='PASS' if not failures else 'FAIL',cases=len(records),failures=failures,analyst_sha256=M.sha(SCRIPT),tests_sha256=M.sha(Path(__file__)),real_data_used=False,training_updates=0,geometry_executed=False))
    with (OUT/'external_manifest.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['path','bytes','sha256'],lineterminator='\n');w.writeheader()
        for p in sorted(EXT.rglob('*')):
            if p.is_file():w.writerow(dict(path=str(p),bytes=p.stat().st_size,sha256=M.sha(p)))
    print(json.dumps(dict(status='PASS' if not failures else 'FAIL',cases=len(records),failures=failures)),flush=True)
    return 1 if failures else 0


if __name__=='__main__':sys.exit(main())
