"""Casos adicionales de los diffs v3; nunca lee tablas reales."""
import ast
import copy
import csv
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
import warnings
import numpy as np
from support import STAGE, CFG, EXTERNAL, write, sha, code_guard, guard, target, v1_functions, clean
import cases_v3 as C


def normal_result(r):
    """Normalización exclusiva de diagnósticos nuevos, no de estadísticas."""
    r=copy.deepcopy(r)
    b=r.get('bootstrap',{})
    if 'fallos_primeros' in b:b['fallos']=b.pop('fallos_primeros')
    b.pop('diferencia_c_L0_L5',None)
    return clean(r)


def compatibility():
    a=target('v2');b=target('v3');rows=[]
    env=dict(np=np,CFG=CFG,C=CFG['levels_c']);v1_functions(('fixture',),env)
    for seed in CFG['compatibility_seeds']:
        g=np.random.default_rng(seed);rr=env['fixture'](20)
        for r in rr:
            # Independent level noise; strong signal ensures the bootstrap is reached.
            r['rho_caras_250']=float(np.exp(np.log(r['rho_caras_250'])+.10*g.normal()))
            r['c250']+=float(.002*g.normal())
        old=a.analizar(copy.deepcopy(rr),20,True,'',**CFG['case_parameters'])
        new=b.analizar(copy.deepcopy(rr),20,True,'',**CFG['case_parameters'])
        rows.append(dict(seed=seed,v2=old,v3=new,equal=normal_result(old)==normal_result(new),
                         reached_bootstrap='IC95_beta' in old.get('bootstrap',{})))
    return dict(cases=rows,all_exact=all(r['equal'] for r in rows),all_nondegenerate=all(r['reached_bootstrap'] for r in rows),
                metadata_only_normalized=['fallos_primeros -> fallos','diferencia_c_L0_L5'])


def structural():
    trees={v:ast.parse((STAGE/f'sources/{v}/Q13DR/analisis_Q13DR.py').read_text()) for v in ('v2','v3')}
    fs={v:{f.name:f for f in t.body if isinstance(f,ast.FunctionDef)} for v,t in trees.items()}
    changed=[n for n in fs['v2'] if ast.dump(fs['v2'][n])!=ast.dump(fs['v3'][n])]
    added=sorted(set(fs['v3'])-set(fs['v2']))
    # Express exactly the three previously inspected diagnostic changes in analizar.
    text=(STAGE/'sources/v2/Q13DR/analisis_Q13DR.py').read_text()
    text=text.replace('fallos_primeros=fallos[:20]','fallos=fallos')
    text=text.replace('rango_c=cs[0] - cs[-1],','rango_c=rango_c(cs), diferencia_c_L0_L5=cs[0] - cs[-1],')
    text=text.replace('margen_dD_equivalencia=0.02 * (cs[0] - cs[-1])','margen_dD_equivalencia=0.02 * rango_c(cs)')
    expected=next(f for f in ast.parse(text).body if isinstance(f,ast.FunctionDef) and f.name=='analizar')
    # All assignments and the returned expression of pendiente remain exact.
    assignments=lambda f:[ast.dump(x) for x in f.body if isinstance(x,(ast.Assign,ast.Return))]
    refs={d:sha(STAGE/f'sources/v2/{d}/{n}')==sha(STAGE/f'sources/v3/{d}/{n}') for d,n in [('C1','analisis_C1_v2.py'),('Q13','analisis_Q13.py')]}
    return dict(changed_functions=changed,added_functions=added,
                analizar_only_declared_diagnostics=ast.dump(expected)==ast.dump(fs['v3']['analizar']),
                pendiente_assignments_and_return_unchanged=assignments(fs['v2']['pendiente'])==assignments(fs['v3']['pendiente']),
                reused_sources_identical=refs)


