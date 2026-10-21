# Preparación del ensayo de T4′ sobre split8_j8_true (D4) — 2026-10-21

**Escrito antes de correr el ensayo.** Bajo el anexo E1 v1.1 congelado (2026-10-21 09:20). No modifica el anexo, ni el código congelado, ni el intento original de j8. Es la reevaluación retrospectiva autorizada en D4; **no reemplaza** la pausa original (`piloto/calibracion/REVISION_PENDIENTE_split8_j8_true.json`, paso 67, t = 0.07992408179528583), que se conserva junto con todas las auditorías. **No asigna Y** (piloto) y no cambia la compuerta del piloto por sí mismo.

## 1. Qué se corre
`anexo_implementacion/visita_completa_instrumentada_v11_t4p.py` (SHA-256 `b7352b23…ceee`) por su **camino normal**: primero `bg.calibrate` (v1.0, cota 0.09); si se pausa, recuperación T4′ (`t4prima.py`, `c58eb54b…3360`) con el driver `resumable_dop853_instrumentado_v11.py` (`e061617e…7cd`). Sin `--forzar-t4prima` (eso es solo para validación) y sin `--extra-budget`. Topes por defecto = anexo v1.1: 250 intentos, max(120 s, 0.04 s × n_rayos) por integración, 900 s de visita y 3600 s si entra a refinamiento. Carpeta de trabajo **nueva**; la del intento original (`D:\RIPG_DATA\T2_A\expediente\piloto_calibracion\split8_j8_true`) no se toca.

## 2. Predicciones declaradas (de datos ya existentes, solo lectura)
Fuente: traza por paso de `piloto/diagnostico_escape/escape_split8_j8_true.csv` (float64, nt = 2048, mismo DOP853 y tolerancias; contenedor). Coincide con la pausa original en el equipo del responsable (paso 67, dif. ≈ 2×10⁻¹¹).

| Paso | t | dt | contador de alarma | ¿revisión de área T4′? |
|---|---|---|---|---|
| 56 | 0.07894004938 | 1.92×10⁻⁴ | 0 | sí → A ≈ 0.0199 < 0.02, sigue |
| 60 | 0.07948321945 | 8.30×10⁻⁵ | 1 | sí → A ≈ 0.0202 ≥ 0.02, **para** |
| 64 | 0.07975379359 | 6.18×10⁻⁵ | 5 | (margen: segunda oportunidad) |
| 67 | 0.07992408177 | 5.50×10⁻⁵ | 8 | alarma → pausa de v1.0 |

1. La calibración v1.0 dentro de la visita **se vuelve a pausar** con `PAUSED_LOW_RADIAL_PROGRESS` en el paso 67 y el mismo t que la original (mismo equipo y versiones: se espera coincidencia exacta; tolerancia del lector 1×10⁻⁹).
2. T4′ se detiene en el **paso 60** (primer múltiplo de 4 con A ≥ 0.02), dos revisiones antes de que se cumpla la alarma. Detalle del driver que lo hace posible: la alarma se evalúa antes del commit de cada paso, pero dt < 10⁻⁴ empieza en el paso 60, de modo que en 60 y 64 el contador vale 1 y 5.
3. Radio nominal en **(0.07894005, 0.07948322]**; estimación gruesa del diagnóstico ≈ 0.07923. El escape (t* ≈ 0.0875, MPFR) queda ≈ 10 % más lejos.
4. Las auditorías integran hasta el radio nominal. En la traza de calibración el dt hasta ≈ 0.0794 es > 10⁻⁴, pero con 4096–16384 rayos o fase 0.5 los pasos pueden acortarse: **una pausa por alarma en las auditorías es posible** y sería operacional.
5. **No se predice la clasificación.** Es probable (no seguro) que la visita entre a refinamiento por la distorsión del sector 1816–1827; si entra, el tope de visita sube a 3600 s (T2).

## 3. Comando (PowerShell, equipo del responsable)
Antes de empezar (D7: el tope mide reloj de pared; la hibernación produce pausas falsas):
```powershell
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
```
Comprobación previa (hashes congelados y carpeta nueva libre):
```powershell
$imp = "D:\RIPG_DATA\T2_A\expediente\anexo_implementacion"
Get-FileHash "$imp\visita_completa_instrumentada_v11_t4p.py","$imp\t4prima.py","$imp\resumable_dop853_instrumentado_v11.py" -Algorithm SHA256 | Format-Table Hash, Path -AutoSize
Test-Path "D:\RIPG_DATA\T2_A\expediente\ensayo_t4p_j8_D4_2026-10-21"
```
Esperado: `B7352B23…CEEE`, `C58EB54B…3360`, `E061617E…B7CD` y `False`. Si algo no coincide, no correr.

