# Detalles de las referencias, antes de medir

Para las cotas superiores de casos sin mínimo conocido se fija una sola
curva sin usar el resultado nativo: en mass_face, normal algebraica de la
cara de26 índices; en los demás paneles, extinción monótona de k_piso según
la construcción de Q1. Los mínimos ya demostrados usan sus testigos
algebraicos de igualdad. No se seleccionan estados ni rayos por el valor
reportado por el instrumento bajo prueba.

La curva normal de mass_face tiene26 probabilidades iguales y una distinta.
Por tanto su imagen es una recta del simplex desde a0 a la cara uniforme.
Su longitud para cualquier M constante es exactamente la cuerda. Si esa
cuerda es el mínimo de L_end, la cota inferior y la superior coinciden.
En particular, para I/n vale ρ=1/(n√(n−1)). Para la perturbación isotrópica
de k=26 y los ε≤.1 fijados, la cuerda de esa cara es la menor y
ρ=sqrt(1−ε+ε/(n−1))/n. No contradice el caso de caras pequeñas de THEORY:
aquí la cara tiene más de n/2 índices. Esta observación es analítica, previa
a medir; los casos siguen contrastándose también con su dirección reportada.

En el argumento espectral Q3, las n muestras exponenciales generan todo el
espacio afín recorrido por a(su): su rango es g y las diferencias tienen
rango g−1. Así ker A anula no sólo las diferencias muestreadas, sino también
todo a'(su). Apoyar M en ese núcleo da una curva de longitud cero para todo
s, justificando el contraejemplo, no sólo una cota de muestras finitas.

Las entradas float de f se interpretan como racionales exactos para decidir
caras/empates. Las direcciones algebraicas se guardan por sus dos fracciones;
no se sustituye una normal exacta por un ángulo casi empatado. Al auditar el
ángulo retornado se promueven exactamente los floats cos(theta),sin(theta)
que utiliza el instrumento. Se conservan transiciones arbitrariamente tardías.

Las matrices PSD se definen por las fórmulas de cada caso; sus .npy son la
representación float normalizada a traza1. Desviaciones de PSD o identidades
al nivel de redondeo se registran con tolerancias congeladas, sin reparar
la matriz ni modificar la función rho_borde.py. La referencia usa normas
factorizadas en MP para evitar cancelación de un cuadrado casi cero.
