# Q15: registro de aportes de la literatura para RIPG

**Qué es:** un registro vivo de lo que cada obra leída en texto completo **aporta** a las preguntas del instrumento, punto por punto. Se actualiza con cada extracción auditada.

**Qué no es:** **no es una adjudicación de novedad.** La síntesis y la adjudicación se hacen según el §8 del protocolo v3, con todo el corpus. Este registro solo ordena lo leído.

**Reglas del registro:**
1. Cada entrada separa **lo que afirma la fuente** (demostrado, postulado o ilustrado) de la **inferencia** nuestra o del extractor, que va marcada.
2. Solo entran obras con **extracción auditada por otra familia de modelos**. Las que tienen la auditoría pendiente van en una sección aparte y marcadas.
3. Ninguna afirmación sale de la memoria de un modelo (precisión del 2026-11-11 en [criterios vigentes](CRITERIOS_VIGENTES_Q15_2026-11-10.md), §8).
4. Las fichas completas y sus auditorías están en los comentarios del PR #138 citados en cada entrada. Si este resumen no coincide con la ficha, manda la ficha.

Antecedente: [notas del punto 4](NOTAS_TEXTO_COMPLETO_PUNTO4_2026-11-10.md) (2026-11-10). Este registro las amplía y las pone al día.

---

## 1. Resumen por punto del protocolo

| Punto | Qué pregunta el instrumento | Lo más cercano leído | Lo que sigue sin antecedente en lo leído |
|---|---|---|---|
| **1** | Incremento predictivo D fuera de muestra | **W04638:** un estado actual bien medido absorbe el valor de la historia | — |
| **2** | Señal temprana que anticipa confianza, dificultad o geometría | **W05548:** σ de la entrada del softmax cambia bruscamente al inicio (RELACIONADO) | Una señal temprana **evaluada como predictor** |
| **3a** | Kernel de gradientes blanqueado por la Fisher, M = R(F+γI)⁻¹Rᵀ | **W06320** *(auditoría pendiente)*: acoplamiento de dos gradientes por la pseudoinversa de la Fisher en logits | Un **kernel entre ejemplos** con Fisher y ridge |
| **3b** | Pullback G = JᵀMJ | W06320 usa el jacobiano del softmax solo como regla de la cadena (RELACIONADO) | El pullback a un espacio de parámetros de perspectiva |
| **3c** | Longitud de semirrectas al borde del símplex | Nada | Todo |
| **4a** | Calibración y regularización | W05449, W05415 y W05584 (ANTECEDENTE_PARCIAL), W05378 | — |
| **4b** | Concentración, confianza y escala de logits | **W05548: la misma escala del instrumento** (σ = RMS centrada); W05449, el rango | El **vínculo cuantitativo** entre escala y confianza, y la **concentración c** sobre ejemplos |
| **4c** | Modulación de D | Nada (W05548, W05449 y W06320: RELACIONADO o NO_PERTINENTE) | Todo |

---

## 2. La escala de logits en las fuentes leídas (punto 4b)

Escala del instrumento: **s(z) = √((1/m)Σⱼ(zⱼ − z̄)²)**. Es la RMS de los logits centrados entre clases, invariante a sumar una constante a todos los logits y homogénea de grado 1. Identidad: ‖z‖₂² = m·s² + m·z̄².

| Obra | Medida | ¿Centrada o invariante a desplazamiento? | Relación con la confianza en la fuente |
|---|---|---|---|
| W05193 | ‖z/τ‖₂, media sobre pares y semillas | No | Por intervención: la temperatura, con la norma fija, mueve el retraso del *grokking* |
| W05165 | No define una escala; usa la dirección NLM (z → c·z) | No aplica | Mecanismo: tras sobreajustar, la entropía cruzada escala los logits y satura el softmax |
| W05378 | ‖z‖₂ y ‖z‖_ρ | No | Postulada, sin cuantificar |
| W05415 | ‖f‖, norma del vector de logits | No | Postulada («we posit»), sin medir calibración |
| W05584 | ‖p‖₂, normalizada a 1, con temperatura aprendida por muestra û | No | Tomada de LogitNorm, sin medirla ni aislarla con una ablación |
| **W05449** | **Rango R(l) = máx − mín** | **Sí** (invariante y homogéneo de grado 1) | La Prop. 1 separa la norma de la confianza; que el rango sea la causa se postula |
| **W05548** | **σ(x), desviación estándar con divisor n** | **Sí: es exactamente s(z)** cuando x son logits | Verbal, con una sola figura (Fig. 2b): σ baja al inicio corresponde a «baja confianza» |

