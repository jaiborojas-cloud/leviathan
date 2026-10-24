# DIN-C1 — confirmatorio del mecanismo de acercamiento al borde, BORRADOR v0 (2026-10-24)

**Estado:** borrador. **No congelado.** Por decisión del responsable (2026-10-24 14:33), no se congela antes de tener la fase teórica (D2 y D2b). La cohorte nueva **no se entrena** hasta congelar este diseño.

## 1. Decisiones del responsable (14:33)
1. **Primaria predictiva:** algo medido temprano debe predecir, dentro del split, la cercanía posterior al borde.
2. **Cohorte:** misma familia (WineMLP, panel de validación de 27), con **splits nuevos** y semillas nuevas.
3. **Esperar la teoría antes de congelar.**

## 2. Antecedentes (exploratorios: DIN-borde D1, D3 y D4, sobre los 780 de T2-A1)
- Tras el update 50, M colapsa sobre **un** ejemplo de validación, k*, que es el de menor confianza.
- ρ_borde sigue la incertidumbre de k*: Spearman con log(1 − p(y_k*)) de 0.998 en total y 0.80 dentro del split.
- Con k* bien clasificado, 55 % de los estados queda por debajo de r*. Con k* mal clasificado, ninguno.

## 3. Problema de diseño central (lo resuelve la fase teórica)
- **Parte de la relación es álgebra.** M se construye con los gradientes de log p(y), proporcionales a (1 − p(y)). Que ρ_borde siga a (1 − p_min) en el mismo update está forzado en parte por la definición. **No se confirma una identidad.**
- **Riesgo de tautología predictiva (la lección de T1-B y T2-A1).** Si el predictor temprano es la confianza en k* en el update 50, y ρ_borde(u50) es casi una función de ella, predecir ρ_borde(u250) equivale a «ρ_borde persiste». Para que sea informativo, el predictor tiene que **aportar más allá de ρ_borde(u50)**, o venir de una cantidad que no entre en M.
- **Candidatos a predictor**, a evaluar en una fase de descubrimiento con los datos antiguos (sección 4):
  - (a) p(y_k*) en el update 50, con ajuste por ρ_borde(u50);
  - (b) confianza o margen del ejemplo de **entrenamiento** más difícil en el update 50, que no está en el panel ni en M;
  - (c) precisión en validación en el update 5 (la señal exploratoria del cierre de T2-A1);
  - (d) la velocidad de cambio de la confianza en k* entre los updates 25 y 50.

## 4. Fases propuestas
| fase | qué | datos |
|---|---|---|
| **T** | D2 (piso 1/n) y **D2b**: qué parte de ρ_borde ~ (1 − p_min) es identidad algebraica y qué parte es empírica | sintéticos (otro agente) |
| **D5 descubrimiento** | elegir el predictor y su forma con los 780 de T2-A1, que ya están gastados para confirmar y son legítimos para descubrir | antiguos |
| **0 congelación** | predictor, desenlace (log ρ_borde(u250); secundario Y_b con r*), estadístico W dentro del split (y su versión ajustada, si aplica), potencia simulada con los datos de descubrimiento, tamaño de cohorte y umbrales INCONCLUSIVE | — |
| **1 cohorte nueva** | splits **168 en adelante** (no aparecen en el repositorio; T2-A0 usó 8–167 y el descubrimiento de T1, 0–7), 5 inicializaciones por split, con la misma regla de semillas: init j = 5 + 5(s − 8) + k, semilla de init 2000 + j, semilla de lote 4000 + 10s + j. Entrenamiento hasta el update 250 | nuevos |
| **2 análisis único** | según lo congelado | nuevos |

**Coste estimado de la fase 1:** unos 17 s por visita (entrenamiento más ρ_borde). Con 100 splits (500 trayectorias) y unas 3 visitas por trayectoria son ≈ 1500 visitas, del orden de 30–60 min con 12 procesos.

## 5. Pendiente
- El resultado de D2 y D2b.
- D5, cuyo plan se registra antes de correrlo.
- Decidir si la primaria va ajustada por ρ_borde(u50).
