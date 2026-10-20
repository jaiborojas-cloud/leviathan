# 5. Composicionalidad y coarse-graining perspectival

Fuentes: [propuesta histórica G](../archive/import-2026-10-17/RUTAS_INVESTIGACION_texto_extraido.md),
[especificación E16](../../experiments/E16/mathematical_spec.md),
[fe de erratas](../../experiments/E16/ERRATA_v2.md) y
[cierre E16-B](../../experiments/E16/B/CONCLUSION.md).
La propuesta histórica es una hipótesis de investigación; pullback y regla de
cadena son identidades matemáticas, no descubrimientos empíricos.

## 5.1 Cuatro operaciones distintas

| Operación | Mapa | Interpretación |
|---|---|---|
| Carta invertible | $p=\varphi(q)$ difeomorfismo local | Misma familia y geometría en otra representación |
| Subfamilia | $p=\varphi(q)$, dimensión menor | Pullback a una restricción declarada |
| Agregación | $q=\pi(p)$ no invertible | Requiere condiciones de descenso para heredar un tensor |
| Composición escalar | $S_{\rm macro}=\Psi(S_1,\ldots,S_k)$ | Nueva relevancia por regla de cadena |

No toda composición es coarse-graining; no todo mapa no invertible define una
métrica sobre su espacio de llegada. En este capítulo los mapas de perspectivas
son independientes de $\theta$ y la cométrica base se fija respecto de $p$.

## 5.2 Restricción y conservación de rango

Con $J=D\varphi$ de forma $m\times n$:

$$
h_q=J^Th_pJ,\qquad
\operatorname{rank}h_q=\operatorname{rank}(B_p^TJ)
\le\min(n,\operatorname{rank}h_p).
$$

La igualdad usa positividad de la cométrica en la imagen admisible. Se conserva
el rango si $\operatorname{im}(B_p^TJ)=\operatorname{im}B_p^T$. Una restricción
puede eliminar direcciones activas o sólo redundantes; dimensión menor no implica
pérdida estricta de rango. En cambios de carta invertibles, el rango se conserva.

## 5.3 Descenso a un cociente

Para una submersión sobreyectiva $\pi:\mathcal P\to\mathcal Q$, se busca
$\bar h$ tal que

$$
h=\pi^*\bar h.
$$

Se requiere que $h$ sea horizontal: $h(v,\cdot)=0$ para toda dirección vertical
$v\in\ker D\pi$, y que la evaluación sobre levantamientos sea independiente
del representante en cada fibra. Bajo las hipótesis de un cociente suave y esa
propiedad básica, define

$$
\bar h_q(u,w)=h_p(\widetilde u,\widetilde w),\qquad\pi(p)=q.
$$

La horizontalidad elimina la elección de levantamiento; la independencia de
representante elimina la elección de $p$. Si $\ker h=\ker D\pi$, $\bar h$
es positiva definida. Como $D\pi$ es sobreyectiva:

$$
\operatorname{rank}(\pi^*\bar h)=\operatorname{rank}\bar h.
$$

Las coordenadas eliminadas ya eran geométricamente nulas en este descenso.
Un cociente por minimización de energía con elección horizontal es otra
construcción, no la igualdad tensorial anterior ni algo automático.

Si $S(\theta,p)=\bar S(\theta,\pi(p))$ y la cométrica es la misma a lo largo
de las fibras, entonces $B=D\pi^T\bar B$ y el tensor inducido factoriza. Si
$C$ dependiera del representante, la factorización del escalar no bastaría.

## 5.4 Composición escalar y todos los términos mixtos

Para $\Psi:\mathbb R^k\to\mathbb R$ sin dependencia explícita adicional en
$\theta$ o $p$, escribir $\Psi_\ell=\partial_\ell\Psi$ y
$\Psi_{\ell r}=\partial_r\partial_\ell\Psi$:

$$
\omega_{{\rm macro},i}=\sum_\ell\Psi_\ell\omega_{\ell,i},
$$

$$
\boxed{B_{{\rm macro},ai}=
\sum_\ell\Psi_\ell B_{\ell,ai}
+\sum_{\ell,r}\Psi_{\ell r}(\partial_aS_r)\omega_{\ell,i}.}
$$

Los coeficientes $\Psi_\ell(S(\theta,p))$ no son constantes. Derivar primero
en $p$ exige después su dependencia en $\theta$; derivar primero en $\theta$
exige después su dependencia en $p$. Ambas rutas dan la fórmula completa.
Si $\Psi$ depende explícitamente de $\theta,p$, se añaden también sus términos
explícitos: esta fórmula no cubre ese caso sin ampliación.

Una mezcla afín con coeficientes constantes sólo conserva el primer sumando;
puede sufrir cancelaciones. En composiciones no lineales no hay una ley general
de disminución del rango respecto de cada componente o respecto de su suma.
Siempre $\operatorname{rank}h_{\rm macro}\le\min(m,d)$ en el caso SPD declarado.

## 5.5 Ejemplos y contraejemplos calculables

Tomar $\theta,p\in\mathbb R^2$ y $C=\operatorname{diag}(2,3)$:

- $S=\theta^1x+\theta^2y$: $B=I$ y $h=\operatorname{diag}(2,3)$.
  Restringir a $(x,y)=(t,2t)$ da $h_t=14$ y rango $2\to1$.
- $S=\theta^1x$ tiene rango 1 antes y después de restringir a $(t,0)$.
- $S=\theta^1(x+y)$ y $\pi=x+y$ dan
  $h=2\begin{pmatrix}1&1\\1&1\end{pmatrix}=\pi^*(2\,dq^2)$: rango $1\to1$.
- Para la familia $h=\operatorname{diag}(2,3)$, $\pi=x$ no permite descenso:
  la dirección vertical $\partial_y$ tiene norma cuadrada 3. Las secciones
  $y=0$ e $y=x$ inducen 2 y 5 respectivamente; son elecciones adicionales.
- $S_1=\theta^1x+\theta^2y$, $S_2=-S_1+\theta^1$ tienen suma con $B=0$.
  Para $\Psi=(S_1^2+S_2^2)/2$, en $\theta=(1,2),p=(1,1)$:
  $B=\begin{pmatrix}6&2\\2&9\end{pmatrix}$, determinante 50 y rango 2.

El último valor incorpora la fe de erratas de E16; no se reproduce su referencia
manual fallida como fórmula vigente. Los contraejemplos delimitan afirmaciones
universales; no prueban emergencia ni una ventaja predictiva.
