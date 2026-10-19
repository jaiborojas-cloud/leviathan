# E16 — Progreso

## Diseño

2026-10-19: fuentes reconstruidas, E16 reservado, formalización y diseño v1
persistidos antes de programar y ejecutar. Pendientes controles A–D, degenerado,
derivadas independientes, verificación y publicación. Sin resultados abiertos.

## Incidencia v1

El control A terminó y guardó tablas; la escritura del progreso falló por mezclar
ruta relativa y absoluta. Corrida global INCONCLUSIVE. Se conserva `results/run_v1`.
Corrección prevista v2: normalizar la ruta, sin cambiar criterios.

- v2, A_cartas_SPD: PASS; 0.116 s acumulados. Resultados: `results/run_v2`.

- v2, B_subfamilias: PASS; 0.125 s acumulados. Resultados: `results/run_v2`.

- v2, C_descenso: PASS; 0.134 s acumulados. Resultados: `results/run_v2`.

- v2, D_composicion: FAIL; 0.242 s acumulados. Resultados: `results/run_v2`.

- v2, E_cociente_degenerado: PASS; 0.249 s acumulados. Resultados: `results/run_v2`.

- v2, F_presupuesto: PASS; 0.250 s acumulados. Resultados: `results/run_v2`.

## Incidencia v2 y corrección explícita

run_v2: 121 comprobaciones, una FAIL de referencia manual cuadrática; las
otras 120 PASS. Véase [fe de erratas](ERRATA_v2.md). No es evidencia contra la
cadena ni motivo para cambiar tolerancias. La implementación v2 y su fallo
quedan en Git antes de corregir. El diseño congelado sigue intacto.
