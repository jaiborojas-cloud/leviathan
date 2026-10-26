# DIN-C2: implementación de generación, sin análisis

El [plan congelado](PLAN_COHORTE_CONGELADO_v1.md) y su SHA están publicados antes
que este código. [Diff completo G3→C2](cohorte/G3_to_C2_run.diff).

Se conservan sin cambios las funciones de red, puntuaciones estables, entrenamiento,
checkpoint y extracción de M/rho de G3. Cambios: un nivel s=.8; 200 splits; bases de
semillas 611000/621000/631000; IDs c2_s0000_k0; cuatro visitas autorizadas; rutas C2;
se eliminan importación y controles del análisis estadístico. La guarda no permite
leer G2/G3, Wine/Iris/T2/DIN-C1 ni importar los scripts de análisis C1/C2/potencia.
No se invoca load_wine ni load_split, aunque core.py intacto los define.

La [compuerta](cohorte_scripts/reproduce_v1.py) usa tres modelos aleatorios sin
entrenar ajenos a la cohorte; conserva sus pesos/M/f fuera de Git. Se exige error
relativo exactamente 0 y f idéntica al reconstruir. Las semillas antiguas se leen
sólo de las configuraciones publicadas y se comprueban antes de la guarda.

El [publicador](cohorte_scripts/publish_v1.py) copia valores individuales a las 12
columnas previstas. Se emite una fila por ID incluso con error o ausencia; no se
sustituye ni filtra ninguna. `script_sha256` del resumen corresponde al generador
`cohorte_scripts/run_v1.py`; `publicador_sha256` identifica el publicador. El SHA
congelado del analista se conserva en el manifiesto original. No se ejecuta.

[Archivador](cohorte_scripts/archive_v1.py): JSONL reversible bit por bit, con SHA
individual, sin borrar originales. [Verificador](cohorte_scripts/verify_v1.py):
conteos, copia exacta, SHA, ámbito aditivo, cronología y f/panel. No calcula D, p,
W, correlaciones ni medianas c/q. Los diagnósticos crudos siguen disponibles; la
compuerta de régimen y el análisis único quedan al analista después de publicar.

Todas las escrituras son exclusivas. Cualquier fallo permanece registrado y no
se sobrescribe. No hay entrenamiento de prueba de la cohorte ni selección por resultado.
