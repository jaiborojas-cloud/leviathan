# Estatus de la sesión paralela sobre la compacta — para el agente original de T2-A

**Fecha de corte:** 2026-10-19. **Alcance:** trabajo hecho en una sesión de chat con Claude sobre la carpeta `Leviathan_T2A_800_basales_compacto`, el ZIP `RIPG_RESULTADOS_PC.zip` y los archivos que generó el responsable en su PC. **No hubo acceso al entorno completo** (faltan 66 de los 78 scripts de `script_hashes.json`, los registros de visitas y la continuación 5→250).
**Convención:** [VERIF] = salida literal de terminal del responsable o archivo revisado directamente. [INFER] = deducción. [HIPÓTESIS] = exploratorio, sin validar. Los scripts de esta sesión los escribió el asistente y los ejecutó el responsable (`python -I`, venv_torch, Windows).

## 1. Estado del caso (alineación de terminología)

- Visita: `split8_j5_true`, régimen true, update 25. Integración MPFR desde el origen **pausada deliberadamente**: el cálculo tardaba mucho y se detuvo para analizar por qué; **no hubo fallo ni excepción registrada**. [VERIF `progress.md`, `index.json`, `task_log.csv`]
- Paso aceptado **139** en todos los archivos (el responsable lo recordaba como 136; confirmar), r₁₃₉ = 0.07447265825972331, nfev 2651, CPU 2589.28 s, pared 2606.59 s. r₁₃₉ no es radio nominal ni frontera certificada; el radio nominal de esa visita no está determinado.
- Diagnóstico del agente original (según el responsable; paquete `Leviathan_T2A_diagnostico_paso139.zip`): frontera de la familia softmax a distancia intrínseca finita; rayos 1775/1776; borde local mínimo ≈ 0.07447421007 (corrige 0.07447440069); certificación global **INCONCLUSIVE**; área diagnóstica del prefijo ≈ 0.018714 (< 0.02), no A_embed.
- Snapshot de update 25 de la otra corrida: `partial_t025_split8_j5_true_checkpoint_snapshot.zip` SHA-256 `9970F03618264059921462821F8B611E8A0008293E2ECF5DB388EF99C0A4749E`; su `state.npz` SHA-256 `6713246b106c517b0d887d8cc3c61026d6a21d68e745f653ec682dcbe139e19c` coincide con el documentado. [VERIF]

## 2. Lo que se hizo y su estatus

**Integridad de insumos [VERIF]**
- `verificar.py`: PASS (800 checkpoints basales y archivos compactos). 16/16 partes ZIP con SHA-256 correcto.
- `sources/`: de 78 entradas de `script_hashes.json`, 12 existen y coinciden; **66 faltan en disco; ningún MISMATCH**.

**Basales (update 5) [VERIF]** — 800/800 INJECTIVE_AT_NOMINAL_RADIUS con predictor PASS; radio nominal 0.07976–0.07980; |det|min ≈ 1; `predictor.radius` = r* = 0.05697156262709151. Semillas de j5 (1008/2005/4085) y j6 (1008/2006/4086) coinciden con las fórmulas del preregistro.

**Margen basal softmax (exploratorio) [VERIF]** — 800 estados, update 5, 128 rayos, rejilla 0.5R, umbrales elegidos por el analista:
- primer cruce de min_eff < 10: 9.6R a 19.5R (mediana 15); de cond(G) > 100: 10.1R a 36.5R (mediana 23.5).
- Estable con 128/256/512 rayos en los 10 estados de menor margen (resolución 0.1R).
- `f` es idéntico entre los 5 inits de cada uno de los 160 splits. El cruce de cond(G) tiene 92 % de varianza entre splits (el de min_eff, 34 %).
- Reproducibilidad: dos ejecuciones dan los mismos cruces.

