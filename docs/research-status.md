# Estado científico documentado

## Actualización 2026-10-26 (prevalece sobre el corte anterior en lo que toca)
| Etapa | Estado respaldado | Fuente |
|---|---|---|
| T2-A0 | **INCONCLUSIVE** por limitación del instrumento; X siguió sellado | [cierre](../experiments/T2_A/claude/CIERRE_T2A0_v1_CONGELADO.md) |
| T2-A1 | **NOT_MET** (confirmatorio): X (curvatura en el update 5) no anticipa ρ_borde posterior; W = 0.019, p = 0.33 | [cierre](../experiments/T2_A1/CIERRE_T2A1_v1_CONGELADO.md) |
| DIN-borde D1–D7 | exploratorio: M colapsa sobre el ejemplo de validación menos confiado; el destino se decide entre los updates 10 y 30; la señal temprana es global y ≈ 46 % pasa por la incertidumbre final del dominante | [D1](../experiments/DIN_borde/RESULTADO_D1_2026-10-24.md) … [D7](../experiments/DIN_borde/RESULTADO_D7_2026-10-25.md) |
| DIN-D2, D2b, D2c | teoría y auditoría (sintético): piso 1/n condicional; parte algebraica bajo colapso; defectos de entrada corregidos antes de congelar C1 | [D2](../experiments/DIN_borde/D2/CONCLUSION.md), [D2b](../experiments/DIN_borde/D2b/CONCLUSION.md), [D2c](../experiments/DIN_borde/D2c/CONCLUSION.md) |
| **DIN-C1** | **PASS** (confirmatorio, cohorte nueva de 780): la incertidumbre del ejemplo difícil en el update 10 mejora fuera de muestra la predicción de ρ_borde(250) sobre una base cúbica de ρ_borde(10); D = 0.026, p = 1/5001. Se sostiene con la sensibilidad a las aristas (D = 0.022) | [cierre](../experiments/DIN_borde/CIERRE_DIN_C1_v1_CONGELADO.md), [sensibilidad](../experiments/DIN_borde/C1/sensibilidad_aristas/SENSIBILIDAD_ARISTAS_2026-10-25.md) |
| DIN-G1 (Iris) | exploratorio: el colapso sobre el ejemplo difícil aparece (H2 al 100 %); la señal temprana **no** se reproduce | [G1](../experiments/DIN_borde/G1/CONCLUSION.md) |
| Instrumento ρ_borde v1 | límite demostrado: no alcanza las normales exactas de las aristas, así que mide el mínimo sobre rayos que terminan en un vértice; en Wine, en el update 10, el 68 % de los estados tiene un rayo normal más corto | [G1, suplemento](../experiments/DIN_borde/G1/CONCLUSION.md), [sensibilidad](../experiments/DIN_borde/C1/sensibilidad_aristas/SENSIBILIDAD_ARISTAS_2026-10-25.md) |
| Instrumento ρ_borde v2 (DIN-I2) | validado en 302 estados sintéticos: separa ρ_caras (todas las semirrectas) de ρ_vert (rayos a vértices); 17 veces más rápido que v1 | [I2](../experiments/DIN_borde/I2/CONCLUSION.md) |
| Reevaluación con v2 (DIN-R1) | 1560 + 6240 estados de Wine: T2-A1 sigue NOT_MET; DIN-C1 sigue PASS (D = 0.022 con ρ_caras); D1, D4, D6 y D7 sin cambios. El límite de v1 pesa sobre todo en los updates 5–10 | [etapa 1](../experiments/DIN_borde/R1/RESULTADO_R1_etapa1_2026-10-25.md), [etapa 2](../experiments/DIN_borde/R1/RESULTADO_R1_etapa2_2026-10-25.md) |
| DIN-G2 (mezclas gaussianas, 6 niveles × 20 splits) | exploratorio: H-var (la señal depende de cuánto varía la resolución) **contradicha** según su regla, con potencia baja; en los niveles más solapados M no colapsa | [G2](../experiments/DIN_borde/G2/CONCLUSION.md) |
| DIN-G3 (mezclas gaussianas, 3 niveles × 100 splits, potencia planificada) | exploratorio: **la señal aparece** en el único nivel con colapso (s = 0.8: D = 0.017, p = 0.003); es nula sin colapso, con potencia ≥ 0.8 para D = 0.02 | [G3](../experiments/DIN_borde/G3/CONCLUSION.md) |
| **DIN-C2** | **PASS** (confirmatorio): réplica en la familia gaussiana de G3 (s = 0.8), cohorte nueva de 1000 trayectorias; D = 0.0295, p = 1/5001; régimen de colapso cumplido | [cierre](../experiments/DIN_borde/CIERRE_DIN_C2_v1_CONGELADO.md) |

