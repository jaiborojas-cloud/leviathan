# Progreso DIN-D2b

## Fase0 · lectura, sin redes ni mediciones

Se leyó AGENTS.md raíz y no hay instrucciones subordinadas en experiments.
Main actualizado al merge de D2,85c5f35; rama nueva research/din-d2b-algebra.
Lectura: D1/D3/D4/D5 publicados, D2 completo (Q1–Q5), código core completo,
geometry y rho intactos. D6 y DIN-C1 borradorv1 se leyeron mediante git show
del árbol9904db0, sin fusionarlo ni ejecutar su código. No se abrieron estados,
tablas de T2, checkpoints, baseline, comparators ni predictors_locked.

El core deriva parámetros REDUCIDOS: tercera clase de referencia, primeras
dos filas de W3 menos la tercera; por tanto no sirve comparar contra un
Fisher de tres logits con parametrización redundante. make_geom_state devuelve
Rb por capas y Ub con columnas ejemplo/clase. subset_M usa Woodbury con
ridge1e-4*max(lambda_max(UᵀU),1e-14), piso absoluto1e-18. Los bloques[0,1,2]
se concatenan antes de invertir; no se suman tres M independientes.

rho público realmente recibe Geometry, no (M,f), y permite ndir/orden;
aquí se usan sus defaults sin cambiar globals. Su mínimo local no está
certificado, y D2 archivó fallos en caras o transiciones tardías. El contraste
de D2b conserva esa distinción y no reabre D2.

D3 publicó concentración de diagonal≈.065 a u5 y≈.927 a u250; D4 la
dominancia del ejemplo menos confiado y Spearman≈.998 después del colapso.
D6: u10 tiene concentración≈.14, W≈.040 de L10 y W_adj≈.218 de X10;
selección entre6 tiempos×3 medidas. Sólo contexto, no inferencia nueva.

DIN-C1 NO está congelado en el árbol leído. Su primaria residualiza Y por
L linealmente y después calcula Spearman(X,e), sin residualizar X. La prueba
teórica de cinco observaciones muestra una limitación de ese estimando;
no se usa para declarar que D6 sea un artefacto. La decisión permanece con
el responsable y no se modifica C1.

Se instaló torch CPU2.9.1 fuera del repositorio en
/workspace/work/din-d2b-deps; sólo se comprobó importación/versiones.
Hasta este commit: cero redes construidas, cero llamadas a make_geom_state,
subset_M o rho_borde. Diseño y contraejemplos derivados algebraicamente.
