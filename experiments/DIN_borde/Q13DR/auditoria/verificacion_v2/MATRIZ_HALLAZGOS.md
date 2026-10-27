# F01–F06 y decisiones: resultado contra245d735f

Analista v2 SHA afb807aad20830e0402c5fdb8f946f783b2a0835f497855e12364bf1fae356e6.
Cada caso usa filas sintéticas del mismo generador/seed910100 de #104. Se
conservan los nombres v1 aunque su resultado esperado haya cambiado. Parámetros
reducidos B39/NB16 aíslan lógica; los casos CLI usan nominales completos si
llegan al análisis. Nada se sobrescribe en la auditoría anterior.

| Hallazgo | Resultado de regresión | Evidencia y alcance |
|---|---|---|
| F01, población c punto/bootstrap | **RESUELTO** | El caso literal con14/20 comunes ahora termina INCONCLUSIVE por80%. El [caso adicional válido19/20](results/cases/F01_valid_95percent_common.json) llega al punto y sus c coinciden exactamente con las medianas comunes. |
| F02, crash/NaN bootstrap | **PARCIAL** | [L degenerada N200](results/cases/v1_L_bootstrap_constant_N200.json) da INCONCLUSIVE con cinco fallos de16, sin crash. El [caso c singular antiguo](results/cases/v1_singular_beta_N200.json) se rechaza por comunes104/200. Persisten otra constancia no identificada (N01) y diagnóstico truncado (N05). |
| F03, plan/dosis/esquema | **PARCIAL** | Los mismos seis eps0, eps ausente, clave nivel ausente, n fraccional y n0 ahora ABORTA/código3/sin traceback. Bool, nivel bool y401 también. Nuevas entradas enteras enormes y archivos ilegibles aún causan crash: N03/N04. |
| F04, Spearman con empates | **RESUELTO** | [Seis D idénticos](results/cases/v1_complete_identical_levels.json) producen null. Rangos medios parciales coinciden con SciPy; también constante decimal .1. |
| F05, interpretación del margen | **RESUELTO EN TEXTO** | El diseño dice .02·rango(c), sin tope universal .010. En c ordenada, salida .5→.010 correcta. Aparece un error nuevo de cálculo del rango común no ordenado: N02. |
| F06, ABORTA versus crash | **RESUELTO** | [Sin clave nivel](results/cases/v1_plan_missing_nivel_crash.json) aborta con3, prefijoABORTA y sin traceback. La nueva heurística exige esas condiciones; los crashes nuevos se identifican como tales. |

## Ambigüedades y decisiones del responsable

| Tema de #104 | Verificación v2 |
|---|---|
| Precisión L4–L5 | Resuelto: pérdida .09 aceptada, .11 rechazada; ganancia .07 aceptada. L2 con ganancia/pérdida .07 se rechaza. [Casos](results/cases/summary.json). |
| Mínimo común | Resuelto: [6/12](results/cases/v1_common_splits_only_half.json) y104/200 se rechazan. Exactamente160/200 pasa; se exige≥3 válidas por nivel. |
| Inicializaciones comunes | Aclarado: se emparejan splits con≥3 por nivel, no se exige que sean las mismas k. Coincide con el diseño; esa limitación continúa declarada. |
| Dominio físico | Resuelto para el contrato elegido:27 pruebas de q/acc∈[0,1], c∈(0,1], rho positiva y finitud. [Resultados](results/checks/domain_and_rules.json). X sigue requiriéndose finita; no se añaden restricciones ajenas al diseño. |
| Comparaciones exactas | Definición explícita, comportamiento anterior conservado: .86−.56 puede dar .29999999999999993 y fallar; .95−.90 da .04999999999999993 y pasa. Sin redondeo ni tolerancias añadidas. |
| MODULA y NO_MODULA simultáneos | Resuelto: IC[.001,.01] devuelve MODULA primaria **y** NO_MODULA secundaria, no una elección por prioridad. |
| Tendencia versus monotonía | Resuelto en alcance: se prueba tendencia lineal, no orden de seis D. Spearman sólo describe. |
| Potencia de equivalencia | Resuelto en promesa: no se exige ni promete potencia para NO_MODULA; regla de dimensionamiento sólo MODULA. Se repite la tasa secundaria sin ocultarla. |
| Dependencia entre niveles | Se fija independencia para dimensionar y correlaciones como sensibilidad. Esta verificación no estima dependencia de Q13 real ni identifica una matriz6×6. El carácter conservador es condicional al modelo de simulación. |

## Emparejamiento y serialización

La [traza reejecutada](results/cases/v1_bootstrap_trace_pairing_folds_D_c_beta.json)
confirma mismos draws en los seis niveles, copias en bloque original y recálculo
de D/c/β; c cambia realmente entre réplicas. El escritor [CLI completo](results/cases/new_CLI_complete.json)
produce JSON estricto, sin NaN/Infinity. Limpiar NaN a null también pasa sus pruebas
funcionales; no reemplaza la necesidad de detectar una β no identificada (N01).

La suite del autor se leyó, pero no se ejecutó ni se abrió su fixture C2. Se
inspeccionan sus35+15 controles declarados sin tomarlos como prueba independiente.
Los [defectos nuevos/residuales](NUEVOS_DEFECTOS.md) explican por qué no se da un
aprobado global para congelar aunque muchas regresiones estén corregidas.
