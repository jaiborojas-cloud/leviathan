# Auditoría de la entrega C, lote 03, de Q15

**2026-11-05, hora de México.** Auditor: Claude. Entregó: Argon ("Antigravity (IA)"), como lector único. Aplica los criterios de los commits `0b9592b1` (CONTEXTO) y `b11d7238` (medidas de dificultad, opción B).

## Objeto auditado
- Paquete: `Q15_C_LOTE03_2026-11-05.zip`, en la carpeta de trabajo de Argon, fuera de Git.
- SHA-256: `46354f8361951c13c868c422f210ed9ee174d8e2ee7a63f1fd77565ee3ef3cff`. Coincide con su `.sha256`.
- Manifiesto interno con LF: 7 de 7 archivos correctos.
- Declara intacto el paquete del lote 02 (`8c6a9a1e…59a8`).
- Tiempo declarado: de 16:43:08 a 16:50:42, unos 8 minutos para 100 obras. Argon agotó su cuota justo después de sellar el paquete; el lote está completo.

## Veredicto
**Aprobado, sin observaciones de criterio.** Todos los puntos de Q15 siguen **PENDIENTE, sin adjudicar**.

## Verificaciones (recalculadas por Claude)
- Las 100 obras son exactamente la selección fijada antes de leer.
- Decisiones: EXCLUIR_FUERA_TEMA 83, INCLUIR_PARA_TEXTO 16, CONTEXTO 1. Hay 100 razones distintas, y las 100 obras se leyeron con resumen.
- Columna `arxiv`: un solo ID sin versión por obra, sin `|` y sin sufijo de versión, como se pidió.
- Grupos de título duplicado: todos los que tocan el lote quedaron anotados en `conflicto` (por ejemplo TG001, TG002 y TG006). No hubo fusiones.
- `correcciones_lote02.csv`: las 6 obras de O2 tienen razones nuevas que citan el criterio, y conservan la decisión y la razón anteriores en columnas aparte. El paquete del lote 02 no se modificó.

## Revisión de la alta tasa de exclusión
83 de 100 es mucho más que en el lote 02 (12 de 50). Revisé los 100 títulos y leí los resúmenes y las razones de los casos dudosos. La tasa se explica por las consultas de origen:
- **T05** (confianza y calibración) trajo muchos homónimos: confianza en agentes LLM, detección de objetos, rastreo, robótica y otros.
- Las unidades de **núcleos de Fisher** trajeron trabajos de recuperación de imágenes que usan *Fisher Vectors* de un GMM sobre descriptores locales, que no son la información de Fisher de los parámetros de una red.

Las razones distinguen bien esos casos. Por ejemplo, W00346 y W00348 se excluyen porque el "Fisher" es la codificación de un GMM, mientras que W00345, W00349, W00374 y W00375 se incluyen porque tratan la información de Fisher de un modelo. Las inclusiones abarcan la literatura central de la pregunta 3: *Critical Learning Periods*, *Catastrophic Fisher Explosion* y *When Does Label Smoothing Help?*. Algunos casos son de frontera pero defendibles con su razón, como W00153 (el suavizado de etiquetas mejora la calibración) y W00377 (resultado teórico que liga influencia, curvatura e información de Fisher).

## Avance
Ya se cribaron 155 de las 3 153 retenciones de B: 5 en el lote 01, 50 en el lote 02 y 100 en el lote 03. Quedan 2 998 en `PENDIENTE_CRIBADO`.

## Cómo se verificó
- SHA del zip y `sha256sum -c MANIFEST.sha256`.
- Recuento de la selección, las decisiones, las razones, el formato de `arxiv` y las anotaciones de grupo con `python3 -I`, contra `cribado_lote03.csv`, `correcciones_lote02.csv` e `identity_adjudication.csv` de B.
- Lectura de los resúmenes en `evidencia_lote03.json` para los casos de frontera.
