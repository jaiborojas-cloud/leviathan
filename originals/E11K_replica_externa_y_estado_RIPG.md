# E11-K — réplica externa previamente especificada

## Predicción registrada

E11-J fijó antes de esta réplica:

- relevancia: log verosimilitud de la etiqueta verdadera;
- referencia: \(H=I\) en la carta declarada;
- regularización: \(\rho=10^{-4}\);
- estimando:

\[
G_\rho=B\bigl(F+\rho\lambda_{\max}(F,H)H\bigr)^{-1}B^T;
\]

- predicción direccional: \(D_{\mathrm{aleatoria}}<D_{\mathrm{real}}\), es decir, \(C=D_{aleatoria}-D_{real}<0\).

No se escogió otro \(\rho\), observable o signo después de observar los resultados.

## Dominio y arquitectura nuevos

Se utilizó `sklearn.datasets.load_breast_cancer`, Wisconsin Diagnostic Breast Cancer: 569 observaciones, 30 variables continuas y clasificación binaria. Para cada uno de cuatro repartos estratificados se reservaron 284 observaciones para entrenamiento y 285 para evaluación. La normalización se estimó únicamente en el conjunto de entrenamiento de cada reparto.

La arquitectura fue una MLP ReLU **30→96→2**, distinta de la red 64→128→10 usada con dígitos. Se entrenaron cinco semillas comunes por reparto con etiquetas verdaderas y con una permutación fija de las etiquetas: 20 pares y 40 modelos. Todos alcanzaron al menos 99 % de precisión sobre su objetivo.

| Régimen | Pasos medios al 99 % | Precisión media de entrenamiento | Precisión media en evaluación verdadera |
|---|---:|---:|---:|
| Etiquetas verdaderas | 51 | 99.35 % | 96.54 % |
| Etiquetas aleatorias | 465 | 99.38 % | 52.88 % |

La geometría se calculó en la coordenada identificable del logit binario de la última capa, de dimensión 97. Fisher es \(E[p(1-p)uu^T]\). Los dos parámetros de perspectiva fueron radio medio y textura media, normalizados con las estadísticas de entrenamiento. Para la evaluación geométrica siempre se usaron las etiquetas verdaderas, también en redes entrenadas con etiquetas aleatorias.

## Resultado principal

Con los 285 casos reservados de cada reparto:

| Magnitud | Resultado |
|---|---:|
| \(D_{real}\), media | 4.004 |
| \(D_{aleatoria}\), media | 2.709 |
| \(C=D_{aleatoria}-D_{real}\), media | **−1.295** |
| Pares con \(C>0\) | 6/20 |
| Repartos con media \(C>0\) | **0/4** |
| Medias de reparto | −0.802, −0.560, −3.406, −0.412 |
| Prueba bilateral de signos sobre cuatro medias | \(p=0.125\) |

La predicción fijada se cumplió en el promedio total y en cada uno de los cuatro repartos. El resultado no significa que cada inicialización respete la desigualdad: seis pares individuales dieron el signo contrario. Con solo cuatro repartos, \(0.125\) es el menor valor bilateral posible cuando todos comparten dirección; esta réplica aporta evidencia descriptiva externa, no una prueba poblacional concluyente.

En la cuadrícula 4×5, la descomposición descriptiva de suma de cuadrados atribuye 29.2 % al reparto, 62.1 % a la semilla y 8.7 % a la interacción. Como los repartos comparten observaciones y cada semilla controla varios elementos aleatorios, estas fracciones no son componentes causales de varianza.

## Convergencia del panel

Los subpaneles preservan aproximadamente la proporción de clases del panel completo. Cada tamaño tiene dos extracciones por reparto, emparejadas entre regímenes y semillas. Las extracciones de 160 y 240 se solapan inevitablemente por el tamaño total disponible.

| Casos | Contraste medio | Sesgo frente a 285 | RMSE del contraste | Coincidencia de signo | Error relativo mediano de D | Percentil 90 | Error absoluto mediano |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 80 | −2.513 | −1.218 | 2.594 | 80 % | 57.7 % | 156.2 % | 1.889 |
| 160 | −1.531 | −0.236 | 1.364 | 80 % | 20.0 % | 55.7 % | 0.701 |
| 240 | −1.295 | −0.001 | 0.893 | 95 % | 9.3 % | 49.6 % | 0.253 |

El promedio de 240 casos casi coincide con el panel completo y el signo coincide en 95 % de las estimaciones. El percentil 90 relativo sigue alto porque algunas distancias de referencia son pequeñas; el error absoluto mediano muestra una caída clara. La réplica confirma de nuevo que un panel pequeño puede exagerar la magnitud y que la convergencia por promedio no garantiza precisión para cada modelo.

## Covariancia

Se aplicó al reparto 0 y semilla 0 un cambio no ortogonal con escalas coordinadas entre 0.01 y 100, transportando \(H\). El error máximo entre métricas del mismo estado fue \(6.89\times10^{-14}\). La réplica conserva el control numérico de covariancia de E11-J en una arquitectura y dimensión diferentes.

## Qué queda respaldado

E11-K aporta la primera réplica externa favorable de la hipótesis **condicionada**:

> Con relevancia de etiqueta verdadera, \(H=I\), \(\rho=10^{-4}\) y evaluación independiente suficientemente amplia, la deformación regularizada entre inicio y memorización fue menor para etiquetas aleatorias que para etiquetas verdaderas, en promedio.

El resultado apareció en un problema binario tabular y en otro tamaño de red. Junto con E11-J, deja de ser una peculiaridad exclusiva del conjunto `digits`. Aun así, la dispersión entre semillas es grande, los cuatro repartos no son conjuntos de datos independientes y la geometría sigue restringida a la última capa. Por ello todavía no hay base para una ley universal de redes profundas.

## Estado de RIPG y siguiente paso

La parte formal se mantiene: admisibilidad \(d_\theta S_P\in(\ker F)^\circ\), cociente Fisher y familia regularizada covariante cuando \(H\) se declara y transporta. La evidencia empírica ahora respalda una predicción reproducida bajo un estimando fijo, con las condiciones visibles.

El paso E11-L debería ampliar simultáneamente escala y alcance geométrico: registrar el mismo estimando en un conjunto multicategoría mayor, usar un panel independiente de miles de ejemplos y comparar geometría de última capa con una subred de dos capas. Eso permitirá saber si el contraste pertenece a la representación aprendida o solo al clasificador final. La predicción principal debe permanecer \(C<0\) con `true`, \(H=I\) y \(\rho=10^{-4}\).

## Reproducción

Ejecutar `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 e11k_external_replication.py` y `python3 e11k_plot_results.py`. El paquete incluye código, repartos, estados de los 40 modelos, métricas, distancias, contrastes y figura.
