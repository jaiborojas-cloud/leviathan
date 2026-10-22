# NEM3 run_v3_collinear — Diseño congelado

## 1. Objetivo

Medir observables geométricos ($C_A$, $R_{\text{eff}}$, $\Lambda_q$) sobre un dataset sintético con colinearidad entre características, para inducir modos débiles de Fisher y comparar contra el dataset no-colineal de run_v1.

## 2. Dataset sintético colineal

- n_inputs = 50, n_features = 5, n_classes = 3
- Características generadas con colinearidad estructurada:
  - x2 = 0.95 * x1 + ruido
  - x3 = 0.90 * x1 + 0.50 * x2 + ruido
  - x4 = ruido independiente
  - x5 = ruido independiente
- Esto induce autovalores de Fisher cercanos a cero (modos débiles).

## 3. Protocolo (idéntico a run_v1 salvo el dataset)

- Modelo lineal de regresión logística (pesos aleatorios fijos, sin entrenamiento).
- Familia de perspectivas no lineal (softmax de rasgos fijos, m=2).
- Grid 9×9 en p ∈ [-1, 1]².
- Diferencias finitas ε = 1e-5.
- Perturbación del panel: ε_panel = 0.2.
- Umbral SPD: det h > 1e-12.
- Umbral modo débil: tau = 1e-6.

## 4. Congelación

No se modifica el diseño después de observar resultados.
