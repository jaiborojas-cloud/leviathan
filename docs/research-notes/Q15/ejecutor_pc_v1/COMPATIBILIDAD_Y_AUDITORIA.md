# Puntos para la auditoría de Claude antes de ejecutar

2026-11-02, America/Mexico_City. Implementación en BORRADOR; no se modifican v3, sus consultas, sus límites ni S0.

## Bloqueante: Semantic Scholar, booleanos y relevancia

La [documentación oficial de Graph API](https://api.semanticscholar.org/api-docs/graphs), recuperada para comprobar contratos técnicos, distingue:

| Ruta | Contrato que importa aquí |
|---|---|
| `/paper/search` | Consulta de texto sin sintaxis especial y resultados por relevancia. |
| `/paper/search/bulk` | Admite operadores booleanos; no es intercambiable con el ranking de relevancia previsto. |
| `/paper/search/match` | Resolución de un título, no sustituto de la consulta temática. |
| `/paper/{id}/references`, `/citations` | Grafo por ID, con paginación; no ofrece el filtro DIN de la v3 del lado del servidor. |

La especificación consultada dice «No special query syntax is supported» para relevancia. La recuperación directa de esa documentación devolvió 429 en algunos intentos; se pudo contrastar el texto indexado de la URL oficial. No se han probado estas rutas con consultas bibliográficas nuevas para el productor.

Por eso, en `Runner.native`, las 55 consultas S2 quedan **PENDIENTE_ENMIENDA_S2** sin enviar. Sus URL literales se construyen y registran, pero no se quitan operadores, no se cambia a bulk, no se mezclan subconsultas y no se reordena un resultado a conveniencia. Esto conserva v3 y evita afirmar una ejecución exacta imposible de garantizar con el contrato actual.

**Decisión que requiere una enmienda previa autorizada:** elegir cómo se ejecutará S2 (por ejemplo, booleanos con un orden documentado de bulk, o una traducción distinta de consultas con una regla explícita de recuperación/ranking). No basta con cambiar una línea de endpoint: podría cambiar el conjunto seleccionado por K=200. Este borrador no toma esa decisión ni usa su salida para adjudicar novedad. Los fixtures validan que el bloqueo no se confunda con cero coincidencias ni con una consulta completada.

## Cobertura de catálogos que debe comprobar el auditor

1. **NeurIPS:** los enlaces oficiales se descubren desde el índice; se distinguen tracks creativos/workshops. Se detectan años no listados y fallos de páginas. Un año ausente puede significar que todavía no se publicaron las actas; se registra como pendiente de comprobar, no se inventa el motivo.
2. **ICML:** el productor solo usa volúmenes PMLR que el índice identifica como ICML. El histórico anterior a esa serie queda explícitamente pendiente, conforme a v3. No se introduce una fuente histórica nueva sin registrar su procedencia/regla en el protocolo.
3. **OpenReview:** API v1 hasta 2023, v2 desde 2024; se contrasta el grupo oficial y `venueid` exacto. No se consideran aceptadas todas las sumisiones ni un workshop. Los años antiguos cuyos campos/IDs no coincidan con este contrato se conservan como pendientes; el ejecutor no convierte cero notas reconocidas en ausencia de publicaciones.
4. **Resúmenes/fechas ausentes:** ni los índices parciales ni los títulos por sí solos justifican totales exactos de coincidencias si quedan documentos sin comprobar. Se conservan pendientes y las posiciones seleccionadas sin rellenar cupos.

Los esquemas se probaron con respuestas sintéticas representativas, no con una captura completa de cada versión histórica de los sitios. Esa es una limitación de validación externa, explícita antes de que el responsable ejecute. La implementación conserva el fallo, la respuesta cruda y el estado de cobertura para que una desviación real obligue a revisar el contrato, sin esconderla.

## Contratos de ingeniería probados

Reanudación y SHA de caché; cuerpos huérfanos/temporales tras interrupción; colisión con marcador; exclusión de dos procesos; reintentos 429; no filtrar antes del cupo; años descendentes; filtro DIN con límites de palabra y guiones Unicode; fechas parciales; IDs nulos; S0 resuelta antes del grafo; no recursión; JSON no finito; resolución de ancla que falla con título discordante; salida parcial con código 2.

La prueba Windows es simulada. El auditor/responsable debe comprobar la ejecución de las pruebas en su Windows antes de la red. El [procedimiento](PROCEDIMIENTO_WINDOWS.md) separa ambas acciones.
