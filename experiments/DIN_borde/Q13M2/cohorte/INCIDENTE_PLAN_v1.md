# Incidente de preparación del plan, sin mediciones

2026-10-28. Una primera comprobación auxiliar del plan supuso que `ast.walk` devolvía las listas numéricas LP y WD en orden textual. El recorrido por niveles las devolvió en otro orden y disparó `AssertionError` **antes de escribir cualquier plan**. No se generó otro universo, no se entrenó ni se ejecutó el productor.

El commit `70fa22d6` tiene un título que anunciaba el plan, pero contiene únicamente la equivalencia AST y su documento. Se conserva ese commit sin reescribir historia. La publicación efectiva del plan está en el commit posterior que añade `q13m2_plan.json` y su SHA, todavía anterior a todo código del productor.

La comprobación auxiliar se repitió identificando cada comprensión por su prefijo LP/WD, sin depender del orden de recorrido AST. Las dosis coinciden con el analista congelado; no hubo cambios del protocolo ni del instrumento científico. Este fue un fallo de preparación de metadatos, no de medición, por lo que no se corrigió ni reejecutó una corrida científica. Se conserva aquí el fallo y su causa.
