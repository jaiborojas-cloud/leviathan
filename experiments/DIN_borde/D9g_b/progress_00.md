# DIN-D9g-b: lectura previa al diseño

AGENTS.md leído. Base main0dbc973. D9g no está fusionado; se archivaron únicamente
sus tablas, configuración, resultados ya publicados y documentos por commit8996c2c
(PR#91), en sources/D9g/, con SHA. No se modifica la etapa D9g ni se leen datos C2.

El test250 de las 1.500 trayectorias ya existe: se reutilizará su pérdida escalar
exacta, con seeds711000..711099; no hay regeneración ni forward sobre test. Sólo
se derivarán tres covariables baratas nuevas del panel/pesos u30 archivados G3.
Se conocen los resultados B1 publicados (D=.02185 en s=.8), no se han calculado
bases flexibles ni asociaciones D9g-b. Se fijan B1–B4; B5 no se incluye.

El control negativo debe pertenecer a la misma base evaluada: la predicción
lineal de c30 con B4 no tiene por qué ser redundante frente a B1. Usar c_hat_j
ajustado sólo en entrenamiento de B_j garantiza esa redundancia y aplica a las
cuatro bases; se informará el coeficiente como no identificable, no como efecto0.
