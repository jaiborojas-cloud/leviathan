# I1 · todas las semirrectas, normales y límite unilateral

Suponer f de rango afín2 y M PSD, fija e independiente de P. Se interpreta
su norma como seminorma si M es singular. Las longitudes son finitas:
cada componente softmax a_i(su) es unimodal (la media de logits direccionales
crece), de modo que su variación total≤2; la norma métrica queda dominada
por sqrt(lambda_max(M)) sum_i|a'_i|. No hace falta una métrica invertible.

## Partición exacta del espacio de direcciones

Toda dirección no nula expone una cara del polígono conv{f_i}. En2D y rango
afín2, es un vértice o una arista. Las que exponen sólo un vértice forman su
cono normal abierto. Cada arista tiene una única normal exterior positiva
como dirección proyectiva. Si hay coordenadas f repetidas, un vértice puede
contener varios índices y a_infinito es uniforme sobre ese grupo; no deja
de ser un rayo genérico hacia un vértice geométrico.

Por partición (no por continuidad angular), exactamente:

    inf_todas L = min(inf_conos_abiertos L, min_aristas L(normal)).

Ésta es rho_caras. La optimización finita de v2 estima esos ínfimos; la
identidad de conjuntos no certifica que un optimizador local los encuentre.
Puntos interiores a una arista pertenecen TODOS al soporte uniforme final.
Una tolerancia positiva que fusione casi colineales puede cambiar el objeto
discontinuamente; I2 usa membresía racional exacta y alertas separadas.

## Límite al borde de un cono

Sea nu normal exterior de la arista S y w tangencial, dirigido hacia uno
de sus vértices V. Por homogeneidad se estudia u_e=nu+e w, e>0. En tiempo
s acotado, a(su_e)→a(snu). En la escala tardía t=e s, todas las componentes
fuera de S ya son exponencialmente pequeñas y las de S tienden a

    b_i(t)=1[i∈S] exp(t f_i·w)/sum_{j∈S} exp(t f_j·w).

Arranca en el uniforme de S y termina en el uniforme de V. Separar las
integrales en s=e^(-1/2) permite pasar al límite: fuera de S hay un gap
positivo fijo y su error integrado es exponencial; en la primera parte la
perturbación tangencial contribuye O(sqrt(e)), y en la segunda el t inicial
tiende a0. Las normas se controlan por la variación total finita y los gaps.
Así,

    lim_e↓0 L(u_e)=L(nu)+L_S→V.

Se aplica a cada lado. La normal exacta es estrictamente más corta que ese
límite SI Y SÓLO SI la cola de arista tiene longitud positiva. Para M PSD,
la cola es0 exactamente si M^(1/2)b'(t)=0 casi en todas partes (y por
regularidad, en todo t finito). La cuerda da

    L_S→V ≥ ||a_V−a_S||_M.

Una cuerda positiva es suficiente para un salto. Una cuerda0 NO basta para
anular la longitud en una cara con varios puntos: puede haber variación en
la proyección pese a coincidir los extremos. Si S sólo tiene dos posiciones
distintas, la curva es un segmento y la cola SÍ coincide con la cuerda.
La estricta ventaja local de una normal no asegura que gane al mejor cono
no adyacente. Se toma el mínimo global de candidatos de ambos tipos.

## D2 y triángulos

Para M=e_k e_kᵀ, L(u)=TV(a_k). En una cara máxima S que contiene k,
a_k aumenta monótonamente de1/n a1/|S|. En una dirección genérica de
extinción monótona vale1/n. En las geometrías D2 sin vértices duplicados:

    rho_vert=1/n,
    rho_caras=min(1/n,1/m_k−1/n).

Si k es interior se omite el segundo término. mass_face n27,m26 produce
rho_caras=1/702, frente a rho_vert=1/27: factor26. No se generaliza la fórmula
rho_vert=1/n a grupos de vértices duplicados arbitrariamente grandes.

En los triángulos AG hay tres grupos iguales y el origen es el baricentro
en probabilidades de grupo. La imagen es un triángulo plano en la seminorma
M. Las medianas son semirrectas porque los dos logits subdominantes empatan,
así que rho_vert es la menor distancia al vértice. Los normales de arista
son también segmentos hacia puntos medios. Si v es un vértice y m el punto
medio opuesto, m−a0=−(v−a0)/2; por homogeneidad de cualquier seminorma,

    rho_caras = rho_vert/2.

d_borde es la proyección mínima a segmentos de arista y puede ser menor
que la distancia al punto medio: d_borde≤rho_caras, no igualdad universal.
Por ello exigir rho_vert=v1 cuando v1 acertó rho_caras contradice esta
referencia. Se preserva ese FAIL de compatibilidad literal y su explicación.

## Restos de integración logarítmica

Con gaps delta_i≥0, multiplicidades m_i y soporte máximo S,
w_i=m_i exp(-delta_i s)/Z(s), Z≥m_S. Se obtiene

    ||w'||1 ≤ 2 sum_i w_i delta_i.

En una representación por contrastes con norma espectral lambda,
la integral restante desde T cumple

    resto(T) ≤ 2 sqrt(lambda)/m_S sum_fuera m_i exp(-delta_i T).

No necesita monotonicidad individual. Normalizar max(delta)=1 da para
el intervalo inicial[0,t0] la cota2 sqrt(lambda)t0. En x=log s la velocidad
es la norma de w*(media(s delta)−s delta), que conserva transiciones muy
tardías sin restar velocidades casi iguales en s enorme.
Los restos son cotas analíticas para la métrica PSD ideal; su evaluación,
la corrección de redondeo PSD y quad en esta implementación son flotantes,
sin certificados de intervalos ni garantía global del optimizador.
