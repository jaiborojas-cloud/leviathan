# Inventario fechado de visitas — 2026-10-19 (candidato para E1, no congelado)

Previstas: 8000 (800 trayectorias × 10 visitas). Abiertas o clasificadas: 4, todas en update 25 (ver `inventario_fechado_2026-10-19.csv`, tres ejes no excluyentes). **Toda visita no listada se considera NO_INICIADA a la fecha de corte** (E1 v6, sección 8): 7996.

| Estado | Visitas |
|---|---|
| clasificada | 1 (`split8_j6_true/update25`) |
| abierta / parcial | 3 (`split8_j5`, `split8_j7`, `split8_j8`, update 25) |
| no iniciada | 7996 |

Fuentes: entrega de solo lectura 2026-10-19, `inventario_visitas.csv` (sha256 `9a4fbf64…2cbe`; 8000 filas) y los registros de `records/` (corte de fuentes **2026-10-17T03:46:17Z**).

Reconciliación con el disco local (2026-10-19, búsqueda de solo lectura en `D:\RIPG_DATA\T2_A`, sin la carpeta de trajectories ni los venv): el único rastro de visitas es `expediente\archivos\partial_t025_split8_j5_true_checkpoint_snapshot.zip`. No hay `visit_complete.json`, `ode_resume*`, `origin_mpfr*`, `visits.csv`, `outcomes.csv` ni `task_log.csv` fuera de la entrega y del retorno del PC. Los parciales de j7 y j8 y los registros de visitas solo existen en la entrega recibida. **Esto no certifica ausencia de actividad posterior al corte en el entorno original ni en otras máquinas.**

**Confirmación del responsable (declaración en conversación, 2026-10-19 17:09, America/Mexico_City):** no hubo actividad después del corte de fuentes 2026-10-17T03:46:17Z. Es una declaración, no una verificación independiente.

Pendiente para congelar: fecha y hora del congelado y hash de este manifiesto.
