# Resultados operativos del piloto de 20 visitas, update 25 (2026-10-19, ≈23:30)

**Naturaleza:** piloto operativo. Estos son diagnósticos geométricos de visitas de update 25; **no asignan Y**, **no estiman frecuencias** (4 splits; dentro de un split `f` es común) y **no establecen el veredicto predictivo** de T2-A0. El predictor X no se ha mirado en relación con estos resultados.

| Estado | Visitas |
|---|---|
| Visita completa evaluada, `INJECTIVE_AT_NOMINAL_RADIUS` | 15: split8_j6; split9_j10–j14; split10_j15, j16, j18, j19; split11_j20–j24 |
| Visita completa evaluada, `GEOMETRIC_NONINJECTIVITY` | 1: **split10_j17_true** |
| `PAUSED_PENDING_REVIEW` (mantener pausadas, decisión 2026-10-19 22:40) | 3: split8_j5, j7, j8 |
| Calibración completa tras reanudar con presupuesto adicional; visita completa por correr | 1: split8_j9 |

Compuerta operacional provisional (más de 5 de 20 sin resolver, o 5 de 5 de un split): hoy 3 de 20 sin resolver y 3 de 5 en split 8 (j9 pendiente de visita completa) → **no se dispara**.

## split10_j17_true (primer positivo del piloto)
- Clasificación del instrumento: `GEOMETRIC_NONINJECTIVITY`; nivel de refinamiento 2; resolución máxima 8192 rayos. Estable: primera autointersección 0.0643969 (512 a 8192 rayos, ambas fases) y punto conjugado de Jacobi r_conj = 0.0643969001 (dispersión ≈ 5×10⁻¹⁶); cambio de signo del determinante (mínimo con signo −0.6035; mínimo en valor absoluto 1.37×10⁻⁵; condición intrínseca máxima 7.3×10⁴).
- Radio nominal 0.0859956 (el disco nominal está plegado: `polygon_valid` y `polygon_simple` falsos). A_embed (área en r_conj) = 0.0119397 (ratio 0.597 de 0.02; diferencia relativa 32/64 de 6×10⁻¹¹). El instrumento advierte: «A_embed estimate does not exclude an earlier cut locus»; `cut_locus_probable` = false.
- No se redujo A = 0.02 para rescatar el caso.
- Instrumentación: 65 integraciones, 3341 intentos (547 rechazos), alarma 0, `sin_cubrir` vacío, 0 pausas. Tiempo de integraciones 563 s de un tope de visita de 900 s (63 %); la integración más larga (rayos, 8192, ≈ 99 s) usó ≈ 83 % del tope por integración de 120 s; sesión total 895 s.

## Observaciones operativas (sin cambiar el anexo congelado)
1. Una visita con candidato a evento consume ≈ 10 veces más cómputo que una sana (3341 frente a 187–653 intentos; 563 s frente a 60–145 s). Los topes del anexo (calibrados con visitas sanas) quedaron holgados en las sanas y ajustados en esta: una visita candidata con 16384 rayos pausaría por el tope de tiempo por integración. Es un dato para una eventual revisión versionada del anexo, no un cambio.
2. Dentro de split 10, j15, j16, j18 y j19 son inyectivas y j17 no: el evento depende de la inicialización además del split.
3. La alarma de progreso no disparó en ninguna de las 16 visitas completas; sí disparó en las 4 visitas de split 8 durante la calibración. En j9 disparó y la calibración terminó al reanudar.
4. Pendiente: visita completa de split8_j9 (con `--extra-budget`, decisión registrada) y revisión de si j5, j7, j8 se reanudan o se cierran.

Archivos: `visitas_piloto.csv/.log`, `result_split10_j17_true.json`, `VISITA_COMPLETA_split10_j17_true.json`, `../PILOTO_20_estado_2026-10-19.csv`.

## Actualización 2026-10-20 ≈08:26: split8_j9_true
Tras corregir el driver (incidencia `INCIDENCIA_driver_split8_j9_2026-10-20.md`) la visita completa de j9, con presupuesto adicional, terminó: **`GEOMETRIC_NONINJECTIVITY`**, nivel de refinamiento 2, resolución máxima 8192; primera autointersección 0.07742001 y punto conjugado r_conj = 0.07741996 (< radio nominal 0.08010249), cambio de signo del determinante (mínimo con signo −0.0850; condición intrínseca máxima 2.3×10⁴), persistente en fases; A_embed = 0.018703 (ratio 0.935; diferencia relativa 32/64 de 4.4×10⁻¹¹); `cut_locus_probable` falso, con la misma advertencia del instrumento (no excluye un cut locus anterior). 67 integraciones, 2696 intentos, 0 pausas, `sin_cubrir` vacío. El resultado anterior `INCONCLUSIVE` era un artefacto del error del driver y se descartó (archivos en `descartado_por_error_driver_2026-10-20`).

**Estado del piloto:** 17 de 20 visitas con diagnóstico geométrico de update 25 (15 `INJECTIVE_AT_NOMINAL_RADIUS`, 2 `GEOMETRIC_NONINJECTIVITY`: split10_j17 y split8_j9); 3 `PAUSED_PENDING_REVIEW` (split8_j5, j7, j8). Compuerta provisional: 3 de 20 sin resolver, 3 de 5 en split 8 → no se dispara. Sigue sin asignarse Y y sin veredicto predictivo.

Observaciones (descriptivas, no concluyentes): (1) split 8 reúne 4 de las 5 inicializaciones con geometría problemática (j5, j7, j8 pausadas cerca de r ≈ 0.074–0.087; j9 con conjugado en 0.0774) y solo j6 sana; split 10 tiene 1 de 5 (j17). (2) A_embed de j9 (0.0187) es casi igual al área del prefijo que se midió en el borde local de j5 en el replay MPFR (≈ 0.018714): hipótesis, sin probar, de que lo observado en j5 sea también una pérdida de inyectividad/conjugado y no una salida del dominio. Es lo que el diagnóstico MPFR de j7 y j8 y una eventual repetición con j5 pueden distinguir; hasta entonces no se reinterpreta la pausa de j5. (3) En j9 la alarma de progreso disparó a r = 0.0892, más allá del radio conjugado; en j17 no disparó: la alarma no equivale a «hay evento».

**Nota 2026-10-20 ≈11:50:** la observación (2) de arriba (hipótesis «¿pérdida de inyectividad o salida del dominio?» para j5) quedó **superada** por `../diagnostico_escape/RESULTADO_escape_rayos_2026-10-20.md`: en j5, j7 y j8 un sector de rayos sale de la carta a distancia intrínseca finita (reproducido en MPFR); en j9, en cambio, hay un punto conjugado (determinante con cambio de signo, |p| acotado). La coincidencia numérica de áreas (0.0187) entre j9 y el prefijo de j5 es **casual** y no se usa como evidencia.
