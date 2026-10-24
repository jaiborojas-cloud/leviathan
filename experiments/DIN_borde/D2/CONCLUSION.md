# DIN-D2 · conclusión exploratoria v1

**Q1 PASS · Q2 PASS · Q3 PASS · Q4 PASS_DESCRIPTIVE · Q5 FAIL.**
Los PASS teóricos responden preguntas con condiciones; no confirman un piso
universal cuando M colapsa. Corrida VALID_EXPLORATORY,210 casos sintéticos,
12 paneles,8/8 controles independientes y 210/210 controles de matrices PASS.
No se usaron estados de entrenamiento. No se modificó ningún instrumento.

## Q1 · la coordenada: condición exacta y casos de igualdad

Sea m_k el mayor número de índices en una cara expuesta que contenga k;
si k es interior, ese término se omite. Para rango afín2,

**ρ̃(e_k e_kᵀ)=min(1/n,1/m_k−1/n).**

Por tanto vale1/n exactamente cuando m_k≤n/2 o k no pertenece a ninguna
cara. No hace falta que k sea vértice: un interior estricto siempre da1/n.
En posición general2D y n=27 las caras tienen≤2 índices y el piso vale para
todos los k. En cambio, una cara de26 índices con k en ella da
1/26−1/27=**1/702≈.00142450**, no 1/27. Un vértice puede fallar ese piso.

La prueba usa a'_k=a_k(r_k−μ) y μ'=Var(r)≥0. Hay una sola subida y
bajada como máximo. Las direcciones que extinguen k y cumplen
r_k≤mean(r) tienen TV=1/n; siempre existe una. Si k está entre los máximos,
la longitud es exactamente1/|S|−1/n. Caras con |S|=n/2 también dan igualdad
si n es par. Para m_k>n/2 alcanzan el mínimo las caras mayores que contienen k.
Con rango afín menor que2 puede existir una dirección sin cambio de a: la
misma definición paramétrica daría0, sin llegada al borde de la imagen.

## Q2 · rango1 general: el ínfimo sobre v es cero

ρ(u)=TV(vᵀa(su)). Su valor exacto es una suma finita de incrementos
absolutos entre ceros positivos del polinomio exponencial de la derivada y
los extremos0,∞. La cuerda da la cota
ρ̃≥min_S |mean_S(v)−mean_all(v)|; es igualdad en una dirección exactamente
cuando la proyección es monótona. No se asume monotonicidad de v general.

**inf_||v||=1 ρ̃=0**, alcanzado por el vector constante. Incluso con v⊥1,
v=(e_k−e_j)/√2 da0 en una dirección perpendicular a f_k−f_j, pues
a_k=a_j para todo s. Rango1 no implica piso1/n.
Además observar1/n no identifica de forma única una coordenada: hay modos
densos y un ejemplo de dos influencias interiores con ese mismo piso,
demostrados en [IDENTIFIABILITY.md](IDENTIFIABILITY.md), sin añadir casos al ensayo.

## Q3 · PSD general: cotas y límites de la información espectral

La cota de cuerda es **ρ̃≥min_S sqrt(Δ_SᵀMΔ_S)**,
Δ_S=1_S/|S|−1/n. Es suficiente para el piso que TODOS esos cuadrados
sean≥1/n². Con τ=λmin de M en1⊥ y m_max=max|S|,
ρ̃≥sqrt(τ(1/m_max−1/n)); τ≥max(0,1−(n−1)λmax).
Por ejemplo I/n sí conserva el piso cuando todas las caras tienen≤n/2 índices.

No hay una cota positiva universal basada sólo en «λmax cercano a1»:
λ ccᵀ+(1−λ)wwᵀ tieneρ=0 para cualquierλ∈[.5,1], con c constante y
w contraste. En la cara26, un proyector normalizado de rango26 daρ=0
incluso con λmax=1/26. Se conservan esas verificaciones de espectro.

THEORY da además una cota finita por un Gram de incrementos A(u). Si
d=max_u(n−número de proyecciones distintas+1), una cota positiva universal
sobre orientaciones de M existe cuando λmax<1/d; su constante depende de f.
Para λmax≥1/d hay una matriz apoyada en el núcleo conρ=0. En paneles
sin dos cuerdas paralelas d=2; en la cara26 d=26. No se certificó numéricamente
un mínimo angular del Gram ni se afirma que esa cota alcance1/n.
Sólo HMH afecta G, H=I−11ᵀ/n; tr M puede incluir masa invisible a J.

## Q4 · déficit bajo el piso y comparación con D1

Bajo la mezcla PSD especificada, **ρ̃≥sqrt(1−ε)/n** si el caso base tiene
piso1/n. La cota es aguda: N=11ᵀ/n anula J y produce igualdad exacta.
Un déficit LOGARÍTMICO δ exige ε≥1−exp(−2δ), alcanzable en ese modelo.
Para δ=5e−5, ε≈**9.9995e-05**.
Si5e−5 fuera una diferencia absoluta deρ, el resultado sería otro:
ε≈0.0026981775.

