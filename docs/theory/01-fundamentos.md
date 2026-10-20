# 1. Espacios, relevancia y axioma de admisibilidad

Fuentes principales: [contexto y axioma](../archive/import-2026-10-17/originals/RIPG_contexto_vigente_axioma.md),
[E12-B](../archive/import-2026-10-17/originals/E12B_campo_no_lineal_admisible_y_estado_RIPG.md)
y [antecedentes del notebook](../archive/review-before-import/docs/foundations/mathematical-framework.md).
Convenciones comunes en el [índice](README.md).

## 1.1 Perspectiva y funcional

Una perspectiva $p$ especifica una función escalar del modelo:

$$
S:M\times\mathcal P\to\mathbb R,\qquad S_p(\theta)=S(\theta,p).
$$

Puede representar un observable, costo, score o ponderación de un panel. No se
deduce de Fisher una única elección de $S$. Una perspectiva no es una carta de
coordenadas: cambiar $p$ puede cambiar operacionalmente qué se evalúa.

Su relevancia es el diferencial respecto del modelo:

$$
\omega_p=d_\theta S_p\in T_\theta^*M,\qquad
(\omega_p)_i=\partial_{\theta^i}S(\theta,p).
$$

Es un covector, no un vector de actualización. Para una métrica SPD $g$, el
vector gradiente es $\operatorname{grad}_gS=g^{-1}\omega$ y el flujo descendente
satisface $\dot\theta=-g^{-1}d_\theta S$. Un paso Euler finito en coordenadas no
es automáticamente invariante bajo reparametrizaciones no lineales.

## 1.2 Fisher del modelo

Para un modelo probabilístico y una distribución de evaluación declarada $\mu$:

$$
F_{ij}(\theta)=\mathbb E_{x\sim\mu,\ y\sim p_\theta(\cdot|x)}
\left[\partial_i\log p_\theta(y|x)\,\partial_j\log p_\theta(y|x)\right].
$$

Fisher es semidefinida positiva. La distribución de entradas y el panel finito
son parte de la definición operacional. Un promedio de productos de scores con
etiquetas observadas no se identifica sin más con esta expectativa sobre todas
las etiquetas del modelo.

En logits categóricos identificables, con Jacobiano $J_n$ y covarianza categórica
$\Sigma_n$ reducida:

$$
F=\frac1N\sum_{n=1}^N J_n^T\Sigma_n J_n.
$$

Si $\Sigma_n\succ0$, entonces $k\in\ker F$ implica $J_nk=0$ para todo $n$.
Los logits reducidos eliminan la redundancia aditiva softmax; no eliminan todas
las simetrías o degeneraciones posibles de una red.

## 1.3 Axioma de admisibilidad perspectival

Escribimos $\mathcal K_\theta=\ker F_\theta$ y su anulador

$$
\mathcal K_\theta^\circ
=\{\alpha\in T_\theta^*M:\alpha(k)=0\ \forall k\in\mathcal K_\theta\}.
$$

El axioma exige que una relevancia no distinga direcciones que Fisher considera
nulas:

$$
\boxed{\omega_p\in\mathcal K_\theta^\circ.}
$$

La variación perspectival debe cumplir también

$$
B_{ai}=\partial_{p^a}\partial_{\theta^i}S,\qquad
\boxed{B k=0\quad\forall k\in\mathcal K_\theta.}
$$

Si la admisibilidad de $\omega_p$ vale en un abierto de perspectivas, con
$\theta$ fijo y suavidad suficiente, su derivada en $p$ implica la segunda
condición. Se escribe explícitamente para comprobar también las implementaciones.
No se obtiene admisibilidad simplemente recortando valores numéricos a posteriori.

La geometría identificable vive en

$$
Q_\theta=T_\theta M/\mathcal K_\theta,\qquad
Q_\theta^*\simeq\mathcal K_\theta^\circ.
$$

Fisher induce en ese cociente una métrica no degenerada $\bar g_{F,\theta}$.
Para obtener campos suaves de cocientes se requieren hipótesis locales, como
rango constante; el cociente tangente puntual no es por sí solo un cociente
global de modelos por simetrías.

## 1.4 Familias lineales y no lineales

Para observables $o_\ell:M\to\mathbb R$ y coeficientes $c_\ell(p)$:

$$
S(\theta,p)=\sum_{\ell=1}^k c_\ell(p)o_\ell(\theta),\qquad
\omega=V c,\qquad B=J_c^T V^T,
$$

con $V=(d_\theta o_1,\ldots,d_\theta o_k)\in\mathbb R^{d\times k}$ y
$(J_c)_{\ell a}=\partial_a c_\ell\in\mathbb R^{k\times m}$. Aquí $c$ es
independiente de $\theta$. Si $V^Tk=0$ en el kernel Fisher, las combinaciones
son admisibles. El tensor inducido es

$$
h=J_c^T V^T C V J_c.
$$

Una familia no lineal usada en E12 toma, con panel y rasgos $f_n$ fijos:

$$
a_n(p)=\frac{e^{p^Tf_n}}{\sum_r e^{p^Tf_r}},\qquad
S_p(\theta)=\sum_n a_n(p)\log p_\theta(y_n|x_n).
$$

Definiendo $r_n=d_\theta\log p_\theta(y_n|x_n)$ y
$\mu_a(p)=\sum_n a_n(p)f_{na}$:

$$
\omega_p=\sum_n a_n r_n,\qquad
B_{ai}=\sum_n a_n(f_{na}-\mu_a)(r_n)_i.
$$

Si cada score anula $\ker F$ del mismo panel, $\omega$ y $B$ son admisibles
para todo $p$ finito. Ese argumento no garantiza por sí solo rango completo de $B$.
El tamaño efectivo $N_{\rm eff}=1/\sum_n a_n^2$ describe concentración de pesos;
no es un nuevo número de observaciones independientes.

## 1.5 Exactitud, Hessiana y derivada covariante

Para cada perspectiva fija, $\omega=d_\theta S$ es exacta:

$$
d_\theta\omega=0,\qquad \oint_\gamma\omega=0
$$

si $S$ está definido globalmente a lo largo del lazo. En contraste,

$$
(\nabla_j\omega)_i=\partial_j\omega_i-\Gamma^k_{ji}\omega_k
$$

puede ser no nula. Esta conexión es la del espacio del modelo si los índices
son paramétricos; la conexión del espacio de perspectivas se construye después
con $h$. $d_p\omega$, $d_\theta\omega$, la Hessiana y $\nabla\omega$ son objetos
distintos. La exactitud no implica curvatura nula ni holonomía trivial.
La dependencia histórica `relevance_covariant_derivative` sigue entre los
[faltantes documentales](../handoff/missing-sources.md); esta fórmula estándar
no reconstruye su implementación ausente.
