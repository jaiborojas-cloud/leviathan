# E16-B — Progreso

2026-10-19: checkout limpio de E16, rama nueva research/e16-b-instrumentacion.
Se leyó AGENTS.md y NEXT_PHASE.md. Se comprobó main remoto ce0b970 sin modificar
ni ejecutar el trabajo ajeno T2-A. PR #5 continúa sin fusionar automáticamente.

Inventario de pesos locales: ninguno en extensiones habituales .npz/.pt/.pth/
.safetensors/.pkl del repositorio y directorios compartidos. Los documentos
históricos no sustituyen un checkpoint independiente. PyTorch y JAX no están
instalados. Hay NumPy, SymPy y SciPy.

Se preparó formalización candidata y se pidió elección de artefacto. Pendiente:
resolver red existente frente a red mínima nueva sin entrenamiento; después
fijar pesos, paneles, perspectivas, métrica, tolerancias, presupuesto y criterios
antes del código experimental y de observar resultados. No modificar la fase A.

Se concretó DESIGN_CANDIDATE.md: red 2→2→1, tres estados explícitos nuevos,
tres paneles sintéticos, tres puntos y composiciones, cartas y criterios
numéricos propuestos. Sin cálculo de observables, sin código experimental y
sin afirmar congelación. La elección del artefacto sigue pendiente.

## Elección resuelta y congelación

El usuario autorizó explícitamente «Crear una red mínima nueva, sin entrenamiento,
con pesos y datos sintéticos fijados antes de medir». Se congela el candidato
como DESIGN_FROZEN.md v1 y config.json; autograd 1.8.0 disponible en entorno
local work/e16b-deps, sin instalar ni modificar código histórico. No hay
resultados científicos abiertos. Próximo: implementar ejecutor y controles.

- run_v1: 01_datos, PASS; 0.004 s acumulados. Tablas en `results/run_v1`.

- run_v1: n0_P0, INCONCLUSIVE; 0.177 s acumulados. Tablas en `results/run_v1`.

- run_v1: n0_P1, INCONCLUSIVE; 0.362 s acumulados. Tablas en `results/run_v1`.

- run_v1: n0_P2, INCONCLUSIVE; 0.538 s acumulados. Tablas en `results/run_v1`.

- run_v1: n1_P0, INCONCLUSIVE; 0.719 s acumulados. Tablas en `results/run_v1`.

- run_v1: n1_P1, INCONCLUSIVE; 0.897 s acumulados. Tablas en `results/run_v1`.

- run_v1: n1_P2, INCONCLUSIVE; 1.074 s acumulados. Tablas en `results/run_v1`.

- run_v1: n2_P0, INCONCLUSIVE; 1.250 s acumulados. Tablas en `results/run_v1`.

- run_v1: n2_P1, INCONCLUSIVE; 1.417 s acumulados. Tablas en `results/run_v1`.

- run_v1: n2_P2, INCONCLUSIVE; 1.604 s acumulados. Tablas en `results/run_v1`.

- run_v1: 11_paneles, PASS; 1.612 s acumulados. Tablas en `results/run_v1`.

- run_v1: 12_presupuesto, PASS; 1.621 s acumulados. Tablas en `results/run_v1`.

## Cierre de ejecución v1

1615 checks: 1534 PASS, 0 FAIL, 81 INCONCLUSIVE. Las identidades y derivadas
pasaron; el rango autodiff=2 en 81/81, pero 0/81 cumplen la validación FD
congelada. No se modifican umbrales ni se añaden estados favorables. Se conserva
el resultado inconcluso. No hay evidencia aquí de cambio de rango entre las
composiciones y la suma. Términos mixtos no nulos no bastan para producirlo.

`summary.json`, tablas y `descriptive.json` conservan el detalle. El cociente de
errores FD al dividir paso es ≈4: diagnóstico post hoc compatible con truncamiento
O(δ²), no permiso para ajustar el criterio de rango. Futuro trabajo: protocolo
nuevo de precisión de rango antes de entrenamiento o estudio predictivo.

Dependencia pequeña autograd instalada fuera del repositorio en
/workspace/work/e16b-deps; no se versiona. Presupuesto cumplido (~1.63 s, ~31.5 MiB).
Sin scripts ni datos T2-A ejecutados, recuperados o modificados. Pendiente:
verificar reproducción, enlaces/hashes y alcance, publicar PR dependiente.

## Incidencia del verificador v1

La reproducción byte a byte de checks.csv falló porque la fila `tiempo` registra
segundos observados, distintos entre ejecuciones. Un diagnóstico independiente
comparó las 1615 filas: sólo esa fila difiere, conservando PASS y umbral 120 s;
las otras 1614 coinciden exactamente. Se conserva verification_v1_diagnostic.json
y la primera implementación del verificador en el commit previo a corregirla.
La corrección propuesta compara las filas científicas byte/equivalencia exacta
y valida estado/umbral del tiempo por separado, sin exigir idéntica duración.
No hay cambio en código experimental, protocolo, tablas u outcomes originales.
