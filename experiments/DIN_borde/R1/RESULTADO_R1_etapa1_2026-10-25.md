# DIN-R1 etapa 1 — la cohorte DIN-C1 con ρ_borde v2 (2026-10-25)

**Naturaleza:** reevaluación posterior y declarada, según `PLAN_R1.md`, registrado antes de calcular. **El veredicto de DIN-C1 (PASS) no cambia.** Se calculó con ρ_borde v2 r3 (`2ac015a2…`) en la VM del equipo del responsable, con 2 procesos y en lotes reanudables. **1560 de 1560 estados** quedaron como `VALID_NUMERICAL_ESTIMATE`: 0 fallos, 0 rechazos. Tabla: `r1_c1_v2.csv`, SHA `0c6bd90f9a115ffd3f1492d15021efbff9e47db89381b766ffd8640fb4ac85c9`.

## v2 frente a v1
| update | gana una cara (ρ_caras < ρ_vert) | ρ_caras/v1: mínimo / mediana / máximo | ρ_vert/v1: mínimo / percentil 1 / mediana / máximo |
|---|---|---|---|
| 10 | **67.8 %** | 0.517 / 0.891 / 1.000009 | 0.591 / 1.000 / 1.000 / 1.0001 |
| 250 | 13.3 % | 0.830 / 1.000 / 1.00009 | 1.000 / 1.000 / 1.000 / 1.00009 |

- **v1 coincide con ρ_vert** (los rayos a vértices) en prácticamente todos los estados. La excepción es un caso aislado en el update 10, con un cociente de 0.59: ahí el v1 perdió un cono.
- **En el update 10**, ρ_caras es menor en el 68 % de los estados. Reproduce exactamente la auditoría de normales de arista del PR #81.

## Sensibilidad de la primaria de DIN-C1 (análisis congelado; no confirmatorio)
| desenlace y covariable | veredicto | D | p | pendiente | W_adj | D con base de grado 5 |
|---|---|---|---|---|---|---|
| v1 (congelado) | PASS | 0.0256 | 0.0002 | +0.81 | 0.199 | 0.026 |
| L = ρ_caras(10) | PASS | 0.0220 | 0.0004 | +0.82 | 0.198 | 0.040 |
| L e Y con ρ_caras | PASS | 0.0217 | 0.0004 | +0.81 | 0.195 | 0.040 |
| L e Y con ρ_vert | PASS | 0.0256 | 0.0002 | +0.81 | 0.199 | 0.0085 |

**Lectura:** el resultado de DIN-C1 **se sostiene con el instrumento corregido**. Con ρ_vert, la base de grado 5 da un D menor (0.0085); no se investigó si lo explica el caso aislado del v1. Es un secundario y no cambia la lectura.

**Siguiente (etapa 2):** los estados de T2-A1 y DIN-borde (updates 5, 50, 150 y 250, splits 12–167), unos 3140, en el equipo del responsable.
