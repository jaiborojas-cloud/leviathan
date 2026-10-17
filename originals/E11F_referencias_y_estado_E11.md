# E11-F — referencias transportadas y estado de la investigación E11

**Fecha:** 22 de septiembre de 2026. Continuación de E11-E sobre los mismos diez pares de redes y los estados inicial / primer 99% de accuracy de entrenamiento. Fisher corresponde a los nueve logits relativos de la **capa final** y a las 450 imágenes fijas; los funcionales de relevancia son `true` y `uniform`.

## Pregunta

E11-E reparó la invariancia entre cartas usando un corte de autovalores **generalizados** de \((F,H)\), siempre que la métrica de referencia adicional \(H\) se transporte como tensor. E11-F pregunta: **¿cuánto depende el contraste empírico de la elección de (H\), manteniendo esa covariancia?**

Se fijaron tres referencias en la carta inicial de cada semilla, compartidas por sus ramas true/random:

\[
H_1=I,\qquad
H_2=F_0+\tau I,\qquad
H_3=\operatorname{diag}(F_0)+\tau I,
\qquad \tau=10^{-3}\lambda_{\max}(F_0).
\]

Al cambiar coordenadas \(\theta=T\phi\) se transportan **ambos** tensores: \(F_\phi=T^TF_\theta T\), \(H_\phi=T^TH_\theta T\) y \(B_\phi=B_\theta T\). Se probaron cortes relativos \(10^{-8},10^{-10},10^{-12}\) sobre los autovalores generalizados. Elegir \(H\) y el corte sigue siendo una decisión científica y numérica; estas tres alternativas no agotan las posibilidades.

## Resultado a corte \(10^{-10}\)

| Referencia | Relevancia | (D_{0,99}\) true | random | Pares random > true |
|---|---|---:|---:|---:|
| (I\) | Etiqueta verdadera | 3.576 | 5.443 | 8/10 |
| (F_0+\tau I\) | Etiqueta verdadera | 3.577 | 5.707 | 8/10 |
| (\operatorname{diag}(F_0)+\tau I\) | Etiqueta verdadera | 3.577 | 5.708 | 8/10 |
| (I\) | Uniforme | 12.548 | 6.988 | 0/10 |
| (F_0+\tau I\) | Uniforme | 12.572 | 7.198 | 0/10 |
| (\operatorname{diag}(F_0)+\tau I\) | Uniforme | 12.563 | 7.180 | 0/10 |

En estas referencias, el **signo** del contraste permanece fijado por la relevancia elegida. La **magnitud** no queda determinada: con relevancia de etiqueta verdadera, al cambiar el corte de \(10^{-8}\) a \(10^{-12}\), la distancia media random pasa de aproximadamente 4.63 a 6.04 con \(H_1\), y de 4.63 a 6.28 con \(H_2/H_3\); true permanece cerca de 3.57–3.58. Con relevancia uniforme también varían las magnitudes, aunque true supera a random en los diez pares para cada referencia y corte examinados. Los valores *p* de las tablas son exploratorios porque se inspeccionaron múltiples referencias, cortes y relevancias.

## Control de carta

En un estado true y uno random, tanto al inicio como al 99%, se aplicó la reescala no ortogonal más fuerte de E11-E (factores ~0.01–100). Se transportaron (F,H,B\) y se repitió la descomposición generalizada con \(H_2\) y \(H_3\). En los 16 casos (2 semillas × 2 estados × 2 referencias × 2 relevancias), el rango retenido fue idéntico entre cartas. El mayor error (d_{SPD}(G_\theta,G_\phi)\) fue \(4.19\times10^{-9}\). La referencia transportada corrigió el fallo de invariancia del corte sobre el espectro crudo **en los cambios lineales probados**. No establece invariancia ante cualquier cambio no lineal ni elimina el problema de selección de rango.

## Estado de E11-A → E11-F

| Fase | Lo que estableció | Límite actual |
|---|---|---|
| E11-A | La variación entre paneles Fisher sobre un modelo congelado podía igualar o superar saltos temporales cortos. | El observable prospectivo no reconstruye exactamente E10. |
| E11-B | La métrica se aproxima a la referencia empírica al ampliar el panel hasta casi todo el test; se midió una trayectoria discreta con panel fijo. | No se demostró convergencia temporal de la longitud total; la red pequeña random no memorizó. |
| E11-C | Una red mayor memorizó etiquetas random hasta ~99% en 10 semillas; un contraste geométrico a train accuracy emparejada fue observable. | La dirección se invirtió al ampliar de 16–32 características proyectadas a la capa final completa. |
| E11-D | El cambio de signo se concentró en modos relativamente débiles de Fisher; variar sólo (S_P\) también invirtió el contraste. | Cortar modos cambia la relevancia representada; magnitudes sensibles al pseudoinverso. |
| E11-E | Un umbral relativo del espectro crudo falló la invariancia de carta; la métrica de referencia transportada restauró invariancia en estados de control. | (H\) fue una estructura adicional elegida, no derivada canónicamente. |
| E11-F | Tres referencias transportadas y tres cortes conservan el signo dentro de cada relevancia en estas redes; (H_2/H_3\) pasan controles de reescala. | La magnitud random varía con el corte; falta justificar rango, (H\) y reproducibilidad fuera de `digits`. |

**Conclusión de E11 hasta ahora:** el axioma \(\omega_P\in(\ker F)^\circ\) y \(BK=0\) sigue siendo la regla formal. La métrica inducida refleja elecciones operativas de relevancia. Para la capa final de estas redes es posible hacer **covariante entre las cartas ensayadas** el procedimiento numérico de rango usando (H\) transportado; no hay todavía una elección intrínseca y estadísticamente estable de los modos débiles. No se sostiene una ley universal del sentido true/random de (D_G\), ni utilidad predictiva o causalidad general.

## Siguiente cálculo natural: E11-G

Estimar por remuestreo del panel de evaluación la incertidumbre de los **autovalores generalizados** de \((F,H)\), y definir por anticipado una regla de rango que conserve sólo modos cuyo valor sea estable frente a tamaño y composición del panel. Transportar (H\) en un cambio de carta independiente y medir simultáneamente: error de invariancia, variación de (G\) entre paneles y estabilidad del contraste true/random. Si no aparece una ventana donde los tres controles pasan, registrar el resultado negativo y no usar (L_G\) como magnitud intrínseca empírica de estas redes. Este control es prioritario frente a más benchmarks de accuracy.

Los CSV `E11F_generalized_metrics.csv`, `E11F_paired_distances.csv`, `E11F_reference_sensitivity_summary.csv` y `E11F_transported_reference_control.csv` permiten reproducir las comparaciones desde los estados archivados de E11-C.
