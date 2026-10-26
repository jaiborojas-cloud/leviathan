# DIN-D9g: teoría del estimando y alcance

Sea i la inicialización, g=(nivel,split), y c el candidato. Tildes indican
centrado en las cinco inicializaciones del grupo g. La base es
B=(loss_train, loss_panel, acc_panel, X), evaluada al tiempo t del candidato.

En cada bloque b se estiman por OLS en splits ajenos a b:

\[
\hat\beta_{B,-b}=\arg\min_\beta\|\widetilde Y_{-b}-\widetilde B_{-b}\beta\|^2,
\qquad
\hat\theta_{-b}=\arg\min_\theta\|\widetilde Y_{-b}-[\widetilde B,\widetilde c]_{-b}\theta\|^2.
\]

\[
D_{c\mid B}=1-\frac{\sum_b\|\widetilde Y_b-[\widetilde B,\widetilde c]_b\hat\theta_{-b}\|^2}
 {\sum_b\|\widetilde Y_b-\widetilde B_b\hat\beta_{B,-b}\|^2}.
\]

D negativo se conserva. D positivo mide mejora sobre ESTA base lineal. Los
controles D_B y D_c,solo usan como denominador SSE_0=sum Y_tilde². No se comparan
como si fueran el mismo denominador: 1−D_completo,0=(1−D_B)(1−D_c|B).

Frisch–Waugh–Lovell permite calcular exactamente el mismo ajuste sin 2.001 SVD
completas por bloque: residualizar c respecto de B en entrenamiento, coeficiente
r_cᵀY/||r_c||² y predicción sobre c_test−B_test beta_c,train. La implementación
contrasta los D nulos completos con OLS directo y con D_cv C1 sin cambios.
SVD/pseudoinversa conserva el rango numérico; un alias se declara no identificable.

La permutación es del candidato, dentro de g, manteniendo base/desenlace/bloques.
Su p exploratorio usa (1+#D_perm≥D−1e-15)/2001. La equivalencia computacional no
es una demostración de calibración bajo cualquier dependencia o misspecificación.
La regla del responsable conserva .05/12 para los ONCE candidatos enumerados.

El riesgo empírico test usa 3.000 ejemplos nuevos, balance fijo 1.000/clase. Su SE
descriptiva estratificada es sqrt(sum_c s_c²/(9·1000)). La red y la escala se fijaron
sólo con train; panel aparece en predictores, nunca se usa test para optimizar.
Test emparejado entre inicializaciones/niveles reduce ruido de comparación, pero
requiere bloquear los tres niveles del mismo split juntos, como se hace aquí.

M=R(F+γI)^−1Rᵀ y su dependencia del gradiente de log-probabilidad son identidades.
Ni c=maxdiag/tr ni log tr ni log rho determinan algebraicamente la pérdida TEST.
Que un candidato añada D sobre cuatro covariables es un hallazgo de estos datos,
no una identidad, causa ni prueba de información nueva frente a toda base flexible.
Un efecto condicional puede coexistir con D marginal nulo o negativo.
