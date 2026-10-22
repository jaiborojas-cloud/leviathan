# NEM2 — Avance y reanudación

## Estado actual

COMPLETADO (run_v1).
Documentos: README, DESIGN_FROZEN, mathematical_spec, sources, progress, CONCLUSION, requirements, manifest.csv (hashes SHA-256).
Scripts: run.py (cálculo de h, Γ, K y holonomía), verify.py (reproducción byte a byte).
Resultados: results/run_v1/ (summary.json, curvature_grid.csv, holonomy.csv).
Verificación: reproducción byte a byte OK.

## Resultados (run_v1)

- Modelo lineal: 3 features, 2 clases, 8 parámetros, 15 entradas.
- Familia de perspectivas: 2D (p^1, p^2), softmax de rasgos fijos (forma E12).
- Grid: 9×9 = 81 puntos en [-1, 1]^2.
- Puntos SPD: 81/81.
- Rango de K: [-2.34e+02, 4.42e+01].
- Holonomía calculada en 6 puntos (3 centros × 2 deltas).

## Historial

- 2026-10-22: Diseño congelado, documentos iniciales.
- 2026-10-22: Scripts run.py y verify.py implementados en Python puro.
- 2026-10-22: Corrida run_v1 ejecutada.
- 2026-10-22: Verificación byte a byte pasada.
- 2026-10-22: manifest.csv con hashes SHA-256 de 12 archivos propios.
- 2026-10-22: progress.md y CONCLUSION.md actualizados con resultados.
