# Revisión de literatura Q15: ¿qué es nuevo en la línea DIN? (primera pasada, 2026-10-28)

**Por qué ahora:** cerrar Q13-M2 era uno de los hitos que hacían obligatoria esta revisión (ver [preguntas abiertas](open-questions.md)). Lo pidió el responsable el 2026-10-28 a las 20:10.

**Alcance honesto:** es una **revisión dirigida, no sistemática**.
- **Cómo se hizo:** búsquedas web en torno a cinco temas, más la lectura del resumen de las fuentes clave.
- **Etiqueta de verificación de cada referencia:**
  - **[leído]:** se leyó el resumen o la página del artículo en esta revisión.
  - **[título]:** solo se confirmó el título y la existencia; lo que se dice de su contenido viene de conocimiento previo y hay que leerlo antes de citarlo fuera.
- **Antes de publicar** falta una búsqueda sistemática (bases, términos y criterios fijados de antemano) y la lectura completa de las fuentes marcadas como «leer antes de publicar».

## 1. ¿La métrica D es nueva? **No.**
- **Qué es D:** D = 1 − SSE_completo/SSE_base, calculado fuera de muestra. Es el **R² fuera de muestra** (Campbell y Thompson 2008, para predicción de retornos) [leído: definición en [macroforecast](https://macroforecast.readthedocs.io/en/stable/encyclopedia/l5/relative_metrics/r2_oos.html)]. En estadística es una forma de **ΔR² con validación cruzada** o de «validez incremental».
- **Qué es nuestro:**
  - el **objeto** al que se aplica: la confianza temprana X10 como predictor de la distancia final al borde, ρ_borde(250), de la geometría perspectival, por encima de ρ_borde(10);
  - el **protocolo**: centrado en el split, bloques de splits y permutación dentro del split.
- **Cómo hay que decirlo:** «usamos el R² incremental fuera de muestra (Campbell y Thompson 2008)». Nunca «proponemos la métrica D».

## 2. ¿Alguien mostró que una medida temprana predice el colapso o la geometría final?
Hay una literatura amplia sobre «lo temprano anticipa lo final», pero **no se encontró el resultado DIN**.

| trabajo | qué muestra | relación con DIN |
|---|---|---|
| Toneva et al. 2019, *Example Forgetting* (ICLR) [leído] | los ejemplos «inolvidables» se identifican temprano; el orden emerge hacia la época 25 y se estabiliza hacia la 75 | lo temprano anticipa el **destino de cada ejemplo**. No hay métrica ni borde |
| Paul, Ganguli, Dziugaite 2021, *Deep Learning on a Data Diet* (NeurIPS) [título] | puntajes por ejemplo (EL2N, GraNd) calculados pocas épocas después de empezar identifican los ejemplos importantes | misma intuición, por ejemplo y no geométrica. **Leer antes de publicar** |
| Swayamdipta et al. 2020, *Dataset Cartography* (EMNLP) [título] | la confianza y su variabilidad a lo largo del entrenamiento separan ejemplos fáciles, difíciles y ambiguos | usa la confianza como X10, pero sin predecir una geometría final. **Leer antes de publicar** |
| Baldock, Maennel, Neyshabur 2021, *Example Difficulty* (NeurIPS) [leído] | la «profundidad de predicción» sigue la incertidumbre, la confianza y la velocidad de aprendizaje de cada ejemplo | dificultad por ejemplo; sin métrica de Fisher |
| Jastrzębski et al. 2021, *Catastrophic Fisher Explosion* (ICML) [leído] | un Tr(F) temprano grande va con peor generalización final, entre tasas de aprendizaje y tamaños de lote; penalizarlo desde el inicio mejora la generalización | **el más cercano a D9**: Fisher temprana → generalización. Ellos comparan **entre configuraciones**; D9 miró **dentro del split** y no encontró nada. Es compatible: la variación que ellos explotan no es la que D9 midió |
| Jastrzębski et al. 2020, *Break-Even Point* (ICLR) [título] | la fase temprana fija la curvatura que alcanza el entrenamiento | dinámica temprana de la curvatura. **Leer antes de publicar** |
| Achille, Rovere, Soatto 2019, *Critical Learning Periods* (ICLR) [título] | hay períodos críticos tempranos, con la información de Fisher como herramienta | Fisher temprana; no predice el borde |
| Nguyen et al. 2026, *Early Training Telemetry* (arXiv 2608.03709) [leído] | métricas de las primeras épocas predicen la precisión final de test entre 23 788 corridas | predicción temprana **entre corridas** con aprendizaje automático, sin geometría |

**Hasta donde se encontró:**
- no hay trabajos que relacionen la **confianza en el ejemplo más difícil del panel**, en el update 10, con la **distancia final al borde de una métrica perspectival**;
- ni que muestren que esa señal se **modula con el colapso** de la métrica sobre un ejemplo.

## 3. ¿Qué se sabe de las intervenciones (LS, penalización de logits, WD)?
**Este punto cambia cómo se lee Q13-M2.**
- **Müller, Kornblith, Hinton 2019,** *When Does Label Smoothing Help?* [leído]: LS agrupa las representaciones de cada clase y quita a los logits la información sobre el parecido entre clases. Es coherente con que LS reduzca el colapso de M sobre un ejemplo.
- **Beck, Bar-Sinai, Levi** (arXiv 2602.12039), *The Implicit Bias of Logit Regularization* [leído]:
  - **LS y las penalizaciones de logits pertenecen a la misma familia** de regularización convexa de logits: cada ejemplo recibe un logit objetivo finito, en lugar de márgenes que crecen sin límite;
  - **WD es distinto**, porque acopla a todos los ejemplos a través de la norma global de los pesos y no se descompone por ejemplo.
  - **Consecuencia para nosotros:** LS y LP **comparten mecanismo**, así que **WD es la triangulación realmente independiente** de Q13-M2. Que WD module con una pendiente compatible (0.056) es la parte más informativa del resultado. La lectura «tres intervenciones» debería precisarse: **dos familias de mecanismo**, la regularización por ejemplo de logits (LS y LP) y el encogimiento global de pesos (WD).
- **Wei et al. 2022,** *LogitNorm* (ICML) [título]: normalizar los logits reduce la sobreconfianza. Es otra intervención de la misma familia que LP.
- **Zhou et al. 2022,** *Are All Losses Created Equal: A Neural Collapse Perspective* (arXiv 2210.02192) [leído]: LS y la pérdida focal también llegan al *neural collapse*.
  - El *neural collapse* (Papyan, Han, Donoho 2020) [título] **no es** nuestro colapso de M: el suyo es de las medias de clase en las representaciones; el nuestro es la concentración de la métrica perspectival en un ejemplo del panel.
  - **Hay que decirlo explícitamente** al escribir, para evitar la confusión de nombres. Lo prudente sería **renombrar el nuestro** («concentración de M» o «colapso perspectival»).

## 4. Fisher por ejemplo y ejemplos difíciles
- **Bernstein et al. 2026** (arXiv 2610.16161) [leído]: la Fisher del modelo **final** localiza la memorización en direcciones particulares de los pesos (ResNet-20 sobre CIFAR-10). No miran lo temprano ni la distancia al borde. **Puente abierto** (ya registrado en la Q15): ¿el ejemplo sobre el que se concentra M vive en esas direcciones?
- **Jastrzębski et al. 2021** (arriba): su penalización de Fisher frena el aprendizaje de ejemplos con etiquetas ruidosas. Es otra conexión entre la Fisher y los ejemplos difíciles.
- **Simplex y borde:** hay trabajos sobre la geometría de la salida softmax y su saturación (por ejemplo, arXiv 2502.00456) [título]. No se encontró una medida equivalente a ρ_borde, la distancia geodésica al borde bajo la métrica perspectival.

## 5. ¿Es general?
- **Lo que hay:** evidencia propia en dos familias pequeñas (MLP en Wine y mezclas gaussianas), con un caso negativo (Iris, G1).
- **La literatura relacionada usa redes y datos mucho mayores:** CIFAR, ResNet y modelos de lenguaje.
- **Brecha principal:** probar la señal y su modulación en arquitecturas y datos estándar antes de cualquier afirmación general.

## 6. Qué se puede decir y qué no
| afirmación | ¿se puede? |
|---|---|
| «Proponemos la métrica D» | **No.** Es el R² incremental fuera de muestra |
| «Lo temprano predice lo final» como idea general | **No es nuevo**; citar a Toneva, Paul, Swayamdipta, Jastrzębski y Nguyen |
| «La confianza temprana en el ejemplo más difícil predice la distancia final al borde de la geometría perspectival, fuera de muestra, en dos familias, y esa señal se modula con la concentración de M bajo dos familias de intervención» | **Sí, como resultado propio**, con el alcance declarado y tras la búsqueda sistemática |
| «Es el primero» o «nunca se había mostrado» | **No todavía.** Falta la revisión sistemática |
| «El colapso causa la señal» | **No.** Las intervenciones lo mueven, pero también la escala de los logits |

## 7. Implicaciones para el plan
1. **Reformular A31 y la portada:** decir «tres intervenciones de **dos familias de mecanismo**» (Beck et al.).
2. **Renombrar el «colapso de M»** en los textos externos, o distinguirlo explícitamente del *neural collapse*.
3. **Nuevo control posible:** la escala de los logits como variable rival del colapso. Beck et al. indican que LS y LP fijan logits objetivo finitos. Un diseño que mueva el colapso **sin** mover la escala de los logits, o al revés, separaría las dos.
4. **Transferencia:** CIFAR con una ResNet pequeña es el terreno de la literatura relacionada (Bernstein, Jastrzębski, Paul), y por eso el paso natural.
5. **Antes de publicar:**
   - búsqueda sistemática, con términos, bases y criterios fijados;
   - lectura completa de los marcados [título];
   - revisar Jastrzębski 2021 a fondo, porque es el más cercano a D9.

## Fuentes
- [Campbell–Thompson R²_OS, definición](https://macroforecast.readthedocs.io/en/stable/encyclopedia/l5/relative_metrics/r2_oos.html)
- [Toneva et al. 2019](https://arxiv.org/pdf/1812.05159)
- [Paul, Ganguli, Dziugaite 2021](https://arxiv.org/abs/2107.07075v2)
- [Swayamdipta et al. 2020](https://aclanthology.org/2020.emnlp-main.746)
- [Baldock et al. 2021](https://proceedings.neurips.cc/paper/2021/hash/5a4b25aaed25c2ee1b74de72dc03c14e-Abstract.html)
- [Jastrzębski et al. 2021, Catastrophic Fisher Explosion](https://arxiv.org/html/2012.14193v3)
- [Jastrzębski et al. 2020, Break-Even Point](https://www.emergentmind.com/papers/2002.09572)
- [Achille et al. 2019](https://arxiv.org/abs/1711.08856v3)
- [Nguyen et al. 2026](https://pith.science/paper/2608.03709)
- [Müller et al. 2019](https://arxiv.org/abs/1906.02629v2)
- [Beck, Bar-Sinai, Levi, Logit Regularization](https://arxiv.org/html/2602.12039v2)
- [Wei et al. 2022, LogitNorm](https://proceedings.mlr.press/v162/wei22d.html)
- [Zhou et al. 2022](https://arxiv.org/abs/2210.02192)
- [Papyan, Han, Donoho 2020](https://arxiv.org/abs/2008.08186)
- [Bernstein et al. 2026](https://arxiv.org/html/2610.16161)
- [Explorations of the Softmax Space](https://arxiv.org/html/2502.00456v1)
