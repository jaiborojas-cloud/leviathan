# Q15: registro de aportes de la literatura para RIPG

**Qué es:** un registro vivo de lo que cada obra leída en texto completo **aporta** a las preguntas del instrumento, punto por punto. Se actualiza con cada extracción auditada.

**Qué no es:** **no es una adjudicación de novedad.** La síntesis y la adjudicación se hacen según el §8 del protocolo v3, con todo el corpus. Este registro solo ordena lo leído.

**Reglas del registro:**
1. Cada entrada separa **lo que afirma la fuente** (demostrado, postulado o ilustrado) de la **inferencia** nuestra o del extractor, que va marcada.
2. Solo entran obras con **extracción auditada por otra familia de modelos**. Si alguna tiene la auditoría pendiente, va en una sección aparte y marcada.
3. Ninguna afirmación sale de la memoria de un modelo (precisión del 2026-11-11 en [criterios vigentes](CRITERIOS_VIGENTES_Q15_2026-11-10.md), §8).
4. Las fichas completas y sus auditorías están en los comentarios del PR #138 citados en cada entrada. Si este resumen no coincide con la ficha, manda la ficha.

Antecedente: [notas del punto 4](NOTAS_TEXTO_COMPLETO_PUNTO4_2026-11-10.md) (2026-11-10). Este registro las amplía y las pone al día.

---

## 1. Resumen por punto del protocolo

| Punto | Qué pregunta el instrumento | Lo más cercano leído | Lo que sigue sin antecedente en lo leído |
|---|---|---|---|
| **1** | Incremento predictivo D fuera de muestra | **W04638:** un estado actual bien medido absorbe el valor de la historia | — |
| **2** | Señal temprana que anticipa confianza, dificultad o geometría | **W05548:** σ de la entrada del softmax cambia bruscamente al inicio (RELACIONADO); **W06200:** confianza seguida por rondas de autoentrenamiento, con un contraste de precedencia temporal mayormente indeterminado (RELACIONADO) | Una señal temprana **evaluada como predictor** |
| **3a** | Kernel de gradientes blanqueado por la Fisher, M = R(F+γI)⁻¹Rᵀ | **W06320:** acoplamiento de dos gradientes por la pseudoinversa de la Fisher en logits, en una posición (ANTECEDENTE_PARCIAL) | Un **kernel entre ejemplos** con Fisher y ridge |
| **3b** | Pullback G = JᵀMJ | **W06354:** pullback K_ℓ = J̄ᵀF*J̄ de la Fisher del softmax hacia los estados ocultos, con espectro, rango efectivo y núcleo (ANTECEDENTE_PARCIAL). W06320 usa el jacobiano solo como regla de la cadena (RELACIONADO) | El pullback de una **M entre ejemplos** por el jacobiano de un **campo softmax respecto de una perspectiva** |
| **3c** | Longitud de semirrectas al borde del símplex | Nada (W06354, Ec. 43: energía de Fisher en un segmento finito = KL; RELACIONADO) | Todo |
| **4a** | Calibración y regularización | W05449, W05415, W05584 y **W06200** (ANTECEDENTE_PARCIAL), W05378 | — |
| **4b** | Concentración, confianza y escala de logits | **W05548: la misma escala del instrumento** (σ = RMS centrada); W05449, el rango; **W06335:** vínculo demostrado entre la magnitud de la *perturbación* de los logits (RMS centrada y oscilación) y el cambio de la distribución (ANTECEDENTE_PARCIAL) | El **vínculo cuantitativo** entre escala y confianza, y la **concentración c** sobre ejemplos |
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
| **W06335** | **‖Δz‖₂/√n (RMS) y oscilación max Δz − min Δz**, ambas de la **perturbación** Δz entre dos pasos, no de z | RMS: el centrado es una hipótesis aparte (1ᵀΔz = 0) y no es invariante. Oscilación: **sí es invariante**, homogénea de grado 1 | **Demostrada:** H(softmax(z), softmax(z+Δz)) = osc(Δz); 2·RMS ≤ osc ≤ √(2n)·RMS; sup TV = tanh(osc/4); \|Δℓ\| ≤ osc |
| W06354 | No define una escala; solo centra los logits sobre el vocabulario (P = I − (1/\|V\|)11ᵀ) y usa τ = 2 fija en destilación | Centrado sí, escala no | No relaciona magnitud con confianza; acota el residuo del hessiano por ‖p* − q‖ |

