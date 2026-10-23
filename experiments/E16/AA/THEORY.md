# Tolerancia, continuación y curvatura restringida

AA continúa los puntos de Z sin refinar la malla. Para una curva con variables
interiores x, longitud L y caja C, el residuo físico es

$$r(x)=\frac{\|x-\Pi_C(x-\nabla L(x))\|_\infty}{\max(1,|L(x)|)}.$$

En el interior, un residuo pequeño limita componentes del gradiente; no las
hace exactamente nulas. Exigir cien veces menos residuo no garantiza que
L-BFGS-B encuentre un punto admisible dentro de 4800 iteraciones. AA conserva
la salida final, sin promoverla a estacionaria si no cumple el criterio.

La comparación de segundo orden mantiene la masa M de Z/Y:

$$\mu(x)=\min_{v^TMv=1,\;g(x)^Tv=0}v^TH(x)v,\qquad
H=\nabla^2L,\quad g=\nabla L.$$

Con base B ortonormal del núcleo de gᵀ, se resuelve

$$B^THB\,w=\mu\,B^TMB\,w.$$

Para cada arista de peso fijo δ, la masa P1 aporta
δ/6 [[2,1],[1,2]] por componente; los extremos están fijos. No se sustituye M
por identidad ni se recalcula con la nueva geometría.

Al continuar cambian tanto H como la dirección de g y, por tanto, el subespacio
g⊥. Reducir ||g|| no estabiliza por sí mismo ese subespacio: el proyector
I−ggᵀ/(gᵀg) depende de su dirección. Un cambio en μ no identifica cuál de
estos mecanismos lo produce. Tampoco un μ positivo implica mínimo global,
ni descarta direcciones de primer orden, otros subespacios o mínimos ajenos.

La clase espectral float usa un umbral relativo al espectro completo restringido.
Por separado, una diferencia central MP sobre una dirección auditada puede
mostrar curvatura negativa local aun cuando la clase float sea NEAR_ZERO.
Por ello se conservan ambas columnas; no se sustituyen una por otra.
Un testigo MP es numérico, no una cota con intervalos.

La pregunta estricta sólo puede responderse para puntos que cumplan primer
orden, validación espectral e interioridad. Si las curvas cuadráticas agotan
el presupuesto sin alcanzar 1e-7, sus espectros se informan como diagnósticos
de los puntos devueltos. No se concluye persistencia ni desaparición de una
silla estacionaria a esa tolerancia. C0 controla casos analíticamente planos;
no valida por sí solo que el optimizador resuelva las curvas cuadráticas.

AA cambia inicio, umbral, gtol y ftol: es una continuación exploratoria
prospectiva, no un ensayo que aísle causalmente sólo la tolerancia. Los datos
sintéticos y las familias siguen siendo los mismos; no hay muestra independiente.
