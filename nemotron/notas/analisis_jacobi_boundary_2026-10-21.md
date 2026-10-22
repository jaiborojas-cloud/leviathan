# Análisis Jacobi y Frontera — Basales T2-A (Nemotron)

Fecha: 2026-10-21
Fuente: `/mnt/d/RIPG_DATA/T2_A/data/baselines/Leviathan_T2A_800_basales_compacto/baseline/states` (solo lectura)
Total de estados: 800

## Estadísticas Jacobi (agregado por clave de archivo)

| Clave | n | media | mediana | mín | máx |
|---|---|---|---|---|---|
| max_intrinsic_condition | 3200 | 1.000764 | 1.000774 | 1.000028 | 1.001472 |
| minimum_signed_determinant | 3200 | 0.999998 | 1.0 | 0.999653 | 1.0 |
| audit_min_eigenvalue | 3200 | 0.681515 | 0.672716 | 0.296616 | 1.277695 |
| audit_max_condition | 3200 | 1.978538 | 1.847927 | 1.140404 | 4.463985 |

## Estadísticas Frontera (agregado por clave de archivo)

| Clave | n | media | mediana | mín | máx |
|---|---|---|---|---|---|
| origin_winding | 3200 | 1.0 | 1.0 | 1.0 | 1.0 |
| turning_number | 3200 | 1.0 | 1.0 | 1.0 | 1.0 |
| signed_chart_area | 3200 | 0.022113 | 0.021479 | 0.012638 | 0.041577 |
| union_chart_area | 3200 | 0.022113 | 0.021479 | 0.012638 | 0.041577 |

## Conteo de topología frontera
- frontera simple: 3200
- frontera válida: 3200
- intersecciones totales: 0
- primera intersección detectada: 0

## Conteo de problemas Jacobi
- auditoría nonpositive: 0
- auditoría nonfinite: 0
- conjugate_minimum no nulo: 0

## CSV detallado
Ver `jacobi_boundary_resumen.csv` con 800 filas.

## Notas
- `max_intrinsic_condition` es el acondicionamiento intrínseco máximo (κ).
- `minimum_signed_determinant` es el determinante mínimo con signo (cercano a 1 = sin colapso).
- `audit_min_eigenvalue` y `audit_max_condition` provienen de la evaluación de auditoría en la malla.
- `origin_winding` y `turning_number` describen la topología de la frontera.
- Este análisis es exploratorio y no modifica datos originales.