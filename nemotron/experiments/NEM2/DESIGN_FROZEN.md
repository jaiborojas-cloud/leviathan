# NEM2 — Diseño congelado

Este documento se congela antes de escribir código ni generar resultados. No se modifican los umbrales, métricas, tolerancias, semillas ni radios después de observar resultados.

## 1. Objetivo

Medir la curvatura escalar $K$ y la holonomía en el espacio de perspectivas para una familia de observables no lineal, verificando:
1. La distribución de $K(p)$ sobre un dominio de perspectivas.
2. La coherencia de la holonomía de lazos pequeños con $\theta_{\text{hol}} \approx \int K\, dA$.

## 2. Familia de perspectivas

Familia no lineal usada en E12 (adaptada, sin ejecutar E12):

$$
a_n(p) = \frac{e^{p^T f_n}}{\sum_r e^{p^T f_r}}, \qquad
S_p(\theta) = \sum_n a_n(p) \log p_\theta(y_n|x_n)
$$

con:

$$
\omega_p = \sum_n a_n r_n, \qquad
B_{ai} = \sum_n a_n (f_{na} - \mu_a) (r_n)_i, \qquad
\mu_a = \sum_n a_n f_{na}
$$

donde $r_n = d_\theta \log p_\theta(y_n|x_n)$ y $f_n \in \mathbb R^m$ son rasgos fijos por muestra.

## 3. Métrica de perspectivas

$$
h(p) = B(p) \, C \, B(p)^T
$$

con $C$ cométrica declarada (identidad). Para $m=2$ perspectivas, $h$ es $2\times 2$.

## 4. Curvatura

Conexión de Levi-Civita:

$$
\Gamma^a_{bc} = \frac{1}{2} h^{ad} (\partial_b h_{cd} + \partial_c h_{bd} - \partial_d h_{bc})
$$

Curvatura (convención de E12-C):

$$
R^a{}_{bcd} = \partial_c \Gamma^a_{bd} - \partial_d \Gamma^a_{bc}
+ \Gamma^e_{bd} \Gamma^a_{ec} - \Gamma^e_{bc} \Gamma^a_{ed}
$$

Curvatura de Gauss en 2D:

$$
K = \frac{R_{1212}}{\det h}
$$

## 5. Holonomía

Para un lazo pequeño $\gamma$ que encierra un área $A$:

$$
\theta_{\text{hol}}(\gamma) = \int_\Sigma K\, dA + o(A)
$$

Se verifica numéricamente transportando un vector alrededor de un cuadrado de lado $\delta$ y comparando el ángulo de rotación con $K(p_0) \cdot \delta^2$.

## 6. Congelación

- Espacio de perspectivas: $p^1, p^2 \in [-1, 1]$.
- Grid: 9×9 puntos (81 evaluaciones de $h$ y $K$).
- Lados de lazo para holonomía: $\delta \in \{0.1, 0.2\}$.
- Diferencias finitas: $\epsilon = 10^{-5}$.
- Umbral SPD: $\det h > 10^{-12}$.
- No se modifica el diseño después de ver resultados.

## 7. Alcance y límites

- Sin entrenamiento de redes.
- Sin datos externos ni checkpoints.
- No se modifica `docs/theory/`, `docs/research-notes/`, `experiments/` ni `experiments/T2_A/`.
- No se reutilizan scripts ni resultados de NEM1 ni otros experimentos.
- Resultado exploratorio, no confirmatorio.
