# DIN-C1 — pruebas del script de análisis y de la compuerta (2026-10-24)

## Compuerta de reproducción (`c1_cohorte.py` v1, `5feb0e0f…`)
Se corrió en el equipo del responsable, con salida en `D:\RIPG_DATA\DIN_C1\compuerta_v1b`. Resultado: **PASA**, 5 de 5 en el update 5 y 5 de 5 en el 50, con las tolerancias de `DIAG_compuerta_2026-10-24.md`. La corrida anterior con la v0 (exacta) se conserva como FALLA. Hubo además una corrida duplicada de la v0 por un error de copia de Claude, y también se conserva.

## Script de análisis (`analisis_C1.py`, borrador v0)
- **Reproducción del descubrimiento.** Con una tabla de los splits 12–167 armada a partir de d6 y d1, en modo descubrimiento y con 5000 permutaciones, da **W_adj = 0.218**, idéntico a D6. También coinciden la secundaria A (W = 0.580) y el W sin ajuste (0.225).
- **Robustez del ajuste (Q10 de D2b, sobre datos de descubrimiento).** Con un ajuste flexible, en rangos dentro del split y polinomio cúbico de L10, da **W_adj = 0.225**. El efecto descubierto **no** es un artefacto de la no linealidad entre Y y L10.
- **Calibración nula.** Con 200 X sintéticos independientes y 1000 permutaciones, la tasa de rechazo al 5 % es 0.035 y la mediana de p es 0.51.
- **Con efecto.** Con r = 0.15 (32 semillas, 500 permutaciones), W medio = 0.119 y potencia 0.97, coherente con `potencia_C1`.

## Compuerta con `c1_cohorte.py` v2 (`c357f33c…`, 2026-10-25 10:44)
Se corrió en el equipo del responsable, con salida en `D:\RIPG_DATA\DIN_C1\compuerta_v2`. Resultado: **PASA**, 5 de 5 en el update 5 y 5 de 5 en el 50, 0 errores. Esta vez tardó unos 0.4 min por trayectoria, frente a 0.1 min con la v1. La v2 no hace más cálculos en modo compuerta, así que la diferencia probablemente se debe a la carga del equipo. No se investigó.
