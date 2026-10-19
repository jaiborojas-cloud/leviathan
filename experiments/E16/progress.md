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

- v3, A_cartas_SPD: PASS; 0.114 s acumulados. Resultados: `results/run_v3`.

- v3, B_subfamilias: PASS; 0.123 s acumulados. Resultados: `results/run_v3`.

- v3, C_descenso: PASS; 0.131 s acumulados. Resultados: `results/run_v3`.

- v3, D_composicion: PASS; 0.238 s acumulados. Resultados: `results/run_v3`.

- v3, E_cociente_degenerado: PASS; 0.245 s acumulados. Resultados: `results/run_v3`.

- v3, F_presupuesto: PASS; 0.246 s acumulados. Resultados: `results/run_v3`.

## Cierre de ejecución

Congelación: `7db497d`. v3 completó 122/122 PASS y mantiene v1/v2. Tablas y
recursos en `results/run_v3`; entorno consolidado en environment.json. Fuentes
históricas con hashes; índices y roadmap enlazan la línea sin alterar estados
científicos históricos. No hay figuras necesarias para estos ejemplos.

Reanudar: no repetir controles válidos para ampliar resultados. Usar verify.py
para comprobar hashes y reproducción en temporal; una réplica manual debe usar
un directorio nuevo. La siguiente fase es NEXT_PHASE.md y requiere su propio
protocolo; no ejecutar scripts T2-A.

La conexión Git funciona al solicitar capacidad de red al ejecutor. `main` remoto
avanzó con trabajo ajeno T2-A; se conserva nuestra base e historial sin editar
esos archivos. El PR se comparará contra main; no se requiere fusionar ni
reescribir commits de diseño para incorporar trabajo ajeno.

## Verificación previa a publicación

Diff revisado: sólo E16 y cinco entradas de navegación. Diseño congelado intacto,
hashes y enlaces propios válidos, tablas de v3 reproducidas byte a byte,
398/398 fuentes del archivo y 34/34 fuentes de cierres verificadas.
Ningún archivo T2-A cambió respecto a la base; sin ejecución de sus scripts.
Dependencias fijadas en requirements.txt. Próximo paso operacional: push de
esta rama y PR contra main, sin merge.

La revisión de whitespace detectó los CRLF estándar de csv.DictWriter. Se declara
`whitespace=cr-at-eol` sólo para CSV de E16 en .gitattributes, conservando todos
los bytes originales de resultados y su reproducción; sin normalizar históricos.
