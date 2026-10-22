# NEM3 — Diseño congelado

Este documento se congela antes de escribir código ni generar resultados. No se modifican los umbrales, métricas, tolerancias, semillas ni radios después de observar resultados.

## 1. Objetivo

Medir sobre el espacio de perspectivas:
1. La energía curvatural $\mathcal E_K = \frac{1}{A} \int_{D_A} K^2\, dA$ y $C_A = \sqrt{\mathcal E_K}$.
2. La concentración espacial $\Lambda_q = \frac{1}{E} \sup_{U \subseteq D_A,\, \operatorname{Area}(U) = qA} \int_U e\, dA$ con $e = K^2$, para $q \in \{0.25, 0.5, 0.75\}$.
3. La participación efectiva espacial $R_{\text{eff}} = \frac{(\int_{D_A} K^2\, dA)^2}{A \int_{D_A} K^4\, dA}$.
4. Cómo varían estos observables ante una perturbación del panel de evaluación $\mu$ (extensión de NEM1).

## 2. Familia de perspectivas

Familia no lineal (softmax de rasgos fijos, forma E12):

$$
a_n(p) = \frac{e^{p^T f_n}}{\sum_r e^{p^T f_r}}, \qquad
S_p(\theta) = \sum_n a_n(p) \log p_\theta(y_n|x_n)
$$

$$
B_{ai} = \sum_n a_n (f_{na} - \mu_a) (r_n)_i, \qquad
h(p) = B(p) \, C \, B(p)^T
$$

con $m=2$ perspectivas, $C$ identidad, dominio $p = (p^1, p^2) \in [-1, 1]^2$.

## 3. Elemento de área y energía curvatural

El elemento de área de la métrica $h$ es $dA = \sqrt{\det h}\, dp^1 dp^2$.

$$
A = \int_{D_A} \sqrt{\det h}\, dp^1 dp^2, \qquad
e(p) = K(p)^2
$$

$$
\mathcal E_K = \frac{1}{A} \int_{D_A} e(p)\, dA, \qquad
C_A = \sqrt{\mathcal E_K}
$$

## 4. Concentración espacial

Para $q \in (0, 1)$, $\Lambda_q$ mide la fracción de energía curvatural concentrada en la subregión de área $qA$ con mayor $e$. Discretizado sobre la grid:

1. Ordenar puntos por $e$ descendente.
2. Acumular $dA$ hasta alcanzar $qA$.
3. $\Lambda_q = \frac{\int_U e\, dA}{\int_{D_A} e\, dA}$ donde $U$ es esa subregión.

## 5. Participación efectiva espacial

$$
R_{\text{eff}} = \frac{(\int e\, dA)^2}{A \int e^2\, dA}
$$

Mide cuánta parte del dominio participa efectivamente de la energía curvatural.

## 6. Comparación panel base vs perturbado

Se ejecuta el protocolo para:
- Panel base $\mu_0$.
- Panel perturbado $\mu_\epsilon = (1-\epsilon)\mu_0 + \epsilon\,\delta\mu$ con $\epsilon = 0.2$.

## 7. Congelación

- Grid: 9×9 puntos en $[-1, 1]^2$.
- Diferencias finitas: $\epsilon_{\text{fd}} = 10^{-5}$.
- Umbral SPD: $\det h > 10^{-12}$.
- $\epsilon$ de perturbación del panel: 0.2.
- No se modifica el diseño después de ver resultados.

## 8. Alcance y límites

- Sin entrenamiento de redes.
- Sin datos externos ni checkpoints.
- No se modifica `docs/theory/`, `docs/research-notes/`, `experiments/` ni `experiments/T2_A/`.
- No se reutilizan scripts ni resultados de NEM1, NEM2 ni otros experimentos.
- Resultado exploratorio, no confirmatorio.
