"""Verifica y publica la revisión v2 ya probada; no ejecuta análisis ni medidas."""
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
REV=HERE/'revision_v2'
OUT=REV/'pruebas'
BASE='cb89f0a4a9ccbc6107b64e1daa07c05fcb67ba85'
CLOSING={'manifest.csv','manifest.sha256','PUBLICACION_v2.sha256'}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,value):
    with p.open('x',encoding='utf-8') as f:
        json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
def text(p,value):
    with p.open('x',encoding='utf-8') as f:f.write(value)


def main():
    own=Path(__file__).resolve()
    assert own.read_bytes()==subprocess.check_output(['git','show','HEAD:'+own.relative_to(ROOT).as_posix()],cwd=ROOT)
    summary=read(OUT/'summary.json')
    assert summary['status']=='PASS' and summary['cases']==71 and summary['failures']==[]
    assert summary['analyst_sha256']==sha(HERE/'analisis_F1_v2.py')
    assert summary['tests_sha256']==sha(HERE/'pruebas_F1_v2.py')
    assert summary['real_data_used'] is False and summary['geometry_executed'] is False and summary['training_updates']==0
    records=[(p,read(p)) for p in sorted(OUT.glob('*.json')) if p.name!='summary.json']
    assert len(records)==71 and all(r['ok'] is True for _,r in records)
    cases={r['case']:r for _,r in records}
    with (OUT/'indice_casos.csv').open('x',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['case','file','sha256'],lineterminator='\n');writer.writeheader()
        for p,r in records:writer.writerow(dict(case=r['case'],file=p.name,sha256=sha(p)))
    with (OUT/'external_manifest.csv').open() as f:external=list(csv.DictReader(f))
    assert all(sha(Path(r['path']))==r['sha256'] for r in external)
    raw_log=Path('/tmp/din-cifar-f1-pruebas-v2.log')
    with (OUT/'console.log').open('xb') as f:f.write(raw_log.read_bytes())
    assert read(OUT/'summary.json')['cases']==71
    previous_manifest=list(csv.DictReader((HERE/'manifest.csv').open()))
    assert all(sha(HERE/r['path'])==r['sha256'] for r in previous_manifest)
    previous_closure=[]
    for name in ['manifest.csv','manifest.sha256','PUBLICACION_v1.sha256']:
        p=HERE/name
        assert p.read_bytes()==subprocess.check_output(['git','show',BASE+':'+p.relative_to(ROOT).as_posix()],cwd=ROOT)
        previous_closure.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
    changes=subprocess.check_output(['git','diff','--name-status',BASE],cwd=ROOT,text=True).splitlines()
    assert all(r.startswith('A\t') for r in changes),changes
    assert all(r.split('\t')[1].startswith('experiments/DIN_borde/CIFAR/F1/') or r.split('\t')[1]=='experiments/DIN_borde/CIFAR/DISENO_CIFAR_F1_BORRADOR_v2.md' for r in changes)
    plan=read(HERE/'plan_F1_BORRADOR_v2.json');old=read(HERE/'plan_F1_BORRADOR_v1.json')
    assert plan['estado']=='BORRADOR'
    normalized=json.loads(json.dumps(plan));normalized['protocol']=old['protocol'];del normalized['analisis']['c_strata_assignment']
    assert normalized==old
    comparisons=[cases[f'equivalencia_{i:02d}']['result'] for i in range(20)]
    assert all(r['p_equal'] is True and r['primary_v1_identical'] is True for r in comparisons)
    max_error=max(r['D_error'] for r in comparisons)
    ast=cases['v2_AST_primaria_validacion_sin_cambios']['result']
    assert ast['primary_and_gates_identical'] and ast['all_other_functions_identical']
    assert cases['CLI_nominal_5000']['result']['permutations']==5000
    verification=dict(status='PASS_DRAFT_V2_SYNTHETIC_ONLY',design_state='BORRADOR',cohort_design_frozen=False,
        base_v1=BASE,tests_passed=71,previous_cases_reexecuted=54,new_cases=17,independent_tables=20,
        max_D_error=max_error,p_identical=True,primary_v1_identical_on_20_tables=True,
        primary_AST_unchanged=True,rho_validator_AST_unchanged=True,
        analyst_sha256=summary['analyst_sha256'],tests_sha256=summary['tests_sha256'],plan_sha256=sha(HERE/'plan_F1_BORRADOR_v2.json'),
        old_manifest_members_preserved=len(previous_manifest),old_manifest_closure=previous_closure,
        external_members_verified=len(external),real_data_used=False,training_updates=0,geometry_executed=False,
        producer_created=False,watchdog_120_seconds='REQUIREMENT_FOR_FUTURE_PRODUCER_NOT_TESTED_HERE',
        F2_N_selected=False,python=platform.python_version())
    write(REV/'verification.json',verification)
    report=f'''# Pruebas de CIFAR F1 · revisión v2

2026-10-29, hora de México. **71/71 PASS:** se repitieron los 54 casos anteriores contra el analista v2 y se añadieron 17 controles prospectivos. Sin imágenes, entrenamiento, geometría ni cohortes reales. No se repitió Monte Carlo de tamaño o potencia.

- Analista SHA: `{summary['analyst_sha256']}`.
- Pruebas SHA: `{summary['tests_sha256']}`.
- Plan v2 SHA: `{verification['plan_sha256']}`.
- Las 20 tablas independientes conservan exactamente la primaria y el veredicto de v1; frente al cálculo independiente, error máximo de D = `{max_error:.17g}` y p idéntico. También se reprodujeron C1 directo y la CLI con 5.000 permutaciones.
- AST: primaria, inclusión, validador rho, integridad, CLI y semillas sin cambios. Solo se añadió el agrupamiento por split, se sustituyó el secundario de estratos y se actualizaron las referencias de versión y plantilla.

## Cambios comprobados

| Caso | Resultado |
|---|---|
| c individuales atraviesan .4 y .8 | Cada split conserva sus cinco trayectorias; 33/34/33 splits y 165/170/165 trayectorias en bajo/intermedio/alto. Asignación igual a un cálculo independiente por split; sin IDs repetidos o perdidos. |
| Medianas exactamente .4 y .8; c = 1 | Empates hacia el estrato superior; se reportan también el estrato vacío y sus conteos. |
| Splits con 3 o 4 elegibles | Medianas solo entre elegibles; la mediana par usa los dos centrales. Un split con 2 elegibles queda fuera de la primaria y de los estratos, y se identifica explícitamente. |
| 19 frente a 20 splits | NO_DEFINIDO frente a DESCRIPTIVO, conservando número e IDs de splits y trayectorias. La primaria no cambia. |
| Quad_error nulo, vacío, NaN, infinito o negativo | Rechazo en ambos ganadores sin imputar cero; mismos resultados primarios que v1 ante esos datos inválidos. |
| Tolerancias por longitud del ganador | Se acepta el límite relativo y se rechaza el exceso de una ULP; el error de caras usa ρ_caras y el de vértices usa ρ_vert, también si difieren por un factor 10. |

[Resumen](pruebas/summary.json), [índice de los 71 casos](pruebas/indice_casos.csv), [log](pruebas/console.log), [manifest externo](pruebas/external_manifest.csv) y [verificación](verification.json). Todos los resultados nuevos están separados de v1, cuyos {len(previous_manifest)} miembros y manifiestos permanecen intactos. Los nombres nuevos son portables en Windows; estas pruebas se ejecutaron en Linux, no se afirma validación nativa de Windows.

El watchdog externo de 120 s es un requisito del productor futuro. El analista y estas pruebas solo verifican el tiempo declarado y el tratamiento de timeout como falta de medida. No se implementó ni probó aquí una interrupción real de rho. Ninguna prueba autoriza congelar o entrenar F1.
'''
    text(REV/'PRUEBAS_F1_v2.md',report)
    existing=(REV/'README.md').read_text()
    # El índice v2 es un documento vivo de esta revisión, no un archivo de v1.
    existing=existing.replace('Analista, pruebas y sus salidas se publicarán en esta misma revisión, conservando las de v1. No se crea productor ni se usa ninguna cohorte real.',
        '[Analista v2](../analisis_F1_v2.py), [pruebas v2](../pruebas_F1_v2.py), [esquema v2](../ESQUEMA_TABLA_v2.md), [reporte de 71 pruebas](PRUEBAS_F1_v2.md), [verification.json](verification.json) y [manifest](manifest.sha256). La primaria se conserva exactamente en las 20 tablas de comparación. No se crea productor ni se usa ninguna cohorte real.\n\nPara una reproducción sintética, con los [requisitos heredados](../requirements.txt), usar una copia donde las rutas de salida nuevas estén vacías; el script nunca sobrescribe una corrida existente:\n\n```bash\nOPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python -I experiments/DIN_borde/CIFAR/F1/pruebas_F1_v2.py\n```\n\nLos fixtures se conservan fuera de Git en `/workspace/work/din-cifar-f1-pruebas-v2`, enlazados por SHA. La v1 sigue accesible desde su [índice histórico](../README.md).')
    (REV/'README.md').write_text(existing,encoding='utf-8')
    text(REV/'progress.md','''# Progreso de la revisión v2

2026-10-29, hora de México. Leídos AGENTS.md, el diseño, el analista y las pruebas v1, y la petición de la auditoría del PR #127. No se usaron imágenes ni estados de F0/F0b o F1.

La revisión prospectiva, el diseño legible con espacios y el plan v2 se comprometieron en `ec32a7de`, antes del analista y sus pruebas (`17030c89`). Se conservan todos los archivos y resultados de v1. Se ejecutaron 71 pruebas sintéticas: 54 heredadas y 17 nuevas, sin fallos inesperados. Las 20 comparaciones conservaron exactamente la primaria de v1; los cambios de estratos no afectan a la inclusión ni al estimando global.

Se separó la clasificación por mediana elegible del split de los perfiles operacionales por c individual. Se publican todos los conteos e IDs de estratos aunque D sea NO_DEFINIDO. «Longitud» se aclaró como ρ del ganador, y None se rechaza en los errores de cuadratura sin modificar el validador. El watchdog de 120 s continúa reservado al productor como requisito.

El diseño y el analista permanecen BORRADOR para revisión; no se congela F1, no se crea productor ni se elige N de F2. No se entrenó ni se midió ninguna cohorte real.
''')
    files=[HERE/n for n in ['analisis_F1_v2.py','pruebas_F1_v2.py','plan_F1_BORRADOR_v2.json','ESQUEMA_TABLA_v2.md','publicar_v2.py']]
    files.append(HERE.parent/'DISENO_CIFAR_F1_BORRADOR_v2.md')
    files+=sorted(p for p in REV.rglob('*') if p.is_file() and p.name not in CLOSING)
    assert all(not re.search('[<>:"|?*]',p.relative_to(ROOT).as_posix()) for p in files)
    assert all(p.suffix not in ('.npy','.npz','.pt','.pth','.zip') for p in files)
    for p in files:
        if p.suffix!='.md':continue
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' in link:continue
            path=link.split('#')[0]
            if path in ('manifest.sha256',):continue
            assert not path or (p.parent/path).exists(),(p,link)
    members=[dict(path=Path(os.path.relpath(p,REV)).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in files]
    with (REV/'manifest.csv').open('x',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['path','bytes','sha256'],lineterminator='\n');writer.writeheader();writer.writerows(members)
    text(REV/'manifest.sha256',''.join(r['sha256']+'  '+r['path']+'\n' for r in members))
    text(REV/'PUBLICACION_v2.sha256',''.join(sha(REV/n)+'  '+n+'\n' for n in ['manifest.csv','manifest.sha256']))
    assert all(sha(REV/r['path'])==r['sha256'] for r in members)
    print(json.dumps(dict(status='PASS',tests=71,v1_members_preserved=len(previous_manifest),v2_members=len(members),design_still_draft=True)))


if __name__=='__main__':main()
