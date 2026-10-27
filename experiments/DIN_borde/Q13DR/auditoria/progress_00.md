# Fase 0 — fuentes leídas antes del código de auditoría

Se leyeron el diseño v1, analisis_Q13DR y pruebas_Q13DR en e7dfc435…, más los
referentes Q13/C1 por SHA. La suite usa un fixture G3 bajo C2; no se ejecutará ni
se copiará ese CSV. Sólo sus fuentes se inspeccionan. Main no contiene el borrador:
se conservan snapshots inalterados en sources para un PR estrictamente aditivo.

Riesgos identificados por lectura, aún pendientes de ejecución: eps del plan no
se valida; medianas observadas sobre todas las válidas frente a bootstrap sobre
comunes; excepciones de bootstrap no capturadas; rangos físicos sólo finitos;
Spearman calculado por doble argsort sin tratar empates; precisión L4/L5 descrita
de dos maneras. La prueba de tasas usará ruido independiente entre niveles; las
copias idénticas de la suite no bastan para medir tamaño.

No se ha ejecutado ningún cálculo estadístico de auditoría ni se han leído datos
reales. Se congela el protocolo antes del código/mediciones.
