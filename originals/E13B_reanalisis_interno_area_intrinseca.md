# E13-B — reanálisis interno con áreas intrínsecas iguales

**Estado:** completado con una enmienda computacional documentada.  
**Fecha:** 23 de septiembre de 2026.  
**Prerregistro:** E13-A, áreas (A\in\{0.01,0.02,0.04\}), primaria (A_*=0.02).

## Pregunta

E13-B prueba si la separación observada en E12,

\[
|K_{\rm true}|>|K_{\rm random}|,
\]

persiste al comparar regiones que encierran la misma área intrínseca, evitando confundir curvatura con la fuerte expansión métrica de los estados `random`.

El estimando primario prerregistrado es

\[
C_A=\left(\frac1A\int_{D_A}K^2\,dA\right)^{1/2},
\qquad
\Delta C_A=C_A^{\rm true}-C_A^{\rm random}.
\]

## Implementación y enmienda computacional

Se reutilizaron sin reentrenar los 80 estados finales de E11-O: dos tareas, cuatro particiones, cinco semillas y dos regímenes. Se mantuvieron (S_P), el panel, (H=I), (ho=10^{-4}), el centro (P_0=(0,0)), las áreas y la malla de E13-A.

Una evaluación directa de (G,\partial G,\partial^2G) en las 8192 celdas por estado habría requerido decenas de miles de inversiones iterativas de Fisher. Antes de calcular contrastes pareados se fijó la siguiente enmienda:

1. calcular exactamente en (P_0) el jet analítico de segundo orden
   \[
   G(0),\quad \partial G(0),\quad \partial^2G(0);
   \]
2. transformar a coordenadas blanqueadas por (G(0));
3. construir el campo métrico cuadrático local determinado por ese jet;
4. integrar sobre él los discos geodésicos con la malla congelada de (128\times64) y 256 pasos RK4;
5. repetir el área primaria con (256\times128) y 512 pasos.

La enmienda no altera el jet en el centro: reproduce exactamente la conexión y la curvatura central de E12-D. Sí limita el alcance de E13-B a una **normalización intrínseca local**; no equivale a reconstruir exactamente el campo completo lejos del centro.

## Resultado primario: (A=0.02)

| Tarea | Pares incluidos | Mediana (C_A^{true}) | Mediana (C_A^{random}) | Mediana (Delta C_A) | Pares positivos | Particiones positivas | (p) exacto unilateral |
|---|---:|---:|---:|---:|---:|---:|---:|
| Digits | 20 | 1.609122 | 0.007169 | **1.604148** | **20/20** | **4/4** | 0.0625 |
| Wisconsin | 17 | 0.253230 | 0.007066 | **0.249999** | **16/17** | **4/4** | 0.0625 |

Las medias de contraste por partición fueron:

| Tarea | Split 0 | Split 1 | Split 2 | Split 3 |
|---|---:|---:|---:|---:|
| Digits | 2.072972 | 1.564050 | 2.243029 | 1.212023 |
| Wisconsin | 0.203552 | 0.723168 | 11.185266 | 0.018117 |

Wisconsin conserva heterogeneidad fuerte: una partición contiene valores muy grandes y un único par incluido tuvo contraste negativo, (-0.002185). Por eso la mediana es más informativa que la media poblacional.

El valor (p=0.0625) es el mínimo alcanzable con cuatro particiones bajo la prueba exacta unilateral de inversión de signos. E13-B muestra consistencia direccional, pero no puede cumplir por sí solo un umbral de 0.05.

## Robustez a las tres áreas

| Tarea | Área | Mediana (C_A^{true}) | Mediana (C_A^{random}) | Mediana (Delta C_A) | Positivos |
|---|---:|---:|---:|---:|---:|
| Digits | 0.01 | 1.604910 | 0.007169 | 1.599935 | 20/20 |
| Digits | 0.02 | 1.609122 | 0.007169 | 1.604148 | 20/20 |
| Digits | 0.04 | 1.675256 | 0.007169 | 1.668037 | 20/20 |
| Wisconsin | 0.01 | 0.192112 | 0.007060 | 0.188328 | 16/17 |
| Wisconsin | 0.02 | 0.253230 | 0.007066 | 0.249999 | 16/17 |
| Wisconsin | 0.04 | 0.852137 | 0.007078 | 0.837618 | 16/17 |

