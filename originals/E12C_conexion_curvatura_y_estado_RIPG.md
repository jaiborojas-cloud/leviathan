# E12-C — conexión y curvatura del espacio de perspectivas

## Objetivo

E12-C calcula la conexión de Levi-Civita, el tensor de Riemann y la curvatura gaussiana del campo construido en E12-B:

\[
G_\rho(P;\theta)
=B(P)\left(F_\theta+\rho\lambda_{\max}(F_\theta,I)I\right)^{-1}B(P)^T,
\qquad \rho=10^{-4}.
\]

Se mantienen los cuatro atlas iniciales fijados en E12-B: reparto 0, semilla 0, condiciones `true/random`, para `digits` y Wisconsin.

## Derivación usada

Sea

\[
M=\left(F+\rho\lambda_{\max}I\right)^{-1},
\qquad
G_{ij}=\langle B_i,B_j\rangle_M.
\]

Como \(F\) y \(M\) son constantes respecto de \(P\) en cada atlas, se calcularon analíticamente las derivadas de las ponderaciones exponenciales hasta tercer orden. Si

\[
C_{ik}=\partial_kB_i,
\qquad
D_{ikl}=\partial_l\partial_kB_i,
\]

entonces

\[
\partial_kG_{ij}
=\langle C_{ik},B_j\rangle_M+
\langle B_i,C_{jk}\rangle_M,
\]

y

\[
\begin{aligned}
\partial_l\partial_kG_{ij}
={}&\langle D_{ikl},B_j\rangle_M
+\langle C_{ik},C_{jl}\rangle_M\\
&+\langle C_{il},C_{jk}\rangle_M
+\langle B_i,D_{jkl}\rangle_M.
\end{aligned}
\]

Esta ruta evita estimar la curvatura primaria dividiendo diferencias ruidosas por \(h^2\). Las diferencias finitas se conservan únicamente como control independiente.

La conexión se obtuvo mediante

\[
\Gamma^k_{ij}
=\frac12G^{k\ell}
\left(\partial_iG_{j\ell}+\partial_jG_{i\ell}-\partial_\ell G_{ij}\right).
\]

Se usó la convención

\[
R^l{}_{ijk}
=\partial_j\Gamma^l_{ik}-\partial_k\Gamma^l_{ij}
+\Gamma^m_{ik}\Gamma^l_{mj}
-\Gamma^m_{ij}\Gamma^l_{mk}.
\]

En dos dimensiones,

\[
\boxed{
K=\frac{R_{1212}}{\det G},
\qquad R_{\mathrm{scalar}}=2K.
}
\]

Por ello el tensor de Riemann completo queda determinado por \(K\) y \(G\).

## Resultados de curvatura

Se evaluaron 25 centros por atlas sobre

\[
(P^1,P^2)\in\{-0.4,-0.2,0,0.2,0.4\}^2.
\]

| Datos | Régimen | \(K_{\min}\) | Mediana de \(K\) | \(K_{\max}\) | Signos en 25 puntos |
|---|---|---:|---:|---:|---:|
| Digits | true | −3.169 | **−1.271** | −0.306 | 25 negativos |
| Digits | random | −0.00759 | **−0.00574** | −0.00248 | 25 negativos |
| Wisconsin | true | −0.0220 | **+0.00376** | +0.0383 | 18 positivos, 7 negativos |
| Wisconsin | random | −0.0245 | **−0.00375** | −0.00050 | 25 negativos |

La conclusión inmediata es doble:

1. el campo de E12-B no es plano;
2. no existe un signo universal de curvatura entre tareas y regímenes.

`digits-true` presenta curvatura hiperbólica negativa de magnitud sustancial en todo el vecindario. `digits-random` es también negativo, pero cerca de plano. Wisconsin `random` permanece ligeramente negativo; Wisconsin `true` contiene regiones positivas y negativas.

## Conexión y curvatura en el centro

Los coeficientes siguientes corresponden a la carta operacional \((P^1,P^2)\) y a \(P=0\). No son invariantes escalares.

| Datos/régimen | \(\Gamma^1_{11}\) | \(\Gamma^1_{12}\) | \(\Gamma^1_{22}\) | \(\Gamma^2_{11}\) | \(\Gamma^2_{12}\) | \(\Gamma^2_{22}\) | \(K(0)\) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Digits true | 0.486 | 0.343 | −0.300 | 0.281 | −0.552 | 0.559 | **−1.8886** |
| Digits random | 0.102 | 0.053 | −0.172 | −0.069 | −0.045 | −0.038 | **−0.00759** |
| Wisconsin true | 0.008 | 0.265 | −0.210 | −0.094 | 0.549 | 0.928 | **+0.00228** |
| Wisconsin random | 2.343 | −0.164 | −0.194 | −1.789 | 0.642 | 0.700 | **−0.00397** |

