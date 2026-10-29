# DIN-E-escala — resultado exploratorio (2026-10-28)

**Lectura según la regla del plan:** **NO_SE_SEPARAN_CON_ESTOS_DATOS.** Los dos análisis apuntan en direcciones **opuestas**, y eso es informativo.

## Procedencia
- **Plan:** `PLAN_E_escala_v1.md`, registrado antes de calcular (commit `38d30519`).
- **Extracción de la escala:** `extraer_escala.py` (`32f29770…`), en el equipo del responsable.
  - Q13-DR: 6000 de 6000 trayectorias, 0 errores (`98c43f61…`).
  - Q13-M2: 17 600 de 17 600, 0 errores (`ffef9e74…`).
- **Análisis:** `analisis_E_escala.py`. Resultado en `resultado/RESULTADO_E_escala.json`.
  - D y c por nivel salen de los JSON congelados de Q13-DR y Q13-M2.
  - E2 usa las tablas de cohorte.
- **Naturaleza:** exploratorio, sobre cohortes ya usadas para confirmar.

## E1: entre niveles (17 niveles manipulados)
| nivel | familia | c250 | S (escala de logits) | m (margen) | p (confianza) | D |
|---|---|---|---|---|---|---|
| DR L0 | A0 | 0.869 | 5.74 | 8.75 | 0.968 | 0.0343 |
| DR L1–L5 | LS | 0.694 → 0.399 | 3.44 → 1.68 | 5.39 → 2.65 | 0.945 → 0.857 | 0.011 → −0.001 |
| M2 A0 | A0 | 0.885 | 5.71 | 8.66 | 0.968 | 0.0248 |
| M2 LP1–LP5 | LP | 0.721 → 0.387 | 3.41 → 1.59 | 5.43 → 2.54 | 0.948 → 0.846 | 0.0089 → −0.0006 |
| M2 WD1–WD5 | WD | 0.670 → 0.440 | 3.30 → 1.98 | 5.32 → 3.34 | 0.945 → 0.896 | 0.0096 → −0.0007 |

- **Spearman:**
  - D con c: 0.958;
  - D con S: 0.966;
  - **c con S: 0.973.** Entre niveles, c y S son casi colineales.
- **Parciales:**
  - D con c dado S: 0.31;
  - **D con S dado c: 0.50.** La diferencia es −0.19, apenas dentro del umbral de ±0.2.
- **MCO estandarizado:** el coeficiente de S es 0.012 y el de c −0.003.
- **Diagnóstico de familias:** a igual c, **WD conserva logits más grandes** que LS/LP, y también más D:
  - con c ≈ 0.51: WD4 tiene S = 2.30 y D = 0.0035, frente a LP4 con S = 2.08 y D = 0.0006;
  - con c ≈ 0.56: WD3 tiene S = 2.58 y D = 0.0055, frente a DR L3 con S = 2.45 y D = 0.0013.

  **Entre manipulaciones, S sigue a D algo mejor que c.**

## E2: dentro de los controles sin manipular (variación natural)
- **Qué cambia aquí:** c y S apenas se correlacionan entre trayectorias (Spearman 0.15 en DR L0 y 0.16 en M2 A0). Es una **disociación natural**.

| control | gradiente de D por cuartiles de c (Q4 − Q1) | gradiente de D por cuartiles de S (Q4 − Q1) |
|---|---|---|
| DR L0 (1000 trayectorias) | **+0.151** (de −0.023 a 0.128) | −0.017, no monótono |
| M2 A0 (1600 trayectorias) | **+0.080** (de −0.011 a 0.069) | +0.034, no monótono |

**Dentro de los controles, c sigue a D mucho mejor que S**, en las dos cohortes.

## Lectura
1. **Los dos análisis discrepan,** y por eso la regla da NO_SE_SEPARAN:
   - **entre manipulaciones** (E1), la escala de los logits explica D un poco mejor, sobre todo porque WD mantiene logits grandes y algo de señal a igual c;
   - **dentro de los controles** (E2), donde c y S varían casi por separado, es la concentración c la que ordena D, con un gradiente fuerte y repetido en dos cohortes.
2. **Interpretación tentativa (hipótesis, no resultado):** pueden actuar las dos cosas. La concentración de M parece ser la que importa trayectoria por trayectoria, y la escala de los logits podría añadir un efecto a nivel de intervención. Una alternativa es que E1 refleje solo que WD alcanza menos rango de c.
3. **Cautelas:**
   - **E2 condiciona en c250 y S250,** medidas en el mismo momento que el desenlace Y = log ρ250. En particular c está ligada mecánicamente a ρ250 bajo concentración (D2b). Por eso E2 puede contener relaciones algebraicas y no debe leerse como causal.
   - **Muestras chicas:** los cuartiles usan entre 70 y 320 trayectorias, con menos splits.
   - **E1 tiene 17 puntos casi colineales.**

## Siguiente paso posible (para decidir)
Un **confirmatorio con datos nuevos** que aproveche la disociación natural de E2, sin manipular. En una cohorte control nueva, estimar la modulación de D por c **condicionando en S** con una regla registrada; y, si fuera posible, con una medida de c tomada **antes** del update 250, para evitar el vínculo algebraico con Y.

Otra opción es un manipulador que mueva S sin mover c, por ejemplo escalar la temperatura de los logits, aunque eso también cambia M. Necesita más diseño.
