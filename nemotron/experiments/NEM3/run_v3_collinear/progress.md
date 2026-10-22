# NEM3 run_v3_collinear — Avance y reanudación

## Estado actual

COMPLETADO (run_v1).
Documentos: README, DESIGN_FROZEN, mathematical_spec, sources, progress, CONCLUSION, requirements, manifest.csv (hashes SHA-256).
Scripts: run.py, verify.py.
Resultados: results/run_v1/ (summary.json, observables.csv, checks.csv).
Verificación: reproducción byte a byte OK.

## Resultados (run_v1)

- Dataset: sintético colineal (5 features, 3 clases, 50 entradas, 17 parámetros).
- Colinearidad: x2 = 0.95*x1 + ruido, x3 = 0.90*x1 + 0.50*x2 + ruido.
- Grid: 9×9 = 81 puntos en [-1, 1]².
- Puntos SPD: 81/81.

### Fisher y modos débiles
| Métrica | Panel base | Panel perturbado |
|---|---|---|
| max eigenvalue | 2.20e+00 | 2.28e+00 |
| min eigenvalue | 2.55e-06 | 3.65e-06 |
| n_weak_modes (tau=1e-6) | 0 | 0 |

### Observables geométricos
| Observable | Panel base | Panel perturbado | Cambio relativo |
|---|---|---|---|
| A | 5.03e+00 | 4.90e+00 | -2.5e-02 |
| E_K | 5.91e+00 | 5.81e+00 | -1.7e-02 |
| C_A | 2.43e+00 | 2.41e+00 | -8.3e-03 |
| R_eff | 1.96e-02 | 2.11e-02 | +7.9e-02 |
| Lambda_0.25 | 0.9976 | ~1.0 | ~1.0 |
| Lambda_0.50 | 0.9999 | ~1.0 | ~1.0 |
| Lambda_0.75 | 1.0 | ~1.0 | ~1.0 |

## Comparación con run_v1 (Wine, no colineal)

| Métrica | run_v1 (no colineal) | run_v3_collinear (colineal) |
|---|---|---|
| Fisher min eigenvalue | 1.81e-02 | 2.55e-06 (7000× menor) |
| C_A base | 1.57e+01 | 2.43e+00 |
| C_A perturbado | 1.89e+02 (+12×) | 2.41e+00 (≈ sin cambio) |
| R_eff base | 1.77e-02 | 1.96e-02 |
| R_eff perturbado | 1.49e-04 (-99%) | 2.11e-02 (≈ sin cambio) |

## Historial

- 2026-10-22: Diseño congelado, documentos iniciales.
- 2026-10-22: Scripts run.py y verify.py implementados en Python puro.
- 2026-10-22: Corrida run_v1 ejecutada.
- 2026-10-22: Verificación byte a byte pasada.
- 2026-10-22: manifest.csv con hashes SHA-256 de 11 archivos propios.
- 2026-10-22: progress.md y CONCLUSION.md actualizados con resultados.
