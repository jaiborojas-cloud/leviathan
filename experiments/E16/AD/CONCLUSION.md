# Conclusión E16-AD

**INCONCLUSIVE** bajo el diseño prospectivo. Parte A: suma, producto y cuadrática
son localmente planas en región SPD. Parte B:12/12 controles PASS y12/12
diagnósticos PASS; nueve casos cumplen la ruta de estacionariedad, tres LIBRE
cuadráticos no la cumplen. No se afirma H2 ni H1.

## A: curvatura

SymPy verifica K=0 para métrica constante y métrica cónica universal. La suma
es lineal; producto y cuadrática tienen inmersiones homogéneas de grado2.
Los81 puntos SPD por composición pasan contraste float/MP80/MP120.
Suma: rango MP120[0,0]. Producto:[−2.3452e-114,1.6896e-116];
cuadrática:[−2.8283e-114,1.0703e-115]. Son residuos numéricos conservados;
la afirmación analítica procede de la deducción y la identidad simbólica, no
 de redondear una malla a cero. [Rangos completos](results/part_a_v1/summary.csv).
No se ejecutaron caminos del producto ni es un candidato no plano aquí.

## B: las seis cuadráticas, sin selección

KKT se refiere al problema admisible; la columna completo es el residuo físico
ambiental. Mínimo total usa norma métrica nodal, no masa P1. Los mínimos físicos
se conservan por separado en paths.csv. FT corresponde a modos ambientales
resueltos más allá de tau, no a todas las pequeñas negativas crudas.

| Malla | Carta | Estado | KKT admisible | KKT completo | Mín total métrico | Mín NN | Mín admisible | FT min–max |
|---|---|---|---:|---:|---:|---:|---:|---|
| 132 | LIBRE | INCONCLUSIVE | 2.44086e-05 | 2.44086e-05 | -2.70722e-06 | 0.154271 | -2.70722e-06 | UNKNOWN |
| 132 | COCIENTE | PASS | 4.7676e-07 | 0.000150458 | -0.150537 | 0.147503 | 0.147478 | 0.99867776–0.99924398 |
| 264 | LIBRE | INCONCLUSIVE | 2.19065e-05 | 2.19065e-05 | -2.37745e-06 | 0.0747918 | -2.37745e-06 | UNKNOWN |
| 264 | COCIENTE | PASS | 5.7995e-07 | 2.10247e-05 | -0.0190704 | 0.0737454 | 0.0737425 | 0.99991125–0.99999798 |
| 528 | LIBRE | INCONCLUSIVE | 8.53205e-06 | 8.53205e-06 | -0.000797764 | 0.0368939 | -0.000797764 | 0.99999038–0.99999730 |
| 528 | COCIENTE | PASS | 5.73759e-06 | 2.97803e-06 | -0.00226343 | 0.0368715 | 0.0368714 | 0.99999291–0.99999775 |

Los tres LIBRE alcanzan2400 iteraciones, con successFalse/status1 conservados.
El de528 tiene KKT final8.53e-6, pero no éxito nativo ni tres auditorías
programadas consecutivas válidas; el descriptor final aislado no lo promueve.
En132 y264 KKT es2.44e-5 y2.19e-5. No hubo sustituciones o reinicios.

Los tres COCIENTE pasan su criterio restringido. Sus Hessianas ambientales
siguen teniendo modos negativos resueltos, con fracciones tangenciales mínimas
0.99868,0.99991,0.99999, mientras NN y el bloque admisible son positivos.
Esto es compatible con el papel de redistribución de nodos; no basta para
atribuir causa única a negativas de otras etapas o resolver H2 por selección.
En LIBRE/132 y264 los mínimos crudos negativos quedan dentro del umbral
relativo; no hay modos negativos **resueltos** en esas dos mallas. LIBRE/528
tiene dos negativos resueltos, con fracciones tangenciales de0.99999038
a0.99999730. Se conservan todos los valores, tau y testigos MP.
La guardia de presencia de negativas LIBRE evita una atribución vacía incluso
si se pasaran todas las condiciones universales sobre un conjunto vacío.

## Controles e instrumento

C0:seis controles (mallas×cartas) con NN positivo y sin negativas resueltas.
Esfera: seis controles,0 normales negativas en0.75π y exactamente1 en1.5π,
en las tres mallas. Hessianas de cuadratura32/64 y fórmula FEM concuerdan.
El instrumento detecta el índice1 geométrico del control, sin simular producto.
Los espectros y Hessianas por bandas, bloques TT/NN/TN, modos negativos,
componentes métricas y testigos MP quedan archivados. Los modos normales
negativos esféricos se reconstruyeron de las bandas, sin nueva Hessiana AD.

## Alcance y próximo paso

Exploratorio; sin certificados con intervalos, mínimo global o causa única.
La carta normal fija no identifica todo el cociente ni exige KKT completo.
Sólo se modificó AD; S–AC y T2_A/T2_A1 permanecen intactos.

Si se establece H2, como el producto también es plano, correspondería cerrar
la sublínea con síntesis S–AD, no buscar conjugados regulares inexistentes del
producto. En el estado actual, antes de cerrar falta resolver prospectivamente
la parada LIBRE y el carácter de sus negativas subumbral, conservando los tres
inconclusos. No se propone AE de producto no plano: no se cumple esa premisa.

## Integridad

PASS_REPRODUCTION:4 salidas científicas A y13 B idénticas byte a byte;
B:255.158662s/275.050781MiB, primera B254.725054s/275.984375MiB.
Los tiempos se excluyen de igualdad. Se reconstruyeron bloques y modos desde
bandas sin nuevas Hessianas. [Verificación](verification.json).
Integridad aprobada no convierte INCONCLUSIVE en H2.
