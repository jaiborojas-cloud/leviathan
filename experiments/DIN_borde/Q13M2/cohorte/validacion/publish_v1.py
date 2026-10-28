"""Cierre de integridad del paquete; no entrena ni ejecuta analistas."""
import ast
import csv
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess

ROOT=Path(__file__).resolve().parents[5]
STAGE=ROOT/'experiments/DIN_borde/Q13M2/cohorte'
PLAN_COMMIT='b75448d28a41753f2287b44d79db9febc6c95434'
PRODUCER_COMMIT='0c00de9362252aa3f51aa2e619b4b36848870ed4'
MANIFEST_NAMES={'manifest.csv','manifest.sha256','PUBLICACION_v2.sha256'}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
    def bad(x):raise ValueError('JSON no estricto: '+x)
    return json.loads(p.read_text(),parse_constant=bad)
def write(p,x):
    with p.open('x',encoding='utf-8') as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')


def main():
    self_path=Path(__file__).resolve();rel=self_path.relative_to(ROOT).as_posix()
    assert self_path.read_bytes()==subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT)
    prov=load(STAGE/'fuentes/provenance.json');validation=load(STAGE/'validacion/results_v1/verification.json')
    power=load(STAGE/'power_frozen_equivalence.json');plan=load(STAGE/'q13m2_plan.json');script=STAGE/'scripts/cohorte_v2.py'
    assert validation['status']=='PASS' and validation['training_updates']==validation['new_cohort_trajectories_trained']==0
    assert validation['no_cohort_CLI_executed'] and not validation['native_Windows_tested']
    assert power['status']=='EQUIVALENT_NONDEGENERATE_ESTIMAND' and power['frozen_analyst_sha256']=='190e3e878b9e5516d51480cc4f5af79a2ac214f69f94a686e9085fbb868fb2d4'
    assert all(sha(ROOT/x['path'])==x['sha256'] for x in prov['sources'])
    assert sha(STAGE/'q13m2_plan.json')==validation['plan_sha256']==prov['plan_sha256']
    assert sha(script)==validation['script_sha256']==(STAGE/'scripts/cohorte_v2.sha256').read_text().split()[0]
    constants={n.targets[0].id:ast.literal_eval(n.value) for n in ast.parse(script.read_text()).body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ['LEVELS','COLUMNS','PLAN_SHA','VERSIONS']}
    assert plan['n_splits']==320 and plan['niveles']==constants['LEVELS'] and len(plan['niveles'])==11 and len(constants['COLUMNS'])==15
    ids=[f'q13m2_{l["nivel"]}_s{s:04d}_k{k}' for l in plan['niveles'] for s in range(320) for k in range(5)]
    assert len(ids)==len(set(ids))==17600 and hashlib.sha256('\n'.join(ids).encode()).hexdigest()==plan['ids_sha256']
    # Comprobar identidad de las dosis con la expresión del analista, sin importarlo.
    tree=ast.parse((ROOT/'experiments/DIN_borde/Q13M2/analisis_Q13M2.py').read_text());node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='NIVELES' for t in n.targets))
    doses={c.elt.elts[0].values[0].value:ast.literal_eval(c.generators[0].iter.args[0]) for c in ast.walk(node.value) if isinstance(c,ast.ListComp)}
    for arm in ('LP','WD'):assert [l['dosis'] for l in plan['niveles'] if l['brazo']==arm]==doses[arm]
    assert plan['niveles'][0]==dict(nivel='A0',brazo='A0',dosis=0)
    subprocess.run(['git','merge-base','--is-ancestor',PLAN_COMMIT,PRODUCER_COMMIT],cwd=ROOT,check=True)
    assert subprocess.run(['git','cat-file','-e',PLAN_COMMIT+':'+script.relative_to(ROOT).as_posix()],cwd=ROOT,capture_output=True).returncode!=0
    assert subprocess.check_output(['git','show',PRODUCER_COMMIT+':'+script.relative_to(ROOT).as_posix()],cwd=ROOT)==script.read_bytes()
    assert subprocess.check_output(['git','show',PLAN_COMMIT+':'+(STAGE/'q13m2_plan.json').relative_to(ROOT).as_posix()],cwd=ROOT)==(STAGE/'q13m2_plan.json').read_bytes()
    with (STAGE/'validacion/results_v1/external_manifest.csv').open() as f:external=list(csv.DictReader(f))
    assert all(sha(Path(x['path']))==x['sha256'] for x in external)
    gate=load(STAGE/'validacion/results_v1/COMPUERTA_linux_sin_entrenar.json')
    assert gate['PASA'] and gate['entrenamientos']==0 and len(gate['reconstrucciones'])==3 and all(x['relative_M_error']==0 and x['f_identical'] for x in gate['reconstrucciones'])
    changes=subprocess.check_output(['git','diff','--name-only',prov['base_main']],cwd=ROOT,text=True).splitlines()
    assert all(x.startswith(STAGE.relative_to(ROOT).as_posix()+'/') for x in changes)
    assert not list(STAGE.rglob('*.npz')) and not list(STAGE.rglob('*.pt')) and not (STAGE/'q13m2_cohorte.csv').exists()
    text=(STAGE/'EJECUCION_WINDOWS_v2.md').read_text()
    assert PRODUCER_COMMIT in text and sha(script) in text and 'D:\\RIPG_DATA\\venv_q13' in text and 'D:\\RIPG_DATA\\DIN_Q13M2_v2' in text and 'D:\\leviathan-q13' in text
    assert '--limite 33' in text and text.count('--limite 5900')==3 and 'venv_torch' not in text
    write(STAGE/'verification.json',dict(status='PASS_PREPARATION_ONLY',plan_commit=PLAN_COMMIT,producer_commit=PRODUCER_COMMIT,
        plan_sha256=sha(STAGE/'q13m2_plan.json'),script_sha256=sha(script),ids_sha256=plan['ids_sha256'],planned_trajectories=17600,
        columns=constants['COLUMNS'],versions=constants['VERSIONS'],power_matches_frozen_nondegenerate_estimand=True,power_repeated=False,
        training_updates=0,cohort_trajectories_trained=0,cohort_CLI_executed=False,real_cohort_table_published=False,analyst_executed=False,
        gate_Linux_exact_reconstructions=3,native_Windows_tested=False,Windows_gate_required=True,plan_published_before_producer=True,
        artificial_IO_fixtures_only=True,external_members_verified=len(external),only_new_cohort_package_files=True,python=platform.python_version()))
    files=sorted(p for p in STAGE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.name not in MANIFEST_NAMES)
    for p in files:
        if p.suffix=='.json':load(p)
    members=[dict(path=p.relative_to(STAGE).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in files]
    with (STAGE/'manifest.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['path','bytes','sha256'],lineterminator='\n');w.writeheader();w.writerows(members)
    with (STAGE/'manifest.sha256').open('x') as f:
        for x in members:f.write(x['sha256']+'  '+x['path']+'\n')
    with (STAGE/'PUBLICACION_v2.sha256').open('x') as f:
        for name in ['manifest.csv','manifest.sha256']:f.write(sha(STAGE/name)+'  '+name+'\n')
    broken=[]
    for p in STAGE.glob('*.md'):
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' not in link and link.split('#')[0] and not (p.parent/link.split('#')[0]).exists():broken.append([p.name,link])
    assert not broken,broken
    assert all(sha(STAGE/x['path'])==x['sha256'] for x in members)
    print(json.dumps(dict(status='PASS',members=len(members),plan_sha256=sha(STAGE/'q13m2_plan.json'),script_sha256=sha(script),cohort_trained=False)))


if __name__=='__main__':main()