**Lectura (inferencia nuestra):**
- **El centrado no es exclusivo del instrumento.** W05548 usa la misma escala como temperatura por vector y critica explícitamente la norma sin centrar de LogitNorm. W05449 usa otra medida invariante a desplazamientos.
- **W06335 (A.2, con z = 0):** hay logits centrados con RMS → 0 y probabilidad máxima 1/2 cuando n crece. **La RMS centrada no acota por sí sola la concentración de forma uniforme en el número de clases; el rango (oscilación) sí acota la TV y el cambio de pérdida.** Conviene tenerlo presente al interpretar s(z) con muchas clases.
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

### W06320: OC-OPD (arXiv:2611.01965v1)
- **Fuente:**
  - **J(q) = diag(q) − qqᵀ**, «the categorical Fisher matrix», con pseudoinversa de Moore–Penrose (p. 5).
  - Teorema 1: g_Rᵀ J(q)⁺ g_F = KL(q‖p) + KL(p‖q).
  - Lema 2: uᵀJ⁺v = uᵀdiag(q)⁻¹v en el espacio tangente.
- **Atributos de la Fisher, confirmados por el auditor contra el texto:**
  - vive en los logits de **una sola posición**;
  - se evalúa en la distribución del alumno;
  - usa **pseudoinversa, sin +γI**;
  - **no forma un kernel entre ejemplos**;
  - no entra en el algoritmo, que usa geometría euclídea.
- **Inferencia del extractor, verificada por el auditor (sympy y numpy) y a mano por Claude:**
  - (e_y − q)ᵀJ⁺(e_y′ − q) = δ_yy′/q_y − 1, con diagonal **(1 − q_y)/q_y**, la misma forma que la aproximación diag((1 − p)/p) del diccionario;
  - J(q)·diag(q)⁻¹·J(q) = J(q): la Fisher en logits es el pullback de diag(q)⁻¹ por el softmax.
  - El artículo no hace estos cálculos.
- **Códigos:** 3a ANTECEDENTE_PARCIAL (el menos seguro; RELACIONADO también es defendible); 3b RELACIONADO; 4b RELACIONADO.
- **Homónimos:** en el artículo, M, R, F, D y c son otros objetos. El auditor verificó que la ficha no los confunde.
- **Ficha v2** (Fable 5.2), auditada por Qwen3.8-Max con 0 errores de hecho. Comentario 6808812016.

### W06354: *Predictive Geometry of Hidden Trajectories in Transformers* (arXiv:2609.37717v1)
- **Fuente:**
  - **K_ℓ = J̄_ℓᵀ F* J̄_ℓ** (Ec. 5, p. 4), con F* = diag(p*) − p*p*ᵀ.
  - Es un **pullback** desde los logits centrados de la posición objetivo hacia el estado oculto de la capa ℓ (todas las posiciones hasta t). La forma cuadrática es degenerada en ker J̄_ℓ.
  - Teorema 1 (con prueba): en un punto de baja pérdida, el residuo del hessiano está acotado por ‖p* − q‖₂ ≤ √(2ε*) (Ec. 4).
- **Atributos de la Fisher (regla 10), confirmados por el auditor:**
  - vive en logits y **se evalúa en la predicción del propio modelo**, no en el objetivo;
  - **sin inversa, pseudoinversa ni +γI**; la única inversa del artículo es la de un hessiano de parámetros (Ec. 46);
  - **no forma un kernel entre ejemplos**.
- **Pullback (regla 11):**
  - se agrega promediando sobre ejemplos de calibración y posiciones, uno por capa (p. 19);
  - el espectro se mide con Lanczos, rango efectivo por razón de participación con sondas de Hutchinson (Ec. 12), masa de cola (Ec. 13) y trazas por token (Ec. 8–9).
  - El segundo pullback, el del profesor en destilación (Ec. 29 y 45), **no se implementa**: se usa un sustituto sin jacobiano (Ec. 30–32) que el texto reconoce más débil.
