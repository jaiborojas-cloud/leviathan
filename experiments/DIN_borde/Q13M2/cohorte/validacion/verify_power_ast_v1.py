"""Correspondencia estática de potencia y congelación: no importa analistas."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[5]
STAGE=ROOT/'experiments/DIN_borde/Q13M2/cohorte'
BASE=ROOT/'experiments/DIN_borde'
POWER=BASE/'Q13M2/potencia_preparacion/N320_v1'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n):return ast.dump(n,include_attributes=False)
def funcs(p):return {n.name:n for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef)}
def assign(n,k):return isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==k for t in n.targets)
def write(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')


def main():
    rel=Path(__file__).resolve().relative_to(ROOT).as_posix()
    assert Path(__file__).read_bytes()==subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT)
    old=POWER/'sources/Q13M2/analisis_Q13M2.py';new=BASE/'Q13M2/analisis_Q13M2.py'
    assert sha(old)=='2e69516e62b59d90d8abd9d91e1468e538c07b50dc059a6814cd7a20197030fa'
    assert sha(new)=='190e3e878b9e5516d51480cc4f5af79a2ac214f69f94a686e9085fbb868fb2d4'
    assert sha(BASE/'DISENO_DIN_Q13M2_v2_CONGELADO.md')=='5c6c238e6536c24c4188f82d69c947327a590bfdca9d7068519a885e52945814'
    ff={v:funcs(p) for v,p in [('power',old),('frozen',new)]}
    same={k:dump(ff['power'][k])==dump(ff['frozen'][k]) for k in ff['power'] if k not in ['analizar','compatibilidad','main']}
    segments={};primary={}
    for v in ff:
        b=ff[v]['analizar'].body;i=next(i for i,n in enumerate(b) if assign(n,'beta'));j=next(i for i,n in enumerate(b) if assign(n,'ok'))
        segments[v]=[dump(n) for n in b[i:j]]
        primary[v]=[dump(n) for n in ast.walk(ff[v]['analizar']) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='A' and n.func.attr=='primaria']
    const={k:[dump(n) for n in ast.parse(old.read_text()).body if assign(n,k)]==[dump(n) for n in ast.parse(new.read_text()).body if assign(n,k)] for k in ['NIVELES','MANIP','NOMBRES','N_MAX','Q_PRI','Q_SEC','SHAS']}
    deps={p:sha(POWER/'sources'/p)==sha(BASE/p) for p in ['C1/analisis_C1_v2.py','Q13/analisis_Q13.py','Q13DR/analisis_Q13DR.py']}
    good=all(same.values()) and all(const.values()) and all(deps.values()) and segments['power']==segments['frozen'] and primary['power']==primary['frozen']
    result=dict(status='EQUIVALENT_NONDEGENERATE_ESTIMAND' if good else 'STOP_REQUIRES_POWER_REVIEW',power_analyst_sha256=sha(old),frozen_analyst_sha256=sha(new),
        unchanged_functions_AST=same,constants_AST=const,dependencies_SHA=deps,bootstrap_classification_AST_identical=segments['power']==segments['frozen'],
        primary_call_AST_identical=primary['power']==primary['frozen'],power_repeated=False,real_cohort_analysis_executed=False,
        scope='Equivalencia de ruta no degenerada del escenario de potencia; la localización de errores, IO y secundarios sí cambiaron. No identidad completa del programa.')
    (STAGE/'fuentes').mkdir(exist_ok=True)
    with (STAGE/'fuentes/analista_potencia_congelado.diff').open('x') as f:f.write(''.join(difflib.unified_diff(old.read_text().splitlines(True),new.read_text().splitlines(True),fromfile='potencia_N320_2e69516e',tofile='congelado_190e3e87')))
    write(STAGE/'power_frozen_equivalence.json',result)
    print(json.dumps(result,ensure_ascii=False))
    if not good:raise RuntimeError('No preparar productor con equivalencia no demostrada')


if __name__=='__main__':main()
