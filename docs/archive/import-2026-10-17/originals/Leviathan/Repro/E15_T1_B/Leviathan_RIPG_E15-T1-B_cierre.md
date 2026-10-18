# Leviathan / RIPG — cierre E15-T1-B

**Ejecución completa: 80 estados, 320 combinaciones estado–radio y 320 tareas Jacobi. Todas las compuertas numéricas predefinidas pasan.**

La asociación entre C_A y condición de Dexp persiste al fijar el radio. En true pasa de 0.971769 nominal a 0.954918 en el radio común principal; diferencia −0.016851. El resultado se interpreta principalmente como control geométrico esperado por Jacobi. No establece causalidad ni una nueva ley.

C1-A permanece INCONCLUSIVE. Las clasificaciones T1-A no cambian. No hubo reentrenamiento, sustitución de estados, reducción de dominios C1 ni C_A artificial para los dos positivos.

## 1. Elección de radios y comparabilidad

Antes de obtener resultados nuevos se fijó b = mínimo de los 80 radios nominales archivados y los dos primeros conjugados detectados. Resultó b = 0.07596208350278867. Se aplicaron, sin optimización de correlaciones, las fracciones 0.25, 0.50, 0.75 y 0.90. El radio principal es la fracción 0.75.

| Radio | Valor | Papel |
|---|---:|---|
| r1 | 0.01899052087570 | Sensibilidad |
| r2 | 0.03798104175139 | Sensibilidad |
| r3 | 0.05697156262709 | Principal |
| r4 | 0.06836587515251 | Sensibilidad |

Estos radios son inferiores al menor radio nominal (0.07712801675414226) y a los plegados conocidos. El uso de límites previos selecciona una región numéricamente segura; no selecciona un umbral predictivo mediante los dos positivos. La validez se comprobó por SPD, determinante positivo en prefijos muestreados, bordes simples y acuerdo entre 256/512 direcciones, ambas fases. No es un certificado global de inyectividad.

Se conserva el núcleo exacto M/f de RIPG, P0=(0,0), rho=1e-4, arquitectura y checkpoints C1. DOP853 mantiene rtol=2e-10 y atol=2e-12. Se usa Jacobi con j(0)=0, j′(0)=1 y det Dexp=j/r en marcos intrínsecos; κ=max(1,|j/r|)/min(1,|j/r|).

El primario es el máximo angular **sobre el borde**. Se guardó también el máximo en el prefijo del disco para compararlo con el resumen previo de T1-A. En este panel sus correlaciones coinciden en cada escala; la persistencia no se debe a cambiar de resumen. C_A conserva su dominio nominal original: el análisis uniforma la escala de Dexp, no redefine C_A.

## 2. Correlaciones y sensibilidad

| Régimen | Radio | n con C_A | Spearman común | Diferencia vs nominal | Intervalo descriptivo 95% de rho |
|---|---:|---:|---:|---:|---:|
| true | r1 | 38 | 0.911807 | -0.059963 | [0.656186, 0.978175] |
| true | r2 | 38 | 0.943101 | -0.028668 | [0.769857, 0.986570] |
| true | r3 | 38 | 0.954918 | -0.016851 | [0.821449, 0.986848] |
| true | r4 | 38 | 0.967174 | -0.004596 | [0.873675, 0.989840] |
| random | r1 | 40 | 1.000000 | +0.000375 | [1.000000, 1.000000] |
| random | r2 | 40 | 0.999625 | +0.000000 | [0.997178, 1.000000] |
| random | r3 | 40 | 0.999625 | +0.000000 | [0.997178, 1.000000] |
| random | r4 | 40 | 0.999625 | +0.000000 | [0.997178, 1.000000] |

En el primario true: rho = 0.954918; intervalo descriptivo del cambio [-0.084833, 0.008267]. Nominal true = 0.971769; nominal random = 0.999625.

Bootstrap: 5000 remuestreos de ocho bloques split, conservando los estados disponibles de cada bloque y usando los mismos remuestreos para las diferencias pareadas; semilla 151510. Son intervalos de sensibilidad descriptivos: los splits comparten Wine y no representan datasets independientes. No se calculan p-valores ni una confirmación sobre estos 80 estados.

| Régimen | Comprobación en r3 | Rango de rho |
|---|---|---:|
| true | Dentro de split | 0.500000 – 1.000000 |
| true | Excluir cualquiera de los ocho splits | 0.933489 – 0.971257 |
| true | Excluir cualquiera de los estados | 0.951162 – 0.972499 |
| random | Dentro de split | 1.000000 – 1.000000 |
| random | Excluir cualquiera de los ocho splits | 0.999440 – 1.000000 |
| random | Excluir cualquiera de los estados | 0.999595 – 0.999798 |

