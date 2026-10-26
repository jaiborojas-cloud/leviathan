# DIN-Q13 — ¿el colapso de M es necesario para la señal temprana? BORRADOR v2 (2026-10-26)

**Estado:** borrador. **No** está congelado. Lo pidió el responsable a las 14:47 («si por favor»), después de que la calibración v1 terminara en INCONCLUSIVE_MANIPULACION (PR #97).

**Qué es:** un protocolo nuevo y prospectivo. **No** reescribe la v1, que queda congelada con su resultado: INCONCLUSIVE_MANIPULACION, ninguna dosis elegible y sin cohorte.

## 1. Qué se vio en la v1 y qué no
- **Lo único observado:** la calibración v1 midió **solo** c250, q250 y la precisión del panel.
  - Ningún X, ρ, D ni asociación existe para ninguna dosis.
  - Elegir una rejilla nueva a partir de esa calibración no usa información sobre la señal, que es el desenlace de Q13. Por eso la v2 sigue siendo un diseño anterior a los datos que importan.
- **LS se pasó:** ε = 0.02 ya baja la mediana de c250 a 0.42 (A0: 0.81).
- **WD se quedó corto:** λ = 0.1 solo llega a 0.73.
- **La precisión del panel aguantó:** 0.89 en LS y 0.93 en WD, frente a 0.93 en A0.

## 2. Cambios respecto de la v1 (todo lo demás, idéntico y por referencia a `DISENO_DIN_Q13_v1_CONGELADO.md`, sha `81d8ad9e…`)
| | v1 | v2 |
|---|---|---|
| rejilla LS (ε) | {0.02, 0.05, 0.1, 0.2} | **{0.001, 0.002, 0.005, 0.01}** |
| rejilla WD (λ, AdamW) | {1e-3, 1e-2, 5e-2, 1e-1} | **{0.2, 0.5, 1.0, 2.0}** |
| semillas de calibración | split 701000+s, init 702000+5s+k, lote 703000+5s+k | **split 741000+s, init 742000+5s+k, lote 743000+5s+k** (nuevas) |
| A0 en la calibración | se mide | se mide igual. Es solo referencia para la precisión; no hay compuerta en el piloto |

**Lo que no cambia:**
- El rango objetivo de c250 es [0.55, 0.70].
- La regla de dosis: la más pequeña dentro del rango, con una diferencia de precisión del panel frente a A0 menor que 0.05.
- El descarte de un brazo cuando ninguna dosis cumple.
- La parada si caen los dos brazos.
- La cohorte, sus semillas (711000, 721000, 731000; **sin usar**), la potencia y su rejilla de N.
- `analisis_Q13.py` (`9998a1b2…`), que no se toca. Las dosis le llegan por `q13_plan.json`.
- Las compuertas y las reglas de veredicto.

## 3. Riesgos declarados antes de los datos
1. **A0 en el límite del régimen:**
   - En el piloto v1, la mediana de c250 de A0 fue 0.808, muy cerca del 0.8 que exige la compuerta de manipulación. En G3 fue 0.864 y en C2 0.858.
   - La compuerta **no se cambia**, porque es la definición de colapso operacional de G3 y C2 y se aplica sobre la cohorte grande.
   - Si la cohorte da una mediana de c250 menor que 0.8 en A0, el resultado será INCONCLUSIVE_MANIPULACION y se reportará así. No se rescata.
2. **WD fuerte:** con λ = 2 y lr = 0.006, AdamW encoge los pesos unas 0.988 veces por paso. Puede arruinar el ajuste. La regla de precisión del panel lo filtra, y la dosis elegida es siempre la más pequeña que cumple.
3. **LS fino:** si incluso ε = 0.001 baja c250 por debajo de 0.55, LS queda descartado. Significaría que el *label smoothing* cambia de régimen de forma abrupta, sin una zona intermedia.
4. **Si la v2 tampoco logra la manipulación:** Q13 se cierra como «manipulación no lograda con dos rejillas» y la pregunta queda abierta. No habrá una v3 sin replantear los manipuladores.

## 4. Reparto (sin cambios)
1. El responsable aprueba y congela la v2.
2. El agente de cohorte ejecuta la calibración v2, la potencia, el plan (y pide confirmación si N > 400), la compuerta, la cohorte y la publicación, sin calcular D ni p.
3. Claude hace el análisis único.
4. El responsable aprueba el cierre.
