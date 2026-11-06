# Acceso y trazabilidad del primer lote

Fecha de consulta: 2026-11-02. El protocolo operativo se comprometió y publicó en `a9b85e64dc9d32bd99a593765a40b74019e7ab7d` antes de la primera solicitud. La lista S0 de 19 anclas se publicó en `102dd5b8` antes de intentar la recuperación del grafo.

## Acceso

El proxy del entorno rechazó las seis solicitudes iniciales con `Tunnel connection failed: 403 Forbidden`. El estado de Cloud Environment confirmó política **restricted/enforced**, sin esos destinos en la lista permitida. Son denegaciones del entorno, no evidencia de que las bases carezcan de artículos ni de que estén caídas.

Se probaron las búsquedas A08 en arXiv, Semantic Scholar y Scholar: 3 combinaciones intentadas, ninguna completada. Los accesos a los catálogos NeurIPS, PMLR y OpenReview son diagnósticos de interfaz, no ejecución de las 129 combinaciones temáticas de actas. El visor web abrió los índices NeurIPS/PMLR; no se recuperó el corpus título/resumen de todas las actas. OpenReview solo devolvió la página de carga. El grafo de S17 no se pudo recuperar en ninguna dirección.

No se enviaron 294 consultas para repetir un bloqueo de configuración conocido. `estado_plan_294_v1.csv` conserva las 291 no ejecutadas como tales. Los totales de coincidencias siguen desconocidos. No se suman los 191 resultados de cuatro grupos web auxiliares como si fueran resultados de las bases nativas; incluyen páginas duplicadas, fuentes secundarias y materiales sin pertinencia todavía cribada.

## Registro auxiliar y precisión temporal

Las lecturas de originales y la resolución de anclas son rutas auxiliares permitidas por el protocolo. Las once consultas nuevas se enviaron también al buscador web general en sus cadenas literales; se añade un grupo de cuatro consultas para resolver las anclas Guo, Amari, Jaakkola y Campbell–Thompson. Este último usa nombres como ayuda explícita de resolución, no como una ejecución exacta de filtros de autor de las bases. La salida agrupada no identifica un conteo por consulta. El log conserva sus cadenas y solo declara el conteo por grupo.

Las respuestas de herramientas web no conservaron hora de llamada: para ellas se registra fecha con precisión de día, y hora de registro del artefacto por separado, sin inventar instantes de consulta. Las solicitudes directas sí tienen timestamps UTC/México. Las respuestas completas de lectura se guardan localmente fuera de Git, con SHA, para no publicar artículos completos. El CSV público de resultados auxiliares conserva títulos y enlaces, sin copiar resúmenes largos.

## Desviaciones detectadas y conservadas

El primer sondeo web de arXiv usó una cadena reducida a título en vez de título/resumen y omitió fechas. Falló y **no se usa ni cuenta como ejecución de A08**. Queda preservado en `q15_web_access` como diagnóstico no conforme. El intento directo A08 original y el posterior por el alias arxiv.org sí conservan la cadena operativa completa; ambos fallaron. Esto no altera las cadenas autorizadas ni habilita cambiar silenciosamente las consultas.

La lectura incidental de referencias al abrir originales no equivale al seguimiento sistemático de un nivel. Por ejemplo, Amari aparece citado en Jaakkola; se usó para contrastar metadatos, sin declarar completada la expansión de S19.

## Acceso necesario para completar

Hace falta habilitar en la configuración de red del entorno `arxiv.org`, `export.arxiv.org`, `api.semanticscholar.org`, `www.semanticscholar.org`, `scholar.google.com`, `proceedings.neurips.cc`, `papers.neurips.cc`, `papers.nips.cc`, `proceedings.mlr.press`, `openreview.net`, `api.openreview.net` y `api2.openreview.net`. La accesibilidad de Scholar y los límites/rate limits propios de cada servicio se comprobarán después; permitir un dominio no garantiza acceso. No se modifica ni se elude el proxy o su política. Alternativa: ejecutar la recuperación autorizada en un entorno con esos accesos y traer las exportaciones fechadas y con hashes.

Hasta completar la cobertura y las lecturas críticas, los puntos afectados permanecen sin adjudicación final de novedad.
