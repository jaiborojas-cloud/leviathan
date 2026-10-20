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
