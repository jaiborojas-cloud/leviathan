# Declaración de entorno v2, sin cambiar mediciones v1

El requirements.txt congelado conserva NumPy/SciPy/MPMath, pero omitía la
dependencia transitiva Shapely del audit.py autorizado importado por AF,
y Autograd de la fuente D utilizada sólo por el control plano.
La corrida v1 ya usa Shapely2.1.2 y Autograd1.8.0 instalados antes de su inicio; el import y
los controles pasaron en ese entorno. requirements_runtime_v2.txt añade esas
mismas versiones para reproducirlo. Se conserva la declaración inicial y sus
hashes; no cambia el entorno ejecutado, código científico, estados, reglas ni
resultados. Es una corrección documental del entorno, sin repetir geometría.
