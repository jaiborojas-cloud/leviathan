# DIN-C1 — confirmatorio de la señal temprana, BORRADOR v2 (2026-10-25)

**Estado:** borrador **listo para congelar**, pendiente de la aprobación del responsable. Sustituye al v1, que se conserva. El cambio de primaria lo aprobó el responsable el 2026-10-25 a las 10:34 («lo apruebo»), a partir de la revisión de DIN-D2b (PR #74).

## 1. Qué cambia respecto del v1 y por qué
D2b mostró con un contraejemplo que la primaria del v1 (residuo lineal de Y sobre L seguido de Spearman) puede dar W_adj > 0 **aunque X sea función exacta de L**. Por eso no identifica información «más allá de ρ(10)». La v2 cambia el estimando:
- **Primaria:** **incremento predictivo fuera de muestra** de X sobre un modelo base flexible de L.
- **La W_adj del v1** pasa a secundaria, con su afirmación acotada a ese estimando.
- **X** se calcula desde los logits con logsumexp, sin saturación en p = 1.
- **Empates:** rangos promedio. Un split sin variación sale del W y se cuenta.
- **Auditoría de precisión** de ρ(10) y cota de cuerda.

## 2. Pregunta (sin cambios)
En WineMLP con panel de validación de 27 ejemplos, ¿la incertidumbre del modelo sobre su ejemplo de validación más difícil en el update 10 **mejora la predicción** de log ρ_borde(250), dentro del split, respecto de lo que predice ρ_borde(10) por sí solo, modelado de forma flexible?

## 3. Cohorte (sin cambios respecto del v1)
- **Muestra:** splits 168–323, con 5 inicializaciones por split (780 trayectorias) y la regla de semillas de T2-A0 extendida.
- **Entrenamiento:** de cero hasta el update 250, con `c1_cohorte.py` v2.
- **Compuerta de reproducción numérica:**
  - en el update 5, |Δθ| ≤ 10⁻¹² con el RNG de numpy idéntico;
  - en el update 50, la diferencia relativa de M ≤ 10⁻¹⁰.
  Pasó con la v1 (5/5 y 5/5) y **se repite con la v2** antes de la cohorte.

## 4. Variables
- **X:** max_n [logsumexp_{c ≠ y_n} z_n,c − logsumexp_c z_n,c] en el update 10, es decir, log(1 − p_min).
- **L:** log ρ_borde(10).
- **Y:** log ρ_borde(250).
- **ρ_borde:** `rho_borde.py` congelado (`d8ec69f8…`).

## 5. Análisis (`C1/analisis_C1_v1.py`)
- **Primaria D:**
  - Todo se centra dentro del split. z = (L − media)/de en la cohorte.
  - **Base:** Yc ~ [z, z², z³]c. **Completo:** base + Xc, con pendiente común.
  - **Validación cruzada:** 10 bloques de splits, asignados con default_rng(260010).
  - **Estadístico:** D = 1 − SSE_completo/SSE_base fuera de muestra.
  - **Nulo:** se permuta X dentro del split, 5000 veces (semilla 260001), recalculando D completo.
  - **PASS si p < 0.05 y la pendiente de X es > 0** (sentido fijado en el descubrimiento). NOT_MET si los datos son válidos y no se cumple.
- **INCONCLUSIVE:**
  - la compuerta no pasa;
  - menos del 80 % de los splits tienen al menos 3 trayectorias completas;
  - más del 5 % de las trayectorias tienen faltantes;
  - o X no tiene variación.
- **Secundarios** (no deciden):
  - W_adj lineal-rangos (definición v1; afirmación acotada; semilla 260002, 20 000 permutaciones);
  - W_adj con ajuste flexible por rangos (260003);
  - secundaria A: W de log ρ(30) frente a Y (260004);
  - D con base de grado 5 (260005);
  - auditoría de precisión de ρ(10): 40 trayectorias preseleccionadas con semilla 270001, 5760 direcciones y orden 1600;
  - violaciones de la cota de cuerda en el update 10.

## 6. Pruebas antes de congelar (contenedor; tabla de descubrimiento, splits 12–167)
| prueba | resultado |
|---|---|
| **Descubrimiento** (500 permutaciones) | D = 0.078, p = 0.002, pendiente 1.16; W_adj lineal 0.218 (coincide con D6); flexible 0.225; D con grado 5 = 0.074 |
| Control: X = L | D = 0.000, NOT_MET |
| Control: X = función cúbica de L | D = 0.000, NOT_MET |
| Control: Y = g(L) no lineal, X afín a L (estilo D2b) | D = 0.000, NOT_MET (la W_adj lineal da −0.07) |
| Control: X constante | INCONCLUSIVE (no identificable) |
| Control: L medido con error, X = L latente | **PASS** (D ≈ 0.58), como se esperaba: **limitación declarada** (sección 7) |
| Control: incremento real (r = 0.3) | PASS (D ≈ 0.09–0.10) |
| **Calibración nula** (96 X de ruido, 400 permutaciones) | PASS en 4.2 % (con la regla de la pendiente > 0) |
| **Potencia** (32 semillas, 400 permutaciones) | r = 0.10 → 0.69; **r = 0.15 → 1.00**; r = 0.20 → 1.00 |

r es la correlación de X con el residuo intra-split de Y sobre la base cúbica.

## 7. Qué no se afirma
- **Un PASS es predictivo, no causal:** X mejora la predicción de ρ(250) respecto de ρ(10) **observado**. Si ρ(10) fuera una medida ruidosa de la variable que de verdad mueve el desenlace, X podría ganar por medirla mejor (control «L con error»). La auditoría de precisión acota el ruido numérico de ρ, pero no el «ruido conceptual».
- **Familia única:** WineMLP, datos Wine, panel de 27. No hay transferencia.
- **Selección previa:** la primaria se eligió en D6 entre 18 combinaciones; la cohorte nueva es independiente de esa selección.

## 8. Pendiente para congelar
1. Repetir la compuerta con `c1_cohorte.py` v2.
2. Aprobación del responsable. Al congelar se publican los SHA de este diseño, de `c1_cohorte.py` v2 y de `analisis_C1_v1.py`.
