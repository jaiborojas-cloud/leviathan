# Catálogo de experimentos (consulta rápida)

Corte: `main` del 2026-10-23 (hasta el PR #56). Una fila por experimento: qué preguntó, sobre qué sistema, su estado oficial, el hallazgo en una línea y dónde leerlo. **El estado y el hallazgo los fija el cierre enlazado**; esta tabla solo los resume y no los modifica. La última columna indica la utilidad para el replanteo de T2-A1 (sección 8). Índices más detallados: [experiment-index.md](experiment-index.md), [experiments/README.md](../experiments/README.md) y [E16/README.md](../experiments/E16/README.md).

**Sistemas.** *Wine real*: MLP 13→64→32→3 entrenada en Wine (true/random). *Sintético 2→2→1*: red tanh pequeña sin entrenamiento (E16). *Notebook*: ejemplos de `Perspectivas.ipynb`.

## 1. Etapas iniciales (E1–E9)
| ID | pregunta | sistema | estado | hallazgo | fuente |
|---|---|---|---|---|---|
| E1–E5 | gradientes, covariancia, trayectorias, Fisher, transporte | notebook | código sin cierre recuperado | controles instrumentales previstos | [revisión estática](archive/review-before-import/docs/experiment-index.md) |
| E6 | holonomía neuronal | notebook, rebanada 2D | salidas con discrepancia | exploratorio; procedencia sin aclarar | ídem |
| E7/E7b | geometría de relevancias | red 2→4→2 | PASS almacenados | control esperado, no prospectivo | ídem |
| E8 | relevancia y transporte local | notebook | falta una función | reproducción no establecida | ídem |
| E9 | síntesis y axioma | — | cierre autónomo no recuperado | [contexto](archive/import-2026-10-17/originals/RIPG_contexto_vigente_axioma.md) | [faltantes](handoff/missing-sources.md) |

## 2. Geometría en entrenamiento real (E10–E14)
| ID | pregunta | sistema | estado | hallazgo | fuente | T2-A1 |
|---|---|---|---|---|---|---|
| E10 | ¿la geometría anticipa el aprendizaje? | MLP real | CERRADO_EXPLORATORIO | la precisión se separó **antes** que la geometría; sin poder incremental robusto (N01) | [E10](../experiments/E10/CONCLUSION.md) | antecedente negativo para «señal temprana» |
| E11 | estabilidad, covariancia, alcance tangente | MLP 64→128→10 | CERRADO_EXPLORATORIO | la métrica depende de **panel**, referencia, regularización y rango; con paneles chicos el contraste cambia de signo | [E11](../experiments/E11/CONCLUSION.md) | **panel = factor de primer orden** (H-split) |
| E12 | campo perspectival, conexión, curvatura | MLP | CERRADO_EXPLORATORIO | holonomía = control derivado; \|K_true\| > \|K_random\| en 36/40 pares (exploratorio) | [E12](../experiments/E12/CONCLUSION.md) | — |
| E13 | curvatura a área intrínseca común | Digits, Wisconsin, Wine | INCONCLUSIVE | interno 36/37; réplica Wine: el jet cuadrático pierde positividad en 37/40 true | [E13](../experiments/E13/CONCLUSION.md) | **validar cobertura antes de contrastar** |
| E14 | reconstrucción métrica positiva | — | cierre no recuperado | — | [faltantes](handoff/missing-sources.md) | habría sido el antecedente directo |

## 3. E15 y T1 (Wine, panel de 80 estados)
| ID | pregunta | estado | hallazgo | fuente | T2-A1 |
|---|---|---|---|---|---|
| E15-B6 | auditoría del primario | CIERRE_NUMERICO | C_A ≈ 1052.61 a 8192 rayos | [B6](../experiments/E15/B6/CONCLUSION.md) | — |
| E15-B7 | split 5 true / 6 random | PASS_NUMERICO | seis fuentes, contorno 2048 | [B7](../experiments/E15/B7/CONCLUSION.md) | — |
| E15-B8 | independencia de malla | PASS_NUMERICO | true con más energía y concentración | [B8](../experiments/E15/B8/CONCLUSION.md) | — |
| E15-C1-A | contraste a D0.02 en 40 pares | INCONCLUSIVE | 2 dominios no admisibles; **no reducir el área ni excluir** | [C1-A](../experiments/E15/C1-A/CONCLUSION.md) | regla L3 |
| E15-C1-A2 | diagnóstico de esos 2 | GEOMETRIC_NONINJECTIVITY | split0 j1, j3: conjugados en r ≈ 0.0760–0.0764; área embebida 0.0154 y 0.0169 | [C1-A2](../experiments/E15/C1-A2/CONCLUSION.md) | **0.02 está en el borde** |
| T1-A | mapa topológico de 80 estados | MAPA_COMPLETO_DESCRIPTIVO | 2/40 true y 0/40 random no inyectivos | [T1-A](../experiments/T1/A/CONCLUSION.md) | tasa de base |
| T1-B | X frente a C_A a radio común | EXPECTED_GEOMETRIC_CONTROL | Spearman 0.955 en r* = 0.0569 (Jacobi) | [T1-B](../experiments/T1/B/CONCLUSION.md) | **X y desenlace ligados; radio fijo viable** |
| E15-T2 | diseño H-T2-1 (transversal) | diseño, no ejecutado | cola top 10 % por X, lift ≥ 3 | [diseño](archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_E15-T2_diseno_validacion_externa.md) | alternativa barata |

## 4. T2-A0 (predicción temporal, Wine, 800 trayectorias)
| ID | qué | estado | hallazgo | fuente |
|---|---|---|---|---|
| Prerregistro | X en el update 5 → Y en 10 visitas | congelado | — | [prerregistro](archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_T2-A0_preregistro.md) |
| Piloto (u25, 20) | visitas y topes | CERRADO | 16 INJECTIVE, 2 GNI, 2 INCONCLUSIVE (split 8) | [cierre piloto](../experiments/T2_A/claude/piloto/CIERRE_PILOTO_20_2026-10-21.md) |
| T5 | certificar escape del disco | v4: j5 certificada, j7 no | primer T5 del proyecto: el rayo sale de la familia en r = 0.07447, U = 0.01943 | [corrida 4](../experiments/T2_A/claude/piloto/certificacion_t5/RESULTADO_corrida4_v4_2026-10-21.md) |
| Lote 0 | 128 de 180 visitas | detenido por disco | 76 pausadas: 71 en calibración, 5 en auditoría; agrupadas por split | [lote 0](../experiments/T2_A/claude/produccion/lote_0/CIERRE_LOTE0_2026-10-22.md) |
| Cierre | — | **INCONCLUSIVE** (limitación del instrumento) | X sigue sellado | [cierre](../experiments/T2_A/claude/CIERRE_T2A0_v1_CONGELADO.md) |

## 5. T2-A1 (en curso)
| ID | qué | estado | fuente |
|---|---|---|---|
| Diseño v2 | desenlace D «disco no construible»; W dentro del split | borrador | [diseño v2](../experiments/T2_A1/DISENO_T2A1_BORRADOR_v2.md) |
| Fase 0a | instrumento D (vía C con factores dobles) | **PASA**; j5 da U₂ = 0.02015 → D = ? | [resultado 0a](../experiments/T2_A1/fase0/RESULTADO_0a_2026-10-23.md) |
| Fase 0b | cobertura en splits 8–11 | corriendo | [protocolo 0b](../experiments/T2_A1/fase0/PROTOCOLO_0b_v1_CONGELADO.md) |

## 6. E16 — composición, métricas y caminos (sintético 2→2→1, sin entrenamiento)
Línea independiente: no continúa E15/T2. Todo es exploratorio o de validación instrumental.
Actualización documental de esta sección hasta AF; el corte inicial de la cabecera se conserva para el resto del catálogo. AE cambia la familia perspectival sobre la red; AF usa estados softmax sintéticos de 27 componentes, sin datos T2.

| ID | pregunta | estado | hallazgo | T2-A1 |
|---|---|---|---|---|
| [E16](../experiments/E16/CONCLUSION.md) | ¿qué conserva la composición de perspectivas? | EXPECTED_GEOMETRIC_CONTROL | el rango depende de cancelaciones y de la Hessiana de la composición; contraejemplos de descenso | — |
| [B](../experiments/E16/B/CONCLUSION.md) | rango en red nueva | identidades PASS, rango INCONCLUSIVE | las diferencias finitas no alcanzan la compuerta | — |
| C (fijado por commit) | otro protocolo de rango | PASS_NUMERICAL | 99/99 | — |
| [D](../experiments/E16/D/CONCLUSION.md) | réplica en configuraciones nuevas | PASS_NUMERICAL | 396/396 rangos, 216/216 negativos | — |
| [E](../experiments/E16/E/CONCLUSION.md) | distancia y anisotropía entre métricas | exploratorio | conservar el rango ≠ conservar la métrica; **distancia afín-invariante SPD** y anisotropía κ, siempre estimables | **medida local continua** (opción C) |
| [F](../experiments/E16/F/CONCLUSION.md) | longitudes de caminos fijos | INCONCLUSIVE | 239/324 | — |
| [G](../experiments/E16/G/CONCLUSION.md) | resolver F | PASS_NUMERICAL | 324/324: primitiva + Gauss–Legendre + cotas Bernstein | **longitud validada** |
| [H](../experiments/E16/H/CONCLUSION.md) | transferencia de G | PASS_NUMERICAL | 324/324 en datos nuevos | — |
| [I](../experiments/E16/I/CONCLUSION.md) | caminos de 2 tramos | PASS_NUMERICAL | 18/18 no lineales más cortos que la recta | caminos mínimos |
| [J](../experiments/E16/J/CONCLUSION.md)–[Q](../experiments/E16/Q/CONCLUSION.md) | refinar caminos óptimos (mallas, Hausdorff, representación, energía) | INCONCLUSIVE en todos | **la longitud converge antes que la forma**; la forma del camino óptimo no se estabiliza | **advertencia**: un instrumento de caminos mínimos heredaría este problema |
| [R](../experiments/E16/R/CONCLUSION.md) | precondicionamiento | INCONCLUSIVE | KKT físico mejor en 4/4, sin terminar | — |
| [S](../experiments/E16/S/CONCLUSION.md) | parada por KKT físico auditado | PASS_NUMERICAL | 8 cuadráticos con 3 auditorías MP | criterio de parada usable |
| [T](../experiments/E16/T/CONCLUSION.md)–[Y](../experiments/E16/Y/CONCLUSION.md) | segundo orden, descensos, subespacios, refinamiento | exploratorios, mínimos UNKNOWN | **curvatura negativa** (direcciones de descenso) en los cuadráticos finos: los «óptimos» son sillas numéricas | — |
| [Z](../experiments/E16/Z/CONCLUSION.md) | reestacionarizar y luego el espectro | PASS_PROTOCOL | 12/12 primer orden; 8 testigos MP negativos | — |
| [AA](../experiments/E16/AA/CONCLUSION.md) | KKT ≤ 1e-7 | INCONCLUSIVE | 8 cuadráticos agotan 4800 iteraciones | — |
| [AB](../experiments/E16/AB/CONCLUSION.md) | región de confianza | INCONCLUSIVE (progreso) | 5/8 llegan a KKT ≤ 1e-7; 4 testigos negativos en 528 segmentos | — |
| [AC](../experiments/E16/AC/CONCLUSION.md) | ¿negativas discretas o conjugados continuos? | INCONCLUSIVE (v2 VALID_EXPLORATORY; v1 INVALID conservada) | 12 índices continuos 0; faltan bloques discretos de Z/AB para resolver H2 | — |
| [AD](../experiments/E16/AD/CONCLUSION.md) | ¿planitud y negativas en el cociente normal? | INCONCLUSIVE | suma/producto/cuadrática K≡0; NN positivo y cociente sin negativas admisibles; tres LIBRE no cumplen la ruta de estacionariedad | — |
| [AE](../experiments/E16/AE/CONCLUSION.md) | ¿conjugados, índice y corte en la familia tipo E12? | Q1/Q2/Q3 INCONCLUSIVE | K mayormente negativa; todo censurado, sin conjugados observados; r_deg y A(r_deg) UNKNOWN | — |
| [AF](../experiments/E16/AF/CONCLUSION.md) | ¿degeneración estable, Morse y reducción de desconocidos en sintéticos? | Q1 PASS; Q2 INCONCLUSIVE; Q3 PASS; Q4 FAIL | cinco eventos y 35/40 censurados; Q3 exploratorio, sin escapes ni reducción de «?» (0→0); Q2 pendiente | — |

## 7. Patrones transversales
1. **Los instrumentos fallan donde la geometría es interesante:** E13 (37/40 true), C1-A (2 dominios), T2-A0 (split 8) y, en sintético, E16 J–Q.
2. **La longitud o el área convergen antes que la forma o la topología** (E16 L–P; T5: el área se acota aunque no se resuelva la inyectividad).
3. **El panel pesa** (E11, sospecha H-split en T2-A).
4. **X y los desenlaces geométricos están ligados por Jacobi** (T1-B).
5. **Un PASS de primer orden no certifica mínimos** (E16 S–AB): no presentar candidatos numéricos como certificados.
6. **Las composiciones del sintético 2→2→1 son planas; los fenómenos de conjugados exigen otra familia** ([AE](../experiments/E16/AE/CONCLUSION.md), [AF](../experiments/E16/AF/CONCLUSION.md)).

## 8. Para replantear el desenlace de T2-A1
| opción (ver conversación del 2026-10-23) | antecedente | lectura |
|---|---|---|
| A. radio fijo r* en vez de área 0.02 | T1-B midió a radio común sin problemas en 80 estados | evita la calibración del área (las pausas de split 10 parecen de presupuesto); no resuelve split 8 |
| C. medida local continua | E16-E: distancia afín-invariante SPD y anisotropía κ, estimables siempre | cambio de la métrica en P0 entre el update 5 y la visita, sin integrar geodésicas; riesgo de tautología con X (T1-B) |
| D. radio de primera degeneración, con censura | T5 (cota de área monótona), C1-A2 (conjugados) | las visitas difíciles darían una cota en vez de «?» |
| distancia por caminos mínimos en vez de la exponencial | E16 G–H (longitud validada), S (parada KKT) | **no recomendado como instrumento principal**: E16 J–AB muestra que la forma de los caminos óptimos no se estabiliza |