Con el mínimo publicado redondeado−3.29588, el desfase respecto a
−log27≈-3.295836866004 es≈4.3133996e-05.
No se deduce precisión adicional de ese redondeo. La mezcla saturante
ilustrativa predice λmax≈0.99990371,
no el valor mediano≈.9 de D1; además el estado mínimo y una mediana no son
la misma observación. Es **compatibilidad matemática, no explicación causal**.
No se leyó la orientación de ningún M entrenado ni se ajustó un modelo a D1.

N=I/n no baja del piso en paneles de caras pequeñas; en la cara26 la
geometría es distinta y se obtiene sqrt(1−ε+ε/26)/27. No toda perturbación
produce el mismo efecto. Una mezcla Loewner no equivale a una pequeña
inclinación arbitraria de un autovector.

## Q5 · función congelada bajo prueba

Se llamó rho_borde(g) con sus defaults1440/800, sin cambiar fuente, globals,
clases ni cuadraturas. geometry.py también se importó intacto con SHA.
Los resultados son 173 consistentes,
33 fallidos y 4 inconclusos.

| Forma | Casos | Q5 PASS | Q5 FAIL | INCONCLUSIVE | Falla mínimo/cota | Falla longitud reportada |
|---|---:|---:|---:|---:|---:|---:|
| gaussian | 51 | 51 | 0 | 0 | 0 | 0 |
| interior | 51 | 51 | 0 | 0 | 0 | 0 |
| near_collinear | 51 | 44 | 5 | 2 | 5 | 0 |
| mass_face | 57 | 27 | 28 | 2 | 28 | 1 |

FAIL puede significar que el valor no encuentra un mínimo/cota analítica o
que no coincide con la longitud completa de su ángulo reportado. Se auditan
ambos por separado. Una cara exacta y un ángulo casi empatado tienen distintos
extremos; la búsqueda uniforme/local no garantiza cubrir los casos aislados.
Una integración al infinito también puede perder transiciones muy tardías.
No se reparó el instrumento ni se reinterpretó una discrepancia como éxito.
[Casos fallidos](results/run_v1/failures.csv) · [retornos, avisos y referencias](results/run_v1/raw_and_references.json).

En casos sin mínimo exacto, PASS sólo indica consistencia con las cotas y el
testigo contrastado, no un certificado de óptimo global. Los inconclusos se
conservan; no se usan sus integrales MP no convergentes como evidencia firme.
Las parejas gaussian/near_collinear son cambios de carta invertibles:
[comparación descriptiva](results/run_v1/affine_pairs_descriptive.csv), sin
cambiar retrospectivamente los criterios de Q5. La homogeneidad nativa4M
frente a M fue PASS.

## Alcance, conservación y siguiente información necesaria

Ocho controles de referencia PASS y 210 controles de PSD/traza/norma
factorizada PASS. Tiempo 865.843661s, tres procesos numéricos,
BLAS/OMP1. Se conservan360 arrays sintéticos fuera de Git,
con SHA; todos los210 casos permanecen. [Recursos](results/run_v1/resources.json).
Diseño2269b7f → código61e7fe6 → mediciones; no se reejecutaron etapas
cerradas ni se leyó ningún dato T2 fuera del código permitido y contexto D1.

La lectura empírica de que el piso requiere «un único ejemplo» sigue sin
identificarse con los escalares publicados; hay contraejemplos matemáticos
a su necesidad. Haría falta información sobre la orientación/localización del
modo dominante y la masa visible HMH, que esta tarea no leyó. No se afirma
transferencia a T2, confianza del modelo, certificado de aritmética de intervalos
ni un piso de distancia geodésica general. Véanse [pruebas](THEORY.md),
[detalles de referencia](REFERENCE_DETAILS.md) y [procedencia D1](progress.md).

En los modos coordenados de paneles sin cara grande, el mínimo de
log(ρ_nativa/ρ_referencia) fue≈−3.33e-16. Este ensayo no reprodujo allí
el déficit de D1 como error numérico de5e-5. Los fallos de Q5 muestran
limitaciones en otras geometrías y no identifican la causa del déficit real.

Comprobación algebraica adicional del caso mass_face/2026102600/random_rank1:
la longitud nativa≈0.0055836 es menor que la cuerda del mismo ángulo,
≈0.2058983; la referencia completa da≈0.2409219. Esta contradicción ya
corresponde a un fallo Q5 preservado y no depende sólo de la integración MP.
No se reevalúan ni promueven los cuatro casos inconclusos.

[Verificación final PASS](verification.json):360 hashes externos,153 valores
globales conocidos,210 controles espectrales, fuentes congeladas intactas y
coherencia de los resultados preservados. Este PASS de integridad no cambia
el FAIL del instrumento en Q5. No se reintegró ni se repitió el instrumento.
