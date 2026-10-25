# Construcción, identidades y observaciones que G1 puede contrastar

P es la coordenada perspectival2D; p_y es probabilidad de la red para una
etiqueta. No son la misma variable. Con panel de n ejemplos,
a(P)=softmax(fP), J=diag(a)(f-1 aᵀf), G=JᵀMJ y a(0)=1/n.
En G1, f contiene sépalo largo/ancho estandarizados por train. Los gradientes
de la red usan sus cuatro variables; no se eligió f según su poder predictivo.

## Qué se mantiene exactamente

make_geom_state original clona parámetros de las dos capas ReLU y de dos
logits relativos a la tercera clase. U tiene columnas sqrt(p_c/n) grad log p_c;
R tiene filas grad log p_y. subset_M concatena TODOS los bloques y calcula
M=R(F+gamma I)⁻¹Rᵀ, F=UUᵀ, gamma=1e-4 max(lambda_max(UᵀU),1e-14).
No se suman tres M independientes ni se cambia ridge. Iris tiene tres clases;
R27/P60/W27 cumplen el forward fijo sin editar core. W27 cambia anchos,
no añade capas que la función original no sabría representar.

Adam entrena parámetros completos de tres logits, igual que el antecedente;
la construcción geométrica usa después la parametrización reducida original.
Se continúa250 updates con lotes propios; no se llama al cargador/entrenador
Wine ni se toma una decisión de parada a partir de validación.

## Parte algebraica conocida, no un hallazgo nuevo

[D2b](../D2b/THEORY.md) demuestra, con A Jacobiano apilado de los logits
reducidos y delta_n=1-p_y,n:

    M_nm=delta_n delta_m h_nᵀ(F+gamma I)⁻¹h_m.

Si rango(A)=2n y ridge es despreciable en el rango Fisher relevante,

    M≈n diag((1-p_y,n)/p_y,n).

En cualquier rango,0≤M≤n diag(odds). La igualdad aproxima diagonalidad y
dominancia del menos confiado, pero no obliga a que sólo un odds domine.
Con Jacobianos alineados, rango deficiente o ridge significativo, no fuerza
diagonalidad ni que argmax Mkk coincida con argmin p_y.

Por eso G1 registra rango/espectro numérico de Fisher, gamma/lambda_min
resuelta, error frente a n diag(odds), y leverage Mkk/(n odds_k). Un rango
Fisher numérico no es certificado exacto de rango A. Los errores de coma
flotante no se convierten en pruebas de desigualdades Loewner rigurosas.

Tras colapso COORDENADO (no cualquier rango1), [D2](../D2/THEORY.md) da

    rho≈sqrt(Mkk) min(1/n,1/m_k-1/n).

Aquí m_k cuenta índices en una cara expuesta que contiene k. Si todas esas
caras tienen≤n/2 índices, el factor es1/n, también para k interior.
Si además leverage≈1, rho≈sqrt(n odds_k)/n. Esto es una aproximación
CONDICIONAL. Su uso no certifica un mínimo geodésico ni transferencia a otra
cohorte. D2b también muestra modos invisibles y contraejemplos a un piso universal.

### Límite de rango dentro de una región ReLU

Si m ejemplos comparten TODAS las máscaras de activación de las dos capas,
cada logit es afín en x dentro de esa región. Para cada parámetro, su
derivada también es afín en x con esas máscaras fijas. El Jacobiano apilado
de dos logits sobre ese grupo factoriza mediante [X,1]⊗I2; por tanto

    rango(A_grupo) ≤ 2 rango([X,1]) ≤ 2(d_entrada+1).

En Iris4D el límite es10, frente a28 en13D. Más de5 puntos en una misma
región bastan para que no se pueda invocar la condición SUFICIENTE de rango
completo2n. No se deduce sólo de ello que M no sea diagonal: la igualdad
sobre los scores puede tener condiciones menos exigentes que rango(A)=2n.
G1 no midió ni seleccionó regiones de activación; esto es un lema teórico,
no la explicación causal comprobada de un eventual contraste entre familias.

## Qué es empírico en H1–H5

La concentración de odds durante aprendizaje, el número de ejemplos difíciles,
su identidad y estabilidad, el tiempo de memorizar y la predicción10→250 no
están determinados por la identidad estática. H1/H2 examinan esas propiedades
con umbrales de localización/diagonalidad. H3 examina una asociación esperable
si se cumplen las condiciones, no una ley causal nueva.

H4 compara eventos observados por visitas con censura. La falta de memorizar
o de colapso en250 no prueba que no ocurran con entrenamiento más largo.
Eventos en visitas adyacentes tampoco prueban simultaneidad ni causa única.

H5 compara una BASE CÚBICA prefijada de L10 con esa base más X10. Un D positivo
puede corresponder a una mejor representación funcional de L, sin información
condicional nueva sobre todo L. [D2c](../D2c/CONCLUSION.md) proporciona casos
X=h(L) que lo muestran. W_adj lineal-rangos se conserva sólo como descriptivo
del antecedente; [D2b](../D2b/RECOMENDACION_DIN_C1.md) explica su limitación.
G1 no reutiliza ni evalúa el confirmatorio DIN-C1 que está en curso.

## Panel y arquitectura: límites de los contrastes

P60 incorpora33 ejemplos fijados (11 por clase) además de los27 de R27.
Cambia n en a(0), promedio Fisher, número de scores y composición geométrica;
ésas son consecuencias del cambio de panel, no variables ajustadas aparte.
Si el mismo k y odds dominaran y leverage≈1, cambiar27→60 produciría un
factor esperado sqrt(27/60) en rho BRUTO por construcción. Comparar sus
medianas sin esa advertencia confundiría normalización con dinámica.

W27 cambia expresividad, número/organización de parámetros y condición Fisher;
gamma sigue la misma regla espectral. No se interpreta como intervención
aislada sobre capacidad predictiva abstracta. Semillas de pesos siguen una
regla común; matrices de distinto tamaño no pueden ser pesos idénticos.

R27 es una referencia externa adaptada a4 entradas frente a13. La partición
90/60 y el tamaño total150 difieren del antecedente Wine. La generalización
se limita a Iris, dos anchos y dos paneles, con250 updates y la misma receta.
Los20 splits reusan observaciones y R27/P60 comparten entrenamientos: no son
20 datasets independientes ni300 redes independientes.

## Cuerda completa y resolución

Toda curva hasta la cara S tiene longitud al menos||a_infinito-a0||M.
El mínimo de esas cuerdas sobre TODAS las caras es una cota inferior de rho.
En vértices se incluyen coordenadas duplicadas; en aristas, todos los índices
colineales. Se usa una tolerancia geométrica declarada y un control sintético.
Iris tiene mediciones discretas: no se supone posición general.

El instrumento congelado hace cuadratura angular y refinamiento local; no
certifica el mínimo angular global y puede tener problemas en direcciones
aisladas/colas, ya documentados en D2. Los contrastes720/400 frente a1440/800
son pruebas de consistencia numérica, no una reparación ni una certificación.
Se preservan diferencias entre rho_min_gl y rho refinada y todos los avisos.
H3/H5 sólo tienen el alcance operacional del instrumento y las reglas de calidad.
