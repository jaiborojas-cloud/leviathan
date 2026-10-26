"""Informe documental desde análisis final; no reentrena ni mide geometría."""
import json
import math
from support_v1 import STAGE, RUN, CFG


def f(v, digits=4):
    return '—' if v is None or not isinstance(v, (int, float)) or not math.isfinite(v) else f'{v:.{digits}f}'


def main():
    data = json.loads((RUN/'analysis.json').read_text())
    verification = json.loads((STAGE/'verification.json').read_text())
    power = json.loads((STAGE/'results/power_v1/summary.json').read_text())
    execution = json.loads((RUN/'execution.json').read_text())
    reading = data['reading']
    interpretation = {
      'SENAL_PRESENTE_FUERA_DE_WINE_DESCRIPTIVA': 'Al menos un nivel con colapso operacional cumple la primaria. Es una señal exploratoria en este sintético; no transferencia a datos reales ni confirmación de DIN-C1.',
      'AUSENTE_CON_POTENCIA_SIMULADA_DESCRIPTIVA': 'No se detecta señal con la regla previa, con potencia simulada suficiente para el tamaño.026. No demuestra el nulo, ausencia de efectos menores ni equivalencia. La lectura de colapso se limita a los niveles que lo cumplen.',
      'INDETERMINADO_PARA_COLAPSO': 'El patrón no permite la lectura global de señal en colapso prevista. Se conservan los resultados por nivel, sin rescatar la primaria por secundarios ni por selección de individuos.'}
    text = ['# DIN-G3 · conclusión exploratoria', '', '**'+reading['verdict']+'**.', interpretation[reading['verdict']], '',
       f"Se completó el universo previsto de{CFG['planned_trajectories']} trayectorias y{CFG['planned_states']} visitas; inválidas:{data['invalid_states']}.",
       f"{len(CFG['splits'])} splits nuevos×5 inicios por nivel, s=.25/.5/.8. Primaria rho_caras de I2 r3 intacto.",
       'Los niveles se eligieron mirando G2, declarado antes del código. Las semillas y',
       'observaciones de cohorte son nuevas; G2 sólo fue piloto de planificación.', '',
       '## Potencia fijada antes de entrenar', '',
       '| s | potencia .015 | potencia .020 | potencia .026 | Wilson inferior95% .026 | falsos PASS nulo |',
       '|---:|---:|---:|---:|---:|---:|']
    for l in power['candidates'][-1]['levels']:
        e = l['estimates']
        text.append('|'+ '|'.join([f(l['s'], 2),f(e[1]['rate']),f(e[2]['rate']),f(e[3]['rate']),f(e[3]['lower']),f(e[0]['rate'])])+'|')
    text += ['', '400 réplicas/nivel/efecto,1999 permutaciones C1 por réplica; cuatro',
       'soportes bootstrap del piloto,100 ruidos Gaussianos cada uno. Primer tamaño',
       'válido:100 splits. Se exigió límite inferior Wilson≥.8 para.026 y límite',
       'superior del nulo≤.10 en los tres niveles. Los tamaños mayores no se probaron.',
       'La equivalencia FWL/C1 pasó en cuatro tablas con p idéntica y errorD≤1e-10.',
       'D_obj es oráculo bajo el modelo; elD CV medio finito se publica por separado.',
       '**Potencia condicional a ruido Gaussiano y soporte piloto**, no garantía',
       'universal ni intervalo de un efecto de la cohorte observada.', '',
       '## Primaria y régimen por nivel', '',
       '| s | pares | D | p exploratorio | beta X | veredicto | mediana c250 | mediana q250 | régimen |',
       '|---:|---:|---:|---:|---:|---|---:|---:|---|']
    for l in data['levels']:
        a=l['primary']; c=a.get('C1_exact', {})
        text.append('|'+ '|'.join([f(l['s'],2),str(a['valid_pairs']),f(c.get('D')),f(c.get('p_exploratorio'),4),
           f(c.get('pendiente_X')),a['verdict'],f(l['median_c250']),f(l['median_q250']),l['regime']])+'|')
    text += ['', 'PASS_DESCRIPTIVO requiere p<.05,D>0,beta>0, con compuerta válida. Colapso',
       'operacional requiere mediana c≥.8 y mediana q≤.05. No se filtran individuos',
       'por colapso para cambiar el ajuste ni se presupone el régimen por s.',
       'Se reutilizan cen,D_cv,primaria de C1 sin cambios: base cúbica, centrado',
       'intra-split,10 bloques/260010,1999 permutaciones dentro del split/260001.',
       'La primaria mejora a esa base concreta, no a toda función de log rho10.', '',
       f"Niveles elegibles para colapso:{reading['eligible_collapse_levels']}; PASS primarios:{reading['detected_levels']};",
       f"PASS en colapso:{reading['detected_in_collapse']} (índices0–2).",
       'La lectura de ausencia exige todos NOT_MET, pares completos y potencia',
       'simulada suficiente, y sigue sin ser una prueba de equivalencia.', '',
       '## Resolución continua y clasificación binaria secundaria', '',
       '| s | V_cont | V_bin | k* mal250 | fracción individual colapsada | acc panel250 mediana | frecuencia modal k* |',
       '|---:|---:|---:|---:|---:|---:|---:|']
    for l in data['levels']:
        text.append('|'+ '|'.join([f(l['s'],2),f(l['V_cont'],6),f(l['V_bin']),f(l['mal_fraction']),
            f(l['collapsed_fraction']),f(l['val_acc250']),f(l['modal_dominant_fraction'])])+'|')
    text += ['', 'V_cont=media de varianzas poblacionales de los cinco R250 por split;',
       'R=log(1−p_y(k*(250))). La clasificación puede ser constante y la confianza',
       'variar. La identidad k* puede cambiar; no es un individuo común preseleccionado.',
       f"Spearman entre D yV_cont: **{f(reading['spearman_D_Vcont'])}**, sólo TRES niveles.",
       'No hay p de esa tendencia ni contraste de dependencia causal; se informa',
       'qué niveles cumplen colapso para evitar mezclar regímenes sin advertirlo.', '',
       '## Secundarios prefijados', '',
       '| s | D_X condicionado R | fracción descriptiva retirada | D vert | p vert exploratorio | veredicto vert | W_adj legado | p legado exploratorio |',
       '|---:|---:|---:|---:|---:|---|---:|---:|']
    for l in data['levels']:
        a,b=l['primary'],l['secondary']; d=a.get('D7_conditional_R',{});c=b.get('C1_exact',{});w=a.get('W_adj_legacy',{})
        text.append('|'+ '|'.join([f(l['s'],2),f(d.get('D')),f(a.get('fraction_removed_descriptive')),
           f(c.get('D')),f(c.get('p_exploratorio'),4),b['verdict'],f(w.get('W')),f(w.get('p_exploratorio'),4)])+'|')
    text += ['', 'D7 añade Rc lineal a la misma base y conserva los diez bloques; R se mide',
       'en250 y no está disponible en10. La razón1−Dcond/D sólo existe siD>.01,',
       'sin recorte, y compara bases/SSE diferentes: no es fracción causal mediada.',
       'W_adj es LEGADO (residuo Y lineal sobre L y rangos conX): no prueba nueva',
       'información condicional y no rescata un NOT_MET, según el contraejemplo D2b.', '',
       '## Identidad algebraica y límites', '',
       'M=R_grad(F+gamma I)⁻¹R_gradᵀ y el factor residual1−p_y son identidades',
       'del instrumento. La aproximación n·diag(odds) exige rango interpolante',
       'y ridge despreciable; no obliga a colapso ni a una señal temporal.',
       'D,V_cont y los veredictos de la cohorte son hallazgos empíricos, no identidades.',
       'La planificación reutiliza G2 para elegir niveles/escala, no como cohorte G3.',
       'Hay tres análisis exploratorios y una tendencia de tres puntos; incluso un',
       'PASS con semillas nuevas no se llama confirmatorio. Sin transferencia a',
       'Wine/Iris/datos reales, causalidad, certificado de mínimo de rho o intervalos.',
       'El centrado Y del estimando usa las medias de splits completos; no es por',
       'sí solo un predictor operativo con medias finales desconocidas.', '',
       '## Controles, conservación y cronología', '',
       f"verification.json: **{verification['status']}**;{verification['state_count']} registros,{verification['trajectory_count']} trayectorias,",
       f"{verification['external_files_verified']} archivos externos conSHA. Fuentes intactas; sólo G3 modificado.",
       'Controles triángulo/cara26,r3,generador,C1 y semillas disjuntas PASS.',
       'Tres reconstrucciones M desde pesos prefijadas: error relativo0,f idéntica,',
       'sin reentrenar ni repetir rho. Se conservan fallos y outputs desconocidos.',
       'Metadatos originales en shardsJSONL reversibles; arrays, pesos, RNG/Adam,',
       'diagnósticos rho y simulaciones de potencia fuera de Git conSHA.',
       f"Tiempo cohorte:{execution['seconds']:.2f}s, dos procesos CPU/BLAS1.",
       'Diseño7bce1dc → código potencia3f01bc7 → potencia → tamaño1e88d2b →',
       'código cohorte2048dd4 → controles/entrenamientos/mediciones. No cambian',
       'el cierre de C1 ni G1/G2 ni instrumentos congelados.', '',
       '[Diseño](DESIGN_FROZEN.md) · [tamaño](SAMPLE_FROZEN.md) · [potencia](results/power_v1/power_table.csv) ·',
       '[análisis completo](results/run_v1/analysis.json) · [niveles](results/run_v1/levels.csv) ·',
       '[trayectorias](results/run_v1/trajectories.csv) · [visitas](results/run_v1/states.csv) ·',
       '[verificación](verification.json) · [manifest](manifest.csv).', '',
       '![Potencia y señal](figures/potencia_senal.png)', '', '[SVG exportable](figures/potencia_senal.svg).', '']
    with (STAGE/'CONCLUSION.md').open('x') as file:
        file.write('\n'.join(text))


if __name__ == '__main__':
    main()
