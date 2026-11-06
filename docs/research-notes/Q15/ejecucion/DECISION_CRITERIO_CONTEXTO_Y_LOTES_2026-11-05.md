# Decisión del responsable: criterio de CONTEXTO y tamaño de lotes

**2026-11-05, 14:20, hora de México.** Decide: el responsable. Responde a la observación O1 de la [auditoría del lote 01](AUDITORIA_CRIBADO_C_LOTE01_2026-11-05.md). Interpreta la sección 6 de `PROTOCOLO_OPERATIVO_v3.md` sin modificarla.

## Criterio para aplicaciones primarias
- Una aplicación va a **CONTEXTO** si su pregunta central es si un predictor o componente añadido mejora a un modelo base, es decir, una evaluación incremental.
- Va a **EXCLUIR_FUERA_TEMA** ("aplicación sin contenido relevante") si la base solo aparece como referencia para promocionar un modelo nuevo.

El criterio se aplica igual desde el lote 02. Las decisiones del lote 01 (W00014 excluida; W00024 y W00027 en CONTEXTO) son coherentes con él y no se reabren.

## Lotes
- Las 3 148 obras en `PENDIENTE_CRIBADO` se cortan en lotes **por orden ascendente de `obra_id`**, no por unidad de búsqueda, porque muchas obras tienen varias rutas. El orden queda fijado antes de leer y no se eligen obras por resultado.
- **Lote 02:** las primeras 50 obras. El tamaño de los lotes siguientes se decide con lo que se mida en este (tiempo y consumo), subiendo poco a poco.
- Cada lote guarda sus decisiones de forma incremental, de modo que si el agente se queda sin créditos lo leído no se pierde y el lote se reanuda donde quedó.
