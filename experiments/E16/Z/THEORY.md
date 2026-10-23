# Reestacionarización física y comparación espectral

Z optimiza la curva poligonal, no los pesos de la red. Cada fuente se subdivide
independientemente y se usa un único método físico L-BFGS-B. Las etiquetas
reference/scaled identifican la procedencia en S, no dos algoritmos de Z.

## Residuo físico y monitor filtrado

Para variables interiores x, caja C y longitud L, se usa

$$r(x)=\frac{\|x-\Pi_C(x-\nabla L(x))\|_\infty}{\max(1,|L(x)|)}.$$

El umbral 1e-5 es numérico. No afirma derivada exactamente nula o mínimo.
Cada 200 iteraciones aceptadas se mide r con AD. Si supera 2e-5, el punto se
registra SCREENED_NONSTATIONARY y la racha se reinicia, sin ejecutar FD MP.
Este filtro es una observación AD; no se presenta como verificación MP negativa.

Los puntos que pasan el filtro se contrastan mediante gradiente MP80 completo,
con dos pasos de diferencias finitas locales. Sólo tres auditorías programadas
consecutivas verificadas y r≤1e-5 solicitan parada en ese mismo punto.
La evaluación inicial no cuenta y no se selecciona el mejor estado anterior.
Un fallo de verificación queda UNVERIFIED e impide aprobar el camino.

La interrupción por callback produce success=False/status99 en SciPy. Esas
banderas se conservan; la aceptación del protocolo se registra por separado.
Una terminación natural con success=True necesita validación física final,
pero no se le atribuye una racha no observada. El límite de iteraciones sin
esa terminación o racha conserva INCONCLUSIVE.

Tres observaciones no garantizan cumplimiento entre muestras ni en el futuro.
La validación final MP se realiza aparte de las usadas para detenerse.

## Masa fija y espectro final

La masa P1 se fija desde la fuente inicial de Y y se conserva aunque cambie la
curva. Se comparan L, gradiente y mínimo de

$$\min_{v^TMv=1,\;g^Tv=0}v^THv.$$

Es una norma de desplazamientos respecto del parámetro inicial. No es longitud
de arco intrínseca ni una masa recalculada sobre cada curva final. Los números
son comparables antes/después dentro de cada fuente; no deben confundirse
con normas de otras fuentes, aunque terminen en la misma imagen geométrica.

El punto final se analiza también cuando no cumple la parada, si es evaluable.
Un autovalor negativo allí se conserva como diagnóstico, sin usarlo para
aprobar el caso ni convertir supervivientes en confirmación independiente.
La dirección mínima se contrasta con MP, incluyendo su normalización de masa.

## Bordes y elegibilidad

En cajas, el cono crítico es un subconjunto del cono de direcciones factibles
con variación de primer orden nula. En un borde activo, g⊥ incluye direcciones
que pueden ser inviables. Z no resuelve ese cono. Por eso sólo declara elegible
la comparación estacionaria si pasa primer orden y espectro y el punto es
interior con margen superior a 1e-8. También se registra una prueba bilateral
pequeña, sin sustituir el criterio de elegibilidad.

Un negativo numérico en un punto aproximadamente estacionario no certifica
silla exacta. KKT de primer orden tampoco certifica mínimo; puede coexistir
con curvatura negativa validada direccionalmente.

## Fuentes repetidas y límites

Algunas subdivisiones de S/132 ya fueron fuentes de optimizaciones S/264.
Si el mismo algoritmo y la misma regla efectiva llegan al mismo estado, se
informa como repetición determinista, no evidencia nueva independiente.
El filtro de Z cambia el coste del monitor, sin convertir ese caso repetido
en un nuevo dato confirmatorio. Todas las fuentes siguen en el denominador.

La proyección float de la subdivisión difiere ligeramente de la construcción
MP exacta de Y. Se controla esa diferencia, sin afirmar igualdad bit a bit.
La referencia de longitud, positividad y gradientes sigue siendo numérica,
sin aritmética de intervalos. Z no demuestra geodésica, mínimo o convergencia.
