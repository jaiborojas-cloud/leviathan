# DIN-D9g-b: teoría del control y de la robustez

En cada bloque exterior, las transformaciones φ_j se construyen con parámetros
estimados sólo sobre las filas de entrenamiento. Se forman polinomios y productos
antes de centrar cada término dentro del grupo (nivel,split). No se eleva al cuadrado
una variable previamente centrada como sustituto: esa operación definiría otra base.

B1⊂B2⊂B3⊂B4 como espacios de funciones para la transformación entrenada. La media
y escala afín no cambian el espacio polinómico completo incluido; se conservan para
mejorar estabilidad numérica. Centrar términos elimina interceptos de grupo. Los
coeficientes OLS son comunes entre splits y se estiman sin datos del bloque retenido.

D=1−SSE(base+c30)/SSE(base) compara dos errores de CV. El control D_base usa
SSE_0=sum Y_centrado². Con bases de distinta complejidad cambian ambos denominadores;
no se equipara la desaparición de D con absorción demostrada de información. Una base
más flexible puede generalizar peor por estimación/extrapolación, aun siendo anidada.

El control negativo es c_hat_j=B_j a_j con a_j ajustado en entrenamiento del bloque.
Entonces span[B_j,c_hat_j]=span(B_j) también en el bloque retenido: añadir esa
columna no amplía el predictor ajustado. El coeficiente es no identificable, y D≈0
se verifica numéricamente sin imponerlo por código. Una predicción desde B4 no está
en general en span(B1); su incremento sobre B1 no acusaría sesgo por sí mismo.

FWL residualiza el candidato con la base entrenada; su pendiente usa r_cᵀY/||r_c||².
Las predicciones retenidas usan c_test−B_test a_c,train. Se contrasta todo el vector
de D nulos contra OLS directo. Candidatos por alias se resuelven con SVD del ajuste
completo y no reciben un coeficiente interpretable. Rank/condición se conservan.

La permutación dentro de grupos conserva la base y cambia sólo c30. La igualdad
computacional con OLS no prueba calibración estadística universal. La prueba positiva
usa una señal residual grande e independiente: valida sensibilidad del instrumento,
no su potencia para el incremento pequeño observado anteriormente.

«Artefacto de base lineal» es una etiqueta operacional prefijada cuando B3 y B4 dan
D≤0. No es un teorema de que toda la señal inicial derive de no linealidad barata,
ni un resultado causal. La construcción de M y la relación de probabilidades con
sus gradientes son identidades algebraicas; el error de generalización no lo es.
