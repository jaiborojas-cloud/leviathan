# Repetición nominal contra v2: mismas semillas, clasificaciones separadas

Se completaron las **1.000 réplicas solicitadas**: nulos d=.02 N200/N400 (400
por celda) y alternativa β=+.03 N400 (200). **5.000 permutaciones y2.000 bootstrap
por réplica**, sin reducir parámetros. Tiempo del intento final599.75 s, dos
procesos de un hilo BLAS. Datos totalmente sintéticos, ruido independiente entre
niveles; no se leyó Wine, C2 ni Q13 real.

| Celda | MODULA primaria | NO_CONCLUYENTE primaria | INCONCLUSIVE | NO_MODULA secundaria |
|---|---:|---:|---:|---:|
|null_N200,400 réplicas|8/400 =2.00%|377/400 =94.25%|15/400 =3.75%|0/400|
|null_N400,400 réplicas|10/400 =2.50%|390/400 =97.50%|0/400|0/400|
|positive_N400,200 réplicas|74/200 =37.00%|126/200 =63.00%|0/200|0/200|

INCONCLUSIVE aquí significa INCONCLUSIVE_SIN_SENAL_CONTROL; los otros motivos
no aparecen en estas tablas completas regulares. Las tres primeras columnas
suman cada celda; la secundaria no es una cuarta opción excluyente. En general
NO_MODULA secundaria puede coexistir con MODULA, y se comprueba aparte con IC
[.001,.01]. No se cambió esa definición para igualar etiquetas antiguas.

## Intervalos y denominadores

- Falsos MODULA bajo nulo d=.02:2.00%, Wilson95[1.02%,3.90%] en N200;
  2.50%,[1.36%,4.54%] en N400. No se observa exceso global sobre5% en estos modelos.
- Condicionado al control:8/385=2.08%,[1.06%,4.05%] en N200;10/400 en N400.
  No mezclar385 con400 como denominador. Quince controles no pasan en N200.
- NO_MODULA secundaria bajo nulo:0/400 por celda, límite superior Wilson95=.95%.
  Condicionada a control es0/385 (límite .99%) y0/400. No hay potencia de equivalencia
  relevante bajo este modelo; v2 ya no la promete ni la usa para dimensionar.
- Alternativa β=+.03: potencia MODULA37%, Wilson95[30.61%,43.88%]. NO_MODULA
  secundaria0/200, límite superior1.88%; fuera de banda sería equivalencia falsa.
  Esta alternativa no es el escenario(a) más intenso del diseño: no sustituye
  el cálculo prospectivo de tamaño de la cohorte.

Los extremos se conservan: PERSISTE378/400 en null_N200,400/400 en null_N400 y
199/200 en positive_N400; DESAPARECE0,0 y1 respectivamente. La clasificación es
estadística, no prueba de D exactamente cero. Conteos/IC globales y condicionados
completos en los CSV, sin excluir resultados no concluyentes.

## Identidad con la repetición v1

Se mantiene SeedSequence([910300,índice_original,réplica]): índices **0,1,3**.
La alternativa positiva no se renumeró como2 al reducir la lista. Los seeds de
bootstrap860001, permutación260001 y folds260010 no cambiaron. El kernel de álgebra
independiente se copió byte por byte del anterior y se contrastó con funciones v2.

En **las1.000 réplicas**, X/L/Y regeneradas, D/p y bootstrap de β coinciden **bit
por bit** con los arrays sintéticos archivados de v1. Se verifican sus SHA contra
el manifiesto original de #104; sólo se leen. No se reutilizan resultados como
datos de una cohorte nueva ni se sobrescribe ningún artefacto v1.

La política v2 usa clasificar_beta y equivalencia separadas. En estas celdas no
había equivalencias antes, así que los conteos primarios son iguales. Esto no
demuestra que la v2 esté libre de los casos adversariales: éstos están fuera de
las tablas regulares del Monte Carlo y se reportan en [NUEVOS_DEFECTOS](NUEVOS_DEFECTOS.md).

## Transparencia de implementación y límites

Un primer intento del **verificador** falló por importar Path incorrectamente
(faltaba el import), antes de persistir réplicas completas. Driver, controles y
traceback quedan archivados; se congeló una enmienda y se ejecutó r2 en otra
carpeta con las mismas semillas/configuración, sin elegir resultados ni redibujar.
No es un defecto del analista auditado. El intento final no tuvo fallos ni descartes.

El motor acelerado usa FWL para permutaciones y multiplicidades de splits para
OLS bootstrap con bloque original. Los controles contra primaria C1 y D_punto
v2 dan error≤1e-10 y p idéntica, con controles nominales5000 y adicionales199.
Las medianas c son constantes dentro del nivel en estas celdas; la traza con c
variable comprueba que el analista las recalcula donde corresponde.

Estas tasas dependen del generador, de independencia entre ruidos y de tablas
completas. No son garantía universal, calibración para faltantes ni potencia para
otras dependencias. No se estima ninguna correlación de Q13 real en esta tarea.

[Resumen final](results/monte_carlo_v2_r2/summary.json) · [tasas](results/rates.csv) ·
[extremos](results/endpoint_rates.csv) · [enmienda](ENMIENDA_MC_r2_CONGELADA.md) ·
[primer fallo preservado](results/monte_carlo_v2/FAILURE.json).
