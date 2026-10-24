# Ejecución AG v1

Diseño e9e4034 anterior a código6f814a2. Los11 controles previos pasan:
binario GL400/800 y MP80, triángulo analítico, escape en carta de cara,
invariancia afín en nuevo/AF y geometría plana AD con longitud AC archivada.
Los40 nuevos conservan todas sus escalas y producen escapes; la comparación
con respuesta analítica pasa en todos. AF sigue en ejecución, sin sustituir
fallos ni ajustar reglas. Los avisos de quad se conservan en el log externo.
La declaración inicial omitió Shapely/Autograd transitivas; ERRATA_ENTORNO.md añade su
versión efectiva, sin cambiar el entorno ni las mediciones v1.

Final:80/80 escapes refinados, todos los estados conservados.11/11 controles
previos y40/40 contrastes exactos PASS. Q1 PASS; Q2 FAIL; Q3 FAIL;
Q4 INCONCLUSIVE (ningún DRAG_5000); Q5 FAIL_DESCRIPTIVE. Tiempo480.724688s,
sin bloqueos de la guarda en procesos científicos. No se modificó código,
diseño ni entorno durante la corrida. Se conserva stdout/stderr incluyendo
avisos de quad. Las cuatro cuadraturas y ambos tiempos coarse/refinado mantienen
los veredictos en análisis derivado de archivos, sin reintegración.

Verificación final de archivos PASS:480 arrays,80 estados, MP80 de respuestas
exactas y24 contrastes derivados; no se reintegró geometría. Se mantuvieron
todos los2566 intentos de quad y los avisos originales.
