# E12-A — canonicidad condicionada de la participación oculta

## Objetivo

E12-A somete a una compuerta de estabilidad la magnitud prioritaria cerrada en E11-O:

\[
\eta=\frac12\operatorname{tr}\!\left(
G_{\mathrm{full}}^{-1}\Delta G_{\mathrm{hidden}\mid\mathrm{output}}
\right),\qquad
\Delta\eta=\eta_{\mathrm{random}}-\eta_{\mathrm{true}}.
\]

La pregunta no es si el valor numérico de \(\eta\) es independiente de las elecciones auxiliares —E11 ya mostró que la métrica regularizada no lo es—, sino si la dirección empírica \(\Delta\eta>0\) sobrevive variaciones declaradas de \(\rho\), referencia \(H\), observables y partición oculta.

## Protocolo

Se reutilizaron sin reentrenar los 40 pares finales de E11-O:

- `digits`: MLP 64→128→10, cuatro repartos y cinco semillas;
- Wisconsin Breast Cancer: MLP 30→96→2, cuatro repartos y cinco semillas.

Se empleó el panel completo independiente de cada reparto. Cada comparación salida/subred usó una escala común

\[
\alpha=\rho\lambda_{\max}(F,H),
\]

de modo que

\[
G_{E\cup U}=G_E+\Delta G_{U\mid E},\qquad \Delta G_{U\mid E}\succeq0.
\]

El diseño fue de sensibilidad **un factor a la vez**:

1. \(\rho\in\{10^{-6},10^{-5},10^{-4},10^{-3},10^{-2}\}\), con \(H=I\), observable base y bloque oculto completo;
2. referencias tensoriales: identidad, precisión asociada a la inicialización He y balance de traza por bloques;
3. tres pares de observables independientes de las etiquetas por conjunto;
4. bloque oculto completo y cuatro particiones complementarias de unidades: mitades primera/segunda y unidades pares/impares.

Las referencias alternativas se definen en la carta base declarada y deben transportarse como formas bilineales covariantes bajo una reparametrización. No se reinicializa una diagonal nueva en cada carta.

Los sistemas de `digits` para \(\rho=10^{-7},10^{-8}\) no alcanzaron la tolerancia iterativa declarada aun con precondicionamiento de Jacobi analítico. Esos dos valores quedan como régimen numérico no resuelto y no se usan como evidencia.

## Resultado frente a \(\rho\)

| \(\rho\) | Mediana global de \(\Delta\eta\) | Mínimo individual | Pares positivos | Digits | Wisconsin |
|---:|---:|---:|---:|---:|---:|
| \(10^{-6}\) | +0.669 | +0.361 | 40/40 | 20/20 | 20/20 |
| \(10^{-5}\) | +0.561 | +0.271 | 40/40 | 20/20 | 20/20 |
| \(10^{-4}\) | +0.420 | +0.145 | 40/40 | 20/20 | 20/20 |
| \(10^{-3}\) | +0.330 | +0.053 | 40/40 | 20/20 | 20/20 |
| \(10^{-2}\) | +0.332 | **−0.054** | **38/40** | 20/20 | 18/20 |

La dirección agregada permanece positiva en cinco décadas, pero la afirmación punto por punto falla en dos pares de Wisconsin para \(\rho=10^{-2}\). Además, la magnitud cambia materialmente con \(\rho\). Por tanto, \(\eta\) no es canónica respecto a la intensidad de regularización.

## Resultado frente a la referencia \(H\)

Comparación principal a \(\rho=10^{-4}\):

| Referencia | Mediana global de \(\Delta\eta\) | Mínimo individual | Pares positivos |
|---|---:|---:|---:|
| Identidad | +0.420 | +0.145 | 40/40 |
| Precisión de inicialización | +0.316 | +0.066 | 40/40 |
| Balance por bloques | +0.296 | **+0.004** | 40/40 |

El signo sobrevive las dos referencias alternativas, aunque el margen casi se cierra en un par de Wisconsin bajo balance por bloques. La señal es estable en la familia examinada, no independiente de \(H\).

## Resultado frente a observables

