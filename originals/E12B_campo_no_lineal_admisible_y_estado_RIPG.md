# E12-B — campo no lineal admisible de perspectivas

## Objetivo

E12-B reemplaza la familia lineal usada para validar la maquinaria inicial por una familia suave y genuinamente no lineal de perspectivas. Debe satisfacer simultáneamente:

\[
\omega_P=d_\theta S_P\in K_\theta^\circ,
\qquad
B(P)K_\theta=0,
\qquad K_\theta=\ker F_\theta,
\]

en todo un vecindario de \(P\), no sólo en un punto aislado.

## Familia propuesta

Para un panel fijo \(\{(x_n,y_n)\}_{n=1}^N\) y dos observables estandarizados \(f_n\in\mathbb R^2\), se define

\[
\boxed{
S_P(\theta)=\sum_{n=1}^N a_n(P)\log p_\theta(y_n\mid x_n)
}
\]

con

\[
\boxed{
a_n(P)=\frac{\exp(P^Tf_n)}{\sum_m\exp(P^Tf_m)}.
}
\]

El punto \(P=0\) asigna peso uniforme. Al mover \(P\), la perspectiva inclina suavemente la relevancia hacia observaciones con determinados valores de los dos observables. La imagen de \(P\mapsto a(P)\) es una familia exponencial bidimensional dentro del simplex; no es una combinación afín constante de dos covectores.

Sea

\[
r_n(\theta)=d_\theta\log p_\theta(y_n\mid x_n),
\qquad
\mu(P)=\sum_n a_n(P)f_n.
\]

Entonces

\[
\boxed{
\omega_P=\sum_n a_n(P)r_n
}
\]

y

\[
\boxed{
B_i(P)=\partial_{P^i}\omega_P
=\sum_n a_n(P)\bigl(f_{ni}-\mu_i(P)\bigr)r_n.
}
\]

Por tanto, \(B\) es una covarianza perspectival entre el observable y el score del modelo.

## Admisibilidad en todo el vecindario

En la parametrización reducida de logits usada desde E11,

\[
F_\theta=\frac1N\sum_n J_n^TC_nJ_n,
\]

donde \(C_n\succ0\) es la covarianza softmax sobre los \(K-1\) logits identificables. Si \(k\in\ker F_\theta\), entonces

\[
J_nk=0\qquad\forall n.
\]

Como

\[
r_n=J_n^T(e_{y_n}-q_n),
\]

se sigue que

\[
r_n(k)=0\qquad\forall n.
\]

Toda combinación de los \(r_n\), incluidos \(\omega_P\) y cada fila de \(B(P)\), pertenece a \(K_\theta^\circ\). En consecuencia,

\[
\boxed{
\omega_P(k)=0,\qquad B(P)k=0
\quad\forall P,\ \forall k\in\ker F_\theta.
}
\]

La admisibilidad es aquí analítica sobre todo el dominio finito de \(P\), no una coincidencia de la malla.

## Protocolo numérico

Se reutilizaron los 80 estados finales de E11-O:

- dos conjuntos naturales;
- cuatro repartos;
- cinco semillas;
- condiciones `true` y `random`.

Se evaluó la malla

\[
(P^1,P^2)\in\{-0.6,-0.4,-0.2,0,0.2,0.4,0.6\}^2,
\]

es decir, 49 puntos por estado y 3,920 evaluaciones de admisibilidad. Para evitar que la familia colapse hacia unas pocas observaciones también se registró el tamaño muestral efectivo

\[
N_{\mathrm{eff}}(P)=\frac{1}{\sum_na_n(P)^2}.
\]

Como control nulo explícito se usaron las 128 o 96 direcciones exactas de reescala de unidades ReLU:

\[
(\delta w_{1j},\delta b_{1j},\delta\beta_j)
=(w_{1j},b_{1j},-\beta_j).
\]

Estas direcciones preservan la función localmente y pertenecen al kernel Fisher.

## Resultados de admisibilidad

