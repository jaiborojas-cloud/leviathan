# Matriz de revisión de M2

Versión auditada: commit `66f5de58`, no versiones posteriores. [Fuentes y hashes](sources/provenance.json), [diseño de auditoría](DESIGN_FROZEN.md), [conclusión](CONCLUSION.md).

| Objeto | Evaluación | Evidencia y alcance |
|---|---|---|
| Bootstrap LP/WD pareado | OK | [Traza](results/cases/bootstrap_trace.json): draws960001 idénticos, copias con bloque original, A0 idéntico. |
| Recálculo D, mediana c, β | OK | Traza con c variable por split; MCO independiente, error máximo β 4.44×10⁻¹⁵. |
| IC primario 97.5 % | OK | Cuantiles .0125/.9875 idénticos a referencia; no se usa el IC95 secundario para MODULA. |
| LS independiente | OK | [2000 draws](results/reference_LS/reference.json), semilla960002, sin fallos; M2 usa960001. Misma tabla LS permitida, no otra cohorte. |
| Misma réplica LS por brazo | OK | [Traza](results/cases/compatibility_trace.json): mismo objeto LS, IC de β_m,b−β_LS,b correcto. |
| β_LS exacta | F04 | No literal; diferencia3.747×10⁻¹⁶, [dos primarias originales coincidentes](results/reference_LS/numeric_comparison.json). |
| Fallos bootstrap LS | OK | [23/64 fallos sintéticos](results/cases/LS_failures_do_not_change_primaries.json) completos; primarias inalteradas, sin IC LS/compatibilidad; LP−WD sigue disponible. |
| Compuertas independientes | OK | Fallos LP/WD por separado conservan al sano y dan PARCIAL; fallo A0 afecta ambos. |
| Ajuste puntual independiente | **F01** | WD3 o LP3 con Y constante borra al sano, sin cambiar sus datos ni estadísticas. |
| X/L constante exclusivo | Ambigüedad F01 | El código declara global; aclarar excepción frente a independencia solicitada y tabla del diseño. |
| Fallos bootstrap por brazo | OK | [WD4](results/cases/WD4_bootstrap_degenerate.json):94/300 fallos WD,0LP; [A0](results/cases/A0_bootstrap_degenerate.json):mismos94 en ambos. Todos los índices coinciden con el draw esperado; no redibuja. |
| c constante decimal puntual | OK | [Comunes exactamente80 %](results/cases/common_c_LP_decimal_constant.json): gate válido, c común=.1; solo LP inconcluso por pendiente no definida. |
| c constante decimal en réplica | OK | [API adicional](results/api_edges/results.json): `FloatingPointError`, no pendiente espuria. |
| Rango de c común invertido | OK, limitación declarada | [Caso](results/cases/common_range_reversed.json): rango=max−min positivo. Gate usa todas las válidas; pendiente usa comunes11. No se intercambian esas poblaciones. |
| Plan11 nombres/brazos/dosis/tope320 | OK | [109 casos](results/validation/schema.json): tipo, orden, longitud, dosis exacta, NaN/inf, entero enorme,320/321. |
| IDs duplicados/ajenos | OK | Excepción `Aborta` esperada en los [casos](results/cases/summary.json). |
| Faltantes y comunes11 | OK | 5/100 no activa >5 %;6/100 sí. Umbrales globales declarados; no es independencia por brazo de la elegibilidad de cohorte. |
| Dominio físico | OK | [27 controles](results/domain/domain.json); una q inválida se cuenta como faltante. Sin tolerancias añadidas a umbrales. |
| Entradas ilegibles/ausentes/directorio | OK | [CLI](results/validation/summary.json):8 entradas erróneas devuelven3, prefijoABORTA, sin traceback. |
| Salida y JSON | Mixto | JSON estricto, no NaN; **F02** sobreescribe salida existente. |
| Evidencia de pruebas del autor | **F03** | Informe/JSON archivados corresponden a SHA anteriores; no se presupone si hubo otra ejecución. |
| Tamaño familiar bajo nulos | Compatible en modelo | [800 tablas](results/monte_carlo_v1/summary.json), N320, presupuestos nominales. Error familiar1.50 %/2.25 %; no prueba universal. |

## Interpretaciones que deben quedar claras

- `NO_CONCLUYENTE` es un veredicto primario válido sin evidencia positiva; no equivale a `INCONCLUSIVE` por un análisis indefinido. La etiqueta conjunta no debe convertir esta segunda categoría en ausencia de modulación.
- La señal de A0 y las restricciones de cohorte común son deliberadamente compartidas. La independencia de los contrastes LP/WD no significa ignorar fallos de A0 o cambiar los splits comunes según el resultado.
- «Sin diferencia detectada» de β_m−β_LS no prueba equivalencia ni una misma causa. El IC de compatibilidad se calcula con incertidumbre de ambas cohortes.
- La monotonicidad estricta y los umbrales de rango/precisión se aplican tal como están escritos. Empates de c no satisfacen el gate. No se agregan tolerancias después de observar las tablas.
- La frase del diseño §1 que atribuye la modulación al colapso debe leerse con la limitación de §7: tres intervenciones aún pueden mover juntas otra variable. Recomendación de redacción, no defecto demostrado del algoritmo.

## Herencia de las auditorías Q13-DR

Se leyeron [#104](sources/reference/DR_audit_conclusion.md), [#105](sources/reference/DR_v2_conclusion.md) y [#107](sources/reference/DR_v3_conclusion.md). No se reabrieron sus cierres ni se reasignaron sus estados. Aquí se comprobó en M2: bloque original en copias, recálculo de pendiente, protección de c constante, rango no negativo, plan con entero enorme, lectura ausente/directorio y preservación completa de fallos. F01 es una interacción de los dos manipuladores en el tramo puntual que la antigua auditoría de una sola vía no resolvía.
