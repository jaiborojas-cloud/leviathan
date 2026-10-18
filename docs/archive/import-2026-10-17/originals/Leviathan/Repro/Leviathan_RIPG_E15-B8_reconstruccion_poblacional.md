# Leviathan / RIPG — E15-B8: reconstrucción poblacional mesh-independent

Fecha: 24 septiembre 2026.

Casos PASS: **16/16**. Cada estado utiliza seis fuentes y un contorno geodésico común de 2048 rayos, j=0. Resultado poblacional completo: **PASS**.

## Estimandos por estado

| Split | Régimen | Estado | C_A mediano | Dispersión C_A (%) | Λ₁% | Λ₀.₁% | f₅₀ | f₉₀ | R_eff |
|---|---|---|---|---|---|---|---|---|---|
| 0 | random | PASS | 0.000376249257422 | 2.08209731653e-08 | 0.0105171333032 | 0.00105337149156 | 0.488611746694 | 0.895472864483 | 0.999279925098 |
| 0 | true | PASS | 387.701371651 | 0.000437392343293 | 0.355986950089 | 0.0456998522187 | 0.0162548656209 | 0.0672377092915 | 0.0481653825331 |
| 1 | random | PASS | 0.000146135247429 | 2.52196119667e-09 | 0.0100470550237 | 0.00100485496939 | 0.498962475678 | 0.899601196661 | 0.999994023941 |
| 1 | true | PASS | 329.409044064 | 0.000619029463203 | 0.43772226976 | 0.0702535135492 | 0.0131678386769 | 0.141490777142 | 0.0399787763248 |
| 2 | random | PASS | 0.000256565654265 | 2.72768707215e-08 | 0.0101340353309 | 0.00101382542216 | 0.497056404766 | 0.898864930634 | 0.999951897834 |
| 2 | true | PASS | 3.04954544051 | 0.00205009213537 | 0.0790623914785 | 0.0087724595977 | 0.100072444299 | 0.377295381651 | 0.289775158544 |
| 3 | random | PASS | 0.000145072910692 | 1.85441785293e-09 | 0.0101795963473 | 0.00101853742605 | 0.496051453098 | 0.898470991244 | 0.99991344609 |
| 3 | true | PASS | 14.7854262739 | 0.00129204525587 | 0.0757154936432 | 0.00824240283222 | 0.0995426069933 | 0.336632958459 | 0.284546982351 |
| 4 | random | PASS | 0.00383803858569 | 1.96289129279e-08 | 0.0103499548926 | 0.00103613015405 | 0.49238514604 | 0.897038453361 | 0.999678109213 |
| 4 | true | PASS | 1.07230364287 | 0.000450826411594 | 0.0906621466918 | 0.0100250682956 | 0.0782256036604 | 0.249319381674 | 0.221230719929 |
| 5 | random | PASS | 0.000413792952761 | 2.08145208872e-09 | 0.0100624365982 | 0.00100644288429 | 0.498621123252 | 0.899468760413 | 0.999989444662 |
| 5 | true | PASS | 36.7531617773 | 0.00131591828835 | 0.608588764461 | 0.142487974763 | 0.00670065911107 | 0.0324522776794 | 0.0185014354309 |
| 6 | random | PASS | 2.66182702476e-06 | 4.24298450916e-07 | 0.0104281964176 | 0.0010441851239 | 0.490567745283 | 0.89627524165 | 0.999506082053 |
| 6 | true | PASS | 1053.5743122 | 0.00102494008097 | 0.962848050841 | 0.793716260257 | 0.000259782716806 | 0.00230549765682 | 0.000748323108021 |
| 7 | random | PASS | 0.00406372127556 | 1.77993640927e-07 | 0.010940374374 | 0.00109716351738 | 0.479721498347 | 0.891828310365 | 0.99771856752 |
| 7 | true | PASS | 96.2177366389 | 0.000538301746174 | 0.215994044075 | 0.027686634772 | 0.0299084493538 | 0.0896296473197 | 0.0822793208225 |

## Direcciones pareadas

| Estimando | Mediana true | Mediana random | Pares válidos | true > random | true < random |
|---|---|---|---|---|---|
| C_A | 66.4854492081 | 0.000316407455844 | 8 | 8 | 0 |
| lambda_1pct | 0.285990497082 | 0.01026477562 | 8 | 8 | 0 |
| lambda_01pct | 0.0366932434953 | 0.00102733379005 | 8 | 8 | 0 |
| frac50 | 0.0230816574874 | 0.494218299569 | 8 | 0 | 8 |
| frac90 | 0.115560212231 | 0.897754722303 | 8 | 0 | 8 |
| R_eff | 0.0652223516778 | 0.999795777652 | 8 | 0 | 8 |

## Sustitución del mapa provisional B5

`E15_B8_poblacion_mesh_independent.csv` es la nueva tabla canónica para los estados PASS. Las estimaciones se agregan como mediana de las seis fuentes a 2048 rayos. El mapa B5 original se conserva intacto como histórico; no se promedian sus valores con B8 ni se los trata como incertidumbre estadística.

La definición por área de las métricas de concentración se mantiene exactamente como B6/B7. Los números B5 basados en fracciones de celdas no son el mismo observable y no se interpretan como diferencias cuantitativas de la misma medida. El CSV incluye sólo C_A histórico como referencia de revisión numérica, no una banda de error.

El contraste describe los checkpoints guardados. No agrega evidencia causal, no usa las fases como réplicas estadísticas y no actualiza los cálculos Shapley por profundidad. No se amplía a los 40 pares.

## Precisión y límites

PASS distingue convergencia interna e independencia entre las seis triangulaciones. El dominio es un polígono de 2048 rayos que aproxima el disco geodésico. La auditoría 8192 de B6 sólo corresponde a una fuente de split 6 true; no certifica por sí sola la precisión de borde de toda la población. La reconstrucción es mesh-independent al protocolo/resolución declarados, no un límite continuo demostrado.

Los archivos por caso guardan área calibrada, errores de área por fuente, mínimos autovalores, máxima condición, historial de refinamiento, tiempos, excepciones y hashes de las matrices finales. Se guardan muestras deterministas de celdas para inspección; las nubes completas se regeneran con el ejecutor y los checkpoints. No se recalcularon valores problemáticos cambiando umbrales.

## Coste

```json
{
  "wall_seconds": 412.6337489740008,
  "workers": 2,
  "sum_case_cpu_seconds": 935.4510555750002
}
```

El reloj de la reanudación reutiliza B7 ya calculado; el coste por caso conserva el tiempo íntegro de B7.

## Incidencias

Sin casos fallidos ni inconclusos. La excepción de serialización del log previa al arranque de B8 está documentada en B7 y no modificó la geometría ni las compuertas.
