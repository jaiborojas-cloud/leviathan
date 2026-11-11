# Q15: criterios de cribado vigentes (compilación al 2026-11-10)

**Naturaleza:** es una **compilación** de reglas ya decididas por el responsable y registradas en el PR #138 y en el repositorio. **No crea reglas nuevas ni cambia ninguna.** Si este texto y su fuente difieren, **manda la fuente citada**. Sirve para tres cosas:
1. como referencia única para un lector nuevo, por ejemplo un chat nuevo de Codex;
2. para el repaso consolidado de los lotes 05–25 y A1;
3. como anexo metodológico de Q15.

Lo compiló Claude a pedido del responsable (2026-11-10). La pregunta, las consultas, los topes, el corte y el diccionario siguen siendo los del [protocolo v3](../PROTOCOLO_OPERATIVO_v3.md).

---

## 1. Qué se compara (protocolo v3, §1 y §1.1)

| Punto | Pregunta | Subpuntos |
|---|---|---|
| 1 | Antecedente de D como comparación predictiva | R² fuera de muestra respecto de una base, validez incremental, validación por grupos, métrica frente a aplicación |
| 2 | Confianza temprana que anticipa confianza, **dificultad** o geometría final | Por ejemplo y por corrida; dentro de split frente a entre arquitecturas; ajuste por información temprana rival; fuera de muestra |
| 3 | Geometría perspectival de DIN | **3a** kernel de gradientes blanqueados por Fisher; **3b** pullback por el campo softmax; **3c** longitud mínima de semirrectas al borde |
| 4 | La concentración o la escala de logits modulan la señal temporal | **4a** calibración, sobreconfianza y regularización; **4b** vínculo entre concentración, confianza y escala; **4c** modulación del incremento predictivo |

**Diccionario (§1.1), en resumen:**
- D = 1 − SSE_completo/SSE_base, fuera de muestra.
- M = R(F + γI)⁻¹Rᵀ. Siempre se anota qué Fisher se usa: del modelo, empírica, GN u otra.
- G(P) = Jᵀ M J no se identifica automáticamente con Fisher–Rao, con la Fisher de parámetros ni con el NTK.
- d_borde ≤ ρ_ray.
- c = max M_nn / tr M **no** es tr F, ni rango efectivo, ni *neural collapse*.
- La escala de logits es la **RMS de logits centrados entre clases**.
- Aplicar *temperature scaling* no es, por sí solo, evidencia de modulación de D.

## 2. Decisiones de cribado (protocolo v3, §6)

| Decisión | Cuándo |
|---|---|
| `INCLUIR_PARA_TEXTO` | Investigación primaria, teórica o empírica, que define, demuestra o prueba un objeto o una afirmación de los puntos 1–4. También: evaluación incremental, fundamentos de geometría de la información o kernels pertinentes, dinámica temprana, dificultad por ejemplo y calibración o regularización que puedan explicar el resultado |
| `CONTEXTO` | Revisiones, tutoriales y notas secundarias, que sirven como ruta a originales y no son prioridad primaria. También los casos que D2, D3 y D4 envían a CONTEXTO |
| `EXCLUIR_FUERA_TEMA` | Aplicación sin contenido relevante para las preguntas, o **uso solo instrumental** de una señal, sin estudiar qué capta ni cuándo falla |
| `PENDIENTE_ACCESO` / `PENDIENTE_VERIFICACION` | Resumen vacío, truncado o no atribuible al autor, o identidad dudosa. **Un paywall, un resumen no disponible o un enlace roto no justifican «no pertinente»** |
| `EXCLUIR_POR_TITULO_SIN_RESUMEN` | Solo con la regla del §5 |

**Reglas generales:**
- Se decide por los objetos y las afirmaciones **del resumen**, nunca por palabras clave, por número de citas ni por lo que se sepa de la obra por fuera.
- Cada obra lleva una razón propia, la fecha UTC real y el revisor.
- No se excluye un antecedente porque use otro dataset, otra arquitectura u otro acrónimo, si contiene la misma afirmación.

## 3. Cercanía (solo para INCLUIR y CONTEXTO)

La cercanía **no cambia la inclusión**: solo ordena la lectura de texto completo. Las obras **BAJA no se leen completas**, salvo que lo requiera una fuente ALTA o MEDIA. La cercanía global es la más alta que justifique el resumen, con desglose por subpunto (`puntos_Q15`).

### 3.1 Punto 2: rúbrica del 2026-11-09 a las 14:55 (SHA `80b83f1d…`), modificada por D1

