# Lo que el piso no identifica

Deducciones analíticas complementarias, sin añadir casos ni modificar las
reglas congeladas. Se refieren a ρ de semirrectas, no a un piso de distancia
geodésica general; con M singular la métrica pullback puede ser degenerada.

## No identifica de forma única un ejemplo

Sea H=I−11ᵀ/n. Como1ᵀJ=0, sólo HMH influye en G. Los vectores
v=e_k y v'=e_k−(2/n)1 tienen norma1 y dan la MISMA métrica, aunque v' tiene
todas sus componentes no nulas. El piso no distingue esas dos matrices.

Hay también un ejemplo con dos influencias observables. Si i,j son puntos
estrictamente interiores del panel, sean c=(1/√n)·1 y
v=(e_i+e_j)/2+γc, γ=−1/√n+sqrt(1/2+1/n). Entonces ||v||=1 y
vᵀa=(a_i+a_j)/2+γ/√n. Todo extremo de semirrecta excluye i,j, de modo
que su variación es al menos1/n. Existe u no nulo con
(f_i−mean f)·u≤0 y(f_j−mean f)·u≤0: intersección de dos semiplanos
por el origen. En esa dirección ambas probabilidades decrecen hasta0,
así que la variación es EXACTAMENTE1/n. Su modo observable es proporcional
a H(e_i+e_j), no a un único H e_k. Por tanto localizarse en un solo ejemplo
es suficiente bajo Q1, pero no necesario para observar el piso.

## Qué permite concluir el déficit

En el modelo Loewner explícito Mε=(1−ε)e_k e_kᵀ+εN y bajo el caso base
con piso1/n, una caída logarítmica δ>0 exige
ε≥1−exp(−2δ). N=11ᵀ/n alcanza la cota: ése es el ε MÍNIMO compatible,
no una estimación de ε en una matriz entrenada desconocida.

Para esa mezcla saturante, los dos autovalores no nulos son
[1±sqrt(1−4ε(1−ε)(1−1/n))]/2. Un δ≈5e−5 exige ε≈1e−4 y en ese
modelo λmax≈.9999. El λmax mediano≈.9 de D1 no demuestra ese modelo;
además una mediana poblacional y el estado de mínimoρ no son el mismo dato.
Otros residuos/orientaciones pueden producir valores distintos con el mismo
espectro. Ni el déficit ni el rango agregado identifican el mecanismo real.

Una matriz rank1 inclinada respecto a e_k tampoco tiene por qué admitir una
resta positiva (1−ε)e_k e_kᵀ: la hipótesis de mezcla PSD de Q4 es más fuerte
que decir «autovector casi alineado». No se extrapola esa cota sin verificarla.

El mínimo publicado−3.29588 está redondeado; sólo se compara como escalar
exploratorio. No se leyeron estados de entrenamiento ni orientaciones de M.