def bootstrap_constant_c():
    """Point is identifiable; bootstrap samples without its pivotal split are not."""
    rr=C.balanced([.1]*6)
    for r in rr:
        s,l=r['split'],r['nivel']
        if s>=40:r['c250']=.04 if s<119 else CFG['levels_c'][l] if s==119 else .9
    old_rng=np.random.default_rng;draws=[]
    class Spy:
        def __init__(self,rng):self.rng=rng
        def choice(self,*a,**kw):
            d=self.rng.choice(*a,**kw);draws.append(d.copy());return d
    def factory(seed=None,*a,**kw):
        g=old_rng(seed,*a,**kw);return Spy(g) if seed==860001 else g
    np.random.default_rng=factory
    try:r=C.execute(rr,200,NB=300)
    finally:np.random.default_rng=old_rng
    errors=[]
    for i,draw in enumerate(draws):
        med=[float(np.median([.04 if s<119 else CFG['levels_c'][l] if s==119 else .9 for s in draw for k in range(5)])) for l in range(6)]
        if max(med)==min(med):errors.append(i)
    actual=r.get('bootstrap',{}).get('fallos',[])
    return dict(target_result=r,expected_constant_c_indices=errors,draw_calls=len(draws),
                exactly_saved_indices=errors==[x['replica'] for x in actual],
                all_errors_are_constant_c=all('c constante' in x['error'] for x in actual))


def ranges_slopes():
    a=target('v2');b=target('v3');D=[.01,.03,-.02,.06,.02,.05];records=[]
    for c in itertools.permutations(CFG['levels_c']):
        x=a.pendiente(D,c);y=b.pendiente(D,c)
        records.append(dict(c=c,v2=x,v3=y,equal=x==y,range=b.rango_c(c),oracle=max(c)-min(c)))
    invalid=[]
    for vec in [[.1]*6,[.2]*6,[.4]*6,[.7]*6,[float('nan')]+CFG['levels_c'][1:],[float('inf')]+CFG['levels_c'][1:]]:
        try:b.pendiente(D,vec);invalid.append(dict(c=vec,rejected=False))
        except FloatingPointError as e:invalid.append(dict(c=vec,rejected=True,error=str(e)))
    return dict(permutations=records,all_exact=all(x['equal'] and x['range']==x['oracle'] for x in records),invalid=invalid,
                all_invalid_rejected=all(x['rejected'] for x in invalid))


def plans():
    m=C.R
    base=dict(n_splits=20,niveles=[dict(nivel=l,eps=e) for l,e in enumerate(m.EPS)],ids_sha256='0'*64)
    tests=[]
    def add(name,p,expected):
        try:answer=m.validar_plan(p);actual='ACCEPT';error=None
        except m.Aborta as e:actual='ABORTA';answer=None;error=str(e)
        except Exception as e:actual='CRASH';answer=None;error=repr(e)
        tests.append(dict(name=name,expected=expected,actual=actual,n=answer,error=error,ok=actual==expected))
    for n in [1,20,400,0,-1,401,True,False,20.,'20',None,10**400]:
        p=copy.deepcopy(base);p['n_splits']=n;add('n_'+str(n)[:32],p,'ACCEPT' if type(n)is int and 1<=n<=400 else 'ABORTA')
    for i in range(6):
        for j,e in enumerate([True,False,'0',None,float('nan'),float('inf'),10**400,{},[],m.EPS[i],np.nextafter(float(m.EPS[i]),np.inf)]):
            p=copy.deepcopy(base);p['niveles'][i]['eps']=e
            add(f'eps_l{i}_j{j}',p,'ACCEPT' if j==9 else 'ABORTA')
    for p in [None,[],1,'x'] :add('root_'+str(type(p).__name__),p,'ABORTA')
    for vals in [[],base['niveles'][:5],base['niveles'][::-1],None,{}]:
        p=copy.deepcopy(base);p['niveles']=vals;add('levels_'+str(len(tests)),p,'ABORTA')
    return dict(cases=tests,all_ok=all(t['ok'] for t in tests))


