# Q15 v3.1 — ejecutor PC v2

Esta es la versión vigente para el responsable, después de la auditoría comunicada por él y de la [enmienda S2 autorizada](../ENMIENDA_S2_OPERATIVA_v3_1.md). El [ejecutor v1](../ejecutor_pc_v1/README.md), sus informes y sus pendientes se conservan sin modificaciones.

- **Enmienda publicada antes del código:** `7e668f81cf6f7beeecb28a4541d06311a21f233d`.
- **Código y pruebas publicados:** `5259d942d4f54c3d28f917f6e4a41ed9bd890a42`.
- **SHA-256 del ejecutor:** `9d986a770956c49edd1174d9bb2b50bc65dbfe5c4958c7e753083d5ceb2df8a4`.
- **SHA-256 de la suite:** `eadbb41fae694e8c30077037320bfc46a239768d1861cf4b0d30a2839174aadc`.
- **Pruebas finales:** [91/91 PASS, solo simuladas](pruebas_simuladas/run_02.json).

El responsable corre primero el **paso 2** y, si pasa, el **paso 3** del [procedimiento PowerShell](PROCEDIMIENTO_WINDOWS.md). No hace falta otra decisión sobre S2 para aplicar el contrato publicado. Aquí no se ejecutaron búsquedas reales. La conectividad del PC y los esquemas vivos se comprobarán allí; un bloqueo deja pendientes, nunca ceros inventados.

## Qué cambia respecto a v1

Las 55 consultas S2 usan `/paper/search/bulk`, con su expresión booleana literal, `sort=citationCount:desc`, desempate nativo por `paperId` y tokens de continuación. El cupo es el de la enmienda: hasta 500, todo; por encima, 200 posiciones seleccionadas. Una respuesta puede contener hasta 1000 registros: se conserva completa y los adicionales quedan `selected=false`. El total de bulk es estimado y no se presenta como conteo exacto.

Se mantienen las 294 unidades planificadas y las 19 anclas S0, arXiv por relevancia, actas por año descendente, grafo a un nivel, filtro DIN local sobre las primeras 200 citas cuando corresponde y Google Scholar opcional omitida. No cambian preguntas, corte bibliográfico, reglas de lectura ni adjudicación de novedad. [LIMITES_v3_1.json](../LIMITES_v3_1.json) es el contrato aplicado; [plan_busquedas_v3_1.csv](../plan_busquedas_v3_1.csv) cambia solo interfaz y orden de las filas S2 respecto de v3.

También se corrigen los dos defectos reproducidos en la revisión independiente del ejecutor:

1. Una respuesta HTTP 200 con JSON, Atom o esquema inválido queda vinculada a un marcador exclusivo de rechazo. `--reintentar-fallos` crea otro intento; no reutiliza indefinidamente la respuesta inválida ni sobrescribe el fallo. Los artículos incompletos admiten el mismo reintento explícito.
2. Cada trabajo conserva dependencias con SHA. Al reutilizarlo se comprueban cuerpos y metadatos crudos, trabajos hijos y snapshots. La verificación es transitiva para consulta → catálogo → artículo → HTTP. La falta o alteración de un cuerpo aborta por integridad. Se memoizan huellas de archivos inalterados durante una ejecución, sin guardar todos los cuerpos en memoria.

## Controles y alcance

La suite conserva los controles anteriores aplicables y sustituye los dos que exigían el bloqueo S2 por integración bulk simulada. Añade límites 0/200/500/501/1000, tokens opacos, reanudación de páginas, estimaciones, orden, empates, duplicados, postfiltros y los defectos de caché. [PRUEBAS_Y_CAMBIOS.md](PRUEBAS_Y_CAMBIOS.md) explica el detalle y los informes históricos.

Las respuestas se escriben exclusivamente, con UTC/México y SHA, fuera del clon. Usar una **salida nueva para v2**: la identidad rechaza mezclar código/insumos con v1. Se mantienen bloqueo de proceso, caché, pausas S2 ≥ 1 s y arXiv ≥ 3 s, reintentos 429/Retry-After y conservación de fallos. No se requiere red para las pruebas ni para `--fase preparar`. Solo Python 3.12+ y, en Windows, [tzdata fijado](requirements.txt).

La cobertura histórica ICML anterior a PMLR y los formatos antiguos de OpenReview no soportados siguen pendientes explícitos. No se introdujo una recuperación alternativa no autorizada. Windows se ha comprobado por la rama exclusiva simulada, no con un Windows real: el paso 2 es obligatorio en el PC.
