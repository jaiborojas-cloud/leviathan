# E11-D — modos de Fisher y cambio de signo en la geometría perspectival

**Fecha:** 22 de septiembre de 2026. Continúa E11-C con las mismas 10 semillas, redes `64→128→10`, partición fija y primer estado que alcanza 99% de accuracy de entrenamiento en cada régimen. La geometría usa la **capa final completa**, sus nueve logits relativos y 450 imágenes de referencia. Los resultados son condicionales a este modelo y panel.

## Pregunta y cálculo

En E11-C, (d(G_0,G_{99})\) era mayor en true con proyecciones de 16–32 características, pero mayor en random al incluir toda la capa final. Para localizar el cambio se diagonalizó Fisher en cada estado,

\[
Fv_j=\lambda_jv_j,\qquad
G_{(k)}=\sum_{j=1}^{k}\frac{(Bv_j)(Bv_j)^T}{\lambda_j},
\quad \lambda_1\ge\cdots\ge\lambda_k>0,
\]

y se midió la distancia SPD (d(G_{(k),0},G_{(k),99})\). El corte `full` retiene valores propios mayores que (10^{-10}\) veces el mayor; se repitió la métrica de E11-C con diferencia máxima de entradas (8.7\times10^{-11}\). Los cortes (k<\mathrm{rank}(F)\) son **diagnósticos espectrales**, no métricas plenamente admisibles del cociente original si una parte de (B\) queda en direcciones descartadas.

## Dónde se invierte el contraste

| Modos mejor determinados retenidos | Distancia true | Distancia random | Pares random > true | Fracción media de (\operatorname{tr}G_{full}\) retenida: true / random |
|---:|---:|---:|---:|---:|
| 50 | 2.916 | 1.061 | 0/10 | 12.3% / 0.8% |
| 200 | 3.281 | 1.451 | 0/10 | 29.9% / 3.0% |
| 400 | 3.317 | 2.182 | 1/10 | 52.4% / 7.7% |
| 600 | 3.349 | 3.199 | 4/10 | 73.0% / 20.3% |
| 800 | 3.407 | 4.335 | 9/10 | 91.8% / 54.7% |
| `full` | 3.576 | 5.443 | 8/10 | 100% / 100% |

La inversión ocurre al incluir direcciones menos determinadas por Fisher. En el estado de 99%, los modos **posteriores al 800** aportan en promedio ~45.3% de la traza completa de (G\) para random y ~8.2% para true. En random, los 400 modos principales explican sólo ~7.7% de esa traza. El residual medio de (B\) fuera de los primeros 400 modos es ~25.9% en random y ~0.9% en true: descartar esos modos cambia el objeto de relevancia, además de cambiar la regularización. Los valores *p* por corte, incluidos en el CSV, son exploratorios porque se inspeccionaron múltiples cortes en las mismas semillas.

## Control operativo de relevancia

Con **las mismas redes y el mismo Fisher de toda la capa final**, pero reemplazando en (S_P\) la etiqueta verdadera de cada imagen por una referencia uniforme entre clases, se obtiene:

| Relevancia | (d(G_0,G_{99})\) true | random | Dirección en pares | (p\) exacta bilateral |
|---|---:|---:|---|---:|
| Log probabilidad de etiqueta verdadera | 3.576 | 5.443 | random > true en 8/10 | 0.0078 |
| Referencia uniforme | 12.548 | 6.988 | true > random en 10/10 | 0.00195 |

Por tanto, **no existe una dirección true/random determinada sólo por Fisher o por la red**: también depende de qué relevancia (S_P\) se eligió. Ambos funcionales son explícitos, pero responden a preguntas diferentes. En el primero, random asigna a la etiqueta verdadera del panel una probabilidad mediana ~0.0012 (pérdida logarítmica media ~8.13), mientras true asigna ~0.996 (pérdida ~0.124). Esta diferencia es compatible con una amplificación del observable true en modos débiles de Fisher; no demuestra que ésa sea una causa única del efecto.

## Robustez numérica y conclusión

En la capa final completa, variar el corte relativo de Fisher de (10^{-8}\) a (10^{-12}\) cambia la distancia media random de ~4.634 a ~6.037, frente a ~3.574–3.576 en true. El residual de (B\) fuera del subespacio retenido llega a ~\(3.0\times10^{-4}\) con corte (10^{-10}\), y ~\(7.0\times10^{-3}\) con (10^{-8}\). Así, la **magnitud** del contraste completo no es estable frente a regularización espectral aun cuando su signo en estos cortes permanezca igual. La igualdad matemática (BK=0\) del observable no elimina el problema numérico de un pseudoinverso casi singular.

**Resultado de E11-D:** la inversión vista en E11-C se concentra en direcciones relativamente débiles de Fisher y puede invertirse también al cambiar la relevancia, manteniendo redes y Fisher. RIPG sigue distinguiendo geometrías condicionadas a una perspectiva, pero (D_G\) no tiene aquí una interpretación escalar universal de generalización o memorización. La siguiente prueba debe especificar primero qué direcciones son identificables con estabilidad y qué relevancia representa la pregunta científica; después podrá compararse el comportamiento bajo regularización y otros modelos.

El script `e11d_fisher_spectrum.py` reproduce los modos, métricas y distancias desde los estados archivados de E11-C. `E11D_prediction_confidence.csv` y los resultados de ambas relevancias completan el control funcional.
