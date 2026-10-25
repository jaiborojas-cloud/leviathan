# Estado científico documentado

## Actualización 2026-10-25 (prevalece sobre el corte anterior en lo que toca)
| Etapa | Estado respaldado | Fuente |
|---|---|---|
| T2-A0 | **INCONCLUSIVE** por limitación del instrumento; X siguió sellado | [cierre](../experiments/T2_A/claude/CIERRE_T2A0_v1_CONGELADO.md) |
| T2-A1 | **NOT_MET** (confirmatorio): X (curvatura en el update 5) no anticipa ρ_borde posterior; W = 0.019, p = 0.33 | [cierre](../experiments/T2_A1/CIERRE_T2A1_v1_CONGELADO.md) |
| DIN-borde D1–D7 | exploratorio: M colapsa sobre el ejemplo de validación menos confiado; el destino se decide entre los updates 10 y 30; la señal temprana es global y ≈ 46 % pasa por la incertidumbre final del dominante | [D1](../experiments/DIN_borde/RESULTADO_D1_2026-10-24.md) … [D7](../experiments/DIN_borde/RESULTADO_D7_2026-10-25.md) |
| DIN-D2, D2b, D2c | teoría y auditoría (sintético): piso 1/n condicional; parte algebraica bajo colapso; defectos de entrada corregidos antes de congelar C1 | [D2](../experiments/DIN_borde/D2/CONCLUSION.md), [D2b](../experiments/DIN_borde/D2b/CONCLUSION.md), [D2c](../experiments/DIN_borde/D2c/CONCLUSION.md) |
| **DIN-C1** | **PASS** (confirmatorio, cohorte nueva de 780): la incertidumbre del ejemplo difícil en el update 10 mejora fuera de muestra la predicción de ρ_borde(250) sobre una base cúbica de ρ_borde(10); D = 0.026, p = 1/5001. Se sostiene con la sensibilidad a las aristas (D = 0.022) | [cierre](../experiments/DIN_borde/CIERRE_DIN_C1_v1_CONGELADO.md), [sensibilidad](../experiments/DIN_borde/C1/sensibilidad_aristas/SENSIBILIDAD_ARISTAS_2026-10-25.md) |
| DIN-G1 (Iris) | exploratorio: el colapso sobre el ejemplo difícil aparece (H2 al 100 %); la señal temprana **no** se reproduce | [G1](../experiments/DIN_borde/G1/CONCLUSION.md) |
| Instrumento ρ_borde v1 | límite demostrado: no alcanza las normales exactas de las aristas, así que mide el mínimo sobre rayos que terminan en un vértice; en Wine, en el update 10, el 68 % de los estados tiene un rayo normal más corto | [G1, suplemento](../experiments/DIN_borde/G1/CONCLUSION.md), [sensibilidad](../experiments/DIN_borde/C1/sensibilidad_aristas/SENSIBILIDAD_ARISTAS_2026-10-25.md) |

Primer resultado confirmatorio predictivo positivo del proyecto: DIN-C1. Es de una sola familia (WineMLP); predictivo, no causal; y su comparación es con una base cúbica.

## Corte anterior (se conserva)

Corte de fuentes: 2026-10-17 03:46 UTC. Revisión documental, sin nuevas ejecuciones.

| Etapa | Estado respaldado | Fuente |
|---|---|---|
| C1-A | INCONCLUSIVE; no rescatar excluyendo estados o reduciendo área | [Cierre C1](archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_E15-C1_cierre_y_E15-C2_inicio.md) |
| C1-A2 | Dos casos GEOMETRIC_NONINJECTIVITY: split0/true/j1 y j3 | [Auditoría](archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_E15-C1-A2_cierre.md) |
| T1-A | Panel histórico de 80 estados auditado | [Cierre](archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_E15-T1-A_cierre_y_T1-B_inicio.md) |
| T1-B | Correlación descriptiva ≈0.9549 a radio común, 38 true admisibles; control geométrico esperado | [Cierre](archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_E15-T1-B_cierre.md) |
| T2-A | 800 basales; 1 visita cerrada; 0 horizontes completos | [Progreso](archive/import-2026-10-17/originals/Leviathan/Repro/T2_A/progress.md) |

J5/update25 tiene [cierre documental](archive/import-2026-10-17/originals/Leviathan/Repro/T2_A/Leviathan_T2A_cierre_split8_j5_update25_v1.md), pero la clasificación topológica y Y siguen desconocidos. J7/update25 está pausado operacionalmente en paso128, r=0.074554276173483244; todavía no es radio nominal ni visita completa: [avance](archive/import-2026-10-17/originals/Leviathan/Repro/T2_A/j7_update25_avance.md).

Las [800 filas de outcomes](archive/import-2026-10-17/originals/Leviathan/Repro/T2_A/outcomes.csv) conservan Y vacío; [visits.csv](archive/import-2026-10-17/originals/Leviathan/Repro/T2_A/visits.csv) registra únicamente j6/update25. La cohorte contiene estado basal histórico NOT_OPENED; no usarlo como descripción del seguimiento actual.

## Límites

Frontera de dominio, conjugado y cut locus son fenómenos distintos. La convergencia numérica no es un certificado global. Los 80 estados T1 no confirman hipótesis formuladas a partir de ellos. No hay resultado confirmatorio predictivo nuevo establecido **en este corte**; ver la actualización del 2026-10-25 arriba.

E1–E8 conservan la [revisión estática anterior](archive/review-before-import/docs/research-status.md). Persisten la dependencia ausente `relevance_covariant_derivative` y la diferencia entre salidas E6 de celdas129/132. E14 y el cierre autónomo E9 siguen sin fuente primaria independiente recuperada; ver [faltantes](handoff/missing-sources.md).
