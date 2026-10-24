# AH · testigos de longitud al borde

Para a(P)=softmax(fP), g=JᵀMJ. El segmento y la semirrecta desplazada usan
la misma fórmula β=a(z−media(z)). En el segmento z=fQ, a=softmax(tz).
En la cola b=fQ,z=fu,a=softmax(b+sz). El soporte S maximiza z y el extremo
es a∞_S=softmax(b_S). Cambiar Q cambia el extremo dentro de una arista.
Una dirección casi empatada acaba en otro extremo: debe integrarse también
su transición tardía. Se separan ramas de arista de sectores abiertos.

Con z máximo0 y gaps δ_i=−z_i>0 fuera de S, Z_S=Σ_Sexp(b),
a_i(s)≤exp(b_i−logZ_S−δ_i s). Se tiene ||β||₁≤2Σ_fuera a_iδ_i.
Por tanto la longitud restante desde U es≤2√λmax(M)Σ_fuera
exp(b_i−logZ_S−δ_iU). Se conserva esta cota de cola y no se presenta el
corte como llegada al borde. Las operaciones float/MP no son intervalos.

Cada camino validado llega al borde de la completación; su longitud es una
cota superior de d_borde. Una búsqueda finita sólo estima el mínimo global:
hatρ1=min candidatos validados. Incluir el mismo camino Q=0 produce
hatρ1≤ρ0 validada; d_borde≤hatρ1 no depende de convergencia del optimizador.
El resultado describe este conjunto acotado y presupuesto, no el ínfimo
sobre todos los quiebres. Los40 d triangulares se usan para evaluación,
no como objetivos ni inicializaciones. AF conserva d real UNKNOWN.

El mapa q=BQ se define con diferencias de rasgos; bajo P=Az+b, B→BA y el
origen físico se transforma. Esto permite comparar las mismas curvas y
el mismo dominio acotado, no dos cajas arbitrarias en coordenadas naturales.
