# NEM1 — Diseño congelado

Este documento se congela antes de escribir código ni generar resultados. No se modifican los umbrales, métricas, tolerancias, semillas ni radios después de observar resultados.

## 1. Objetivo

Medir la estabilidad de la métrica de perspectivas $h = B C B^T$ frente a:
1. Perturbaciones pequeñas del panel de evaluación $\mu$.
2. Activación de direcciones casi-degeneradas (modos débiles) de Fisher.

## 2. Hipótesis de trabajo (no ley)

$| \Delta h |$ crece monotónicamente con el tamaño de la perturbación del panel y con la proximidad al kernel de Fisher, sin que esto implique una ley universal de curvatura o generalización.

## 3. Objetos y definiciones

- Perspectiva $p$, funcional escalar $S_p(\theta) = S(\theta, p)$.
- Relevancia $\omega_p = d_\theta S_p$.
- Matriz de Fisher $F_\theta$ y su núcleo $\mathcal K_\theta = \ker F_\theta$.
- Axioma de admisibilidad: $\omega_p \in (\ker F_\theta)^\circ$ y $B k = 0$ para todo $k \in \mathcal K_\theta$.
- Métrica de perspectivas $h = B C B^T$, con $C$ cométrica declarada.
- Distancia SPD entre dos perspectivas: $d_{\text{SPD}}(G_0, G_1) = \|\log(G_0^{-1/2} G_1 G_0^{-1/2})\|_F$.
- Curvatura escalar $R_{\text{scalar}} = 2K$ en dimensión dos.

## 4. Protocolo

1. Construir una red sintética pequeña sin entrenamiento.
2. Establecer un panel base $\mu_0$ y una familia de perspectivas $\{p_a\}$.
3. Generar paneles perturbados $\mu_\epsilon = \mu_0 + \epsilon \cdot \delta\mu$ con $\epsilon$ en una cuadrícula finita.
4. Identificar modos débiles de Fisher (autovalores cercanos a cero) y proyectar perturbaciones sobre ellos.
5. Calcular $h$ para cada $(\mu_\epsilon, p_a)$ y medir:
   - $\| h(\mu_\epsilon) - h(\mu_0) \|_F$ (variación absoluta).
   - $d_{\text{SPD}}(h(\mu_\epsilon), h(\mu_0))$ (distancia SPD).
   - Cambio de curvatura escalar cuando $h$ sea SPD en dimensión dos.
6. Repetir para varias perspectivas y registrar variación máxima y media.

## 5. Congelación

- Umbrales de "cercanía al kernel": decláralos en `mathematical_spec.md` antes de ejecutar.
- Tolerancias numéricas: decláralas antes de ejecutar.
- No se seleccionan supervivientes tras observar resultados.
- No se modifica el diseño después de ver los resultados.

## 6. Alcance y límites

- Sin entrenamiento de redes.
- Sin datos externos ni checkpoints.
- No se modifica `docs/theory/`, `docs/research-notes/`, `experiments/` ni `experiments/T2_A/`.
- No se reutilizan scripts ni resultados de otros experimentos (E16, E15, T1, T2-A).
- Resultado exploratorio, no confirmatorio.
