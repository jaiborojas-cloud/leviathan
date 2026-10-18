# T2-A — validación de la aceleración algebraicamente equivalente

Resultado: **NOT_VALIDATED_FOR_PRODUCTION**. No se adopta la variante en la trayectoria oficial. El integrador oficial sigue pausado en el paso512, con una visita completa y tres pendientes. No se cambia ninguna clasificación, semilla, radio, tolerancia ni umbral científico.

## Qué se validó

Candidato: a = -solve(G, Jᵀ M H[v,v]), evaluado en float64. Es algebraicamente equivalente a la aceleración geodésica congelada, pero evita formar y contraer explícitamente toda la conexión. La equivalencia algebraica no garantiza equivalencia numérica.

Plan guardado antes de las pruebas: stable_acceleration_validation_plan.json. 44 puntos (4 estados internos ×11 rayos), referencias con80 y120 dígitos y11 integraciones aisladas. DOP853, rtol2e-10, atol2e-12 y513 puntos de evaluación densa en cada comparación. Los intervalos diagnósticos no reemplazan el dominio nominal oficial.

Compuerta operacional predefinida: máximo por componente de |candidato−referencia120|/(2e-12+2e-10|referencia120|) ≤1 en todas las pruebas. Es una comprobación conservadora de equivalencia instrumental, no un nuevo criterio topológico ni una afirmación de que la tolerancia local garantice por sí sola error global ≤1.

## Resultados

| Prueba | Referencia80 frente120 | Candidato |
|---|---|---|
| 5 rayos desde el centro hasta r=0.06 | Coincidencia | 5/5 pasan |
| 3 rayos difíciles desde el snapshot512, Δr=1e-6 | Coincidencia | 0/3 pasan; error escalado14.25–18.83 |
| 3 rayos difíciles desde el snapshot512, Δr=1e-5 | Coincidencia | 0/3 pasan; error escalado47.15–203.15 |

Las once referencias80 y120 producen los mismos valores float64 en las mallas comparadas. Las pruebas puntuales confirman mejora frente a la formulación original en muchos puntos difíciles, pero persiste error suficiente para incumplir la compuerta de trayectoria. En la peor prueba, el error escalado es203.147. No se amplía la tolerancia para hacerlo pasar.

Una prueba corta de un solo paso había mostrado menos rechazos. Esta validación demuestra por qué eso no bastaba para aprobar la sustitución: aceptar pasos con mayor facilidad y calcular más rápido no implica mantener exactitud suficiente en la solución.

## Interpretación y siguiente candidato

El diagnóstico de mal acondicionamiento y amplificación de redondeo sigue respaldado. Esta variante float64 es insuficiente; no es un resultado contra la hipótesis RIPG ni un diagnóstico de no inyectividad.

La siguiente opción razonable sería validar una versión separada con evaluación de precisión elevada o selectiva, manteniendo la misma ecuación, radios y tolerancias. Su regla de activación, coste y compuertas deben fijarse antes de probarla; no cambiar retrospectivamente el veredicto de esta versión. También debe comprobarse el haz completo, la calibración de área, Jacobi y topología antes de un uso oficial.

Limitaciones: mismas geometrías ya observadas, rayos aislados y segmentos finitos. Las referencias parten del mismo estado float64 almacenado y no corrigen el error acumulado anterior del checkpoint512. No se estima ahorro global ni se afirma completitud geodésica. Esta es validación instrumental exploratoria, no confirmación predictiva sobre los800 estados.

Todos los resultados se guardaron por etapas. No se avanzó ni sobrescribió el checkpoint oficial. No hay procesos activos.
