# E11-L — escala multicategoría y alcance geométrico

## Objetivo y carácter del experimento

E11-L amplía la prueba en dos direcciones: más ejemplos y una geometría que incluye las dos últimas capas. Como el entorno local no contiene un benchmark real multicategoría mayor que los ya usados, se construyó una **prueba de esfuerzo sintética controlada** mediante `sklearn.make_classification`: 4,000 ejemplos, 24 variables, 18 informativas, cuatro redundantes, cinco clases, dos conglomerados por clase, separación 1.6 y 2 % de ruido de etiquetas. Este experimento mide escalabilidad y dependencia del alcance; no cuenta como una tercera réplica en datos naturales.

Se mantuvieron las elecciones registradas en E11-J/K:

\[
G_\rho=B\bigl(F+\rho\lambda_{\max}(F,H)H\bigr)^{-1}B^T,
\qquad H=I,\quad\rho=10^{-4},
\]

con relevancia de etiqueta verdadera y predicción \(C=D_{aleatoria}-D_{real}<0\). E11-L pregunta además si esa predicción sobrevive al extender el espacio tangente desde el clasificador final hasta la subred completa de las dos últimas capas.

## Diseño

- Arquitectura nueva: MLP ReLU **24→160→48→5**.
- Tres repartos estratificados, cada uno con 3,000 ejemplos de entrenamiento y 1,000 de evaluación independiente.
- Cuatro semillas por reparto y etiquetas verdaderas frente a una permutación fija: 12 pares, 24 modelos.
- Todos los modelos alcanzaron al menos 99 % de precisión sobre su objetivo.

| Régimen | Pasos medios al 99 % | Precisión media de entrenamiento | Precisión media de evaluación verdadera |
|---|---:|---:|---:|
| Etiquetas verdaderas | 363 | 99.07 % | 91.33 % |
| Etiquetas aleatorias | 1,515 | 99.15 % | 20.24 % |

Los dos parámetros perspectivales fueron las coordenadas de entrada 0 y 1, normalizadas exclusivamente con estadísticas de entrenamiento. La relevancia siempre usó la etiqueta verdadera del panel de evaluación.

## Dos alcances geométricos

### Última capa

Se utilizó la parametrización identificable de cuatro logits respecto a la quinta clase: \((48+1)\times4=196\) coordenadas. Fisher se diagonalizó de forma explícita.

### Dos últimas capas

Se incluyeron la matriz y sesgo 160→48 y los cuatro logits identificables de salida: **7,924 coordenadas**. No se formó una matriz Fisher densa de aproximadamente 62.8 millones de elementos. Se aplicó Fisher como operador mediante propagación tangente y se resolvieron las dos columnas necesarias de

\[
(F+\rho\lambda_{\max}I)X=B^T
\]

con gradiente conjugado. Los residuos relativos máximos fueron \(9.98\times10^{-7}\), coherentes con la tolerancia declarada de \(10^{-6}\). \(\lambda_{\max}\) se estimó con 35 iteraciones de potencia.

## Resultado principal: inversión por alcance

Con los 1,000 ejemplos independientes de cada reparto:

| Alcance | \(D_{real}\) | \(D_{aleatoria}\) | \(C\) medio | Pares con \(C>0\) | Repartos con media \(C>0\) |
|---|---:|---:|---:|---:|---:|
| Última capa | 3.070 | 1.290 | **−1.779** | 0/12 | 0/3 |
| Dos últimas capas | 1.354 | 4.177 | **+2.823** | 12/12 | 3/3 |

Las medias por reparto fueron:

- última capa: −1.429, −1.863, −2.046;
- dos últimas capas: +3.315, +2.643, +2.512.

La predicción fijada se reproduce sin excepción en la última capa. Su extensión a dos capas queda **falsificada sin excepción en esta cuadrícula**. Incluir la capa 160→48 no solo cambia la magnitud: invierte la relación y muestra mucha más deformación durante la memorización aleatoria.

