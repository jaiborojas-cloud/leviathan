# Auditoría de la entrega C, lote 02, de Q15

**2026-11-05, hora de México.** Auditor: Claude. Entregó: Argon (se identifica como "Antigravity (IA)"), como lector único. Es su primer lote tras la [reasignación de Q15](DECISION_CRITERIO_CONTEXTO_Y_LOTES_2026-11-05.md) y [la adenda](ADENDA_AUDITORIA_CRIBADO_B_2026-11-05.md).

## Objeto auditado
- Paquete: `Q15_C_LOTE02_2026-11-05.zip`, en la carpeta de trabajo de Argon, fuera de Git.
- SHA-256: `8c6a9a1e1dd348885a68b262dda7ce303bac5c2a0324439610204229dcf559a8`. Coincide con su `.sha256`.
- Manifiesto interno con LF: 6 de 6 archivos correctos.
- Insumos verificados por Argon y declarados: el lote 01 de C (`56a1bb73…7ad6`) y `Q15_v31_1_ENTREGA_B.zip` (`5299acf6…29d1`).
- Tiempo de cribado declarado: de 16:25:45 a 16:31:37, unos 6 minutos para 50 obras.

## Veredicto
**Aprobado, con una observación de criterio (O2)** que debe resolver el responsable antes del lote 03. Todos los puntos de Q15 siguen **PENDIENTE, sin adjudicar**.

## Verificaciones (recalculadas por Claude)
- Las 50 obras son exactamente la selección fijada antes de leer.
- `cribado_lote02.csv` tiene las 18 columnas de la plantilla, en orden.
- Decisiones: INCLUIR_PARA_TEXTO 28, EXCLUIR_FUERA_TEMA 12, CONTEXTO 9, PENDIENTE_ACCESO 1. Coinciden con el informe.
- Hay 50 razones distintas, una por obra.
- 95 posiciones elegibles en el registro de lectura, que coinciden con las 95 de `posiciones_C.csv` para esas obras.
- W00126 queda en PENDIENTE_ACCESO porque su único resumen es `","`. Es correcto.
- El grupo de identidad TG000 (W00098 y W00135, *Deep Learning on a Data Diet*) existe en `identity_adjudication.csv` de B, y no se fusionó. Es correcto.
- **N1 atendido en el lote:** se reunieron los DOI y los ID de arXiv de todas las posiciones elegibles (42 de 50 obras con DOI y 30 con arXiv).

## Calidad de las razones
Leí las 21 razones de exclusión y contexto contra sus resúmenes, y los títulos de las 29 restantes. Las razones citan el contenido concreto del resumen y no hay plantillas. Las inclusiones abarcan la literatura central de las preguntas 2 y 4: *Data Diet*, *Dataset Cartography*, olvido de ejemplos, EL2N y GraNd, y poda dinámica. **Es una mejora clara frente a B.**

## Observación

### O2. CONTEXTO se extendió más allá del criterio aprobado, y se aplicó de forma desigual
El criterio aprobado cubre las aplicaciones cuya pregunta central es una **evaluación incremental**. W00044, W00057 y W00080 encajan en él.

Argon usó además CONTEXTO para **aplicaciones que usan medidas de dinámica de entrenamiento o dificultad por ejemplo como herramienta**: W00100, W00110, W00112, W00121, W00122 y W00131. Esa categoría no está en el criterio aprobado. Además, en casos parecidos excluyó: W00108 y W00120 usan eventos de olvido para seleccionar muestras de un ataque, y W00133 usa EL2N y GraNd como líneas base.

La sección 6 del protocolo incluye la dificultad por ejemplo, así que no basta con decidir entre CONTEXTO y EXCLUIR. **Se requiere una decisión del responsable** que fije, para estas aplicaciones:
- **Opción A:** todas a CONTEXTO, incluidas W00108, W00120 y W00133.
- **Opción B:** INCLUIR_PARA_TEXTO si reportan un hallazgo sobre la propia medida (cuándo funciona, falla o se relaciona con la generalización), y EXCLUIR si solo la usan como instrumento.

Con la opción B, W00100, W00110 y W00131 pasarían a INCLUIR, y W00112, W00121 y W00122 a EXCLUIR. Las seis se corrigen en el paquete del lote 03, sin modificar el del lote 02.

### Menor
En `arxiv`, algunas obras tienen la versión y el ID sin versión juntos (`2205.07246v3 | 2205.07246`) y otras solo uno. Conviene normalizar a un solo ID sin versión y dejar la versión en `version_id`. Se puede hacer en la consolidación final.

## Cómo se verificó
- SHA del zip y `sha256sum -c MANIFEST.sha256`.
- Recuento de la selección, las decisiones, las razones y las posiciones con `python3 -I`, contra `cribado_lote02.csv`, `log_lectura_lote02.csv` y `posiciones_C.csv` del lote 01.
- Lectura de los resúmenes en `evidencia_lote02.json`.
