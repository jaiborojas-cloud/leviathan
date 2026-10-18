# E11-I — separar variación por reparto, semilla y panel

## Pregunta

E11-H encontró que el contraste de la relevancia asociada a etiquetas verdaderas cambió con el corte espectral y ya no reprodujo la diferencia positiva de E11-F/G. E11-I separa descriptivamente tres posibles fuentes: reparto de entrenamiento y evaluación, semilla del modelo, y selección de imágenes del panel de evaluación.

## Diseño y criterio principal

- Cuatro repartos estratificados de `load_digits` con 897 imágenes de entrenamiento y 900 de evaluación cada uno (semillas de reparto 11008, 11009, 11010 y 11011), cinco semillas de inicialización y entrenamiento comunes a los repartos; total **20 pares real/aleatorio**. El reparto 0 y sus diez modelos se reutilizaron de E11-H, y los otros 30 modelos se entrenaron para este experimento. Cada reparto tiene conjuntos internos disjuntos; los cuatro repartos **comparten imágenes entre sí** y no son cuatro conjuntos de datos independientes.
- Arquitectura MLP 64→128→10 y primer estado que supera 99 % de precisión sobre la etiqueta de entrenamiento. Todos los 40 modelos alcanzaron el criterio: promedios de 122 pasos y 95.86 % de precisión en evaluación con etiquetas reales, 1 674 pasos y 9.77 % con aleatorias.
- **Comparación principal fijada:** relevancia de log verosimilitud de la etiqueta verdadera, referencia declarada \(H=I\), autovalores generalizados \(Fv=\lambda Hv\) conservados si \(\lambda/\lambda_{\max}>10^{-10}\), distancia \(D_{0,99}\) entre métricas inicial y final, contraste pareado \(C=D_{\mathrm{aleatoria}}-D_{\mathrm{real}}\). El referente de cada par son las 900 imágenes nunca usadas para entrenar ese par.
- Para distinguir el error de panel se seleccionaron, **con el mismo subpanel para ambos regímenes y las cinco semillas de cada reparto**, dos subpaneles de 40 y dos de 70 imágenes por clase. Los dos subpaneles de 40 son disjuntos dentro de cada reparto; los de 70 se solapan. El brillo y la asimetría perspectivales se normalizan una vez por reparto sobre las 900 imágenes, y se mantienen fijos dentro de él.
- Los otros dos umbrales, \(10^{-8}\) y \(10^{-12}\), y la relevancia uniforme son controles de sensibilidad: no se usan para sustituir el criterio principal después de ver el resultado.

## Resultado principal con paneles completos

| Reparto | Media de \(C\) sobre cinco semillas |
|---:|---:|
| 0 (E11-H) | −0.610 |
| 1 | +0.160 |
| 2 | −1.059 |
| 3 | −0.438 |

Media de los veinte pares: \(D_{\rm real}=3.052\), \(D_{\rm aleatoria}=2.565\), \(C=-0.487\). Solo **7/20 pares** y **1/4 repartos** tienen contraste positivo. La prueba descriptiva bilateral de inversión de signos sobre las **cuatro medias de reparto** da \(p=0.25\); cuatro repartos solapados no justifican afirmar un efecto poblacional. La cuadrícula por reparto y semilla figura en la imagen adjunta.

La descomposición aditiva de la suma de cuadrados de esta **cuadrícula concreta 4×5** atribuye 24.3 % al término de reparto, 66.1 % al término de semilla y 9.5 % a la interacción restante (desviación cuadrática media de interacción 0.273). Las desviaciones estándar de las medias de reparto y de semilla son 0.505 y 0.805. Estas proporciones son **descriptivas y dependientes de este diseño**: las semillas, reutilizadas entre repartos, incluyen inicialización, selección de minibatches y permutación de etiquetas, y los repartos tienen imágenes en común. No son componentes de varianza poblacional identificadas causalmente.

## Error de elegir el panel

Resumen del contraste principal; el error de panel compara cada estimación con las 900 imágenes del **mismo reparto y semilla**. Hay 40 contrastes estimados por tamaño (20 pares × 2 extracciones) y 80 distancias individuales para los porcentajes de error.