La señal no depende de seleccionar después una sola área. `Random` permanece casi plano al ampliar el disco; `true` mantiene mayor energía curvatural y, especialmente en Wisconsin, aumenta su heterogeneidad espacial.

## Exclusiones prerregistradas

Tres estados `Wisconsin-true` no pudieron encerrar las áreas objetivo dentro del jet cuadrático manteniendo una métrica positiva:

- split 0, semilla 0;
- split 0, semilla 2;
- split 2, semilla 3.

Se excluyeron los tres pares completos, sin reemplazo. Quedaron 77/80 estados y 37/40 pares: 20/20 en Digits y 17/20 en Wisconsin. Esta pérdida del 15% dentro de Wisconsin impide presentar esa tarea como una réplica interna sin reservas; es también evidencia de que su campo local es más difícil de representar mediante un jet de segundo orden.

## Auditoría numérica

| Control | Resultado |
|---|---:|
| Error relativo máximo de área | (9.88\times10^{-7}) |
| Error absoluto máximo de (K(0)) frente a E12-D | (3.29\times10^{-8}) |
| Cambio máximo de (C_{0.02}) al duplicar resolución | **0.0308%** |
| Umbral de refinamiento | 0.5% |
| Residuo máximo del solucionador | (5.00\times10^{-8}) |
| Determinante métrico mínimo en casos incluidos | 0.3367 |
| Condición métrica máxima | 71.41 |
| Error absoluto máximo holonomía–flujo | 0.00162 |
| Error relativo mediano holonomía–flujo | (8.96\times10^{-7}) |
| Error relativo máximo holonomía–flujo | 2.14% |

El máximo relativo de holonomía ocurre con flujo cercano a cero; el percentil 99 fue 0.386%. La holonomía sigue funcionando como control derivado, no como estimando independiente.

## Auditoría directa del jet fuera del centro

Se evaluó el campo analítico exacto en ocho puntos de la frontera primaria para cuatro estados representativos incluidos: Digits true/random y Wisconsin true/random.

| Caso | Error métrico relativo máximo | Error escalado máximo de (K) |
|---|---:|---:|
| Digits true | 1.017% | 17.21% |
| Digits random | 0.000055% | 0.0019% |
| Wisconsin true | 0.169% | 13.47% |
| Wisconsin random | 0.000806% | 0.144% |

El jet aproxima con gran precisión los campos casi planos `random`, pero la curvatura —que depende de segundas derivadas— es más sensible en los campos `true`. Aun usando las evaluaciones exactas de frontera, 

\[
|K_{true}|>|K_{random}|
\]

se mantuvo en 8/8 direcciones de Digits y 8/8 de Wisconsin. Esto apoya la dirección del contraste, pero las magnitudes regionales reportadas deben considerarse aproximaciones locales.

## Conclusión de E13-B

La señal central de E12 **sobrevive a la normalización por área intrínseca** en el reanálisis local:

\[
\boxed{C_{0.02}^{true}>C_{0.02}^{random}}
\]

en 36/37 pares incluidos y en 8/8 medias de partición-tarea. La expansión métrica de `random` no explica por sí sola la diferencia de organización curvatural: al comparar áreas iguales, `random` continúa casi plano y `true` conserva una curvatura RMS mucho mayor.

La formulación científicamente correcta es todavía condicional:

> En los estados internos de Digits y Wisconsin, y bajo el estimador RIPG fijado, la mayor magnitud curvatural del aprendizaje verdadero persiste en discos locales de igual área intrínseca. La evidencia es robusta a área y resolución, pero está limitada por cuatro particiones, tres exclusiones de Wisconsin y la aproximación local de segundo orden.

E13-B no es la confirmación externa. Su función es eliminar la confusión entre curvatura y expansión de área y justificar el paso a E13-C/D con una tarea y arquitectura nuevas.
