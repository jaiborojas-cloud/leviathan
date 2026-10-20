# E16-H — Transferencia prospectiva del instrumento G

## Objetivo y separación de fases

G resolvió de forma diagnóstica los casos conocidos de F. H evalúa transferencia
a configuraciones nuevas generadas y congeladas antes de medir sus observables.
No se reinterpreta F ni se toca evidencia A–G o T2-A. No hay entrenamiento.
La hipótesis instrumental predefinida es que el método G alcanza PASS_NUMERICAL
en las 324 longitudes nuevas bajo sus mismas tolerancias y presupuestos.
Si un caso no pasa, la hipótesis completa no queda satisfecha: conservar FAIL o
INCONCLUSIVE y no ampliar muestra, cambiar semillas, caminos o criterios.
No se exige ninguna dirección de cambio de longitud entre composiciones.

## Configuraciones nuevas

Generador NumPy PCG64; semillas de pesos 20261022, entradas 20261023 y perspectivas
20261024. Red 2→2→1 tanh/Bernoulli, mismo orden de nueve parámetros que D.
12 vectores uniformes en [-0.8,0.8], 12 entradas bidimensionales y tres
perspectivas uniformes en [-1.2,1.2], redondeados a seis decimales.
Se guardan todos los primeros sorteos, sin evaluar ni seleccionar su geometría.
P0 contiene todas las entradas; P1 índices pares y P2 impares. Etiqueta
int(z1+z2>0), misma cométrica (F+0.01I)^(-1) y composiciones que D/G.
Los tres segmentos son 0→1, 1→2 y 2→0 entre los puntos nuevos, sin selección.
12 estados × 3 paneles × 3 segmentos × 3 composiciones = 324 longitudes;
216 razones respecto a la suma. No se regeneran puntos si pasan cerca del origen.
La verificación reproduce los sorteos y comprueba ausencia de coincidencias
exactas con estados, entradas y perspectivas D, sin usar observables H.

## Método congelado sin cambios científicos

Se conserva el método G de hash fijado en config.json y su [diseño](../G/DESIGN_FROZEN.md).
Todas sus funciones compartidas se compararán por AST: primitiva de sqrt(q),
partición alrededor del mínimo, Gauss–Legendre 16/32/64, cotas Bernstein mediante
de Casteljau, geometría y operaciones auxiliares. La adaptación del programa sólo
sustituye los datos fuente, elimina la comparación por caso con F (no aplicable
a estos casos nuevos) y registra procedencia H/G. No cambia los controles ni
la clasificación numérica. Se guarda un adaptador reproducible desde la fuente G.

Se copian exactamente de G: precisiones 80/120; exponentes de anchura 0…40;
tolerancias gruesa 1e-12, fina 1e-24, precisión e identidad 1e-40;
margen de positividad 1e-30; profundidad 20 y 8191 nodos Bernstein;
cartas y controles, umbral de razón 1e-8; presupuesto 180 s y 512 MiB, un hilo.
No se alteran estos valores después de observar H.

## Decisión y salidas

Por caso, FAIL si falla una identidad; INCONCLUSIVE si la fórmula no es admisible,
la precisión, integración o cotas de positividad son insuficientes;
PASS_NUMERICAL sólo si todo pasa, como G. El resultado global es FAIL si existe
FAIL; de otro modo INCONCLUSIVE si existe caso/criterio inconcluso; de otro modo
PASS_NUMERICAL. El presupuesto también debe cumplirse para validar la fase.
Guardar todas las longitudes, rapidez cuadrática, márgenes, controles, razones,
resumen por panel con denominadores, procedencia y recursos. No omitir inconclusos.
No repetir con ajustes. Una segunda ejecución idéntica está autorizada solamente
como verificación de reproducción, sin contarla como una muestra adicional.
Comparar cinco salidas científicas byte a byte, con tiempos separados.

## Alcance

Un PASS completo apoyaría transferencia instrumental dentro de esta misma familia
sintética y tamaño, con estados/entradas/perspectivas nuevos. No demuestra tasas
poblacionales de éxito, independencia entre observaciones que comparten datos,
una ley general RIPG, capacidad predictiva ni entrenamiento exitoso.
Las razones de longitud son descriptivas y no una hipótesis confirmatoria de
acortamiento. No se buscan geodésicas ni se mide curvatura. Las cotas SPD son
numéricas de precisión múltiple, no certificadas con intervalos dirigidos.
Congelar diseño, datos y configuración en Git antes del código y mediciones.
