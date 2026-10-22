# E16-P — Contraste de representación de curvas

Diagnóstico exploratorio de la limitación observada en O. Se mantienen Q0, Q1
y C0, los mismos datos sintéticos y pesos sin entrenamiento. No es confirmación
independiente ni búsqueda de un mínimo global certificado.

## Contraste y dominio común

Fuentes Q0/Q1: O ronda 4, 132 segmentos. C0: O ronda 0, 128 segmentos. Para
igualar presupuestos a 132, C0 se subdivide en los cuatro primeros segmentos,
sin cambiar la recta. Se registra la identidad de la fuente con su intervalo
de redondeo archivado. No se reejecuta O.

Dos variantes, en este orden fijo, para cada linaje:
- fixed: conservar t_i de la fuente y optimizar sólo s_i.
- free: optimizar conjuntamente (t_i,s_i) de todos los nodos interiores.

Cada variante parte de la MISMA fuente, no del óptimo de la otra. Extremos
(0,0)/(1,0), dominio rectangular 0≤t≤1, |s|≤0,25, métrica y función de longitud
idénticos. La variante libre admite t no monótono, segmentos verticales y
retrocesos; no impone restricciones de orden, separación mínima, penalización
ni regularización. Es una familia más amplia, no mera reparametrización de un
camino fijo. Las variables normalizadas t/s tienen la misma escala espacial.

Se optimiza en 132 y luego 264 segmentos, subdividiendo TODOS los segmentos
del camino de cada variante por sus puntos medios en (t,s). Esto preserva el
polígono inicial del refinamiento. Se conserva cada candidato devuelto, incluidos
fracasos. No hay reinicios, selección del mejor de varios resultados ni fallback
entre variantes. L-BFGS-B mantiene los ajustes heredados en config.json.

Aristas exactamente nulas o primitiva no válida producen objetivo infinito
para rechazar ensayos; registrar conteos y causas, sin recortar/floorear la
métrica. Un resultado final no evaluable es inconcluso y se conserva. No se
excluye un linaje si falla; se continúan las operaciones que sean evaluables.
El presupuesto nuevo es 600 s y 512 MiB por corrida, sin ampliación posterior.

## Validación

Usar la misma primitiva estable por segmentos y validación de G: precisión
80/120, cuadraturas 16/32/64, reparametrización, positividad Bernstein de h00 y
det h, tolerancias heredadas. Las coordenadas t se convierten exactamente desde
su float binario y s desde su texto decimal más corto, como en O, para poder
cotejar la fuente. Las diferencias finitas se perturban en multiprecisión,
sin reconvertir a float durante el paso.

En la variante free, gradiente AD y FD local de 80 cifras en AMBAS coordenadas,
con pasos 1e-18/1e-22, acuerdo entre pasos 1e-20 y AD/MP 1e-6; residual KKT
proyectado sobre las cajas t/s ≤1e-5. En fixed, sólo s es variable; informar
también el gradiente longitudinal liberado de la fuente como diagnóstico, no
exigir que la fuente sea estacionaria en variables que O no optimizó.
No confundir estacionariedad de una familia con la de otra.

Controles: longitud de un segmento vertical evaluable, inversión del recorrido,
subdivisión colineal, y controles Hausdorff heredados de N. C0 debe conservar
la longitud de la recta y s≈0 en ambas variantes; redistribución longitudinal
sobre la misma recta no se interpreta como cambio de forma.

## Medidas y criterio

Por cada variante y linaje, comparar 132/264: cambio de longitud normalizado
≤1e-3 y cota superior de Hausdorff≤1e-3, con brecha≤1e-5. Usar N sin modificar,
en la carta euclídea (t,s), equivalente a perspectiva dividida por cuerda;
no es distancia intrínseca de h ni certificado riguroso de intervalos.
Comparaciones fixed/free y Q0/Q1 son descriptivas: longitud, Hausdorff y acuerdo
de longitud ≤1e-5/Hausdorff superior≤1e-3. No condicionar éxito a que dos familias
produzcan el mismo candidato. No exigir sup|delta s(t)| a free, pues puede no
ser un gráfico. Dos mallas no demuestran convergencia de una sucesión.

Descriptores: desplazamientos de t de la fuente, componente longitudinal del
gradiente inicial, retrocesos dt<-1e-8, mínima longitud euclídea de arista,
número de aristas casi verticales |dt|/norma(delta(t,s))≤1e-3, posición del nodo
heredado con t=0,984375, y separación tras remuestrear por arco euclídeo en 257
puntos. El remuestreo por arco es sólo descriptivo; no sustituye Hausdorff.
No usar velocidad respecto a t para afirmar singularidad o regularidad de free.

PASS_NUMERICAL de una variante requiere dos caminos válidos, gradiente, KKT,
no empeoramiento, integración/SPD y refinamiento de longitud/Hausdorff. Fallos
de identidades son FAIL; condiciones numéricas pendientes son INCONCLUSIVE.
Global sólo pasa si todas las variantes/linajes y controles pasan. Preservar
primera corrida y fallos; reproducir todas las salidas científicas byte por byte,
con tiempos/memoria aparte. Este protocolo no certifica mínimos globales,
unicidad, geodésicas ni existencia de una curva límite.
