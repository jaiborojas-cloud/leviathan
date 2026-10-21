# Resultado del ensayo de T4′ sobre split8_j8_true (D4) — 2026-10-21

Corrido por el responsable en su equipo (Windows 11, Python 3.12.10, numpy 2.3.5, scipy 1.18.1, 24 CPU) el 2026-10-21, según `PREPARACION_ensayo_t4p_j8_2026-10-21.md`, que se escribió antes de correr y **no se modifica**. Carpeta de trabajo: `D:\RIPG_DATA\T2_A\expediente\ensayo_t4p_j8_D4_2026-10-21`. Los datos de abajo se transcriben de `VISITA_COMPLETA.json`, `states/split8_j8_true/nominal.json`, `states/split8_j8_true/result.json` y del último checkpoint de `ode_checkpoints/rays/5078069ed6986d8dee87`, pegados por el responsable. El lector `leer_ensayo_t4p_j8.py` no se ejecutó: el comando de la nota llevaba un marcador `<repo>` sin sustituir y el script no estaba en el equipo. Las compuertas se comprobaron a mano con los mismos criterios.

**Es la reevaluación retrospectiva de D4. No reemplaza la pausa original** (`../calibracion/REVISION_PENDIENTE_split8_j8_true.json`), que se conserva. **No asigna Y.** Cómo se registra j8 en `PILOTO_20_*.csv` lo decide el responsable.

## 1. Compuertas de integridad
| # | Criterio (declarado antes) | Observado | |
|---|---|---|---|
| 0 | caso `split8_j8_true` | `split8_j8_true` | OK |
| 1 | topes v1.1 sin `--extra-budget` | 250 / 120 s / 900 s / 3600 s; `extra_budget` falso | OK |
| 2 | `sin_cubrir` vacío | vacío | OK |
| 3 | pausa v1.0: paso 67, `PAUSED_LOW_RADIAL_PROGRESS`, alarma 8, t = 0.07992408179528583 ± 10⁻⁹ | paso 67, misma razón, alarma 8, 88 intentos / 21 rechazos (idénticos al original), t = 0.07992408182102524 (dif. 2.57×10⁻¹¹) | OK (ver §3) |
| 3b | `calibration_v10_pause` / `calibration_mode` | `PAUSED_LOW_RADIAL_PROGRESS` / `T4_PRIME_AREA_STOP` | OK |
| 4a | T4′ para en el paso 60, t_reached = 0.07948321945 ± 10⁻⁹ | paso 60, t_reached = 0.0794832195210516 (dif. 7.6×10⁻¹¹); A(t_reached) = 0.02019008 | OK |
| 4b | radio en (0.07894004938, 0.07948321945] | 0.079127336616792 | OK |
| 4c | \|error rel. de área\| ≤ 10⁻⁶ | 5.8×10⁻¹⁵ | OK |
| — | polígono (registro, sin criterio) | válido y simple | — |
| 5a | sin errores | `errors` vacío; sin `errors_en_result` | OK |
| 5b | sin pausas fuera de la calibración v1.0 | solo `rays/5078069e…` (t_span [0, 0.09], la pausa v1.0) | OK |
| 5d | métrica SPD y finita | `metric_nonpositive` 0, `metric_nonfinite` 0, autovalor mínimo 7.58×10⁻⁸ | OK |

## 2. Resultado del instrumento (sin cambios, `topological_map.result`)
- `VISIT_EVALUATED`, **`INJECTIVE_AT_NOMINAL_RADIUS`**, nivel 1. No entró a refinamiento (`entro_a_refinamiento` = null), es decir, `candidate` resultó falso.
- Radio nominal 0.079127336616792; A_embed 0.020000000000000115 (censurada, ratio 1.0000000000000058).
- Sin autointersección (`self_intersections` 0), sin conjugado (`r_conj` null, sin cambio de signo del determinante), resolución máxima del borde 1024.
- `max_Dexp_condition` 2.8953; mínimo de det Dexp (con signo y en valor absoluto) 0.36177.
- 10 integraciones, 754 intentos, 172 rechazos; 268 s de pared en la sesión (auditorías ≈ 94 s).
- Nota del instrumento: *«No sampled loss up to nominal radius; observational right-censoring, no global injectivity certificate.»*

## 3. Corrección a la nota de preparación (compuerta 3)
La nota decía «se espera coincidencia exacta» del t de la pausa v1.0 en el mismo equipo. **No fue exacta:** difiere en 2.57×10⁻¹¹, dentro de la tolerancia declarada (10⁻⁹). Paso, intentos, rechazos, alarma y razón sí coinciden exactamente.
- **Explicación probable (no verificada byte a byte):** la calibración original del piloto (`calibrar_piloto.py`) usó el estado regenerado de `estados_u25` (`state_025_regen_split8_j8_true.npz`, SHA-256 f70d88b3…). La visita reentrena desde `checkpoint_005.pt` y escribe su propio `state.npz` (SHA-256 817a4620…). Esos estados no son el mismo archivo: `regeneracion_u25.csv` registra para j8 `max_dM_vs_state005` = 2.45×10⁻¹¹, del mismo orden que la diferencia en t. Lo mismo pasa en j6 (regenerado 0e3fbfd3…, visita 97130aeb…).
- **Consecuencia:** la compuerta 3 verifica la identidad del estado **hasta el error de reconstrucción ya documentado**, no bit a bit. En una versión posterior de la nota, la frase debería decir «coincidencia de contadores; t dentro de 10⁻⁹».

## 4. Contexto y alcance (descriptivo)
- El radio nominal (0.07913) cae antes de que empiece el escape (t* ≈ 0.0875, MPFR; `../diagnostico_escape/`): ≈ 10 % de margen. Coincide con la estimación gruesa del diagnóstico (A = 0.02 en t ≈ 0.0792).
- Según 2.1 del anexo, que A = 0.02 se alcance antes del escape no basta para afirmar que el disco está embebido. El respaldo son las auditorías completas, que aquí no detectaron pérdida de inyectividad en lo muestreado (borde hasta 1024 rayos, Jacobi, ambas fases), sin certificado global.
- El autovalor mínimo de la métrica (7.6×10⁻⁸) es positivo y es el menor de las visitas revisadas (j6 5.6×10⁻⁴, j17 3.3×10⁻⁵, j9 9.3×10⁻⁶). Se registra sin criterio: el instrumento solo exige positividad y finitud.
- No hay comparador v1.0 para j8 (v1.0 nunca produjo radio), así que el criterio D6 no aplica.
- No certifica T5 ni dice nada sobre j5 y j7, que siguen `PAUSED_PENDING_REVIEW`.
- Una sola corrida, en un equipo. No se repitió ni se ajustó nada.

## 5. Pendiente (decisión del responsable)
1. Si y cómo se anota la reevaluación de j8 en `PILOTO_20_estado_*.csv` y `PILOTO_20_visitas_update25.csv`, junto a la pausa original. Si se cuenta: 18 de 20 con diagnóstico (16 `INJECTIVE_AT_NOMINAL_RADIUS`, 2 `GEOMETRIC_NONINJECTIVITY`) y 2 `PAUSED_PENDING_REVIEW` (j5, j7).
2. Copiar al repositorio los JSON pequeños de la corrida (sin checkpoints), como en `../validacion_v11_t4p/`.
