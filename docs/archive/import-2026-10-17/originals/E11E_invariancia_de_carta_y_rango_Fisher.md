# E11-E — invariancia de coordenadas del estimador Fisher truncado

**Fecha:** 22 de septiembre de 2026. Continuación de E11-C/D en las mismas diez semillas y estados inicial/primer 99% de entrenamiento. Se calculó Fisher de la capa final completa para las relevancias `true` y `uniform` sobre el panel fijo de 450 imágenes.

## Prueba geométrica

Sea \(\theta=T\phi\) un cambio lineal invertible de coordenadas de la **misma** capa final. No cambian la red, sus probabilidades ni (S_P\). Las componentes transforman como

\[
F_\phi=T^T F_\theta T,
\qquad B_\phi=B_\theta T.
\]

El valor matemático de (h=BF^{-1}B^T\) (o del cociente singular exacto cuando (B\ker F=0\)) debe ser el mismo en ambas cartas. En el cálculo numérico E11-C se toma el pseudoinverso reteniendo autovalores \(\lambda>10^{-10}\lambda_{max}\) **en las coordenadas actuales**. Esa definición de rango puede cambiar bajo una congruencia no ortogonal. Se probó (T\) diagonal con escala de características entre aproximadamente:

| \(\alpha\) | Rango de escalas |
|---:|---:|
| 0 | 1 |
| 0.5 | 0.316–3.162 |
| 1 | 0.1–10 |
| 2 | 0.01–100 |

Se aplicó la misma escala por característica a los nueve logits relativos, conservando sesgos. El error observado es (d_{SPD}(h_\theta,h_\phi)\) para **el mismo estado**, no distancia entre redes.

## Resultado

| Escala \(\alpha\) | Error de carta mediano, relevancia true | Error máximo | Cambio mediano de rango retenido | (D_{0,99}\) true / random |
|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 3.576 / 5.443 |
| 0.5 | ~0 | 2.836 | 0 | 3.576 / 5.334 |
| 1 | 0.00596 | 2.861 | −8 | 3.582 / 5.323 |
| 2 | 0.318 | 6.034 | −305 | 3.620 / 4.658 |

El resumen de relevancia uniforme también tiene errores: con \(\alpha=2\), mediana 0.205 y máximo 3.851. Aunque el contraste **promedio** true/random conserva dirección en las escalas ensayadas, algunas métricas de estados individuales cambian drásticamente. Por ejemplo, en una red random de la seed 6, una escala entre 0.316 y 3.162 pierde sólo **un** modo retenido y da (d_{SPD}(h_\theta,h_\phi)=2.836\). Con \(\alpha=2\), una seed random alcanza error 6.034. Estos errores no son atribuibles a un cambio de función aprendida: sólo cambian las coordenadas.

Como control de implementación, una permutación ortogonal de las características en un estado true dejó el rango en 909 y produjo distancia de carta \(1.14\times10^{-12}\), con error máximo de entradas \(2.36\times10^{-12}\). La falla aparece con escalamiento no ortogonal y decisiones de rango relativo, como predice la ley de transformación de (F\).

## Lectura científica

El **axioma RIPG** y el cociente Fisher exacto no están refutados: este ensayo detecta que el **estimador concreto de E11-C/D, con umbral de autovalores de la matriz cruda de Fisher, no es invariante bajo reparametrizaciones generales**. Un contraste estadístico entre regímenes no subsana este defecto de coordenadas. Los resultados E11-C/D sirven como diagnósticos en una carta fijada, pero no deben presentarse aún como medidas geométricas intrínsecas verificadas para la capa final completa.

## Reparación a probar

Una selección de rango covariante necesita transportar también una **métrica de referencia** (H\): (H_\phi=T^TH_\theta T\), y cortar los autovalores generalizados de ((F,H)\), que sí son invariantes bajo ese cambio. Elegir (H\) es una hipótesis adicional y debe justificarse; fijar (H=I\) de nuevo en cada carta repetiría el problema. Una alternativa es un procedimiento de cociente de rango estable basado en incertidumbre de muestreo y verificado directamente bajo cambios de coordenadas. La siguiente fase debe construirlo, comprobar (BK=0\), comparar resultados al variar la regularización y sólo entonces reinterpretar (D_G\) o (L_G\) como intrínsecos.

Se implementó además un **control positivo de reparación** para tres estados representativos (uno true y dos random, incluyendo la seed con el mayor error de carta). Se fijó (H_\theta=I\) en la carta inicial y se transportó como (H_\phi=T^TH_\theta T\); el rango se seleccionó con autovalores generalizados (Fv=\lambda Hv\). Para \(\alpha=0.5,1,2\), y ambas relevancias, el rango retenido permaneció idéntico entre cartas y el máximo (d_{SPD}(h_\theta,h_\phi)\) fue **(3.27\times10^{-9}\)**. Ese éxito verifica la covariancia del procedimiento implementado en los casos probados; **no convierte (H_\theta=I\) en una elección canónica** ni prueba estabilidad ante otros cambios o ruido estadístico.

Los CSV contienen métricas, distancias de carta, contrastes por semilla y el control de métrica transportada. Los scripts `e11e_chart_invariance.py` y `e11e_generalized_reference.py` reproducen el cálculo desde los estados archivados de E11-C. Valores \(p\) exploratorios del contraste true/random no se usan aquí como criterio de aprobación: **el test primario es invariancia de la misma red entre cartas**.
