# E16-K — Diagnóstico de los tres límites J: protocolo nuevo

## Estatus y casos

Fase diagnóstica, con conocimiento de resultados J. Se fijan sus tres casos
INCONCLUSIVE: h00/0/cuadrática, h01/1/producto, h01/1/cuadrática. Controles:
h00/0/suma y h01/1/suma, sin duplicar el segundo. Mismos datos H, P0 y pares.
No se pretende confirmación independiente ni se modifica el estado histórico J.
Sin entrenamiento ni cambios en evidencia previa o T2-A.

## Integración y gradiente

Reemplazar el objetivo de cuadratura fija por la integral cerrada de cada tramo,
diferenciable por autograd en float64. Para vectores blanqueados u, d (rapidez
u+t d), a=||d||², h=(u·d)/a, r=u−h d y δ=||r||².
Esta δ usa el residual ortogonal, evita restar dos números casi iguales y no
añade un piso. Con w=sqrt(δ/a),
P(x)=[x sqrt(a x²+δ)+(δ/sqrt(a)) asinh(x/w)]/2,
longitud=P(1+h)−P(h). Para suma se usa ||u|| directamente.
Si a≤0 o δ≤0 en una composición no lineal, conservar evaluación no admisible,
no repararla. No se ajusta el objetivo mediante clipping.

Validar cada salida del optimizador mediante la misma longitud evaluada a 80
cifras desde fuentes D. Contrastar gradiente autograd con diferencias centrales
MP80 a pasos 1e-18 y 1e-22: acuerdo entre pasos≤1e-20 y con autograd≤1e-6,
normalizando por max(1,L). Longitud float64 frente a MP80≤1e-10.
Estos controles son numéricos, no cotas rigurosas de derivación.

Para cada salida, comprobar SPD por cotas Bernstein G a 80 cifras en todos sus
tramos. Guardar margen mínimo y fallos; no llamar rama física a una salida sin SPD.
Para el candidato elegido por resolución, evaluar además longitud, márgenes y
SPD a 80/120 cifras con derivadas D, primitiva G, cuadraturas localizadas 16/32/64
y reparametrización G; tolerancias gruesa 1e-12, fina 1e-24, precisión 1e-40.

## Mallas anidadas y selección

M=4,8,16 segmentos uniformes; N=M−1 puntos interiores,
p_i=a+(i/M)v+s_i Rv, |s_i|≤1/4. Extremos fijos, misma caja que J.
Prolongar el candidato elegido de la malla anterior por interpolación lineal:
conserva su camino quebrado. Verificar igualdad de longitudes a 1e-12; no
confundir el redondeo de interpolación con una familia distinta.

Cinco inicializaciones fijas por malla: 0, ±0.1 sin(πt), ±0.1 sin(2πt).
En M=8 y 16 añadir una sexta: prolongación del candidato anterior.
Sin reinicios posteriores según resultados. L-BFGS-B con ftol=1e-14,
gtol=1e-9, maxiter=600, maxfun=10000, maxls=40. Pasar método como argumento,
no como opción redundante (advertencia registrada en J no se reinterpreta).
Son 85 búsquedas: 5 casos × (5+6+6), sin muestra nueva.

Conservar todas las salidas, incluso fallidas. Elegir menor objetivo finito entre
ellas y el camino heredado (recta para M=4), desempate por orden de lista;
conservar heredado si la mejora no supera 1e-12 max(1,L_heredado).
No filtrar según éxito o SPD después de medir: si el elegido falla, INCONCLUSIVE.
Comparar longitud elegida con recta y heredado, sin empeoramiento a 1e-12.
Comparar 4→8 a 5e-3 y 8→16 a 1e-3 (mismos umbrales de refinamiento J, con
las nuevas mallas). No afirman convergencia matemática al continuo.

## Ramas, estacionariedad y fronteras

Para cada salida calcular gradiente MP por el paso menor y residual
||s−clip(s−grad L,−1/4,1/4)||∞/max(1,L), exigido≤1e-5, como J.
Guardar también gradiente libre y nodos activos a distancia≤1e-6 de la caja.
Hessiana autograd simetrizada y mínimo autovalor del bloque de coordenadas
libres: diagnóstico de segundo orden con umbral −1e-5 normalizado, no una
certificación de mínimo. No usarlo para descartar ni reemplazar soluciones.

Rango de longitudes MP80 entre todas las salidas de una malla≤1e-5 indica acuerdo
entre reinicios, como J. Si lo supera y todas las salidas tienen gradiente validado,
KKT pequeño y SPD, etiquetar DISTINCT_STATIONARY_CANDIDATES: evidencia numérica
de candidatos distintos, no prueba de múltiples mínimos. El caso conserva
INCONCLUSIVE por falta de estabilidad entre reinicios. Si falla alguna validación,
etiquetar NUMERICAL_OR_OPTIMIZATION_LIMIT. No llamar mínimo a una parada del solver.

## Decisiones y controles

Por resolución: FAIL si falla identidad/control o no-empeoramiento;
INCONCLUSIVE si cualquier reinicio falla optimización, precisión del objetivo o
gradiente, KKT o SPD, si no coinciden los reinicios, o si falla validación del
elegido. PASS_NUMERICAL si todo pasa. Los fallos no se excluyen de denominadores.
Por caso añadir ambos criterios de refinamiento; prioridad FAIL, INCONCLUSIVE,
PASS_NUMERICAL. Caso en frontera no es candidato geodésico libre aunque pase.

Controles de suma: camino elegido recto, longitud igual a la recta a 1e-12.
Verificar caja y extremos, y conservación del camino por prolongación.
La recta de referencia se valida con G a 80/120 cifras. Registrar comparación
J8/K16 sin exigir superar J: el objetivo es resolver límites instrumentales.
No ajustar las tolerancias después de medir. Un caso no resuelto permanece así.

## Evidencia y límites

Guardar longitudes, parámetros finales de cada reinicio, gradientes contrastados,
residuales, Hessiana mínima resumida, validación de tramos, ramas, refinamiento,
procedencia, recursos, hashes y manifests. No publicar arrays internos del solver.
Repetir una vez sólo para reproducción byte a byte; recursos separados.
300 s/512 MiB, un hilo, por corrida; conservar parciales si se agota presupuesto.
La muestra se selecciona por sus dificultades conocidas: estudio diagnóstico.
No se certifican geodésicas continuas, mínimos globales o SPD mediante intervalos.
Congelar este diseño y configuración en Git antes de programar o ejecutar.