**Reentrenamiento a update 25 [VERIF]** — desde las semillas del manifiesto, con compuerta en update 5: j5 max|ΔM| 1.4×10⁻¹¹ y max|Δθ| 6.9×10⁻¹⁶; j6 max|ΔM| 2.1×10⁻¹¹ (**max|Δθ| de j6 pendiente**). `state_025_regen.npz` (j5) `845C2251…4776`; `state_025_regen_j6.npz` `0E3FBFD3…6CAC`. Son **copias exploratorias**, no sustituyen ninguna corrida confirmada. Las cantidades derivadas de j5 coinciden con el snapshot de la otra corrida a los dígitos impresos (max|M| 1.138; autovalores de G(P₀) 0.00054407 y 0.00652912; ρ_min 0.022609); **la diferencia elemento a elemento de M no se ha reportado**.

**Sondeo directo en doble precisión (`rays`, DOP853, 128 rayos, R_ref = 0.0797751845662646 = nominal basal de j5) [VERIF]**
- j5 update 25: min_eff cruza 10 en ≈ 0.44R_ref; max cond(G) = 95.8 a 0.80, 256 a 0.85 y 1.05×10⁵ a 0.90R_ref. A 0.95R_ref el cálculo tardó mucho y **el responsable lo interrumpió**; no se sabe si habría terminado o fallado.
- j6 update 25: sin señales de borde hasta 0.95R_ref (min_eff 6.7; cond 43); min_eff cruza 10 en ≈ 0.756R_ref.

**Evidencia de la integración pausada (de `RIPG_RESULTADOS_PC.zip`) [VERIF]**
- 13 segmentos (12 de 4 pasos + uno final de 1 paso), pasos 91–139. Estado guardado del solver: DOP853 de SciPy, rtol 2e-10, max_step = inf, t_bound = 0.09, 8192 variables.
- `task_log.csv` (sin encabezado): campo 5 = nfev acumulado; campo 6 = **tiempo de integración (pared) acumulado**, no CPU.
- Paso aceptado ≈ 3.3×10⁻⁵ hasta el 118; 1.9×10⁻⁵ (121), 5.6×10⁻⁶ (127), 1.6×10⁻⁶ (133), 4.3×10⁻⁷ (139); cociente entre pasos consecutivos 0.805–0.816 desde el 125.
- Pared por paso aceptado: 16–20 s hasta el 118; ≈ 29 s desde entonces.
- [INFER] Rechazos por nfev (15 evaluaciones por paso aceptado, 12 por rechazo): 0–1 por bloque de 4 pasos hasta el 118 y 1 por paso aceptado desde ~119. Supuesto sin verificar en el código del integrador.

**Preregistro T2-A0 leído [VERIF]** — Y = 1 si alguna de las 10 visitas (25…250) es GEOMETRIC_NONINJECTIVITY; Y = 0 solo si las 10 son INJECTIVE; INCONCLUSIVE y NUMERICAL_FAILURE no son ceros; «sin reducir el radio nominal para rescatarlo»; bootstrap de splits completos (20000, semilla 220020); PASS_PROSPECTIVE_PILOT exige entre otros ≥ 640 elegibles en ≥ 128 splits, ≥ 30 eventos en ≥ 10 splits, lift ≥ 3 e IC95 % > 0; toda incompatibilidad requiere enmienda versionada antes de estados nuevos.

**Inspección de solo lectura de `sources/` [VERIF parcial]** — hecha con otro modelo (Nemotron 3.5 super VL) y con el agente local; las citas de línea no se re-verificaron. Hallazgos: solo `solve_ivp` DOP853 de una pasada y RK4 de paso fijo (sin límites de pasos ni de tiempo, con comprobación de `success`); sin recuento de rechazados; reanudación solo de pesos, Adam y RNG, y solo probada en `replay()`. **Estas conclusiones valen solo para `sources/`**, no para el integrador de visitas.

## 3. Hipótesis y puntos que NO deben tomarse como hechos