| Imágenes por clase | Media de \(C\) estimado | Sesgo medio frente a 900 | Error cuadrático medio de \(C\) | Signo igual al panel completo | Error relativo mediano en D | Percentil 90 |
|---:|---:|---:|---:|---:|---:|---:|
| 40 | +0.083 | +0.570 | 1.415 | 25/40 | 37.3 % | 75.0 % |
| 70 | −0.303 | +0.184 | 0.464 | 33/40 | 8.4 % | 17.7 % |
| 900 total | −0.487 | 0 | 0 | 40/40 | 0 | 0 |

Con 40 por clase **el promedio cambia de signo** respecto al panel completo por sesgo de evaluación, aun manteniendo todos los demás elementos del cálculo. Con 70 mejora, pero tampoco permite asignar con seguridad el signo de cada par. Las extracciones usan las mismas imágenes entre las cinco semillas de cada reparto; por eso **40 observaciones no son 40 paneles independientes**.

## Sensibilidad espectral y perspectival en las 900 imágenes

| Corte | Relevancia | D real | D aleatoria | \(C\) medio | Pares con \(C>0\) | Repartos con media \(C>0\) |
|---:|---|---:|---:|---:|---:|---:|
| \(10^{-8}\) | verdadera | 3.051 | 2.318 | −0.733 | 4/20 | 0/4 |
| \(10^{-10}\) | verdadera | 3.052 | 2.565 | −0.487 | 7/20 | 1/4 |
| \(10^{-12}\) | verdadera | 3.052 | 3.775 | +0.724 | 10/20 | 4/4 |
| \(10^{-8}\) | uniforme | 10.391 | 3.910 | −6.480 | 0/20 | 0/4 |
| \(10^{-10}\) | uniforme | 10.445 | 4.267 | −6.178 | 0/20 | 0/4 |
| \(10^{-12}\) | uniforme | 10.502 | 5.850 | −4.652 | 0/20 | 0/4 |

La dirección del contraste verdadero vuelve a invertirse al conservar modos extremos. Que las cuatro **medias de reparto** sean positivas a \(10^{-12}\) no crea estabilidad: solo 10 de 20 pares lo son y la Fisher resulta numéricamente más delicada cerca de ese umbral (control de carta de E11-H). La relevancia uniforme sigue mostrando contraste negativo en estos repartos; la dirección, por tanto, depende materialmente de qué funcional \(S_P\) define la perspectiva. Esta sensibilidad persiste con paneles completos.

## Estado de RIPG y ruta

El axioma de admisibilidad \(d_\theta S_P\in(\ker F)^\circ\) y la construcción del cociente se mantienen como estructura formal. Los experimentos E11-A–I **no avalan** que la longitud observada sea una magnitud empírica única sin especificar funcional de relevancia, referencia, regularización y distribución de evaluación. E11-I muestra separadamente variación del entrenamiento y del reparto, y un sesgo de subpanel capaz de invertir el contraste promedio. Tampoco demuestra que la Fisher o el cociente sean inválidos: mide límites de una implementación finita y de un contraste propuesto.

El paso E11-J más informativo sería estudiar primero la **regularización como parte explícita del estimando**: escoger mediante una regla declarada y transportable \(H\) y un regularizador, medir convergencia de \(G\) y \(D\) con tamaños mayores y después repetir el protocolo en otro conjunto de datos. Solo con predicciones y criterios fijados antes de esa réplica tendría sentido buscar una afirmación general sobre memorizar etiquetas aleatorias.

## Reproducción y archivos

Ejecutar en orden `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 e11i_train_multisplit.py`, `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 e11i_variance_decomposition.py`, y `python3 e11i_plot_results.py`. La tabla `E11I_splits.csv` fija los repartos; `E11I_training_outcomes.csv`, los finales de entrenamiento; `E11I_heldout_metrics.csv`, las matrices y los rangos; `E11I_distances.csv` y `E11I_paired_contrasts.csv`, las distancias y pares; `E11I_full_variance_components.csv` y `E11I_panel_variation.csv`, las descomposiciones. El paquete incluye también los estados originales de E11-H necesarios para reproducir exactamente el reparto 0 y los estados nuevos de E11-I.