- **Escala (regla 9):** no hay ninguna medida de escala de logits; solo centrado y τ = 2 fija.
- **Inferencia del extractor, verificada por el auditor con cálculo:**
  - K_ℓ = (∂p/∂X)ᵀ diag(p*)⁻¹ (∂p/∂X): es el **pullback de la métrica de Fisher del símplex** por el mapa de estados ocultos a probabilidades;
  - F* = F*·diag(p*)⁻¹·F*, la misma identidad que J·diag(q)⁻¹·J = J de W06320;
  - la Ec. 43 (energía de Fisher a lo largo de un segmento en logits) es igual a una KL.
- **Fallas de la fuente, recalculadas por el auditor:**
  - la fila FKL de la Tabla 1 reporta 8 «Wins», pero solo hay 6 diferencias positivas;
  - la media de SkewKL está dominada por un modelo (59.5 baja a 42.6 sin él);
  - faltan 19 de 108 configuraciones;
  - no hay número de semillas ni dispersión, aunque el checklist dice lo contrario.
  - La tensión entre el texto y las Figs. 2 y 3 es lectura aproximada del extractor (NO VERIFICABLE para el auditor).
- **Códigos:** 1 RELACIONADO; 2 NO_PERTINENTE; 3a RELACIONADO (multiplica por F, no blanquea con su inversa); **3b ANTECEDENTE_PARCIAL**; 3c RELACIONADO; 4a NO_PERTINENTE; 4b RELACIONADO; 4c NO_PERTINENTE.
- **Para el instrumento (inferencia nuestra):**
  - Es **el antecedente más cercano a 3b leído**: la forma JᵀAJ con espectro y direcciones nulas ya existe en la literatura de interpretabilidad de Transformers.
  - Lo que lo separa de G(P) = J(P)ᵀ M J(P) es que A es la Fisher de salida de **un ejemplo**, no una matriz M **entre ejemplos**, y que el jacobiano es respecto de estados ocultos, no de un parámetro de perspectiva.
- **Ficha v2** (Fable 5.2; v2 añade el DOI de arXiv del metadato `/DOI`), auditada por Qwen3.8-Max con 0 errores de hecho, 0 CORREGIR y 1 AÑADIR. Comentario 6859713328.

### W06335: *Taming Softmax at the Limits of Muon: A Unified Approach through Hilbert Geometry* (arXiv:2610.17588v1)
- **Fuente (teórica, sin experimentos propios):**
  - Para softmax, la distancia proyectiva de Hilbert entre la distribución antes y después de una actualización es la **oscilación** de la perturbación de los logits: H(softmax(z), softmax(z+Δz)) = max Δz − min Δz (Ec. 3, p. 4). No depende de z.
  - **Demostrado:** 2‖Δz‖_RMS ≤ H ≤ √(2n)‖Δz‖_RMS para Δz centrada (Ec. 15, A.1); sup_z TV = tanh(H/4) (A.2; la cota TV ≤ tanh(H/4) se cita de Cohen & Fausti); \|Δℓ_i\| ≤ H (p. 4).
  - Restringir H ≤ ε se traduce en el LM head en una cota del diámetro de las filas de ΔW (Ec. 5) y en atención en una cota espectral de ΔM (Ec. 12–13). Así se unifican RowNorm y la restricción QK.
- **Reglas 10 y 11:** no hay Fisher ni kernel; Fisher aparece una sola vez, como mención en Related work. No hay jacobiano ni la palabra «pullback». Lo que construye es una medida de tamaño inducida desde la salida hacia ΔW, con la métrica de Hilbert (de tipo máximo, no cuadrática) y agregada por supremo sobre entradas.
- **Inferencia del extractor, verificada por el auditor con cálculo:**
  - a lo largo de un rayo z + s·u, H = s·osc(u), así que **en la métrica de Hilbert el borde del símplex queda a distancia infinita**, a diferencia del ρ_ray finito del instrumento;
  - con z = 0, TV(uniforme, softmax(v)) ≤ tanh(√(2n)·RMS(v)/4).