**Lectura (inferencia nuestra):**
- **El centrado no es exclusivo del instrumento.** W05548 usa la misma escala como temperatura por vector y critica explícitamente la norma sin centrar de LogitNorm. W05449 usa otra medida invariante a desplazamientos.
- **Lo que sigue sin antecedente en lo leído** es lo que el instrumento hace con esa escala: relacionarla cuantitativamente con la confianza, con la concentración c sobre ejemplos y con el incremento D.

---

## 3. Fichas auditadas

### W04638: Hofmann y Mäder (arXiv:2610.09621v1)
- **Fuente:** con 748 rasgos del checkpoint, un **estado actual bien medido absorbe el valor incremental** de la historia del entrenamiento: −21.4 % [−91.9, 8.1], frente a un umbral previo de +10 %. Su métrica es g = 1 − RMSE/RMSE_base.
- **Inferencia:** D = 1 − (1 − g)², válida solo en su estudio principal. Cualquier incremento D de DIN tiene que ganarle a una **base fuerte y calibrada**.
- **Códigos:** 1 ANTECEDENTE_PARCIAL; 2 RELACIONADO; 4c NO_PERTINENTE (con el enunciado completo del punto 4).
- **Ficha v3** (Claude), auditada por Fable y por DeepSeek. PR #138: comentarios 6769762070, 6778732666 y 6778787002.

### W05193: Truong 2026 (arXiv:2606.18465)
- **Fuente:** L = media de ‖z/τ‖₂ en el paso de *grokking*. Por intervención, la temperatura mueve el retraso con la norma fija, y L explica R² = 0.97.
- **Inferencia:** un efecto temporal atribuido a la norma, o a la confianza, puede estar **mediado por la escala de logits**. El instrumento debería controlarla o modelarla como mediadora.
- **Ficha v2** (Claude), auditada por Argon. Comentarios 6772577286 y 6772889888.

### W05165: Prieto et al., ICLR 2025 (arXiv:2501.04697)
- **Fuente:** tras el 100 % de exactitud en entrenamiento, la entropía cruzada empuja a escalar los logits en la dirección NLM, sin cambiar las predicciones. Eso satura el softmax (*Softmax Collapse*).
- **Inferencia:** en la fase tardía, **la confianza puede crecer sin información**. Si DIN usa confianza o escala tardías, parte de la señal podría ser ese escalamiento.
- **Ficha v2** (Claude), auditada por DeepSeek. Comentarios 6773422204 y 6774726792.

### W05378: Zhang y Xie 2024 (arXiv:2412.15301)
- **Fuente:** postulan, sin cuantificar, que la entropía cruzada amplifica la amplitud ‖z‖ y causa sobreconfianza. La calibración divide z por γ‖z‖_ρ + β.
- **Ficha v2** (extraída por Argon), auditada por Claude. Comentario 6773887567.

### W05415: *Typicalness-Aware Learning* (arXiv:2411.01981v2)
- **Fuente:** separa la magnitud de la dirección del logit y ajusta la magnitud con una temperatura dinámica T(τ) según la tipicidad de cada muestra. Que las muestras atípicas causen sobreconfianza se **postula**.
- **Códigos:** 2 RELACIONADO; 4a ANTECEDENTE_PARCIAL; 4b RELACIONADO.
- **Ficha v1** (Fable 5.2), auditada por Qwen3.8-Max con 0 errores. Comentario 6778382239.

### W05449: *Robust Calibration of Large Vision-Language Adapters* (arXiv:2407.13588v1)
- **Fuente:**
  - Prop. 1: un desplazamiento común sube la norma sin cambiar el softmax.
  - Prop. 2: escalar por a > 1 sube a la vez el rango y la confianza.
  - Empíricamente, el rango crece con la miscalibración y la norma baja o no la acompaña.
  - El resumen dice «underlying cause», pero el cuerpo la llama «potential cause».
- **Inferencia:** el rango es invariante a desplazamientos, como s. La diferencia con el instrumento es la norma que se aplica al vector centrado (oscilación frente a RMS).
- **Códigos:** 4a ANTECEDENTE_PARCIAL; 4b ANTECEDENTE_PARCIAL; 4c RELACIONADO.
- **Ficha v2** (extraída por DeepSeek), auditada por Claude. Comentario 6799385177.

