# T2-A1 — diagnóstico de la degeneración temprana: resultado (2026-10-24)

Protocolo `PROTOCOLO_diagnostico_degeneracion_v0.md`; script `diagnostico_degeneracion.py`. Ambos registrados con commit (`032a1d7`) **antes** de correr. 80 estados (60 visitas primarias de 0b y 20 del update 25), todos analizados, sin selección. **Sin X.** Muestra de desarrollo; el régimen de cada estado viene de 0b y se conocía antes de medir. Salidas en `resultados/`.

## 1. H-d1: la distancia al borde explica la patología. **Se apoya.**
ρ_borde es la longitud métrica mínima de una semirrecta de la carta hasta el infinito: una cota superior de la distancia de P0 al borde de la familia. Cálculo estable: diferencia entre órdenes de cuadratura ≤ 6×10⁻¹⁴ relativo; entre 720 y 1440 direcciones ≤ 10⁻⁴.

| régimen en 0b | estados | ρ_borde mín | mediana | máx |
|---|---|---|---|---|
| escape certificado (vía C, split8_j9) | 3 | 0.0077 | 0.0097 | 0.0168 |
| degeneración temprana (haz agota 5000 pasos o C5 falla; splits 8 y 11) | 22 | 0.0048 | 0.0174 | 0.0572 |
| calibración pausada, cota no calculada (split 11) | 4 | 0.0150 | 0.0244 | 0.0389 |
| **presupuesto de calibración** (split 10) | 8 | **0.0968** | 0.1135 | 0.1732 |
| auditoría interrumpida | 7 | 0.098 | 0.755 | 3.16 |
| evaluada INCONCLUSIVE | 3 | 0.56 | 0.60 | 0.86 |
| sana (D = 0) | 13 | 0.77 | 3.37 | 8.54 |
| update 25 (piloto): T5 j5 / sospecha j7 / j8 vía D4 | 3 | 0.0800 | 0.0825 | 0.0924 |
| update 25: GNI / INJECTIVE | 2 / 15 | 0.097 / 0.106 | — | 0.233 / 1.21 |

- **Separación sin solape:** todos los casos degenerados o con escape tienen ρ_borde ≤ 0.057; todos los demás, ≥ 0.097. Split 10 (presupuesto) queda del lado no degenerado, como se predijo.
- **Coherencia (prueba de falsación del protocolo):** en los 25 casos donde el haz se detuvo antes de t_bound (escape o 5000 pasos), lo hizo en t = 0.67–0.97 × ρ_borde. En los 8 escapes con T* medido, **T* ≤ ρ_borde en todos**: 5 del paso 3 de 0b (split8 j5 y j7 en el update 50 y j9 en 50, 150 y 250) y 3 del update 25 de la corrida 4 de T5 (j5 0.07447 ≤ 0.08245; j7 0.07466 ≤ 0.08001; j8 0.08747 ≤ 0.09238). Ningún caso viola la cota.
- **Lectura:** el «arrastre» del integrador en los splits 8 y 11 no es un defecto numérico arbitrario. Los rayos **se están acercando al borde de la familia** (la métrica es incompleta) a una distancia del orden de ρ_borde, mucho menor que el radio nominal (≈ 0.08). En esas geometrías el disco de área 0.02 no puede construirse con la exponencial porque el borde está antes.
- **Evolución:** la degeneración es progresiva con el entrenamiento. Por ejemplo, ρ_borde de split8_j5 pasa por 0.082, 0.018, 0.008 y 0.006 en los updates 25, 50, 150 y 250. Split11_j20 pasa por 0.124, 0.041, 0.018 y 0.013, y la cara de escape cambia entre el update 25 y el 50.

## 2. H-d2: el panel. **No explica por sí solo.**
f es idéntico dentro de cada split (un solo hash por split y en todos los updates). Las envolventes son parecidas: 8–9 vértices, arista mínima 0.27–0.47, ángulo mínimo 64°–96°. Split 8 no es atípico, y split 11 tiene la envolvente más «regular». La degeneración aparece al entrenar con el **mismo** f, así que la produce M (el modelo) en interacción con el panel. H-split queda matizada: el split importa, pero no por una rareza visible del panel.

## 3. H-d3: el origen
- **K(P0)** es grande y positiva en los degenerados (mediana ≈ 5×10³; hasta 1.6×10⁴) y casi nula o negativa en los sanos (≈ −0.06).
- **La condición de G(P0) no discrimina**: los sanos tienen una mediana de ≈ 5×10³.

## 4. Qué implica (para el diseño v3; nada de esto es una regla vigente)
1. **ρ_borde es barato** (≈ 12 s por estado, sin integrar la exponencial), **siempre computable** (0 fallos en 80) y separa los regímenes sin solape. Es candidato natural a desenlace o a disparador de T2-A1 v3.
2. **Es una cota superior.** ρ_borde < r demuestra, con la precisión del cálculo, que hay un punto del borde a distancia menor que r. Pero ρ_borde ≥ r **no** demuestra que el borde esté más lejos. Para un desenlace binario con ambos lados acotados haría falta una cota inferior. Una opción es combinarlo con la exponencial cuando esta sí completa su disco.
3. **Riesgo de tautología con X**, que se mide en el update 5 con la misma geometría (la lección de T1-B). Hay que medirlo antes de congelar nada.
4. **Split 10 es otro problema** (presupuesto de calibración, no geometría) y se resolvería con más tiempo o con un radio fijo.

## 5. Qué no se afirma
ρ_borde no es la distancia exacta al borde ni un certificado de que la exponencial escape. La separación se observó en 80 estados de 4 splits (desarrollo), con régimen conocido. No se usó X.
