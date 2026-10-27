"""Planes/dominio/CLI; fixtures sintéticos,LS real solo como referencia."""
import copy
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import traceback
from support import STAGE,CFG,PROV,EXT,LS,write,sha,code_guard,guard,target,fixture


def schema_cases(m):
    base=dict(n_splits=320,niveles=[dict(nivel=a,brazo=b,dosis=c) for a,b,c in m.NIVELES],ids_sha256='x')
    cases=[]
    def check(name,p,expected):
        try:value=m.validar_plan(p);actual='ACCEPT';error=None
        except m.Aborta as e:value=None;actual='ABORTA';error=str(e)
        except Exception as e:value=None;actual='CRASH';error=repr(e)
        cases.append(dict(name=name,expected=expected,actual=actual,value=value,error=error,ok=actual==expected))
    for n in (1,200,320,321,0,-1,True,False,320.,'320',None,10**400):
        p=copy.deepcopy(base);p['n_splits']=n;check('N_'+str(n)[:30],p,'ACCEPT' if type(n)is int and 1<=n<=320 else 'ABORTA')
    for i in range(11):
        for field,value in [('nivel','LS1'),('nivel',None),('brazo','LS'),('dosis',True),('dosis',None),('dosis',float('nan')),('dosis',float('inf')),('dosis',10**400)]:
            p=copy.deepcopy(base);p['niveles'][i][field]=value;check(f'level{i}_{field}_{len(cases)}',p,'ABORTA')
    for nv in [base['niveles'][:10],base['niveles'][::-1],None,{},base['niveles']+[base['niveles'][0]]]:
        p=copy.deepcopy(base);p['niveles']=nv;check('levels_'+str(len(cases)),p,'ABORTA')
    for p in (None,[],1,'bad'):check('root_'+str(len(cases)),p,'ABORTA')
    return dict(cases=cases,all_ok=all(r['ok'] for r in cases))


def cli(m,name,mode):
    out=EXT/'cli'/name;out.mkdir(parents=True,exist_ok=False);rows=fixture(1)
    for r in rows:r['X10']=-2.
    table=out/'table.csv';plan=out/'plan.json';summary=out/'summary.json';result_dir=out/'result';result_dir.mkdir()
    with table.open('x',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    p=dict(n_splits=1,niveles=[dict(nivel=a,brazo=b,dosis=c) for a,b,c in m.NIVELES],ids_sha256=hashlib.sha256('\n'.join(m.universo(1)).encode()).hexdigest())
    if mode=='invalid_plan':p['n_splits']=321
    write(plan,p);write(summary,dict(tabla_sha256=sha(table),plan_sha256=sha(plan)))
    args=dict(tabla=table,plan=plan,resumen=summary,tabla_ls=LS)
    if mode in ('missing_table','table_dir'):args['tabla']=out/'absent.csv' if mode=='missing_table' else out
    if mode in ('missing_plan','plan_dir'):args['plan']=out/'absent.json' if mode=='missing_plan' else out
    if mode=='missing_summary':args['resumen']=out/'absent_summary.json'
    if mode=='bad_utf8_plan':
        bad=out/'invalid_utf8';bad.write_bytes(b'\xff\xfe');args['plan']=bad
    if mode=='bad_json_summary':
        bad=out/'invalid_json';bad.write_bytes(b'{bad');args['resumen']=bad
    existing=result_dir/'RESULTADO_Q13M2.json'
    marker=b'{"existing_result":"PRESERVE_ME"}\n'
    if mode=='output_collision':existing.write_bytes(marker)
    cmd=[sys.executable,'-I','-B',str(STAGE/'sources/target/Q13M2/analisis_Q13M2.py'),'--tabla',str(args['tabla']),'--tabla-sha',sha(table),
         '--plan',str(args['plan']),'--plan-sha',sha(args['plan']) if args['plan'].is_file() else sha(plan),
         '--resumen',str(args['resumen']),'--tabla-ls',str(LS),'--tabla-ls-sha',PROV['LS_reference']['sha256'],'--out',str(result_dir)]
    proc=subprocess.run(cmd,capture_output=True,text=True)
    (out/'stdout.txt').write_text(proc.stdout);(out/'stderr.txt').write_text(proc.stderr)
    ab=proc.returncode==3 and proc.stderr.startswith('ABORTA:') and 'Traceback' not in proc.stderr
    parsed=json.loads(existing.read_text()) if proc.returncode==0 else None
    return dict(mode=mode,returncode=proc.returncode,strict_aborta=ab,stderr=proc.stderr,result=parsed,
                output_marker_preserved=existing.exists() and existing.read_bytes()==marker if mode=='output_collision' else None,
                output_file_SHA=sha(existing) if existing.exists() else None,JSON_strict=bool(parsed is not None and 'NaN' not in existing.read_text() and 'Infinity' not in existing.read_text()),fixture_dir=str(out))


def main():
    code_guard();guard();out=STAGE/'results/validation';out.mkdir(parents=True,exist_ok=False);m=target()
    write(out/'schema.json',schema_cases(m));records=[]
    for mode in ('missing_table','table_dir','missing_plan','plan_dir','missing_summary','bad_utf8_plan','bad_json_summary','invalid_plan','output_collision'):
        try:rec=dict(case=mode,status='RETURNED',result=cli(m,mode,mode))
        except Exception as e:rec=dict(case=mode,status='EXCEPTION',error=repr(e),traceback=traceback.format_exc())
        write(out/(mode+'.json'),rec);records.append(rec);print(json.dumps(dict(case=mode,status=rec['status'])),flush=True)
    pure=dict(constant_c_rejected=True,constants=[],rango_invertido=m.DR.rango_c([.3,.35,.4,.45,.5,.6]),
              spearman_constante=m.DR.spearman([.1]*6,[.9,.7,.6,.55,.5,.4]),q975=m.q(list(range(1001)),m.Q_PRI),
              limpio_JSON=json.dumps(m.DR.limpio(dict(a=float('nan'),b=float('inf'))),allow_nan=False))
    for c in (.1,.2,.3,.4,.5,.7,.9):
        try:m.DR.pendiente([1,2,3,4,5,6],[c]*6);pure['constant_c_rejected']=False;pure['constants'].append(dict(c=c,rejected=False))
        except FloatingPointError:pure['constants'].append(dict(c=c,rejected=True))
    write(out/'pure_rules.json',pure);write(out/'summary.json',dict(cases=records,pure=pure))


if __name__=='__main__':main()
