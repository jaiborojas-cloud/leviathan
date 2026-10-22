# NEM3 — Formalización y derivaciones

## 1. Familia no lineal de perspectivas

Sea $\mu$ una distribución de evaluación sobre pares $(x, y)$. Para cada muestra $n$ se declara un rasgo fijo $f_n \in \mathbb R^m$ (con $m=2$ perspetivas). Definimos:

$$
a_n(p) = \frac{e^{p^T f_n}}{\sum_r e^{p^T f_r}}, \qquad
S_p(\theta) = \sum_n a_n(p) \log p_\theta(y_n|x_n)
$$

Sea $r_n = d_\theta \log p_\theta(y_n|x_n) \in T_\theta^* M$. Entonces:

$$
\omega_p = \sum_n a_n r_n
$$

Definiendo $\mu_a(p) = \sum_n a_n f_{na}$:

$$
B_{ai} = \partial_{p^a} \partial_{\theta^i} S
= \sum_n a_n (f_{na} - \mu_a) (r_n)_i
$$

## 2. Métrica de perspectivas y elemento de área

Con cométrica $C$ declarada (identidad en NEM3):

$$
h(p) = B(p) \, C \, B(p)^T
$$

Para $m=2$, $h$ es una matriz $2\times 2$. El elemento de área es:

$$
dA = \sqrt{\det h(p)}\, dp^1 dp^2
$$

El área total del dominio:

$$
A = \int_{[-1,1]^2} \sqrt{\det h(p)}\, dp^1 dp^2
$$

## 3. Curvatura de Gauss

Conexión de Levi-Civita:

$$
\Gamma^a_{bc}(p) = \frac{1}{2} h^{ad}(p)
\left( \partial_b h_{cd}(p) + \partial_c h_{bd}(p) - \partial_d h_{bc}(p) \right)
$$

Curvatura:

$$
R^a{}_{bcd} = \partial_c \Gamma^a_{bd} - \partial_d \Gamma^a_{bc}
+ \Gamma^e_{bd} \Gamma^a_{ec} - \Gamma^e_{bc} \Gamma^a_{ed}
$$

$$
K(p) = \frac{R_{1212}(p)}{\det h(p)}
$$

## 4. Observables geométricos

Densidad de energía: $e(p) = K(p)^2$.

Energía curvatural total:

$$
E = \int_{D_A} e(p)\, dA = \int_{[-1,1]^2} K(p)^2 \sqrt{\det h(p)}\, dp^1 dp^2
$$

Energía curvatural media:

$$
\mathcal E_K = \frac{E}{A}, \qquad C_A = \sqrt{\mathcal E_K}
$$

Concentración espacial para $q \in \{0.25, 0.5, 0.75\}$:

$$
\Lambda_q = \frac{1}{E} \sup_{U \subseteq D_A,\, \operatorname{Area}(U) = qA} \int_U e(p)\, dA
$$

Participación efectiva espacial:

$$
R_{\text{eff}} = \frac{E^2}{A \int_{D_A} e(p)^2\, dA}
$$

## 5. Discretización

Sobre una grid de $N \times N$ puntos con paso $\Delta p$ en cada dirección:

$$
dA_i \approx \sqrt{\det h(p_i)}\, \Delta p^2, \qquad
A \approx \sum_i dA_i
$$

$$
E \approx \sum_i e_i\, dA_i, \qquad
\int e^2\, dA \approx \sum_i e_i^2\, dA_i
$$

Para $\Lambda_q$: ordenar puntos por $e_i$ descendente, acumular $dA_i$ hasta superar $qA$, y sumar $e_i dA_i$ de los puntos seleccionados.

## 6. Umbrales declarados (pre-ejecución)

| Parámetro | Valor | Observación |
|---|---|---|
| Dominio | $[-1, 1]^2$ | Espacio de perspectivas |
| Grid | 9×9 | 81 puntos |
| $\epsilon_{\text{fd}}$ | $10^{-5}$ | Paso para derivadas de $h$ |
| Umbral SPD | $\det h > 10^{-12}$ | Para descartar puntos degenerados |
| $\epsilon$ panel | 0.2 | Perturbación del panel |
| $q$ para $\Lambda_q$ | 0.25, 0.5, 0.75 | Niveles de concentración |
| Modelo | Regresión logística lineal, 3 features, 2 clases | Sin entrenamiento |
| Rasgos $f_n$ | Las 2 primeras características de cada muestra | Fijados antes de ejecutar |
