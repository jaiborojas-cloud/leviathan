# Q15 v3.1: cierre de la recuperación (ejecutor v2.1), 2026-11-05

Lo redactó Claude a partir de las salidas que el responsable copió de su PC. Es **documental**: no evalúa la pertinencia de ningún registro.

## Ejecución
- **Equipo:** el del responsable, Windows 11, con Python 3.12 en `D:\RIPG_DATA\venv_q15`.
- **Código:** clon `D:\leviathan-q15-v31-1` en el commit `505e4239`. SHA verificados antes de correr: ejecutor `6f05b419…` y suite `e1782c6d…`.
- **Pruebas:** `Q15_v31_1_CONTROLES\pruebas_002.json` con **98/98 OK**.
  - `pruebas_001` en esa misma carpeta se corrió por error con la suite v2 (91 pruebas, 4 fallos de separadores ya conocidos). Se conserva.
- **Preparación:** `Q15_v31_1_PREPARACION_B`, con código 0.
  - `Q15_v31_1_PREPARACION` la llenó por error el ejecutor v2; el ejecutor v2.1 la rechazó por identidad. Se conserva.
- **Salida de red:** `D:\RIPG_DATA\Q15_v31_1_RED`, fuera de Git. Las corridas van de `run_000001` a `run_000012`:
  - el último run completo de `--fase todo` es **`run_000009`**;
  - el último de `--fase citas`, que es el final, es **`run_000012`** (escrito a las 09:15:32).
  - `run_000010` (08:55) y `run_000011` (09:05) son reintentos intermedios de citas.
- **Sin clave S2:** el formulario de Semantic Scholar rechaza correos de dominio gratuito.

## Desviaciones operativas (no tocan consultas, topes, orden ni insumos)
1. **`--timeout 120`** en lugar de 45 en las corridas con `--reintentar-fallos`. Con 45 s, los índices de NeurIPS 2022–2024 fallaban sin respuesta (estado `None`, 6 intentos). Con 120 s se recuperaron. El tiempo de espera no forma parte de `IDENTIDAD.json`.
2. **`--fase citas --reintentar-fallos`** para reintentar solo las anclas, sin recalcular los catálogos.
3. **Interrupciones con Ctrl+C** (código de Windows -1073741510) y reanudación sobre la misma salida, como dice el procedimiento.

## Inventario (run_000009 y run_000012)
**Búsquedas (294 unidades):**
- COMPLETA 104;
- TRUNCADA_DECLARADA 5;
- OMITIDA_OPCIONAL 55 (Google Scholar);
- PARCIAL_CATALOGO 129 (43 consultas por 3 catálogos; ver ICLR);
- PARCIAL 1 (A08 en S2).

**Catálogos:**

| catálogo | registros | avisos declarados |
|---|---|---|
| NeurIPS | 30 602 | `ANIOS_NO_LISTADOS_PENDIENTES_DE_COMPROBAR: 2026` (memorias aún no publicadas); 1 artículo de 2000 no recuperado |
| ICML (PMLR) | 20 905 | `HISTORICO_ICML_ANTERIOR_A_PMLR_NO_RECUPERADO` |
| ICLR (OpenReview) | **0** | ver decisión abajo |

**Citas (19 anclas, una por dirección), según el run final `run_000012`:**
- COMPLETA 22, TRUNCADA_DECLARADA 7, PARCIAL 5, PENDIENTE_RESOLUCION_ANCLA 4 (2 anclas). **Hay 17 de 19 anclas resueltas.**
- **Anclas sin resolver:**
  - **S03**: **429** de S2 en todos los intentos.
  - **S20**: **404** en `search/match`; S2 no encuentra el título y no es reintentable.
  - Se cerró la recuperación sin más reintentos.
- **Parciales:**
  - S04, S16 y S17 ATRÁS: `FIN_ANTES_DEL_TOTAL_DECLARADO`, porque S2 entrega menos referencias que su `referenceCount`;
  - S18 y S19 ATRÁS: `Semantic Scholar no devuelve data[]`.

## Incidencias
- **A08_SemanticScholar = PARCIAL.** `ID_REPETIDO_BULK` con los paperId `92b9619db5b9768351c4822f36b1ab2e735dae75` y `8c76b4f7a77523e88a32d5d798b03bbf615cb12f`: el proveedor repite esos dos registros dentro de la misma página. La evidencia cruda se conserva. **No se deduplicó.** Cómo tratarlos en el cribado lo decide el protocolo.
- **ICLR / OpenReview:**
  - 2018–2026 dan **403** en `/notes`, en `api` y en `api2`. Desde el incidente de seguridad de noviembre de 2025, OpenReview exige autenticación; las consultas anónimas reciben un anti-bot challenge.
  - 2013–2017 dan **404** en `/groups`: esos identificadores de grupo no existen con el formato que usa el ejecutor.

## Decisión del responsable (2026-11-05, 09:12, hora de México)
**ICLR queda excluido como catálogo y se declara como limitación de alcance.** No hay vía razonable de acceso autenticado para el responsable. La decisión se tomó **sin haber visto ningún registro de ICLR**, porque no se recuperó ninguno.
- Los estados fallidos de ICLR **se conservan tal cual**: no se reemplazan ni se borran.
- **Cobertura residual:** solo lo de ICLR que aparezca en las consultas de Semantic Scholar o arXiv, con el tope K = 200 de cada una. Los trabajos de ICLR poco citados pueden quedar fuera, y la conclusión de Q15 debe decirlo.
- **Ampliación futura posible**, ninguna autorizada: las listas oficiales de iclr.cc (aproximadamente 2020 en adelante, sin cuenta) o OpenReview autenticado. Cualquiera de las dos requeriría una enmienda, una versión nueva del ejecutor y pruebas.

## Pendiente para el otro agente
1. Registrar en el PR #138 este cierre, las desviaciones 1–3 y la decisión sobre ICLR.
2. Hacer el cribado y la extracción según el protocolo v3 sobre `Q15_v31_1_RED` (`run_000009` para las búsquedas, `run_000012` para las citas). Claude lo audita.
3. **Google Scholar** sigue como OMITIDA_OPCIONAL, como dice el protocolo. Si el otro agente lo cree necesario para S20 o S03, puede proponer una consulta manual complementaria **registrada antes**, con consulta, fecha y campos anotados. Esa consulta no sería parte de la búsqueda sistemática.

## Corrección (2026-11-05, 09:50)
La primera versión de este reporte (commit `caf78c94`) atribuía el inventario final de citas a `run_000011`. **Es un error de Claude.** Esas cifras (17/19 anclas, pendientes S03 y S20) salen de **`run_000012`**: el comando de resumen tomaba el run más reciente y no se verificó su nombre.

Lo detectó el otro agente al revisar el primer paquete, `Q15_v31_1_ENTREGA.zip` (SHA `8428591b…2b4e`). Ese paquete trae `run_000011`, que tiene 18 COMPLETA y 8 PENDIENTE_RESOLUCION_ANCLA (S03, S06, S07 y S20). El paquete se conserva, pero queda **sustituido** para las citas por `Q15_v31_1_ENTREGA_B.zip`, que incluye `run_000012`. Su SHA se publica en el PR #138.
