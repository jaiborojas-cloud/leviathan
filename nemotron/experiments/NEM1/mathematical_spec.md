# NEM1 — Formalización y derivaciones

## 1. Perturbación del panel

Sea $\mu_0$ la distribución de evaluación base y $\delta\mu$ una perturbación con $\int \delta\mu = 0$. Definimos:

$$
\mu_\epsilon = (1 - \epsilon) \, \mu_0 + \epsilon \, \delta\mu, \qquad 0 \le \epsilon \le \epsilon_{\max}
$$

La matriz de Fisher se convierte en:

$$
F_\theta(\mu_\epsilon) = \mathbb E_{(x,y) \sim \mu_\epsilon} \left[ \partial_i \log p_\theta(y|x) \, \partial_j \log p_\theta(y|x) \right]
$$

## 2. Modos débiles de Fisher

Sea $F_\theta = U \Lambda U^T$ la descomposición espectral con autovalores $\lambda_1 \ge \lambda_2 \ge \cdots \ge \lambda_d \ge 0$. Un modo débil es un autovector $u_k$ con $\lambda_k < \tau$ para un umbral $\tau$ declarado antes de ejecutar.

El núcleo aproximado es $\mathcal K_\theta \approx \operatorname{span}\{u_k : \lambda_k < \tau\}$.

## 3. Variación de la métrica de perspectivas

Para cada panel $\mu_\epsilon$ y perspectiva $p_a$, la matriz $B$ depende del panel a través de los observables $o_l(\theta; \mu)$:

$$
B(\mu_\epsilon)_{ai} = \partial_{p^a} \partial_{\theta^i} S(\theta, p_a; \mu_\epsilon)
$$

En la implementación de NEM1 se usa una aproximación lineal:

$$
B(\mu_\epsilon) = B_0 + \epsilon \cdot \delta B
$$

donde $\delta B$ se deriva de la diferencia de medias de entradas entre el panel base y el panel perturbado, proyectada sobre el espacio de observables. Esto modela el efecto del panel sobre los observables $o_l(\theta)$ de la familia lineal (sección 1.4 de `docs/theory/01-fundamentos.md`).

$$
h(\mu_\epsilon) = B(\mu_\epsilon) \, C \, B(\mu_\epsilon)^T
$$

Se mide:

$$
\Delta h(\epsilon) = \| h(\mu_\epsilon) - h(\mu_0) \|_F
$$

$$
d_{\text{SPD}}(\epsilon) = \left\| \log\left( h(\mu_0)^{-1/2} \, h(\mu_\epsilon) \, h(\mu_0)^{-1/2} \right) \right\|_F
$$

Cuando $h$ es SPD en dimensión dos, la curvatura escalar es:

$$
K(\epsilon) = \frac{R_{1212}(\epsilon)}{\det h(\mu_\epsilon)}, \qquad R_{\text{scalar}}(\epsilon) = 2 K(\epsilon)
$$

## 4. Proyección sobre modos débiles

Para cada dirección de perturbación $\delta S = S(\cdot; \mu_\epsilon) - S(\cdot; \mu_0)$, se calcula su componente sobre el núcleo aproximado de Fisher:

$$
\delta S_{\ker} = \sum_{\lambda_k < \tau} \langle \delta S, u_k \rangle \, u_k
$$

y se correlaciona con $\Delta h(\epsilon)$. En la implementación, la proyección se calcula sobre la diferencia de matrices de Fisher $dF = F(\mu_\epsilon) - F(\mu_0)$ proyectada en el espacio de modos débiles.

## 5. Umbrales declarados (pre-ejecución)

| Parámetro | Valor | Observación |
|---|---|---|
| $\epsilon_{\max}$ | 0.2 | Máxima perturbación del panel |
| Pasos de $\epsilon$ | 11 | Cuadrícula uniforme $[0, 0.2]$ |
| $\tau$ (modo débil) | $10^{-6}$ | Umbral de autovalor de Fisher |
| Red sintética | 3 capas, 8-8-4 neuronas | Sin entrenamiento |
| Número de perspectivas | 5 | Familia lineal de observables |
| Cométrica $C$ | Identidad | Declarada explícitamente |
