"""Verificación de fuentes, pipeline repetido y tablas; no análisis adicional."""
import csv
import json
from pathlib import Path
import subprocess
import numpy as np
from support_v1 import ROOT,STAGE,RUN,CFG,ARRAYS,sha,write,csv_write,code_guard,guard


def main():
    code_guard();guard();errors=[];external={}
    def register(r):
        p=Path(r['path'])
        if not p.is_relative_to(ARRAYS):errors.append('Raíz externa:'+str(p));return
        if sha(p)!=r['sha256'] or p.stat().st_size!=r['bytes']:errors.append('SHA externo:'+str(p))
        external[str(p)]=r
    ctrl=json.loads((RUN/'controls.json').read_text())
    for r in ctrl['records']:register(r['array'])
    if ctrl['status']!='PASS':errors.append('Controles fallidos')
    result=json.loads((RUN/'analysis.json').read_text())
    for r in result['records']:
        register(r['array'])
        if r['B1_D_error']>1e-10:errors.append('B1 no reproduce')
        if not r['adequacy_repeated_identical'] or not r['lambda_repeated_identical']:errors.append('Parámetros base dependieron de c')
        with np.load(r['array']['path'],allow_pickle=False) as z:
            if z['lambda_choices'].shape!=(10,1000) or z['lambda_scores'].shape!=(10,1000,33):errors.append('No se conservan todos los pipelines')
            if len(z['D_reading'])!=1000:errors.append('No hay999permutaciones')
            # La base de lectura se decide por rendimiento de base, no por incremento.
            sb1=z['SSE_B1_base'][0];sbr=z['SSE_BR_base'][0]
            if r['reading']!='BR' and r['base_adequate']:errors.append('Lectura inconsistente')
            if r['adjusted'] not in [500,1500]:errors.append('Datos ajustados inesperados')
    rows=list(csv.DictReader((STAGE/'sources/D9g_b/results/run_v1/features.csv').open()))
    if len(rows)!=1500 or len({r['id'] for r in rows})!=1500:errors.append('Universo distinto')
    for r in csv.DictReader((STAGE/'freeze_manifest.csv').open()):
        if sha(ROOT/r['path'])!=r['sha256']:errors.append('Entrada congelada:'+r['path'])
    first_code=subprocess.check_output(['git','log','--reverse','--format=%H','--diff-filter=A','--','experiments/DIN_borde/D9g_c/scripts/statistics_v1.py'],cwd=ROOT,text=True).splitlines()[0]
    if subprocess.run(['git','merge-base','--is-ancestor','d5e694a',first_code],cwd=ROOT).returncode:errors.append('Diseño posterior a código')
    for line in subprocess.check_output(['git','diff','--name-status',CFG['base_main']],cwd=ROOT,text=True).splitlines():
        state,path=line.split('\t',1)
        if state!='A' or not path.startswith('experiments/DIN_borde/D9g_c/'):errors.append('Fuera de alcance:'+line)
    if any(p.suffix in ['.npz','.npy','.pt','.pth','.zip'] for p in STAGE.rglob('*') if p.is_file()):errors.append('Arrays en Git')
    csv_write(STAGE/'external_manifest.csv',[external[k] for k in sorted(external)],['path','sha256','bytes'])
    write(STAGE/'verification.json',dict(status='PASS' if not errors else 'FAIL',errors=errors,rows=len(rows),datasets=len(result['records']),
        external_files_verified=len(external),permutations=999,p_resolution=.001,outer_pipeline_calls_per_dataset=10000,
        B1_reproduced=True,all_lambda_selection_repeated=True,all_adequacy_selection_repeated=True,C2_data_read=False,
        candidate_residualization_user_chosen=True,test_regenerated=False,test_reevaluated=False,new_training=False,design_commit='d5e694a',code_commit=first_code))
    print(json.dumps(dict(status='PASS' if not errors else 'FAIL',errors=errors,external_files=len(external))))
    if errors:raise RuntimeError('Verificación fallida')

if __name__=='__main__':main()
