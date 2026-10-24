# DIN-borde D5 — resultado del descubrimiento (2026-10-24)

**Naturaleza:** descubrimiento exploratorio, según `PLAN_D5_descubrimiento.md` (commit `65e07d8`, registrado antes de correr). Datos: 780 trayectorias de 156 splits. Salidas:
- `d5/d5_trayectorias.csv`, SHA `ca56627f…24d1`;
- `d5/d5_resumen.json`, SHA `579f0102…c9a0`.

Los p-valores son bilaterales, con 5000 permutaciones, y descriptivos: no hay corrección por multiplicidad.

| candidato | W con log ρ(u250) | W_adj (más allá de ρ(u50)) | W_adj pares / impares | Spearman con ρ(u50) dentro del split |
|---|---|---|---|---|
| P0: log ρ(u50) (persistencia) | **0.766** (p 2·10⁻⁴) | — | — | 1 |
| (a) log(1 − p(y_k*)) en el 50 | 0.753 | 0.055 (p 0.16) | 0.026 / 0.085 | 0.79 |
| (b) min p(y) en entrenamiento, 50 | 0.003 | 0.038 | 0.054 / 0.023 | −0.03 |
| (b) mal clasificados en entrenamiento, 50 | — | — | — | — |
| (b) pérdida de entrenamiento, 50 | 0.004 | −0.016 | −0.009 / −0.023 | −0.01 |
| (c) precisión en validación, 5 | −0.144 (p 4·10⁻⁴) | −0.058 (p 0.15) | −0.076 / −0.041 | −0.11 |
| (d′) Δ log(1 − p_min,val), 5→50 | 0.601 | 0.031 | −0.013 / 0.076 | 0.74 |

**Notas:**
- **Mal clasificados en entrenamiento:** no tiene variación. En el update 50, 779 de 780 trayectorias tienen 0 errores en entrenamiento, así que el estadístico solo se define en 1 split.
- **Medidas de entrenamiento en general:** el conjunto de entrenamiento ya está memorizado en el update 50, y esas medidas no informan.
- **Persistencia:** la pendiente intra-split de log ρ(u250) sobre log ρ(u50) es 0.91.

## Aplicación del criterio registrado
**Ningún candidato pasa |W_adj| > 0.2.** El máximo es 0.058. Según el plan, **lo que se predice más allá de la persistencia es débil**: el destino de ρ_borde ya está casi decidido en el update 50, y ninguna medida del update 50 ni del 5 añade información relevante. DIN-C1 debe replantearse.

## Lectura
- Entre los updates 5 y 50, el modelo memoriza el conjunto de entrenamiento y M colapsa sobre el ejemplo de validación más difícil. Desde ahí, la cercanía al borde cambia poco: W = 0.77 y pendiente 0.91.
- **La ventana en la que se decide el destino está entre los updates 5 y 50.** X (update 5) llegaba demasiado pronto; cualquier medida del update 50 llega tarde, porque ya es casi el desenlace.
- La señal de la precisión en validación del update 5 (−0.14 en bruto) existe, pero es pequeña y no añade nada sobre ρ(u50).

## Opciones para DIN-C1 (las decide el responsable)
1. **Confirmar la persistencia** (H: W de ρ(u50) frente a ρ(u250) > 0 en la cohorte nueva), declarada como hipótesis de autocorrelación. Es fácil y poco informativa.
2. **D6, «¿cuándo se decide?»:** reconstruir estados intermedios (updates 10, 20, 30 y 40) de las trayectorias antiguas, reentrenando desde checkpoint_005 con el ejecutor v12, y ver en qué momento ρ_borde(t) o la confianza en el ejemplo difícil empiezan a predecir el update 250. Después, confirmar en la cohorte nueva un predictor en ese momento t*.
3. **Confirmar el mecanismo** (borde ⇔ k* resuelto, o colapso sobre el ejemplo menos confiado), después de que D2b separe lo algebraico de lo empírico.
