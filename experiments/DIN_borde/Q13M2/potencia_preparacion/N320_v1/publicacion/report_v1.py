"""Verificación independiente de archivos simulados e informe de potencia."""
import collections
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[6]
STAGE=ROOT/'experiments/DIN_borde/Q13M2/potencia_preparacion/N320_v1'
sys.path.insert(0,str(STAGE/'scripts'))
from support import CFG,OUT,EXTERNAL,SOURCES,sha,write,code_guard,analyst
from power_v1 import wilson


def main():
    code_guard();p=Path(__file__)
    assert p.read_bytes()==subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(ROOT))],cwd=ROOT)
    M=analyst();summary=json.loads((OUT/'summary.json').read_text());scenario=json.loads((OUT/'scenario.json').read_text())
    controls=json.loads((OUT/'controls.json').read_text());assert controls['status']=='PASS'
    c=np.array(CFG['c']);manifest=[];records=[];max_beta_error=0.;max_ci_error=0.
    for r in summary['scenarios']:
        marginal={m:0 for m in ('LP','WD')};joint_count=0;counts={m:collections.Counter() for m in ('LP','WD')}
        for f in r['frames']:
            a=f['array'];p=Path(a['path']);assert p.is_relative_to(EXTERNAL) and sha(p)==a['sha256'];manifest.append(a)
            with np.load(p,allow_pickle=False) as z:
                assert z['D'].shape==(11,100) and z['bootstrap_D'].shape==(500,11,100)
                assert z['all_D'].shape==(1,2000,1100) and np.isfinite(z['all_D']).all()
                assert np.array_equal(z['bootstrap_draw'],np.random.default_rng(960001).choice(CFG['N'],size=(500,CFG['N']),replace=True))
                assert np.array_equal(z['targets'],np.maximum(0,np.array(CFG['target_raw'])))
                control=(z['D'][0]>0)&(z['p'][0]<.05)&(z['slopes'][0]>0)
                labels={}
                for m,nvs in M.MANIP.items():
                    ix=[CFG['levels'].index(nv) for nv in nvs]
                    # Independent OLS design, not the centered-slope implementation.
                    design=np.column_stack([np.ones(6),c[ix]])
                    raw=z['bootstrap_D'][:,ix,:].transpose(1,0,2).reshape(6,500*100)
                    beta=(np.linalg.pinv(design)@raw)[1].reshape(500,100)
                    err=float(np.max(np.abs(beta-z['bootstrap_beta_'+m])));max_beta_error=max(max_beta_error,err);assert err<=1e-10
                    ci=np.quantile(beta,[.0125,.9875],axis=0);err=float(np.max(np.abs(ci-z['IC975_beta_'+m])))
                    max_ci_error=max(max_ci_error,err);assert err<=1e-10
                    labels[m]=np.array(['INCONCLUSIVE_SIN_SENAL_CONTROL' if not control[i] else 'MODULA' if ci[0,i]>0 else 'NO_CONCLUYENTE' for i in range(100)])
                    assert np.array_equal(labels[m],z['labels_'+m]);marginal[m]+=int(np.sum(labels[m]=='MODULA'))
                    counts[m].update(labels[m].tolist())
                both=int(np.sum((labels['LP']=='MODULA')&(labels['WD']=='MODULA')))
                assert both==f['both_MODULA'];joint_count+=both
                assert both<=sum(labels['LP']=='MODULA') and both<=sum(labels['WD']=='MODULA')
        for m in marginal:
            assert wilson(marginal[m])==r[m] and dict(counts[m])==r['counts_'+m]
            records.append(dict(rho=r['rho'],target=m,**r[m]))
        assert wilson(joint_count)==r['both_MODULA'];records.append(dict(rho=r['rho'],target='LP_Y_WD',**r['both_MODULA']))
    with (STAGE/'potencia.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['rho','target','success','n','rate','lower','upper'],lineterminator='\n');w.writeheader();w.writerows(records)
    with (STAGE/'external_manifest.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['path','bytes','sha256'],lineterminator='\n');w.writeheader();w.writerows(manifest)
    check=dict(status='PASS_PREPARACION',N=CFG['N'],scenarios=4,replicates_per_scenario=400,frames=16,all_simulated_arrays_verified=True,
               bootstrap=500,primary_quantiles=[.0125,.9875],independent_OLS_beta_max_error=max_beta_error,independent_IC_max_error=max_ci_error,
               A0_single_response_reused=True,paired_bootstrap_shared_by_manipulators=True,joint_power_counted_not_multiplied=True,
               all_replications_preserved=True,D_statistics_not_clipped=True,only_target_positive_part_clipped=True,
               target_analyst_SHA=SOURCES['M2']['sha256'],analyst_still_draft=True,frozen_SHA_verification_or_repeat_required=True,
               real_cohort_D_computed=False,plan_generated=False,cohort_generated=False)
    write(STAGE/'verification.json',check)
    lines=['# DIN-Q13-M2 — potencia preparatoria N=320','',
        '**Preparación, no congelación del confirmatorio.** Se simulan400 réplicas por rho,con11 niveles y un A0 único compartido;500 bootstrap y1999 permutaciones. Las potencias incluyen inconclusas en el denominador.','',
        '| rho | MODULA LP: éxitos/400; potencia [Wilson95] | MODULA WD: éxitos/400; potencia [Wilson95] | Ambos MODULA: éxitos/400; potencia [Wilson95] |',
        '|---|---|---|---|']
    fmt=lambda a:f"{a['success']}/400; {a['rate']:.2%} [{a['lower']:.6f},{a['upper']:.6f}]"
    for r in summary['scenarios']:lines.append(f"| {r['rho']:g} | {fmt(r['LP'])} | {fmt(r['WD'])} | {fmt(r['both_MODULA'])} |")
    r=summary['scenarios'][0]
    lines+=['', '**Regla de preparación:** rho0 decide. Wilson inferior≥.8 por manipulador; la conjunta solo se reporta. '+('Ambos cumplen.' if r['meets_individual_rule'] else 'No cumplen ambos: reportar al responsable sin cambiar N ni generar plan.'),
            '',f"Tiempo total: {summary['seconds']:.3f}s; dos procesos de un hilo. Son estimaciones condicionales al modelo y soporte piloto, no una garantía de potencia en la cohorte futura ni certificado de error finito.",
            '', '## Generadora y efecto que queda tras truncar','',
            '`D_recta(c)=−0.038434071244996953+0.077c`; objetivo `d(c)=max(0,D_recta(c))`, autorizado antes de simular. Se recortan objetivos de varianza explicada, nunca los estadísticos D de las réplicas. La curva es lineal a tramos, no lineal en todo el rango.','',
            '| Nivel | c esperada | Recta sin truncar | Objetivo generador | Truncado |','|---|---:|---:|---:|---|']
    for p in scenario['points']:lines.append(f"| {p['level']} | {p['c']:.3f} | {p['raw']:.12f} | {p['target']:.12f} | {'sí' if p['truncated'] else 'no'} |")
    lines+=['','LP4 y WD4,c=.50: .000065928755>0,no se truncan,pero quedan prácticamente en cero. LP5(.40) y WD5(.438) sí se truncan.','',
            '| Manipulador | beta nominal | Pendiente MCO efectiva de seis objetivos | Rango c | beta efectiva×rango |','|---|---:|---:|---:|---:|']
    for m,e in scenario['effective'].items():lines.append(f"| {m} | .077 | {e['beta_effective']:.12f} | {e['c_range']:.3f} | {e['linear_contrast']:.12f} |")
    lines+=['','Ambas pendientes efectivas son menores que.077. WD tiene menor rango,pero su pendiente post-truncamiento es mayor que LP; su contraste ajustado a lo largo del rango es ligeramente menor. No se atribuye de antemano una menor potencia de WD solo a su rango. La potencia observada resuelve esa comparación en este modelo.','',
            'El truncamiento reduce la pendiente nominal respecto de la recta sin recortar. No se toma esto como una garantía matemática de conservadurismo para toda distribución o ajuste. La curvatura por tramos,los errores de muestra y la dependencia se preservan en las simulaciones.','',
            '## Método y alcance','',
            'Piloto G3s=.8 por SHA1364e8e7…:100 splits×5,se remuestrean splits completos en cuatro marcos de100 réplicas gaussianas. Solo se usan sus covariables y varianza residual de Y respecto de base cúbica de L. No se calcula D de ninguna cohorte real. Los seis D/c de LS se leen del resultado oficial ya publicado(SHA0f74669d…),no se recalculan desde su tabla.','',
            'Ruido con factor común y11 específicos:rho0/.3/.6/.615. Un solo A0 se genera y evalúa por réplica y se reutiliza en ambas pendientes. El bootstrap de500 draws(seed960001) comparte splits en los11 niveles y mantiene copias en su bloque original. La conjunta se cuenta como intersección,no producto de marginales.','',
            'La compuerta operacional se supone válida con c fijos y precisión/q apropiadas; la señal del control sí se evalúa con C1 exacto. Los fallos de control permanecen como inconclusos. d es objetivo nominal del generador gaussiano, no el valor esperado exacto del D estimado por CV en una muestra finita. No se vuelven a calibrar efectos para alcanzar una potencia deseada.','',
            'Los motores agrupados se contrastaron con el analista M2 completo solo en dos tablas sintéticas,N20/N40: D,p,réplicas,IC97.5 y etiquetas individuales/conjuntas. p idénticos; errores numéricos<1e−10. Se verificaron todas las16 salidas y sus pendientes mediante una MCO independiente.','',
            f"**Referencia provisional:** PR#114,commit66f5de58,analista SHA`{SOURCES['M2']['sha256']}`. Sigue siendo borrador. Al congelar hay que cotejar el SHA y demostrar equivalencia del estimando o repetir la potencia. Esta preparación no autoriza plan o cohorte.",
            '', '[Potencias CSV](potencia.csv) · [Resumen y conteos completos](results_v1/summary.json) · [Controles](results_v1/controls.json) · [Verificación](verification.json) · [Arrays por SHA](external_manifest.csv) · [Procedimiento previo](PROCEDIMIENTO_v1_CONGELADO.md) · [Decisión de truncamiento](DECISION_TRUNCAMIENTO.md).']
    (STAGE/'RESULTADO_v1.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(check),flush=True)


if __name__=='__main__':main()
