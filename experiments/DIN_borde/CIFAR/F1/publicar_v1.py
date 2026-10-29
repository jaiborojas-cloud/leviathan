"""Empaquetado portable e integridad de pruebas existentes; no ejecuta analista."""
import csv
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
BASE=ROOT/'experiments/DIN_borde/CIFAR'
RAW=HERE/'pruebas/results_v1'
PUB=HERE/'pruebas/publicacion_v1'
EXCLUDED={'manifest.csv','manifest.sha256','PUBLICACION_v1.sha256'}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
    def bad(x):raise ValueError('JSON no finito: '+x)
    return json.loads(p.read_text(),parse_constant=bad)
def write(p,x):
    with p.open('x',encoding='utf-8') as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')


def main():
    rel=Path(__file__).resolve().relative_to(ROOT).as_posix()
    assert Path(__file__).read_bytes()==subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT)
    summary=load(RAW/'summary.json');assert summary['status']=='PASS' and summary['cases']==54 and summary['failures']==[]
    assert summary['analyst_sha256']==sha(HERE/'analisis_F1_v1.py') and summary['tests_sha256']==sha(HERE/'pruebas_F1_v1.py')
    assert summary['real_data_used'] is False and summary['training_updates']==0 and summary['geometry_executed'] is False
    prov=load(HERE/'fuentes/provenance.json')
    assert all(sha(ROOT/x['path'])==x['sha256'] for x in prov['references'] if 'snapshot' not in x)
    assert all(sha(HERE/x['snapshot'])==x['sha256'] for x in prov['references'] if 'snapshot' in x)
    assert all(sha(ROOT/x['path'])==x['sha256'] for x in prov['sources'].values())
    plan=load(HERE/'plan_F1_BORRADOR_v1.json');assert plan['estado']=='BORRADOR'
    ids=[f'cifar_f1_s{s:04d}_k{k}' for s in range(100) for k in range(5)]
    assert len(ids)==len(set(ids))==500 and hashlib.sha256('\n'.join(ids).encode()).hexdigest()==plan['ids_sha256']
    with (RAW/'external_manifest.csv').open() as f:external=list(csv.DictReader(f))
    assert all(sha(Path(x['path']))==x['sha256'] for x in external)
    PUB.mkdir(exist_ok=False);members=[];cases=[]
    for p in sorted(RAW.iterdir()):
        if not p.is_file():continue
        if p.name in ('summary.json','external_manifest.csv'):safe=p.name
        else:safe=re.sub('[^A-Za-z0-9_.-]+','_',p.stem)[:72]+'_'+sha(p)[:10]+p.suffix
        with (PUB/safe).open('xb') as f:f.write(p.read_bytes())
        assert sha(PUB/safe)==sha(p)
        members.append(dict(raw_name=p.name,published_name=safe,sha256=sha(p)))
        if p.suffix=='.json' and p.name!='summary.json':
            r=load(p);assert r['ok'] is True
            cases.append(dict(case=r['case'],published_file=safe,sha256=sha(p)))
    assert len(cases)==54
    with (PUB/'indice_casos.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['case','published_file','sha256'],lineterminator='\n');w.writeheader();w.writerows(cases)
    write(PUB/'mapeo_portable.json',dict(sin_cambios_de_bytes=True,miembros=members))
    comparisons=[load(RAW/f'equivalencia_{i:02d}.json')['result'] for i in range(20)]
    maxerr=max(x['D_error'] for x in comparisons);assert maxerr<=1e-10 and all(x['p_equal'] for x in comparisons)
    cli=load(RAW/'CLI_nominal_5000.json')['result'];assert cli['permutations']==5000
    report=f'''# Pruebas sintéticas del borrador CIFAR F1 v1

**54/54 PASS**, sin fallos inesperados. No se ejecutaron imágenes, entrenamiento, geometría ni cohortes reales. Son pruebas del software, no resultados de F1 ni una validación nominal de potencia/tamaño.

- Analista SHA `{summary['analyst_sha256']}`.
- Pruebas SHA `{summary['tests_sha256']}`.
-20 tablas independientes: error máximo de D `{maxerr:.17g}`, p idéntico con las mismas permutaciones. Incluyen coeficientes negativos, cero y positivos; no se exige un veredicto inferencial a cada nulo aleatorio.
- Equivalencia exacta con llamada C1 por SHA y prueba CLI nominal con5000 permutaciones.
- Límites25/26 faltantes, X/L/Y constantes y saturación, c=1/panel erróneo sin filtro, fallos5 sin contaminación, presupuesto/timeout/auditoría rho, dominios múltiples sin log inválido, estrato pequeño, IDs/visitas/hash f, plan y metadatos.
- CLI: JSON estricto, salida inicial/final exclusiva, lecturas ausentes/directorio/SHA incorrecto/JSON inválido y bloqueo de tipo real mientras el plan es BORRADOR.

[Resumen](pruebas/publicacion_v1/summary.json), [índice de54 casos](pruebas/publicacion_v1/indice_casos.csv), [manifest externo](pruebas/publicacion_v1/external_manifest.csv). Las copias publicadas son byte a byte de los resultados crudos; [enmienda de empaquetado](ENMIENDA_PUBLICACION_v1.md) y mapeo conservan los nombres originales no portables. No se modifica ni repite una prueba para publicarla.
'''
    with (HERE/'PRUEBAS_F1_v1.md').open('x',encoding='utf-8') as f:f.write(report)
    changes=subprocess.check_output(['git','diff','--name-only',prov['base_main']],cwd=ROOT,text=True).splitlines()
    assert all(x.startswith('experiments/DIN_borde/CIFAR/F1/') or x=='experiments/DIN_borde/CIFAR/DISENO_CIFAR_F1_BORRADOR_v1.md' for x in changes)
    write(HERE/'verification.json',dict(status='PASS_DRAFT_SYNTHETIC_ONLY',design_state='BORRADOR',design_frozen_for_cohort=False,
        tests_passed=54,independent_tables=20,max_D_error=maxerr,p_identical=True,nominal_CLI_permutations=5000,
        analyst_sha256=summary['analyst_sha256'],tests_sha256=summary['tests_sha256'],C1_sha256=prov['sources']['C1']['sha256'],
        real_F1_data_read=False,training_updates=0,geometry_executed=False,producer_created=False,F2_N_selected=False,
        portable_copies_byte_identical=True,external_members_verified=len(external),python=platform.python_version()))
    files=sorted(p for p in HERE.rglob('*') if p.is_file() and not p.is_relative_to(RAW) and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.name not in EXCLUDED)
    design=BASE/'DISENO_CIFAR_F1_BORRADOR_v1.md';files.append(design)
    assert not [p for p in files if p.suffix.lower() in ('.npz','.npy','.pt','.pth','.zip')]
    assert all(not re.search('[<>:"|?*]',p.relative_to(BASE).as_posix()) for p in files)
    manifest=[dict(path=Path(__import__('os').path.relpath(p,HERE)).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in files]
    with (HERE/'manifest.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['path','bytes','sha256'],lineterminator='\n');w.writeheader();w.writerows(manifest)
    with (HERE/'manifest.sha256').open('x') as f:
        for r in manifest:f.write(r['sha256']+'  '+r['path']+'\n')
    with (HERE/'PUBLICACION_v1.sha256').open('x') as f:
        for n in ['manifest.csv','manifest.sha256']:f.write(sha(HERE/n)+'  '+n+'\n')
    broken=[]
    for p in list(HERE.glob('*.md'))+[design]:
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' in link:continue
            dest=link.split('#')[0]
            if dest and not (p.parent/dest).exists():broken.append([p.name,link])
    assert not broken,broken
    assert all(sha(HERE/r['path'])==r['sha256'] for r in manifest)
    print(json.dumps(dict(status='PASS',published_members=len(manifest),cases=54,design_still_draft=True)))


if __name__=='__main__':main()
