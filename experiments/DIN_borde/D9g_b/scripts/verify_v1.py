"""Universo, SHA y controles; no vuelve a medir ni a analizar."""
import csv
import json
from pathlib import Path
import subprocess
from support_v1 import ROOT,STAGE,RUN,CFG,ARRAYS,G3,sha,write,csv_write,code_guard,guard


def main():
    code_guard();guard();errors=[];external={}
    def register(r):
        p=Path(r['path'])
        if not(p.is_relative_to(ARRAYS) or p.is_relative_to(G3)):errors.append('Raíz externa:'+str(p));return
        if str(p) not in external:
            if sha(p)!=r['sha256'] or p.stat().st_size!=int(r['bytes']):errors.append('SHA externo:'+str(p))
            external[str(p)]=dict(path=str(p),sha256=r['sha256'],bytes=int(r['bytes']))
    for r in csv.DictReader((STAGE/'input_manifest.csv').open()):register(r)
    details=json.loads((RUN/'feature_details.json').read_text())
    for r in details:
        if 'array' in r:register(r['array'])
    ctrl=json.loads((RUN/'controls.json').read_text())
    for r in ctrl['positive_negative']+ctrl['numeric']:register(r['array'])
    if ctrl['status']!='PASS':errors.append('Controles artificiales fallidos')
    result=json.loads((RUN/'analysis.json').read_text())
    for r in result['records']:
        if 'array' in r:register(r['array'])
        if r.get('negative_control_pass') is not True:errors.append('Control negativo real:'+str((r['dataset'],r['base'])))
        if r['base']==1 and (r['reference_D9g']['D_error']>1e-10 or not r['reference_D9g']['p_identical']):errors.append('B1 no reproduce')
    rows=list(csv.DictReader((RUN/'features.csv').open()));src=list(csv.DictReader((STAGE/'sources/D9g/results/run_v1/trajectories.csv').open()))
    originals={r['id']:r for r in src};expected={f'S{l:02}_s{s:02}_k{k}' for l in range(3) for s in range(100) for k in range(5)}
    if len(rows)!=1500 or {r['id'] for r in rows}!=expected:errors.append('Universo de filas')
    for r in rows:
        s=originals[r['id']]
        for dest,key in [('Y','test_loss_250'),('c30','c_30'),('train_loss','train_loss_30'),('val_loss','val_loss_30'),('val_acc','val_acc_30'),('X','X_30')]:
            if float(r[dest])!=float(s[key]):errors.append('Copia de D9g distinta:'+r['id']+':'+key)
    if len(result['records'])!=16:errors.append('Celdas distintas de 16')
    for r in csv.DictReader((STAGE/'freeze_manifest.csv').open()):
        if sha(ROOT/r['path'])!=r['sha256']:errors.append('Fuente congelada:'+r['path'])
    first_code=subprocess.check_output(['git','log','--reverse','--format=%H','--diff-filter=A','--','experiments/DIN_borde/D9g_b/scripts/features_v1.py'],text=True,cwd=ROOT).splitlines()[0]
    if subprocess.run(['git','merge-base','--is-ancestor','9c598bc',first_code],cwd=ROOT).returncode:errors.append('Diseño no precede código')
    for line in subprocess.check_output(['git','diff','--name-status',CFG['base_main']],cwd=ROOT,text=True).splitlines():
        state,path=line.split('\t',1)
        if state!='A' or not path.startswith('experiments/DIN_borde/D9g_b/'):errors.append('Fuera de alcance:'+line)
    if any(p.suffix in ['.npz','.npy','.pt','.pth','.zip'] for p in STAGE.rglob('*') if p.is_file()):errors.append('Arrays dentro de Git')
    csv_write(STAGE/'external_manifest.csv',[external[k] for k in sorted(external)],['path','sha256','bytes'])
    write(STAGE/'verification.json',dict(status='PASS' if not errors else 'FAIL',errors=errors,rows=len(rows),analysis_cells=len(result['records']),external_files_verified=len(external),
        artificial_controls='PASS' if ctrl['status']=='PASS' else 'FAIL',B1_reproduced=True,all_real_negative_controls_pass=all(r.get('negative_control_pass') for r in result['records']),
        test_loss_copied_exactly=True,test_regenerated=False,test_reevaluated=False,new_training=False,C2_data_read=False,design_commit='9c598bc',code_commit=first_code))
    print(json.dumps(dict(status='PASS' if not errors else 'FAIL',errors=errors,rows=len(rows),external_files=len(external))))
    if errors:raise RuntimeError('Verificación fallida')

if __name__=='__main__':main()