La asociación true permanece alta al retirar cualquier estado; no la sostiene un único extremo. Las correlaciones dentro de cada split usan sólo cinco inicializaciones, y tres en split 0 para C_A; no deben sobreinterpretarse. En random, κ en r3 va de 1.00000000145 a 1.00000797510: el orden casi perfecto corresponde a deformaciones minúsculas, no a proximidad a un pliegue.

## 3. Los dos positivos antes del plegado

| Estado | Radio | κ máximo | Rango entre 40 true | Top 10% predefinido |
|---|---|---:|---:|---|
| split0_j1_true | r1 | 1.055558815 | 1/40 | Sí |
| split0_j3_true | r1 | 1.002925400 | 15/40 | No |
| split0_j1_true | r2 | 1.396555032 | 1/40 | Sí |
| split0_j3_true | r2 | 1.098835225 | 8/40 | No |
| split0_j1_true | r3 | 3.082204585 | 1/40 | Sí |
| split0_j3_true | r3 | 1.637514952 | 2/40 | Sí |
| split0_j1_true | r4 | 8.671506628 | 1/40 | Sí |
| split0_j3_true | r4 | 3.744366301 | 2/40 | Sí |

En el principal r3 los positivos ocupan los lugares 1 y 2, con κ≈3.082205 y 1.637515, y mínimos |det|≈0.324443 y 0.610681. Ambos siguen antes del primer conjugado. **Esto no ocurre a todas las escalas:** j=3 ocupa los lugares 15 y 8 en r1 y r2. No se puede presentar un condicionamiento extremo infinitesimal como propiedad ya demostrada.

La cola se había fijado como top 4/40 antes del nuevo cálculo. Los estados positivos ya eran conocidos: su ubicación en la cola es exploratoria, no confirmación de una regla predictiva ni razón para recalibrar el radio. No tienen C_A ni residuo respecto de una tendencia C_A asignados artificialmente.

## 4. Residuos prioritarios

Se ajustó una tendencia monótona creciente por regresión isotónica de log10(C_A) a log10(max(κ−1,1e-12)), dejando un split completo fuera en cada predicción. Un residuo grande se definió antes del cálculo como |e|>log10(2): error mayor que factor 2 en la **deformación κ−1**, no en κ. Las extrapolaciones se limitan al rango de entrenamiento y se marcan.

En r3 hay 7/38 residuos true grandes y 1/40 random. La mediana de error absoluto true es 0.163092 y la media 0.199217 en unidades log10. Un residuo no identifica por sí mismo un mecanismo geométrico: puede contener error de la tendencia, falta de cobertura del predictor y estructura omitida.

| Estado | Residuo log10 | Deformación observada / predicha | Extrapolación limitada |
|---|---:|---:|---|
| split0_j0_true | +0.357026 | 2.275231 | No |
| split0_j4_true | +0.323845 | 2.107877 | No |
| split1_j1_true | +0.612225 | 4.094729 | No |
| split5_j1_true | -0.765003 | 0.171790 | No |
| split6_j1_true | -0.527272 | 0.296980 | Sí |
| split6_j3_true | +0.387014 | 2.437891 | No |
| split7_j1_true | +0.400303 | 2.513641 | No |
| split6_j0_random | -0.434662 | 0.367569 | Sí |

El caso true más marcado es split5/j1: la deformación observada es 0.1718 veces la predicha (la tendencia sobrepredice por ≈5.82), z robusto≈−3.20, sin extrapolación. Split1/j1 tiene ≈4.09 veces lo predicho. Split6/j1 true y split6/j0 random tienen extrapolación limitada, por lo que no se interpretan como evidencia limpia de estructura omitida. El residuo random ocurre con κ−1≈1.45e-9; un z enorme debido a MAD diminuta no lo convierte en un gran efecto geométrico.

### Variables que describen las desviaciones

| Variable, true en r3 | rho con residuo firmado | rho con magnitud del residuo |
|---|---:|---:|
| lambda_1pct | -0.287887 | +0.365357 |
| lambda_01pct | -0.305394 | +0.383740 |
| R_eff | +0.293358 | -0.362293 |
| frac50 | +0.311303 | -0.349601 |
| frac90 | +0.156801 | -0.304081 |
| nominal_radius | +0.346756 | +0.007769 |
| angular_K_abs_cv | +0.031404 | +0.092023 |
| angular_K_peak_to_rms | +0.078674 | +0.271912 |
| angular_K_top10_energy | +0.009957 | +0.218295 |
| K_rms | +0.048911 | +0.333844 |

