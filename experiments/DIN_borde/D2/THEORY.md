# DIN-D2 · demostraciones y alcance del piso

Se escribe a0=1/n·1, r_i=f_i·u, μ(s)=Σa_i r_i. Se supone rango afín2,
salvo donde se dice otra cosa. Toda dirección no nula llega a una cara
expuesta S(u); a∞=1_S/|S|. Los índices se cuentan con multiplicidad, no sólo
los vértices distintos. M PSD define una seminorma; no se invierte G singular.

## Q1 · teorema de la coordenada

Sea m_k el mayor número de índices en una cara expuesta que contenga k;
si k es interior, no existe tal cara y el término correspondiente es∞.
Entonces

ρ(e_k e_kᵀ)=min{1/n, 1/m_k−1/n}.

Prueba. a'_k=a_k(r_k−μ) y μ'=Var_a(r)≥0. Si k es máximo, a_k crece
monótonamente de1/n a1/|S|, dando exactamente1/|S|−1/n. Si no es máximo,
a_k termina en0 y su TV es≥1/n, con igualdad exactamente cuando
r_k≤μ(0). Si r_k>μ(0), hay un único máximo interior a*, y TV=2a*−1/n.
Existe siempre una dirección de extinción monótona: u=mean(f)−f_k si no
es cero; da r_k<μ(0). Si f_k=mean(f), cualquier dirección no constante
da r_k=μ(0)<max r y después decrece. Eso prueba la fórmula y su alcance.

Por tanto el piso1/n vale exactamente cuando ninguna cara que contiene k
tiene más de n/2 índices. En posición general2D hay a lo sumo2 por cara:
para n=27 vale para TODOS los k, incluidos interiores. k no necesita ser
vértice. Para k interior estricto m_k no existe y el valor siempre es1/n.
Si una cara tiene26 de27 índices y k está en ella, el valor es
1/26−1/27=1/702, menor que1/27. Si k es el índice restante, vale1/27.

Casos de igualdad: cuando el valor mínimo es1/n, lo realizan todas las
direcciones que excluyen k y satisfacen r_k≤mean(r); también caras con
k y |S|=n/2 si n es par. Cuando m_k>n/2, sólo las caras de máximo tamaño
m_k que contienen k alcanzan el mínimo. Si el rango afín es menor que2,
una dirección perpendicular puede mantener todos los logits iguales:
la definición con todas las direcciones entonces daρ=0, aunque esa curva
no llegue al borde de la imagen. La hipótesis de rango importa.

## Q2 · modo de rango1 general

Para M=vvᵀ, ||v||=1, la longitud es TV de F(s)=vᵀa(s). Su derivada tiene
numerador

H(s)=Σ_{i<j}(v_i−v_j)(r_i−r_j)exp((r_i+r_j)s),

con denominador Z(s)². Agrupando exponentes iguales, si H no es idénticamente
cero tiene a lo sumo T−1 raíces reales (contando multiplicidad), donde T es
el número de términos no nulos distintos: propiedad de Chebyshev de las
exponenciales reales. Si t1,…,tq son las raíces positivas, t0=0 y t(q+1)=∞,
la longitud exacta es Σ|F(t(l+1))−F(tl)|. Si H≡0 la longitud es0.
Esto da una fórmula finita por puntos críticos, no exige monotonicidad.

Siempre ρ(vvᵀ)≥min_S |mean_S(v)−mean_all(v)|. La cota de extremo es
igualdad en una dirección si y sólo si F es monótona (incluido constante).
Un mínimo global igual a esa cota requiere una cara minimizante con tal
dirección monótona. Es cota, no igualdad automática para v repartida.

El ínfimo sobre v unitario es0 y se alcanza: v=1/√n anula todo J.
Incluso imponiendo v⊥1, v=(e_k−e_j)/√2 tiene una dirección perpendicular
a f_k−f_j en la que a_k=a_j para todo s. Si los rasgos coinciden, sucede
en todas las direcciones. En rango afín2 se puede escoger una curva no
constante hasta el borde: rango1 NO implica piso1/n.

Para este contraste hay otra fórmula útil. Si r_k=r_j, TV=0. Si el mayor
de ambos es máximo global y los r son distintos, |F| crece hasta1/(|S|√2).
Si ambos son menores al máximo global, |F| tiene un único pico y TV=2|F*|:
log|F|'=r_min+δ/(1−exp(−δs))−μ(s), δ=|r_k−r_j|,
y su derivada es estrictamente negativa. Esto permite bisección independiente.