En `digits` se compararon intensidad–izquierda/derecha, intensidad–arriba/abajo y centro–borde. En Wisconsin se compararon rasgos medios 0–1, rasgos 2–3 y rasgos “worst” 20–21.

| Datos | Observable alternativo | Mediana de \(\Delta\eta\) | Mínimo | Pares positivos |
|---|---|---:|---:|---:|
| Digits | arriba/abajo | +0.396 | +0.293 | 20/20 |
| Digits | centro/borde | +0.428 | +0.358 | 20/20 |
| Wisconsin | forma 2–3 | +0.514 | +0.340 | 20/20 |
| Wisconsin | worst 20–21 | +0.422 | +0.202 | 20/20 |

La dirección no depende del par observable base dentro de esta pequeña familia, pero esto no prueba universalidad sobre todos los funcionales \(S_P\).

## Resultado frente a particiones ocultas

| Subbloque oculto | Mediana global de \(\Delta\eta\) | Mínimo individual | Pares positivos |
|---|---:|---:|---:|
| Primera mitad | +0.387 | +0.209 | 40/40 |
| Segunda mitad | +0.358 | +0.101 | 40/40 |
| Unidades pares | +0.373 | +0.160 | 40/40 |
| Unidades impares | +0.378 | +0.141 | 40/40 |

La mayor participación oculta bajo memorización aleatoria no está sostenida por una sola mitad de unidades. Aparece en particiones complementarias de ambas arquitecturas. Estas particiones son controles estructurales de una capa, no sustituyen una réplica con varias capas ocultas y fronteras semánticas entre capas.

## Auditoría numérica

| Control | Resultado |
|---|---:|
| Filas de métricas | 1,040 |
| Comparaciones emparejadas | 520 |
| Residuo máximo del solucionador | \(2.0\times10^{-6}\) |
| Menor autovalor de \(\Delta G\) | \(7.9\times10^{-5}\) |
| Menor autovalor de \(G\) | \(7.72\times10^{-4}\) |
| Rango observado de autovalores generalizados | 0.0053–0.9986 |

No se aplicaron recortes espectrales a las métricas bidimensionales. La positividad de la corrección de Schur se conservó en todos los cálculos aceptados.

## Veredicto de la compuerta

Conviene separar tres nociones:

1. **Estabilidad agregada:** aprobada. La mediana de \(\Delta\eta\) es positiva en todos los conjuntos y configuraciones examinados.
2. **Estabilidad punto por punto:** aprobada para \(H\), observables, particiones y \(10^{-6}\leq\rho\leq10^{-3}\); falla en 2/20 pares de Wisconsin para \(\rho=10^{-2}\).
3. **Canonicidad numérica:** rechazada. El valor de \(\eta\) y el tamaño de \(\Delta\eta\) dependen materialmente de \(\rho\) y \(H\).

La conclusión correcta es:

> En las dos tareas naturales y las familias declaradas, la memorización aleatoria desplaza de forma robusta una fracción mayor de la geometría regularizada hacia la corrección Schur oculta. La señal es una propiedad condicional estable del protocolo, no un invariante canónico independiente de regularización, referencia u observable.

## Estado de RIPG tras E12-A

E12-A justifica avanzar a E12-B. La desigualdad de participación oculta ya no descansa en una única elección de observable, referencia o partición, pero tampoco puede elevarse a ley universal. Las conclusiones negativas de E11 permanecen: ni \(D_G\) ni el signo de su contraste temporal son universales.

La siguiente pregunta cambia de tipo. Debe construirse una familia no lineal suave

\[
P\longmapsto S_P
\]

en un vecindario bidimensional y verificar simultáneamente

\[
d_\theta S_P\in(\ker F_\theta)^\circ,
\qquad
B(P)K_\theta=0
\]

en toda la malla. Sólo después tendrá sentido calcular \(G(P;\theta)\), su conexión de Levi-Civita y su curvatura intrínseca.

## Reproducción

El paquete incluye el script principal, el agregador y todas las tablas. El análisis reutiliza los estados de E11-O. Para reproducirlo en ocho fragmentos monohilo, ejecutar `e12a_conditional_canonicity.py` con `E12_SHARD=0,...,7` y `E12_NSHARDS=8`, y después `e12a_aggregate.py`.
