# Preguntas abiertas y evidencia necesaria

Registro documental, no autorización de ejecución ni protocolo experimental nuevo.
Las preguntas se separan de las afirmaciones respaldadas en el
[mapa de evidencia](claims-and-evidence.md). La prioridad es lógica, no una
estimación de probabilidad de éxito.

| ID | Pregunta | Tipo | Dependencia o bloqueo | Qué permitiría resolverla |
|---|---|---|---|---|
| Q01 | ¿Qué hacía exactamente `relevance_covariant_derivative` y cuál fue la secuencia E6? | Procedencia | Fuente/implementación original y salidas sin reconstrucción retrospectiva | Recuperación con versión, hashes y correspondencia de celdas; [faltantes](../handoff/missing-sources.md) |
| Q02 | ¿Qué elecciones de familia, $H$ y regularización tienen justificación canónica? | Matemática/metodológica | Covariancia no selecciona una referencia única | Criterio explícito, derivación o comparación que delimite dependencia; [E11-F](../archive/import-2026-10-17/originals/E11F_referencias_y_estado_E11.md) |
| Q03 | ¿Qué parte de la geometría es estable frente al panel y modos débiles? | Instrumental | Rango, tamaño de panel y error de estimación | Protocolo propio de estabilidad con error separado de deriva temporal; [E11-J](../archive/import-2026-10-17/originals/E11J_regularizacion_explicita_y_estado_RIPG.md) |
| Q04 | ¿Qué dominio admite inyectividad y minimización con garantías suficientes? | Geométrica/instrumental | Conjugado, corte, frontera y error numérico distintos | Cotas justificadas o estimaciones claramente etiquetadas; [diseño T1](../archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_E15-T1_diseno_topologia_local.md) |
| Q05 | ¿La señal de magnitud/localización replica fuera de las tareas de descubrimiento? | Empírica | Datos independientes, cobertura y dominios válidos | Réplica prospectiva con faltantes conservados; [cierre E13](../archive/import-2026-10-17/originals/E13_cierre_y_punto_de_partida_E14.md) |
| Q06 | ¿Cuándo cambia de forma estable el rango por composición en redes? | Matemática/empírica | Precisar operación y criterio, sin confundir término mixto con pérdida de rango | Nuevos estados y predicción fijada antes de medir; [E16-B](../../experiments/E16/B/CONCLUSION.md) y [C fijado](https://github.com/jaiborojas-cloud/leviathan/blob/4fd7eb5790a7161731e22c238f29138cd66425ac/experiments/E16/C/CONCLUSION.md) |
| Q07 | ¿La señal temprana anticipa eventos futuros con utilidad incremental? | Predictiva | Cohorte elegible, seguimiento, auditorías y regla de decisión congelados | Evaluación del contrato completo, no una visita ni calibración aisladas; [T2-A0](../archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_T2-A0_preregistro.md) |
| Q08 | ¿Cuál es la definición operacional completa de $s_\ell$, $H_\phi$ y juego vacío? | Procedencia/definición | La nota seleccionada reporta cifras pero no todas las reglas | Recuperar protocolo o código original y tratar contribuciones negativas; [estado E15-B1](../archive/import-2026-10-17/originals/Leviathan_RIPG_estado_E15-B1_2026-09-24.md) |
| Q09 | ¿Puede otro colaborador reproducir cada etapa con sus datos externos? | Reproducibilidad | Disponibilidad y permisos de paquetes/checkpoints, no sólo URL | Respaldo verificable y entorno versionado sin credenciales; [guía](reproduction-guide.md) |

| Q10 | ¿Por qué la señal temprana de DIN-C1 aparece en Wine y no en Iris? | Empírica/mecanística | **Avance:** G2 descartó H-var; G3 sugiere H-colapso (aparece donde M colapsa); DIN-C2 la evalúa en confirmatorio. Sigue abierto si el colapso es necesario | Un estudio con familias que varíen la resolución final; [D7](../../experiments/DIN_borde/RESULTADO_D7_2026-10-25.md), [G1](../../experiments/DIN_borde/G1/CONCLUSION.md) |
| Q11 | ¿Qué lleva el 54 % de la señal que no pasa por R (leverage ℓ_k, grado de colapso, escala Fisher)? | Mecanística | Medir esas cantidades en el update 10 sin tautología con M | Plan exploratorio nuevo sobre los datos de descubrimiento |
| Q12 | ¿Cambian los resultados con ρ_borde v2 (todas las caras)? | Instrumental | **Respondida: no** (DIN-R1); los veredictos y descriptivos se sostienen | Reevaluación declarada de T2-A1, D1–D7 y DIN-C1, sin cambiar los veredictos congelados |

| Q13 | ¿El colapso de M es **necesario** para la señal temprana? **Reformulada (2026-10-26):** ¿el colapso *modula* su intensidad? **Respondida en parte (Q13-DR, MODULA):** sí con LS; falta separarlo del manipulador | Causal/mecanística | Q13 v2: INCONCLUSIVE_MANIPULACION (WD no bajó el colapso). Q13-LS: con LS (c250 0.86 → 0.60) la señal cae ≈ 79 % pero sobrevive (NO_CONCLUYENTE). La forma reformulada nació de este resultado. Q13-DR: β = 0.077 [0.028, 0.140], D de 0.034 a −0.001 en seis dosis | Segundo manipulador de dosis estable (p. ej. otra regularización calibrada con más splits) y transferencia a Wine. Antes: dosis-respuesta prospectiva con varias dosis de un manipulador estable, calibración con más splits y control de la varianza de log ρ250. Fuentes: [Q13 v2](../../experiments/DIN_borde/Q13/resultado/RESULTADO_Q13_2026-10-26.md), [Q13-LS](../../experiments/DIN_borde/Q13/q13_ls/RESULTADO_Q13_LS_2026-10-26.md) |
| Q14 | ¿La **distancia al borde de saturación** (qué tan lejos está un estado de colapsar en una elección dura) anticipa algo en modelos que razonan en latente o cuantizan conceptos? En HybridAgent (arXiv 2610.18861) se sale del modo latente por similitud coseno con el ancla `</latent>`; en NCM (Next-Concept Modeling) se elige el código más cercano del diccionario (VQ) | Extensión / analogía | La familia perspectival a(P) = softmax(f·P) tiene la forma de una atención; emitir un token o elegir un código es su vértice (el borde). Hoy es una **analogía de forma**, sin resultado | Definir ρ_borde para la decisión «seguir en latente / emitir» o «elegir código»; medirla en un modelo abierto (p. ej. HybridAgent-14B) y ver si anticipa errores o la calidad del razonamiento, con un diseño propio congelado. Fuentes: [arXiv 2610.18861](https://www.emergentmind.com/papers/2610.18861), [NCM](https://www.edenai.co/fr/post/ncm-vs-llm-next-concept-modeling) |
| Q15 | ¿Qué parte de la línea DIN es **nueva** frente a la literatura? Tres preguntas concretas: (a) ¿alguien propuso antes la métrica D? (b) ¿alguien mostró que una medida tan temprana predice el colapso o la geometría final? (c) ¿el fenómeno aparece en otros modelos y datasets? | Revisión de literatura | Búsqueda rápida (2026-10-27), no exhaustiva: (a) D **no** es nueva; es el R² fuera de muestra (Campbell y Thompson 2008) o ΔR² con validación cruzada; lo propio es su aplicación a X10 → ρ_borde. (b) Hay trabajos afines, pero no el mismo resultado: puntajes tempranos por ejemplo (EL2N/GraNd, Paul et al. 2021), *dataset cartography* (Swayamdipta et al. 2020); el *neural collapse* (Papyan et al. 2020) es otro fenómeno. No se encontró la modulación por el colapso de M. **Relacionado:** Bernstein et al. (2026, [arXiv 2610.16161](https://arxiv.org/html/2610.16161)) usan la Fisher del modelo **final** para localizar la memorización en direcciones de los pesos (ResNet-20/CIFAR-10). No estudian lo temprano ni la distancia al borde. **Puente abierto, sin resultado:** ¿el ejemplo sobre el que colapsa M vive en las direcciones de Fisher que ellos asocian con la memorización? (c) Solo hay evidencia propia: Wine y gaussianas con un MLP; Iris sin señal | **Revisión sistemática con fuentes citadas**; cuándo hacerla, en la sección «Cuándo revisar la literatura (Q15)» |

## Cuándo revisar la literatura (Q15)

La revisión sistemática es **obligatoria** antes de cualquiera de estos tres hitos, y se hace en el **primero** que ocurra:
1. **Antes de escribir algo para fuera del proyecto** (preprint, artículo, charla o publicación). Toda afirmación de novedad («no se conocía», «primera vez») necesita esa revisión.
2. **Antes de diseñar la transferencia a otros modelos o datasets** (Q15c). La literatura dice qué arquitecturas y medidas tempranas ya se estudiaron, y así se eligen comparaciones que aporten en lugar de repetir.
3. **Al cerrar Q13-M2.** Ahí queda fijada la afirmación más fuerte de la línea («la modulación se reproduce con tres intervenciones»), y es la que hay que contrastar.

Mientras ningún hito ocurra, la revisión no bloquea los experimentos internos. Se puede adelantar si un resultado lo pide (por ejemplo, para comparar D con una medida publicada) o si el responsable lo decide.

## Dependencias entre preguntas

Q01 y Q08 son faltantes de fuente: no se rellenan mediante nuevos experimentos.
Q02–Q04 afectan la interpretación de Q05–Q07, aunque una pregunta empírica puede
usar un estimando regularizado condicionado si se declara expresamente.
El control instrumental de precisión C no resuelve por sí solo Q02, Q04 o Q06.
No se presenta esta tabla como secuencia obligatoria que modifique protocolos.

## Preguntas todavía más amplias

Canonicidad en dimensión mayor, tomografía Grassmanniana, benchmarks físicos,
teoría de aproximación y mecanismos causales figuran en las
[rutas históricas](../research-directions.md). Antes de abrirlas hay que formular
objetos y falsadores específicos. No hay aquí una teoría causal o una reducción
universal de dimensión derivada sólo de agrupar perspectivas.

## Cómo mantener el registro

Añadir fuente y fecha/corte al resolver una pregunta; conservar su formulación
anterior y la evidencia que motivó el cambio. Distinguir «sin respuesta»,
«inconcluso por instrumento» y «hipótesis no respaldada con instrumento válido».
Una nueva métrica, umbral, muestra o resumen exige su propio diseño; no retocar
silenciosamente una pregunta para hacerla coincidir con resultados conocidos.
