# NEM2 — Formalización y derivaciones

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

## 2. Métrica de perspectivas

Con cométrica $C$ declarada (identidad en NEM2):

$$
h(p) = B(p) \, C \, B(p)^T
$$

Para $m=2$, $h$ es una matriz $2\times 2$. El dominio de perspectivas es $p = (p^1, p^2) \in [-1, 1]^2$.

## 3. Conexión de Levi-Civita

$$
\Gamma^a_{bc}(p) = \frac{1}{2} h^{ad}(p)
\left( \partial_b h_{cd}(p) + \partial_c h_{bd}(p) - \partial_d h_{bc}(p) \right)
$$

donde las derivadas parciales se calculan por diferencias finitas centrales:

$$
\partial_a h_{bc}(p) \approx \frac{h_{bc}(p + \epsilon e_a) - h_{bc}(p - \epsilon e_a)}{2\epsilon}
$$

## 4. Tensor de curvatura y curvatura de Gauss

$$
R^a{}_{bcd} = \partial_c \Gamma^a_{bd} - \partial_d \Gamma^a_{bc}
+ \Gamma^e_{bd} \Gamma^a_{ec} - \Gamma^e_{bc} \Gamma^a_{ed}
$$

$$
R_{abcd} = h_{ae} R^e{}_{bcd}, \qquad
K = \frac{R_{1212}}{\det h}
$$

## 5. Holonomía

Para un lazo pequeño cuadrado de lado $\delta$ centrado en $p_0$, se transporta paralelamente un vector $v$:

$$
\frac{dv^a}{dt} + \Gamma^a_{bc}(\gamma(t)) v^b \frac{d\gamma^c}{dt} = 0
$$

Discretizado en pasos pequeños:

$$
v_{k+1} = v_k - \Gamma(\gamma_k) \, v_k \, \Delta p
$$

El ángulo de holonomía es:

$$
\theta_{\text{hol}} = \arccos\left( \frac{v_{\text{final}} \cdot v_{\text{initial}}}{|v_{\text{final}}|\,|v_{\text{initial}}|} \right)
$$

Se compara con $K(p_0) \cdot \delta^2$.

## 6. Umbrales declarados (pre-ejecución)

| Parámetro | Valor | Observación |
|---|---|---|
| Dominio | $[-1, 1]^2$ | Espacio de perspectivas |
| Grid | 9×9 | 81 puntos |
| $\epsilon$ (diferencias finitas) | $10^{-5}$ | Paso para derivadas de $h$ |
| $\delta$ (lado de lazo) | 0.1, 0.2 | Dos tamaños de lazo |
| Pasos de transporte | 20 por lado | Discretización del lazo |
| Umbral SPD | $\det h > 10^{-12}$ | Para descartar puntos degenerados |
| Modelo | Regresión logística lineal, 3 features, 2 clases | Sin entrenamiento |
| Rasgos $f_n$ | Las 2 primeras características de cada muestra | Fijados antes de ejecutar |
