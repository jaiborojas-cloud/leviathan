"""Diff/AST y vinculación documental; no datos de cohortes."""
import ast
import json
from support import STAGE,sha,write,code_guard,guard


def dump(n):return ast.dump(n,include_attributes=False)
def functions(p):return {x.name:x for x in ast.parse(p.read_text()).body if isinstance(x,ast.FunctionDef)}
def assigned(n,name):return isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets)


def main():
    code_guard();guard();out=STAGE/'results/static';out.mkdir(parents=True,exist_ok=False)
    paths={v:STAGE/f'sources/{v}/Q13M2/analisis_Q13M2.py' for v in ('v1','v2')}
    ff={v:functions(p) for v,p in paths.items()}
    unchanged={k:dump(ff['v1'][k])==dump(ff['v2'][k]) for k in ff['v1'] if k not in ['analizar','main','compatibilidad']}
    segment={}
    for v in paths:
        b=ff[v]['analizar'].body;i=next(i for i,n in enumerate(b) if assigned(n,'beta'));j=next(i for i,n in enumerate(b) if assigned(n,'ok'))
        segment[v]=[dump(n) for n in b[i:j]]
    deps={r:sha(STAGE/'sources/v1'/r)==sha(STAGE/'sources/v2'/r) for r in ['C1/analisis_C1_v2.py','Q13/analisis_Q13.py','Q13DR/analisis_Q13DR.py']}
    primary=[]
    for v in paths:
        primary.append([dump(n) for n in ast.walk(ff[v]['analizar']) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='A' and n.func.attr=='primaria'])
    const={}
    for name in ['NIVELES','MANIP','NOMBRES','N_MAX','Q_PRI','Q_SEC','SHAS','LS_TABLA_SHA']:
        const[name]=[dump(n) for n in ast.parse(paths['v1'].read_text()).body if assigned(n,name)]==[dump(n) for n in ast.parse(paths['v2'].read_text()).body if assigned(n,name)]
    report=STAGE/'sources/v2/Q13M2/PRUEBAS_Q13M2_v2_2026-10-27.md';evidence=json.loads((STAGE/'sources/v2/Q13M2/pruebas_Q13M2.json').read_text());tests=STAGE/'sources/v2/Q13M2/pruebas_Q13M2.py'
    cases=[v for v in evidence.values() if isinstance(v,dict) and 'esperado' in v and 'ok' in v]
    hashes=dict(analyst=sha(paths['v2']),tests=sha(tests))
    f03=dict(hashes=hashes,JSON_linked=evidence['analisis_sha256']==hashes['analyst'] and evidence['pruebas_sha256']==hashes['tests'],
        report_linked=all(h in report.read_text() for h in hashes.values()),cases_recorded=len(cases),all_recorded_ok=all(x['ok'] for x in cases),
        pure_rules=evidence['reglas_puras'],failures=evidence['fallos'],author_suite_executed_here=False)
    tol_nodes=[n for n in ast.walk(ast.parse(tests.read_text())) if isinstance(n,ast.Compare) and any(isinstance(k,ast.Constant) and k.value==1e-12 for k in n.comparators)]
    design=STAGE/'sources/v2/DISENO_DIN_Q13M2_BORRADOR_v2.md'
    leftovers=[dict(line=i,text=t.strip()) for i,t in enumerate(design.read_text().splitlines(),1) if 'exactamente 0.07692466151365258' in t]
    output=dict(functions_unchanged=unchanged,bootstrap_and_classification_AST_identical=segment['v1']==segment['v2'],dependencies_unchanged=deps,
        primary_call_AST_identical=primary[0]==primary[1],constants_identical=const,F03=f03,F04_test_uses_1e_12=bool(tol_nodes),
        documentary_exact_wording_remaining=leftovers,MC_repeated=False)
    output['PASS_static_and_evidence']=all(unchanged.values()) and output['bootstrap_and_classification_AST_identical'] and all(deps.values()) and all(const.values()) and output['primary_call_AST_identical'] and f03['JSON_linked'] and f03['report_linked'] and len(cases)==25 and f03['all_recorded_ok'] and f03['pure_rules']==dict(n=18,fallos=[]) and f03['failures']==[] and bool(tol_nodes)
    write(out/'results.json',output);print(json.dumps(output,ensure_ascii=False))


if __name__=='__main__':main()
