# Cohorte · copia de G2 con cambios explícitos

SAMPLE1e88d2b se congeló ANTES de este código de entrenamiento.
El diff reproducible está en [G2_to_G3_run.diff](sources/G2_to_G3_run.diff).
Sólo cambia identificación, raíces de salida (support G3), tres semillas,
número de niveles (config), N (config), presupuesto43200s y1999 permutaciones
en los controles. Se añade comprobación de semillas G2/G3 disjuntas.

Generador, escalado train, red, Adam, lotes, updates, snapshots, extracción
de M y llamada I2 r3 son los mismos. Las funciones core/geometry/I2 y C1
originales no se modifican. Los cambios G3 de análisis se versionarán aparte;
no hay observaciones G3 reutilizadas desde el piloto.
