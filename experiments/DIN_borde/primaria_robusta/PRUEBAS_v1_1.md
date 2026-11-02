# Resultado de las pruebas sintéticas A1

2026-11-02. **BORRADOR para auditoría de Claude.** Corrida actual v1.1: **58/58 PASS**. No se entrenó, midió geometría ni leyó ninguna tabla real. No se evaluó tamaño nominal o potencia; estas pruebas no son una confirmación científica ni una garantía universal de robustez.

| Componente | SHA-256 |
|---|---|
| Analista v1, sin correcciones entre corridas | `1e2d903bfba8fa18a5eb6ecf5d93a759bc247009365c56ac561bc9b46604114d` |
| Pruebas actuales v1.1 | `1bac1b642c8f6fff9f651999441269a235c1f459619f15abd359e28be1d793b6` |
| Pruebas iniciales v1 | `2400170b1a973fe17f0c848db277a868e1e5ea5630c5bdefbfe623ffaa825e65` |
| C1, solo código sobre sintéticos | `8711f468d0df110a94c9cfdf6a1d0777f495537546cdce516929f0cb129858d5` |

## Obligatorios y equivalencia

- **NO_APRENDIO:** .49 cuenta como falta, con ID y todos sus motivos, sin sustitución; .5 exacto pasa y su vecino representable inferior no. Límites de 5 % y 80 % comprobados con denominadores planificados.
- **L extrema:** |z| = **13.10272432**, una trayectoria recortada en su bloque y conservada en la muestra. Recorte antes de potencias/centrado, limitado al rango de entrenamiento e independiente de X/Y; errores y p contrastados con cálculo independiente.
- **C1 exacto sin recorte:** 20 tablas con extremos repetidos dentro del entrenamiento de todos los bloques; D, p, pendiente y cuantil 95 idénticos bit a bit al código congelado. Otra tabla general se contrastó en modo diagnóstico sin recorte. Frente a la reimplementación independiente, error máximo de D = `0`, p idéntico. B = 39 en estos controles; la CLI nominal mantiene **5.000**.
- **Influencia:** g_i y D_sin_max frente a cálculo independiente, empates por orden del universo, fracción mayor que 1 sin truncar y null cuando la suma no es positiva. Omitir un ID conserva las otras dos filas de un split de tres.
- **Decisión:** tabla mínima PASS / NO_ROBUSTO / NOT_MET / INCONCLUSIVE. La propagación de NO_ROBUSTO y del fallo de D_sin_max se prueba además mediante **inyecciones unitarias explícitas**, no con una cohorte inventada que se afirme degenerada.
- **Dominios y E/S:** log solo tras validar rho; múltiples motivos, ausentes/fallidas, constantes, identidad/splits/plan, orden CSV invariante; salida exclusiva inicial y final, JSON estricto y bloqueo de tipo real en borrador. No se afirma validación nativa Windows; se ejecutó en Linux.

## Fallo y versiones conservados

La primera corrida terminó **56/57 PASS**. El fixture `D_sin_max_degenerado_conserva_fallo` suponía indebidamente que la única trayectoria con variación de X sería también argmax g fuera de muestra. El fallo, sus datos y su traceback se conservan. Se registró la [enmienda](ENMIENDA_PRUEBAS_v1_1.md) en `c4be8b9b` **antes** de corregir las pruebas (`6d153497`); el analista nunca cambió. La versión nueva reemplaza esa expectativa por inyección de fallo controlada y añade propagación de NO_ROBUSTO. Los **56 casos comunes tienen resultados byte a byte idénticos** entre corridas.

[Resumen inicial FAIL](pruebas/results_v1/summary.json), [resumen actual PASS](pruebas/results_v1_1/summary.json), [fallo original](pruebas/results_v1/D_sin_max_degenerado_conserva_fallo.json), [verificación](verification.json). Fixtures/arrays y salidas CLI fuera de Git, con manifests por versión en los directorios de resultados. Los logs originales se conservan sin reejecutar las pruebas.

## Qué debe auditar Claude

La especificación adoptada queda intacta. Revisar las convenciones operacionales declaradas en el contrato: pendiente global como C1, empates exactos, fracción no definida con suma no positiva, conservar dos filas en la omisión diagnóstica y D_sin_max degenerado → INCONCLUSIVE. Revisar además vínculos del productor, conteos y distinción entre pruebas de la regla por inyección y evidencia estadística. Los secundarios de rangos/spline/grado 5 son recomendaciones de la adopción, **no se implementan ni se seleccionan aquí**. Ningún resultado habilita automáticamente una cohorte real o la congelación.
