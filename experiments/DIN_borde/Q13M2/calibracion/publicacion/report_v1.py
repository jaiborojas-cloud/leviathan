"""Verificación y publicación: únicamente c,q,acc de la calibración archivada."""
import collections
import copy
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[5]
STAGE=ROOT/'experiments/DIN_borde/Q13M2/calibracion'
sys.path.insert(0,str(STAGE/'scripts'))
from support_m2 import CFG,OUT,EXTERNAL,sha,write,code_guard
from summarize_v1 import summarize


def unit_summary():
    conditions=[('A0',0.)]+[(a,d) for a in ('LP','WD') for d in CFG[a]]
    cvalues={'A0':[.8],'LP':[.75,.69,.64,.58,.54,.48,.44,.40],'WD':[.70,.65,.60,.50,.40]}
    records=[]
    for arm,dose in conditions:
        idx=[d for a,d in conditions if a==arm].index(dose)
        for s in range(100):
            for k in range(5):records.append(dict(brazo=arm,dosis=dose,split=s,k=k,status='MEASURED',c250=cvalues[arm][idx],q250=.001,acc_panel250=.9375))
    tests=[]
    def check(name,actual,expected):
        assert actual==expected,(name,actual,expected)
        tests.append(dict(name=name,status='PASS'))
    result,_=summarize(records,conditions)
    check('LP_eligible',result['elegibilidad']['LP']['estado'],'ELEGIBLE');check('WD_eligible',result['elegibilidad']['WD']['estado'],'ELEGIBLE')
    check('no_confirmatory_dose_selection',result['dosis_confirmatorio_elegidas'],False)
    check('fraction_includes_070',next(r for r in result['conditions'] if r['brazo']=='WD' and r['dosis']==.2)['fraccion_c250_le_070'],1.)
    r=copy.deepcopy(records)
    for row in r:
        if row['brazo']=='LP' and row['dosis']==.001:row['c250']=.8
    value,_=summarize(r,conditions);check('inversion_rejected',value['elegibilidad']['LP']['criterio1_monotona_no_creciente'],False)
    r=copy.deepcopy(records)
    for row in r:
        if row['brazo']=='WD' and row['dosis']==4.:row['c250']=.5
    value,_=summarize(r,conditions);check('range_not_reached',value['elegibilidad']['WD']['criterio2_alcanza_c045_y_preserva_acc'],False)
    r=copy.deepcopy(records)
    for row in r:
        if row['brazo']=='LP' and row['dosis'] in (.1,.3):row['acc_panel250']=.75
    value,_=summarize(r,conditions);check('low_c_accuracy_loss_rejected',value['elegibilidad']['LP']['criterio2_alcanza_c045_y_preserva_acc'],False)
    r=copy.deepcopy(records)
    for row in r:
        if row['brazo']=='WD' and row['dosis']==.2:row['acc_panel250']=.875
    value,_=summarize(r,conditions);check('high_c_accuracy_rejected',value['elegibilidad']['WD']['criterio3_acc_preservada_si_c_ge_055'],False)
    r=copy.deepcopy(records)
    r[next(i for i,x in enumerate(r) if x['brazo']=='LP')]['status']='FAILED'
    value,_=summarize(r,conditions);q=next(x for x in value['conditions'] if x['brazo']=='LP')
    check('incomplete_median_unknown',q['c250'],None);check('incomplete_CI_unknown',q['IC95_mediana_c250'],None)
    check('incomplete_monotonicity_unknown',value['elegibilidad']['LP']['criterio1_monotona_no_creciente'],None)
    # One value per split replicated five times: independently construct bootstrap.
    r=copy.deepcopy(records)
    for row in r:
        if row['brazo']=='A0':row['c250']=(row['split']+1)/100
    value,_=summarize(r,conditions)
    g=np.random.default_rng(904001);draw=g.choice(100,size=(2000,100),replace=True)
    boot=np.median((draw+1)/100,axis=1)
    check('bootstrap_split_not_row',value['conditions'][0]['IC95_mediana_c250'],np.quantile(boot,[.025,.975]).tolist())
    return dict(status='PASS',tests=tests,synthetic_fixture_only=True)


