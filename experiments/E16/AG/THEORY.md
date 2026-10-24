# AG · métrica, borde y cartas

a(P)=softmax(fP), J_ni=a_n(f_ni−μ_i), g=JᵀMJ. Se importa el geometry.py
autorizado intacto. ρ=min_u∫√((Ju)ᵀM(Ju))ds; las direcciones representan
semirrectas, por lo que su normalización no cambia la integral. Un cambio
afín biyectivo de carta preserva este conjunto si se transforma el origen.
La aproximación con una rejilla angular no es exactamente invariante.

En una familia finita con M SPD, la inmersión tiene completación con borde.
Toda semirrecta da una curva hacia ese borde; de ahí d_borde≤ρ. El tiempo
de alcanzar ||P||∞=150 es otra cosa: puede ser ANTERIOR al borde real y no
es una cota superior demostrada de d_borde. La exponencial angular finita
además puede omitir la dirección más corta. Q1 es una comparación falsable
de instrumentos, no una nueva prueba del teorema de la cota.

## Triángulos de respuesta conocida

D agrupa nueve componentes por vértice, E=D/9 y w=softmax(FP), con F3×2
no colineal. a=Ew, W=EᵀME, y la imagen es todo el triángulo abierto.
En q=(w0,w1), w=(q0,q1,1−q0−q1), la métrica H=NᵀWN es constante.
Las geodésicas son segmentos rectos en w. d_borde es la distancia mínima
del baricentro a los tres segmentos de frontera, proyectados con W.

Desde P0=0, una semirrecta tiene como extremo un vértice si el logit máximo
es único, o el punto medio de una arista si los dos máximos empatan. Sus
longitudes son al menos la distancia recta al extremo. Para los seis extremos
hay una dirección normal a la arista opuesta/en cuestión cuyos otros dos
logits empatan: w(s) es una recta y realiza exactamente esa distancia.
Por tanto ρ es el mínimo de esas seis distancias. Los mínimos en aristas
requieren empate EXACTO: una dirección casi empatada puede recorrer además
una arista mucho más tarde. Se incluyen normales de la envolvente y se
parten las integrales en las escalas de separación de logits; no confiar en
una cuadratura que parezca convergente pero haya omitido ese tramo tardío.

Es una subfamilia plana y degenerada por duplicación del panel, deliberada
para disponer de respuesta analítica, no una reproducción general de la
curvatura de T2. La métrica27×27 es SPD pese al rango2 de Q. El espectro de
M y la cota previa de d_borde fijan escalas sin observar escapes.
Los40 estados AF usan sus M/f originales; sus bordes reales no se identifican
con la frontera del triángulo ni con un escape finito.