| Nivel | Criterio |
|---|---|
| **ALTA 2** | Señal temprana de dinámica (curvatura, Fisher, normas o escala de logits, NTK, entropía) que anticipa un estado posterior de geometría, confianza, **dificultad** (añadida por D1) o calibración. También el estudio de la **ventana temprana misma** (períodos críticos, *break-even*) |
| **MEDIA 2** | Extrapolación de curvas o predicción del desempeño final desde épocas tempranas |
| **BAJA 2** | HPO o NAS que usan esa predicción como componente. **D1:** también los estudios de **validez de una medida de dificultad por ejemplo** sin una señal temprana ni una predicción del desempeño final |

Una predicción de exactitud final no recibe ALTA 2 solo por usar datos tempranos. No se inventa una ventana que el resumen no especifique.

### 3.2 Punto 3a: rúbrica del 2026-11-09 a las 19:58 (SHA `e0d6b157…`, commit `69201593`)

| Nivel | Criterio |
|---|---|
| **ALTA 3a** | La Fisher, el NTK o la GN como **objeto geométrico** de la red: espectro, rango efectivo, relación Fisher–NTK, límites de la Fisher empírica, pullback, métrica inducida, singularidades |
| **MEDIA 3a** | **Aproximación o precondicionador** basado en la Fisher o la GN (K-FAC, Shampoo y similares), sin un resultado sobre la geometría |
| **BAJA 3a** | La Fisher como **componente** de una aplicación (EWC, poda, cuantización). **Práctica auditada (lotes 20–22):** los estudios del **Hessiano** o de *sharpness* también son BAJA 3a, salvo que identifiquen el objeto con la Fisher, la GN o el NTK |

### 3.3 Punto 4: recalibración del lote 08 (SHA `cca6a9b4…`), con D2 y D4

| Nivel | Criterio |
|---|---|
| **ALTA 4a** | El resumen enuncia un **mecanismo de descalibración o de sobreconfianza** |
| **ALTA 4b** | Relación explícita entre la **escala o la temperatura de los logits y la confianza o la concentración**, más allá de aplicar TS |
| **MEDIA 4a** | Método nuevo de calibración o de regularización de la confianza sin esa afirmación. Fundamentos adyacentes cuando el resumen justifica la proximidad |
| **BAJA 4a** | Aplicar TS o ECE a un dominio sin calibrador ni mecanismo nuevos |

## 4. Decisiones del responsable D1–D4

Se aplican **hacia adelante** desde el lote indicado y **hacia atrás solo en el repaso consolidado**.

