# NEM3 — Avance y reanudación

## Estado actual

COMPLETADO (run_v1).
Documentos: README, DESIGN_FROZEN, mathematical_spec, sources, progress, CONCLUSION, requirements, manifest.csv (hashes SHA-256).
Scripts: run.py (cálculo de observables geométricos), verify.py (reproducción byte a byte).
Resultados: results/run_v1/ (summary.json, observables.csv, checks.csv).
Verificación: reproducción byte a byte OK.

## Resultados (run_v1)

- Modelo lineal: 3 features, 2 clases, 8 parámetros, 15 entradas.
- Familia de perspectivas: 2D (p^1, p^2), softmax de rasgos fijos (forma E12).
- Grid: 9×9 = 81 puntos en [-1, 1]^2.
- Puntos SPD: 81/81 (panel base y perturbado).

### Panel base
| Observable | Valor |
|---|---|
| A (área) | 6.44e-01 |
| E (energía total) | 1.59e+02 |
| E_K (energía media) | 2.47e+02 |
| C_A = sqrt(E_K) | 1.57e+01 |
| R_eff | 1.77e-02 |
| Lambda_0.25 | 0.9893 |
| Lambda_0.50 | 0.9984 |
| Lambda_0.75 | 0.9997 |

### Panel perturbado (epsilon = 0.2)
| Observable | Valor | Cambio relativo |
|---|---|---|
| A | 5.78e-01 | -1.02e-01 |
| E_K | 3.56e+04 | +1.43e+02 |
| C_A | 1.89e+02 | +1.10e+01 |
| R_eff | 1.49e-04 | -9.92e-01 |
| Lambda_0.25 | ~1.0 | ~1.0 |
| Lambda_0.50 | ~1.0 | ~1.0 |
| Lambda_0.75 | ~1.0 | ~1.0 |

## Historial

- 2026-10-22: Diseño congelado, documentos iniciales.
- 2026-10-22: Scripts run.py y verify.py implementados en Python puro.
- 2026-10-22: Corrida run_v1 ejecutada (panel base y perturbado).
- 2026-10-22: Verificación byte a byte pasada.
- 2026-10-22: manifest.csv con hashes SHA-256 de 12 archivos propios.
- 2026-10-22: progress.md y CONCLUSION.md actualizados con resultados.
