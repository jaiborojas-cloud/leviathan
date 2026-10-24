# Ejecución D2 v1

Congelación2269b7f y detalles d233ea6 anteriores al código61e7fe6 y a las
mediciones.8/8 controles independientes PASS.210/210 controles de matrices
PASS y153 testigos globales exactos más57 cotas coherentes. Tres procesos,
BLAS/OMP1; tiempo865.843661s. No hubo reintentos ni reemplazos de estados.

Q1–Q3 PASS (caracterizaciones y cotas condicionales), Q4 PASS_DESCRIPTIVE
(compatibilidad, no causa), Q5 FAIL. Los210 retornos nativos quedan archivados:
173 PASS,33 FAIL,4 INCONCLUSIVE. Las referencias de longitud que no pasan
GL16/32 se conservan inconclusas. No se modificó rho_borde.py ni geometry.py.
Los985 avisos nativos permanecen en raw_and_references.json. No hubo lectura
de estados T2 ni bloqueos de acceso durante las mediciones.

El informe y los apéndices distinguen pruebas, contrastes numéricos y
compatibilidad descriptiva. No se infiere localización real del modo de D1
ni se trasladan los fallos sintéticos a su cohorte. Se inicia verificación
desde archivos, sin volver a llamar al instrumento ni integrar curvas.

Verificación final PASS:360 hashes,153 valores globales conocidos y210
controles espectrales. Se verificó por cuerda un fallo ya identificado; los
cuatro inconclusos permanecen. No se cambió código de medición ni fuentes
congeladas, y no se volvió a ejecutar el instrumento.
