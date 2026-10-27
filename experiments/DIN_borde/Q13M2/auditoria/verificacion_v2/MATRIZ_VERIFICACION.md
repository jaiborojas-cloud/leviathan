# Matriz de verificación v2

| Objeto | Resultado | Prueba |
|---|---|---|
| WD3 con Y constante | PASS, F01 resuelto | [Salida](results/changed_cases/F01_WD3_Y.json): LP idéntico, WD inconcluso, PARCIAL |
| WD3 con X constante | PASS | [Salida](results/changed_cases/F01_WD3_X.json) |
| WD3 con L constante | PASS | [Salida](results/changed_cases/F01_WD3_L.json) |
| LP3 con Y constante | PASS | [Salida](results/changed_cases/F01_LP3_Y.json): WD idéntico, LP inconcluso, PARCIAL |
| LP3 con X constante | PASS | [Salida](results/changed_cases/F01_LP3_X.json) |
| LP3 con L constante | PASS | [Salida](results/changed_cases/F01_LP3_L.json) |
| A0 con Y/X/L constantes | PASS, global | [Y](results/changed_cases/F01_A0_Y.json), [X](results/changed_cases/F01_A0_X.json), [L](results/changed_cases/F01_A0_L.json) |
| Ambos exclusivos fallidos | PASS | [Salida](results/changed_cases/both_exclusive_bad.json): ambos inconclusos, no NO_REPRODUCIDA |
| Dos fallos en un brazo | **N01** | [Primaria](results/changed_cases/two_primary_failures_WD.json) y [X/L](results/changed_cases/two_malo_levels_WD.json): falta segundo motivo |
| Compuerta por manipulador | Sin regresión | Casos LP/WD fallidos en [comparación exacta](regression_matrix.json) |
| Fallos exclusivos y compuerta | Sin contaminación | [Salida](results/changed_cases/bad_level_and_bad_gate_WD.json) |
| F02 marcador, CLI original | PASS | [ABORTA3 y marcador intacto](results/cli/marker_original_CLI.json) |
| Directorio, CLI original | PASS | [Salida](results/cli/directory_original_CLI.json) |
| Enlace colgante, inyección | PASS | [Salida](results/cli/dangling_symlink.json) |
| Carrera tras precomprobación | PASS | [Salida](results/cli/exclusive_race.json): ABORTA3 y marcador intacto |
| F03 SHA del informe/JSON | PASS | [Estática](results/static/results.json),25 casos y18 reglas vinculados |
| F04 β_LS≤tol | PASS numérico | [Referencia](results/reference_LS/reference.json); diferencia3.747×10⁻¹⁶ |
| Draws, bloques, A0, D/c/β | PASS, exacto v1 | [Traza](results/cases/bootstrap_trace.json) |
| Cuantiles .0125/.9875 | PASS | Misma traza y funciones AST idénticas |
| Referencia LS960002 | PASS | 2000 draws; archivo externo byte a byte igual al de #117 |
| Réplica LS común LP/WD | PASS | [Compatibilidad](results/cases/compatibility_trace.json) |
| Fallos bootstrap M2 completos | PASS | [WD4](results/cases/WD4_bootstrap_degenerate.json), [A0](results/cases/A0_bootstrap_degenerate.json):94/300 en cada brazo afectado |
| Fallos LS completos | PASS | [23/64](results/cases/LS_failures_do_not_change_primaries.json), primarias inalteradas |
| Error LS explícito por API | PASS | [Salida](results/changed_cases/LS_error_does_not_contaminate.json) |
| Error LS en main y escritura válida | PASS, inyección | [Salida](results/cli/LS_failure_main_valid_write.json), código0 y JSON estricto |
| Tamaños de compatibilidad | PASS | [64/63](results/changed_cases/compatibility_64_63.json), [64/1](results/changed_cases/compatibility_64_1.json), [64/64](results/changed_cases/compatibility_64_64.json) |
| Plan/constantes/dependencias | Sin cambio AST/SHA | [Estática](results/static/results.json); no se repiten109 controles ajenos al diff |
| Casos previos no afectados | Sin regresiones | 19/23 exactamente iguales;4 cambios esperados de F01 |
| Monte Carlo | **No repetido** | Motor/AST y ruta no degenerada sin cambios; no se generan tasas nuevas |

No se ejecutaron las pruebas del autor sobre su fixture G3/C2. F03 verifica la vinculación de la evidencia publicada; los restantes PASS proceden de sintéticos independientes y referencia LS autorizada. Los resultados de #117 se conservan por SHA y no se sobrescriben.
