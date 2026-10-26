# Enmienda de presentación — congelada antes de corregir

El borrador no comprometido report_v1.py falló en ast.parse por delimitador de
f-string sin cerrar en la fila de verificación. No se ejecutó el reporte ni se
modificaron mediciones, análisis, tablas, datos o criterios. Se conserva literalmente
en versions/report_v0_invalid.txt y su fallo/SHA en versions/report_v0_failure.json.

Cambio autorizado y fijado: cerrar correctamente el literal de la fila de
verificación. Sólo sintaxis de presentación; ninguna cifra, base, control, umbral,
semilla o conclusión se recalcula. Verificar sintaxis, comprometer y ejecutar
report_v1.py. Este commit precede a la corrección y primera ejecución del reporte.