### W05548: NormSoftmax (envío anónimo a ICLR 2023; el snapshot registra la versión de IEEE COINS 2023)
- **Fuente:**
  - NormSoftmax(x, γ) = softmax((x − µ(x)1)/min(σ(x), γ)), con σ² = ‖x‖₂²/n − µ².
  - Con γ = ∞ equivale a LogitNorm sobre el vector **centrado**.
  - Critica que LogitNorm no centre («the mean has an impact on the ℓ2 norm»).
  - Lema 1: cota del gradiente proporcional a 1/σ.
  - Fig. 2b: σ salta de 0.14 a 1.31 en la época 15 (ResNet-1202). Que eso explique la dificultad del inicio se **postula**.
- **Inferencia:** σ(x) **es** la escala del instrumento. El artículo no la llama así ni la relaciona cuantitativamente con la confianza, ni con c, ni con D.
- **Limitaciones:** no da semillas ni dispersión; en ResNet-152 queda por debajo del softmax en los cuatro presupuestos.
- **Códigos:** 2 RELACIONADO; 4a RELACIONADO; **4b ANTECEDENTE_PARCIAL**; 4c RELACIONADO.
- **Ficha v2** (Fable 5.2), auditada por Qwen3.8-Max con 0 errores de hecho. Comentario 6803966177.

### W05584: UE-NL (arXiv:2302.07608v1)
- **Fuente:**
  - p̄ = p/‖p‖ (L2 sin centrar).
  - CELoss sobre p̄/û, con û = Σᵢ uᵢεᵢ², una temperatura aprendida por muestra.
  - La relación norma → sobreconfianza se toma de LogitNorm. No hay ablación de la normalización.
- **Inferencia:** es LogitNorm con una temperatura aprendida por muestra. Contrasta con W05449 (rango) sin aportar evidencia propia.
- **Códigos:** 4a ANTECEDENTE_PARCIAL; 4b RELACIONADO.
- **Ficha v2** (extraída por DeepSeek), auditada por Claude. Comentario 6803754855.

---

## 4. Fichas con auditoría pendiente

### W06320: OC-OPD (arXiv:2611.01965v1). Extraída por Fable 5.2; **auditoría de Qwen en curso**
- **Fuente, según la ficha:**
  - **J(q) = diag(q) − qqᵀ**, «the categorical Fisher matrix», con pseudoinversa de Moore–Penrose (p. 5).
  - Teorema 1: g_Rᵀ J(q)⁺ g_F = KL(q‖p) + KL(p‖q).
  - Lema 2: uᵀJ⁺v = uᵀdiag(q)⁻¹v en el espacio tangente.
- **Atributos de la Fisher, según la ficha:**
  - vive en los logits de **una sola posición**;
  - se evalúa en la distribución del alumno;
  - usa **pseudoinversa, sin +γI**;
  - **no forma un kernel entre ejemplos**;
  - no entra en el algoritmo, que usa geometría euclídea.
- **Inferencia del extractor, verificada a mano por Claude:** para gradientes de log-probabilidad, (e_y − q)ᵀJ⁺(e_y′ − q) = δ_yy′/q_y − 1, cuya diagonal **(1 − q_y)/q_y** tiene la misma forma que la aproximación diag((1 − p)/p) del diccionario del instrumento. El artículo no hace ese cálculo.
- **Códigos propuestos:** 3a ANTECEDENTE_PARCIAL (el menos seguro según el extractor); 3b RELACIONADO; 4b RELACIONADO.
- **Homónimos:** en el artículo, M, R, F, D y c son otros objetos.

---

## 4b. Candidatas señaladas solo por su resumen (sin leer)

**Nivel de evidencia: solo título y resumen del snapshot.** Las señaló Claude en las auditorías de cribado y del repaso porque parecían pertinentes para un punto. **No son aportes confirmados.** Esta no es la lista completa de ALTA del corpus: es lo que se marcó en las auditorías citadas. El inventario sistemático por punto queda pendiente (§5).

