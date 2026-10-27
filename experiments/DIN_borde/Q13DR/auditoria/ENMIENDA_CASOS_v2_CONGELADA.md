# Extensión prospectiva de casos v2 — sin cambiar el Monte Carlo

Se conservan código y resultados cases_v1. Los controles del motor nominal han
pasado; sus escenarios, semillas, tamaños y reglas NO cambian y siguen en curso.

La inspección de la discrepancia de medianas sugiere un caso más fuerte: N=12,
faltantes disjuntos de tres filas en un split por nivel (5% exacto), seis splits
comunes. En los comunes, c de cada fila es idéntica entre niveles y cubre [.04,.96].
En los no comunes se fija c por nivel [.99,.70,.61,.54,.42,.04]. La compuerta usa
las medianas de todas las válidas, que son estrictamente decrecientes; el bootstrap
ve c idéntica en sus seis niveles. Comprobar si el denominador de β desaparece y
si se emiten intervalos no finitos, sin modificar una línea del analista.

Corrección de presentación del auditor, antes de nuevo código: la heurística CLI
v1 etiqueta ABORTA si encuentra ese texto en stderr. Un traceback puede contener
ABORTA en la línea fuente de un if y ser realmente KeyError. Conservar la etiqueta
original y clasificar en v2 por presencia de traceback primero. La misma heurística
existe en pruebas_Q13DR.py: reportar que puede enmascarar crashes, por lectura de
su código; no ejecutar la suite ni su fixture C2.

La extensión produce archivos nuevos; no sobrescribe casos, datos ni conclusiones.
No cambia los criterios de ningún resultado científico ni las tasas Monte Carlo.
