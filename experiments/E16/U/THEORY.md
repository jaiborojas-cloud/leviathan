# Descenso finito, simetría y geometría

U usa los candidatos y direcciones exploratorios de T, sin nuevos datos ni
confirmación independiente. Cada dirección v tiene norma euclídea uno en las
variables físicas normalizadas (t,s). Todos los pasos parten del original x.
No se componen perturbaciones ni se elige el mejor punto como nuevo resultado.

## Cambios par e impar

Sea c=max(1,|L(x)|). Se definen

$$\Delta_\pm(h)=\frac{L(x\pm hv)-L(x)}{c},\qquad
E(h)=\frac{\Delta_+(h)+\Delta_-(h)}2,\qquad
O(h)=\frac{\Delta_+(h)-\Delta_-(h)}2.$$

Si L es suficientemente suave y h es pequeño,

$$E(h)=\frac{h^2 v^THv}{2c}+O(h^4),\qquad
O(h)=\frac{h\nabla L(x)^Tv}{c}+O(h^3).$$

U registra las predicciones y los residuos, sin demostrar cotas de los términos
omitidos ni imponerles una tolerancia posterior. La banda de signo ±1e-20 es
una regla numérica congelada, no incertidumbre estadística.

Un descenso unilateral puede proceder del gradiente residual. E negativo indica
que la media de las dos longitudes disminuye y, por tanto, al menos una disminuye;
no indica que ambas disminuyan. Un E positivo tampoco impide descenso en uno
de los sentidos. Los dos signos se conservan en cada pareja.

La concordancia MP80/MP120 comprueba consistencia numérica de la primitiva.
No es una cota rigurosa del error, ni una validación independiente de la métrica.
El gradiente y Rayleigh archivados son predicciones locales; las evaluaciones
finitas son mediciones distintas sobre las mismas fuentes y direcciones.

## Distancia entre imágenes poligonales

Sean A y B las imágenes de las poligonales. Para una muestra finita S_A de
vértices y puntos medios de A, se calcula la distancia exacta en aritmética real
de cada muestra a todos los segmentos de B. Simétricamente para S_B:

$$\ell=\max\{\max_{p\in S_A}d(p,B),\max_{q\in S_B}d(q,A)\}\le d_H(A,B).$$

Si las poligonales tienen los mismos índices y extremos, cada punto de una
arista tiene un correspondiente con la misma coordenada afín en la otra.
La convexidad de la norma proporciona

$$d_H(A,B)\le u=\max_j\|a_j-b_j\|.$$

El valor u depende de la correspondencia. Puede ser grande aunque A=B:
redistribuir nodos de un segmento recto da un ejemplo. Por ello una cota inferior
pequeña junto a una superior grande deja UNRESOLVED, sin probar identidad.
El test CHANGED exige inferior ajustada>1e-8; WITHIN_TOLERANCE exige superior
ajustada≤1e-8. La geometría es euclídea en la carta (t,s), no intrínseca.

Las operaciones geométricas son float64 sobre la proyección de puntos MP.
Se controla el error de esa proyección y se aplica un colchón fijo de 1e-12 a
las cotas, sin afirmar que sea un intervalo riguroso de redondeo. Tampoco se
refina la muestra después de observar qué ensayos quedaron sin resolver.

## Admisibilidad y control recto

Se exigen cajas MP, extremos fijos, aristas no nulas, primitiva definida y
positividad métrica numérica por Bernstein de h00 y determinante en cada arista.
Las perturbaciones inviables o inválidas se conservan; no se recortan.

En C0, el desplazamiento tangencial que conserva el orden de nodos mantiene
longitud e imagen recta en aritmética real. Si invierte segmentos, puede aumentar
la longitud recorrida aun manteniendo la misma imagen. Los autovectores mínimos
de un espacio nulo degenerado dependen del eigensolver; no se consideran una
dirección física única. U no usa el control para reajustar umbrales.

Ningún descenso finito certifica un mínimo, una geodésica o convergencia continua.
Una dirección débil mayormente tangencial puede cambiar la imagen del polígono:
no es una reparametrización exacta de una curva suave fijada.
