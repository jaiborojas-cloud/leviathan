"""Publicación de valores individuales y conteos operacionales; sin asociaciones."""
import csv
import json
import math
import subprocess
from collections import Counter
from support_v1 import ROOT, STAGE, RUN, CFG, sha, write, guard, code_guard

COLUMNS = ['trajectory','split','k','X10','R250','c250','q250','rho_caras_10','rho_caras_250','rho_vert_10','rho_vert_250','error']


def main():
    code_guard(); guard()
    plan=json.loads((STAGE/'cohorte/c2_plan.json').read_text())
    ids=[f'c2_s{s:04d}_k{k}' for s in range(plan['n_splits']) for k in range(5)]
    import hashlib
    if hashlib.sha256('\n'.join(ids).encode()).hexdigest()!=plan['ids_sha256']:
        raise RuntimeError('IDs no coinciden con plan')
    rows=[]; status_counts=Counter(); failures=0
    for s in range(plan['n_splits']):
        for k in range(5):
            identity=f'c2_s{s:04d}_k{k}'
            row={c:'' for c in COLUMNS}; row.update(trajectory=identity,split=s,k=k)
            errors=[]; states={}
            record_path=RUN/'trajectories'/(identity+'.json')
            if not record_path.exists(): errors.append('TRAJECTORY_RECORD_MISSING')
            else:
                record=json.loads(record_path.read_text())
                if record.get('error'): errors.append(record['error'])
            for step in CFG['updates']:
                path=RUN/'states'/f'{identity}_u{step:03}.json'
                if not path.exists():
                    errors.append(f'STATE_MISSING_u{step:03}'); continue
                state=json.loads(path.read_text()); states[step]=state
                status_counts[state['status']]+=1
                if state['status']!='MEASURED':
                    errors.append(f"u{step:03}:{state['status']}:{state.get('exception',state.get('rho',{}).get('reason',''))}")
            # Copia directa; ningún ajuste, centrado ni estadístico entre filas.
            early=states.get(10,{}); last=states.get(250,{})
            row['X10']=early.get('metrics',{}).get('X','')
            for column,key in [('R250','log1m_star'),('c250','c'),('q250','q')]:
                row[column]=last.get('metrics',{}).get(key,'')
            for step,state in [(10,early),(250,last)]:
                for quantity in ['rho_caras','rho_vert']:
                    row[f'{quantity}_{step}']=state.get('rho',{}).get(quantity,'')
            for key in COLUMNS[3:-1]:
                value=row[key]
                if not isinstance(value,(int,float)) or not math.isfinite(value):
                    errors.append('NONFINITE_OR_MISSING:'+key)
                    if value is None: row[key]=''
            for key in ['rho_caras_10','rho_caras_250','rho_vert_10','rho_vert_250']:
                if isinstance(row[key],(int,float)) and row[key]<=0: errors.append('NONPOSITIVE:'+key)
            row['error']=' | '.join(errors)
            failures+=bool(errors);rows.append(row)
    table=STAGE/'cohorte/c2_cohorte.csv'
    with table.open('x',newline='',encoding='utf-8') as file:
        writer=csv.DictWriter(file,fieldnames=COLUMNS);writer.writeheader();writer.writerows(rows)
    execution=json.loads((RUN/'execution.json').read_text())
    summary=dict(tabla_sha256=sha(table),plan_sha256=sha(STAGE/'cohorte/c2_plan.json'),
        script_sha256=sha(STAGE/'cohorte_scripts/run_v1.py'),
        publicador_sha256=sha(STAGE/'cohorte_scripts/publish_v1.py'),
        conteos_operacionales=dict(splits_planificados=plan['n_splits'],trayectorias_planificadas=len(ids),
            filas_publicadas=len(rows),filas_con_error=failures,filas_sin_error=len(rows)-failures,
            estados_planificados=CFG['planned_states'],estados_por_estado=dict(status_counts)),
        segundos_entrenamiento_medicion=execution['seconds'],
        generation_commit=execution['code_commit'],
        analysis_executed=False,associations_computed=False,
        regimen_agregado_calculado=False)
    write(STAGE/'cohorte/RESUMEN_c2.json',summary)
    with (STAGE/'cohorte/PUBLICACION_c2.sha256').open('x') as file:
        for path in [table,STAGE/'cohorte/c2_plan.json',STAGE/'cohorte/RESUMEN_c2.json']:
            file.write(sha(path)+'  '+str(path.relative_to(ROOT))+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