| Control | Resultado |
|---|---:|
| Estados evaluados | 80 |
| Puntos por estado | 49 |
| Fracción efectiva mínima \(N_{\mathrm{eff}}/N\) | 0.240 |
| Menor autovalor de \(BB^T\) | \(2.47\times10^{-4}\) |
| Condición máxima de \(B\) | 10.96 |
| Residuo máximo \(\omega_P(k)\) en simetrías ReLU | \(9.02\times10^{-17}\) |
| Residuo máximo \(B(P)k\) en simetrías ReLU | \(8.70\times10^{-17}\) |
| Error máximo de \(B=d_P\omega\) por diferencias finitas | \(1.83\times10^{-10}\) |

No apareció pérdida de rango de \(B\). Por tanto la familia define una inmersión local bidimensional en todos los estados y puntos examinados. Incluso en los extremos, al menos 24 % del panel permanece efectivo; el campo no se produce por concentración en una sola observación.

## Campo métrico

Se construyó, con la formulación condicionada validada en E12-A,

\[
\boxed{
G_\rho(P;\theta)
=B(P)\left(F_\theta+\rho\lambda_{\max}(F_\theta,I)I\right)^{-1}B(P)^T,
\qquad \rho=10^{-4}.
}
\]

El primer atlas numérico usa cuatro casos fijados antes del cálculo: reparto 0, semilla 0, `true/random`, para `digits` y Wisconsin. Contiene 196 matrices métricas.

| Datos | Régimen | Menor autovalor de \(G\) | Menor determinante | Condición máxima | Máxima distancia SPD desde \(P=0\) |
|---|---|---:|---:|---:|---:|
| Digits | true | 0.217 | 0.136 | 12.4 | 2.111 |
| Digits | random | 56.536 | 7,748.4 | 4.0 | 1.065 |
| Wisconsin | true | 0.065 | 0.526 | 921.9 | 7.456 |
| Wisconsin | random | 4.993 | 319.4 | 39.4 | 3.003 |

El residual máximo del solucionador fue \(2.0\times10^{-6}\). Todas las matrices fueron definidas positivas. La distancia afín-invariante desde el centro es distinta de cero en los cuatro casos, por lo que el campo métrico no es constante.

Wisconsin `true` presenta anisotropía alta. Esto no invalida el campo, pero obliga a que E12-C use derivadas covariantes y controles de paso/malla; no debe inferirse curvatura mediante diferencias finitas de una sola resolución.

## Qué queda demostrado

1. Existe una familia no lineal operacionalmente interpretable \(P\mapsto S_P\).
2. \(\omega_P\) y \(B(P)\) satisfacen el axioma de admisibilidad para todo \(P\), por construcción y no por proyección posterior.
3. La malla completa conserva rango dos en los 80 estados.
4. El estimando regularizado produce un campo SPD no constante en los cuatro atlas iniciales.

## Qué no queda demostrado

- No se ha calculado todavía la conexión ni la curvatura.
- No se ha establecido que la curvatura sea distinta de cero o estable entre semillas.
- La métrica sigue condicionada a \(H=I\), \(\rho=10^{-4}\), el panel y los observables declarados.
- La verificación numérica exhaustiva del campo métrico cubre cuatro representantes; la admisibilidad y el rango de \(B\) sí cubren los 80 estados.

## Estado de RIPG y siguiente paso

E12-B queda aprobado. El objeto de E12-C está ahora bien definido:

\[
P\longmapsto G_\rho(P;\theta).
\]

El siguiente cálculo debe obtener

\[
\Gamma^k_{ij}
=\frac12G^{k\ell}
(\partial_iG_{j\ell}+\partial_jG_{i\ell}-\partial_\ell G_{ij})
\]

y, en dimensión dos, la curvatura gaussiana \(K(P;\theta)\). Debe comparar al menos dos pasos de diferencias finitas y comprobar covariancia bajo una transformación no ortogonal de las coordenadas de perspectiva antes de interpretar el signo de \(K\).

## Reproducción

El paquete incluye `e12b_nonlinear_field.py`, el agregador, el script base requerido de E12-A y todas las tablas consolidadas. Reutiliza los estados del paquete E11-O.
