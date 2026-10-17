# E11-N — atribución por bloques mediante complementos de Schur

## Objetivo

E11-M localizó el cambio del contraste al ampliar el alcance geométrico, pero cada alcance usaba su propio \(\lambda_{\max}\). Las diferencias de distancias no podían interpretarse como aportes de las capas. E11-N fija, para cada estado y panel, una escala única derivada de la red completa:

\[
\alpha=\rho\lambda_{\max}(F_{completa},H),
\qquad \rho=10^{-4},\quad H=I,
\]

y usa exactamente ese mismo \(\alpha\) en salida, dos últimas capas y red completa.

## Descomposición

Para un alcance ya incluido \(E\) y un bloque nuevo \(U\), la Fisher regularizada común se escribe

\[
F+\alpha H=
\begin{pmatrix}
A & C\\
C^T & D
\end{pmatrix},
\qquad
B=(B_E\;B_U).
\]

Con

\[
S=D-C^TA^{-1}C,
\qquad
R=B_U-B_EA^{-1}C,
\]

la métrica ampliada satisface

\[
\boxed{
G_{E\cup U}=G_E+\Delta G_{U\mid E},
\qquad
\Delta G_{U\mid E}=RS^{-1}R^T\succeq0.
}
\]

Se calcularon dos correcciones:

1. capa 160→48 condicionada a la salida;
2. capa 24→160 condicionada a las dos capas posteriores.

Operacionalmente, las correcciones se obtuvieron como diferencia de métricas anidadas bajo el mismo \(\alpha\), equivalente a la fórmula anterior. La positividad fue comprobada estado por estado.

## Diseño

Se reutilizaron los 24 modelos, tres repartos, cuatro semillas y paneles de E11-L/M. No hubo nuevo entrenamiento ni selección de hiperparámetros. La red completa contiene 11,924 coordenadas identificables. Las inversiones de dos capas y red completa se resolvieron por gradiente conjugado; el residuo relativo máximo fue \(9.98\times10^{-7}\) con 1,000 ejemplos y \(10.00\times10^{-7}\) con 750.

## Perfil total con escala común

| Alcance | \(D_{real}\) | \(D_{aleatoria}\) | Contraste | Pares positivos | Repartos positivos |
|---|---:|---:|---:|---:|---:|
| Salida | 3.107 | 1.187 | **−1.920** | 0/12 | 0/3 |
| Dos últimas capas | 1.390 | 4.114 | **+2.724** | 12/12 | 3/3 |
| Red completa | 1.097 | 4.645 | **+3.548** | 12/12 | 3/3 |

La escala común conserva el perfil de E11-M. La inversión no era un artefacto de normalizar cada alcance con un \(\lambda_{\max}\) distinto.

## Trayectoria de las correcciones de Schur

Cada \(\Delta G\) define una métrica 2×2 positiva definida en este experimento. Se midió su propia distancia entre estado inicial y final:

| Corrección condicionada | \(D_{real}\) | \(D_{aleatoria}\) | Contraste | Pares positivos | Repartos positivos |
|---|---:|---:|---:|---:|---:|
| Capa intermedia dada la salida | 1.088 | 4.531 | **+3.443** | 12/12 | 3/3 |
| Primera capa dadas las posteriores | 0.854 | 6.216 | **+5.362** | 12/12 | 3/3 |

La deformación aleatoria supera claramente a la real en ambas correcciones. El bloque intermedio produce la transición de signo del total; la primera capa añade otra corrección cuya trayectoria diferencia aún más ambos regímenes.

Las distancias de las correcciones **no se suman** para obtener la distancia total: la distancia SPD es no lineal y los bloques interactúan. La aditividad válida ocurre en las métricas de cada estado, \(G_{E\cup U}=G_E+\Delta G_{U\mid E}\).

## Positividad y peso de cada bloque

El menor autovalor observado entre todas las correcciones, estados, semillas y paneles fue **0.774**. No hubo correcciones indefinidas ni necesidad de recortar autovalores.

Fracción de traza de la corrección respecto a la métrica ampliada, panel completo:

| Bloque | Inicial, mediana | Final real | Final aleatorio |
|---|---:|---:|---:|
| Intermedio condicionado a salida | 66.7 % | 92.7 % | 96.5 % |
| Primera capa condicionada a posteriores | 13.5 % | 33.7 % | 40.8 % |

La capa intermedia domina la métrica de dos capas después del entrenamiento en ambos regímenes. La primera capa adquiere más peso bajo memorización aleatoria que bajo aprendizaje real. La traza depende de las coordenadas perspectivales fijadas; aquí sirve como comparación interna porque esas coordenadas permanecen iguales.

## Control con 750 ejemplos

| Componente | Contraste | Sesgo frente a 1,000 | RMSE | Coincidencia de signo |
|---|---:|---:|---:|---:|
| Salida total | −1.433 | +0.487 | 0.558 | 100 % |
| Dos capas total | +3.145 | +0.421 | 0.498 | 100 % |
| Red completa total | +3.882 | +0.334 | 0.421 | 100 % |
| Corrección intermedia | +3.795 | +0.352 | 0.436 | 100 % |
| Corrección de primera capa | +5.497 | +0.135 | 0.325 | 100 % |

La atribución conserva la dirección en todos los subpaneles evaluados.

## Covariancia numérica

Se aplicó un cambio diagonal con factores entre 0.01 y 100, respetando los bloques y transportando \(H\). Error máximo de carta:

- salida: \(3.69\times10^{-15}\);
- dos últimas capas: \(9.01\times10^{-8}\);
- red completa: \(2.08\times10^{-8}\).

Los errores de los alcances iterativos permanecen por debajo de la tolerancia de solución \(10^{-6}\).

## Estado de RIPG

E11-N convierte el perfil descriptivo de E11-M en una atribución métrica válida bajo regularización común. En este benchmark:

- la salida favorece mayor deformación para estructura verdadera;
- el bloque intermedio introduce la inversión;
- la primera capa refuerza la deformación asociada a memorizar etiquetas aleatorias;
- ambas correcciones son positivas y covariantes bajo transformaciones que preservan la partición por bloques.

La conclusión permanece condicionada a \(S_P\), \(H\), \(\rho\), panel, arquitectura y partición elegida. Además, el benchmark de E11-L/N es sintético. La atribución matemática está validada; su generalidad empírica todavía requiere datos naturales.

## Siguiente paso natural

E11-O debe aplicar esta misma atribución Schur, sin cambiar \(S_P\), \(H\) ni \(\rho\), a los modelos naturales ya entrenados:

1. `digits` de E11-J, comparando salida frente a red 64→128→10 completa;
2. Wisconsin de E11-K, comparando salida frente a red 30→96→2 completa.

Ambas arquitecturas tienen una sola capa oculta, por lo que la corrección oculta condicionada a la salida puede medirse directamente. Si su contraste también es positivo mientras la salida es negativa, el patrón de profundidad obtendría dos réplicas naturales sin reentrenar modelos.

## Reproducción

Ejecutar E11-L/M y después `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 e11n_schur_attribution.py` y `python3 e11n_plot_results.py`. El paquete incluye código, estados, métricas comunes, correcciones Schur, controles y figura.
