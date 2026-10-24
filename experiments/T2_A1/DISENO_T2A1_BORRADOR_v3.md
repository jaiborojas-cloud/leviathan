# T2-A1 — diseño, BORRADOR v3 (2026-10-24)

**Estado:** borrador. Las tres decisiones quedaron resueltas por el responsable el 2026-10-24 a las 10:11 (sección 7). **No congelado; no autoriza ejecutar nada** salvo la fase 0a′ (instrumento y controles, sin muestra confirmatoria). Sustituye al desenlace D del diseño v2, cuya fase 0b falló (`fase0/RESULTADO_0b_2026-10-24.md`: D = ? en 44 de 60). Lo motiva el diagnóstico de desarrollo (`diagnostico/RESULTADO_diagnostico_2026-10-24.md`). Se mantiene todo lo de v2 que no se menciona aquí: muestras, X cerrado y comparadores no geométricos.

**Advertencia de procedimiento:** el desenlace de v3 se elige **después** de ver los desenlaces de la muestra de desarrollo (splits 8–11). Está permitido, porque la muestra confirmatoria (splits 12–167) sigue sin ninguna visita futura abierta, pero se declara. Ningún umbral de v3 se ajusta a los datos de desarrollo más allá de lo que aquí se escribe.

## 1. Pregunta (sin cambios)
¿Una señal geométrica temprana (X, update 5) anticipa la degeneración posterior de la geometría perspectival durante el entrenamiento?

