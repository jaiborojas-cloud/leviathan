# E11-M — perfil geométrico por profundidad

## Pregunta

E11-L encontró una inversión del contraste al ampliar la geometría desde la salida hasta las dos últimas capas. E11-M completa el perfil anidado sobre exactamente los mismos modelos, repartos y paneles:

\[
\mathcal U_1=\text{salida}
\subset
\mathcal U_2=\text{dos últimas capas}
\subset
\mathcal U_3=\text{red completa}.
\]

En cada alcance se usa

\[
G_{\rho,\mathcal U}
=B_{\mathcal U}
\left(F_{\mathcal U}+\rho\lambda_{\max}(F_{\mathcal U},H_{\mathcal U})H_{\mathcal U}\right)^{-1}
B_{\mathcal U}^T,
\qquad H_{\mathcal U}=I,\quad\rho=10^{-4}.
\]

La red completa añade la primera transformación 24→160 a las 7,924 coordenadas de E11-L y alcanza **11,924 coordenadas identificables**.

## Diseño heredado de E11-L

- Benchmark sintético controlado: 4,000 ejemplos, 24 variables y cinco clases.
- Red ReLU 24→160→48→5.
- Tres repartos de 3,000 ejemplos para entrenamiento y 1,000 para evaluación.
- Cuatro semillas por reparto; 12 pares real/aleatorio.
- Todos los modelos superaron 99 % de precisión sobre su objetivo.
- Relevancia de etiqueta verdadera, \(H=I\), \(\rho=10^{-4}\), mismos dos parámetros perspectivales.

Fisher de red completa se aplicó como operador mediante propagación tangente. Las dos columnas necesarias de la inversa regularizada se obtuvieron con gradiente conjugado. El residuo relativo máximo fue \(9.94\times10^{-7}\) con panel completo y \(9.99\times10^{-7}\) con 750 ejemplos.

## Perfil principal

Con los 1,000 ejemplos independientes:

| Alcance | Coordenadas | \(D_{real}\) | \(D_{aleatoria}\) | \(C=D_{aleatoria}-D_{real}\) | Pares con \(C>0\) | Repartos positivos |
|---|---:|---:|---:|---:|---:|---:|
| Salida | 196 | 3.070 | 1.290 | **−1.779** | 0/12 | 0/3 |
| Dos últimas capas | 7,924 | 1.354 | 4.177 | **+2.823** | 12/12 | 3/3 |
| Red completa | 11,924 | 1.096 | 4.645 | **+3.549** | 12/12 | 3/3 |

El cambio de signo ocurre al incorporar la capa 160→48. Añadir la primera capa no genera otra inversión: reduce la distancia real media de 1.354 a 1.096 y aumenta la aleatoria de 4.177 a 4.645.

Las medias de contraste por reparto en la red completa fueron +4.002, +3.407 y +3.237. La prueba bilateral de signos sobre solo tres medias tiene resolución mínima \(p=0.25\); el patrón es uniforme en esta cuadrícula, aunque el número de repartos es pequeño.

## Transiciones pareadas

Para cada uno de los 12 pares se calculó la diferencia entre contrastes de alcances consecutivos:

| Transición | Mínimo | Media | Máximo | Pares positivos |
|---|---:|---:|---:|---:|
| Salida → dos capas | +3.584 | **+4.602** | +5.400 | 12/12 |
| Dos capas → red completa | +0.529 | **+0.725** | +0.862 | 12/12 |

Estas diferencias localizan el cambio empírico, pero **no son contribuciones aditivas de cada bloque**. Cada alcance usa su propio \(\lambda_{\max}(F_{\mathcal U},H_{\mathcal U})\), por lo que cambia también la escala absoluta del regularizador. Una atribución por bloque requiere una escala común y una descomposición de Schur.

## Control con 750 ejemplos

| Alcance | Contraste medio | Sesgo frente a 1,000 | RMSE | Coincidencia de signo |
|---|---:|---:|---:|---:|
| Salida | −1.260 | +0.520 | 0.593 | 91.7 % |
| Dos últimas capas | +3.248 | +0.425 | 0.502 | 100 % |
| Red completa | +3.885 | +0.336 | 0.422 | 100 % |

Los dos alcances profundos conservan el signo en todos los subpaneles de 750. La red completa muestra incluso menor error de contraste que la salida en este control.

## Covariancia numérica

Se transformaron las 11,924 coordenadas mediante factores diagonales entre 0.01 y 100, transportando \(H\). Los errores de carta fueron:

- inicial: \(2.47\times10^{-8}\);
- final real: \(2.87\times10^{-9}\);
- final aleatorio: \(9.01\times10^{-9}\).

Todos están por debajo de la tolerancia iterativa de \(10^{-6}\). Las soluciones transformadas requirieron como máximo 413 iteraciones y conservaron residuos inferiores a \(9.94\times10^{-7}\).

## Estado de la hipótesis RIPG

E11-M localiza la frontera observada:

1. El clasificador final se deforma más con estructura verdadera que con etiquetas aleatorias.
2. Al incluir la capa que construye la representación final, la memorización aleatoria se deforma mucho más.
3. La primera capa refuerza esa diferencia sin cambiar su signo.

Por tanto, el contraste de última capa de E11-J/K no describe el comportamiento global de la red. El perfil sugiere que el aprendizaje verdadero concentra adaptación útil en el clasificador final, mientras la memorización aleatoria exige cambios geométricos internos. Esta lectura sigue siendo una inferencia: las distancias regulares por alcance no proporcionan todavía una atribución causal o aditiva.

La estructura formal de RIPG permanece consistente y gana una condición empírica adicional: además de perspectiva, referencia, regularización y panel, debe declararse el **alcance tangente**. Dos afirmaciones con distintos \(\mathcal U\) describen magnitudes diferentes.

## Siguiente paso natural

E11-N debe convertir el perfil en una atribución matemática por bloques. Se debe fijar una única escala regularizadora derivada de la red completa y descomponer

\[
F+\alpha H=
\begin{pmatrix}
A & C\\
C^T & D
\end{pmatrix}
\]

mediante el complemento de Schur. Eso permitirá separar la métrica inducida por el bloque ya incluido de la corrección condicional aportada por la nueva capa, sin interpretar simples diferencias de distancias como sumas. El mismo conjunto de E11-L/M permite hacer ese cálculo sin reentrenar modelos.

## Reproducción

Ejecutar E11-L y después `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 e11m_depth_profile.py` y `python3 e11m_plot_results.py`. El paquete incluye código, estados, métricas, residuos, controles de carta, contrastes y figura.