La concentración espacial muestra asociaciones moderadas con la magnitud del residuo: Lambda0.1%≈0.384, Lambda1%≈0.365 y R_eff≈−0.362. El radio nominal se asocia débil a moderadamente con el signo (≈0.347), no con la magnitud (≈0.008). La anisotropía de K en el borde no ofrece una explicación fuerte: CV angular con el residuo firmado≈0.031; pico/RMS≈0.079; concentración angular top10%≈0.010.

La asociación firmada con Lambda0.1% se debilita a ≈−0.032 al retirar split5 y a ≈−0.149 al retirar split6: no es una relación robusta y general ya establecida. En random aparecen asociaciones de rangos≈0.76 con concentración/anisotropía, sobre deformaciones casi nulas y un régimen de errores de la tendencia muy pequeño; se conservan exploratorias, sin inferencia de importancia geométrica.

No se ha identificado qué estructura **explica** los residuos. La distribución radial y angular de K a lo largo de trayectorias completas, su signo y la organización del campo son hipótesis pendientes. Sólo se midió K de borde y concentración espacial previa; no se cartografió el cut locus ni se efectuó minimización independiente de distancias. Los 38 true con residuos tienen r_conj no detectado y A_embed censurada; los dos con evento no tienen C_A. Por ello no puede estimarse una asociación residuo–r_conj/A_embed sin fabricar información.

## 5. Área objetivo y observables adimensionales

La caída de rho en el radio principal (0.016851) no activa la definición preestablecida de caída sustancial (>0.10). Ninguno de los cuatro radios produce una caída mayor de 0.10. La fuerte asociación no desaparece al fijar el radio, de modo que no se explica principalmente por diferencias en los radios nominales.

En true, rho(C_A,Rnom)≈0.166, rho(Rnom,κnom)≈0.255 y rho(Rnom,κcomún)≈0.245. La correlación parcial de rangos C_A–κcomún condicionada a Rnom es≈0.956. Son ajustes descriptivos, no identificación causal ni prueba de mediación.

La mediana de (κnom−1)/(κcomún−1) es≈2.447 en true y≈1.966 en random. Usar radios nominales generalmente mayores sí cambia apreciablemente la **amplitud** de la deformación. Esa comparación combina crecimiento con la escala y heterogeneidad de radios; no asigna una fracción causal a la regla A=0.02.

| Candidato, true en r3 | Spearman | MAE fuera de split, log10 |
|---|---:|---:|
| CA | 0.954918 | 0.199217 |
| CA_A_over_4pi | 0.954918 | 0.199217 |
| CA_Rnom_squared | 0.954262 | 0.203024 |
| CA_rcommon_squared | 0.954918 | 0.199217 |

C_A tiene unidades de curvatura, así que C_A A/(4π) y C_A r² son adimensionales. Con A o r común fijos son simples reescalamientos: no pueden mejorar el orden de Spearman ni agregar información. C_A Rnom² sí cambia entre estados, pero aquí no mejora: MAE≈0.203024 frente a≈0.199217 de C_A. **No hay evidencia para reemplazar C_A por un observable adimensional superior.** C1 queda intacto.

## 6. Jerarquía de evidencia

| Nivel | Hallazgos | Alcance |
|---|---|---|
| EXPECTED_GEOMETRIC_CONTROL | Persistencia C_A–κ a escala común; crecimiento de deformación con radio | Coherencia interna con Jacobi, no descubrimiento causal inesperado |
| EXPLORATORY_STRUCTURE | Siete residuos true; dependencia con escala del rango de j3; concentración moderadamente asociada al error; dos positivos en cola en r3 | Mismo panel de descubrimiento, mecanismo no identificado |
| NEW_HYPOTHESIS | Transportabilidad del ranking de κ(r3) como indicador de enriquecimiento de no inyectividad posterior en estados nuevos | Hipótesis predictiva limitada; aún no validada, no ley nueva ni nuevo score de curvatura |

La ecuación que organiza la interpretación es j″(s)+K(γθ(s))j(s)=0. La evolución de j y, por tanto, de Dexp depende de la curvatura a lo largo de cada geodésica. Un RMS regional C_A no codifica por sí solo signo, distribución radial o dirección. La asociación observada es coherente con ese control; los residuos no demuestran qué componente omitida lo produce.

