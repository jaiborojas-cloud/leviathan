# E16-D — Progreso

2026-10-20: nueva rama desde main 93b8686, checkout limpio. E16-D libre en la
búsqueda documental. Imagen del usuario confirmada en raíz; integración al README
publicada en PR #16 separado. La imagen original no se modifica.

Se leyó cierre y diseño C por commit 4fd7eb5; PR #9 integrado en la rama E16,
pero C no está en esta base main. Se reutilizará su código con procedencia,
sin importar ni ejecutar resultados históricos. A/B/T2-A permanecen intactos.

Generados y persistidos 12 estados y 12 entradas con semillas y distribución
previas a toda medición. Configuración sin filtrado. Congelados diseño, datos,
derivación, dependencias y procedencia antes del código. Pendiente implementación
y ejecución de la réplica, guardando todos los estados e incidencias.

- run_v1, d00_P0: PASS, 0.393 s acumulados; tablas en `results/run_v1`.

- run_v1, d00_P1: PASS, 0.747 s acumulados; tablas en `results/run_v1`.

- run_v1, d00_P2: PASS, 1.093 s acumulados; tablas en `results/run_v1`.

- run_v1, d01_P0: PASS, 1.513 s acumulados; tablas en `results/run_v1`.

- run_v1, d01_P1: PASS, 1.878 s acumulados; tablas en `results/run_v1`.

- run_v1, d01_P2: PASS, 2.241 s acumulados; tablas en `results/run_v1`.

- run_v1, d02_P0: PASS, 2.625 s acumulados; tablas en `results/run_v1`.

- run_v1, d02_P1: PASS, 2.967 s acumulados; tablas en `results/run_v1`.

- run_v1, d02_P2: PASS, 3.321 s acumulados; tablas en `results/run_v1`.

- run_v1, d03_P0: PASS, 3.733 s acumulados; tablas en `results/run_v1`.

- run_v1, d03_P1: PASS, 4.086 s acumulados; tablas en `results/run_v1`.

- run_v1, d03_P2: PASS, 4.441 s acumulados; tablas en `results/run_v1`.

- run_v1, d04_P0: PASS, 4.836 s acumulados; tablas en `results/run_v1`.

- run_v1, d04_P1: PASS, 5.210 s acumulados; tablas en `results/run_v1`.

- run_v1, d04_P2: PASS, 5.578 s acumulados; tablas en `results/run_v1`.

- run_v1, d05_P0: PASS, 6.028 s acumulados; tablas en `results/run_v1`.

- run_v1, d05_P1: PASS, 6.380 s acumulados; tablas en `results/run_v1`.

- run_v1, d05_P2: PASS, 6.733 s acumulados; tablas en `results/run_v1`.

- run_v1, d06_P0: PASS, 7.146 s acumulados; tablas en `results/run_v1`.

- run_v1, d06_P1: PASS, 7.538 s acumulados; tablas en `results/run_v1`.

- run_v1, d06_P2: PASS, 7.928 s acumulados; tablas en `results/run_v1`.

- run_v1, d07_P0: PASS, 8.344 s acumulados; tablas en `results/run_v1`.

- run_v1, d07_P1: PASS, 8.702 s acumulados; tablas en `results/run_v1`.

- run_v1, d07_P2: PASS, 9.123 s acumulados; tablas en `results/run_v1`.

- run_v1, d08_P0: PASS, 9.645 s acumulados; tablas en `results/run_v1`.

- run_v1, d08_P1: PASS, 10.002 s acumulados; tablas en `results/run_v1`.

- run_v1, d08_P2: PASS, 10.364 s acumulados; tablas en `results/run_v1`.

- run_v1, d09_P0: PASS, 10.790 s acumulados; tablas en `results/run_v1`.

- run_v1, d09_P1: PASS, 11.155 s acumulados; tablas en `results/run_v1`.

- run_v1, d09_P2: PASS, 11.536 s acumulados; tablas en `results/run_v1`.

- run_v1, d10_P0: PASS, 11.961 s acumulados; tablas en `results/run_v1`.

- run_v1, d10_P1: PASS, 12.393 s acumulados; tablas en `results/run_v1`.

- run_v1, d10_P2: PASS, 12.754 s acumulados; tablas en `results/run_v1`.

- run_v1, d11_P0: PASS, 13.190 s acumulados; tablas en `results/run_v1`.

- run_v1, d11_P1: PASS, 13.587 s acumulados; tablas en `results/run_v1`.

- run_v1, d11_P2: PASS, 13.980 s acumulados; tablas en `results/run_v1`.

## Ejecución completada

run_v1: 396/396 rangos PASS_NUMERICAL y 216/216 negativos detectados. 3420 checks
PASS, 1584 descriptores, cero FAIL/INCONCLUSIVE. Los 324 principales tienen rango 2.
108/108 tríos permiten comparación validada, con 0 cambios producto/suma y 0
cuadrática/suma; 108/108 grupos de sensibilidad de panel estables. No se descartan
casos ni se amplía la muestra. Sin entrenamiento ni hipótesis predictiva probada.

Presupuesto cumplido: ~13.981 s y 38588 KiB máximos. Código de C adaptado con
rótulo/seeds, procedencia y prioridades de decisión congeladas; diff persistido.
Aviso autodiff de independencia para el control constante esperado y contrastado.
No hubo fallos ni correcciones de implementación en esta fase.

Pendientes: reproducción exacta de ocho tablas/reportes, hashes/congelación,
revisión de alcance y publicación de PR. Los pasos siguientes están propuestos
sin ejecutar en NEXT_PHASE.md; no reabrir B ni extender automáticamente la réplica.

## Verificación y revisión previas a publicación

Ocho tablas/reportes reproducidos exactamente en salida temporal. Diseño,
configuración y fuentes congeladas verificados; novedad de pesos/entradas/puntos
confirmada también contra config C por commit fijo, con diagnóstico persistido.
No se cambió la configuración ni se eligieron casos después de observar resultados.
Manifests A/B y fuentes C intactos; archivo histórico 398/398 y cierres 34/34.
Diff y enlaces revisados; sólo D y tres entradas de navegación. Sin cambios a
T2-A ni al árbol protegido claude respecto de base main 93b8686.

Pendiente sólo publicar PR científico separado del PR #16 de imagen, sin merge.

La revisión de estilo identificó un espacio de contexto válido en el patch
unificado de procedencia. Se declara whitespace sólo para archivos .patch en D,
conservando su formato aplicable, sin cambiar código ni resultados científicos.
