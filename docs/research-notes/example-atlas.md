# Atlas de ejemplos y contraejemplos

Los ejemplos son identidades calculables o controles ya reportados. No se
reejecutaron en esta tarea. La [especificación E16](../../experiments/E16/mathematical_spec.md),
[su diseño](../../experiments/E16/DESIGN_FROZEN.md) y [su conclusión](../../experiments/E16/CONCLUSION.md)
contienen las referencias reproducibles. Aplicar la [errata](../../experiments/E16/ERRATA_v2.md)
al leer la referencia manual cuadrática del diseño original.

Tomar $\theta,p\in\mathbb R^2$, $p=(x,y)$ y $C=\operatorname{diag}(2,3)$,
salvo cuando se indique otra cosa.

| Caso | Objeto | Resultado esperado | Qué delimita |
|---|---|---|---|
| E01 | $S=\theta^1x+\theta^2y$ | $B=I$, $h=\operatorname{diag}(2,3)$ | Control SPD, sin confundirlo con Fisher estimada de una red |
| E02 | Carta $p=\varphi(q)$ invertible | $h_q=D\varphi^Th_pD\varphi$; rango conservado | Cambiar coordenadas no cambia la familia |
| E03 | Restricción $(x,y)=(t,2t)$ de E01 | $h_t=14$, rango 2→1 | Pérdida por restricción, no automáticamente coarse-graining |
| E04 | $S=\theta^1x$, restricción $(t,0)$ | Rango 1→1 | Menos coordenadas no implica menos rango geométrico |
| E05 | $S=\theta^1(x+y)$, $\pi=x+y$ | $h=2\begin{pmatrix}1&1\\1&1\end{pmatrix}$, $\bar h=2$ | Descenso válido, rango 1→1; vertical nula |
| E06 | E01 con $\pi=x$ | Norma vertical cuadrada 3; secciones $y=0$ e $y=x$ dan 2 y 5 | No existe el descenso tensorial pretendido |
| E07 | $S=\theta^1xy$, $\pi=x$ | En $x=1$, horizontales en $y=1,2$ dan 2 y 8 | Dependencia del representante; también hay obstrucción vertical |
| E08 | Producto $(\theta^1x)(\theta^2y)$ | $B=\begin{pmatrix}\theta^2y&\theta^1y\\\theta^2x&\theta^1x\end{pmatrix}$, rango 1 para factores no nulos | Los términos mixtos no pueden omitirse |
| E09 | $S_1=\theta\cdot p$, $S_2=-S_1+\theta^1$ | Suma: rango 0; cuadrática: rango 2 en el punto fijado | No hay monotonía universal frente a la suma |
| E10 | $F=\operatorname{diag}(2,0)$ y $S=\theta^1x$ | Contracción admisible $h_{xx}=1/2$ en dos cartas | La invariancia se justifica en el cociente |
| E11 | Mismo F, $S=\theta^2x$, $\theta=A\eta$, $A=\begin{pmatrix}1&1\\0&1\end{pmatrix}$ | Contracción ingenua 0 frente a 1/8 | Inadmisibilidad; no tensorialidad general de Moore–Penrose |

En E09, para $\Psi=(S_1^2+S_2^2)/2$, $\theta=(1,2)$ y $p=(1,1)$:

$$
B=\begin{pmatrix}6&2\\2&9\end{pmatrix},\qquad\det B=50.
$$

Ese valor es la referencia corregida, no la matriz manual fallida preservada
en el prerregistro. Es un contraejemplo algebraico, no evidencia de emergencia.

## Plano y esfera: controles de geometría diferencial

Un ejemplo expositivo de inmersión, sin reconstruir la implementación histórica
E9, toma $\theta\in\mathbb R^3$, $C=I_3$ y $S=\theta^Tc(p)$.
Entonces $\omega=c(p)$ y $h=(Dc)^TDc$.

- Para $c(u,v)=(u,v,0)$, se obtiene el plano: $h=I_2$ y $K=0$.
- Para $c(\vartheta,\varphi)=(\sin\vartheta\cos\varphi,
  \sin\vartheta\sin\varphi,\cos\vartheta)$, se obtiene
  $ds^2=d\vartheta^2+\sin^2\vartheta\,d\varphi^2$ y $K=1$, fuera de los
  polos de esa carta. El fallo de coordenadas en un polo no significa
  singularidad geométrica de la esfera.

Los controles históricos $K=0$ y $K=1$ se reportan en
[E12-C](../archive/import-2026-10-17/originals/E12C_conexion_curvatura_y_estado_RIPG.md)
y [E12-E](../archive/import-2026-10-17/originals/E12E_holonomia_control_derivado_y_cierre_E12.md).
La fórmula expositiva anterior es estándar y no se presenta como nueva ejecución.

## Rango y detección de código defectuoso

La [fuente fijada E16-C](https://github.com/jaiborojas-cloud/leviathan/blob/4fd7eb5790a7161731e22c238f29138cd66425ac/experiments/E16/C/CONCLUSION.md)
reporta controles de rango 0 (escalar constante en $p$), rango 1 (filas duplicadas)
y detección de omisión del término mixto. Conservar rango no basta para validar
una derivada: una implementación defectuosa puede seguir dando rango 2.
Los métodos de alta precisión tampoco constituyen certificados exactos globales.