- **Mecanismo ρ_min [HIPÓTESIS]:** el cruce de min_eff < 10 sigue ≈ √ρ_min, con ρ_min = menor autovalor de QᵀMQ, Q base ortonormal de span(f − f̄). Sobre 800 basales: R² 0.72 para min_eff, nada útil para cond(G). Entre updates, j5: predicho 0.459R, medido ≈ 0.44R (calculado después de ver el dato); j6: predicho 0.807R **antes** de ver el dato, medido ≈ 0.756R. Dos estados; no confirmatorio.
- La estimación «borde de j6 hacia 1.6R» es ilustrativa y calibrada con j5.
- En mensajes de la sesión se dijo que la integración «se atasca» o «se arrastra sin lanzar excepción». **No está demostrado**: fue una pausa por tiempo, y el criterio de parada interno de `solve_ivp` o del integrador de visitas no se ha verificado.
- El radio nominal de update 25 no está determinado; las unidades «R» de los sondeos usan el nominal basal de j5.

## 4. Decisiones del responsable (borrador de enmienda E1; no vigente ni congelado)

- Resultado confirmatorio de T2-A0: **opción C**. Las visitas no resueltas mantienen su disposición INCONCLUSIVE; la salida del dominio certificada es un diagnóstico adicional, no evento ni negativo. `split8_j5_true` update 25 permanece INCONCLUSIVE y no cuenta como Y = 0. «Fallo técnico» significa que no se pudo completar la auditoría exigida (la causa puede ser geométrica, pero requiere certificación).
- Análisis complementario de identificación parcial (opción A corregida), definido **después** de observar este caso, con cotas por asignaciones adversas por posición (dentro/fuera de la cola); no sustituye el veredicto ni permite declarar PASS. Intervalos: bootstrap percentil exploratorio, cobertura no validada; lift no definido con tasa base cero y su intervalo queda no evaluable.
- La recopilación no se detiene. El informe final abre con el resultado bajo T2-A0 y reporta siempre cuatro categorías: salidas certificadas, sospechas pendientes, pausas/auditorías irresueltas, trayectorias Y no determinado.
- Regla de pausa: cuatro componentes (pasos intentados contando rechazos, presupuesto de tiempo con hardware y precisión, falta de progreso radial con escala y ventana, cond(G) como alarma auxiliar). **Sin valores hasta tener evidencia**; irán en un anexo operativo versionado. Todo disparador produce pausa y checkpoint, nunca clasificación ni certificación.
- Condiciones previas para aplicar E1: anexo operativo e inventario fechado de visitas.

## 5. Solicitudes al agente original (para evitar retrabajo)

**No repetir** lo ya hecho arriba. **Entregar, de solo lectura y tal cual se ejecutaron** (se verificarán contra `script_hashes.json`):
1. Integración y diagnóstico del paso 139: `resumable_dop853.py`, `validate_resumable_dop853.py`, `fast_mpfr_acceleration.py`, `origin_mpfr_replay.py`, `check_origin_mpfr_resume.py`, `close_origin_mpfr_session.py`, `close_origin_mpfr_batch2.py`, `prepare/validate/close_fast_mpfr.py`, `stall_diagnostic_reproducible.py`, `stall_one_step_probe.py`, `finalize_stall_diagnosis.py`, `diagnose_pending_s384.py`, `save_pending_diagnosis.py`.
2. Sesiones y continuación: `bounded_session.py`, `session_runner.py`, `close_session.py`, `followup.py`, `run_followup.py`, `followup_bounded_verified.py`, `checkpoint_followup_running.py`, `continue_first_pending_geometry.py`, `restore_f001.py`, `close_f001_*.py`, `persist.py`, `atomic_csv.py`, `instrument/case_engine_resumable.py`.
3. Análisis: `primary_analysis.py`, `analyze_final.py` (no deben modificarse).
4. Inventario de visitas abiertas: id, update, estado (clasificada, parcial, no iniciada), clasificación si existe, fecha de corte y hash. Registros completos de `split8_j6_true` update 25 (task_log, tiempos, nfev, pasos, hardware, hilos) y cualquier registro que cuente pasos rechazados.
5. Una nota breve de qué se recuperó en los scripts `restore_b*` y `recover_b*`.

