# Análisis de basales T2-A — Nemotron

Fecha: 2026-10-21
Fuente: `/mnt/d/RIPG_DATA/T2_A/data/baselines/Leviathan_T2A_800_basales_compacto/baseline/states` (solo lectura)
Total de estados analizados: 800

## Distribución por régimen
- true: 800

## Distribución por clasificación
- INJECTIVE_AT_NOMINAL_RADIUS: 800

## Estadísticas globales de métricas RIPG

| Métrica | n | media | mediana | mín | máx | p25 | p75 |
|---|---|---|---|---|---|---|---|
| max_Dexp_condition | 800 | 1.000764 | 1.000774 | 1.000028 | 1.001472 | 1.000599 | 1.000942 |
| min_abs_det_Dexp | 800 | 0.999998 | 1.0 | 0.999653 | 1.0 | 1.0 | 1.0 |
| min_signed_det_Dexp | 800 | 0.999998 | 1.0 | 0.999653 | 1.0 | 1.0 | 1.0 |
| metric_min_eigenvalue | 800 | 0.681514 | 0.672715 | 0.296616 | 1.277685 | 0.552071 | 0.810845 |
| nominal_radius | 800 | 0.079774 | 0.079774 | 0.07976 | 0.079795 | 0.07977 | 0.079777 |
| A_embed | 800 | 0.02 | 0.02 | 0.02 | 0.02 | 0.02 | 0.02 |

## Estadísticas por clasificación

### INJECTIVE_AT_NOMINAL_RADIUS
| Métrica | n | media | mediana | mín | máx |
|---|---|---|---|---|---|
| max_Dexp_condition | 800 | 1.000764 | 1.000774 | 1.000028 | 1.001472 |
| min_abs_det_Dexp | 800 | 0.999998 | 1.0 | 0.999653 | 1.0 |
| min_signed_det_Dexp | 800 | 0.999998 | 1.0 | 0.999653 | 1.0 |
| metric_min_eigenvalue | 800 | 0.681514 | 0.672715 | 0.296616 | 1.277685 |
| nominal_radius | 800 | 0.079774 | 0.079774 | 0.07976 | 0.079795 |
| A_embed | 800 | 0.02 | 0.02 | 0.02 | 0.02 |

## Problemas detectados

- A_embed censurado: 800
- cut_locus_probable: 0
- determinant_sign_change: 0
- metric_nonpositive > 0: 0
- metric_nonfinite > 0: 0
- Con errores no vacíos: 0

## Top 10 splits por número de estados
- split 100: 5 estados
- split 101: 5 estados
- split 102: 5 estados
- split 103: 5 estados
- split 104: 5 estados
- split 105: 5 estados
- split 106: 5 estados
- split 107: 5 estados
- split 108: 5 estados
- split 109: 5 estados

## CSV detallado
Ver `basales_resumen.csv` con 800 filas y 16 columnas.

## Notas
- `max_Dexp_condition` es el acondicionamiento de Dexp (relacionado con κ en RIPG).
- `metric_min_eigenvalue` es el valor propio mínimo de la métrica h (SPD requiere > 0).
- Los valores `min_abs_det_Dexp` y `min_signed_det_Dexp` están cercanos a 1.0, sin signo de colapso del determinante.
- Este análisis es exploratorio y no modifica datos originales.