# Q15 v3.1 — validación del ejecutor v2

## Resultado y método

[run_02.json](pruebas_simuladas/run_02.json): **91/91 PASS**, cero fallos y cero errores. Transporte completamente simulado, bloqueo adicional de sockets y de `build_opener`. Ejecutado en Linux con la versión de Python registrada en [verification.json](verification.json). No se consultaron bases bibliográficas ni se añadieron fuentes a la extracción. El contrato oficial se comprobó mediante documentación, no mediante consultas reales.

La suite [pruebas_ejecutar_q15_v3_1.py](pruebas_ejecutar_q15_v3_1.py) valida el [ejecutor](ejecutar_q15_v3.py) con los SHA registrados en el informe. Conserva los controles anteriores aplicables: insumos, URLs, catálogo, orden, topes, filtro DIN, fechas, autoría, S0 previo al grafo, un nivel, respuestas crudas, claves, redirecciones, gzip, exclusividad, bloqueo, pausas y 429/Retry-After. Los dos controles que exigían el bloqueo S2 se sustituyen por comprobaciones bulk sin red.

## Controles nuevos relevantes

| Riesgo | Comprobación simulada |
| --- | --- |
| Cambiar la expresión al cambiar de endpoint | Las 55 cadenas del plan se recuperan idénticas tras decodificar las URL; campos, años y `sort` exactos. |
| Usar paginación de relevancia en bulk | Token opaco con signos/Unicode; URL sin `offset` ni `limit`; primera petición sin token. |
| Cribar todo un lote de 1000 | Fronteras 0/200/500/501/1000; todos los registros conservados, exactamente 200 seleccionados por encima de 500; no se solicita otro token después del cupo. |
| Confundir estimación con censo | Total ausente, estimación inexacta dentro del mismo lado del umbral, cambio de estimación y contradicción al cruzar 500. |
| Omitir resultados por errores de continuidad | Páginas por token, vacío con continuación, token repetido y fallo en una página posterior; se conservan las posiciones ya recuperadas. |
| Ranking inestable | Orden creciente de citas, nulos en medio y IDs repetidos causan `PARCIAL`; empates y nulos al final mantienen el orden recibido. |
| Reponer exclusiones con la posición 201 | Postfiltro de fecha después de seleccionar: quedan 199 elegibles y la posición 201 no entra. |
| Reanudar desde cero | Una página 429 se reintenta sin volver a solicitar la página válida anterior; CLI S2 completa las 55 consultas de fixture y reutiliza sus cuerpos. |
| HTTP 200 inválido permanente | JSON no válido, objeto bulk de esquema inválido y Atom de bloqueo; con reintento explícito se recibe la segunda respuesta válida, preservando la primera. Sin flag no se gasta otra petición. |
| COMPLETE pese a falta de evidencia | Alterar o borrar un cuerpo impide reutilizar un trabajo, incluso indirectamente por consulta → catálogo → artículo. |

## Versiones conservadas

[run_01.json](pruebas_simuladas/run_01.json) fue una pasada de desarrollo con 89 pruebas, todas PASS. Sus fuentes exactas se conservan en [fuentes_run01](pruebas_simuladas/fuentes_run01/ejecutar_q15_v3.py.txt); sus SHA fueron reconstruidos y comprobados contra el informe. El run final agrega integración de caché con esquema bulk inválido y dependencias de catálogos, elimina una función obsoleta de URL de relevancia y convierte un vecino S2 no objeto en error explícito de esquema. No se sobrescribió ningún informe. No hubo pruebas fallidas en estas dos pasadas.

La versión v1 y sus 51/63/65/66 pruebas permanecen en su carpeta y en sus commits, con su manifiesto intacto. La enmienda quedó publicada en `7e668f81…`; el código v2 con el resultado final, en su hijo `5259d942…`. Las fuentes de la pasada de desarrollo no son la suite que debe ejecutarse en el PC.

## Límites de esta validación

No es una prueba de conectividad ni una captura de todos los esquemas históricos reales. Los formatos históricos no soportados de OpenReview y el histórico de ICML anterior a PMLR siguen reportados como pendientes. La rama de escritura exclusiva Windows se prueba mediante simulación; la validación nativa la hará el responsable con el paso 2, antes de la red. La suite no mide lectura bibliográfica, exhaustividad ni novedad científica.