Con tres medias de reparto, la prueba bilateral de inversión de signos tiene resolución mínima \(p=0.25\). La uniformidad del signo es descriptivamente fuerte, pero no sustituye réplicas independientes.

## Control de panel

Para la última capa se usaron dos subpaneles estratificados por tamaño; los de 250 son disjuntos, los de 450 y 750 se solapan parcialmente.

| Tamaño | Contraste medio | Sesgo | RMSE | Coincidencia de signo | Error relativo mediano de D | Percentil 90 |
|---:|---:|---:|---:|---:|---:|---:|
| 250 | +0.681 | +2.461 | 2.583 | 29.2 % | 55.8 % | 137.9 % |
| 450 | −0.203 | +1.576 | 1.631 | 41.7 % | 39.7 % | 74.1 % |
| 750 | −1.260 | +0.520 | 0.593 | 91.7 % | 13.0 % | 32.0 % |

El panel pequeño vuelve a invertir el promedio. Incluso 750 ejemplos conserva errores individuales apreciables, aunque recupera la dirección en 91.7 % de los casos.

Para la geometría de dos capas se repitió el cálculo con dos subpaneles de 750:

| Alcance | Tamaño | Contraste medio | Sesgo | RMSE | Coincidencia de signo | Error mediano de D |
|---|---:|---:|---:|---:|---:|---:|
| Dos capas | 750 | +3.248 | +0.425 | 0.502 | **100 %** | 9.5 % |

Por tanto, la inversión de dos capas no depende de un único panel completo ni de unas pocas observaciones.

## Control de carta y precisión numérica

Se aplicó a las 7,924 coordenadas un cambio diagonal no ortogonal con factores entre 0.01 y 100, transportando \(H\). El precondicionador \(H_\phi^{-1}\) retiró el mal condicionamiento introducido por la carta. Los errores entre métricas del mismo estado fueron:

- inicial: \(1.55\times10^{-7}\);
- final real: \(1.34\times10^{-9}\);
- final aleatorio: \(1.95\times10^{-9}\).

El error inicial está dentro de la tolerancia iterativa del solucionador. Esto respalda la covariancia numérica del cálculo matricial libre de Fisher, con menor precisión que las inversiones densas de E11-J/K.

## Interpretación y estado de RIPG

E11-L establece que el signo observado en E11-J/K es una propiedad de un **alcance geométrico específico**, la última capa. No puede elevarse a una afirmación sobre la red completa. Al abrir una capa adicional, la memorización aleatoria produce una deformación mucho mayor, mientras la distancia real disminuye.

Este resultado es compatible con una lectura estructural: para etiquetas verdaderas, buena parte del cambio puede organizarse en la representación y requerir una adaptación comparativamente moderada del bloque de dos capas; las etiquetas aleatorias exigen reorganización interna adicional. Esa explicación es una inferencia sugerida por los resultados, no una identificación causal.

La formulación formal de RIPG continúa consistente. La familia regularizada permite medir distintos subespacios tangentes de forma covariante. E11-L revela que el **subespacio elegido debe formar parte explícita del estimando**, junto con \(S_P\), \(H\), \(\rho\) y la distribución del panel:

\[
G_{\rho,\mathcal U}
=B_{\mathcal U}
\left(F_{\mathcal U}+\rho\lambda_{\max}(F_{\mathcal U},H_{\mathcal U})H_{\mathcal U}\right)^{-1}
B_{\mathcal U}^T.
\]

## Siguiente paso natural

E11-M debe construir un **perfil por profundidad** con subespacios anidados: salida, dos últimas capas y red completa. La meta es localizar dónde cambia el signo y separar el aporte incremental mediante complementos de Schur o diferencias de bloques regularizados. Ese perfil debe usar los mismos modelos y paneles de E11-L para que la profundidad sea la única variable. Después podrá repetirse en datos naturales de mayor escala.

## Reproducción

Ejecutar `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 e11l_train_synthetic.py`, luego `python3 e11l_geometry.py` y `python3 e11l_plot_results.py`. El paquete incluye código, repartos, estados, métricas, residuos del solucionador, distancias, contrastes y figura.
