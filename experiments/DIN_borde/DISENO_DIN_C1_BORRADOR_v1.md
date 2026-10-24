# DIN-C1 — confirmatorio: ¿la incertidumbre temprana anticipa el acercamiento al borde? BORRADOR v1 (2026-10-24)

**Estado:** borrador. **No congelado.** Sustituye al v0, que se conserva. La primaria y la secundaria las decidió el responsable el 2026-10-24 a las 15:54 («Está bien, adelante»). Según la decisión de las 14:33, la congelación espera a que D2b, la parte teórica del otro agente, separe lo algebraico de lo empírico. La cohorte nueva **no se entrena** hasta congelar.

## 1. Pregunta
En la familia WineMLP con panel de validación de 27 ejemplos, ¿la incertidumbre del modelo sobre su ejemplo de validación más difícil en el update 10 anticipa, dentro del split, qué tan cerca del borde perspectival termina la geometría en el update 250, **más allá** de la distancia al borde que ya hay en el update 10?

## 2. Antecedentes de descubrimiento (exploratorios; splits 12–167)
- **D3 y D4:** después del update 50, M colapsa sobre el ejemplo de validación de menor confianza, y ρ_borde sigue la incertidumbre de ese ejemplo.
- **D5:** desde el update 50, nada predice más allá de la persistencia.
- **D6:**
  - el destino se decide entre los updates 10 y 30 (t* = 30);
  - **en el update 10, log(1 − p_min,val) da W_adj = 0.218 sobre ρ(10) (p ≈ 2·10⁻⁴)**;
  - ρ(10) no predice por sí solo (W = 0.04);
  - M todavía no ha colapsado (M_kk,max/tr = 0.14).
- **Sesgo de selección:** la primaria se eligió entre 6 updates × 3 medidas (más los candidatos de D5). Es de esperar que 0.22 esté inflado; la potencia se evalúa para efectos menores.

## 3. Cohorte confirmatoria (nueva)
- **Splits:** 168 a 167 + S, sin uso previo en el repositorio. T2-A0 usó 8–167 y el descubrimiento de T1, 0–7.
- **5 inicializaciones por split**, con la regla de semillas de T2-A0 extendida:
  - j = 5 + 5(s − 8) + k, con k = 0..4;
  - semilla de inicialización 2000 + j;
  - semilla de lotes 4000 + 10s + j;
  - partición de datos `core.load_split(s)` (random_state 1000 + s).
- **Entrenamiento:** de cero, con `training.new_session` y `training.updates`, sin cambios de mecánica (Adam con lr 0.006, lote 64), de forma continua hasta el update 250.
- **Estados guardados (M, f):** en los updates 5, 10, 30 y 250, con `core.make_geom_state` y `core.subset_M([0, 1, 2])`.
- **Compuerta de reproducción:** con splits antiguos, el mismo código debe reproducir byte a byte checkpoint_005 de T2-A0 y el estado del update 50 de la fase 2 de T2-A1. Se prueba con 5 trayectorias antiguas **antes** de entrenar la cohorte nueva.
- **Tamaño S:** se fija con la potencia de la sección 6. Propuesta: **S = 156** (780 trayectorias), igual que T2-A1.

## 4. Medidas
- **ρ_borde:** `rho_borde.py` congelado (`d8ec69f8…416b`), en los updates 10, 30 y 250.
- **X (predictor primario):** X = log(1 − min_n p(y_n | x_n)) sobre los 27 ejemplos del panel de validación, en el update 10, con el modelo en eval y softmax de las 3 clases.
- **Y (desenlace):** Y = log ρ_borde(250).
- **Ajuste:** L10 = log ρ_borde(10).

## 5. Análisis
- **Primaria B:** W_adj = media sobre splits de la Spearman dentro del split entre X y e, donde e son los residuos de Y ~ ordenada por split + β·L10 (MCO dentro del split).
  - **Hipótesis:** H1 es W_adj > 0. Sentido: más incertidumbre en el update 10 lleva a más distancia al borde después.
  - **Permutación** de residuos dentro del split (Freedman–Lane, sin reestimar β), 20 000 permutaciones, semilla por fijar en la congelación.
  - **Éxito:** p < 0.05, unilateral.
- **Secundaria A** (no decide): W de log ρ_borde(30) frente a Y, unilateral, H1: W > 0.
- **Descriptivos:**
  - W de X sin ajuste;
  - W_adj con ajuste adicional por log ρ_borde(5);
  - precisión en validación en el update 10;
  - k*(250) = argmin p(y) y concentración de M (réplica de D3 y D4);
  - cota de cuerda (auditoría Q5).
- **Empates en X** (p_min puede saturar en 1): por (X, init) ascendente. Los empates en e van a rangos promedio.
- **INCONCLUSIVE:**
  - menos del 80 % de los splits válidos;
  - más del 5 % de trayectorias sin X, sin Y o sin L10;
  - o que falle la compuerta de reproducción.
  Los umbrales se terminan de fijar en la congelación.
- **Veredictos:** PASS, NOT_MET o INCONCLUSIVE. Hay un solo análisis, y el script se congela y se prueba con X sintético antes de entrenar.

## 6. Potencia
`C1/potencia_C1.py`: el residuo e es el real del descubrimiento, la cohorte se simula remuestreando splits completos y X se construye sintético con el efecto r. Los resultados están en `C1/potencia_C1.json` (sección 6.1).

### 6.1 Resultados
1000 réplicas por celda; umbral nulo con 2000 réplicas. El efecto se mide como el W_adj esperado.

| splits S | umbral nulo de W al 5 % | W ≈ 0.10 | W ≈ 0.12 | W ≈ 0.15 | W ≈ 0.19 |
|---|---|---|---|---|---|
| 100 | 0.080 | 0.63 | 0.81 | 0.93 | 0.99 |
| **156** | **0.069** | **0.78** | **0.92** | **0.98** | **1.00** |
| 200 | (pendiente) | | | | |

**Propuesta: S = 156.** Con S = 156, la potencia es ≥ 0.9 para un efecto real de la mitad del descubierto (≈ 0.12) y ≈ 0.78 para 0.10. El coste estimado es de unos 40–60 min en la PC: 780 trayectorias y 3 ρ_borde por trayectoria.

## 7. Qué no se afirma
- Esto es una réplica dentro de la familia (mismo conjunto de datos, nuevos splits e inicializaciones), no una generalización a otras redes, paneles o datos.
- Un PASS diría que **en esta familia** la incertidumbre temprana sobre el ejemplo difícil anticipa el borde más allá de la geometría del update 10. No diría nada sobre su causalidad.
- Parte de la relación entre ρ_borde y la confianza es algebraica (D2b). Por eso la primaria se mide en el update 10, antes del colapso, y está ajustada por ρ(10).

## 8. Pendiente antes de congelar
1. El resultado de D2b, para revisar si X en el update 10 es tautológico respecto de M(10).
2. La potencia (sección 6.1) y la elección de S.
3. Las semillas de permutación, los umbrales INCONCLUSIVE y los scripts: entrenamiento de la cohorte con su compuerta, y análisis probado con X sintético.
