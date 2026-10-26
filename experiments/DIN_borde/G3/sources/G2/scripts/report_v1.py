"""Entrega documental desde las salidas congeladas; no mide ni entrena."""
import json
import math
from support_v1 import STAGE, RUN, write


def fmt(v, digits=4):
    if v is None or not isinstance(v, (int, float)) or not math.isfinite(v):
        return '—'
    return f'{v:.{digits}f}'


def main():
    data = json.loads((RUN/'analysis.json').read_text())
    verification = json.loads((STAGE/'verification.json').read_text())
    execution = json.loads((RUN/'execution.json').read_text())
    rule = data['H_var']
    meaning = {
        'APOYO_DESCRIPTIVO': 'La cohorte cumple el patrón prefijado; no constituye confirmación ni identifica causalidad.',
        'CONTRADICE_DESCRIPTIVAMENTE': 'La cohorte cumple la regla de patrón inverso. No establece una ausencia universal de señal ni contradice las identidades de M.',
        'NO_APOYO_DESCRIPTIVO': 'Hubo variación suficiente, pero el patrón no cumplió el apoyo ni la contradicción prefijados.',
        'INDETERMINADO': 'La manipulación o las compuertas no permitieron dirimir H-var. No se amplió la rejilla ni se seleccionaron niveles después de medir.'}
    lines = [
        '# DIN-G2 · conclusión exploratoria', '', f"**H-var: {rule['verdict']}.** {meaning[rule['verdict']]}", '',
        'Los datos son exclusivamente mezclas gaussianas sintéticas. Se conservaron',
        f"600 trayectorias planificadas y4200 visitas; visitas inválidas: **{data['invalid_states']}**.",
        'La lectura de Wine/DIN-C1/D7/G1 se limitó a informes agregados y código',
        'permitido. No se cargó Wine, Iris ni datos T2/DIN-C1; no cambia ningún',
        'estado anterior. Primaria rho_caras; rho_vert secundaria, sin rescatar la primaria.', '',
        '## Resultados por nivel', '',
        '| s | Mal250 | V intra-split | D_X | beta X | D_X condicionado a R | fracción retirada | p exploratorio | D_X vert secundario |',
        '|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for l in data['levels']:
        a, b = l['primary'], l['secondary']
        c, d = a.get('C1_exact', {}), a.get('D7_conditional_R', {})
        lines.append('|'+ '|'.join([f"{l['s']:g}", fmt(l['mal_fraction']), fmt(l['V']), fmt(c.get('D')),
             fmt(c.get('pendiente_X')), fmt(d.get('D')), fmt(a.get('fraction_removed_descriptive')),
             fmt(c.get('p_exploratorio'), 3), fmt(b.get('C1_exact', {}).get('D'))])+'|')
    lines += ['', 'Mal es la clasificación errónea del dominante final k*=argmax diag M.',
        'V es la media de p_split(1−p_split) con cinco inicializaciones por split;',
        'máximo empírico.24. No mide la resolución del mismo individuo entre inicios:',
        'la identidad del dominante puede cambiar. Las p usan999 permutaciones y son',
        '**exclusivamente exploratorias**: no deciden el veredicto ni confirman nada.', '',
        '## Aplicación de la regla previa', '',
        f"- Spearman entre los seis D y V: **{fmt(rule.get('spearman_D_V'))}**.",
        f"- Manipulación suficiente: **{rule.get('manipulation', False)}**; niveles altos: {rule.get('high_levels', [])}, bajos: {rule.get('low_levels', [])} (índices0–5).",
        f"- Ganadores de D: {rule.get('peak_levels', [])}; ganadores que cumplen máximo interior y V alta: {rule.get('qualifying_peak_levels', [])}.",
        f"- Media D(alta V)−media D(baja V): **{fmt(rule.get('mean_D_high_minus_low'))}**.",
        f"- Motivo adicional: {rule.get('reason', 'Se aplican exactamente los umbrales congelados, sin usar p para decidir.')}.", '',
        'Apoyo exigía correlación≥.6, máximo interior con D≥.02 y beta positiva',
        'cerca del máximo V, y diferencia media≥.02. Contradicción exigía el patrón',
        'inverso definido en el diseño. Una ausencia de p significativa no se convierte',
        'en contradicción; un secundario favorable tampoco rescata la primaria.', '',
        '## Calidad y régimen de entrenamiento', '',
        '| s | pares válidos | compuerta | mediana maxdiag/tr | mediana q | mediana acc train250 | mediana acc panel250 | frecuencia modal k* intra-split |',
        '|---:|---:|---|---:|---:|---:|---:|---:|']
    for l in data['levels']:
        a=l['primary']
        lines.append('|'+ '|'.join([f"{l['s']:g}", str(a['valid_pairs']), a['gate'], fmt(l['median_c250']),
          fmt(l['median_q250']), fmt(l['train_acc250']), fmt(l['val_acc250']),fmt(l['modal_dominant_fraction'])])+'|')
    lines += ['', 'D_X es el estimando C1 original: base cúbica centrada intra-split, diez',
        'bloques de splits, semillas260010/260001. Se reutilizan sus funciones',
        'sin ejecutar el CLI ni leer su cohorte. D_X|R añade Rc linealmente a la',
        'misma base y conserva los bloques. R se mide en250: es descomposición',
        'descriptiva, no predictor disponible en10 ni mediador causal identificado.',
        'La fracción retirada sólo se define si D_X>.01 y no se recorta a[0,1].', '',
        '## Identidad algebraica frente a evidencia', '',
        'M=R_grad(F+gamma I)⁻¹R_gradᵀ es identidad de construcción; el factor',
        '(1−p_y) de los gradientes también. La aproximación n·diag(odds) requiere',
        'rango interpolante y ridge despreciable; no obliga al colapso ni a una',
        'señal temporal. Los patrones de D y V de esta cohorte son evidencia empírica',
        'exploratoria, no una consecuencia demostrada de esa identidad.', '',
        '## Conservación y controles', '',
        f"Verificación: **{verification['status']}**. Controles de triángulo, cara26,",
        'generador y reproducción independiente de D/p en cuatro tablas sintéticas',
        'aprobados. Las tres reconstrucciones prefijadas de M desde pesos tienen',
        'error relativo cero; no se reentrenó ni se volvió a medir rho para ello.',
        f"Archivos externos verificados por SHA: {verification['external_files_verified']};",
        'incluyen4200 checkpoints,4200 matrices/score arrays,4200 diagnósticos rho',
        'completos y140 archivos base/particiones. Se conservan todos los fallos,',
        'errores de cuadratura/restos y snapshots; no se sobrescriben archivos.',
        f"Tiempo de cohorte: {execution['seconds']:.2f}s, dos procesos CPU/BLAS1.",
        'Diseño538120b → código7e6c715 → controles/entrenamientos/mediciones.',
        'Fuente I2 r3 SHA2ac015a2, geometry b4d1e0e4 y core b5251d2f intactas.', '',
        '## Límites y siguiente paso', '',
        'Sólo seis niveles con20 réplicas sintéticas y cinco inicios; los niveles',
        'comparten ruido/pesos/lotes. La correlación entre seis agregados es inestable',
        'y no constituye una confirmación independiente. El ruido modifica Fisher,',
        'gradientes y generalización simultáneamente: no aísla un mecanismo causal.',
        'La clasificación binaria no agota la variación de confianza continua R.',
        'D compara una base cúbica concreta, no toda función de L; centrar Y requiere',
        'las medias de los splits completos. rho es una estimación sin certificado',
        'de óptimo global ni intervalos. No se afirma transferencia a datos reales.',
        'Un siguiente estudio necesitaría réplicas nuevas y diseño previo: no elegir',
        'niveles, arquitectura o visita usando este mismo conjunto como confirmación.', '',
        '[Diseño](DESIGN_FROZEN.md) · [teoría](THEORY.md) · [análisis íntegro](results/run_v1/analysis.json) ·',
        '[tabla6 niveles](results/run_v1/levels.csv) · [tabla600 trayectorias](results/run_v1/trajectories.csv) ·',
        '[tabla4200 visitas](results/run_v1/states.csv) · [variancias por split](results/run_v1/split_variance.csv) ·',
        '[fallos](results/run_v1/failures.json) · [verification](verification.json) · [manifest](manifest.csv).', '',
        '![Resolución y señal temprana](figures/resolucion.png)', '',
        '[SVG exportable](figures/resolucion.svg). Agregados descriptivos, sin intervalos de confianza.', '']
    text = '\n'.join(lines)
    with (STAGE/'CONCLUSION.md').open('x') as f:
        f.write(text)
    write(RUN/'report_provenance.json', dict(analysis='analysis.json', verdict=rule['verdict'], figures='figures/resolucion.png'))


if __name__ == '__main__':
    main()
