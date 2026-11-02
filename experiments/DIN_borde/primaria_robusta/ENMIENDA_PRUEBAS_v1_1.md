# Enmienda prospectiva de pruebas v1.1 · 2026-11-02

**Borrador; solo pruebas sintéticas.** Se compromete antes de corregir el verificador o ejecutar otra corrida. El analista SHA `1e2d903bfba8fa18a5eb6ecf5d93a759bc247009365c56ac561bc9b46604114d`, la configuración y la especificación adoptada **no cambian**.

## Fallo conservado

La corrida `pruebas/results_v1/` terminó **56/57 PASS**, con un fallo en `D_sin_max_degenerado_conserva_fallo`; se conservan todos sus resultados, el código v1 y fixtures externos en `/workspace/work/din-robusta-pruebas-v1`. Los 20 casos de equivalencia exacta con C1, la L con |z| = 13.10, el criterio NO_APRENDIO y la CLI de 5.000 permutaciones pasaron.

El fixture daba variación de X solo a una trayectoria y asumía que esa misma sería argmax g. Esa inferencia no es válida fuera de muestra: el bloque que la contiene se ajusta sin ese ejemplo, y la influencia se calcula con sus errores de prueba. La aserción no construía de forma controlada la condición que pretendía probar. No demuestra un defecto del analista ni autoriza cambiar su regla.

## Corrección fijada

Crear `pruebas_robusta_v1_1.py` con rutas nuevas `pruebas/results_v1_1/` y `/workspace/work/din-robusta-pruebas-v1_1`; no sobrescribir v1. Repetir los 57 controles, sustituyendo únicamente el fixture defectuoso por **inyección unitaria de fallo numérico al recalcular D_sin_max**. Se usa el fixture base válido y se hace fallar `punto` solo al omitir una fila. Se debe conservar la primaria ya calculada y el mensaje, producir D_sin_max = null y veredicto INCONCLUSIVE. La salida lo identificará como inyección de fallo, no como una degeneración descubierta en una cohorte.

Añadir un control de propagación: sobre el fixture base con triple condición válida, inyectar únicamente D_sin_max = 0 y un valor negativo en el resultado de `influencia`, conservando todos sus otros campos. Ambos deben dar NO_ROBUSTO y preservar la primaria. Es un test unitario de conexión entre diagnóstico y veredicto; no se presenta como evidencia estadística de una cohorte. La tabla pura de decisiones ya fijada se mantiene.

No se modifican fórmulas, tolerancias, tamaños, semillas, código del analista ni la interpretación de PASS. Mantener manifest y resultados de ambas versiones. Además, A2 se resumirá editorialmente para cumplir la petición de un documento corto; sin nuevos datos, opciones o decisiones científicas.
