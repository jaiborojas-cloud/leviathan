# DIN-R1 etapa 2 — T2-A1 y DIN-borde con ρ_borde v2 (2026-10-25)

**Naturaleza:** reevaluación posterior y declarada, según `PLAN_R1_etapa2.md`, registrado antes de calcular. **Ningún veredicto congelado cambia.**
- **Cálculo:** `r1_etapa2.py` (`6e708096…`) en el equipo del responsable, con 12 procesos: **6240 de 6240 estados válidos**.
- **Tabla:** `etapa2/r1_etapa2.csv`, SHA `908bd9c0…aa71`.
- **Reanálisis:** en el contenedor, con salida en `r1_etapa2_reanalisis.json`. El análisis de T2-A1 se repitió con una copia de `analisis_T2A1.py` en la que solo cambian los hashes de las tablas de entrada.

## Instrumento: ρ_caras frente a ρ_vert frente a v1
| update | ρ_caras/ρ_vert: mínimo / mediana | gana una cara | ρ_vert/v1: mínimo / percentil 1 / mediana |
|---|---|---|---|
| 5 | 0.61 / **0.785** | 95 % | 0.58 / 0.64 / 1.000 |
| 10 | 0.62 / 0.909 | 69 % | — |
| 50 | 0.78 / 1.000 | 15 % | (50–250, conjunto) 1.000 / 1.000 / 1.000 |
| 250 | 0.81 / 1.000 | 13 % | |

- **Antes del colapso** (updates 5–10), ρ_caras es claramente menor que v1. **Después del colapso**, prácticamente igual.
- **En el update 5, v1 también perdió conos de vértice** en más del 1 % de los estados.

## Reanálisis (exploratorio)
1. **T2-A1** con Y_c y L5 de ρ_caras: **NOT_MET se mantiene.**
   - W = 0.018 (p = 0.33) y W_adj = −0.001 (p = 0.51). Los originales eran 0.019 y 0.011.
   - Δ = −0.051; G global = −0.021; Y_b: precisión 0.29 frente a una incidencia de 0.32.
2. **D6** (curva de «cuándo se decide», con ρ_caras):

   | t | 5 | 10 | 20 | 30 | 40 | 50 |
   |---|---|---|---|---|---|---|
   | W de log ρ_caras(t) frente a log ρ_caras(250) | 0.03 | 0.05 | 0.38 | **0.58** | 0.67 | 0.78 |
   | W_adj de la confianza sobre ρ_caras(t) | 0.11 | **0.22** | 0.10 | 0.02 | 0.01 | — |

   Coincide con la v1: t* = 30, y la señal del update 10 (0.22) se mantiene.
3. **D4:** Spearman entre log ρ_caras y log(1 − p(y_k*)): 0.996–0.998 global y 0.79–0.80 dentro del split, en los updates 50–250. Sin cambios.
4. **D1:** el piso log(ρ_caras/√tr M) sigue en 1/27. El mínimo es −3.29590 en los updates 50–250, con log(1/27) = −3.29584.
5. **Estimando de C1 en descubrimiento con ρ_caras:** D = 0.078 (p = 0.0005), igual que con v1.

## Lectura
**Todas las conclusiones de T2-A1, D1, D4, D6 y DIN-C1 se sostienen con el instrumento corregido.** El límite angular del v1 afecta sobre todo a los estados tempranos (updates 5–10), donde la geometría todavía no colapsó. Sus efectos sobre los análisis son pequeños porque los resultados dependen del orden (rangos) o de los estados ya colapsados.
