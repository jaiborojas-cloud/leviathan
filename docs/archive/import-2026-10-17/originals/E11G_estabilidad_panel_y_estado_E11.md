# E11-G — estabilidad del panel y del rango Fisher

## Pregunta

¿Puede fijarse el rango mediante autovalores generalizados de \((F,H)\) de manera que la distancia del cociente sea a la vez covariante al cambiar de carta y estable al remuestrear el panel de evaluación?

## Diseño reproducible

- Mismos diez pares de semillas y estados 0 % y 99 % de precisión de entrenamiento del MLP 64→128→10 de E11-C/F; Fisher categórico esperado en la última capa; dos observables de relevancia ya definidos (`true`, log verosimilitud de la etiqueta verdadera; `uniform`, referencia de clases uniforme).
- Referencia declarada \(H=I\) en la carta base; autovalores generalizados \(Fv=\lambda Hv\). Se conservan \(\lambda/\lambda_{\max}>10^{-8},10^{-10},10^{-12}\). Este \(H\) depende de la declaración de coordenadas; E11-F había probado otras dos referencias.
- Panel completo: 450 imágenes. Subpaneles equilibrados de 20 o 40 imágenes **sin reemplazo** por clase, tres extracciones con semilla 11007 para cada semilla de entrenamiento. Se usa exactamente la misma extracción para el estado inicial y ambos regímenes; se mantienen diez semillas como unidades independientes, no se tratan las tres extracciones como treinta semillas independientes. Los subpaneles de 40 comparten bastantes imágenes porque cada clase del panel completo solo contiene aproximadamente 43–46.
- \(G=(BV_{\rm ret}\Lambda_{\rm ret}^{-1/2})(BV_{\rm ret}\Lambda_{\rm ret}^{-1/2})^T\), \(D_{0,99}=\|\log\operatorname{eig}(G_0^{-1}G_{99})\|_2\). La fracción de \(B\) eliminada se calcula con el complemento de los autovectores generalizados. La prueba de carta usa \(\theta=T\phi\), factor de escala por coordenada entre 0.01 y 100, \(H_\phi=T^THT\), y la **misma muestra** antes y después de transformar; se aplica en la semilla 0, dos tamaños y tres estados.

## Hallazgos principales

Umbral \(10^{-10}\). Errores respecto al panel completo sobre las 60 distancias (10 semillas × 3 extracciones × 2 regímenes) por fila; coincidencias de signo del contraste aleatorio menos real sobre 30 comparaciones pareadas:

| Imágenes/clase | Relevancia | Error relativo mediano; percentil 90 | Error absoluto mediano | Error de rango mediano; percentil 90 | Media D real; aleatoria | Signo individual frente al panel completo |
|---:|---|---:|---:|---:|---:|---:|
| 20 | etiqueta verdadera | 44.9 %; 85.1 % | 1.770 | 1; 9.1 | 4.301; 8.391 | 24/30 |
| 40 | etiqueta verdadera | 4.4 %; 10.7 % | 0.163 | 0; 4 | 3.548; 5.733 | 25/30 |
| 20 | uniforme | 27.6 %; 69.9 % | 3.283 | 1; 9.1 | 15.450; 10.867 | 30/30 |
| 40 | uniforme | 3.1 %; 6.5 % | 0.316 | 0; 4 | 12.838; 7.411 | 30/30 |

En el panel completo, las medias \(D\) son 3.576/5.443 para relevancia verdadera y 12.548/6.988 para uniforme (real/aleatoria). El promedio de los contrastes por semilla a 40 imágenes/clase es +2.184 para relevancia verdadera y −5.427 para uniforme, frente a +1.866 y −5.561 con 450 imágenes. Prueba bilateral exacta de inversión de signo aplicada a **diez promedios por semilla**: \(p=0.001953\) en ambos contrastes a 40; en panel completo \(p=0.0078125\) y \(p=0.001953\). Estos valores caracterizan este benchmark y estas definiciones, no demuestran una ley universal.

**Rango estable no implica métrica estable.** Con 40 imágenes/clase y umbral \(10^{-10}\), el error mediano del rango final es cero. Aun así, las distancias conservan error mediano de 4.4 % y 3.1 %; algunas muestras invierten el signo del contraste de relevancia verdadera frente a su semilla en panel completo. La fracción máxima de \(B\) descartada fue \(3.42\times10^{-4}\) (`true`) y \(4.94\times10^{-4}\) (`uniform`) en ese ajuste. El error de panel surge también de cómo cambian los modos *conservados* y \(B\), no solo de dónde cae el umbral.

**Dependencia del umbral.** A 40 imágenes/clase, el error relativo mediano de la relevancia verdadera es 4.85 %, 4.40 % y 3.89 % con umbrales \(10^{-8},10^{-10},10^{-12}\), respectivamente; las medias de distancia aleatoria son 4.923, 5.733 y 6.272. Aumentar el rango modifica materialmente esa geometría aunque mejore ligeramente su concordancia con el panel completo para cada umbral. No emerge un rango privilegiado solo por remuestreo.

**Control de carta.** En los 36 pares de métricas de la semilla 0, el cambio de escala con \(H\) transportado no cambió ningún rango. El mayor error de distancia entre métricas del *mismo modelo* fue \(7.56\times10^{-11}\), \(9.96\times10^{-10}\) y \(1.52\times10^{-6}\), para umbrales \(10^{-8},10^{-10},10^{-12}\), respectivamente; la última cifra refleja sensibilidad numérica de modos extremos. Este control prueba solo las cartas, estados y paneles examinados, y mantiene el mismo observable.

## Estado de E11 y camino siguiente

Los axiomas de RIPG y la definición del cociente siguen consistentes. La covariancia numérica con una referencia transportada vuelve a pasar el control. En este benchmark, la estabilidad práctica mejora al acercarse al panel completo, pero la dependencia de panel, observable, referencia declarada y corte impide asignar una distancia empírica intrínseca y universal a \(L_G\). En especial, cambiar la relevancia invierte la dirección real/aleatoria, y el control de rango por sí solo no estabiliza la métrica.

El paso E11-H razonable es ampliar el panel de evaluación **independiente** (o repetir el experimento en un conjunto mayor), fijar de antemano observable y referencia, y comprobar convergencia conjunta de \(G\), \(D\) y del contraste a través de tamaños. Si esa convergencia falla, registrar explícitamente el resultado negativo y usar la distancia solo como diagnóstico condicionado a esas elecciones.

Archivos: `E11G_panel_metrics.csv` contiene las matrices, espectro y rangos; `E11G_panel_distances.csv` las distancias; `E11G_panel_vs_full.csv` el error respecto al panel íntegro; `E11G_paired_contrasts.csv` los pares; `E11G_panel_summary.csv` el resumen; `E11G_chart_control.csv` la prueba de carta. Reproducir con `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 e11g_panel_stability.py` desde el directorio de trabajo, con los estados E11-C y módulos E11-C/E ya existentes.