| Obra | Punto | Por qué se señaló (lectura del resumen) | Estado | Comentario del PR #138 |
|---|---|---|---|---|
| W06354 | 3a y 3b | *Pullback* de la Fisher en estados ocultos de Transformers; espectro de direcciones sensibles y casi nulas | Lista prioritaria | 6779834585 |
| W06335 | 3b y 4b | Sustituye el movimiento RMS por la distancia de Hilbert, una seminorma de oscilación invariante a desplazamientos | Lista prioritaria | 6779834585 |
| W05915 | 3b y 4b | Geometría de la cabeza softmax que respeta la invariancia a desplazamientos comunes | Lista prioritaria | 6778645548 |
| W06200 | 4a y 4b | El autoentrenamiento agudiza las probabilidades sin mejorar la discriminación; la temperatura lo corrige | Lista prioritaria | 6779205680 |
| W06028 | 4a y 4b | Con alta confianza, las brechas entre logits superan la precisión flotante, rompen la suma cero del gradiente e inflan las normas | Lista prioritaria | 6778645548 |
| W06247 | 1 y 4a | ¿Añade una señal información más allá de la confianza softmax, con control de margen? Es el control «ajuste por confianza previa» del protocolo | Incluida MEDIA (corrección) | 6779205680 |
| W00329, W00344 | 2 y 3a | Explosión temprana de la traza de la Fisher | Incluidas ALTA | 6799781607 |
| W00345 | 3a | *Neural Fisher Kernel* | Incluida ALTA | 6799781607 |
| W00102, W00109 | 2 | Cuestionan la validez temprana de GraNd y EL2N | Incluidas ALTA | 6799781607 |
| W06592 | 3a y 4a | Kernel del jacobiano de la red linealizada | Incluida ALTA | 6780064414 |
| W06666 | 2 y 3a | Subespacio tangente tras pocas épocas | Incluida ALTA | 6780064414 |
| W06530, W06684 | 3a | Métrica de Fisher de modelos generativos profundos; información de Fisher ante ejemplos adversariales | Incluidas ALTA | 6780064414 |
| W03612 | 3a | Gauss–Newton para entrenar redes con entropía cruzada, que coincide con la Fisher en logits | Incluida MEDIA (excepción) | 6808699492 |
| W00461 | 3b y 3c | Curvatura de las geometrías α del símplex | Incluida BAJA | 6800913614 |
| W06043 | 3c (conceptual) | Geodésicas en el *manifold* de modelos que llegan a sus bordes (modelos más simples). No es una red ni el símplex bajo G | CONTEXTO BAJA | 6779205680 |
| W01541 | 4b | Descompone MaxLogit en coseno y norma (sin centrar); la norma perjudica el score OOD | Incluida ALTA | 6808273215 |

---

## 4c. Observaciones sobre el propio instrumento

No vienen de la literatura: son derivaciones nuestras, **por verificar o ya verificadas numéricamente**, que surgieron durante la lectura.

1. **Invariancia de M ante reparametrizaciones (Q16, PR #153).**
   - Con θ = g(φ) y B = ∂θ/∂φ invertible, M' = RB(BᵀFB + γI)⁻¹BᵀRᵀ.
   - **M' = M solo si γ = 0 o si B es ortogonal** (permutaciones y signos de neuronas).
   - Un reescalamiento positivo entre capas ReLU conserva la función, pero **cambia M** cuando γ > 0.
   - Verificado numéricamente con matrices aleatorias: diferencia de 0 con γ = 0 y de 0.96 con γ = 0.1.
   - **Pendiente:** comprobar qué activaciones usan las redes de DIN.
2. **Forma (1 − q)/q (a partir de W06320; derivación del extractor, verificada a mano).**
   - Con la Fisher categórica en logits y su pseudoinversa, (e_y − q)ᵀJ(q)⁺(e_y′ − q) = δ_yy′/q_y − 1.
   - La diagonal es (1 − q_y)/q_y, la misma forma que la aproximación diag((1 − p)/p) del diccionario.
   - Es una coincidencia de forma para una posición en el espacio de logits. **No es** el kernel entre ejemplos del instrumento.
3. **Identidad de la escala:** ‖z‖₂² = m·s² + m·z̄². Las medidas sin centrar y la del instrumento se mueven juntas bajo un escalamiento puro y se separan cuando z̄ se desplaza (notas del punto 4, §1).

---

## 5. Pendientes de lectura

De la lista prioritaria (comentario 6802312909): W06354, W06335, W05915, W06200 y W06028.

**Inventario sistemático pendiente:** al cerrar el repaso consolidado conviene que Codex genere, a partir de los paquetes cerrados y de las correcciones, la lista de **todas las INCL ALTA y MEDIA por punto** (1 a 4c). La §4b solo recoge lo señalado en auditorías y no sustituye ese inventario, que servirá para priorizar la lectura de texto completo.

## 6. Balance de extractores (proceso, no resultado)

| Extractor | Obras | Errores de hecho detectados por el auditor |
|---|---|---|
| Fable 5.2 | W05415, W05548 (W06320 pendiente) | 0 y 0 |
| DeepSeek | W05449, W05584 | 1, y 2 de transcripción de ecuaciones por OCR |
| Claude | W04638, W05193, W05165 | 4 (v1) y 2 de página (v2), 0, y 1 más apéndices omitidos |
| Argon | W05378 | 1 |