Ensayo:
```powershell
& "D:\RIPG_DATA\T2_A\cribado_borde\venv_torch\Scripts\python.exe" -I "D:\RIPG_DATA\T2_A\expediente\anexo_implementacion\visita_completa_instrumentada_v11_t4p.py" --case split8_j8_true --work "D:\RIPG_DATA\T2_A\expediente\ensayo_t4p_j8_D4_2026-10-21" *>&1 | Tee-Object -FilePath "D:\RIPG_DATA\T2_A\expediente\ensayo_t4p_j8_D4_2026-10-21.log"
```
Duración esperada: ≈ 35 s la calibración v1.0 (pausa) + ≈ 35–60 s T4′; auditorías de 1–2 min si no hay refinamiento, hasta ≈ 15–60 min si lo hay. Si se interrumpe, se relanza el **mismo** comando sobre la misma carpeta (reanuda desde checkpoints; T4′ es determinista al reanudar), salvo que la pausa sea `PAUSED_TIME_CAP` por hibernación: entonces carpeta nueva (2.5).

Lectura (solo lectura, no integra):
```powershell
& "D:\RIPG_DATA\T2_A\cribado_borde\venv_torch\Scripts\python.exe" -I "<repo>\experiments\T2_A\claude\piloto\ensayo_t4p_j8\leer_ensayo_t4p_j8.py" --work "D:\RIPG_DATA\T2_A\expediente\ensayo_t4p_j8_D4_2026-10-21"
```
`leer_ensayo_t4p_j8.py` SHA-256 `bcd75ce14c8835736346351d8adab428701df0e5d6aeaf4c3b77b23b4f6b35da`.

## 4. Criterio de lectura (fijado antes de ver el resultado)
**A. Compuertas de integridad (el lector las imprime; todas deben dar OK antes de leer la geometría).**
0. Caso = `split8_j8_true`. 1. Topes v1.1 sin `--extra-budget`. 2. `sin_cubrir` vacío.
3. La calibración v1.0 se pausa en el paso 67 con `PAUSED_LOW_RADIAL_PROGRESS`, alarma 8 y t = 0.07992408179528583 (± 10⁻⁹); la visita registra `calibration_v10_pause` = `PAUSED_LOW_RADIAL_PROGRESS` y `calibration_mode` = `T4_PRIME_AREA_STOP`. Esto verifica a la vez la identidad del estado reentrenado y que el camino numérico es el original.
4. T4′ para en el paso 60, t_reached = 0.07948322 (± 10⁻⁹), radio en (t₅₆, t₆₀] y error relativo de área ≤ 10⁻⁶. `polygon_valid`/`polygon_simple` se **registran** sin criterio (igual que `bg.calibrate`).
- Si 3 falla: el estado o la plataforma difieren; no se lee nada más y se revisa.
- Si v1.0 **termina** sin pausa: contradice la traza; se registra como anomalía (el resultado tendría `calibration_mode` = V1.0) y no se interpreta hasta revisar.
- Si T4′ para en otro paso o el radio cae fuera del intervalo: contradice el diagnóstico de escape; anomalía, no se interpreta.

**B. Desenlaces.**
- `VISIT_EVALUATED` con compuertas OK: la clasificación es la del instrumento sin cambios (`topological_map.result`) y se registra como **reevaluación D4 de j8**, al lado de la pausa original, no en su lugar. Con `GEOMETRIC_NONINJECTIVITY` se exige además r_conj < radio nominal y se reportan A_embed, persistencia de fase y resolución mínima con evento. Con `INJECTIVE_AT_NOMINAL_RADIUS` vale la nota del instrumento (censura observacional, sin certificado global) y la advertencia de 2.1 del anexo: que A = 0.02 ocurra antes del escape no basta por sí solo; el respaldo son las auditorías completas. Métrica SPD y finita en todas las auditorías.
- No hay comparador v1.0 para j8 (v1.0 nunca produjo radio), así que el criterio D6 de coincidencia exacta **no aplica**; el contraste externo es el diagnóstico de escape (radio ≈ 0.0792 frente a t* ≈ 0.0875). Los campos sensibles al radio se reportan.
- `PAUSED_PENDING_REVIEW` en auditorías: pausa operacional (se lee `ultima_integracion_lanzada` y la razón). j8 sigue `PAUSED_PENDING_REVIEW`; no se usa presupuesto adicional sin decisión registrada.
- `PAUSED_PENDING_REVIEW` dentro de T4′ (antes del paso 60): contradice la predicción 2; se reporta.
- `ERROR_EJECUCION`: se reporta íntegro. Nota: `t4prima.AreaNotReached` no es `IntegrationPaused` y la visita lo registraría como error, no como pausa, a diferencia de lo que dice 2.1′; en j8 no puede ocurrir (la integración no llega a 0.09), pero queda anotado como discrepancia texto/código para una versión posterior.

**C. Qué no hace este ensayo.** No certifica T5 ni toca j5/j7. No altera el estado del piloto por sí mismo: cómo se registra j8 en `PILOTO_20_*.csv` lo decide el responsable con el resultado a la vista. No se repite ni se ajusta nada para obtener otro desenlace.