## Q3 · PSD general y espectro

Sea Δ_S=1_S/|S|−a0. Por longitud≥cuerda,

ρ(M,f)≥L_end=min_S sqrt(Δ_SᵀMΔ_S).

Es suficiente para ρ≥1/n que TODOS esos cuadrados sean≥1/n².
No es condición necesaria: una curva puede retroceder. Sea H=I−11ᵀ/n,
τ=λ_min de M restringida a1⊥ y m_max=max_S |S|. También

ρ≥sqrt(τ) sqrt(1/m_max−1/n).

Para tr M=1 y ℓ=λmax, τ≥max(0,1−(n−1)ℓ). Da una cota explícita en
n,ℓ y caras, a menudo trivial cerca del colapso. Si M=I/n y m_max≤n/2,
L_end≥1/n. No se concluye lo mismo de ℓ grande por sí solo.

De hecho, para cualquier panel de rango2 y ℓ∈[1/2,1],
M=ℓ ccᵀ+(1−ℓ)wwᵀ, c=1/√n, w=(e_k−e_j)/√2,
tiene traza1, λmax=ℓ yρ=0 en la dirección de igualdad del contraste.
Esto incluye ℓ=.9: el espectro agregado no prueba el piso.

Una cota espectral dependiente de TODA la geometría puede ser más fuerte.
Fijar s_j=j, j=0,…,n−1, y A(u)=Σ_j Δa_jΔa_jᵀ con
Δa_j=a(s_j u)−a(s_(j−1)u). La longitud≥Σ||M^(1/2)Δa_j||
≥sqrt(tr(MA)). Si α_i son los autovalores ascendentes de A,
min_{M PSD,tr1,λmax≤ℓ}tr(MA)=ℓΣ_(i≤k)α_i+(1−kℓ)α_(k+1),
k=floor(1/ℓ), omitiendo el último término si no hay resto. Tomar el mínimo
angular de su raíz da una cota en f yℓ, sin conocer la orientación de M.

Más precisamente, g(u)=número de proyecciones r distintas y
d=max_u[n−g(u)+1]. Las n muestras de exponenciales distintas tienen
rango g (Vandermonde exponencial); sus diferencias tienen rango g−1.
Luego dim ker A(u)≤d y α_(d+1)(A(u))>0 continuamente en la circunferencia.
Por compacidad α*=min_u α_(d+1)>0. Por tanto, si ℓ<1/d,
ρ≥sqrt((1−dℓ)α*)>0. No se calcula un certificado numérico de ese mínimo.
Si ℓ≥1/d, se puede apoyar M en el núcleo de una dirección que alcanza d,
repartir su traza con máximoℓ y obtenerρ=0. Es el umbral exacto para
existencia de una cota positiva universal sobre esas orientaciones de M.
En posición sin dos cuerdas paralelas d=2; en la cara26 de27 se tiene d=26.
El proyector a(1,…,1,−26)⊥ dividido por26 realizaρ=0 con ℓ=1/26.

Además, sólo HMH afecta la métrica, porque1ᵀJ=0. tr M incluye una masa
que puede ser invisible a la geometría. Es otra razón por la que un piso
normalizado por la traza total no se deriva sólo de rango efectivo.

## Q4 · perturbación aguda y escala del déficit

Para Mε=(1−ε)e_k e_kᵀ+εN, N PSD,tr N=1, la monotonía de Loewner da
ρ(Mε)≥sqrt(1−ε)ρ(e_k e_kᵀ). En el caso con piso1/n,

ρ(Mε)≥sqrt(1−ε)/n,
logρ(Mε)≥−log n + (1/2)log(1−ε).

La cota es aguda: N=11ᵀ/n satisface NJ=0 y se alcanza exactamente en
todas las direcciones. Una bajada logarítmica δ permite ε=1−exp(−2δ) en
ese modelo: δ≈5e−5 corresponde aε≈1e−4. Esto es compatibilidad, no prueba
de que esa mezcla describa los estados D1. Si5e−5 fuese un déficit ABSOLUTO
de ρ, correspondería a otro ε≈.002698, no al cálculo logarítmico anterior.

En cambio N=I/n no baja del piso en paneles con todas las caras≤n/2:
las cuerdas tanto de e_k como de I/n tienen norma≥1/n; su mezcla conserva
el cuadrado de esa cota. No toda perturbación baja ρ. El λmax≈.9 publicado
no fija ε ni la orientación/localización de su autovector. Tampoco el mínimo
logarítmico redondeado permite inferir un mecanismo del entrenamiento.