| DIN-D9 (Wine, exploratorio) | **ninguno pasa**: la geometría del colapso (c, tr M, ρ_caras en u10–30; Δc) no añade predicción de la pérdida en test u250 sobre las medidas baratas; ellas tampoco predicen dentro del split (≈ 10 % de varianza intra-split) | [D9](../experiments/DIN_borde/RESULTADO_D9_2026-10-26.md) |
| DIN-Q13 v2 (manipulación del colapso, gaussianas s = 0.8, 3 brazos × 800 × 5) | **INCONCLUSIVE_MANIPULACION**: WD λ = 0.2 dejó c250 = 0.740 (> 0.70); sin D calculado. La calibración v1 tampoco encontró dosis | [v2](../experiments/DIN_borde/Q13/resultado/RESULTADO_Q13_2026-10-26.md), [calibración v1](../experiments/DIN_borde/Q13/cohorte/RESULTADO_CALIBRACION_v1.md) |
| DIN-Q13-LS (A0 frente a LS, decidido tras la compuerta, antes de D) | **NO_CONCLUYENTE**: A0 D = 0.039 [0.026, 0.054]; LS (c250 = 0.60) D = 0.0083 [0.002, 0.015], p = 0.0002; ΔD [0.020, 0.042]. La señal se atenúa sin desaparecer; LS reduce a la mitad la variación de Y | [Q13-LS](../experiments/DIN_borde/Q13/q13_ls/RESULTADO_Q13_LS_2026-10-26.md) |

| **DIN-Q13-DR** (dosis-respuesta, LS en 6 niveles, 200 × 5 × 6 trayectorias nuevas) | **MODULA** (confirmatorio para la pregunta reformulada): β = 0.077 [0.028, 0.140]; D de 0.034 (c = 0.87) a −0.001 (c = 0.40), monótona (Spearman 1); extremo INDETERMINADO (IC sup de D_L5 = 0.0061); equivalencia NO_ESTABLECIDA | [Q13-DR](../experiments/DIN_borde/Q13DR/resultado/RESULTADO_Q13DR_2026-10-26.md) |
| **DIN-Q13-M2** (penalización de logits y weight decay, 11 niveles × 320 × 5, A0 compartido) | **MODULACION_REPRODUCIDA_EN_DOS_VIAS** (confirmatorio): LP β = 0.051 [0.016, 0.098], WD β = 0.056 [0.013, 0.110] (IC 97.5 %); ambas compatibles con LS; D monótona en c (Spearman 1); extremo LP DESAPARECE, WD INDETERMINADO | [Q13-M2](../experiments/DIN_borde/Q13M2/resultado/RESULTADO_Q13M2_2026-10-28.md) |

Primer resultado confirmatorio predictivo positivo del proyecto: DIN-C1. Es de una sola familia (WineMLP); predictivo, no causal; y su comparación es con una base cúbica. Se sostiene con ρ_borde v2. G3 sugiere una condición: la señal aparece cuando M colapsa (hipótesis **H-colapso**, exploratoria). DIN-C2 lo confirmó en otra familia (PASS), aunque no establece que el colapso sea necesario. Q13 intentó manipularlo: con *label smoothing* la señal baja ≈ 79 % pero sigue presente. Q13-DR lo contrastó con seis dosis y cohorte nueva: **MODULA**. La intensidad de la señal sube con el colapso de forma graduada y deja de detectarse desde c ≈ 0.56. Q13-M2 lo reprodujo con otras dos intervenciones (penalización de logits y weight decay), con pendientes compatibles: la modulación no es propia de LS. Según la [revisión Q15](research-notes/revision-literatura-Q15.md), LS y LP pertenecen a la misma familia de regularización de logits por ejemplo; **WD es la vía de mecanismo independiente**, y también modula. Terminología: el «colapso de M» es la concentración perspectival de M en un ejemplo, no el *neural collapse*. Sigue sin identificarse al colapso como causa, porque las tres intervenciones podrían mover juntas otra variable. D9 descartó, en Wine, que la geometría del colapso prediga la generalización dentro del split.

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
