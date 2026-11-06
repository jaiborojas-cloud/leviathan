# Ejecutor Q15 v3 para PC: especificación de implementación en borrador

2026-11-02. No modifica el protocolo operativo ni autoriza todavía una ejecución real. El responsable pidió un productor para auditar con respuestas simuladas, conservando los datos anteriores.

El archivo único `ejecutar_q15_v3.py` leerá `consultas_v2.csv` (idéntica a v3), `plan_busquedas_v3.csv`, `LIMITES_v3.json` y S0, verificando sus SHA y consistencia. Separará preparación, consultas, catálogos, citas y ejecución completa. Google Scholar se declarará omitida por ser opcional y requerir interacción/CAPTCHA; no se automatizará.

Se conservarán por solicitud URL, fecha UTC/México, código HTTP, cuerpo crudo, SHA y cada fallo/reintento. Los cuerpos, metadatos y resultados se publicarán localmente sin reemplazar archivos: escritura temporal exclusiva y promoción exclusiva; bloqueo de proceso para la misma salida. La reanudación usará solo respuestas íntegras y exitosas, respetará los resultados ya terminados y reintentará fallos únicamente mediante opción explícita, creando versiones nuevas. La huella de salida fijará script e inputs para impedir mezclar versiones o simulación con red.

Se aplicará N=500/K=200 antes de deduplicar y postfiltrar, con sondeo máximo 501 cuando no se conozca el total. Las actas se filtrarán por título/resumen y ordenarán por año descendente, título e ID ascendentes. Los campos ausentes y los catálogos históricos no recuperados quedarán como pendientes; ni una respuesta vacía anómala ni una pantalla de carga contarán como catálogo completo. La recuperación de catálogos no se truncará antes de evaluar las consultas: el tope se aplica a sus coincidencias, no a las primeras páginas del catálogo.

Semantic Scholar tendrá pausa mínima de un segundo, respeto de Retry-After y backoff ante 429 y fallos transitorios, guardando cada intento. arXiv usará al menos tres segundos entre solicitudes. Las citas se limitarán al primer nivel de S0; para >500 citas o conteo desconocido se tomará la ruta local de v3: primeras 200 posiciones y luego filtro DIN, sin reponer cupos. Si el total cambia o falla una página, no se declarará exhaustividad.

## Incompatibilidad de la v3 que la implementación no puede resolver silenciosamente

La [documentación oficial de Semantic Scholar](https://api.semanticscholar.org/api-docs/graphs), consultada para esta implementación, declara `/paper/search` como consulta de texto sin sintaxis especial. La sintaxis `+`, `|` y paréntesis corresponde a `/paper/search/bulk`, cuyo orden no es el de relevancia fijado por la v3. El ejecutor construirá las URL literales previstas, pero **no enviará esas 55 consultas como si su semántica estuviera garantizada**: marcará `PENDIENTE_ENMIENDA_S2`. No sustituirá bulk, quitará operadores ni combinará rankings sin una enmienda autorizada previa. La consulta de metadatos y el grafo de S0 no usan esa sintaxis y sí se implementan.

Esto es un bloqueo de compatibilidad que Claude debe resolver antes de la ejecución real, no un cero de resultados ni un cambio del protocolo. El productor puede recuperar las otras bases y el grafo sin fingir completitud de Semantic Scholar. Las pruebas deben cubrir esta condición.

## Catálogos y fechas

NeurIPS se descubre desde su índice oficial y sus páginas de artículos; PMLR solo admite volúmenes ICML verificados en el índice, con sus páginas y resúmenes; OpenReview usa únicamente notas aceptadas cuya pertenencia al venue se pueda comprobar. Se registran API v1/v2 y años no recuperados, especialmente los históricos. La falta de cobertura histórica de ICML anterior a PMLR no se rellena con datos de otra conferencia ni se oculta.

No se probará disponibilidad de servicios ni se obtendrán artículos de investigación nuevos durante esta tarea. Solo se consultó documentación técnica/estructura de interfaces; las pruebas del productor serán completamente simuladas. El tiempo real de recuperación dependerá de catálogos, pausas y respuestas; no se inventará una estimación medida en internet normal.
