# N01–N05 contra la v3

Todos los casos originales se reejecutan sin alterar [las salidas v2](../verificacion_v2/results/cases/summary.json). Se conservan los identificadores históricos aunque incluyan «new» o «v1».

| Caso | Resultado v3 | Veredicto de verificación |
|---|---|---|
| N01: siete c constantes decimales | `.1,.2,.3,.4,.5,.7,.9` provocan FloatingPointError antes de centrar. | RESUELTO |
| N01: punto constante, 160/200 comunes | INCONCLUSIVE, motivo `punto: beta no identificada (c constante)`; no publica una beta o un IC arbitrarios. | RESUELTO |
| N01: punto identificable, réplicas constantes | Punto c=[.88,.8,.755,.72,.66,.63], beta0. De300 draws,271 tienen seis c iguales: se rechazan todos, INCONCLUSIVE, índices y errores completos, sin redibujar. | RESUELTO |
| N02: c común invertida | c=[.3,.35,.4,.45,.5,.6], `rango_c=.3`, margen=.006 y diferenciaL0−L5=−.3 en campo separado. | RESUELTO |
| N03: eps entero10^400 | CLI ABORTA, código3, sin traceback. | RESUELTO |
| N04: entradas ausentes/directorios | Plan ausente/directorio, tabla ausente/directorio y resumen ausente/directorio: ABORTA, código3, sin traceback. | RESUELTO |
| N05: registro de fallos | Los116 fallos de300 draws se guardan íntegros; índices idénticos a la traza independiente, sin redibujos. | RESUELTO |

## Evidencia reproducible

- [Constantes puras](results/cases/new_constant_decimal_c_rules.json), [punto íntegro original](results/cases/new_constant_decimal_c_common80.json), [nuevo caso de réplicas](results/diffs/bootstrap_constant_c.json).
- [Rango invertido](results/cases/new_reversed_common_c_range.json).
- [eps enorme](results/cases/new_plan_huge_integer_eps.json).
- [Plan ausente](results/cases/new_plan_missing_file.json), [plan directorio](results/cases/new_plan_directory.json), [tabla ausente](results/cases/new_table_missing_file.json), [resumen ausente](results/cases/new_summary_missing_file.json), [tabla directorio](results/diffs/table_directory.json), [resumen directorio](results/diffs/summary_directory.json).
- [Los116 fallos](results/cases/new_degenerate_logging_300.json).

El caso nuevo de c constante en réplicas usa el mismo patrón de160 comunes y40 excluidos de N01, conservando una compuerta operacional válida. Entre los comunes,79 splits tienen c=.04 en todos los niveles;80 tienen c=.9; uno tiene las seis c de referencia. La mediana puntual varía, pero muchos remuestreos tienen mediana idéntica en todos los niveles. El verificador enumera esas réplicas desde los draws y compara exactamente con los índices del analista:271/271. Es un caso degenerado intencional, no una estimación de frecuencia poblacional.

La traza N05 original conserva el generador y la semilla860001:116/116 errores completos, frente a20 detalles guardados por la v2. La clave nueva es `fallos`; el motivo abreviado de pantalla puede mostrar diez índices, pero el JSON contiene la lista completa.
