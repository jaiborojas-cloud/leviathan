# T2-A — línea de investigación de Claude (Sonnet 5.5)

Perspectiva independiente sobre los 800 basales y la pausa de `split8_j5_true/update25`. Cada agente tiene su propia carpeta en `experiments/T2_A/`; esta es solo la de Claude. Todo lo de aquí es **exploratorio** y no sustituye ningún resultado oficial, sello ni criterio congelado. No se asigna ningún outcome ni clasificación.

Corte: 2026-10-19. Los registros oficiales recuperados llegan al 2026-10-17 03:46 UTC.

## Contenido

- [`scripts/`](scripts/): análisis de margen sobre los 800 basales (`cribado_800.py`, `extremos_512.py`), prueba del mecanismo ρ_min (`escala_G.py`, `escala_G2.py`, `visita_rho.py`) y sondeo de update 25 (`sondeo_update25.py`). Solo leen datos y escriben en una carpeta de salida; el usuario los ejecuta con `python -I`.
- [`E1/`](E1/): borradores v1–v5 de la enmienda E1 al preregistro (no vigente, no congelada). La vigente de trabajo es [`v5`](E1/Leviathan_RIPG_T2-A0_enmienda_E1_BORRADOR_v5.md).
- [`estatus/`](estatus/): [estatus para el agente original](estatus/ESTATUS_PARA_AGENTE_ORIGINAL.md), [evidencia del integrador para el anexo operativo](estatus/evidencia_integrador_para_anexo.md) y plantilla de inventario de visitas.
- [`HASHES_SHA256.txt`](HASHES_SHA256.txt): SHA-256 de cada archivo de esta carpeta.

## Qué se verificó y qué no

- Verificado en terminal del usuario: integridad de los 800 basales, barrido de margen (mínimo `min_eff<10` en 9.6R, mediana 15.0R; `cond>100` mediana 23.5R), regeneración de update 25 de j5 y j6 desde semillas.
- Verificado por Claude en la entrega de solo lectura (2026-10-19): 78/78 scripts coinciden con `script_hashes.json`; el paso pausado es el **139**, no el 136.
- Hipótesis, no confirmada: el margen sigue a √ρ_min (R² 0.716 entre estados; 2 estados dentro del mismo estado). No usar como predictor ni como evidencia de frontera.
- Sin verificar: número de rechazos del integrador (ningún script lo cuenta), comparación elemento a elemento del `state.npz` de la otra corrida, max|Δθ| de j6.

## Fuera de Git

Los `.npz`, ZIP y CSV de salida con arrays (`state_025_regen*.npz`, `cribado_800.csv`, etc.) no se versionan. Sus hashes están en el estatus y en el borrador v5.
