# E16-M — Seguimiento de candidatos y localización del cambio

## Alcance y selección previa

Diagnóstico sobre h00/0/cuadrática y control h00/0/suma; mismos datos, extremos
y corredor. Se conocen los resultados L; no es confirmación independiente.
No se cambia L ni evidencia anterior o T2-A. Sin entrenamiento.

Agrupar los seis candidatos guardados L32 por caso, en orden creciente del índice
de inicio. Añadir a la primera agrupación si coincide con **todos** sus miembros:
error de longitud normalizado≤1e-5 y máximo de diferencia de parámetros≤1e-3;
si no, abrir grupo nuevo. No filtrar por éxito o SPD. Representante: primer índice,
no el más corto. grupos.json fija dos grupos cuadráticos y uno de suma antes
de medir M. Se verifica el agrupamiento a partir de las tablas fuente con hash fijo.

Los identificadores Q0,Q1,C0 conservan su origen al prolongar. Identifican linajes
de inicialización, no ramas matemáticas certificadas. Un optimizador puede cambiar
de cuenca al refinar; no se permutan etiquetas ni se selecciona la mejor rama.

## Búsqueda y refinamiento

Inicio: parámetros guardados del representante L32, sin reoptimizar esa malla.
Prolongación lineal independiente de cada linaje a 64 y después 128 segmentos,
N=M−1, p_i=a+(i/M)v+s_i Rv, |s_i|≤1/4 y extremos fijos. Una optimización por
linaje y malla nueva: seis en total, sin reinicios adicionales tras resultados.
Guardar siempre la salida del solver. No reemplazarla por la de otro linaje;
si falla validación, conservar INCONCLUSIVE, no rescatar con otra solución.

Objetivo/gradiente: funciones K de integral cerrada estable, sin modificarlas.
L-BFGS-B ftol=1e-14, gtol=1e-9, maxiter=4800, maxfun=80000, maxls=40; los
límites se fijan de antemano para hasta 127 parámetros. No se relajan tolerancias.
Verificar conservación de longitud de la prolongación a 1e-12 y no-empeoramiento
de la salida respecto al camino heredado a 1e-12. No imponer cercanía artificial
al linaje anterior: un salto se registra como cambio de forma, no como continuidad
probada de rama.

## Validación numérica

Cada representante de 32 y cada salida nueva: contraste objetivo float64/MP80
a 1e-10; gradiente autograd frente a diferencias centrales MP80 locales en las
dos aristas adyacentes, pasos 1e-18/1e-22, acuerdo de pasos≤1e-20 y de gradiente
≤1e-6. Residual KKT proyectado≤1e-5, normalizado por max(1,L). Reportar gradiente
libre, activos a distancia≤1e-6, mensajes y éxito del solver.

Todos los recorridos se validan con G a 80/120 cifras: primitiva, cuadraturas
localizadas 16/32/64, reparametrización y SPD global numérica Bernstein.
Umbrales G/L: grueso 1e-12, fino 1e-24, precisión de longitudes y márgenes 1e-40;
SPD margen 1e-30, profundidad 20 y 8191 nodos. No son certificados intervalares.
Control de suma: parámetros y longitud del camino recto a 1e-12.
Verificar extremos, caja y referencias L32 sin cambiar sus estados históricos.

## Comparación de forma, localización y candidatos

Por linaje, 32→64 y 64→128: error de longitud normalizado≤0.001;
separación de forma max|s_fino−s_grueso_prolongado|≤0.001. Son diferencias
normales divididas por la cuerda al mismo t, no distancia intrínseca ni Hausdorff.
Guardar todos los nodos de diferencia, máximo y posición del máximo.

Para cada comparación integrar exactamente en float64 la función |Δs(t)|,
lineal por tramos, tratando explícitamente cruces de signo. Reportar masa L1
total y fracción situada en t≥0.75,0.90,0.95; además máximo interior/exterior
de cada cola, insertando el corte por interpolación para no depender del nodo.
Etiqueta LOCALIZED_AT_END si masa total>0, al menos 50% está en t≥0.90 y el
máximo fuera de esa cola es≤25% del máximo global. En otro caso NOT_ESTABLISHED;
si diferencia cero, ZERO_CHANGE. No se interpreta localización como singularidad,
causa dinámica ni prueba de capa límite de una ecuación continua.

Comparar Q0/Q1 en cada malla: longitudes≤1e-5 y formas≤1e-3 indican
NUMERICAL_AGREEMENT; en otro caso DIFFERENT_CANDIDATES. Conservar etiquetas
Q0/Q1 aunque coincidan. El acuerdo no demuestra unicidad ni una bifurcación;
la diferencia no prueba múltiples mínimos. Es descriptor, no obligación de
hacer coincidir dos candidatos ya distintos en L32.

## Controles auxiliares y decisiones

Integrador de |Δs|: cero da masa cero; Δs=t en [0,1] da 1/2 y fracción 0.19
en t≥0.9; triángulo de altura 1 en t=0.95 y soporte [0.9,1] da masa 0.05 y
fracción de cola 1. Control de cruce: Δs=t−1/2 da masa 1/4.
Tolerancia de estos controles float64 1e-12. No son experimentos de datos nuevos.

Por recorrido: FAIL ante identidad/control/no-empeoramiento fallido;
INCONCLUSIVE ante fallo de optimización, gradiente, integración, precisión o SPD;
PASS_NUMERICAL si todo pasa. Por linaje añadir ambos refinamientos de longitud
y forma. Prioridad global FAIL, INCONCLUSIVE, PASS_NUMERICAL, con presupuesto.
Los descriptores de localización y acuerdo entre Q0/Q1 se guardan separados del
estado global, sin convertir los cambios observados en fallos de instrumentación.

Guardar agrupamiento, recorridos, parámetros, gradientes, tramos, continuidad,
comparaciones entre candidatos y localización, controles, hashes y recursos.
Repetir una vez para reproducción byte a byte, tiempo separado. 300 s/512 MiB,
un hilo. Si falta presupuesto, conservar parciales y no producir PASS global.
No añadir resolución/reinicio ni ajustar criterios después de medir. Sin geodésicas
continuas, mínimos globales, evaluación predictiva o ley universal certificada.
Congelar diseño, grupos y configuración en Git antes de programar y medir.
