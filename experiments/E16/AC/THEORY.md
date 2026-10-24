# Métrica, Gauss, Jacobi e índice

Sean c1,c2 las observables lineales en perspectiva p y v1,v2 sus gradientes
respecto de los pesos θ. D/analytic_B implementa para la cuadrática
B(p)=s1 J1+s2 J2+c1 v1+c2 v2 y C=(F+ρI)⁻¹, con θ y C fijos.
U(p)=B(p)chol(C)=p₁ux+p₂uy y h=UUᵀ. Para la suma B=J1+J2 es constante.
Las derivadas exactas empleadas son

$$h_{,a}=U_aU^T+UU_a^T,\qquad h_{,ab}=U_aU_b^T+U_bU_a^T.$$

Con símbolos de primera especie Cᵢⱼₖ=(hᵢₖ,ⱼ+hᵢⱼ,ₖ−hⱼₖ,ᵢ)/2,
Γⁱⱼₖ=hⁱᵃCₐⱼₖ y

$$K=\frac{h_{01,01}-(h_{00,11}+h_{11,00})/2+
C_{\cdot01}^Th^{-1}C_{\cdot01}-C_{\cdot00}^Th^{-1}C_{\cdot11}}{\det h}.$$

Los controles de esfera e hiperbólico comprueban el signo de esta convención.
La EDO es p̈ⁱ=−Γⁱⱼₖṗʲṗᵏ en tiempo afín t. Se normaliza la velocidad inicial
para tener norma h igual a L: s=Lt. El Jacobi normal escalar satisface
jss+Kj=0,j(0)=0,js(0)=1; en t, jtt+L²Kj=0,jt(0)=L.
Ceros interiores cuentan multiplicidad1 en dimensión2. El cero inicial se
excluye; ceros en B son nulidad y se tratan como ambiguos, no índice negativo.

## Alcance del teorema

El índice de Morse describe variaciones normales con extremos fijos de una
geodésica continua regular. Las tangenciales incluyen libertad de parámetro
para longitud. El índice cero no prueba mínimo global: puede haber otras ramas
o locus de corte sin conjugados en esta rama. El shooting local no busca todas
las ramas, y la cercanía Hausdorff muestreada no certifica identidad de curvas.

La normal euclidiana de T en coordenadas z no es automáticamente el campo
normal riemanniano continuo; el espectro en g⊥ de Z/AB tampoco es el bloque
normal. La comparación solicitada requiere datos del mismo punto, que esos
archivos no contienen. Los UNKNOWN impiden aplicar H1 o H2, aun con índice0.

## Observación analítica posterior al diseño: inmersión cónica

No se usa como criterio retrospectivo de aceptación. En este modelo fijo,
B es el Jacobiano en p de ∇θ[(s1²+s2²)/2]. Por tanto h es la métrica inducida
por la aplicación vectorial Ψ(p)=∇θ[(s1²+s2²)/2]chol(C), homogénea de grado2.
En una región regular (h SPD), su imagen es una superficie cónica:
Ψ(rp)=r²Ψ(p). Por Euler, D²Ψ(p)[p,w]=DΨ(p)[w], tangente a la superficie.
Así, la segunda forma fundamental anula la dirección radial para toda normal;
cada operador de forma tiene determinante0. La ecuación de Gauss implica
K=0 localmente en la región regular. El vértice singular queda excluido por SPD.
Esta derivación explica K casi nula en MP, sin convertir estimaciones de K
puntuales en un certificado de intervalos ni probar que una dirección discreta
negativa sea puramente tangencial. La conclusión H1/H2 sigue la regla congelada.

## Contrastes y errores

MP50/80 evalúa la fórmula exacta de h y K en puntos float de la trayectoria.
RK4 MP integra Jacobi sobre una interpolación lineal de esas K, con256/512 nodos;
no integra la geodésica en MP. Se contrasta conteo, posición de ceros y j(L),
con incertidumbres de trayectoria, interpolación, muestreo y truncamiento.
DOP853 rtol1e-10/1e-12 no es aritmética de intervalos. Se registran Hausdorff
muestreado en ambos sentidos, deriva de velocidad y longitud frente a AB.
Ningún resultado declara mínimo global, causa única o confirmación independiente.
