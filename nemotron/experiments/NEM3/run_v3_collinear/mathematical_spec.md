# NEM3 run_v3_collinear — Formalización

Idéntico a NEM3 run_v1 (ver mathematical_spec.md de run_v1) con las siguientes adiciones:

## Colinearidad sintética

Las características se generan como:

$$
x_2 = 0.95 \, x_1 + \eta_2, \qquad
x_3 = 0.90 \, x_1 + 0.50 \, x_2 + \eta_3
$$

con $\eta_i \sim \mathcal N(0, 0.1^2)$. Esto crea dependencia lineal aproximada entre x1, x2, x3, induciendo autovalores pequeños en Fisher.

## Modos débiles de Fisher

Un modo débil es un autovector de Fisher con autovalor $\lambda_k < \tau = 10^{-6}$. Se cuenta el número de modos débiles y se reporta.