- **Códigos:** 3b RELACIONADO; **4b ANTECEDENTE_PARCIAL** (el menos seguro; RELACIONADO también es defendible); los demás NO_PERTINENTE.
- **Ficha v1** (Fable 5.2), auditada por Qwen3.8-Max: 0 errores de hecho, 0 CORREGIR, 0 AÑADIR. Comentario 6860962516.

### W05915: *Toward a First-Principles Update Geometry for the Language-Model Head* (arXiv:2608.22253v2)
- **Antecesora de W06335**, con los mismos autores; solo trata la cabeza del modelo de lenguaje. Este PDF no cita W06335.
- **Fuente:**
  - H(softmax(z), softmax(z′)) = ‖z − z′‖_var para **dos vectores de logits cualesquiera** (Ec. 3);
  - sup_{‖h‖≤H} H = H·D(S), con D el diámetro de las filas de la actualización, que no depende de la cabeza actual (Ec. 4);
  - \|ΔL_c\| ≤ H, y ‖Sᵀ(p − e_c)‖ ≤ D(S)(1 − p_c), que es su único vínculo con la probabilidad del objetivo;
  - TV ≤ tanh(H/4), demostrada aquí.
- **Experimentos:** preentrenamiento de 190M a 640M parámetros con 3 semillas por tamaño. RowNorm reduce el diámetro final 45–60 veces y el Hilbert RMS 12–15 veces frente a AdamW, con una pérdida de validación ligeramente mayor. **La comparación cambia la receta completa** (tasa, momento, ϵ y decaimiento de pesos), y el texto lo declara.
- **Regla 9:** no hay RMS de logits. Su «Hilbert RMS» es una RMS sobre posiciones del **rango** de la perturbación. **Reglas 10 y 11:** no hay Fisher, kernel ni jacobiano.
- **Inferencia del extractor:** con z′ = 0, H(p, uniforme) = rango(z), así que el **rango de los logits acota \|L_c − log V\| y TV(p, uniforme)**. Además, D(U) acota el rango de los logits. La fuente no hace ninguna de las dos cosas.
- **Códigos:** 3b RELACIONADO; **4b ANTECEDENTE_PARCIAL**; los demás NO_PERTINENTE.
- **Ficha v1** (Fable 5.2), **aprobada sin auditoría de un segundo modelo** por decisión del responsable (caso por caso, PR #158). Claude cotejó la Tabla 3 contra el texto. Comentario 6865922940.

### W06200: *Temperature, Not Knowledge: What Recursive Self-Training and Its Remedies Do to a Language Model's Confidence* (arXiv:2611.01059v1)
- **Fuente (empírica):** cinco rondas de autoentrenamiento con LoRA sobre Qwen3-1.7B, 3 semillas en 8 protocolos y 1 en otros 11. Se evalúa en 600 ítems de Global-MMLU. La confianza se toma de la opción elegida, con las log-probabilidades de las letras desesgadas por letra sobre los ítems.
- **Resultado central:** la exactitud (0.573 → 0.567) y el AUROC (0.711 → 0.704) casi no cambian, pero la confianza se afila: la deriva confianza − exactitud bajo T0 fijo es +0.049 ± 0.006, y la precisión del quinto más confiado baja de 0.867 a 0.800. «Temperature, not knowledge».
- **Recalibración sin etiquetas:** en cada ronda se elige la temperatura que iguala la entropía predictiva media a la del modelo calibrado de partida. El ECE queda a 0.010 o menos del oráculo con etiquetas, a 1.7B y a 8B (Tabla 4).
- **«Output entropy is not calibration»:** con un brazo de una semilla, mantener plana la entropía de generación deja una deriva de −0.073.
- **Gradiente nulo:** E_{y∼p_θ}[∇ log p_θ(y)] = 0 se argumenta en una línea; el afilamiento se atribuye al truncamiento top-p y a ajustar cada respuesta dos veces.
- **Remedios:** TCE, bono de entropía y un solo pase mantienen la deriva; *focal loss* y dos muestras exactas suben el AUROC a 0.742.
- **Regla 9:** **no da fórmula de la temperatura** ni mide ninguna norma o RMS de logits. Por inferencia del extractor, lo que se reescala son las log-probabilidades desesgadas de las letras. El desesgo es un centrado entre ejemplos por letra, no entre clases. **Reglas 10 y 11:** no hay Fisher, kernel ni jacobiano.
- **Fallas de la fuente (confirmadas por el auditor):**
  - Limitations dice «drifts of 0.02–0.13», pero las tablas llegan a −0.190 y −0.200;
  - hay semillas fuera de la banda \|deriva\| ≤ 0.02 que se usa para decir que un protocolo «se sostiene»;
  - p sin corrección múltiple;
  - brazos clave con una sola semilla.
- **Códigos:** 2 RELACIONADO; **4a ANTECEDENTE_PARCIAL**; 4b RELACIONADO; los demás NO_PERTINENTE.
- **Para el instrumento (inferencia nuestra):**
  - Es **el antecedente empírico más cercano a la separación entre escala y conocimiento del punto 4**: la confianza se mueve como un solo escalar mientras el ordenamiento entre ejemplos casi no cambia.
  - Su «temperatura» es una deriva entre confianza y exactitud sobre letras de opción, **no la escala s(z) de los logits**. No la informa por ronda ni la relaciona con una señal predictiva.
- **Ficha v1** (Fable 5.2), auditada por Qwen3.8-Max (sin intérprete de código): 0 errores de hecho, 0 CORREGIR, 0 AÑADIR. Claude verificó los SHA y los metadatos. Comentario 6866545999.

---

## 4b. Candidatas señaladas solo por su resumen (sin leer)

**Nivel de evidencia: solo título y resumen del snapshot.** Las señaló Claude en las auditorías de cribado y del repaso porque parecían pertinentes para un punto. **No son aportes confirmados.** Esta no es la lista completa de ALTA del corpus: es lo que se marcó en las auditorías citadas. El inventario sistemático por punto está en la §4d.

| Obra | Punto | Por qué se señaló (lectura del resumen) | Estado | Comentario del PR #138 |
|---|---|---|---|---|
| W06354 | 3a y 3b | *Pullback* de la Fisher en estados ocultos de Transformers; espectro de direcciones sensibles y casi nulas | **Leída** (§3): 3b ANTECEDENTE_PARCIAL | 6779834585 |
| W06335 | 3b y 4b | Sustituye el movimiento RMS por la distancia de Hilbert, una seminorma de oscilación invariante a desplazamientos | **Leída** (§3): 4b ANTECEDENTE_PARCIAL | 6779834585 |
| W05915 | 3b y 4b | Geometría de la cabeza softmax que respeta la invariancia a desplazamientos comunes | **Leída** (§3): 4b ANTECEDENTE_PARCIAL | 6778645548 |
| W06200 | 4a y 4b | El autoentrenamiento agudiza las probabilidades sin mejorar la discriminación; la temperatura lo corrige | **Leída** (§3): 4a ANTECEDENTE_PARCIAL, 4b RELACIONADO | 6779205680 |
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

## 4d. Inventario sistemático por punto (cierre del repaso)

**Nivel de evidencia: cribado por título y resumen, no lectura.** Codex lo generó a partir de los paquetes cerrados, con las correcciones y excepciones aplicadas (paquete `Q15_REPASO_GRUPO10_Y_BALANCE_FINAL_R2.zip`, SHA-256 `020fcd01c0d60b6b…`). Lo auditó Claude en el comentario 6859098155 del PR #138. Una obra puede contar en varios puntos.

| Punto | Alcance del repaso: ALTA / MEDIA | Todos los lotes auditados: ALTA / MEDIA |
|---|---|---|
| 1 | 3 / 15 | 3 / 20 |
| 2 | 120 / 64 | 130 / 69 |
| 3a | 122 / 154 | 153 / 163 |
| 3b | 50 / 57 | 60 / 57 |
| 3c | 7 / 8 | 7 / 8 |
| 4a | 207 / 549 | 236 / 705 |
| 4b | 60 / 0 | 66 / 0 |
| **4c** | **0 / 0** | **0 / 0** |
| Obras únicas | 1,082 | 1,309 |

- **4c (modulación de D) no tiene ninguna obra en ALTA o MEDIA, y 4b no tiene ninguna en MEDIA.** 3c tiene 15. Son los puntos con menos antecedentes visibles en el cribado, lo que no prueba que no existan: el cribado solo ve resúmenes.
- **Balance final del repaso** (2,633 pares, 2,632 obras): INCL pasa de 1,629 a 1,576, CONTEXTO de 178 a 235 y EXCL de 804 a 800. Siguen 21 PENDIENTE_ACCESO y 1 PENDIENTE_VERIFICACION. Hubo 116 cambios de decisión.
- **12 obras de L29** (NC/ETF) quedan en INCLUIR BAJA con el punto `SIN_PUNTO (NC/ETF; antes 3c)`, por decisión del responsable.
- **Uso:** estas listas son la base para priorizar el texto completo; la §4b queda como registro de lo señalado en auditorías.

### Lo que dejó la pasada del repaso

**Nivel de evidencia: cribado de título y resumen.** Son cuentas de Claude sobre `REPASO_CONSOLIDADO_2633.csv` (R2 más la corrección `SIN_PUNTO`, SHA `01c4ea1e…`), no lecturas.

**1. Cambios de decisión (116).**

| De → a | Obras |
|---|---|
| INCLUIR → CONTEXTO | 42 |
| INCLUIR → EXCLUIR | 32 |
| EXCLUIR → INCLUIR | 21 |
| EXCLUIR → CONTEXTO | 18 |
| CONTEXTO → EXCLUIR | 3 |

La pasada no solo recortó: también recuperó 21 obras excluidas, sobre todo por la rúbrica R3a, porque la Fisher estudiada como objeto se incluye.

**2. Movimiento por punto**, contando cada etiqueta que una obra incluida gana o pierde en las filas con CAMBIO:

| Punto | Gana | Pierde | Motivo principal |
|---|---|---|---|
| 1 | 3 | 0 | |
| 2 | 32 | 38 | R2 (señal temprana como objeto) y D1 (validez de la dificultad por ejemplo en BAJA) |
| 3a | **68** | 6 | R3a: Fisher, Gauss–Newton o NTK como objeto de estudio |
| 3b | **43** | 0 | Pullbacks y métricas de salida reconocidos al aplicar R3a |
| 3c | 1 | **16** | Se retira 3c a NC/ETF y a otras geometrías que no son semirrectas al borde del símplex |
| 4a | 27 | **57** | D2 (generalización o robustez sin calibración) y D4 (OOD por rasgos o distancia) |
| 4b | 1 | 0 | |
| 4c | 0 | 0 | |

En cercanía de las obras que siguieron incluidas, 61 bajaron de MEDIA a BAJA y 55 de ALTA a MEDIA; solo 13 subieron de MEDIA a ALTA. Las 99 que tenían cercanía NO_REGISTRADA en L01–L04 quedaron con una asignada.

**3. Patrones de criterio que fijó la pasada**, útiles para leer:
- **Neural collapse y ETF no son 3c.** El «símplex» de rasgos no es el de probabilidades, y la geometría de medias de clase no es una longitud bajo G. Las 12 obras de L29 quedan con el punto `SIN_PUNTO`.
- **La dificultad usada como insumo**, por ejemplo *focal loss* (W05230), queda excluida por D3.3.
- **La capacidad de memoria sin una señal** (W05183 y W05184) queda en CONTEXTO por D3.1.
- **La Fisher como herramienta numérica o aproximación** (W04628 y W05702) baja a CONTEXTO o a BAJA.
- **Excepciones individuales registradas:** W01141 (INCLUIR BAJA 4a) y W03612 (Gauss–Newton con entropía cruzada, INCLUIR MEDIA 3a).

**4. Las 15 obras de 3c en ALTA o MEDIA no se reexaminaron como 3c.** El alcance del repaso eran D1–D4, R2, R3a y las observaciones de auditoría, así que su etiqueta 3c se conservó «sin reabrir»; Codex lo anota en la razón de casi todas.
- **ALTA (7):** W00557, W00644, W00707, W00759, W00832, W02870 y W04614. Son ALTA por 3a: geometría de Fisher de redes, singularidades y gradiente natural.
- **MEDIA (8):** W00582, W00655, W00940, W00964, W04647, W04713, W04756 y W05287.
- **Por el resumen**, ninguna menciona semirrectas, el borde del símplex de probabilidades o una cota d_borde ≤ ρ_ray. Hablan de geodésicas en otros espacios: ataques, gradiente natural, Fisher–Rao de tipos atómicos, cocientes riemannianos o el ángulo cerca del borde en OOD.
- **Posible duplicado:** W00582 (arXiv:1803.01273) y W00940 (PMLR v80) tienen el mismo título, *Accelerating Natural Gradient with Higher-Order Invariance*. Parecen versiones de una misma obra. Se señala para la síntesis, sin fusionarlas aquí.
- **Implicación para la lectura:** el 3c del instrumento probablemente tiene **todavía menos antecedente directo** de lo que sugieren las 15. Leer primero las ALTA, con atención a si alguna integra una longitud de curva hasta un borde.

---

## 4c. Observaciones sobre el propio instrumento

No vienen de la literatura: son derivaciones nuestras, **por verificar o ya verificadas numéricamente**, que surgieron durante la lectura.

1. **Invariancia de M ante reparametrizaciones (Q16, PR #153).**
   - Con θ = g(φ) y B = ∂θ/∂φ invertible, M' = RB(BᵀFB + γI)⁻¹BᵀRᵀ.
   - **M' = M solo si γ = 0 o si B es ortogonal** (permutaciones y signos de neuronas).
   - Un reescalamiento positivo entre capas ReLU conserva la función, pero **cambia M** cuando γ > 0.
   - Verificado numéricamente con matrices aleatorias: diferencia de 0 con γ = 0 y de 0.96 con γ = 0.1.
   - **Pendiente:** comprobar qué activaciones usan las redes de DIN.
2. **Forma (1 − q)/q (a partir de W06320; derivación del extractor, verificada por el auditor y a mano).**
   - Con la Fisher categórica en logits y su pseudoinversa, (e_y − q)ᵀJ(q)⁺(e_y′ − q) = δ_yy′/q_y − 1.
   - La diagonal es (1 − q_y)/q_y, la misma forma que la aproximación diag((1 − p)/p) del diccionario.
   - Es una coincidencia de forma para una posición en el espacio de logits. **No es** el kernel entre ejemplos del instrumento.
3. **Identidad de la escala:** ‖z‖₂² = m·s² + m·z̄². Las medidas sin centrar y la del instrumento se mueven juntas bajo un escalamiento puro y se separan cuando z̄ se desplaza (notas del punto 4, §1).

---

## 5. Pendientes de lectura

De la lista prioritaria (comentario 6802312909): W06028. W06354, W06335, W05915 y W06200 ya se leyeron (§3).

**Inventario sistemático:** hecho (§4d). La siguiente prioridad de lectura sale de esas listas, empezando por 3c (15 obras) y 3b (117 en todos los lotes).

## 6. Balance de extractores (proceso, no resultado)

| Extractor | Obras | Errores de hecho detectados por el auditor |
|---|---|---|
| Fable 5.2 | W05415, W05548, W06320, W06354, W06335, W06200 (W05915 sin segundo auditor) | 0, 0, 0, 0, 0 y 0 |
| DeepSeek | W05449, W05584 | 1, y 2 de transcripción de ecuaciones por OCR |
| Claude | W04638, W05193, W05165 | 4 (v1) y 2 de página (v2), 0, y 1 más apéndices omitidos |
| Argon | W05378 | 1 |
