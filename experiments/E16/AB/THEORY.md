# Resolver estacionariedad mediante mínimos cuadrados

Sea L(x) la longitud poligonal, g=∇L y H=∇²L, en coordenadas físicas interiores.
AB fija c=max(1,|L(x₀)|) y resuelve con cotas

$$\min_{x\in C}\Phi(x),\qquad
F(x)=g_{AD}(x)/c,\quad\Phi(x)=\tfrac12\|F(x)\|_2^2.$$

El Jacobiano es J=H_AD/c. Su modelo local usa F(x+p)≈F(x)+Jp; TRF restringe
el paso mediante región de confianza y cotas. La opción x_scale='jac' usa
normas de columnas de J para adaptar escalas de variables. Esto trata escalas
dispares, sin asegurar que elimine direcciones casi singulares o degeneraciones.
El subproblema denso usa SVD; no se invierte ingenuamente una Hessiana singular.

En aritmética exacta, ∇Φ=Hᵀg/c². Un punto con ∇Φ≈0 puede seguir teniendo g≠0
si H es singular o casi singular. El éxito de mínimos cuadrados, una mejora
de su coste o un paso pequeño no demuestran estacionariedad de L.
Por eso AB desactiva ftol/gtol nativos y exige validación física final MP,
incluso si SciPy termina por xtol. Agotar evaluaciones se conserva inconcluso.

El objetivo de AB difiere de minimizar L: al reducir ||g||, L puede subir o
bajar. Su diferencia se conserva como descriptor, sin usarla como filtro de
aceptación. El descriptor `length_change` procede de una resta MP a precisión
de trabajo predeterminada fuera de las auditorías; no es una cota certificada.
Las longitudes por separado se contrastan MP80/120 con el umbral congelado.

## Residuo físico y observaciones

El criterio independiente es

$$r(x)=\frac{\|x-\Pi_C(x-g_{MP}(x))\|_\infty}{\max(1,|L_{MP}(x)|)}.$$

La normalización usa la longitud actual, a diferencia del c fijo del solver.
El solver intenta anular el gradiente completo; en un borde, el KKT proyectado
puede ser pequeño con g≠0. No se confunden esos objetivos y los puntos de borde
no son elegibles para la comparación restringida estacionaria de este estudio.

Sólo puntos aceptados distintos cuentan como observaciones de racha. Tres
valores verificados≤1e-7 consecutivos permiten solicitar parada; no garantizan
cumplimiento entre observaciones o en el futuro. C0 inicialmente verificado
puede quedar INITIAL_CONTROL, sin inventar una llamada o éxito nativo.

## Segundo orden

Se conserva la masa M heredada de Y/Z/AA desde la fuente S, incluso si cambia
la geometría. El diagnóstico resuelve

$$\mu(x)=\min_{v^TMv=1,\;g_{MP}^Tv=0}v^TH_{AD}v.$$

Se audita la dirección mínima con diferencias centrales MP80/120. Para gradiente
casi nulo se usa el espacio completo según el umbral1e-25; de otro modo,
la dirección del gradiente define un subespacio que también puede rotar.
Un cambio de μ no identifica por sí solo el mecanismo geométrico responsable.

El testigo de curvatura negativa MP y la clase relativa float son observaciones
distintas. Ninguna constituye certificado con intervalos. Sólo puntos con
primer orden y espectro PASS e interioridad son elegibles; los demás se
conservan como diagnósticos de los puntos devueltos. No se excluyen fallos.

AB cambia el punto inicial y el método respecto de AA. Es exploratorio sobre
los mismos datos sintéticos, sin confirmación independiente ni prueba causal
que aísle el escalado. Una raíz puede ser mínimo, máximo o silla. No se afirma
mínimo, silla exacta, geodésica ni convergencia por alcanzar un umbral numérico.

Los presupuestos de evaluaciones tampoco son equivalentes: una evaluación de
AB puede requerir una Hessiana y una SVD densa, frente a gradientes de L-BFGS-B.
Las tablas de costes separan llamadas residuales, Jacobianos/Hessianas y auditorías
MP. Reducir nfev no basta para afirmar superioridad temporal o computacional.
