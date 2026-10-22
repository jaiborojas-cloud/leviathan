# T2-A1 — antecedentes para el diseño (2026-10-22)

Síntesis de lectura del repositorio. No es diseño ni autorización de ejecutar. Cada punto cita su fuente; los cierres enlazados prevalecen sobre esta síntesis.

## 1. De dónde viene T2-A1
- **T2-A0** (prerregistro: predicción temporal; X = máximo angular de κ(Dexp) en el borde de r* = 0.05697156262709151 en el update 5; Y = GEOMETRIC_NONINJECTIVITY en alguna de 10 visitas futuras) quedó **cerrado INCONCLUSIVE por limitación del instrumento**, con la cohorte incompleta ([cierre](../T2_A/claude/CIERRE_T2A0_v1_CONGELADO.md)).
- Motivos: una visita T5 basta para la compuerta INCONCLUSIVE ([E2 v1](../T2_A/claude/E1/Leviathan_RIPG_T2-A0_enmienda_E2_v1_CONGELADA.md)); 76 de 128 visitas del lote 0 pausadas y agrupadas por split; ≈ 1.2 GB y hasta 54 min por visita ([lote 0](../T2_A/claude/produccion/lote_0/CIERRE_LOTE0_2026-10-22.md)).
- **Antes de T2-A0** hubo otro diseño, H-T2-1 ([E15-T2](../../docs/archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_E15-T2_diseno_validacion_externa.md)): una sola auditoría por estado entrenado, cola top 10 % por X, éxito con lift ≥ 3 y ≥ 8 positivos en ≥ 3 splits. Era transversal (mismo estado) y mucho más barato.

## 2. Cinco lecciones que el diseño debe incorporar

### L1. El área 0.02 está en el borde donde estas geometrías dejan de ser un disco
| caso | qué pasa | escala | fuente |
|---|---|---|---|
| C1-A2: split0 j1, j3 | el mapa exponencial se pliega antes de 0.02 | conjugados r ≈ 0.0760–0.0764; área embebida 0.0154 y 0.0169 | [C1-A2](../E15/C1-A2/CONCLUSION.md) |
| T2-A: split8 j5, j7, update 25 | rayos escapan (T5) | escape r ≈ 0.0745; A₀ ≈ 0.0169–0.0171 | [certificación T5](../T2_A/claude/piloto/certificacion_t5/) |
| T2-A lote 0 | pausas en trayectorias completas | split 8: 45/45 por progreso radial bajo | [lote 0](../T2_A/claude/produccion/lote_0/CIERRE_LOTE0_2026-10-22.md) |

En estados true, el disco de área 0.02 a menudo **no existe** como disco simple. Un instrumento que solo sabe responder «inyectivo» o «no inyectivo» deja sin respuesta los casos que más interesan.

### L2. Validar la cobertura del instrumento antes de abrir contrastes (E13)
El jet cuadrático perdió positividad en 37/40 estados true y 0/40 random: el fallo fue diferencial y la réplica quedó INCONCLUSIVE ([E13](../E13/CONCLUSION.md)). Su cierre fijó la regla: medir cobertura y error contra el campo exacto, con compuerta, **antes** de abrir resultados; y separar desarrollo (recuperación) de confirmación (datos no abiertos).

### L3. No reducir el área para rescatar (C1)
«No reducir áreas, excluir estados ni convertir supervivientes en confirmación» ([C1-A](../E15/C1-A/CONCLUSION.md); repetido en E15-T2). Un área menor solo sería admisible como **observable nuevo** con justificación propia, nunca como rescate. La alternativa compatible es **incluir** la imposibilidad del disco en el desenlace.

### L4. Predictor y desenlace están ligados por Jacobi (T1-B)
En el mismo estado, X y C_A se correlacionan 0.95 a radio común: «control geométrico esperado» ([T1-B](../T1/B/CONCLUSION.md)). Los dos positivos de C1-A2 ocupaban los puestos 1 y 2 de X. Una predicción transversal es casi tautológica; lo informativo es la **predicción temporal**, o la utilidad incremental frente a comparadores.

### L5. El panel es un factor de primer orden (E11)
Con paneles pequeños la métrica cambia materialmente y el contraste puede invertir el signo ([E11-G/I](../E11/CONCLUSION.md)). En T2-A, los 27 puntos del panel de validación (f) dependen solo del split. Que las pausas se agrupen por split es compatible con un **efecto de panel** (hipótesis H-split, sin probar). Un predictor global podría seleccionar «splits con mal panel» en lugar de trayectorias.

## 3. Otros antecedentes
- **E10 (N01):** la geometría no anticipó la precisión en ese diseño. Antecedente negativo para «señal temprana» ([negativos](../../docs/research-notes/negative-results.md)).
- **E14** (reconstrucción métrica positiva): sin cierre recuperado ([faltantes](../../docs/handoff/missing-sources.md)).
- **Certificación T5** ya da una cota superior rigurosa del área A(t) = ∫∫|j| (monótona aunque haya pliegues) más un término Jacobi/Grönwall ([protocolo v1](../T2_A/claude/piloto/certificacion_t5/PROTOCOLO_certificacion_T5_v1_CONGELADO.md)). Es la pieza natural para certificar «el disco no alcanza 0.02».

## 4. Restricciones heredadas
- **X y comparadores siguen cerrados** hasta congelar el instrumento y las reglas de medición de T2-A1 (decisión del responsable, 2026-10-22).
- Existe una copia en claro de medidas basales fuera del repo, en cuarentena ([desviación](../T2_A/claude/DESVIACION_ACCESO_BASELINE_NEMOTRON_2026-10-21.md)). No se consulta.
- **Ya abiertos (desarrollo):** splits 8–10 (piloto u25 y lote 0, 128 visitas). **Sin visitas futuras:** split 11 y splits 12–167. Las 52 visitas evaluadas del lote 0 siguen sin clasificar; solo se abren si este diseño, ya congelado, lo prevé.
- Basales del update 5: 800 trayectorias true, todas INJECTIVE_AT_NOMINAL_RADIUS. Checkpoints `checkpoint_005` verificados por hash; reentrenar desde ellos es determinista.
