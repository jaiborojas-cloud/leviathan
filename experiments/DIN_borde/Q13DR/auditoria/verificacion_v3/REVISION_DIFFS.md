# Revisión acotada a los cambios v2→v3

**No se observaron defectos nuevos en los cambios examinados.** Esta afirmación se limita a las rutas y dominios probados; no certifica la ausencia universal de fallos. [Diff exacto](sources/analista_v2_v3.diff), [estructura AST](results/diffs/structural.json).

| Cambio | Comprobación independiente | Resultado |
|---|---|---|
| pendiente | Rechazo de constancia antes de centrar; finitud; comparación exacta con v2 en las720 permutaciones de seis c físicas distintas; punto/repeticiones constantes. | Pasa. Las asignaciones y la expresión devuelta son idénticas para c finita y no constante. |
| rango_c |720 ordenamientos frente a max−min, más el caso íntegro de orden común invertido. | Pasa. El campo diferencia_c_L0_L5 conserva el contraste de extremos; margen no negativo. |
| validar_plan |87 casos directos: N y tipos, extremos, seis dosis, bool/NaN/inf/entero enorme, dosis inmediatamente distinta por nextafter, raíz y lista malformadas. Casos CLI históricos reejecutados. | Pasa, sin introducir tolerancias. |
| main | Archivos ausentes/directorios, bytes UTF-8 inválidos en tabla/plan/resumen, JSON malformado y campo CSV sobre el límite del parser. Hashes corresponden a las entradas sintéticas usadas. | ABORTA/código3/sin traceback en todos los casos inválidos. CLI completo válido produce JSON estricto. |
| Registro bootstrap |116 fallos por L constante y271 por c constante; comparación de lista completa con traza independiente. | Pasa; se cuenta y conserva cada fallo, sin redibujar. |

[720 pendientes/rangos](results/diffs/slopes_and_ranges.json), [87 planes](results/diffs/plans.json), [todos los casos adicionales](results/diffs/summary.json).

## Por qué no se repitió el Monte Carlo

Las dependencias C1 y Q13 son idénticas por SHA. La comparación AST muestra que `analizar` solo cambia la lista completa de errores y los campos de rango; el muestreo, los bloques, el cálculo de D, las dosis, las semillas, los umbrales y las decisiones no cambian. En `pendiente`, las asignaciones y la expresión del resultado permanecen idénticas; la protección nueva se activa ante constancia o falta de finitud.

Se compararon v2 y v3 sobre diez tablas sintéticas nuevas, N20, seeds910400..910409, todas llegadas a bootstrap sin degeneraciones. Se obtuvo igualdad exacta del resultado completo después de normalizar **solo** `fallos_primeros`→`fallos` y quitar el campo nuevo `diferencia_c_L0_L5`. Esto incluye D, p, pendientes, c comunes, beta, IC, veredictos y secundarios. [Comparación completa](results/diffs/compatibility_10.json).

Por tanto no se activó la condición predeclarada para otro Monte Carlo. Los casos degenerados corregidos no se usan para reestimar tasas. Las tasas nulas y la potencia de la alternativa+.03 publicadas en #105 siguen siendo evidencia anterior, no una corrida v3.

## Límites

Los casos de API interna usan B39/NB16, salvo los dos casos de300 réplicas; la CLI usa los parámetros nominales. Esas reducciones sirven para lógica, no para estimar tamaño/potencia. La suite del autor se leyó y verificó por SHA, pero no se ejecutó porque su fixture está bajo C2. No se usan datos reales. Ejecución en Linux, Python3.12.14; no se verificó ejecución nativa Windows. La aprobación para congelar no forma parte de este informe.
