# Marco teórico de RIPG — síntesis de lectura (Nemotron)

Síntesis documental de `docs/theory/README.md` y sus capítulos 01–06. No contiene nuevas ejecuciones ni cambios a protocolos, resultados ni a `experiments/T2_A/claude`.

## 1. Espacios, funcional y relevancia

Una perspectiva $p$ especifica un funcional escalar:

$$S: M \times \mathcal P \to \mathbb R, \qquad S_p(\theta) = S(\theta, p)$$

Puede representar un observable, costo, score o ponderación de un panel. Su relevancia es el diferencial respecto del modelo:

$$\omega_p = d_\theta S_p \in T_\theta^* M, \qquad (\omega_p)_i = \partial_{\theta^i} S(\theta, p)$$

Es un covector, no un vector de actualización.

## 2. Fisher del modelo y axioma de admisibilidad

Para un modelo probabilístico con distribución de evaluación $\mu$:

$$F_{ij}(\theta) = \mathbb E_{x \sim \mu,\, y \sim p_\theta(\cdot|x)}
\left[\partial_i \log p_\theta(y|x)\,\partial_j \log p_\theta(y|x)\right]$$

El núcleo de Fisher es $\mathcal K_\theta = \ker F_\theta$ y su anulador:

$$\mathcal K_\theta^\circ = \{\alpha \in T_\theta^* M : \alpha(k) = 0\ \forall k \in \mathcal K_\theta\}$$

El axioma de admisibilidad perspectival exige:

$$\boxed{\omega_p \in \mathcal K_\theta^\circ, \qquad B k = 0\ \forall k \in \mathcal K_\theta}$$

con $B_{ai} = \partial_{p^a} \partial_{\theta^i} S$. La geometría identificable vive en el cociente $Q_\theta = T_\theta M / \mathcal K_\theta$.

## 3. Métrica inducida sobre perspectivas

Para cométrica $C$ declarada:

$$\boxed{h_{ab} = B_{ai} C^{ij} B_{bj}, \qquad h = B C B^T}$$

En el caso ideal admisible:

$$h^{(\theta)} = \Phi_\theta^*(\bar g_{F,\theta}^{-1})$$

Si $C$ es positiva en el dual identificable, $h$ es semidefinida con $\ker h = \ker B^T$ y $\operatorname{rank} h = \operatorname{rank} B$. Solo si el rango es $m$ se obtiene una métrica riemanniana en la familia.

En el caso degenerado:

$$h = B F^+ B^T$$

La estimación regularizada (E11-J) es:

$$G_{\rho, \mathcal U} = B_{\mathcal U} (F_{\mathcal U} + \alpha H_{\mathcal U})^{-1} B_{\mathcal U}^T, \qquad \alpha = \rho \lambda_{\max}(F, H)$$

## 4. Geometría diferencial

Cuando $h \succ 0$ y es suave, se construye la conexión de Levi-Civita:

$$\Gamma^a_{bc} = \frac{1}{2} h^{ad}
(\partial_b h_{cd} + \partial_c h_{bd} - \partial_d h_{bc})$$

Curvatura (convención de E12-C):

$$R^a{}_{bcd} = \partial_c \Gamma^a_{bd} - \partial_d \Gamma^a_{bc}
+ \Gamma^e_{bd} \Gamma^a_{ec} - \Gamma^e_{bc} \Gamma^a_{ed}$$

En una superficie:

$$K = \frac{R_{1212}}{\det h}, \qquad R_{\text{scalar}} = 2K$$

Geodésicas:

$$\ddot p^a + \Gamma^a_{bc}(p) \dot p^b \dot p^c = 0$$

Jacobi y acondicionamiento de $D\exp$ en dimensión dos:

$$j''(r) + K(\gamma(r)) j(r) = 0, \quad j(0) = 0, \quad j'(0) = 1$$

$$\det D\exp = \frac{j(r)}{r}, \qquad
\kappa(D\exp) = \frac{\max(1, |j/r|)}{\min(1, |j/r|)}$$

Holonomía para lazos pequeños:

$$\theta_{\text{hol}}(\gamma) = \int_{\Sigma_\gamma} K\, dA + o(\operatorname{Area}(\Sigma_\gamma))$$

## 5. Observables geométricos y atribución

Distancia entre matrices SPD:

$$d_{\text{SPD}}(G_0, G_1) = \left\|\log(G_0^{-1/2} G_1 G_0^{-1/2})\right\|_F$$

Energía curvatural y $C_A$:

$$A = \int_{D_A} dA, \qquad
\mathcal E_K = \frac{1}{A} \int_{D_A} K^2\, dA, \qquad
\boxed{C_A = \sqrt{\mathcal E_K}}$$

Concentración espacial:

$$\Lambda_q = \frac{1}{E} \sup_{U \subseteq D_A,\, \operatorname{Area}(U) = qA} \int_U e\, dA, \qquad e = K^2$$

Participación efectiva espacial:

$$R_{\text{eff}} = \frac{(\int_{D_A} K^2\, dA)^2}{A \int_{D_A} K^4\, dA}$$

Participación oculta:

$$\eta = \frac{1}{m} \operatorname{tr}(G_{\text{full}}^{-1} \Delta G_{\text{hidden|output}})$$

## 6. Composicionalidad y coarse-graining

Cuatro operaciones: carta invertible, subfamilia, agregación, composición escalar.

Para submersión $\pi: \mathcal P \to \mathcal Q$, el descenso de tensor requiere horizontalidad ($h(v, \cdot) = 0$ para $v \in \ker D\pi$) e independencia de representante:

$$\bar h_q(u, w) = h_p(\widetilde u, \widetilde w), \qquad \pi(p) = q$$

Composición escalar $S_{\text{macro}} = \Psi(S_1, \ldots, S_k)$:

$$B_{\text{macro}, ai} = \sum_\ell \Psi_\ell B_{\ell, ai}
+ \sum_{\ell,r} \Psi_{\ell r} (\partial_a S_r) \omega_{\ell, i}$$

## 7. Hipótesis y límites

La hipótesis de trabajo (no ley) es de magnitud, no signo:

$$|K_{\text{true}}(p_0)| > |K_{\text{random}}(p_0)|, \qquad
\Delta C_A = C_A^{\text{true}} - C_A^{\text{random}} > 0$$

E12 reportó dirección de magnitud en 36/40 pares; es evidencia exploratoria en dos tareas, no un teorema. No se adopta como ley que mayor desplazamiento signifique mejor aprendizaje.

Las preguntas abiertas del marco (Q01–Q09) se resumen en `docs/research-notes/open-questions.md` y se mapean en `preguntas_abiertas.md` de esta carpeta.
