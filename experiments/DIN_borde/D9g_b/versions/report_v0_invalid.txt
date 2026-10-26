"""Presenta las 16 celdas archivadas; ninguna base o prueba nueva."""
import csv
import json
from support_v1 import STAGE,RUN,CFG,code_guard,guard


def f(x,n=6):return '—' if x in [None,''] else f'{float(x):.{n}f}'


def main():
    code_guard();guard()
    rows=list(csv.DictReader((RUN/'estimates.csv').open()));a=json.loads((RUN/'analysis.json').read_text());v=json.loads((STAGE/'verification.json').read_text());ctrl=json.loads((RUN/'controls.json').read_text())
    if v['status']!='PASS':raise RuntimeError('No presentar corrida inválida')
    pick=lambda dataset,base:next(r for r in rows if r['dataset']==str(dataset) and int(r['base'])==base)
    primary=[pick(2,b) for b in [1,2,3,4]]
    lines=['# DIN-D9g-b — conclusión exploratoria','',f"**{a['verdict']}**, según la regla congelada: en s=.8, B3 y B4 tienen D≤0. **c30 no conserva el incremento fuera de muestra con las bases flexibles fijadas.**",'',
        '**La etiqueta es operacional.** No demuestra que una no linealidad barata sea la causa única del resultado D9g. '
        'B3/B4 predicen peor que B1 como bases solas y las mitades muestran D inestables. Es compatible con sobreajuste/variabilidad de las bases no regularizadas, '
        'además de posible redundancia de c30. No se separan esas explicaciones aquí.','',
        '## s=.8: las cuatro bases prefijadas','',
        '| Base | Términos | D adicional c30 | p exploratorio | β c30 | D_base sola | β pares / impares | ¿D>.01, p<.0125 y signo? |',
        '|---|---|---:|---:|---:|---:|---|---|']
    labels={1:'4 lineales',2:'+ cuadrados/cubos (12)',3:'+ 6 interacciones (18)',4:'+ margen/entropía/norma (21)'}
    for r in primary:lines.append(f"|B{r['base']}|{labels[int(r['base'])]}|{f(r['D'])}|{f(r['p_exploratorio'])}|{f(r['beta'])}|{f(r['D_base'])}|{f(r['beta_even'])} / {f(r['beta_odd'])}|{'sí' if r['meets']=='True' else 'no'}|")
    lines += ['', 'B1 reproduce D9g (D=.02185384449, p=.00099950025); no se invalida ni reescribe esa conclusión previa sobre una base lineal. '
        'B2/B3/B4 no cumplen la regla de robustez: el incremento es negativo en las tres. Las pendientes siguen negativas y de signo estable; '
        'esa estabilidad de coeficiente no basta para mejorar predicción fuera de muestra.','',
        'La caída del rendimiento de las bases solas es material: D_base=.075126→.063988→.019266→.011801. '
        'No se observa que estas bases flexibles predigan mejor y dejen a c30 sin información. Las bases están anidadas en entrenamiento; '
        'su error de CV puede empeorar por estimación y extrapolación. Por eso «artefacto» no debe leerse como demostración de absorción de no linealidad.', '',
        '## Mitades prefijadas en s=.8','',
        '| Base | D adicional pares | D adicional impares | signo β estable |',
        '|---|---:|---:|---|']
    for r in primary:lines.append(f"|B{r['base']}|{f(r['D_even'])}|{f(r['D_odd'])}|{r['half_sign_stable']}|")
    lines += ['', 'Las mitades flexibles difieren marcadamente en D; no se escogen particiones ni se descartan splits. '
        'Rangos efectivos en s=.8:4,12,18,21; condición máxima de términos no nulos≈2.19,19.90,37.86,38.20 respectivamente. '
        'No aparece pérdida de rango de la base en ese nivel. Los controles numéricos distinguen error de implementación de inestabilidad estadística.', '',
        '## Otros niveles y agregado: sólo descriptivos','',
        '| Conjunto | B1 D / p | B2 D / p | B3 D / p | B4 D / p |',
        '|---|---|---|---|---|']
    for dataset,label in [(0,'s=.25'),(1,'s=.5'),(2,'s=.8, decide'),('aggregate','agregado')]:
        values=[pick(dataset,b) for b in [1,2,3,4]]
        lines.append('|'+label+'|'+'|'.join(f"{f(r['D'])} / {f(r['p_exploratorio'])}" for r in values)+'|')
    lines += ['', 'Ningún conjunto cumple robustez con todas las bases flexibles. s=.25/.5 y agregado no cambian la decisión primaria. '
        'El agregado centra/permutan en (nivel,split) y deja los tres niveles del mismo split juntos en cada bloque; pendientes comunes. '
        'Se conservan los 16 resultados, coeficientes, mitades, controles D_base y transformaciones por bloque.', '',
        '## Controles e integridad','',
        '- Positivo con señal residual independiente: D≈.761/.904/.929/.930 para B1–B4, p=.000500 en las cuatro, pendiente positiva estable. '
        'Demuestra detección de una señal grande; no demuestra potencia para D≈.01–.02.',
        '- Negativo: c_hat_j de la MISMA base B_j, ajustado sólo en entrenamiento. |D|≤2.22e-16 en controles artificiales y ≤1.33e-15 en las 16 celdas reales. '
        'Coeficiente no identificable por alias; no se interpreta como efecto cero estimado.',
        '- Función barata no lineal: c=q0², Y=q0²+ruido. D≈.995 con B1 y |D|<3e-15 con B2–B4. '
        'Una función de medidas baratas puede añadir predicción a B1 si B1 no la representa: no es por sí solo sesgo.',
        '- FWL vs OLS directo: todos los 2.001 D en cuatro controles, error máximo2.89e-15, p idéntica. '
        'B1 reproduce los cuatro conjuntos D9g con error≤3.34e-16 y p idéntica.',
        '- Todas las transformaciones se ajustan sólo con entrenamiento exterior, incluyendo mu/sigma, potencias, productos y escalado de términos; '
        'mitades reajustadas. No B5, tuning o selección posterior.',
        f"- [verification.json](verification.json): **PASS**, {v['rows']} filas, 16 celdas, {v['external_files_verified']} archivos externos por SHA. '
        'La pérdida test250 y c30/medidas baratas se copiaron exactamente de D9g. 1.500 paneles/pesos u30 restaurados sin fallos; test no se regeneró ni reevaluó.', '',
        '## Recomendación al responsable y límites','',
        '**Posponer el confirmatorio de c30 apoyado sólo en D9g.** La señal no pasó esta prueba de robustez. '
        'Si interesa distinguir redundancia real de sobreajuste de bases flexibles, registrar otro estudio de descubrimiento con regularización/suavizado '
        'y selección de complejidad mediante CV anidada, antes de mirar sus resultados. No añadir B5 ahora: se excluyó antes del código. '
        'El responsable decide si vale la pena ese estudio y si después procede confirmar.', '',
        '**C2 sigue intacta y reservada.** No se accedió a su cohorte, estados, checkpoints ni test/asociaciones. '
        'No Wine/Iris/T2/DIN-C1. No se modificó D9g ni otra etapa. Sin reentrenamiento, nueva geometría ni test nuevo.', '',
        'Las medidas B4 son resúmenes de logits/probabilidades y de parámetros; no son argumentos nuevos de M, pero comparten información con su construcción. '
        'La norma de pesos depende de la parametrización; no es una nueva cantidad geométrica invariante. '
        'Las identidades algebraicas de M no demuestran esta lectura de CV ni una causa del resultado.', '',
        'Exploratorio, sin afirmaciones confirmatorias, causales o de transferencia. La regla evalúa estas bases concretas no regularizadas, no toda función barata. '
        'La permutación no garantiza calibración bajo cualquier misspecificación; el negativo sólo valida redundancia en el espacio de cada base. '
        'El centrado de Y usa medias finales del split, como D9g; no es un predictor desplegable sin esas medias. '
        'La prueba positiva grande no da potencia conocida para efectos pequeños. Todos los splits y salidas se conservan, sin sustituciones ni nuevos umbrales.', '',
        '[Diseño](DESIGN_FROZEN.md) · [configuración](config.json) · [16 estimaciones](results/run_v1/estimates.csv) · '
        '[salida íntegra](results/run_v1/analysis.json) · [controles](results/run_v1/controls.json) · [teoría](THEORY.md).']
    with (STAGE/'CONCLUSION.md').open('x') as file:file.write('\n'.join(lines)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(11,4.7),layout='constrained')
    bs=[1,2,3,4]
    axes[0].bar(bs,[float(r['D']) for r in primary],color=['#326c93','#bd5434','#bd5434','#bd5434'])
    axes[0].axhline(0,color='#555',lw=.8);axes[0].axhline(.01,color='#666',ls='--',lw=1,label='umbral robustez .01')
    axes[0].set_title('Incremento de c30 sobre cada base');axes[0].set_ylabel('D adicional');axes[0].legend(fontsize=8)
    axes[1].bar(bs,[float(r['D_base']) for r in primary],color='#326c93');axes[1].axhline(0,color='#555',lw=.8)
    axes[1].set_title('Rendimiento de la base sola');axes[1].set_ylabel('D_base frente a cero')
    for ax in axes:ax.set_xticks(bs,['B1\nlineal','B2\npolinomios','B3\ninteracciones','B4\n+3 medidas']);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
    fig.suptitle('D9g-b · s=0.8 · mismo test250 · bases ajustadas dentro de CV')
    folder=STAGE/'figures';folder.mkdir(exist_ok=False);fig.savefig(folder/'robustez_bases.png',dpi=160);fig.savefig(folder/'robustez_bases.svg');plt.close(fig)
    print('PASS: presentación de resultados archivados, sin contraste nuevo')

if __name__=='__main__':main()