def cli_bad_bytes(name,which,payload=None,directory=False):
    rr=C.ENV['fixture']();out=EXTERNAL/'diffs_cli'/name;out.mkdir(parents=True,exist_ok=False)
    table=out/'table.csv';plan=out/'plan.json';summary=out/'summary.json'
    with table.open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rr[0]),lineterminator='\n');w.writeheader();w.writerows(rr)
    write(plan,dict(n_splits=20,niveles=[dict(nivel=l,eps=e) for l,e in enumerate(C.R.EPS)],ids_sha256=hashlib.sha256('\n'.join(C.R.universo(20)).encode()).hexdigest()))
    paths=dict(tabla=table,plan=plan,resumen=summary)
    # A separate input replaces its canonical counterpart; canonical files are never overwritten.
    if directory:
        pp=out/'entrada_directorio';pp.mkdir();paths[which]=pp
    elif payload is not None:
        pp=out/'entrada_malformada';pp.write_bytes(payload);paths[which]=pp
    st=sha(paths['tabla']) if paths['tabla'].is_file() else sha(table)
    sp=sha(paths['plan']) if paths['plan'].is_file() else sha(plan)
    write(summary,dict(tabla_sha256=st,plan_sha256=sp))
    cmd=[sys.executable,'-I',str(STAGE/'sources/v3/Q13DR/analisis_Q13DR.py'),'--tabla',str(paths['tabla']),'--tabla-sha',st,'--plan',str(paths['plan']),'--plan-sha',sp,'--resumen',str(paths['resumen']),'--out',str(out/'result')]
    p=subprocess.run(cmd,capture_output=True,text=True)
    (out/'stdout.txt').write_text(p.stdout);(out/'stderr.txt').write_text(p.stderr)
    return dict(returncode=p.returncode,stderr=p.stderr,
                ok=p.returncode==3 and p.stderr.startswith('ABORTA:') and 'Traceback' not in p.stderr,fixture_dir=str(out))


def main():
    code_guard();guard();started=time.monotonic();out=STAGE/'results/diffs';out.mkdir(parents=True,exist_ok=False)
    C.R=target();C.ENV=dict(np=np,copy=copy,CFG=CFG,C=CFG['levels_c'],R=C.R,execute=C.execute,cli=C.cli,median_mismatch=C.median_capture)
    v1_functions(('fixture','trace','build_cases'),C.ENV)
    cases=[('structural',structural),('compatibility_10',compatibility),('bootstrap_constant_c',bootstrap_constant_c),
           ('slopes_and_ranges',ranges_slopes),('plans',plans)]
    for name,field,payload,directory in [
        ('table_directory','tabla',None,True),('summary_directory','resumen',None,True),
        ('table_bad_utf8','tabla',b'\xff\xfe',False),('plan_bad_utf8','plan',b'\xff\xfe',False),('summary_bad_utf8','resumen',b'\xff\xfe',False),
        ('plan_bad_json','plan',b'{bad json',False),('summary_bad_json','resumen',b'{bad json',False),
        ('table_csv_field_too_large','tabla',b'trajectory\n'+b'a'*(csv.field_size_limit()+1),False)]:
        cases.append((name,lambda name=name,field=field,payload=payload,directory=directory:cli_bad_bytes(name,field,payload,directory)))
    records=[]
    for name,fn in cases:
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('always')
            try:r=dict(case=name,status='RETURNED',result=fn())
            except Exception as e:r=dict(case=name,status='EXCEPTION',error=repr(e),traceback=traceback.format_exc())
            r['warnings']=[dict(type=w.category.__name__,message=str(w.message)) for w in ws]
        write(out/(name+'.json'),r);records.append(r);print(json.dumps(dict(case=name,status=r['status'])),flush=True)
    write(out/'summary.json',dict(cases=records,seconds=time.monotonic()-started,synthetic_only=True))


if __name__=='__main__':main()
