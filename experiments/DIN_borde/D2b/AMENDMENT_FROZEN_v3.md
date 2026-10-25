# Enmienda congelada v3 · serialización del postproceso

La corrida válida run_v2 terminó las86 redes, sin errores de medición.
El postproceso summarize_v2 falló al escribir summary.json: un booleano NumPy
en el control sameX no es serializable por json.dump estándar. Se conserva
el script, el log vacío y el JSON parcial; no se usa ese archivo como resumen.
La traza se registra en results/run_v2/POSTPROCESS_FAILURE_v2.json.

Antes de corregir se compromete esta enmienda. Un summarize_v3 nuevo convertirá
escalares NumPy a tipos Python exclusivamente al serializar, escribiendo
summary_v3.json y networks_v3.csv nuevos. Mismos86 retornos, idénticas reglas,
sin repetir redes, rho ni controles. No se toca run_v1, run_v2 ni su código.
La verificación final leerá el resumen v3 completo y excluirá explícitamente
el archivo parcial como entrada JSON. Esta enmienda afecta sólo al formato
del postproceso y no altera el diseño científico.
