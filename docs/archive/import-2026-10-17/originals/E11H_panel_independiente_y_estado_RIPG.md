# E11-H — panel independiente ampliado y convergencia de la geometría

## Pregunta y diseño

¿Convergen la métrica de relevancia y las distancias del cociente al aumentar un panel **independiente del entrenamiento**, y se mantiene el contraste entre aprendizaje de etiquetas reales y aleatorias?

Para ampliar realmente la evaluación se entrenaron **modelos nuevos**: reparto estratificado y fijado por `random_state=11008` de las 1 797 imágenes de `sklearn.datasets.load_digits`, 897 para entrenar y **900 nunca vistas durante el entrenamiento** para evaluar (entre 87 y 92 por clase). Se guardó el reparto exacto. Arquitectura 64→128→10, entrenamiento Adam de E11-C con minibatches de 64, semillas 0–9 emparejadas y etiquetas reales frente a una permutación fija de las etiquetas de entrenamiento. Se guardan los estados iniciales y el primer estado con al menos 99 % de precisión sobre el objetivo, medido cada diez actualizaciones. Todos los veinte modelos llegaron a ese umbral; media de pasos 108 (real) y 1 699 (aleatorio). Exactitud media en las 900 imágenes: 95.69 % y 10.46 %, respectivamente.

Se mantuvieron los dos funcionales de relevancia anteriores: etiqueta verdadera (`true`) y clases uniformes (`uniform`). Los rasgos perspectivales (brillo y asimetría) se normalizan una vez usando el panel completo y quedan fijos. La Fisher es la categórica esperada, con \(H=I\) en la carta declarada y tres umbrales de autovalores generalizados \(10^{-8},10^{-10},10^{-12}\). Se calculó \(G=BF_H^+B^T\) con la inversa espectral truncada y \(D_{0,99}\) entre estados iniciales y finales. Para cada semilla se usaron dos extracciones de 20, 40 y 70 imágenes por clase, emparejadas entre ambos regímenes; con 20 y 40, ambas extracciones son disjuntas por clase. Las de 70 se solapan inevitablemente. El panel de referencia contiene las 900 imágenes.

## Convergencia de panel: umbral \(10^{-10}\)

El error relativo compara cada distancia con la distancia de las 900 imágenes de *la misma semilla y régimen*. Se resumen 40 distancias por tamaño y observable (10 semillas × 2 extracciones × 2 regímenes). «Coincidencia» es la dirección del contraste por extracción respecto a la dirección de esa semilla con las 900 imágenes.

| Imágenes por clase | Relevancia | Error relativo mediano | Percentil 90 | Error mediano de rango final | D media real / aleatoria | Coincidencia del signo |
|---:|---|---:|---:|---:|---:|---:|
| 20 | verdadera | 66.7 % | 156.7 % | 10.5 | 4.210 / 5.984 | 9/20 |
| 40 | verdadera | 19.5 % | 59.3 % | 5.5 | 3.469 / 3.910 | 13/20 |
| 70 | verdadera | 7.8 % | 21.5 % | 1 | 3.120 / 3.297 | 17/20 |
| 20 | uniforme | 45.1 % | 112.7 % | 10.5 | 14.075 / 8.207 | 20/20 |
| 40 | uniforme | 18.5 % | 44.5 % | 5.5 | 11.687 / 6.052 | 20/20 |
| 70 | uniforme | 5.0 % | 14.0 % | 1 | 10.507 / 5.177 | 20/20 |

Hay una reducción clara del error conforme crece el panel, pero 70 por clase aún no aproxima uniformemente las distancias completas: sus percentiles 90 son 21.5 % y 14.0 %. No contamos las dos extracciones como réplicas independientes cuando comparten imágenes.

## El contraste depende del corte y del funcional

En las **900 imágenes independientes**, las medias de distancia y la prueba bilateral exacta de inversión de signos para diez diferencias pareadas son:

| Umbral | Relevancia | D real | D aleatoria | Aleatoria − real | Semillas con contraste positivo | \(p\) bilateral |
|---:|---|---:|---:|---:|---:|---:|
| \(10^{-8}\) | verdadera | 3.114 | 2.408 | −0.705 | 1/10 | 0.0117 |
| \(10^{-10}\) | verdadera | 3.114 | 2.872 | −0.242 | 4/10 | 0.4980 |
| \(10^{-12}\) | verdadera | 3.114 | 3.560 | +0.445 | 5/10 | 0.4961 |
| \(10^{-8}\) | uniforme | 10.086 | 4.084 | −6.003 | 0/10 | 0.0020 |
| \(10^{-10}\) | uniforme | 10.139 | 4.624 | −5.515 | 0/10 | 0.0020 |
| \(10^{-12}\) | uniforme | 10.272 | 6.097 | −4.175 | 0/10 | 0.0020 |

En E11-F/G, con *otro reparto de entrenamiento* y panel de 450, el contraste para relevancia verdadera a \(10^{-10}\) era positivo (aleatoria mayor). Ahora es −0.242 y no distinguible de cero por este contraste pareado. A \(10^{-12}\) cambia de signo otra vez. Como los modelos y el reparto también cambiaron, este ensayo **no aísla** si la causa es el tamaño del panel, el reparto o la distribución de modelos aprendidos: sí descarta presentar el signo previo como robusto a esta repetición del protocolo.

## Covariancia y límites numéricos

Para la semilla 0 se verificó la transformación no ortogonal \(\theta=T\phi\), escala coordinada 0.01–100, transportando \(H_\phi=T^THT\), sin cambiar las imágenes. Ninguno de los 36 pares de cálculos alteró el rango. Error máximo de distancia entre métricas del **mismo estado**: \(2.37\times10^{-11}\) a \(10^{-8}\), \(4.73\times10^{-9}\) a \(10^{-10}\), \(5.54\times10^{-4}\) a \(10^{-12}\). En el corte extremo la aritmética de modos casi nulos ya no ofrece la misma precisión numérica; no describimos ese resultado como covariancia exacta a precisión de máquina.

El descarte de \(B\) en el panel completo es pequeño a \(10^{-10}\): máximo 0.000840 para regímenes aleatorios y 0.000082 para reales. Ese control de soporte por sí solo no estabiliza la distancia aleatoria ante el umbral.

## Estado y siguiente paso

El axioma \(\omega_P\in(\ker F)^\circ\) y la construcción del cociente siguen siendo la formulación formal de RIPG. E11-H respalda un **diagnóstico condicionado** a la perspectiva, la referencia espectral, el umbral y el panel, pero refuta para estos experimentos una lectura universal de «memorizar aleatorio induce más distancia» y deja sin identificar un valor empírico intrínseco de \(L_G\). La dependencia del corte persiste incluso en 900 ejemplos ajenos al entrenamiento.

E11-I debería separar explícitamente las fuentes del cambio observado: repetir **varios repartos independientes de entrenamiento y evaluación**, fijar antes del análisis un funcional y un criterio de regularización, y estimar por separado variación por reparto, por semilla del entrenamiento y por panel. Mientras no exista un criterio invariante y estable para escoger referencia y regularización, presentar las distancias con esas condiciones visibles.

Reproducción: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 e11h_train_independent.py` y luego `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 e11h_evaluation_convergence.py`. El paquete incluye reparto, estados guardados, curvas, métricas, errores, contrastes, controles y código; los scripts reutilizan los módulos E11-C/G originales.
