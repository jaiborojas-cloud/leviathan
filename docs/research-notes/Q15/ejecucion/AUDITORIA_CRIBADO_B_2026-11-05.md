# Auditoría del cribado B de Q15

**2026-11-05, hora de México.** Auditor: Claude. Entregó: Codex, como lector único. Esta auditoría no modifica la entrega; las correcciones van en una versión C.

## Objeto auditado
- Paquete: `Q15_CRIBADO_B_AUDITORIA_2026-11-05.zip`, en la carpeta de salidas de Codex en la PC del responsable, fuera de Git.
- SHA-256: `86f8660d8b33e7248de35b338f5260a9ffaf602c52568354f44bd9ce3dfb961d`. Coincide con su archivo `.sha256`.
- Insumo: `Q15_v31_1_ENTREGA_B.zip`, SHA-256 `5299acf6dbbbf6187ac4e9730821f66d8fb68f1178c47d0a5c8cd4305c6029d1`, con `run_000009` para búsquedas y `run_000012` para citas, según el [cierre de la recuperación](CIERRE_RECUPERACION_v31_1_2026-11-05.md).

## Veredicto
**Aprobado como entrega parcial, con observaciones. No se acepta como cribado terminado.** El propio reporte de Codex lo declara incompleto. Todos los puntos de Q15 siguen **PENDIENTE, sin adjudicar**.

## Integridad
- `MANIFEST.sha256` interno: 21 de 21 archivos correctos. El manifiesto usa fines de línea CRLF; con `sha256sum -c` hay que quitar los `\r` antes de verificar.
- Los conteos coinciden entre `cribado.csv`, `COUNTS.json`, `VALIDATION.json` e `INTEGRITY_AND_COUNTS.json`: 4 481 obras con ruta elegible, 5 812 posiciones elegibles, 11 516 posiciones en total y 3 200 no seleccionadas, sin cambios.
- `cribado.csv` usa las 18 columnas de la plantilla del protocolo.
- Se conservan las limitaciones fijas: ICLR excluido, Google Scholar `OMITIDA_OPCIONAL`, S03 y S20 sin grafo de citas, y las 4 posiciones de A08 sin deduplicar.

| decisión | obras |
|---|---:|
| INCLUIR_PARA_TEXTO | 3 153 |
| PENDIENTE_ACCESO | 786 |
| EXCLUIR_FUERA_TEMA | 410 |
| CONTEXTO | 82 |
| PENDIENTE_VERIFICACION | 43 |
| DUPLICADO_MISMA_OBRA | 7 |
| **total** | **4 481** |

## Hallazgos

### H1. Las inclusiones son la opción por defecto, no decisiones individuales (principal)
- `q15_refine.py` aplica exclusiones, contextos y verificaciones mediante **listas explícitas de índices**. Las obras que no figuran en esas listas conservan la acción `RETAIN` y una razón de plantilla derivada del tema de la consulta que las recuperó.
- Hay 3 837 obras con `RETAIN` y alcance `TITLE`. Sus razones salen de **43 plantillas**, y en 39 de las 46 unidades de búsqueda hay un solo tema.
- Por eso la afirmación del reporte "All 4,481 titles were inspected" **no es verificable con los artefactos entregados**. Lo documentado es una **pasada de exclusión**: se sacó lo claramente ajeno y se retuvo el resto.
- **Consecuencia:** las 3 153 obras en `INCLUIR_PARA_TEXTO` requieren un cribado real por título y resumen, con una razón por obra, antes de pasar a la extracción.

### H2. Las 32 posiciones en `EXCLUIDO_FECHA` siguen sin atenderse
- La auditoría del ingreso dejó pendiente reclasificarlas a `PENDIENTE_FECHA`. En esta entrega siguen en `EXCLUIDO_FECHA`, con `date_state = FUERA_FECHA` y la razón *Recovery date postfilter; record preserved*.
- Ninguna de sus 32 obras entró al cribado, y el reporte no las menciona.
- Todas son posiciones de citas de `run_000012`: 1 de S02, 1 de S04, 1 de S08 ATRÁS, 2 de S10, 1 de S14 y 26 de S17 ADELANTE.

| posición | obra |
|---|---|
| `000012:S0_S02_ADELANTE:1` | W03804 |
| `000012:S0_S04_ADELANTE:1` | W04069 |
| `000012:S0_S08_ATRAS:48` | W04842 |
| `000012:S0_S10_ADELANTE:1` | W04992 |
| `000012:S0_S10_ADELANTE:2` | W04993 |
| `000012:S0_S14_ADELANTE:1` | W05846 |
| `000012:S0_S17_ADELANTE:1` a `:26` | W06126 a W06151 |

**Se requiere:** reclasificarlas o justificar por escrito por qué no, sin excluirlas retrospectivamente.

### H3. Exclusión por rango de índices
- 103 exclusiones se aplicaron como `range(1389, 1513)` menos 21 excepciones. El resultado depende del orden de las filas.
- Las revisé una por una y las 103 son calibración física: calorimetría, termopares, termometría y sensores CERES, todas de `L01_SemanticScholar`. **El contenido es correcto**, pero el método es frágil.
- **Se requiere:** en la versión C, listar las exclusiones por `obra_id`.

### H4. Exclusiones revisadas: ninguna parece errónea
- Busqué términos de aprendizaje automático en los títulos de las 410 exclusiones. Aparecen en 6 (W00853, W00883, W01140, W03239, W03310 y W03354), y las seis son genuinamente ajenas a Q15: contaminación, degradación de polietileno, cúmulos de galaxias, auditoría contable y costos de redes de cómputo.
- Ninguna exclusión se basa en la ausencia de resumen. Las 829 obras sin resumen que no se excluyeron por título quedaron en `PENDIENTE_ACCESO` (786) o `PENDIENTE_VERIFICACION` (43).

### H5. Uniones de identidad: sólidas
- Siete pares confirmados. Seis comparten un DOI de las memorias de NeurIPS (`10.52202/…`), verificado en la página primaria. El séptimo es el reenvío accidental que arXiv declara entre 2103.00222 y 2011.10443.
- Los 128 grupos restantes siguen separados como `PENDIENTE_VERIFICACION_IDENTIDAD`. No hubo uniones por título.

### H6. Menores
- 126 razones tienen texto corrupto por doble codificación (`1Ã¢â‚¬â€œ4` en lugar de `1–4`).
- `fecha_utc` vale `2026-11-05T19:33:45.502687+00:00` en las 4 481 filas: es la hora del sellado del paquete, no la de cada decisión. Debe declararse así.
- `abstract_reading_log.csv` tiene 40 filas para 39 obras. Falta aclarar si una obra se leyó dos veces.

## Lo que pide la versión C
1. Atender H2: reclasificar o justificar las 32 posiciones.
2. Cribar de verdad las 3 153 inclusiones de H1, por título y por resumen donde exista, con una razón propia por obra, en lotes auditables.
3. Listar todas las exclusiones por `obra_id` (H3).
4. Corregir la codificación y declarar el significado de `fecha_utc` (H6).
5. No sobrescribir la entrega B.

## Cómo se verificó
- SHA del zip con `sha256sum`, y manifiesto interno con `tr -d '\r' < MANIFEST.sha256 | sha256sum -c -`.
- Conteos, plantillas de razón, alineación entre `q15_screen_decisions.json` y `cribado.csv`, el rango de H3 y la búsqueda de términos en las exclusiones, todo con `python3 -I` sobre los CSV del paquete.
- Lectura de `q15_refine.py`. Siguiendo la regla de trabajo, no se corrieron las pruebas ni los scripts del otro agente.
