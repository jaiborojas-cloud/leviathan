# E16-C — Progreso

2026-10-19: AGENTS.md y cierre de E16-B revisados. Checkout limpio, rama propia
research/e16-c-precision-rango. E16-C libre en búsqueda documental. mpmath 1.3.0,
NumPy 2.3.5 y autograd 1.8.0 disponibles; autograd fuera del repo en
/workspace/work/e16b-deps. Ningún observable nuevo calculado para elegir método.

Se fijaron derivadas explícitas, FD de cuarto orden, 80/120 dps y error sobre
B L; mismos datos conocidos de B, 81 configuraciones más 18 controles de rango.
Diseño y hashes persistidos antes de programar. Pendiente: implementación,
ejecución, reproducción, revisión y publicación sin merge. A/B y T2-A intactos.

- run_v1, n0_P0: PASS, 0.301 s acumulados; tablas en `results/run_v1`.

- run_v1, n0_P1: PASS, 0.596 s acumulados; tablas en `results/run_v1`.

- run_v1, n0_P2: PASS, 0.854 s acumulados; tablas en `results/run_v1`.

- run_v1, n1_P0: PASS, 1.155 s acumulados; tablas en `results/run_v1`.

- run_v1, n1_P1: PASS, 1.441 s acumulados; tablas en `results/run_v1`.

- run_v1, n1_P2: PASS, 1.696 s acumulados; tablas en `results/run_v1`.

- run_v1, n2_P0: PASS, 1.997 s acumulados; tablas en `results/run_v1`.

- run_v1, n2_P1: PASS, 2.266 s acumulados; tablas en `results/run_v1`.

- run_v1, n2_P2: PASS, 2.522 s acumulados; tablas en `results/run_v1`.

## Cierre de ejecución v1

99/99 decisiones de rango PASS_NUMERICAL (81 principales de rango 2; nueve
controles de rango 0 y nueve de rango 1). 54/54 negativos detectados. 855 checks
PASS y 396 descriptores; cero FAIL o INCONCLUSIVE. La implementación no requirió
correcciones. Aviso de autodiff para el control constante en p: cero esperado,
contrastado independientemente y conservado.

FD4 transportado máximo: 6.152e−11 (paso 0.002), 3.845e−12 (0.001). Error
80/120 dps ≈2.407e−80; no se declara certificado exacto. B sigue INCONCLUSIVE.
Tiempo ~2.523 s, memoria máxima 36156 KiB; presupuesto cumplido. Datos conocidos,
no confirmación independiente de hipótesis empírica ni ampliación a entrenamiento.

Estado remoto consultado: PR #7 fue integrado por fuera de esta ejecución en
research/e16-composicionalidad; PR #5 sigue abierto hacia main e incluye B.
La publicación de C usará como base research/e16-composicionalidad para mostrar
sólo C. No se fusiona ni modifica ninguno de esos PRs automáticamente.

Pendiente: reproducción de tablas, integridad A/B/C, revisión de diff y publicación.

## Verificación previa a publicación

Se reprodujeron exactamente checks.csv, ranks.csv, negative_controls.csv,
summary.json y descriptive.json con el mismo entorno. Hashes de todos los
archivos de A/B/C y congelación 1b68c4e verificados. Archivo histórico 398/398,
fuentes de cierres 34/34. Enlaces y diff revisados; sólo C y tres entradas de
navegación. Sin cambios a A/B ni archivos T2-A. No hay fallos que corregir ni
controles inconclusos bajo el nuevo método. Sin entrenamiento o ampliación.

Pendiente únicamente publicación de la rama y PR sobre
research/e16-composicionalidad (#5), que ya contiene la integración de B (#7).

## Entrega publicada

[PR #9](https://github.com/jaiborojas-cloud/leviathan/pull/9) abierto sobre
research/e16-composicionalidad (#5), rama research/e16-c-precision-rango subida.
Sin merge ni auto-merge. Tras integrar #5, cambiar base a main antes de fusionar C.
La fase queda completa: precisión instrumental PASS_NUMERICAL en puntos fijados;
A/B conservan sus estados y hashes. No hay cálculos pendientes bajo este diseño.
