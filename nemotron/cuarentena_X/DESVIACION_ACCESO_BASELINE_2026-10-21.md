# Desviación: acceso a basales selladas de T2-A0 (Nemotron, 2026-10-21)

**Hechos** (sin valores numéricos):
- El 2026-10-21 (hora local; archivos creados 2026-10-22 04:12–04:15 UTC), un agente
  Nemotron leyó `.../Leviathan_T2A_800_basales_compacto/baseline/states` (solo lectura)
  y escribió en `leviathan/nemotron/notas/` dos tablas de 800 filas y dos resúmenes.
- Columnas extraídas (solo nombres): clasificación basal, radio nominal, `A_embed`,
  `max_Dexp_condition`, determinantes de Dexp, autovalor mínimo de la métrica, banderas de
  censura/corte/positividad; y, por resolución y fase, frontera (`R`, intersecciones,
  winding, área, topología, número de giro) y Jacobi (`R`, condición de auditoría,
  conjugado mínimo, condición intrínseca máxima, determinante mínimo, raíces).
  Varias son equivalentes o cercanas al predictor X.
- No se publicaron en GitHub: no aparecen en ninguna rama remota (verificado 2026-10-22).
- El lote 0 de producción empezó el 2026-10-22 ≈08:23 local, después de la creación de
  estos archivos. Las decisiones operativas del lote 0 y el replanteo hacia T2-A1 se
  tomaron **sin leer** su contenido: Claude solo vio los encabezados de columna y los
  conteos de régimen/clasificación basal (800 true, 800 INJECTIVE en update 5).
- 2026-10-22 16:01 UTC: los cuatro archivos se movieron a `cuarentena_X/` sin abrirlos.

**Efecto:** X sigue fijado por su hash y no se modificó; T2-A0 no queda invalidado por
este acceso. Para T2-A1 se declara que existe una copia en claro de medidas basales de
los 800 estados (incluidos los splits 12–167); el predictor de T2-A1 se fija sin
consultarla.

**Compromiso:** ningún agente vuelve a acceder a `baseline/`, `comparators/` ni a esta
carpeta. Solo `sources/` está permitido.
