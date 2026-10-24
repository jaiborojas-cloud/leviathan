# Lema adicional · cota universal de Fisher y qué parte queda libre

Demostración teórica adicional a [THEORY](THEORY.md); no cambia reglas,
umbrales ni diseño. Se deriva antes del cierre del informe, sin usar estados
empíricos. Su auditoría desde arrays sintéticos es suplementaria.

Con las notaciones de Q6, B=W¹/²A y Z=E W⁻¹/²,

    M_gamma=Z B(BᵀB+gamma I)⁻¹Bᵀ Zᵀ=Z H_gamma Zᵀ,
    0<=H_gamma<=I.

En consecuencia, para TODO rango de A y cualquier gamma>0,

    0<=M_gamma<=D=N diag((1-p_n,y)/p_n,y),
    M_nn<=N (1-p_n,y)/p_n,y,
    tr M<=N sum_n (1-p_n,y)/p_n,y.

La igualdad M0=D sin ridge requiere que H0 actúe como identidad sobre
las filas relevantes de Z. Rango(A)=2N es condición suficiente, no necesaria
para esa igualdad sobre R. Con ridge>0, H es contracción estricta en cada
modo no nulo. Diagonalidad no se deduce de esta desigualdad Loewner.

Puede escribirse exactamente, si p_n,y<1,

    M_nn=N (1-p_n,y)/p_n,y · ell_n,  0<=ell_n<=1,
    ell_n=||H_gamma¹/² z_n||²/||z_n||².

ell_n es un leverage regularizado del score de esa observación. Depende del
espacio alcanzable por los Jacobianos, sus escalas relativas y el espectro
Fisher/ridge. No se calcula sólo con p_n,y. Suprimir otros grados de libertad
no está autorizado por observar colapso o diagonalidad de M.

Cuando M≈Mkk e_k e_kᵀ en un panel de caras pequeñas,

    rho≈(sqrt(N)/n) sqrt(((1-p_k)/p_k) ell_k).

Esta fórmula separa un factor de confianza forzado y un factor de red. Aun
cuando sea muy precisa la aproximación coordenada, ell_k podría no ser1.
Los límites de confianza perfecta y ridge despreciable no siempre conmutan:
si desaparecen modos Fisher, no se puede invocar sin control el caso sin ridge.

Por monotonía Loewner, rho(M,f)<=rho(D,f); es una cota superior conceptual
que aún depende del vector COMPLETO de confianzas y f. No hay una cota inferior
positiva sólo a partir de confianza mínima: filas score idénticas producen
M proporcional a11ᵀ y G=0, con la misma confianza arbitraria en todos los puntos.

La normalización por tr M cambia la pregunta. En el límite coordenado,
rho_tilde≈1/n, mientras rho sin normalizar≈sqrt(tr M)/n. La primaria DIN-C1
usa log rho sin normalizar. Antes del colapso, rho incorpora tanto escala como
forma visible HMH y f; la masa constante ccᵀ es invisible a J. No se debe
identificar tr M ni una sola confianza con todo el campo métrico.
