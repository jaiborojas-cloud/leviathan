# E16-J — Refinamiento y estacionariedad discreta: diseño congelado

## Pregunta y muestra

¿Los caminos encontrados son estables al enriquecer la familia y cambiar la
inicialización, y satisfacen condiciones de estacionariedad discreta?
Exploratorio sobre los mismos 27 casos I, sin excluir su caso de frontera:
h00/h01/h02, P0, tres pares H y suma/producto/cuadrática. Sin entrenamiento,
datos nuevos ni confirmación independiente. No se modifica evidencia A–I o T2-A.

## Familias y búsqueda

Para N=2,4,8 puntos interiores, t_i=i/(N+1),
p_i=a+t_i v+s_i Rv, v=b−a, Rv=(−v_y,v_x), |s_i|≤1/4.
Extremos fijos; longitud suma de longitudes de segmentos. Son familias de gráficas
sobre la cuerda en la carta original, no caminos arbitrarios. Las mallas uniformes
no son anidadas: no exigir monotonía ni llamar convergencia matemática a un acuerdo
finito entre tres resoluciones.

Tres inicializaciones por malla: s_i=A sin(πt_i), A=0,+0.1,−0.1. No usar resultados
para añadir reinicios o ampliar dominio. Optimizar en float64 con L-BFGS-B,
ftol=1e-13, gtol=1e-8, maxiter=300, maxfun=5000, maxls=30; guardar todos los estados.
Objetivo: Gauss–Legendre fijo 32 por segmento de ||v_segmentoᵀ B(p)L_C||,
C=L_C L_Cᵀ; no usar la primitiva dentro del optimizador. Gradiente por autograd
de ese objetivo vectorizado. Para suma, B constante. No introducir pisos de norma.

Guardar cada resultado y evaluar también la recta s=0. Escoger el menor objetivo
finito entre las tres salidas y recta, desempate por orden de inicialización.
Conservar recta si la mejora no supera 1e-12 max(1,L_recta). No elegir sólo entre
salidas exitosas: un fallo no se oculta. Si cualquier inicialización no converge,
la resolución queda INCONCLUSIVE, aunque se conserve el mejor camino encontrado.
Son 243 búsquedas científicas, más controles separados. No ejecutar ajustes nuevos.

## Validación numérica de los caminos elegidos

En cada resolución evaluar todos los tramos del camino elegido a 80 y 120 cifras
con derivadas explícitas D y funciones G sin modificar, hashes fijados. Comprobar:
- Primitiva, cuadraturas localizadas 16/32/64, reparametrización y cotas globales
  Bernstein H00/det positivas con criterios G (margen 1e-30, profundidad 20,
  8191 nodos). No son certificados mediante intervalos dirigidos.
- Acuerdo 80/120 de longitudes y márgenes normalizados a 1e-40.
- Longitud total a 120 frente al objetivo 32 de float64 a 1e-8.
- No empeoramiento frente a recta validada a 1e-12. La recta se evalúa mediante
  primitiva y SPD a 80/120. Ningún caso con fórmula no admisible se repara.

## Estacionariedad, fronteras y estabilidad

Calcular gradientes autograd del objetivo con órdenes 32 y 64 en cada candidato.
Exigir diferencia máxima dividida por max(1,L)≤1e-6. Comparar el gradiente 64 con
diferencias centrales del mismo objetivo a pasos 1e-6 y 5e-7, error normalizado
máximo≤1e-5. En frontera las diferencias pueden evaluar la extensión algebraica
fuera de la caja; no se presentan como nuevos caminos admisibles validados.

Residual KKT discreto: ||s−clip(s−∇L64,−1/4,1/4)||∞ / max(1,L)≤1e-5.
Reportar además ||∇L64||∞/max(1,L). Un nodo a distancia≤1e-6 de la caja se
marca activo. Con nodos activos se distingue solución restringida de una libre.
Estacionariedad sólo respecto a desplazamientos normales discretos: ni siquiera
un residual pequeño prueba la ecuación geodésica continua o un mínimo local.

Estabilidad entre inicializaciones: rango de los tres objetivos 64 finales,
dividido por max(1,L),≤1e-5; incluir también los que no convergen en el reporte.
Refinamiento: errores normalizados entre longitudes elegidas 2/4≤5e-3 y 4/8≤1e-3.
Estos umbrales definen acuerdo numérico a resolución finita, no un orden de
convergencia demostrado. No cambiar umbrales si un caso los incumple.
Guardar comparación con I como descripción, sin exigir superar I: las familias
no contienen necesariamente su esquina en t=1/2.

## Controles y decisiones

Métrica euclídea, a=(0,0),b=(1,0): tres inicializaciones en N=2,4,8 deben
converger y dar longitud 1 a 1e-10 y ||s||∞≤1e-5. Controles con suma constante:
candidato elegido recto y ganancia cero a 1e-12. Verificar extremos y caja.

Por resolución: FAIL si falla control/identidad o no-empeoramiento validado;
INCONCLUSIVE si falla optimización, precisión, integración, SPD, KKT, gradiente
o estabilidad entre inicializaciones; PASS_NUMERICAL si todo pasa.
Por caso añadir ambos criterios de refinamiento: si no se cumplen,
INCONCLUSIVE, sin borrar resoluciones ni candidatos válidos.
Clasificación geométrica separada: BOUNDARY_LIMITED si N=8 tiene nodos activos;
INTERIOR_STABLE_DISCRETE sólo si el caso pasa, no hay activos y gradiente libre
cumple 1e-5; resto UNRESOLVED. Ninguna etiqueta afirma mínimo global o geodésica.
Prioridad global FAIL, luego INCONCLUSIVE, luego PASS_NUMERICAL, con presupuesto.

Guardar controles, longitudes, coordenadas/parámetros finales, residuales,
tramos, resúmenes por resolución y casos, fuentes, hashes y recursos.
No subir checkpoints ni arrays internos del optimizador; sí tablas escalares de
los candidatos necesarias para reproducir el resultado. Preservar estados fallidos.
Repetir una vez para reproducción byte a byte, tiempo separado. 300 s/512 MiB,
un hilo, por corrida. Sin geodésicas certificadas, curvatura ni evaluación predictiva.
Congelar este diseño y config en Git antes de implementar o ejecutar.