def main():
    code_guard()
    p=Path(__file__)
    assert p.read_bytes()==subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(ROOT))],cwd=ROOT)
    summary=json.loads((OUT/'summary.json').read_text());pairing=json.loads((OUT/'pairing.json').read_text());control=json.loads((OUT/'controls.json').read_text())
    assert control['status']=='PASS' and pairing['status']=='PASS'
    conditions=[('A0',0.)]+[(a,d) for a in ('LP','WD') for d in CFG[a]]
    planned=[(a,d,s,k) for a,d in conditions for s in range(100) for k in range(5)]
    ids=[f'm2_{a}_d{d:g}_s{s:03d}_k{k}' for a,d,s,k in planned]
    with (OUT/'calibracion.csv').open(newline='') as f:
        reader=csv.DictReader(f);table=list(reader)
        assert reader.fieldnames==['id','brazo','dosis','split','k','c250','q250','acc_panel250','status','error']
    assert len(table)==7000 and [r['id'] for r in table]==ids and sha(OUT/'calibracion.csv')==summary['tabla_sha256']
    records=[json.loads((OUT/'records'/(name+'.json')).read_text()) for name in ids]
    assert sum(r['status']=='MEASURED' for r in records)==summary['measured']
    again,draws=summarize(records,conditions)
    for key in ('conditions','elegibilidad','dosis_confirmatorio_elegidas','bootstrap'):assert again[key]==summary[key]
    tests=unit_summary();write(STAGE/'unit_summary_v1.json',tests)
    manifest=[];cerror=0.;qerror=0.
    for r in records:
        if 'array' not in r:continue
        a=r['array'];p=Path(a['path']);assert p.is_relative_to(EXTERNAL) and sha(p)==a['sha256']
        manifest.append(a)
        with np.load(p,allow_pickle=False) as z:
            M=z['M'];assert M.shape==(27,27) and z['f'].shape==(27,2)
            diag=np.diag(M);c=float(diag.max()/np.trace(M));q=float(np.linalg.norm(M-np.diag(diag))/np.linalg.norm(M))
            cerror=max(cerror,abs(c-r['c250']));qerror=max(qerror,abs(q-r['q250']))
    assert cerror==0 and qerror==0
    b=json.loads((OUT/'bootstrap.json').read_text());assert sha(b['path'])==b['sha256'];manifest.append(b)
    with np.load(b['path'],allow_pickle=False) as z:assert np.array_equal(z['draws'],draws)
    with (STAGE/'external_manifest.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['path','sha256','bytes'],lineterminator='\n');w.writeheader();w.writerows(manifest)
    published=[]
    for line in (STAGE/'IMPLEMENTACION_v1.sha256').read_text().splitlines():
        h,n=line.split('  ',1);assert sha(STAGE/n)==h;published.append(n)
    assert not summary['dosis_confirmatorio_elegidas']
    flags={k:summary[k] for k in ('X_computed','rho_computed','D_computed','associations_computed','confirmatory_cohort_started')}
    assert all(v is False for v in flags.values())
    verify=dict(status='PASS',planned=7000,measured=summary['measured'],failed=summary['failed'],all_ids_present=True,
                all_record_arrays_SHA_verified=True,archived_M_c_q_max_error=[cerror,qerror],paired_data_initial_weights_batches=True,
                controls='PASS',summary_unit_tests=tests['status'],bootstrap_exact_shared_draws=True,bootstrap_unit='split',
                published_implementation_unchanged=True,protocol_unchanged=True,confirmatory_doses_selected=False,**flags)
    write(STAGE/'verification.json',verify)
    lines=['# DIN-Q13-M2 — calibración v1','',f"**{summary['measured']}/7000 ejecuciones medidas;{summary['failed']} fallidas.** Solo c250,q250,acc_panel250. No se seleccionan dosis confirmatorias.",'',
           '| Brazo | Dosis | Mediana c250 | IC95 mediana c | Mediana q250 | Mediana acc_panel250 | Fracción c≤.70 | medidas/fallos |',
           '|---|---:|---:|---|---:|---:|---:|---:|']
    for d in summary['conditions']:
        f=lambda x:'desconocido' if x is None else f'{x:.6f}'
        ci='desconocido' if d['IC95_mediana_c250'] is None else '['+', '.join(f(x) for x in d['IC95_mediana_c250'])+']'
        lines.append(f"| {d['brazo']} | {d['dosis']:g} | {f(d['c250'])} | {ci} | {f(d['q250'])} | {f(d['acc_panel250'])} | {f(d['fraccion_c250_le_070'])} | {d['measured']}/{d['failed']} |")
    lines+=['','## Criterios exactos del §5','', '| Manipulador | C1 monotonía | C2 rango y precisión | C3 precisión si c≥.55 | Resultado |', '|---|---|---|---|---|']
    for a,e in summary['elegibilidad'].items():
        label=lambda x:'desconocido' if x is None else 'cumple' if x else 'no cumple'
        lines.append(f"| {a} | {label(e['criterio1_monotona_no_creciente'])} | {label(e['criterio2_alcanza_c045_y_preserva_acc'])} | {label(e['criterio3_acc_preservada_si_c_ge_055'])} | {e['estado']} |")
        lines+=['',f"{a}: inversiones adyacentes={json.dumps(e['inversiones'],ensure_ascii=False)}; dosis que testimonian C2={e['dosis_testigo_criterio2']}; violaciones C3={json.dumps(e['violaciones_criterio3'],ensure_ascii=False)}."]
    lines+=['',f"Bootstrap percentil de2000 remuestreos de100 splits completos con sus cinco k, semilla904001. Draws compartidos entre condiciones. No son intervalos entre trayectorias independientes ni pruebas confirmatorias de monotonía. Comparaciones exactas con valores sin redondear; las cifras de esta tabla solo se redondean para leer.",
            '',f"Tiempo total de medición y resumen:{summary['seconds']:.3f}s;dos procesos de un hilo. Código publicado antes de medir en16139f48. Fuente de protocolo SHA:{CFG['sources']['protocol']['sha256']}.",
            '', 'Las dosis testigo de C2 son evidencia de un criterio, no elecciones para el confirmatorio. La regla de interpolación y cualquier selección corresponden al diseño posterior y al responsable. No se interpoló, amplió rejilla ni calcularon asociaciones. Las dos calibraciones Q13 anteriores permanecen intactas.',
            '', '[Tabla completa](results_v1/calibracion.csv) · [resumen íntegro](results_v1/summary.json) · [controles](results_v1/controls.json) · [pareado](results_v1/pairing.json) · [verificación](../verification.json) · [arrays por SHA](../external_manifest.csv).']
    # Report lives within results_v1's parent potencia-equivalent directory: fix links explicitly.
    text='\n'.join(lines)+'\n';text=text.replace('](../verification.json)','](verification.json)').replace('](../external_manifest.csv)','](external_manifest.csv)')
    (STAGE/'RESULTADO_v1.md').write_text(text)
    print(json.dumps(verify),flush=True)


if __name__=='__main__':main()
