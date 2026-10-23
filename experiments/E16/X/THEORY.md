# Mínima curvatura dentro de g⊥

W proyectaba una dirección mínima original; X resuelve un problema distinto:

$$\mu_1=\min_{\|u\|=1,\;g^Tu=0}u^THu.$$

Si B tiene columnas ortonormales que generan g⊥, u=By y el problema es el
mínimo autovalor de Hc=BᵀHB. La dirección proyectada de W es un candidato
admisible, pero no necesariamente el mínimo. En aritmética exacta μ₁≤qW.
Esta desigualdad explica cómo qW puede ser positivo mientras μ₁ es negativo.

## Householder y entrelazado

Para n=g/‖g‖, s=sign(n₀) tomando s=+1 en cero, se define

$$a=\frac{n+s e_0}{\|n+s e_0\|},\qquad Q=I-2aa^T.$$

Q es ortogonal y sus columnas desde la segunda forman B. La elección de s
evita cancelación al construir el reflector. Se comprueban ortonormalidad y
ortogonalidad al gradiente normalizado antes de diagonalizar.

Para H simétrico y restricción de codimensión uno, los autovalores ordenados
satisfacen el entrelazado de Cauchy:

$$\lambda_i(H)\le\mu_i(H_c)\le\lambda_{i+1}(H).$$

X guarda ambos espectros escalares y comprueba esta relación numéricamente.
No es aritmética de intervalos ni una cota demostrada del error espectral.
Cuando ‖g‖≤1e-25 se usa el espacio completo, con etiqueta SMALL_GRADIENT;
no se quita una dirección escogida a partir de redondeo.

## Dirección levantada y limpieza MP

Del mínimo autovector y se obtiene v=By. La construcción de B en float64 puede
dejar un residuo pequeño de gᵀv. En MP se elimina sólo ese residuo con la
proyección euclídea y se normaliza. Se comprueban Rayleigh y residuo proyectado
contra μ₁ para evitar que la limpieza cambie materialmente la solución numérica.

Una condición estacionaria restringida es

$$H u-\mu u=\alpha g,$$

no necesariamente Hu=μu. Por eso se evalúa el residuo después de proyectarlo
al subespacio. El control adicional con diferencias finitas MP contrasta la
pendiente y la curvatura en la dirección levantada, no todas las entradas de H.

## Qué permite concluir

Si el mínimo reducido y su Rayleigh MP están por debajo del umbral negativo
congelado y las comprobaciones pasan, se informa curvatura negativa numéricamente
resuelta. Es un subespacio definido por gradiente aproximado, con un umbral
numérico; no un certificado riguroso de segundo orden.

La pendiente casi nula permite contrastar el comportamiento finito sin el término
lineal dominante de las direcciones originales. No elimina los términos impares
cúbicos, así que los dos descensos pueden diferir. Se registran Δ±, E/O,
predicciones y residuos, sin búsqueda de mejor paso.

Un candidato aproximadamente estacionario con descenso en ambos sentidos no se
convierte en prueba de silla exacta. Los cambios de geometría se miden con cotas
numéricas de U, no distancias intrínsecas rigurosas. Tampoco se deduce un mínimo,
una geodésica o convergencia continua. S/T/U/V/W conservan sus resultados.
