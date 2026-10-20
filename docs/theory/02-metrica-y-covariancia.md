# 2. Métrica inducida, covariancia y regularización

Fuentes: [axioma](../archive/import-2026-10-17/originals/RIPG_contexto_vigente_axioma.md),
[E11-J](../archive/import-2026-10-17/originals/E11J_regularizacion_explicita_y_estado_RIPG.md)
y [formalización E16](../../experiments/E16/mathematical_spec.md).

## 2.1 Pullback de la cométrica

Para $\theta$ fijo, la aplicación de relevancias es
$\Phi_\theta:p\mapsto\omega_p$. Su diferencial toma $u\in T_p\mathcal P$
en el covector $B^Tu$. Si $C$ es una cométrica declarada:

$$
h_p(u,v)=(B^Tu)^T C(B^Tv),\qquad
\boxed{h_{ab}=B_{ai}C^{ij}B_{bj},\quad h=BCB^T.}
$$

En el caso ideal admisible:

$$
h^{(\theta)}=\Phi_\theta^*(\bar g_{F,\theta}^{-1}).
$$

Si $C$ es positiva en el dual identificable, $h$ es semidefinida y

$$
\ker h=\ker B^T,\qquad \operatorname{rank}h=\operatorname{rank}B
$$

entendiendo $B$ sobre ese espacio admisible. Se obtiene una métrica riemanniana
en la familia sólo si su rango es $m$. Una dirección nula es una variación de
perspectiva cuya relevancia no cambia a primer orden, no evidencia automática
de un fenómeno emergente. Para cocientar esas direcciones hace falta descenso.

## 2.2 Cambios de carta del modelo

Sea $\theta=\psi(\eta)$, $A^i{}_j=\partial\theta^i/\partial\eta^j$
invertible, independiente de $p$. Puntualmente:

$$
\omega_\eta=A^T\omega_\theta,\quad B_\eta=B_\theta A,\quad
F_\eta=A^TF_\theta A,\quad C_\eta=A^{-1}C_\theta A^{-T}.
$$

Por tanto $B_\eta C_\eta B_\eta^T=h_\theta$. Las segundas derivadas del
cambio aparecen al transformar Hessianas y conexiones, no en esta contracción
puntual de covectores y cométrica.

Para $p=\varphi(q)$ con Jacobiano $J=D\varphi$ independiente de $\theta$:

$$
B_q=J^TB_p,\qquad \boxed{h_q=J^T h_p J.}
$$

Es cambio de carta si $\varphi$ es un difeomorfismo local entre espacios de la
misma dimensión; en una subfamilia es pullback. Los autovalores de una matriz
métrica no son invariantes bajo congruencias arbitrarias, aunque el rango y las
longitudes de vectores correctamente transformados sí lo sean.

## 2.3 Pseudoinversa en el caso degenerado

En coordenadas compatibles, la contracción ideal se escribe

$$
h=B F^+ B^T.
$$

No se presupone que $(A^TFA)^+=A^{-1}F^+A^{-T}$. Moore–Penrose depende de
la estructura euclídea usada para elegir representantes. La invariancia se
justifica por el cociente: para $\alpha,\beta\in\mathcal K^\circ$, si
$Fx=\beta$, entonces $\alpha(x)$ no depende de la solución porque dos
soluciones difieren en $\ker F$. La contracción $\alpha^T F^+\beta$
representa ese valor bajo las hipótesis de admisibilidad, no una ley tensorial
general de la pseudoinversa como matriz.

Si el rango cambia, el campo de pseudoinversas puede perder suavidad. Tampoco
un corte sobre el espectro crudo de Fisher es covariante ante cualquier cambio
no ortogonal. El control debe considerar espectro, kernel y referencia transportada.

## 2.4 Estimando regularizado condicionado

E11-J declara $H\succ0$, $\rho>0$ y el mayor autovalor generalizado de
$Fv=\lambda Hv$:

$$
\alpha=\rho\lambda_{\max}(F,H),\qquad
\boxed{G_{\rho,\mathcal U}
=B_{\mathcal U}(F_{\mathcal U}+\alpha H_{\mathcal U})^{-1}B_{\mathcal U}^T.}
$$

$\mathcal U$ fija el alcance tangente o bloques incluidos. Si $\alpha>0$, la
matriz invertida es SPD; si $F=0$, $\lambda_{\max}=0$ y esa garantía no vale sin
una regla adicional expresamente declarada. La regla no se inventa en esta síntesis.

Transportando $H_\eta=A^TH_\theta A$, los autovalores generalizados no cambian
y se obtiene la misma métrica perspectival. Reponer $H=I$ en cada carta crea
otro estimando. Covariancia condicionada no significa canonicidad de $H$,
$\rho$, el panel, la familia o el alcance.

No todas las etapas usan la misma escala: por ejemplo, E16-B declara
$g=F+0.01H$, sin el factor $\lambda_{\max}$. La formulación general
$h=B g^{-1}B^T$ es común, pero las elecciones operativas no son intercambiables.
El límite de regularización cero sólo recupera la contracción ideal con
admisibilidad y control del soporte/espectro; no de forma automática.

## 2.5 Precisión y rango numérico

Si $C=L L^T$ es SPD, poner $U=BL$ da $h=UU^T$. Para aproximaciones:

$$
\widehat U-U=(\widehat B-B)L+\widehat B(\widehat L-L),
$$

$$
\|\widehat U-U\|_2\le\|\widehat U-U\|_F
\le\|(\widehat B-B)L\|_F+\|\widehat B(\widehat L-L)\|_F.
$$

Weyl acota la diferencia de valores singulares por la norma espectral del error.
Un criterio de rango exige separación del corte y un error compatible en $U$;
comparar sólo error crudo de $B$ con un umbral de $U$ omite la cométrica.
Comparaciones entre métodos, precisión duplicada y diferencias finitas son
controles; sin cotas validadas de error no se convierten en certificados exactos.
Esta desigualdad estándar explica el control instrumental documentado en
[la fuente E16-C fuera de esta base](https://github.com/jaiborojas-cloud/leviathan/blob/4fd7eb5790a7161731e22c238f29138cd66425ac/experiments/E16/C/mathematical_spec.md).
Aquí no se ejecuta ni importa esa rama, ni se cambia el outcome de E16-B.
