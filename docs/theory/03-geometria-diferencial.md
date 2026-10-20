# 3. Campo métrico y geometría diferencial

Fuentes: [E12-C](../archive/import-2026-10-17/originals/E12C_conexion_curvatura_y_estado_RIPG.md),
[E12-E](../archive/import-2026-10-17/originals/E12E_holonomia_control_derivado_y_cierre_E12.md)
y [diseño T1](../archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_E15-T1_diseno_topologia_local.md).
Las identidades de conexión, Jacobi y exponencial son geometría diferencial
estándar aplicada al campo RIPG declarado; no descubrimientos empíricos nuevos.

## 3.1 Dominio regular y derivadas de la métrica

En un abierto de perspectivas donde $h\succ0$ y es suficientemente suave se
construye su conexión de Levi-Civita. Si $h$ tiene kernel, no se invierte
arbitrariamente ni se define así curvatura riemanniana sobre toda la familia.
Primero hace falta una restricción regular o un cociente con descenso justificado.

En los atlas donde $C$ no depende de $p$, con $B_a$ fila y
$\langle u,v\rangle_C=u C v^T$:

$$
\partial_c h_{ab}=\langle\partial_c B_a,B_b\rangle_C
+\langle B_a,\partial_c B_b\rangle_C,
$$

$$
\begin{aligned}
\partial_d\partial_c h_{ab}={}&
\langle\partial_d\partial_c B_a,B_b\rangle_C
+\langle\partial_c B_a,\partial_d B_b\rangle_C\\
&+\langle\partial_d B_a,\partial_c B_b\rangle_C
+\langle B_a,\partial_d\partial_c B_b\rangle_C.
\end{aligned}
$$

Si $C=C(p)$, ya en la primera derivada se añade $B_a(\partial_c C)B_b^T$;
la segunda requiere todos los términos adicionales. Las simplificaciones de E12
fijan modelo, panel, Fisher y regularizador respecto de las perspectivas.
Para esta ruta analítica de curvatura se necesita, como condición suficiente,
$S$ con derivadas mixtas hasta las que aparecen en $\partial_p^2B$; decir sólo
«$S$ diferenciable» no basta.

## 3.2 Conexión y convención de curvatura

$$
\Gamma^a_{bc}=\frac12 h^{ad}
(\partial_b h_{cd}+\partial_c h_{bd}-\partial_d h_{bc}).
$$

Para vectores perspectivales, $(\nabla_b v)^a=\partial_b v^a+\Gamma^a_{bc}v^c$.
Los símbolos de conexión no son componentes de un tensor. En una carta nueva
$p=\varphi(q)$ aparece el término no homogéneo:

$$
\widetilde\Gamma^a_{bc}
=(J^{-1})^a{}_r\left[J^i{}_bJ^j{}_c\Gamma^r_{ij}
+\partial_b\partial_c\varphi^r\right].
$$

Conservando la convención explícita de E12-C:

$$
R^a{}_{bcd}=\partial_c\Gamma^a_{bd}-\partial_d\Gamma^a_{bc}
+\Gamma^e_{bd}\Gamma^a_{ec}-\Gamma^e_{bc}\Gamma^a_{ed}.
$$

Se baja el primer índice mediante $R_{abcd}=h_{ae}R^e{}_{bcd}$.
En una superficie:

$$
K=\frac{R_{1212}}{\det h},\qquad R_{\rm scalar}=2K.
$$

Los componentes cambian con la carta; $K$ es escalar. En dimensión $m>2$ la
curvatura seccional de un plano generado por $u,v$ es

$$
\operatorname{Sec}(u,v)=
\frac{\langle R(u,v)v,u\rangle_h}
{h(u,u)h(v,v)-h(u,v)^2}.
$$

Una única curvatura escalar no describe todas las secciones ni determina corte.
El signo de $K$ observado en una tarea no es una ley del aprendizaje.

## 3.3 Geodésicas, longitud y exponencial

$$
\ddot p^a+\Gamma^a_{bc}(p)\dot p^b\dot p^c=0,\qquad
L_h(\gamma)=\int\sqrt{h_{ab}(\gamma)\dot\gamma^a\dot\gamma^b}\,dt.
$$

La distancia intrínseca es el ínfimo de longitudes de curvas admisibles. Una
geodésica deja de ser necesariamente minimizante al prolongarse. El exponencial
$\exp_{p_0}(v)=\gamma_v(1)$ se define donde la solución existe y permanece en
el dominio regular. No se presupone completitud del campo numérico.

La medida de volumen es $\sqrt{\det h}\,dp^1\cdots dp^m$; en dos dimensiones
se escribe $dA$. Coordenadas normales linealizadas en el centro,
$q=h(p_0)^{1/2}(p-p_0)$, igualan la métrica sólo en ese punto: no reemplazan
la integración geodésica sobre una región finita.