**Preguntas:** ¿el paso de pausa fue 136 o 139? ¿Por qué el tiempo por paso aceptado pasó de 16–20 s a ≈ 29 s (¿un rechazo por paso aceptado?)? ¿Cómo se cuentan hoy los pasos intentados y los rechazados? ¿Qué criterio de parada interno aplica el integrador de visitas?

**Restricciones para retomar:** no cambiar protocolo, X, comparadores, umbrales, cola ni clasificaciones; no usar r₁₃₉ como radio nominal ni reducir el radio nominal; mantener separados predictores y evaluadores; no asignar outcomes; no reanudar más allá del borde sin la regla de pausa ya versionada; no usar `state_005.npz` de los basales ni el estado de `j7` para el contraste de update 25.

## 6. Archivos y hashes (expediente del responsable)

| Archivo | SHA-256 |
|---|---|
| cribado_800.py | EF45AF911AD6AC2D61D2197F65EB9D6D5FE0308EEDFA91807A489219F40F547E |
| extremos_512.py | 7A06995B5EDC8D48C0606970B459E203098603A567ED2D9F54C3C2B34F501F7D |
| escala_G.py | 97EE7439AC200E3EC2D5A7F785E5C15BEA50D8A67A2F5A00EB11EB9BBA53D931 |
| escala_G2.py | 755AEB0E3B2EE53CA2F3E507AA6053BB23DFBDFCF5F1253199B80704DAEA977A |
| visita_rho.py | 098141B96DC1F3680971A96806F8DF823875BAECA4385B6AC36522A44D8F1981 |
| sondeo_update25.py | CFEA44C62D2B4FAB2D9DC8C5E0DFBBC8050697508036AE6EDE0F49BE761F92EB |
| cribado_800.csv | FBB5FF302FD3A7CC1191AD9BCA556B6BD862E9F70D0166D8E8193FBCCCAA44E4 |
| extremos_512.csv | 4AB7B855794C5CE34F8325E183EF028C8BE103CD16793976DEAB4494A6AB9CB6 |
| escala_G.csv | 44722C27F0112B67CEC7002DD3F641711B84EA5D2A50B72537CD4FF49200C0E5 |
| escala_G2.csv | 748F4FA375ED9CC0007E2A9C0D330CFA6FD5A01DF9976D5A10BE79901EF70435 |
| state_025_regen.npz (j5) | 845C22519A20BE8CEEF4E35210157D97BD5BC223FC9F05E1769B91D998AA4776 |
| state_025_regen_j6.npz | 0E3FBFD3DD290B6CF11F8402664C224F668A2F9F4C4055D7E484AD19D5026CAC |
| sondeo_j5_u25.csv (interrumpido en 0.90R) | 38B5D4BEDF4FBBE3AC447CC22A7E579CF1E55701C51903BF7D01A57E23051F3B |
| sondeo_j6_u25.csv (hasta 0.95R) | 4522E8C618F7B9B42BA03A1598BE009B954618ABC046C76495898CAA498BEEE2 |
| Enmienda E1 BORRADOR v5 (md) | 0C87D1E97117BC181CD27BA72A523539AF8947AD2D2338F1D34C309DB6A26F23 |
| evidencia_integrador_para_anexo.md | C685FB64276E5C1008DF33253511C0004420C797BDE73CACA237095A5B3EA94C |
| inventario_visitas_PLANTILLA.csv | E10E5E342AAC55A10C5A8C5C4FDB349FAC17AC1C3CE918CDC0527A8AE9316378 |

Descartados (no usar): primera tabla de 20 estados y `screening_20.log` (IDs inexistentes), R₀ = 0.1082 (`calibrate` no se pudo ejecutar: falta `persist`), umbrales 0.48R/1.3R/4.5R.

**Pendientes del lado del responsable:** max|Δθ| de j6; diferencia elemento a elemento de M entre `state.npz` y `state_025_regen.npz`; inventario fechado; anexo operativo; revisión estadística externa del procedimiento de intervalos; congelar E1 con hash.
