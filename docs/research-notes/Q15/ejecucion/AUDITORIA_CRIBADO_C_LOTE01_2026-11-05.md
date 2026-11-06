# Auditoría de la entrega C, lote 01, de Q15

**2026-11-05, hora de México.** Auditor: Claude. Entregó: Codex, como lector único. Antecede: [auditoría del cribado B](AUDITORIA_CRIBADO_B_2026-11-05.md).

## Objeto auditado
- Paquete: `Q15_C_LOTE01_D01_SemanticScholar_2026-11-05.zip`, fuera de Git.
- SHA-256: `56a1bb737e583652cce1ba979b2e36045a039eb369f3cf905518641fbe057ad6`. Coincide con su archivo `.sha256`.
- Manifiesto interno: 22 de 22 archivos correctos. Ahora usa LF, así que `sha256sum -c MANIFEST.sha256` funciona directamente.

## Veredicto
**Aprobado.** H2, H3 y H6 quedan resueltos, y el lote 01 está cribado con razones propias. Hay una observación de criterio (O1) que conviene fijar antes del lote 02. Todos los puntos de Q15 siguen **PENDIENTE, sin adjudicar**.

## Verificaciones

### Cambios solo donde se declararon
- **Posiciones:** comparé `posiciones_C.csv` contra `positions.csv` de B celda por celda. Hay 11 516 posiciones en el mismo orden. Solo cambian `status`, `date_state` y `reason`, y solo en las 32 posiciones que señaló H2. Las columnas nuevas `status_B`, `date_state_recuperacion` y `cambio_C` preservan los valores anteriores.
- **Obras:** comparé `cribado_estado_C.csv` contra `cribado.csv` de B por `registro_id` (B tiene 7 `obra_id` repetidos por los duplicados confirmados). Están los 4 481 registros de B y se agregan 32 obras de H2, en total 4 513. Transiciones:

| B → C | registros |
|---|---:|
| INCLUIR_PARA_TEXTO → PENDIENTE_CRIBADO | 3 148 |
| INCLUIR_PARA_TEXTO → INCLUIR_PARA_TEXTO (lote 01) | 2 |
| INCLUIR_PARA_TEXTO → CONTEXTO (lote 01) | 2 |
| INCLUIR_PARA_TEXTO → EXCLUIR_FUERA_TEMA (lote 01) | 1 |
| resto de decisiones de B | sin cambio |
| obras nuevas de H2 → PENDIENTE_FECHA | 32 |

Pasar las 3 148 retenciones por defecto a `PENDIENTE_CRIBADO` corrige el problema de fondo de H1: ya no se presentan como inclusiones.

### H2: resuelto
Las 32 posiciones pasan de `EXCLUIDO_FECHA` a `PENDIENTE_FECHA`, sin promoverse a elegibles y sin reponer cuotas. La justificación es coherente con la sección 3 del protocolo: el corte se aplica a la **primera disponibilidad pública verificable**, y las fechas contradictorias quedan pendientes. En 31 casos, la fecha del metadato es posterior al corte del 2026-11-02, pero no prueba que no exista una versión anterior. W04842 (1896) queda antes de la ventana más amplia y también pendiente.

### H3: resuelto
`exclusiones_por_obra_id.csv` tiene 411 filas con 411 `obra_id` distintos. El conjunto coincide exactamente con las 410 exclusiones de B más W00014.

### H6: resuelto
No queda texto corrupto en las razones vigentes, y `correcciones_H6.csv` conserva el antes y el después. `fecha_utc` se declara como hora de sellado, sin inventar horas de decisión. Las 40 filas del registro de lectura corresponden a 39 obras: W00070 aparece en dos posiciones con resúmenes que solo difieren por un espacio U+00A0, y es la misma obra.

### Lote 01: decisiones revisadas contra los resúmenes
Leí los cinco resúmenes de `evidencia_lote01.json`.

| obra | decisión | revisión |
|---|---|---|
| W00014 | EXCLUIR_FUERA_TEMA | Correcta. Es un modelo de volatilidad; el R² fuera de muestra y el Fisher scoring son herramientas, no el objeto. El protocolo excluye las aplicaciones sin contenido relevante. |
| W00017 | INCLUIR_PARA_TEXTO | Correcta. Analiza cuándo el R² fuera de muestra es positivo según persistencia, horizonte y tamaño muestral, que es metodología de evaluación incremental. |
| W00024 | CONTEXTO | Defendible, pero ver O1. Es un modelo AR base contra un AR ampliado, con R² relativo y prueba de Clark y West. |
| W00026 | INCLUIR_PARA_TEXTO | Correcta. Contrasta la habilidad frente a la media y frente a la persistencia, con controles por permutación: un punto metodológico sobre la elección de la base. Su fecha (2026-07-02) cae dentro del corte. |
| W00027 | CONTEXTO | Defendible, pero ver O1. |

## Observación

### O1. Usar CONTEXTO para aplicaciones requiere un criterio escrito
La sección 6 del protocolo reserva el contexto para revisiones, tutoriales y notas secundarias, y excluye las "aplicaciones sin contenido relevante". W00024 y W00027 son aplicaciones primarias que usan la evaluación contra una base sin aportar método, y quedaron en CONTEXTO. W00014 es del mismo tipo y quedó excluida. La diferencia que Codex sostiene, ilustrar la comparación incremental frente a solo usar R², es razonable. Pero si no se escribe antes de seguir, en los lotes siguientes puede aplicarse de forma desigual.

**Se requiere:** antes del lote 02, una regla de una o dos líneas, aplicada igual en todos los lotes, que separe las aplicaciones que van a CONTEXTO de las que se excluyen. La regla interpreta el protocolo sin cambiarlo y la aprueba el responsable. Si no se fija, la alternativa conservadora es excluir las aplicaciones sin contenido metodológico, como dice el texto de la sección 6.

## Cómo se verificó
- SHA del zip y `sha256sum -c MANIFEST.sha256`.
- Comparación celda por celda entre B y C de posiciones y obras, comparación de conjuntos de exclusiones y búsqueda de texto corrupto, con `python3 -I` sobre los CSV de ambos paquetes.
- Lectura de los cinco resúmenes del lote y de las secciones 3 y 6 de `PROTOCOLO_OPERATIVO_v3.md`.
- No se corrieron los scripts del otro agente.