## 3.4 Jacobi y acondicionamiento de Dexp en dimensión dos

Una variación geodésica satisface

$$
\nabla_{\dot\gamma}^2J+R(J,\dot\gamma)\dot\gamma=0.
$$

Para una geodésica unitaria de una superficie y variación transversal angular,
el factor de separación $j$ obedece

$$
j''(r)+K(\gamma(r))j(r)=0,\quad j(0)=0,\quad j'(0)=1.
$$

En marcos ortonormales intrínsecos, el factor radial de $D\exp$ es 1 y el
transversal es $j(r)/r$. Para $r>0$, lejos de singularidades:

$$
\det D\exp=\frac{j(r)}r,\qquad
\kappa(D\exp)=\frac{\max(1,|j/r|)}{\min(1,|j/r|)}.
$$

La primera expresión conserva orientación; el acondicionamiento usa valores
singulares. El límite $j/r\to1$ vale al acercarse al origen. El primer cero
no trivial de $j$ señala un conjugado por esa dirección. El signo, no sólo el
módulo del determinante, importa para diagnosticar pliegues.

Antes de pérdida de inyectividad, $ds^2=dr^2+j(r,\alpha)^2d\alpha^2$ y
$dA=j\,dr\,d\alpha$ con orientación positiva. Más allá, $|j|$ integra área
con multiplicidad: no equivale al área de la unión de imágenes.

Localmente, si $K$ es suave,

$$
\frac{j(r)}r=1-\frac{K(p_0)}6r^2+O(r^3).
$$

La relación entre curvatura y deformación a radio común es por eso un control
geométrico esperado; una correlación en un mismo estado no demuestra predicción
temporal independiente.

## 3.5 Conjugado, corte, Maxwell y frontera

El radio de inyectividad describe hasta dónde el exponencial es difeomorfismo
sobre una bola apropiada. La singularidad local de $D\exp$ y el solapamiento
global de imágenes son fenómenos distintos. En un dominio riemanniano completo,
la teoría estándar relaciona el corte con pérdida de minimización, conjugados
y geodésicas minimizantes múltiples; esas hipótesis no se importan sin comprobar
a un atlas numérico incompleto.

Una colisión de geodésicas de igual longitud es candidata a fenómeno Maxwell;
se necesita verificar minimización y estabilidad para identificar corte. Un borde
simple no prueba inyectividad del interior. Un fallo SPD, una frontera de dominio,
un límite de presupuesto o una integración fallida tampoco son automáticamente
un evento geométrico. Véanse los [límites históricos T1](../research-status.md).

## 3.6 Transporte paralelo y holonomía

$$
\frac{dv^a}{dt}+\Gamma^a_{bc}(p(t))\dot p^b v^c=0.
$$

La holonomía compara el vector final con el inicial en el mismo espacio tangente.
Para lazos pequeños orientados y la convención de E12-E:

$$
\theta_{\rm hol}(\gamma)=\int_{\Sigma_\gamma}K\,dA
+o(\operatorname{Area}(\Sigma_\gamma)).
$$

La orientación y el signo de Riemann deben ser consistentes. Comparar lazos con
el mismo lado coordenado puede confundir curvatura con expansión del área.
La exactitud $d_\theta\omega=0$ trata de una 1-forma del modelo; esta holonomía
trata de la conexión del campo perspectival. No hay contradicción.
La holonomía se usa como control derivado de curvatura, no como prueba causal
ni como predictor independiente ya establecido.

## 3.7 Geometría de la inmersión y ecuación de Gauss

Con $\theta$ fijo, cométrica fija y $B$ de rango fila completo, la aplicación
$\Phi_\theta$ es una inmersión local en el espacio vectorial dual admisible
con su producto positivo. Para una superficie inmersa y $u,v$ ortonormales:

$$
K_{\mathcal P}=\operatorname{Sec}_{\rm amb}(u\wedge v)
+\langle\mathrm{II}(u,u),\mathrm{II}(v,v)\rangle
-\|\mathrm{II}(u,v)\|^2.
$$

$\mathrm{II}$ es la segunda forma fundamental. En ese ambiente vectorial con
producto fijo, la curvatura ambiente es cero; la curvatura inducida puede no serlo.
Esto explica cómo una familia no lineal de relevancias puede curvarse sin atribuir
esa curvatura directamente a Fisher como campo sobre el modelo. En dimensión
mayor se aplica la versión seccional a cada plano. Esta descripción depende de
la familia y del ambiente declarados; no selecciona un ambiente universal ni
autoriza extrapolar desde una sola superficie a todas las familias perspectivales.
