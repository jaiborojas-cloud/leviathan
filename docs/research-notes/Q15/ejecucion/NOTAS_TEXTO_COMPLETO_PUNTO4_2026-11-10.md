# Q15: notas de lectura de texto completo para RIPG (2026-11-10)

**Naturaleza:** son **notas de trabajo** de las lecturas anticipadas de la lista prioritaria (PR #138, comentario 6773265006). **No adjudican novedad**: la síntesis y la adjudicación se hacen según el §8 del protocolo, después del cribado y del repaso consolidado. Este documento separa lo que **afirma cada fuente** de lo que es **inferencia** de Claude, y lo pidió el responsable para tener registrado lo encontrado.

## 1. La escala del instrumento (protocolo v3, §1.1)

- **Escala de logits:** la **raíz media cuadrática de los logits centrados entre clases**,

  s(z) = √( (1/m) Σ_j (z_j − z̄)² ),  con z̄ = (1/m) Σ_j z_j.

- **Propiedades:**
  - Es **invariante a sumar una constante a todos los logits** (z_j → z_j + a), igual que el softmax.
  - Escala de forma lineal: s(c·z) = c·s(z).
  - La temperatura modifica la confianza y las cantidades que el instrumento recalcula.
- **Concentración del instrumento:** c = max_n M_nn / tr M, con M = R(F + γI)⁻¹Rᵀ. Es una concentración **sobre ejemplos**, no sobre clases.
  - No es tr F.
  - No es el rango efectivo.
  - No es el *neural collapse*.

**Relación con la norma sin centrar** (identidad exacta):

‖z‖₂² = m·s(z)² + m·z̄²

Las medidas sin centrar mezclan dos cosas:
- la **dispersión entre clases**, s, que es lo que cambia el softmax;
- el **desplazamiento común**, z̄, al que el softmax es indiferente.

Bajo un escalamiento puro z → c·z, como la NLM de Prieto et al., las dos crecen en proporción y las medidas se mueven juntas. Se separan cuando z̄ cambia por su cuenta, por ejemplo por los sesgos de la última capa o por un desplazamiento común de los logits.

## 2. Qué mide cada fuente leída (o vista en el resumen)

| Obra | Estado | Su medida de «escala» o «magnitud» | ¿Centrada? | Relación con la confianza |
|---|---|---|---|---|
| **W05193**, Truong 2026 (arXiv:2606.18465) | Leída; extracción v2 auditada por Argon | L = media sobre pares y semillas de ‖z/τ‖₂, leída **en el paso de grokking** | **No** | Por intervención: la temperatura, con la norma fija, mueve el retraso del grokking; L explica R² = 0.97. Mide la saturación por la tasa de colapso del softmax, no la confianza |
| **W05165**, Prieto et al., ICLR 2025 (arXiv:2501.04697) | Leída; extracción v2 auditada por DeepSeek | No define una escala. Usa la dirección NLM, que lleva z a c·z sin cambiar predicciones, y la fracción de Softmax Collapse | No aplica | Mecanismo: tras el 100 % de entrenamiento, la entropía cruzada empuja a escalar los logits, lo que satura el softmax y detiene el aprendizaje |
| **W05378**, Zhang y Xie 2024 (arXiv:2412.15301) | Leída por Argon; extracción v2 auditada por Claude | Amplitud ‖z‖₂ por muestra, su media (1/(Nm))Σ‖z‖₂ y la norma ‖z‖_ρ, sin valor absoluto | **No** | **Postulan**, sin cuantificar, que la entropía cruzada amplifica la amplitud y causa sobreconfianza. La calibración divide z por γ‖z‖_ρ + β |
| **W05415**, *Typicalness-Aware Learning* (arXiv:2411.01981v2) | Leída por Fable 5.2; extracción v1 auditada por Qwen3.8-Max, 0 errores | ‖f‖, la norma del vector de logits por muestra, sin declarar el tipo de norma; no la mide en ningún experimento | **No** | **Postulan** («we posit»), sin medir calibración, que las muestras atípicas causan sobreconfianza; fijan la magnitud con una temperatura dinámica T(τ) |
| W05449, *Robust Calibration of Large VL Adapters* | Solo resumen; en la lista prioritaria | «Rango» de los logits | Por ver | El aumento del rango degrada la calibración, y reescalar la corrige |

## 3. Lo que encontramos para RIPG (inferencia, no adjudicación)

1. **Base fuerte (W04638, punto 1).** Hofmann y Mäder muestran que un **estado actual bien medido**, con 748 rasgos del checkpoint, puede absorber el valor incremental de la historia del entrenamiento: −21.4 % frente a un umbral previo de +10 %. Para DIN, cualquier incremento D tendría que ganarle a una base **fuerte y calibrada**, no a una débil. Su métrica, g = 1 − RMSE/RMSE_base, se relaciona con D por D = 1 − (1 − g)², solo en su estudio principal.
2. **La escala de logits como mediadora (W05193).** Bajo entropía cruzada, un efecto temporal que se atribuya a la norma, y quizá a la confianza, **puede estar mediado por la escala de logits**. Conviene que el instrumento la **controle o la modele como mediadora**.
3. **Confianza que crece sin información (W05165).** En la fase posterior al sobreajuste, la confianza puede crecer por un escalamiento que **no cambia las predicciones**. Si DIN usa confianza o escala **tardías**, parte de la señal podría ser ese escalamiento «ingenuo».
4. **Centrado como diferencia operativa (W05193, W05378, W05415 y posiblemente W05449).** Las fuentes leídas miden la magnitud **sin centrar** (‖z‖₂, ‖z‖_ρ, ‖f‖). El instrumento usa la **RMS centrada**. Por la identidad del §1, coinciden en proporción bajo escalamiento puro y difieren cuando z̄ se mueve por su cuenta. **Hay que verificar en la síntesis** si alguna fuente usa una escala centrada (u otra invariante a desplazamiento común) antes de tratar esto como diferencia.
5. **Geometría.** Ninguna de las cinco obras usa la Fisher, el kernel blanqueado M, el pullback G ni la concentración c sobre ejemplos. Los puntos 3a–3c y la c del punto 4b siguen sin antecedente directo **en estas lecturas**. No es una conclusión de ausencia: falta el resto del corpus.

## 4. Pendientes ligados a estas notas

- **Auditoría de la extracción de W05165:** hecha por DeepSeek; quedó la v2 (PR #138, comentario 6774726792).
- **Lectura de W05415:** hecha (comentario 6778382239). **Pendientes:** W05449, W06028 y W05915 (comentario 6778677896).
- **Verificar** si en el corpus hay escalas centradas o invariantes a desplazamiento (punto 4 del §3). **Candidatas del cribado** (solo por el resumen, sin leer): W05915, que deriva una geometría de la cabeza softmax invariante a desplazamientos comunes, y W06335, que sustituye el movimiento RMS por la distancia de Hilbert, una seminorma de oscilación invariante a desplazamientos (comentarios 6778645548 y 6779834585).