En el centro, \(R_{1212}=K\det G\) toma respectivamente −0.334, −58.779, +0.0669 y −51.059. Estos componentes dependen de la carta; el cociente \(K=R_{1212}/\det G\) es la cantidad escalar comparable.

## Convergencia por diferencias finitas

La curvatura analítica en \(P=0\) se comparó con diferencias centrales.

| Caso | Error escalado, \(h=0.10\) | Error escalado, \(h=0.05\) | Reducción |
|---|---:|---:|---:|
| Digits true | 1.22 % | 0.304 % | 4.0× |
| Digits random | \(4.65\times10^{-5}\) | \(1.17\times10^{-5}\) | 4.0× |
| Wisconsin true | 7.57 % | 1.69 % | 4.5× |
| Wisconsin random | \(1.45\times10^{-4}\) | \(3.82\times10^{-5}\) | 3.8× |

La reducción aproximadamente cuádruple al dividir el paso entre dos es la firma esperada de convergencia de segundo orden. Wisconsin `true` converge más lentamente por la anisotropía métrica alta observada en E12-B; el método analítico evita que esa dificultad determine el resultado principal.

## Control de cambio de carta

Se reconstruyó independientemente la familia usando

\[
P=TQ,
\qquad
T=\begin{pmatrix}1&0.35\\-0.2&0.8\end{pmatrix}.
\]

Los observables se transformaron como \(f_Q=f_PT\), se recalcularon \(B_Q\), sus derivadas, \(G_Q\), \(\Gamma_Q\) y \(K_Q\), y se compararon con

\[
G_Q=T^TG_PT,
\]

y, al ser lineal la transformación,

\[
(\Gamma_Q)^a{}_{bc}
=(T^{-1})^a{}_rT^i{}_bT^j{}_c
(\Gamma_P)^r{}_{ij}.
\]

Controles máximos:

| Control | Error máximo |
|---|---:|
| \(|K_Q-K_P|\) | \(2.19\times10^{-8}\) |
| Error relativo de transformación de \(\Gamma\) | \(1.41\times10^{-7}\) |

La curvatura calculada se comporta como escalar y la conexión sigue su ley no tensorial correcta.

## Auditoría numérica

| Control | Resultado |
|---|---:|
| Puntos de curvatura | 100 |
| Residuo máximo del solucionador | \(5.00\times10^{-8}\) |
| Autoprueba plana | \(K=0\) |
| Autoprueba de esfera unitaria | \(K=1\) |

## Estado de RIPG tras E12-C

E12-C demuestra que la familia admisible de E12-B induce una geometría intrínseca no plana y computable. La curvatura ya no es una metáfora ni una consecuencia asumida de Fisher: es la curvatura del campo de relevancia perspectival explícitamente declarado.

No obstante, deben conservarse límites precisos:

- la curvatura depende de la familia \(S_P\), del panel, de \(H\), de \(\rho\) y del estado \(\theta\);
- sólo se evaluaron cuatro atlas representativos;
- el contraste `true/random` observado no constituye todavía una ley ni una prueba causal;
- la coexistencia de signos en Wisconsin descarta una lectura universal como “aprender produce siempre curvatura negativa”.

La afirmación vigente es:

> El entrenamiento puede inducir campos de perspectivas con perfiles de curvatura intrínseca claramente distintos, pero el signo y la magnitud dependen de la tarea y del régimen.

## Siguiente paso natural

E12-D debe evaluar la evolución

\[
K_0(P),\qquad K_t(P),\qquad \Delta K(P)=K_t(P)-K_0(P)
\]

en semillas y repartos emparejados. La comparación primaria no debería ser sólo el promedio firmado de \(K\), pues Wisconsin contiene cambio de signo. Conviene registrar al menos:

1. curvatura mediana firmada;
2. energía de curvatura \(\int K^2\,dA\);
3. fracción de área con \(K>0\) y \(K<0\);
4. heterogeneidad espacial de \(K(P)\).

La holonomía permanece reservada para E12-E como control derivado de esta curvatura.

## Reproducción

El paquete incluye la derivación analítica, el agregador, las tablas de \(G\), \(\Gamma\), \(K\), los controles de diferencias finitas y carta, y las dependencias de E12-A/B. Reutiliza los estados de E11-O.
