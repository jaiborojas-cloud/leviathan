"""SHA, universos, reproducción y aislamiento C2; no reentrena ni repite test/rho."""
import csv
import json
from pathlib import Path
import subprocess
from collections import Counter
from support_v1 import ROOT,STAGE,CFG,RUN,ARRAYS,G3,sha,write,csv_write,code_guard,guard


def main():
    code_guard();guard();errors=[];external={}
    def register(r):
        p=Path(r['path'])
        if not (p.is_relative_to(ARRAYS) or p.is_relative_to(G3)):
            errors.append('Raíz externa:'+str(p));return
        if str(p) not in external:
            if sha(p)!=r['sha256'] or p.stat().st_size!=int(r['bytes']):errors.append('SHA externo:'+str(p))
            external[str(p)]=dict(path=str(p),sha256=r['sha256'],bytes=int(r['bytes']))
    for r in csv.DictReader((STAGE/'input_manifest.csv').open()):register(r)
    datasets=json.loads((RUN/'test_datasets.json').read_text())
    for r in datasets:register(r['noise']);register(r['array'])
    observed=set();statuses=Counter();visits=0;max_errors={}
    for path in sorted((RUN/'records').glob('*.json')):
        r=json.loads(path.read_text());identity=r['id']
        if identity in observed:errors.append('Duplicado:'+identity)
        observed.add(identity);statuses[r['status']]+=1
        if 'test_array' in r:register(r['test_array'])
        for u,v in r['visits'].items():
            visits+=1
            if 'checkpoint' in v:register(v['checkpoint'])
            if v.get('reproduction_ok') is False:errors.append('Discrepancia reproducción:'+identity+':'+u)
            for name,e in v.get('reproduction_errors',{}).items():max_errors[name]=max(max_errors.get(name,0),e)
    planned={f'S{l:02}_s{s:02}_k{k}' for l in range(3) for s in range(100) for k in range(5)}
    if observed!=planned:errors.append('Universo de trayectorias distinto')
    if visits!=7500:errors.append('Conteo de visitas distinto')
    controls=json.loads((RUN/'controls.json').read_text())
    if controls['status']!='PASS':errors.append('Controles fallidos')
    for r in controls['records']:register(r['array'])
    analysis=json.loads((RUN/'analysis.json').read_text())
    if len(analysis.get('records',[]))!=44:errors.append('Celdas de análisis distintas')
    for r in analysis.get('records',[]):
        if 'array' in r:register(r['array'])
    estimates=list(csv.DictReader((RUN/'estimates.csv').open()))
    if len(estimates)!=132:errors.append('Resultados distintos de 132')
    if {r['candidate'] for r in estimates}!={c['name'] for c in CFG['candidates']}:errors.append('Candidatos no coinciden')
    if any(r['candidate']=='delta_c_10_30' for r in estimates):errors.append('Candidato prohibido añadido')
    for r in estimates:
        if r['propose']=='True' and not (r['dataset']=='2' and r['outcome']=='test_loss_250'):errors.append('Promoción fuera de primaria')
    archived=list(csv.DictReader((STAGE/'record_manifest.csv').open()))
    if len(archived)!=1500:errors.append('Archivo incompleto')
    for r in archived:
        if sha(STAGE/r['path'])!=r['sha256']:errors.append('SHA registro:'+r['path'])
    for r in csv.DictReader((STAGE/'freeze_manifest.csv').open()):
        if sha(ROOT/r['path'])!=r['sha256']:errors.append('Entrada congelada:'+r['path'])
    first_code=subprocess.check_output(['git','log','--reverse','--format=%H','--diff-filter=A','--','experiments/DIN_borde/D9g/scripts/measure_v1.py'],cwd=ROOT,text=True).splitlines()[0]
    if subprocess.run(['git','merge-base','--is-ancestor','0896fe4',first_code],cwd=ROOT).returncode:errors.append('Diseño no anterior al código')
    for line in subprocess.check_output(['git','diff','--name-status',CFG['base_main']],cwd=ROOT,text=True).splitlines():
        status,path=line.split('\t',1)
        if status!='A' or not path.startswith('experiments/DIN_borde/D9g/'):errors.append('Cambio fuera de alcance:'+line)
    if any(p.suffix in ['.npz','.npy','.pt','.pth','.zip'] for p in STAGE.rglob('*') if p.is_file()):errors.append('Arrays en Git')
    csv_write(STAGE/'external_manifest.csv',[external[k] for k in sorted(external)],['path','sha256','bytes'])
    write(STAGE/'verification.json',dict(status='PASS' if not errors else 'FAIL',errors=errors,trajectories=len(observed),visits=visits,
        state_counts=dict(statuses),test_panels=len(datasets),test_samples_per_panel=3000,external_files_verified=len(external),
        reproduction_max_errors=max_errors,statistics_controls='PASS' if controls['status']=='PASS' else 'FAIL',analysis_cells=len(estimates),
        candidates=11,Bonferroni_denominator=12,design_commit='0896fe4',code_commit=first_code,C2_data_read=False,new_training=False,new_rho_measurements=False))
    print(json.dumps(dict(status='PASS' if not errors else 'FAIL',errors=errors,external_files=len(external),trajectories=len(observed),visits=visits)))
    if errors:raise RuntimeError('Verificación fallida')

if __name__=='__main__':main()
