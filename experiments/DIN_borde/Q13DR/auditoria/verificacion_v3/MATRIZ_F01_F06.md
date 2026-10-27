# Regresión completa F01–F06 y tabla de decisiones

Se reejecutaron los51 contenedores de casos de #105, con los mismos datos sintéticos y seed910100, contra el snapshot v3. Los nombres se conservaron literalmente. Dos excepciones Aborta de la API son esperadas: IDs duplicados y ajenos; no son crashes. En la CLI se exige código3, prefijoABORTA y ausencia de traceback. [Salida completa](results/cases/summary.json).

| Hallazgo de #104 | Resultado v3 | Evidencia |
|---|---|---|
| F01: c puntual versus población común | RESUELTO, sin regresión. El caso antiguo14/20 se rechaza por80%; el válido19/20 usa exactamente la mediana común. Los seis niveles comparten draws, copias en bloque original y D/c/beta recalculados. Error máximo beta frente a MCO independiente1.18e−15. | [Punto válido](results/cases/F01_valid_95percent_common.json), [traza](results/cases/v1_bootstrap_trace_pairing_folds_D_c_beta.json) |
| F02: degeneraciones/crash/NaN | RESUELTO en los casos reproducibles. L degenerada: INCONCLUSIVE con6/16 fallos en N20 y5/16 en N200. El caso antiguo104/200 se rechaza por comunes. N01 y N05 también resueltos. | [N20](results/cases/v1_L_degenerate_in_bootstrap_only.json), [N200](results/cases/v1_L_bootstrap_constant_N200.json), [N01–N05](MATRIZ_N01_N05.md) |
| F03: plan/dosis/esquema | RESUELTO en la matriz. Rechaza N0, fraccional, bool y401; niveles incorrectos, eps ausente, seis eps0 y clave nivel ausente. También eps enorme y entradas ilegibles. | [CLI original](results/cases/v1_plan_missing_nivel_crash.json), [87 validaciones directas](results/diffs/plans.json) |
| F04: Spearman con constantes/empates | RESUELTO. Seis D idénticos dan null; cuatro controles coinciden con rangos medios de SciPy. | [D iguales](results/cases/v1_complete_identical_levels.json), [dominio/reglas](results/checks/domain_and_rules.json) |
| F05: significado del margen | RESUELTO en texto y rango. El límite es .02·rango(c), no un .010 universal; con c común invertida rango=.3 y margen=.006. | [N02](results/cases/new_reversed_common_c_range.json), [borrador aplicable](sources/v3/DISENO_DIN_Q13DR_BORRADOR_v2.md) |
| F06: confundir ABORTA con crash | RESUELTO. La CLI satisface las tres condiciones estrictas en los casos inválidos; el verificador no acepta la simple aparición de «ABORTA» en un traceback. | [Caso sin nivel](results/cases/v1_plan_missing_nivel_crash.json), [aserciones](verification.json) |

## Decisiones y ambigüedades anteriores

| Tema | Resultado conservado |
|---|---|
| Precisión L4–L5 | Pérdida.09 aceptada, .11 rechazada; ganancia.07 aceptada. Ganancia/pérdida.07 en L2 rechazada. |
| Comunes | Se rechazan6/12,14/20 y104/200. El caso exactamente160/200 puede avanzar; se requieren≥3 válidas por nivel, no necesariamente las mismas k. |
| Faltantes |5/100 por nivel permitidos;6/100 dan INCONCLUSIVE. IDs duplicados/ajenos abortan. |
| Dominio |27 comprobaciones de finitud, q/acc∈[0,1], c∈(0,1] y rho positiva pasan. |
| Umbrales exactos | Se conserva .86−.56=.29999999999999993 y su rechazo; .95−.90<.05 y su aceptación. No se añaden tolerancias. |
| Primaria y equivalencia | IC[.001,.01] da MODULA primaria y NO_MODULA secundaria simultáneamente. No se suman como categorías excluyentes. |
| Extremo | PERSISTE tiene prioridad si L5 es PASS, incluso con IC superior<.006. |
| Tendencia | Sigue siendo pendiente lineal, no orden de las seis D. Spearman es descriptivo. |
| Potencia/equivalencia | No se promete potencia de NO_MODULA; las tasas de #105 no se recalculan. La verificación no estima dependencia entre niveles con datos reales. |
| JSON | CLI válido produce JSON estricto; NaN/Infinity de la limpieza se convierten a null. |

La [comprobación funcional](results/checks/domain_and_rules.json) repite además los27 controles de dominio y cuatro de Spearman. Ninguna de estas comprobaciones cambia estados o conclusiones de etapas anteriores.