## 2. Desenlace nuevo: distancia al borde, ρ_borde
- **Definición.** Para el estado (M, f) de una visita: ρ_borde = min_u ∫₀^∞ √(uᵀ G(s u) u) ds. Es la longitud métrica mínima de las semirrectas P = s·u del parámetro natural del softmax hasta el infinito. En una familia exponencial, esas semirrectas son **e-geodésicas** (rectas de la conexión exponencial), así que ρ_borde no depende de una carta arbitraria: es la longitud mínima de una e-geodésica desde P0 hasta el borde de la familia.
- **Qué acota.** Es una cota superior de la distancia de P0 al borde, porque es la longitud de una curva concreta que llega a él.
- **Qué tan ajustada es (E16-AG, PR #66, exploratorio).** En 40 triángulos softmax con distancia real al borde conocida analíticamente, ρ_borde/d_borde tiene mediana ≈ 2.0 y máximo ≈ 4.3: la cota **no es ajustada**. Pero **ordena bien** (Spearman 0.94 con la distancia real). En los 40 estados de AF la distancia real al borde no se conoce y el umbral finito |P|∞ = 150 no la sustituye: no se concluye nada. Consecuencias: (1) Y_c se interpreta como **longitud e-geodésica al borde**, no como la distancia geodésica; (2) el análisis primario es por rangos (W con Spearman), que depende del orden y no del ajuste; (3) Y_b = 0 es débil, con una holgura de 2–4 veces, y por eso queda como secundario.
- **Ventajas medidas en desarrollo** (80 estados): siempre computable (0 fallos), unos 12 s por estado, sin integrar la exponencial, y estable (≤ 10⁻⁴ entre resoluciones). Separa sin solape la degeneración y los escapes (≤ 0.057) de los demás regímenes (≥ 0.097). Además, el haz real se detiene en 0.67–0.97 × ρ_borde, y T* ≤ ρ_borde en los 8 escapes medidos.
- **Visitas:** updates 50, 150 y 250, como en v2. Por visita solo hace falta el estado (M, f), es decir, entrenar hasta el update k. No hay calibración ni auditoría.
- **Escala del desenlace (decidida):**
  - **(C) continuo, PRIMARIO:** Y_c = min_k ρ_borde(k) sobre las tres visitas, en escala log. No tiene «?» salvo fallo numérico, ni umbral.
  - **(B) binario, SECUNDARIO:** Y_b = 1 si alguna visita tiene ρ_borde < r*, con r* = 0.05697156262709151, el radio de X fijado en el prerregistro de T2-A0. Como ρ_borde es cota superior, Y_b = 1 **sí** demuestra que el borde está a menos de r*. Y_b = 0 solo dice que ρ_borde ≥ r* en las tres visitas, no que el borde esté más lejos; se reporta con esa salvedad.
  - Nota: en desarrollo, el máximo de los degenerados fue 0.0572 y el mínimo de los demás, 0.097, con r* entre ambos. Como r* venía del prerregistro, no se eligió con los datos. Aun así, que caiga ahí se declara.

## 3. Análisis
- **Primario W (dentro del split), sobre Y_c:** dentro de cada split, correlación de rangos entre X y −log Y_c, combinada entre los 156 splits con una prueba de permutación dentro del split. Predicción: X alto → borde más cercano después.
- **Secundarios:**
  - G (global), el mismo análisis sobre las 780 trayectorias, con bootstrap de splits;
  - Y_b con precision@top10 % de X y lift;
  - los comparadores geométricos sellados y los no geométricos (v2);
  - **ρ_borde en el update 5** como comparador propio (sección 4).
- **Criterio de éxito (decidido):** se exigen dos condiciones: (1) W significativa al 5 % unilateral sobre Y_c, y (2) la **misma prueba W aplicada a los residuos** de log Y_c tras una regresión dentro de cada split sobre log ρ_borde(u5), también significativa al 5 % unilateral. Es decir, X debe anticipar la degeneración **más allá** de lo que ya mostraba ρ_borde en el update 5. Los detalles (estadístico exacto, empates, splits sin variación) se fijan en 0c′.

## 4. Riesgo de tautología: X frente a ρ_borde(u5)
X (condición de Dexp en r* en el update 5) y ρ_borde salen de la misma métrica. Si X solo «ve» que el borde ya está cerca en el update 5, predecir ρ_borde futuro sería casi trivial (la lección de T1-B). Por eso:
- **ρ_borde(u5) se calcula para las 800 trayectorias** desde los `checkpoint_005`, antes de abrir X, y se publica por hash.
- La pregunta informativa es si X predice el ρ_borde futuro **más allá** de ρ_borde(u5), y si el cambio Δ = log ρ_borde(u250) − log ρ_borde(u5) se asocia con X.
- **Decidido:** primario W sobre Y_c con la condición de ajuste por ρ_borde(u5) de la sección 3. **Δ = log Y_c − log ρ_borde(u5) es análisis complementario** (W sobre Δ), reportado siempre, sin entrar en el criterio de éxito.
- **Dato de desarrollo que motiva el ajuste:** en las 20 trayectorias de los splits 8–11, ρ_borde(u25) predice el mínimo posterior con Spearman 0.96. Es sobre todo entre splits y en el update 25, no el 5, pero confirma el riesgo de tautología.

## 5. Fases
| fase | qué | compuerta |
|---|---|---|
| **0a′ instrumento** | congelar `rho_borde.py` (derivado sin cambios de cálculo de `diagnostico_degeneracion.py`), con controles analíticos: familia de 2 o 3 componentes con distancia al borde calculable a mano; invariancia afín de P; estabilidad de dirección y cuadratura | controles PASS |
| **0a″ validación externa** | **E16-AG** (otro agente; sintéticos de la familia T2 con respuesta conocida): comparar ρ_borde con la distancia real al borde (escape de la exponencial, shooting) y medir lo ajustada que es la cota | reporte; no bloquea si la cota es ajustada en los casos con escape observado |
| **0b′ cobertura** | ρ_borde en los 80 estados de desarrollo: ya hecho en el diagnóstico (80/80, 0 fallos); se repite con el script congelado de 0a′ | ≤ 1 % de fallos numéricos |
| **0c′ congelación** | desenlace, análisis (W, ajuste por ρ_borde(u5)), potencia simulada, comparadores | revisión adversarial y aprobación |
| 1 | ρ_borde(u5) de las 800, luego abrir X | hashes publicados antes de abrir X |
| 2 | 2340 visitas confirmatorias: entrenar hasta k y calcular ρ_borde (sin calibración ni auditoría) | informes operacionales sin desenlaces |
| 3 | análisis único | — |

**Recursos:** unos 10–20 s por visita (entrenar y ρ_borde) y unos 10 KB de disco por visita. Las 2340 visitas son del orden de horas en la PC, no días.

## 6. Qué no se afirma
- ρ_borde no es la distancia exacta al borde: es la longitud mínima de una e-geodésica hasta él.
- La degeneración que mide (incompletitud de la métrica cerca de P0) es un fenómeno distinto de la no inyectividad de T2-A0. No reabre T2-A0.
- Exploratorio hasta congelar 0c′.

## 7. Decisiones del responsable (2026-10-24 10:11)
Texto: «continuo como primario, éxito con W y ajuste por ρ_borde(u5), y Δ como análisis complementario».
1. Desenlace primario: Y_c continuo (mínimo de ρ_borde en las visitas 50/150/250). Secundario: Y_b binario con r*.
2. Éxito: W sobre Y_c **y** W sobre los residuos tras ajustar por ρ_borde(u5) dentro del split, ambas al 5 % unilateral.
3. Δ = log Y_c − log ρ_borde(u5): análisis complementario.

