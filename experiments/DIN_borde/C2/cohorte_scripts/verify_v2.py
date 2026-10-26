"""Integridad operacional de C2. No calcula relaciones, regresiones ni régimen."""
import csv
import hashlib
import json
from pathlib import Path
from collections import Counter
import subprocess
import numpy as np
from support_v1 import ROOT, STAGE, CFG, RUN, ARRAYS, sha, write, code_guard, guard
from publish_v1 import COLUMNS


def main():
    code_guard()
    errors=[];external={}
    roots=[ARRAYS,Path(CFG['gate_arrays_dir']),Path('/workspace/work/din-c2-power-v1-arrays')]
    def register(record):
        path=Path(record['path'])
        if not any(path.is_relative_to(root) for root in roots):
            errors.append('Raíz externa no autorizada:'+str(path));return
        if str(path) not in external:
            if not path.is_file() or sha(path)!=record['sha256'] or path.stat().st_size!=record['bytes']:
                errors.append('SHA/tamaño externo:'+str(path))
            external[str(path)]=record
    # Potencia: sólo integridad de sus arrays ya publicados, sin recalcular estadísticas.
    power=json.loads((STAGE/'potencia/results_v1/summary.json').read_text())
    for candidate in power['candidates']:
        for frame in candidate['frames']: register(frame['array'])
    if power['selected_splits']!=len(CFG['splits']): errors.append('Plan vs potencia')
    frozen_content=(STAGE/'MANIFIESTO_DIN_C2_v1_CONGELADO.sha256').read_bytes()
    state_manifest_rows=list(csv.DictReader((STAGE/'state_records_manifest.csv').open()))
    guard()
    gate=json.loads((STAGE/'cohorte/compuerta_v1/reconstruction.json').read_text())
    if gate['status']!='PASS' or len(gate['records'])!=3: errors.append('Compuerta fallida')
    for record in gate['records']:
        register(record['array'])
        if record['relative_M_error']!=0 or not record['f_identical']: errors.append('Reproducción no exacta')
    datasets=json.loads((RUN/'datasets.json').read_text()); panel_f={}
    for record in datasets:
        register(record['noise']);register(record['array'])
        with np.load(record['array']['path'],allow_pickle=False) as data:
            panel_f[record['split']]=data['Z'][data['panel_ids'],:2]
    plan=json.loads((STAGE/'cohorte/c2_plan.json').read_text()); n=plan['n_splits']
    ids=[f'c2_s{s:04d}_k{k}' for s in range(n) for k in range(5)]
    if hashlib.sha256('\n'.join(ids).encode()).hexdigest()!=plan['ids_sha256']: errors.append('SHA IDs')
    expected={f'{identity}_u{u:03}' for identity in ids for u in CFG['updates']}
    observed=set();statuses=Counter()
    for path in sorted((RUN/'states').glob('*.json')):
        data=json.loads(path.read_text());identity=data['id']
        if identity in observed: errors.append('Estado duplicado:'+identity)
        observed.add(identity);statuses[data['status']]+=1
        if identity!=path.stem: errors.append('ID/path:'+identity)
        for name in ['checkpoint','array','rho_diagnostic']:
            if name in data: register(data[name])
        if 'array' in data:
            with np.load(data['array']['path'],allow_pickle=False) as arr:
                if not np.array_equal(arr['f'],panel_f[data['split']]): errors.append('f/panel:'+identity)
        if 'rho_diagnostic' in data:
            rho=json.loads(Path(data['rho_diagnostic']['path']).read_text())
            if rho.get('status')=='VALID_NUMERICAL_ESTIMATE' and rho.get('implementation_version')!='r3': errors.append('Versión rho:'+identity)
    if observed!=expected: errors.append('Universo de estados distinto')
    trajectory_names={p.stem for p in (RUN/'trajectories').glob('*.json')}
    if trajectory_names!=set(ids): errors.append('Universo de trayectorias distinto')
    table=STAGE/'cohorte/c2_cohorte.csv'
    with table.open(newline='') as file:
        reader=csv.DictReader(file)
        if reader.fieldnames!=COLUMNS: errors.append('Columnas distintas')
        rows=list(reader)
    if [r['trajectory'] for r in rows]!=ids: errors.append('Orden/universo de filas distinto')
    # Verificar copia de valores, sin asociarlos ni transformarlos.
    for row in rows:
        identity=row['trajectory'];s=int(row['split']);k=int(row['k'])
        if identity!=f'c2_s{s:04d}_k{k}': errors.append('Identidad de fila distinta')
        for u in [10,250]:
            d=json.loads((RUN/'states'/f'{identity}_u{u:03}.json').read_text())
            values={f'rho_caras_{u}':d.get('rho',{}).get('rho_caras',''),f'rho_vert_{u}':d.get('rho',{}).get('rho_vert','')}
            if u==10:values['X10']=d.get('metrics',{}).get('X','')
            else: values.update(R250=d.get('metrics',{}).get('log1m_star',''),c250=d.get('metrics',{}).get('c',''),q250=d.get('metrics',{}).get('q',''))
            for key,value in values.items():
                if value is None:value=''
                if row[key]!=str(value):errors.append('Copia distinta:'+identity+':'+key)
    summary=json.loads((STAGE/'cohorte/RESUMEN_c2.json').read_text())
    if summary['tabla_sha256']!=sha(table) or summary['plan_sha256']!=CFG['plan_sha256']:errors.append('SHA publicación')
    if summary['script_sha256']!=sha(STAGE/'cohorte_scripts/run_v1.py'):errors.append('SHA generador')
    for r in state_manifest_rows:
        p=STAGE/r['path']
        if sha(p)!=r['sha256']:errors.append('SHA estado:'+r['path'])
    if subprocess.check_output(['git','show',CFG['sample_commit']+':experiments/DIN_borde/C2/cohorte/c2_plan.json'],cwd=ROOT)!=(STAGE/'cohorte/c2_plan.json').read_bytes():errors.append('Plan congelado distinto')
    execution=json.loads((RUN/'execution.json').read_text());training_commit=execution['code_commit']
    gate_path='experiments/DIN_borde/C2/cohorte/compuerta_v1/reconstruction.json'
    if subprocess.check_output(['git','show',training_commit+':'+gate_path],cwd=ROOT)!=(ROOT/gate_path).read_bytes():errors.append('Compuerta posterior al inicio')
    code_commit=gate['code_commit']
    for earlier,later in [(CFG['base_main'],CFG['sample_commit']),(CFG['sample_commit'],code_commit),(code_commit,training_commit)]:
        if subprocess.run(['git','merge-base','--is-ancestor',earlier,later],cwd=ROOT).returncode:errors.append('Orden de commits')
    changed=subprocess.check_output(['git','diff','--name-status',CFG['base_main']],cwd=ROOT,text=True).splitlines()
    for line in changed:
        status,path=line.split('\t',1)
        if status!='A' or not path.startswith('experiments/DIN_borde/C2/'):errors.append('Cambio no aditivo o fuera de alcance:'+line)
    if any(p.suffix in ['.npz','.npy','.pt','.pth','.zip'] for p in STAGE.rglob('*') if p.is_file()):errors.append('Array/peso dentro de Git')
    with (STAGE/'cohorte/external_manifest.csv').open('x') as file:
        writer=csv.DictWriter(file,fieldnames=['path','sha256','bytes']);writer.writeheader()
        for path in sorted(external):writer.writerow(external[path])
    result=dict(status='PASS' if not errors else 'FAIL',errors=errors,verification_type='INTEGRIDAD_OPERACIONAL_SIN_ANALISIS',
        planned_trajectories=len(ids),published_rows=len(rows),rows_with_error=sum(bool(r['error']) for r in rows),
        planned_states=len(expected),state_counts=dict(statuses),dataset_panels=len(datasets),
        external_files_verified=len(external),gate_reconstructions=len(gate['records']),
        source_hashes_verified=True,frozen_analysis_unchanged=True,analysis_executed=False,associations_computed=False,
        aggregate_regime_computed=False,scope='Sólo adiciones experiments/DIN_borde/C2/',
        sample_commit=CFG['sample_commit'],initial_cohort_code_commit=code_commit,training_commit=training_commit,
        tabla_sha256=sha(table),plan_sha256=CFG['plan_sha256'])
    write(STAGE/'cohorte/verification.json',result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if errors:raise RuntimeError('Verificación fallida')

if __name__=='__main__':main()
