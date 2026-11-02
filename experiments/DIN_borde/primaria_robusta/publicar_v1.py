"""Integridad y documentación de A1/A2; no ejecuta análisis ni repite pruebas."""
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE='5eff9b5e5907123ee936540c364e14d424de94ee'
EXCLUDED={'manifest.csv','manifest.sha256','PUBLICACION_BORRADOR_v1.sha256'}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def write(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
def text(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as f:f.write(value)


def main():
    own=Path(__file__).resolve()
    assert own.read_bytes()==subprocess.check_output(['git','show','HEAD:'+own.relative_to(ROOT).as_posix()],cwd=ROOT)
    runs={};external_total=0
    for version,n,status in [('v1',57,'FAIL'),('v1_1',58,'PASS')]:
        directory=HERE/'pruebas'/('results_'+version)
        summary=read(directory/'summary.json');assert summary['cases']==n and summary['status']==status
        assert summary['analyst_sha256']==sha(HERE/'analisis_robusta_v1.py')
        assert summary['tests_sha256']==sha(HERE/('pruebas_robusta_'+version+'.py'))
        assert summary['training_updates']==0 and summary['real_data_used'] is False and summary['geometry_executed'] is False
        with (directory/'external_manifest.csv').open() as f:external=list(csv.DictReader(f))
        assert all(sha(Path(r['path']))==r['sha256'] for r in external)
        external_total+=len(external)
        with (directory/'console.log').open('xb') as f:f.write(Path('/tmp/din-robusta-pruebas-'+version+'.log').read_bytes())
        records={}
        for path in directory.glob('*.json'):
            if path.name=='summary.json':continue
            record=read(path);records[record['case']]=(path,record)
        assert len(records)==n
        runs[version]=dict(summary=summary,records=records)
    assert runs['v1']['summary']['failures']==['D_sin_max_degenerado_conserva_fallo']
    assert runs['v1_1']['summary']['failures']==[]
    current=runs['v1_1']['records'];assert all(r['ok'] for _,r in current.values())
    shared=set(runs['v1']['records'])&set(current)
    assert len(shared)==56
    assert all(runs['v1']['records'][k][0].read_bytes()==current[k][0].read_bytes() for k in shared)
    equivalences=[current[f'equivalencia_C1_{i:02d}'][1]['result'] for i in range(20)]
    assert all(r['C1_exact'] and r['p_independent_equal'] for r in equivalences)
    maxerr=max(r['D_error_independent'] for r in equivalences)
    extreme=current['L_extrema_mayor_10'][1]['result'];assert extreme['max_abs_z_L']>10
    references=[
        'experiments/DIN_borde/PRIMARIA_ROBUSTA_v1.md',
        'experiments/DIN_borde/C1/analisis_C1_v2.py',
        'experiments/DIN_borde/revision_primaria/REVISION_PRIMARIA_2026-10-29.md',
        'experiments/DIN_borde/revision_primaria/sensibilidad_bases.py',
        'experiments/DIN_borde/CIFAR/CIERRE_CIFAR3_2026-11-02.md',
        'experiments/DIN_borde/CIFAR/F1/resultado/RESULTADO_F1_2026-10-29.md',
        'experiments/DIN_borde/G3/CONCLUSION.md',
        'experiments/DIN_borde/Q13M2/resultado/RESULTADO_Q13M2_2026-10-28.md',
        'experiments/DIN_borde/Q13M2/calibracion/RESULTADO_v1.md',
        'experiments/DIN_borde/Q13M2/cohorte/EJECUCION_WINDOWS_v2.md']
    sources=[dict(path=r,sha256=sha(ROOT/r)) for r in references]
    assert sources[0]['sha256']=='493a5eabe15028a3522ce5971a07343a806f8379c84288c7a2c2446efe8ad49a'
    assert sources[1]['sha256']=='8711f468d0df110a94c9cfdf6a1d0777f495537546cdce516929f0cb129858d5'
    write(HERE/'fuentes/provenance.json',dict(base_main=BASE,sources=sources,
        reparto=dict(pr=130,revision='f45e320a160514554165488ed719bf2902cb7fff',path='docs/research-notes/reparto-2026-11-02.md',
                     git_blob_sha='7cc404051bf12cd4d7952a251475616c4f3f1ae5',snapshot='reparto_PR130.md',snapshot_sha256=sha(HERE/'fuentes/reparto_PR130.md'),merged_at_initial_read=False),
        no_cohort_tables_or_checkpoints_read=True))
    summary=runs['v1_1']['summary']
    verification=dict(status='PASS_VALIDATION_DRAFT_V1_1',design_state='BORRADOR',frozen=False,
        tests_current_passed=58,tests_initial_passed=56,tests_initial_total=57,failed_runs_preserved=1,
        failed_initial_case='D_sin_max_degenerado_conserva_fallo',amendment_before_test_correction=True,
        analyst_corrected=False,shared_case_results_byte_identical=56,
        C1_exact_tables=20,C1_general_no_clip_exact=True,independent_max_D_error=maxerr,p_identical=True,
        extreme_max_abs_z=extreme['max_abs_z_L'],NO_APRENDIO_and_exact_boundary_verified=True,
        NO_ROBUSTO_rule_and_pipeline_verified=True,pipeline_influence_failure_test='unit_injection_explicitly_labelled',
        nominal_CLI_permutations=5000,
        analyst_sha256=summary['analyst_sha256'],tests_current_sha256=summary['tests_sha256'],
        tests_initial_sha256=runs['v1']['summary']['tests_sha256'],config_sha256=sha(HERE/'config_BORRADOR_v1.json'),
        adopted_spec_sha256=sources[0]['sha256'],C1_sha256=sources[1]['sha256'],external_members_verified=external_total,
        real_data_read=False,training_updates=0,geometry_executed=False,nominal_size_or_power_simulated=False,
        past_stage_files_modified=False,producer_created=False,next_experiment_selected=False,python=platform.python_version())
    write(HERE/'verification.json',verification)
    report=f'''# Resultado de las pruebas sintéticas A1

2026-11-02. **BORRADOR para auditoría de Claude.** Corrida actual v1.1: **58/58 PASS**. No se entrenó, midió geometría ni leyó ninguna tabla real. No se evaluó tamaño nominal o potencia; estas pruebas no son una confirmación científica ni una garantía universal de robustez.

| Componente | SHA-256 |
|---|---|
| Analista v1, sin correcciones entre corridas | `{summary['analyst_sha256']}` |
| Pruebas actuales v1.1 | `{summary['tests_sha256']}` |
| Pruebas iniciales v1 | `{runs['v1']['summary']['tests_sha256']}` |
| C1, solo código sobre sintéticos | `{sources[1]['sha256']}` |

## Obligatorios y equivalencia

- **NO_APRENDIO:** .49 cuenta como falta, con ID y todos sus motivos, sin sustitución; .5 exacto pasa y su vecino representable inferior no. Límites de 5 % y 80 % comprobados con denominadores planificados.
- **L extrema:** |z| = **{extreme['max_abs_z_L']:.8f}**, una trayectoria recortada en su bloque y conservada en la muestra. Recorte antes de potencias/centrado, limitado al rango de entrenamiento e independiente de X/Y; errores y p contrastados con cálculo independiente.
- **C1 exacto sin recorte:** 20 tablas con extremos repetidos dentro del entrenamiento de todos los bloques; D, p, pendiente y cuantil 95 idénticos bit a bit al código congelado. Otra tabla general se contrastó en modo diagnóstico sin recorte. Frente a la reimplementación independiente, error máximo de D = `{maxerr:.17g}`, p idéntico. B = 39 en estos controles; la CLI nominal mantiene **5.000**.
- **Influencia:** g_i y D_sin_max frente a cálculo independiente, empates por orden del universo, fracción mayor que 1 sin truncar y null cuando la suma no es positiva. Omitir un ID conserva las otras dos filas de un split de tres.
- **Decisión:** tabla mínima PASS / NO_ROBUSTO / NOT_MET / INCONCLUSIVE. La propagación de NO_ROBUSTO y del fallo de D_sin_max se prueba además mediante **inyecciones unitarias explícitas**, no con una cohorte inventada que se afirme degenerada.
- **Dominios y E/S:** log solo tras validar rho; múltiples motivos, ausentes/fallidas, constantes, identidad/splits/plan, orden CSV invariante; salida exclusiva inicial y final, JSON estricto y bloqueo de tipo real en borrador. No se afirma validación nativa Windows; se ejecutó en Linux.

## Fallo y versiones conservados

La primera corrida terminó **56/57 PASS**. El fixture `D_sin_max_degenerado_conserva_fallo` suponía indebidamente que la única trayectoria con variación de X sería también argmax g fuera de muestra. El fallo, sus datos y su traceback se conservan. Se registró la [enmienda](ENMIENDA_PRUEBAS_v1_1.md) en `c4be8b9b` **antes** de corregir las pruebas (`6d153497`); el analista nunca cambió. La versión nueva reemplaza esa expectativa por inyección de fallo controlada y añade propagación de NO_ROBUSTO. Los **56 casos comunes tienen resultados byte a byte idénticos** entre corridas.

[Resumen inicial FAIL](pruebas/results_v1/summary.json), [resumen actual PASS](pruebas/results_v1_1/summary.json), [fallo original](pruebas/results_v1/D_sin_max_degenerado_conserva_fallo.json), [verificación](verification.json). Fixtures/arrays y salidas CLI fuera de Git, con manifests por versión en los directorios de resultados. Los logs originales se conservan sin reejecutar las pruebas.

## Qué debe auditar Claude

La especificación adoptada queda intacta. Revisar las convenciones operacionales declaradas en el contrato: pendiente global como C1, empates exactos, fracción no definida con suma no positiva, conservar dos filas en la omisión diagnóstica y D_sin_max degenerado → INCONCLUSIVE. Revisar además vínculos del productor, conteos y distinción entre pruebas de la regla por inyección y evidencia estadística. Los secundarios de rangos/spline/grado 5 son recomendaciones de la adopción, **no se implementan ni se seleccionan aquí**. Ningún resultado habilita automáticamente una cohorte real o la congelación.
'''
    text(HERE/'PRUEBAS_v1_1.md',report)
    text(HERE/'progress.md','''# Progreso A1/A2 · 2026-11-02

Leídos AGENTS.md, adopción robusta, revisión metodológica y cierre CIFAR-3, C1 como código por SHA y reparto de PR #130 (pendiente al iniciar). Solo documentos publicados para A2; ninguna tabla real ni checkpoint se abrió. Base main `5eff9b5e`.

`c3573a13`: contrato y pruebas prospectivas antes de código. `3be81cb1`: analista y pruebas v1 antes de su ejecución. Corrida v1: 56/57, conservada. El fallo era una expectativa indebida del fixture de degeneración, no una corrección del analista. `c4be8b9b`: enmienda anterior a cambios. `6d153497`: pruebas v1.1 con rutas nuevas, antes de ejecutarse; 58/58 PASS. Los 56 casos comunes conservaron resultados idénticos. Analista SHA 1e2d903b sin cambios en ambas corridas.

A2 ofrece dos opciones sin datos nuevos: piloto para separar concentración y escala de logits en gaussianas, o una nueva familia Digits-3. Costes orientativos extrapolados del PC, no benchmarks ni promesa de potencia. El responsable elige y congela; Claude audita y luego implementa el productor. No se toca el piloto Lean.

Se entregan ambas versiones de pruebas, fallo, logs, fuentes, hashes y manifest en un PR de borrador. No se cambia la especificación adoptada, ningún estado previo ni instrumento; no se congela esta implementación, no se ejecuta una cohorte y no se fija un N confirmatorio.
''')
    readme='''# A1/A2 · primaria robusta DIN v1

**BORRADOR para auditoría de Claude**, conforme a la [especificación adoptada](../PRIMARIA_ROBUSTA_v1.md). Solo diseños nuevos; ningún estado previo cambia.

- **A1:** [analista genérico](analisis_robusta_v1.py), [contrato](DISENO_ANALISTA_BORRADOR_v1.md), [interfaz/CSV/CLI](INTERFAZ_v1.md) y [configuración](config_BORRADOR_v1.json).
- [Pruebas actuales v1.1](pruebas_robusta_v1_1.py): **58/58 PASS**, [reporte](PRUEBAS_v1_1.md), [verification.json](verification.json). NO_APRENDIO, L con |z| > 10, equivalencia exacta C1 sin recorte, influencia y cuatro veredictos. Sin simulación de tamaño o potencia.
- [Pruebas v1 conservadas](pruebas_robusta_v1.py): 56/57, fallo del fixture archivado; [enmienda previa](ENMIENDA_PRUEBAS_v1_1.md). El analista no cambió. Resultados comunes idénticos en las dos corridas.
- **A2:** [dos opciones breves](OPCIONES_SIGUIENTE_EXPERIMENTO.md), con pregunta, coste orientativo del PC, riesgos y aplicación de A1. Sin nueva cohorte ni elección por el agente.
- [Fuentes y SHA](fuentes/provenance.json), [reparto PR #130](fuentes/reparto_PR130.md), [progreso](progress.md), [manifest](manifest.sha256). PR #130 estaba pendiente de fusión al leerlo, snapshot de `f45e320a`.

## Reproducir pruebas y revisar

Python 3.12 y [requisitos](requirements.txt). Las salidas son exclusivas: usar una copia anterior a resultados o rutas vacías declaradas para una reproducción, sin borrar las corridas archivadas.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python -I experiments/DIN_borde/primaria_robusta/pruebas_robusta_v1_1.py
```

Los fixtures, arrays y salidas CLI se conservan fuera de Git en `/workspace/work/din-robusta-pruebas-v1` y `/workspace/work/din-robusta-pruebas-v1_1`; cada corrida conserva su manifest externo. Se cargó solo código C1 por SHA, nunca sus datos o su wrapper de cohorte. La CLI del borrador bloquea datos reales; no se incluyen productores ni dependencias de red. Las pruebas se ejecutaron en Linux; no se promete validación nativa Windows.

Antes de congelar, Claude debe revisar las convenciones explícitas y los límites del [reporte](PRUEBAS_v1_1.md). El primer diseño nuevo deberá fijar universo, productores, compuerta y potencia, y congelar esta implementación tras la auditoría. Un PASS frente a esta base no prueba información condicional frente a cualquier función de L, causalidad ni robustez universal. La compuerta añade exactamente D_sin_max > 0, sin inventar otro umbral de fracción dominante.
'''
    (HERE/'README.md').write_text(readme,encoding='utf-8')
    changes=subprocess.check_output(['git','diff','--name-status',BASE],cwd=ROOT,text=True).splitlines()
    assert all(r.startswith('A\texperiments/DIN_borde/primaria_robusta/') for r in changes),changes
    files=sorted(p for p in HERE.rglob('*') if p.is_file() and p.name not in EXCLUDED and '__pycache__' not in p.parts and p.suffix!='.pyc')
    assert not [p for p in files if p.suffix in ('.npz','.npy','.pt','.pth','.zip')]
    assert all(not re.search('[<>:"|?*]',p.relative_to(ROOT).as_posix()) for p in files)
    for p in files:
        if p.suffix!='.md':continue
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' in link or p.name=='reparto_PR130.md':continue
            dest=link.split('#')[0]
            if dest=='manifest.sha256':continue
            assert not dest or (p.parent/dest).exists(),(p,link)
    members=[dict(path=p.relative_to(HERE).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in files]
    # La especificación y C1 son referencias de integridad, no archivos modificados.
    members += [dict(path=Path(os.path.relpath(ROOT/r,HERE)).as_posix(),bytes=(ROOT/r).stat().st_size,sha256=sha(ROOT/r)) for r in references[:2]]
    with (HERE/'manifest.csv').open('x',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['path','bytes','sha256'],lineterminator='\n');writer.writeheader();writer.writerows(members)
    text(HERE/'manifest.sha256',''.join(r['sha256']+'  '+r['path']+'\n' for r in members))
    text(HERE/'PUBLICACION_BORRADOR_v1.sha256',''.join(sha(HERE/n)+'  '+n+'\n' for n in ['manifest.csv','manifest.sha256']))
    assert all(sha(HERE/r['path'])==r['sha256'] for r in members)
    print(json.dumps(dict(status='PASS_VALIDATION_DRAFT_V1_1',tests_current=58,initial_failure_preserved=True,analyst_unchanged=True,members=len(members),real_data_used=False)))


if __name__=='__main__':main()