| Regla | Desde | Fuente | Contenido |
|---|---|---|---|
| **D1** | Lote 19 | [6758641743](https://github.com/jaiborojas-cloud/leviathan/pull/138#issuecomment-6758641743) | La validez de una medida de dificultad por ejemplo es **BAJA 2**. Sube a ALTA 2 si la señal es temprana y anticipa confianza, dificultad, geometría o calibración, o si estudia la ventana temprana; sube a MEDIA 2 si predice el desempeño final o extrapola curvas. Las señales tienen que estar **estudiadas**, no solo usadas |
| **D2** | Lote 19 | ídem | La generalización o la robustez **en general**, cuyo resumen no trata calibración, sobreconfianza, confianza, incertidumbre ni regularización, va a **CONTEXTO BAJA**, no a INCLUIR. No convierte en CONTEXTO cualquier dataset o aplicación |
| **D3** | Lote 22 | [6769657278](https://github.com/jaiborojas-cloud/leviathan/pull/138#issuecomment-6769657278) | (1) La **memorización** se incluye solo si estudia una señal de dificultad, confianza o dinámica temprana; si no, va a CONTEXTO BAJA. (2) El **desaprendizaje y la privacidad**, incluidos los ataques de reaprendizaje y la inferencia de pertenencia, van a EXCLUIR, salvo que estudien la calibración o la confianza como objeto. (3) La **dificultad usada solo como insumo** de poda, coreset, selección o evaluación eficiente va a EXCLUIR |
| **D4** | Lote 26 | [6772520624](https://github.com/jaiborojas-cloud/leviathan/pull/138#issuecomment-6772520624) | **Detección OOD.** Si el puntaje se basa en confianza, logits, softmax, energía o temperatura, va a **INCLUIR, MEDIA 4a**: ALTA 4a si enuncia un mecanismo de sobreconfianza y ALTA 4b si relaciona la escala con la confianza. Si se basa en distancia de rasgos, densidad o autosupervisión, sin tratar la confianza, va a **CONTEXTO BAJA**. Usar temperatura no implica por sí solo ALTA 4b |

## 5. Exclusión por título sin resumen (commit `4b1404cd`, con precisiones)

- **Alcance:** registros que, después de A0 y de leer todas sus posiciones, **siguen sin resumen de autor**. No cubre los `CONFLICTO_IDENTIDAD`.
- **Regla:** se excluye solo si el título es **inequívocamente ajeno** a todos los puntos **y** no contiene **ningún término del vocabulario de Q15**. El vocabulario es el de la regla más esta precisión ([6753896046](https://github.com/jaiborojas-cloud/leviathan/pull/138#issuecomment-6753896046)): *learning*/aprendizaje en cualquier sentido, *curve*, *extrapolat\**, *forecast\**, *predict\** y *performance* como predicción.
- **Precisión del 2026-11-09** ([6758487224](https://github.com/jaiborojas-cloud/leviathan/pull/138#issuecomment-6758487224)): se aplica a **títulos en cualquier idioma**, según la traducción literal; por ejemplo, 학습 es «learning».
- **Aplicación estricta, decidida por el responsable:** el término cuenta aunque aparezca en sentido físico o ajeno. Ante cualquier duda, el registro queda PENDIENTE.
- **Auditoría:** al menos el 20 % de las exclusiones por título y como mínimo 30, o todas si son menos. **Un solo error reabre todas** las exclusiones por título del lote, salvo que la auditoría haya sido un censo completo; en ese caso se corrige solo la obra fallida (decisión del responsable, [6758487224](https://github.com/jaiborojas-cloud/leviathan/pull/138#issuecomment-6758487224)).
- Es reversible y se reporta aparte en el embudo. Nunca cuenta como evidencia de ausencia.

## 6. Identidad y duplicados

- **R4**, con la enmienda IDENTIDAD_CONFIRMADA_METADATOS ([6744475206](https://github.com/jaiborojas-cloud/leviathan/pull/138#issuecomment-6744475206)): se fusionan obras solo con el mismo DOI o la misma familia de arXiv, o con **título normalizado idéntico, la misma lista de apellidos en orden y un año compatible**.
- La coincidencia de título sola se registra como alerta y **no se fusiona**.
- Las obras distintas de un mismo grupo no se fusionan por compartir autores.

## 7. Formato de cada lote

- **Selección:** 100 obras, fijada **antes de leer**. Las reglas nuevas se registran con SHA y fecha UTC real **antes de seleccionar**.
- **Paquete:** decisiones (`cribado_loteNN.csv`), cercanía (`cercania_loteNN.csv`, con desgloses del 2 y del 3a cuando aplique), evidencia con hashes de todas las posiciones elegibles, registro de lectura, avances, rúbricas aplicables, informe, `MANIFEST.sha256` con LF y `.sha256` del zip.
- Las correcciones van **en un paquete aparte**, sin sobrescribir lo aprobado.
- Hay un solo lector declarado, sin cribado doble simulado, y ninguna conclusión de novedad.

## 8. Calidad medida y prácticas que derivan de ella

- **Concordancia a ciegas M40** (lotes 19–20, [6769647740](https://github.com/jaiborojas-cloud/leviathan/pull/138#issuecomment-6769647740)):

  | Par | κ en decisión (3 clases) | κ en incluir o no |
  |---|---|---|
  | Codex – Fable | 0.41 | 0.60 |
  | Codex – Argon | 0.62 | 0.70 |
  | Fable – Argon | 0.68 | 0.89 |

  La discrepancia es sistemática: el primer lector **incluye de más**. Eso motivó D3. Está prevista una segunda medición después del repaso consolidado.
- **Extracción de texto completo:** cada extracción lleva una auditoría independiente contra la fuente, de preferencia de **otra familia de modelos** (lección E14).
- **Procedencia de las afirmaciones.** El responsable la escribió el 2026-11-11 como **precisión** de una práctica que ya se aplicaba, no como regla nueva:
  - **Ninguna afirmación sobre una obra puede venir del conocimiento previo de un modelo.** Si no está en el resumen del snapshot o en el texto leído, **no consta**.
  - Vale para el cribado, la extracción, las auditorías y la síntesis, y para cualquier modelo: Codex, Argon, Claude, Fable, DeepSeek, Qwen u otros.
  - **Motivo:** los modelos no tienen un índice de la literatura, sino una memoria imprecisa de sus datos de entrenamiento. Esa memoria puede mezclar versiones o artículos parecidos y no cubre las obras posteriores a su corte. En los lotes 30–33, 166 de 354 obras son de julio de 2026 o después.
  - **Tampoco cuenta la ausencia en la memoria.** Que un modelo no recuerde una obra o un resultado no es evidencia de que no exista. La novedad solo se adjudica en la síntesis, con el corpus.

## 9. Repaso consolidado pendiente (no ejecutado)

Antes de la lectura de texto completo se aplicarán D1–D4 y las rúbricas 2 y 3a a los lotes **05–25 y A1**. Se incluyen también las observaciones registradas en las auditorías (W04628, W05702, W03908, W03866, W04471, W04877, W04888, W04974, W05042 y otras), sin reabrir decisiones aprobadas fuera de ese repaso.
