# Verificador Monte Carlo r2 — corrección congelada antes del código

El intento r1, scripts/monte_carlo_v2.py, falló con NameError:'Path' al buscar el
array sintético v1 para comparar las semillas. Faltó importar pathlib.Path en el
driver del verificador, no en el analista auditado. Se conservan driver, entorno,
controles PASS, traceback y FAILURE.json en results/monte_carlo_v2. No se guardó
ninguna réplica estadística como resultado completo en ese intento.

Corrección: agregar únicamente la importación faltante en una copia r2 y cambiar
las carpetas de salidas/arrays a nombres r2 exclusivos. No modificar r1, snapshots,
kernel, datos, config, seeds, casos ni criterios. Repetir las mismas1000 réplicas
prefijadas con los mismos índices0/1/3, no nuevos draws elegidos por resultado.
Conservar todo el fallo; no se trata como defecto del objetivo ni exclusión de
una réplica científica. La comparación por bytes con v1 sigue siendo obligatoria.
