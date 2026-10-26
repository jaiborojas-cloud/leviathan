"""Presentación de TODAS las estimaciones ya archivadas; no nuevos contrastes."""
import csv
import json
from pathlib import Path
import numpy as np
from support_v1 import STAGE,RUN,CFG,write,code_guard,guard


def fmt(value,digits=6):
    if value in [None,'']:return '—'
    return f'{float(value):.{digits}f}'


def main():
    code_guard();guard()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows=list(csv.DictReader((RUN/'estimates.csv').open()))
    result=json.loads((RUN/'analysis.json').read_text());verification=json.loads((STAGE/'verification.json').read_text())
    if verification['status']!='PASS':raise RuntimeError('No presentar corrida inválida')
    pick=lambda group,cand,out='test_loss_250':next(r for r in rows if r['dataset']==str(group) and r['candidate']==cand and r['outcome']==out)
    candidate_names=[c['name'] for c in CFG['candidates']]
    primary=[pick(2,c) for c in candidate_names];chosen=pick(2,'c_30')
    lines=['# DIN-D9g — conclusión exploratoria','',f"**{result['verdict']}**: proponer **c(u30)** al responsable para un confirmatorio; no se ejecuta ni se congela ese confirmatorio aquí.",'',
        'En G3, s=.8, c(u30) añade predicción de la pérdida test250 sobre la base LINEAL de pérdida train30, pérdida y precisión panel30 y X30. '
        'D=0.021854, p exploratorio=0.0009995 (<.05/12), con pendiente negativa en ambas mitades prefijadas. '
        'Es una reducción del **2.185% del SSE restante de la base**, dentro de la variación entre inicializaciones del mismo split. '
        'No es una reducción del 2.185% de la pérdida test ni una confirmación de la hipótesis.','',
        'La pendiente ajustada es −0.040886 por unidad de c: a medidas baratas fijas, mayor concentración se asocia a MENOR pérdida test; '
        'no se afirma que inducir colapso mejore la generalización. Sin base, c30 tiene D=−0.000885. '
        'El hallazgo es condicional a ese ajuste, no una asociación marginal ni información nueva sobre toda función de las medidas baratas.','',
        '## Primaria completa: s=.8, pérdida test250','',
        '100 splits×5 inicializaciones, 500/500 filas; once candidatos, sin exclusiones.','',
        '| Candidato | Base en u | D adicional | p exploratorio | β par | β impar | ¿regla completa? |',
        '|---|---:|---:|---:|---:|---:|---|']
    for r in primary:lines.append(f"|{r['candidate']}|{r['time']}|{fmt(r['D'])}|{fmt(r['p_exploratorio'])}|{fmt(r['beta_even'])}|{fmt(r['beta_odd'])}|{'sí' if r['propose']=='True' else 'no'}|")
    lines += ['', 'La regla anterior a medir exige D>.02, p<.05/12 y el mismo signo en mitades par/impar (y ajuste completo). '
        'Sólo c30 la cumple en s=.8. **Errata resuelta ANTES del código:** eran 11, no 12; el responsable conservó /12 y prohibió añadir Δc10→30, suma de los otros dos incrementos.', '',
        '## Estabilidad y controles de c30 en s=.8','',
        f"- Base barata sola frente a cero: D_base={fmt(chosen['D_base'])}.",
        f"- c30 solo frente a cero: D_solo={fmt(chosen['D_candidate_alone'])}.",
        f"- Pendiente completa={fmt(chosen['beta'])}; pares={fmt(chosen['beta_even'])}, impares={fmt(chosen['beta_odd'])}.",
        f"- D adicional en mitades: pares={fmt(chosen['D_even'])}, impares={fmt(chosen['D_odd'])}. Las mitades no superan .02; la regla exige estabilidad de SIGNO, no ese umbral en cada mitad.",
        '- 2.000 permutaciones dentro del split, p con corrección +1 y empates 1e-15; no se repitieron semillas ni se buscaron particiones.', '',
        '## Otros niveles y agregado, descriptivos','',
        '| Conjunto | D c30 | p | β | candidatos que cumplen el umbral de referencia |',
        '|---|---:|---:|---:|---|']
    for dataset,label in [(0,'s=.25'),(1,'s=.5'),(2,'s=.8'),('aggregate','agregado')]:
        r=pick(dataset,'c_30');hits=[x['candidate'] for x in rows if x['dataset']==str(dataset) and x['outcome']=='test_loss_250' and x['meets_reference_rule']=='True']
        lines.append(f"|{label}|{fmt(r['D'])}|{fmt(r['p_exploratorio'])}|{fmt(r['beta'])}|{', '.join(hits) or 'ninguno'}|")
    lines += ['', 's=.25/.5 y agregado no cambian la selección primaria. El agregado centra/permutan en (nivel,split) y bloquea por split compartido, '
        'sin tratar 300 paneles emparejados como 300 splits independientes. Tiene pendientes comunes y no sustituye las estimaciones por nivel. '
        'La presencia descriptiva de c30 también en niveles que G3 no clasificó como colapso no prueba necesidad del régimen.', '',
        '## Desenlaces secundarios, c30 en s=.8','',
        '| Desenlace | D adicional | p exploratorio | β |',
        '|---|---:|---:|---:|']
    for name,label in [('test_loss_250','pérdida test (primario)'),('test_accuracy_250','precisión test'),('gap_loss_250','brecha test−train')]:
        r=pick(2,'c_30',name);lines.append(f"|{label}|{fmt(r['D'])}|{fmt(r['p_exploratorio'])}|{fmt(r['beta'])}|")
    lines += ['', 'Los secundarios no deciden. Se conservan las 132 celdas y ambos controles D para todos los candidatos, incluso negativos o desconocidos, '
        'en [estimates.csv](results/run_v1/estimates.csv); [salida completa](results/run_v1/analysis.json). No se elige un desenlace tras medir.', '',
        '## Controles, datos y conservación','',
        'Se restauraron 7.500 checkpoints de 1.500 trayectorias G3; **error máximo de reproducción 0** en pérdida/precisión train/panel y X. '
        '300 test de 3.000 ejemplos (1.000/clase), seeds711000..711099, normalización exclusivamente train archivada; ruido test emparejado entre niveles. '
        'No reentrenamiento ni nueva medición de rho: se reutilizan G3 y r3 intactos.', '',
        'Controles FWL: cuatro tablas, todos los D de 2.000 permutaciones contra OLS directo; p idéntica, errorD máximo1.11e-15; '
        'contraste adicional con D_cv C1 original. Casos de alias/constante identificados; guarda bloquea C2/T2 antes de leer. '
        f"[verification.json](verification.json): **PASS**, {verification['external_files_verified']} archivos externos por SHA, 1.500 registros reversibles y 132 celdas. No hubo fallos ni enmiendas de implementación.", '',
        'Se conservan todos los logits/pérdidas test por ejemplo, test sintético, pesos originales por referencia/SHA, datos, escalares, '
        'D nulos/SSE completos, metadatos y tiempos. Arrays fuera de Git: [manifest externo](external_manifest.csv); '
        'los [shards](results/run_v1/record_shards/) restauran bit por bit sin borrar originales.', '',
        '## Demostración, evidencia y siguiente paso','',
        'La construcción algebraica M=R(F+γI)^−1Rᵀ y los residuos de confianza son identidades del instrumento. '
        'La relación ajustada de c30 con TEST es evidencia empírica exploratoria; no se deduce de esas identidades. '
        'El test grande sigue siendo una muestra finita, compartida entre las cinco inicializaciones de cada split; se guardan errores estándar descriptivos estratificados. '
        'El centrado de Y usa la media final del split completo: mide variación entre inicializaciones, no un predictor desplegable sin esas medias.', '',
        'Proponer al responsable un diseño confirmatorio específico para **c30 + base barata u30 → pérdida test250**, con signo ajustado esperado negativo. '
        'Fijar antes tamaño/potencia, semillas de test, estimando y script; no usar D observado sin descontar selección exploratoria. '
        '**C2 permanece intacta y reservada** como posible cohorte: no se abrió ningún estado/checkpoint/tabla de C2 ni se calculó su test o asociación. '
        'La decisión de cohorte y de congelación corresponde al responsable.', '',
        'No se afirma causalidad, necesidad del colapso, mejora sobre bases flexibles, certificado geométrico ni transferencia a Wine/Iris/datos reales. '
        'La corrección /12 sólo rige la regla primaria fijada; el resto es descriptivo, no una familia confirmatoria nueva. '
        'No se calculó potencia prospectiva de D9g; la potencia G3 era de otro estimando y no se transfiere. '
        'El efecto observado D=.02185 supera por poco .02; requiere réplica independiente.', '',
        '[Diseño](DESIGN_FROZEN.md) · [configuración](config.json) · [teoría](THEORY.md) · [reproducción](REPRODUCCION.md).']
    with (STAGE/'CONCLUSION.md').open('x') as file:file.write('\n'.join(lines)+'\n')
    fig,axes=plt.subplots(2,2,figsize=(13,9),sharex=True,layout='constrained')
    for ax,dataset,label in zip(axes.ravel(),[0,1,2,'aggregate'],['s=0.25','s=0.5','s=0.8: primaria','Agregado: descriptivo']):
        values=[pick(dataset,c) for c in candidate_names];ds=[float(r['D']) for r in values]
        colors=['#c45532' if r['meets_reference_rule']=='True' else '#326d91' for r in values]
        ax.bar(range(11),ds,color=colors,width=.7);ax.axhline(0,color='#555',lw=.8);ax.axhline(.02,color='#c45532',ls='--',lw=1)
        ax.set_title(label);ax.set_ylabel('D adicional sobre base barata');ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
        ax.set_xticks(range(11),['c10','log tr10','log ρ10','c20','log tr20','log ρ20','c30','log tr30','log ρ30','Δc10–20','Δc20–30'],rotation=60,ha='right')
    fig.suptitle('D9g · pérdida test250 · 11 candidatos · 2.000 permutaciones\nNaranja: D>.02, p<.05/12 y signo estable; sólo s=.8 permite proponer',fontsize=12)
    folder=STAGE/'figures';folder.mkdir(exist_ok=False)
    fig.savefig(folder/'incremento_geometria.png',dpi=160);fig.savefig(folder/'incremento_geometria.svg');plt.close(fig)
    print('PASS: conclusión y figura de todos los candidatos, sin nuevos contrastes')

if __name__=='__main__':main()
