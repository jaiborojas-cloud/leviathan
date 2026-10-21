# E16-L — Refinamiento del caso pendiente y forma del camino

## Estatus y casos

Diagnóstico sobre h00/0/cuadrática, único caso pendiente K por refinamiento,
y el control h00/0/suma. Mismos datos H, P0, extremos y corredor; sin entrenamiento.
No se modifican estados ni evidencia histórica A–K o T2-A. No es confirmación
independiente. El criterio de longitud 0.001 no se relaja.

## Mallas y búsqueda

M=16,32,64 segmentos uniformes, N=M−1 puntos interiores:
p_i=a+(i/M)(b−a)+s_i R(b−a), |s_i|≤1/4, extremos fijos.
Mallas anidadas por interpolación lineal, incluyendo todos los vértices anteriores.
Herencia inicial: candidato K16 guardado, con hash y parámetros fijados; para
32/64, prolongación del candidato L elegido en la resolución anterior.
Comprobar conservación de longitud de la prolongación a 1e-12.

Cinco inicios fríos iguales a K: 0, ±0.1 sin(πt), ±0.1 sin(2πt), más el
heredado, en cada resolución: 36 optimizaciones, ninguna añadida por resultados.
Objetivo y gradiente autograd de la primitiva estable del código K con hash fijo,
sin modificar esas funciones. L-BFGS-B: ftol=1e-14, gtol=1e-9, maxiter=2400,
maxfun=40000, maxls=40. Se amplía de antemano el presupuesto de iteraciones
respecto a K para hasta 63 incógnitas; no se cambian tolerancias numéricas.

Guardar cada resultado, converja o no. Elegir menor objetivo finito entre seis
salidas y heredado; desempate por orden de lista. Conservar heredado si la mejora
no supera 1e-12 max(1,L_heredado). No filtrar por SPD o éxito posteriormente:
un candidato elegido que no se valida queda INCONCLUSIVE, no se reemplaza.

## Controles de longitud, gradiente y positividad

Conservar criterios K: contraste del objetivo float64 con MP80 a 1e-10;
gradiente autograd con diferencias centrales MP80 a pasos 1e-18/1e-22,
acuerdo entre pasos a 1e-20 y con autograd a 1e-6. Residual proyectado KKT
normalizado≤1e-5. Verificar SPD numérica de todos los tramos de cada salida
con Bernstein G, sin intervalos dirigidos, margen 1e-30 y límites G congelados.

Para escalar las diferencias finitas, usar que variar un vértice sólo afecta
los dos tramos adyacentes: calcular el gradiente MP de esa suma local, usando
la función de primitiva K para cada arista. No aproximar ni cambiar el objetivo.
En el candidato seleccionado de M=16, contrastar las coordenadas primera y
última con la diferencia central del objetivo completo, paso 1e-18, a 1e-40.

Candidato elegido de cada malla: primitiva G, cuadraturas localizadas 16/32/64,
reparametrización y SPD a 80/120 cifras; criterios G/K grueso 1e-12, fino 1e-24,
precisión de longitudes y márgenes 1e-40. Recta de referencia igual validación.
No empeorar recta ni heredado a 1e-12; controlar caja y extremos. En suma,
camino elegido recto y longitud igual a recta a 1e-12.
Hessianas no son un criterio de esta fase: el objetivo es refinamiento y forma.

## Estabilidad de longitud y del camino completo

Entre reinicios de una malla: rango de longitudes MP80 normalizado por max(1,L)
≤1e-5; máxima diferencia de parámetros entre cualquier par≤1e-3. No excluir
los reinicios que diverjan. Todos deben converger y validar gradiente, KKT y SPD.

Entre mallas elegidas: error de longitud |L_a−L_b|/max(1,|L_a|,|L_b|)≤0.001
para 16→32 y 32→64. No equivale a error relativo porcentual cuando L<1.
Para forma, prolongar el camino grueso al fino y medir max|s_fino−s_prolongado|:
es exactamente la separación espacial máxima dividida por ||b−a|| para estas
gráficas lineales por tramos con el mismo parámetro longitudinal.
Exigir ≤0.005 en 16→32 y ≤0.001 en 32→64 (0.5% y 0.1% de la cuerda).
Es un acuerdo finito de forma, no una cota de error al continuo ni Hausdorff
entre curvas arbitrarias. Guardar diferencias por nodo, no sólo el máximo.

## Clasificación y salidas

Por resolución: FAIL si falla identidad/control o no-empeoramiento;
INCONCLUSIVE ante fallos de optimización, longitud/gradiente, KKT, SPD o acuerdo
entre reinicios; PASS_NUMERICAL si todos pasan. Por caso añadir ambos criterios
de longitud y forma entre mallas; cualquier incumplimiento conserva INCONCLUSIVE.
Prioridad global FAIL, INCONCLUSIVE, PASS_NUMERICAL, con presupuesto cumplido.
Si hay frontera activa a distancia≤1e-6, no identificar con geodésica libre.
No afirmar unicidad o mínimo global aunque todos los reinicios coincidan.

Guardar longitudes, parámetros finales de todas las salidas, gradientes,
residuales, tramos, diferencias de forma, reinicios, refinamientos, controles,
procedencia, recursos y hashes. Sin arrays internos del optimizador en Git.
Comparar descriptivamente con K16, sin reinterpretar K. Si L no pasa, no añadir
otra malla ni relajar criterios después de ver resultados.
Repetir una vez para reproducción byte a byte, recursos separados. Presupuesto
300 s/512 MiB por corrida, un hilo; preservar parciales si se agota.
Ningún resultado establece geodésicas continuas, una tasa poblacional, capacidad
predictiva o ley universal RIPG. Congelar diseño y config antes de implementar.
