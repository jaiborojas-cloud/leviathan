# Desviación: acceso de un agente a las basales selladas de T2-A0 (2026-10-21)

Registro de hechos, sin valores numéricos. Copia local con el mismo contenido en `leviathan\nemotron\cuarentena_X\` del equipo del responsable (no versionada).

## Hechos
- El 2026-10-21 (hora local; archivos creados 2026-10-22 04:12–04:15 UTC), un agente Nemotron leyó `D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto\baseline\states` y escribió en `leviathan/nemotron/notas/` dos tablas de 800 filas y dos resúmenes.
- **Columnas extraídas** (solo nombres): clasificación basal, radio nominal, `A_embed`, `max_Dexp_condition`, determinantes de Dexp, autovalor mínimo de la métrica, banderas de censura, corte y positividad. Por resolución y fase: frontera (`R`, intersecciones, winding, área, topología, número de giro) y Jacobi (`R`, condición de auditoría, conjugado mínimo, condición intrínseca máxima, determinante mínimo, raíces). Varias son equivalentes o cercanas al predictor X.
- **No se publicaron:** no aparecen en ninguna rama de este repositorio (verificado el 2026-10-22).
- El lote 0 empezó el 2026-10-22 ≈ 08:23 local, después de la creación de esos archivos. **Las decisiones operativas del lote 0 y el replanteo de T2-A0 se tomaron sin leer su contenido.** Claude solo vio los encabezados de columna y los conteos de régimen y clasificación basal (800 true; 800 INJECTIVE en el update 5), que ya constan en el preregistro como condición de entrada.
- 2026-10-22 16:01 UTC: Claude movió los cuatro archivos a `nemotron/cuarentena_X/` con `mv` y `sha256sum`, sin abrirlos. Los hashes antes y después coinciden. El resto de la carpeta `nemotron/` se borró a petición del responsable.

| archivo en cuarentena | bytes | SHA-256 |
|---|---|---|
| `basales_resumen.csv` | 154250 | `29a8b9cfeb1fe7ebf194a6a59e08435718babdacf02ae743d1f7e117c63982ff` |
| `jacobi_boundary_resumen.csv` | 730874 | `f8c7274479f477d57d266b954b5ec0cc80e0697565582c53b7707f8e4bce7039` |
| `analisis_basales_2026-10-21.md` | 2384 | `86459cd7bdfe5a51d1d6580382bfc7aa69c8c64b8ae45b22c26690e78e9627ef` |
| `analisis_jacobi_boundary_2026-10-21.md` | 1783 | `59e889eb1fd9ed11291a5cda238017a8d2d3c1613b40b060b0628a5ead707d9a` |

## Efecto
- X sigue fijado por su hash y no se modificó. El preregistro exige que X quede congelado antes de los desenlaces; eso se cumple. **T2-A0 no queda invalidado por este acceso.**
- Lo que el cegado protege son las decisiones de medición del desenlace. Ninguna se tomó con esos archivos a la vista.
- **Para T2-A1:** se declara que existe una copia en claro de medidas basales de los 800 estados, incluidos los splits 12–167. El predictor y el instrumento de T2-A1 se fijan sin consultarla.

## Compromiso
Ningún agente vuelve a acceder a `baseline/`, `comparators/` ni a `cuarentena_X/`. Solo `sources/` está permitido, hasta que el responsable decida abrir X.
