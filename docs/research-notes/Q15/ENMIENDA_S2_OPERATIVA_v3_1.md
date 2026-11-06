# Q15 — enmienda operativa S2 v3.1

**AUTORIZADA por el responsable en este encargo; registrada antes del código v2 y de cualquier consulta bibliográfica S2 bulk.** Fecha de registro: 2026-11-03 UTC (2026-11-02 en México). Complementa [v3](PROTOCOLO_OPERATIVO_v3.md); no la reemplaza ni modifica sus archivos. No es una nueva búsqueda ni una adjudicación de novedad.

## 1. Cambio autorizado

Las 55 consultas de Semantic Scholar usarán `GET /graph/v1/paper/search/bulk`. Se envía literalmente el campo `semantic_scholar` de [consultas_v2.csv](consultas_v2.csv): frases entre comillas ASCII, `+` para AND, `|` para OR y paréntesis de precedencia. Esas cadenas ya son la traducción de los grupos del protocolo; no se agregan sinónimos, exclusiones, expansiones ni términos según resultados. La autoría sigue como postfiltro de metadatos, sin rellenar cupos.

Se fija `sort=citationCount:desc` en todas las páginas, también cuando el conjunto sea pequeño; el proveedor desempata por `paperId`. Se conserva su orden, sin ordenar localmente una página ni combinar rankings de endpoints. Con total ≤ 500 se recupera todo; con total > 500 se seleccionan las primeras 200 posiciones y se declara `TRUNCADA_DECLARADA`. No se usa relevancia como si fuera equivalente a este orden.

**Justificación predeclarada:** complementar arXiv por relevancia y actas por año descendente con fuentes de mayor influencia medida por citas. Las citas favorecen trabajos antiguos y cambian con el tiempo; no miden pertinencia ni prioridad. La conclusión seguirá limitada a la cobertura efectiva y a la lectura verificada.

## 2. Contrato verificado y límites

Se consultaron la [documentación oficial Academic Graph](https://api.semanticscholar.org/api-docs/graphs#tag/Paper-Data/operation/get_graph_get_paper_search_bulk) y el [tutorial oficial](https://webflow.semanticscholar.org/product/api/tutorial). El índice web del dominio oficial permitió leer sus secciones de bulk; abrir directamente la documentación devolvió HTTP 429 y el tutorial `www` devolvió 403. Esta comprobación técnica no ejecutó consultas bibliográficas ni añadió fuentes al corpus.

Bulk busca en **título y resumen**. El proveedor analiza los términos con stemming inglés: las comillas y los operadores se conservan, pero no se promete equivalencia byte a byte con la coincidencia literal local de actas. El parámetro `sort` tiene formato `campo:orden`; `citationCount:desc` está documentado. El desempate es por `paperId`, y los valores de orden ausentes quedan al final. La documentación advierte que cambios del índice durante la paginación pueden alterar la secuencia.

La paginación usa un **token opaco** de continuación, no `offset`. La documentación no ofrece `limit` en bulk: cada respuesta puede contener hasta 1000 registros. Se conserva íntegra la respuesta cruda y sus posiciones, distinguiendo recuperados de seleccionados; no se criban las posiciones fuera de cupo ni se solicita otro token cuando ya se alcanzó el límite. Una respuesta de 1000 no autoriza cribar 1000.

El total es una **estimación del proveedor**, y así se rotula. Sin total se sondea hasta el fin o hasta al menos 501 posiciones observadas, aplicando entonces K=200. Si la estimación y las posiciones observadas caen en lados distintos del umbral de 500, se preserva el truncamiento conservador y se informa `PARCIAL`, sin simular completitud. Tokens repetidos, páginas vacías con continuación, IDs repetidos u orden de citas creciente se conservan como fallos de paginación/orden. No se deduplican para reponer cupos. No se interpreta el total estimado como número exacto de obras únicas.

Se mantiene el filtro de años que incluía la versión v3 y el postfiltro de fecha precisa al corte 2026-11-02. No se excluyen publicaciones de 2026 con fecha desconocida como si fueran posteriores: quedan pendientes. Se mantienen N=500/K=200, campos ausentes, filtro DIN de citantes, grafo S0 a un nivel, Scholar opcional omitida, preguntas, anclas y reglas de adjudicación de v3. El cambio de bulk **solo afecta las consultas**, no el orden nativo del grafo de citas.

## 3. Trazabilidad y validación antes de red

[LIMITES_v3_1.json](LIMITES_v3_1.json) y [plan_busquedas_v3_1.csv](plan_busquedas_v3_1.csv) fijan el contrato. El CSV conserva las 294 unidades; únicamente cambian interfaz y orden de las 55 filas S2. Las cadenas no cambian. Los manifiestos de v3 y del primer lote quedan intactos. El manifiesto de esta enmienda se compromete y publica por SHA **antes** de implementar el ejecutor v2.

El ejecutor v2 se publicará en carpeta nueva, con identidad de código/insumos y salida nuevas. Los estados `PENDIENTE_ENMIENDA_S2` del ejecutor v1 se conservan históricamente; no se reescriben como búsquedas realizadas.

Pruebas obligatorias: URL y codificación literal de los 55 booleanos, campos y orden exactos, tokens (sin `limit`/`offset`), 0/200/500/501/1000 posiciones, totales ausentes o inconsistentes, interrupción/reanudación, errores, orden, empates y selección antes de postfiltros. Se incluyen los dos defectos reproducidos en la revisión del ejecutor: recuperación de un HTTP 200 inválido mediante un intento nuevo exclusivo y verificación de las dependencias crudas al reutilizar un trabajo. Corregirlos no cambia preguntas ni reglas científicas.

El responsable ejecutará primero las pruebas simuladas y la preparación (paso 2 de PowerShell) y después la red (paso 3). Esta entrega no ejecuta búsquedas reales ni certifica servicios vivos o Windows sin esa prueba.