## 7. Integridad, persistencia y límites

- C1: CRC y SHA del ZIP correctos; 1925/1925 entradas internas correctas. A2: CRC y SHA correctos; 581/581 entradas correctas.
- T1-A: paquete de resumen verificado contra SHA externo; 80 ZIP por estado coinciden con sus hashes; 80 checkpoints y 780 arrays finales verificados.
- Salvedad conservada: el manifiesto T1-A enumera 2194 archivos y un temporal histórico no está en el ZIP; los otros 2193 coinciden y el array final correspondiente está íntegro. No se fabricó el temporal ni se modificó T1-A.
- T1-B: 80/80 checkpoints conservados, 320/320 combinaciones válidas, 320 tareas Jacobi, todos los paquetes por estado guardados. Criterios, scripts y hashes acompañan los resultados.
- CPU nueva agregada por estado: 404.152 s; suma de tiempos de pared por estado: 404.256 s. Son costes de estados; cuatro procesos y guardados se solapan. El coste de bootstrap, informes y guardado no está incluido en esas cifras.
- Un conflicto de versión de la tabla acumulada se resolvió leyendo la versión actual, verificando las 144 filas idénticas y agregando 16; no hubo recálculo.

La precisión y ausencia de eventos se refieren a las pruebas realizadas. No hay certificación exacta de inyectividad global, mecanismo causal identificado ni validación fuera de Wine en esta etapa. El bootstrap y dejar splits fuera siguen usando el panel de descubrimiento: no sustituyen estados nuevos.

## 8. Respuestas obligatorias

1. **¿Persiste a radio común?** Sí. True: rho entre 0.911807 y 0.967174 en los cuatro radios; 0.954918 en el principal.
2. **¿Cuánto cambia?** En r3 baja de 0.971769 a 0.954918: −0.016851. Intervalo descriptivo del cambio [−0.084833, +0.008267].
3. **¿Los dos positivos están en la cola antes del plegado?** En r3 y r4 ocupan los lugares 1 y 2 de 40. j3 no está en el top10% de r1/r2: ocupa 15 y 8.
4. **¿Hay residuos grandes?** Sí: 7/38 true y 1/40 random superan el criterio factor 2 en κ−1. Dos están afectados por extrapolación limitada.
5. **¿Qué variables los describen mejor?** La concentración espacial tiene asociaciones moderadas con |residuo|; radio nominal con su signo. No emerge un descriptor fuerte ni una explicación por anisotropía de borde.
6. **¿Es principalmente un control esperado por Jacobi?** Sí; ésa es la interpretación principal de la correlación.
7. **¿El área fija aporta vía Rnom?** Poco cambio en el orden correlacional, pero cambio de amplitud: deformación nominal/común mediana≈2.447 en true. No se identifica mediación causal.
8. **¿Hay un adimensional nuevo mejor?** No. Reescalar por área o radio común no agrega información; C_A Rnom² no mejoró el error.
9. **¿Qué nivel tiene cada hallazgo?** Correlación: EXPECTED_GEOMETRIC_CONTROL. Residuos y rangos: EXPLORATORY_STRUCTURE. Transportabilidad futura de la cola de κ: NEW_HYPOTHESIS.
10. **¿Qué confirmar en estados nuevos?** Persistencia de la asociación bajo protocolo fijo, enriquecimiento prospectivo de no inyectividad en la cola predefinida y reproducción de desviaciones; cualquier mecanismo de residuos exige medir trayectorias y validación posterior independiente.

## 9. Continuación

Se entrega un diseño T2 para una hipótesis de transportabilidad predictiva limitada, con radio, observable, dirección, población futura y compuertas explícitos. **T2 no se ejecutó ni se abre automáticamente.** Los dos positivos actuales no se usan como confirmación de ese diseño. No se propone un reemplazo de C_A ni se reabre C1.

Tablas: common_radius_results.csv, correlations.csv, stability.csv, residuals.csv, large_residuals.csv, positive_cases.csv, residual_feature_correlations.csv, area_effect.csv y dimensionless_candidates.csv. Protocolos, modelos isotónicos, costes, errores, manifiesto y paquetes por estado permiten recuperar exactamente la ejecución.

![Sensibilidad al radio](correlation_sensitivity.png)

![Condición a radio común y positivos](common_radius_and_positive_cases.png)

![Residuos](residual_diagnostics.png)
