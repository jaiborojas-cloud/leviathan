# DIN-borde D5 — descubrimiento del predictor para DIN-C1 (plan, 2026-10-24)

**Naturaleza:** **descubrimiento exploratorio**. Se registra antes de correr. Usa los 780 de T2-A1 (splits 12–167), ya gastados para confirmar y legítimos para descubrir. El predictor que se elija aquí se confirma **solo** en la cohorte nueva de DIN-C1 (splits 168 en adelante). Lo pidió el responsable el 2026-10-24 a las 14:41 («córrelo de una»), sin esperar a D2/D2b. La congelación de DIN-C1 sigue esperando la teoría.

## Desenlace
Y = log ρ_borde(u250), de la tabla de la fase 2 de T2-A1.

## Candidatos (signo libre; descriptivo)
- **P0, persistencia (referencia):** log ρ_borde(u50).
- **(a)** log(1 − p(y_k*)) en el update 50, el ejemplo de validación de menor confianza (de d4).
- **(b)** log(1 − min p(y)) sobre el conjunto de **entrenamiento** en el update 50, más el número de ejemplos de entrenamiento mal clasificados y la pérdida de entrenamiento, también en el 50. No entran en M.
- **(c)** precisión en validación en el update 5 (de comparadores_ng_u5).
- **(d′)** log(1 − p_min,val) en el 50 menos el mismo valor en el 5. **Cambio respecto del borrador v0:** no hay estados del update 25 para estas trayectorias, así que la velocidad de 25→50 se sustituye por 5→50.

## Estadísticos (por candidato)
- **W:** media de la Spearman dentro del split con Y.
- **W_adj:** lo mismo con los residuos de Y ~ split + log ρ_borde(u50).
- p de permutación dentro del split (5000 permutaciones, semilla 230001 + índice). Son **descriptivos**: con 8 candidatos no hay corrección y nada se confirma aquí.
- Spearman global con Y.
- **Estabilidad:** el mismo W calculado por separado en splits pares e impares.

## Criterio para proponer el predictor de DIN-C1
Se propone al responsable el candidato con el |W_adj| más alto que tenga el mismo signo en las dos mitades. Si ninguno pasa |W_adj| > 0.2, se informa que el «más allá de la persistencia» es débil. En ese caso, DIN-C1 se replantea, por ejemplo con la persistencia misma como hipótesis, declarada como tal.
