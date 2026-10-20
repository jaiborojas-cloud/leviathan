# 4. Observables geométricos y atribución por bloques

Fuentes: [contexto consolidado](../archive/import-2026-10-17/originals/RIPG_contexto_vigente_axioma.md),
[E11-N](../archive/import-2026-10-17/originals/E11N_atribucion_schur_y_estado_RIPG.md),
[cierre E13](../archive/import-2026-10-17/originals/E13_cierre_y_punto_de_partida_E14.md),
[E15-B8](../archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_E15-B8_cierre_y_E15-C_inicio.md)
y [prerregistro T2-A0 histórico](../archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_T2-A0_preregistro.md).
Estas definiciones no cambian estimandos ni umbrales de esos protocolos.

## 4.1 Ángulos y distancia entre matrices SPD

Para relevancias no nulas y admisibles en un mismo espacio dual:

$$
\cos\angle_C(\omega_1,\omega_2)=
\frac{\omega_1^TC\omega_2}
{\sqrt{\omega_1^TC\omega_1}\sqrt{\omega_2^TC\omega_2}}.
$$

Si una norma es cero, ese ángulo queda indefinido. No se imputa mediante una
división regularizada no declarada.

Una distancia afín-invariante usada para comparar métricas SPD es

$$
d_{\rm SPD}(G_0,G_1)=
\left\|\log(G_0^{-1/2}G_1G_0^{-1/2})\right\|_F
=\sqrt{\sum_a\log^2\lambda_a(G_1,G_0)}.
$$

Es invariante bajo una congruencia común. Comparar estados del modelo requiere
mantener identificada la misma familia perspectival. Esa distancia no es la
distancia geodésica entre dos puntos de $\mathcal P$, ni un escalar universal
de generalización. Distancias no lineales de bloques no se suman.

Para una trayectoria suave de matrices, su longitud SPD sería

$$
L_{\rm SPD}=\int\|G^{-1/2}\dot G G^{-1/2}\|_F\,dt.
$$

Una suma sobre checkpoints sólo la aproxima con un muestreo temporal adecuado;
pocos estados no determinan la longitud continua. No se presenta como resultado
experimental establecido: [estado de hipótesis E11-C](../archive/import-2026-10-17/originals/Estado_hipotesis_RIPG_E11C.md).

## 4.2 Área, energía y magnitud de curvatura

Para un dominio admisible $D_A$ de área intrínseca $A$:

$$
A=\int_{D_A}dA,\qquad
\mathcal E_K=\frac1A\int_{D_A}K^2dA,\qquad
\boxed{C_A=\sqrt{\mathcal E_K}.}
$$

$\mathcal E_K$ es promedio de energía curvatural; $C_A$ es su raíz cuadrática.
La integral sin normalizar mezcla magnitud y tamaño del dominio. Comparar a
igual área o radio intrínseco evita una parte de esa confusión, pero presupone
que los dominios existan y sean geométricamente admisibles en todos los estados.
Si no existen, el estimando no se fabrica reduciendo retrospectivamente el área.

## 4.3 Concentración espacial

Sea $e(p)=K(p)^2$ y $E=\int_{D_A}e\,dA>0$. La forma continua de la fracción
máxima de energía en el $q$ de área es

$$
\Lambda_q=\frac1E
\sup_{U\subseteq D_A,\ \operatorname{Area}(U)=qA}\int_U e\,dA.
$$

Se ordena por densidad de energía y se permite fracción de área en los empates.
Las implementaciones históricas fijan interpolación fraccional y convergencia
multifuente; una lista de celdas sin ponderación intrínseca no es equivalente.
La fracción mínima de área que contiene $\beta$ de la energía puede escribirse

$$
f_\beta=\inf\{q:\Lambda_q\ge\beta\},\qquad \beta=0.5,0.9.
$$

La participación efectiva espacial es

$$
\boxed{R_{\rm eff}=
\frac{(\int_{D_A}K^2dA)^2}{A\int_{D_A}K^4dA}.}
$$

Bajo integrabilidad y energía no nula, Cauchy–Schwarz da $0<R_{\rm eff}\le1$;
un valor menor describe mayor concentración. Si $K\equiv0$, aparece $0/0$:
queda indefinido salvo convención de protocolo, no se sustituye automáticamente
por 0 o 1. Mayor concentración no equivale a mayor magnitud ni a mejor aprendizaje.

## 4.4 Schur: aditividad válida de las métricas

Fijar una escala regularizadora común $\alpha$ para los alcances anidados:

$$
g=F+\alpha H=
\begin{pmatrix}A&D\\D^T&E\end{pmatrix},\qquad B=(B_0\ B_1).
$$

Si $g\succ0$, $A\succ0$ y su complemento de Schur $\mathcal S=E-D^TA^{-1}D$
es SPD. Con $\mathcal R=B_1-B_0A^{-1}D$:

$$
G_{0\cup1}=G_0+\Delta G_{1|0},\qquad
G_0=B_0A^{-1}B_0^T,\qquad
\boxed{\Delta G_{1|0}=\mathcal R\mathcal S^{-1}\mathcal R^T\succeq0.}
$$

El bloque fuera de diagonal se llama aquí $D$ para no confundirlo con la cométrica
$C$. La escala debe ser la misma: recalcular $\lambda_{\max}$ por alcance cambia
el problema e invalida la lectura de diferencia como contribución de esa partición.
La atribución depende de los bloques declarados; cambios de carta que mezclan
bloques también cambian su interpretación operacional.

## 4.5 Participación oculta

Para dimensión perspectival $m$ y $G_{\rm full}\succ0$:

$$
\eta=\frac1m\operatorname{tr}
(G_{\rm full}^{-1}\Delta G_{\rm hidden|output}).
$$

La fuente usa $m=2$, de ahí su factor $1/2$. Si
$0\preceq\Delta G\preceq G_{\rm full}$, sus autovalores generalizados están
en $[0,1]$ y $0\le\eta\le1$. La traza es invariante bajo congruencias comunes
en perspectivas, pero depende de regularización, panel, funcional y partición.
La covariancia no la convierte en un descriptor absoluto canónico.

## 4.6 Shapley y profundidad: alcance de la documentación

[El estado E15-B1](../archive/import-2026-10-17/originals/Leviathan_RIPG_estado_E15-B1_2026-09-24.md)
reporta atribuciones Shapley $\phi_\ell$, participaciones $s_\ell$ y concentración
$H_\phi$, además de eficiencia $\sum_\ell\phi_\ell=C_A(\mathrm{full})$.
La definición matemática estándar, para un juego explícito $v$ con $L$ bloques, es

$$
\phi_\ell=\sum_{U\subseteq\{1,\ldots,L\}\setminus\{\ell\}}
\frac{|U|!(L-|U|-1)!}{L!}
\left[v(U\cup\{\ell\})-v(U)\right].
$$

Su eficiencia general es $\sum\phi_\ell=v(\mathrm{full})-v(\varnothing)$.
Es una identidad de atribución, no causalidad; contribuciones negativas son posibles.
La nota recuperada no explicita todas las reglas de normalización de $s_\ell$
y $H_\phi$ con $\phi_\ell$ negativos ni el tratamiento del juego vacío.
No se infieren esas reglas de tablas o nombres; para reproducir exactamente esas
cantidades hace falta la definición operacional completa. Se conserva este faltante
en [fuentes](fuentes.md), sin reemplazarlo por una entropía o normalización supuesta.
