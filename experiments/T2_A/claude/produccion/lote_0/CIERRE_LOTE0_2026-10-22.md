# Cierre operacional del lote 0 — 2026-10-22

**Alcance:** informe operacional del lote 0 de producción de T2-A0 (plan `3c379cee…a03a`, lanzador `2c2f8332…6570`, ejecutor v12 `2381fbcc…3347`). **Sin clasificaciones, sin Y, sin X.** Ningún archivo de `baseline/` ni `comparators/` se consultó.

## 1. Qué se ejecutó
- **Cola:** splits 8–11 × 5 inicializaciones × updates 50–250 = 180 visitas; 8 procesos; equipo del responsable (Ryzen 9 3900X, 12 núcleos físicos / 24 lógicos, 64 GB).
- **Inicio:** inventario `inventario_lote0_20261022_082545.csv` (`8bd0e681…da61`). Primera visita terminada 08:27:45; última 10:53:42 (hora de México).
- **Detención:** el lanzador se detuvo solo con `FIN: DETENIDO: menos de 50 GB libres en D` (regla del plan, sección 4). Las visitas en curso terminaron; no se lanzó ninguna nueva.

## 2. Resultado operacional (`INFORME_OPERACIONAL_lote0.json`, `92e0348a…bd3b`)
| estado | visitas |
|---|---|
| VISIT_EVALUATED | 52 |
| PAUSED_PENDING_REVIEW | 76 |
| ERROR_DE_EJECUCION | 0 |
| NO_INICIADA | 52 (split10_j19 u100–u250 y todo split 11) |

- Fracción pausada o con error: 0.4222 sobre las 180 (0.59 sobre las 128 terminadas). **Regla del 10 %: se activa** («REVISAR ANTES DEL SIGUIENTE LOTE»).
- **Motivos de pausa** (campo `reason` de `REVISION_PENDIENTE.json`; motivos operativos del anexo v1.1, no clasificaciones):

| split | LOW_RADIAL_PROGRESS | TIME_CAP | STEP_BUDGET | evaluadas |
|---|---|---|---|---|
| 8 | 45 | 0 | 0 | 0 |
| 9 | 0 | 0 | 3 | 42 |
| 10 | 8 | 18 | 2 | 10 |
| total | 53 | 18 | 5 | 52 |

  Ninguna visita pausada había entrado en refinamiento. Las pausas se concentran por split.
- **Tiempo por visita evaluada:** mediana 160 s; máximo 3265 s (visitas con refinamiento, 37–54 min). Las pausas por tope de pasos o de tiempo tardaron unos 570–700 s; las de progreso radial, unos 70 s.
- **CPU y memoria:** cada visita usa un núcleo y unos 0.35–0.5 GB (observado en el Administrador de tareas). El campo `pico_memoria_mb` del registro (4 MB) es **erróneo**: mide el proceso lanzador intermedio de Windows, no el que calcula. Defecto de medición sin efecto en resultados.
- **Disco:** el lote ocupa 152 GB en D para 128 visitas (≈ 1.2 GB por visita de media; hasta ≈ 6 GB con refinamiento). Libre al cerrar: D 27 GB, E 5986 GB.

## 3. Defectos del plan, declarados
- **Disco:** el plan (sección 5 y calendario) subestimó el espacio en un orden de magnitud. A este ritmo, un lote de 1300 visitas pediría más de 1.5 TB y la cohorte completa del orden de 10 TB.
- **Tiempo:** con visitas de refinamiento de hasta 54 min y pausas de ≈ 10 min, el calendario de 3–5 h por lote grande no se sostiene.
- **Memoria:** ver sección 2.

## 4. Decisión del responsable (2026-10-22 11:13, sin haber visto desenlaces)
- **El lote 0 queda cerrado en 128 visitas.** Las 52 no iniciadas **no se completan**, por el replanteo de T2-A0 (ver `../../CIERRE_T2A0_BORRADOR_v0.md`). Se registran como NO_INICIADA; no son pausas, errores ni negativos.
- **No se abre el lote 1.**
- `--archivar` queda pendiente: los checkpoints siguen en D.

## 5. Archivos (copias de `D:\RIPG_DATA\T2_A\produccion\lote_0\`)
| archivo | SHA-256 |
|---|---|
| `INFORME_OPERACIONAL_lote0.json` | `92e0348a62d2defd470021b0b2b21546a49bb177bcb0a96895a7e8f18eabbd3b` |
| `MANIFIESTO_lote0.sha256` (237 archivos autoritativos: estado de cada visita, `result.json` y `nominal.json`) | `1696891f464c1df4d084760e857b28aa333713d1ddbea73a20ae1154ffe1fc49` |
| `registro_lote.csv` (estado, código de retorno, segundos y fin por visita, en orden de terminación) | ver `MANIFIESTO_cierre_lote0.sha256` |
| `inventario_lote0_20261022_082545.csv` | `8bd0e68104dfc97dfe080899e5c9d6e8b220eba1567d73d30ec00768cc94da61` |

Los `result.json`, `nominal.json` y estados quedan en el equipo del responsable; el repo guarda solo sus hashes.
