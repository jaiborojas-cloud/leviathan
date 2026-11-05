# Decisión del responsable: aplicaciones que usan medidas de dificultad

**2026-11-05, 16:39, hora de México.** Decide: el responsable. Responde a la observación O2 de la [auditoría del lote 02](AUDITORIA_CRIBADO_C_LOTE02_2026-11-05.md) con la opción B. Complementa el [criterio de CONTEXTO](DECISION_CRITERIO_CONTEXTO_Y_LOTES_2026-11-05.md) e interpreta la sección 6 de `PROTOCOLO_OPERATIVO_v3.md` sin modificarla.

## Criterio
Para las aplicaciones que usan medidas de dinámica de entrenamiento o de dificultad por ejemplo (cartografía de datasets, EL2N, GraNd, eventos de olvido, PVI, puntajes de pérdida o incertidumbre y otras similares):
- **INCLUIR_PARA_TEXTO** si reportan un hallazgo sobre la medida misma: cuándo funciona o falla, qué capta, o cómo se relaciona con la generalización, la calibración o el ruido de etiquetas.
- **EXCLUIR_FUERA_TEMA** si solo la usan como instrumento (para seleccionar, filtrar o comparar) dentro de un sistema cuyo aporte es otro.

CONTEXTO queda reservado para lo que ya cubría: revisiones, tutoriales y material secundario, y las aplicaciones de evaluación incremental del criterio anterior.

## Aplicación al lote 02
Se corrigen en el paquete del lote 03, sin modificar el del lote 02:

| obra | lote 02 | corregida |
|---|---|---|
| W00100 | CONTEXTO | INCLUIR_PARA_TEXTO |
| W00110 | CONTEXTO | INCLUIR_PARA_TEXTO |
| W00131 | CONTEXTO | INCLUIR_PARA_TEXTO |
| W00112 | CONTEXTO | EXCLUIR_FUERA_TEMA |
| W00121 | CONTEXTO | EXCLUIR_FUERA_TEMA |
| W00122 | CONTEXTO | EXCLUIR_FUERA_TEMA |

W00108, W00120 y W00133 siguen excluidas, porque usan la medida solo como instrumento.

## Lotes
- El lote 03 son las siguientes **100** obras en `PENDIENTE_CRIBADO`, por `obra_id` ascendente.
