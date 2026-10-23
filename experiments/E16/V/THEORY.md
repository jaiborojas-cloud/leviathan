# Transporte, subdivisión y cambio de familia

V no vuelve a optimizar los candidatos ni calcula el espectro mínimo refinado.
Compara extensiones prefijadas de una dirección original a representaciones
más densas de la misma poligonal.

## Identidad de subdivisión

Sea Sα la inserción de un punto (1−α)zⱼ+αzⱼ₊₁ en cada arista. Se usan α=1/2
y α=1/4. Conservando el orden de segmentos, la integral de longitud satisface

$$\widetilde L(S_\alpha z)=L(z).$$

La poligonal subdividida conserva imagen y longitud recorrida, incluso si la
poligonal original tiene retrocesos. La igualdad se debe a aditividad de la
integral sobre cada segmento; no requiere que el camino sea mínimo.
La comprobación MP de esta igualdad valida consistencia numérica de la
primitiva y del ensamblaje, sin constituir nueva evidencia confirmatoria.

Si la dirección original es v y los extremos están fijos, el transporte es
la inserción lineal Sαv. En particular,

$$S_\alpha(z+hv)=S_\alpha z+hS_\alpha v.$$

En regiones suaves, la identidad de funciones implica el pullback

$$S_\alpha^T\nabla\widetilde L=\nabla L,\qquad
S_\alpha^T\widetilde H S_\alpha=H.$$

Así, el cambio finito de longitud es el mismo al transportar, para todo paso
admisible, no sólo asintóticamente. Esto no afirma que H y el Hessiano completo
refinado tengan el mismo espectro: el espacio refinado incluye más direcciones.
V no calcula esas direcciones ni demuestra estabilidad espectral.

## Normas y amplitudes

Sαv añade componentes; su norma euclídea en el vector de nodos puede superar
la de v. Si se renormalizara, cambiaría la amplitud física de los vértices
originales. V conserva h y esos desplazamientos y registra las normas.

Un Rayleigh unitario refinado en la dirección transportada sería

$$\frac{(S_\alpha v)^T\widetilde H(S_\alpha v)}{\|S_\alpha v\|^2}
=\frac{v^THv}{\|S_\alpha v\|^2}.$$

Comparar números sin reconocer ese denominador mezclaría dos normalizaciones.
V usa cambios finitos, sin presentar nuevos Rayleigh unitarios.

## Nodos insertados fijos

P denota la inserción del desplazamiento v en los índices de los vértices
originales, poniendo cero en los nuevos. La familia pinned es

$$z_{\alpha,h}^{\rm pinned}=S_\alpha z+hPv.$$

En general Pv≠Sαv. Los puntos insertados permanecen sobre la poligonal original,
pero dejan de estar sobre las aristas perturbadas. Por ello la nueva curva
puede diferir de la transportada, y su cambio de longitud no está obligado
a conservar signo. Esto es un cambio de familia de perturbaciones, no una
reparametrización exacta ni un experimento de convergencia del optimizador.

La elección α altera la distribución de nodos y la familia pinned, conservando
la base. Un resultado distinto entre α o entre familias describe dependencia
local de esa elección; no identifica una causa única de la señal de T/U.

## Signo, geometría y límites

Se conservan Δ±, cambio par E=(Δ++Δ−)/2 y cambio impar O=(Δ+−Δ−)/2, con
banda ±1e-20. El gradiente residual puede producir descenso unilateral aunque
E sea positivo. Un cambio de signo de E no implica por sí solo que ningún
sentido pueda descender.

Las cotas geométricas de U comparan cada ensayo con su base y con su versión
transportada de los mismos índices. Un máximo desplazamiento entre índices
es cota superior de Hausdorff por interpolación afín, pero puede ser holgado.
Las muestras de vértices y puntos medios dan una inferior simétrica. CHANGED,
WITHIN_TOLERANCE y UNRESOLVED siguen siendo clasificaciones numéricas, sin
intervalos rigurosos de redondeo ni distancia intrínseca.

S y T/U usan los mismos datos; V no aporta independencia confirmatoria. La
subdivisión exacta, incluso a 528 segmentos, no es una nueva solución fina
optimizada ni demuestra convergencia continua, mínimos o geodésicas.
