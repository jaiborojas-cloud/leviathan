# T2-A1 — cierre, BORRADOR v0 (2026-10-24)

**Estado:** borrador para el responsable. El resultado confirmatorio es definitivo y no se modifica. Este documento solo lo resume y lo interpreta.

## 1. Veredicto confirmatorio: **NOT_MET**
Análisis único: `fase3/analisis_T2A1.py` (`9a191450…ed37`), corrido el 2026-10-24 a las 14:01 (hora de México) por el responsable. Salida íntegra: `fase3/resultado/RESULTADO_T2A1.json` (`2624dc74…80ad`). Las cuatro entradas coincidieron por hash: X `9458…ee70a`, fase 2 `be47…02de`, L5 `618c…df2d` y comparadores no geométricos `e9e4…8ab6`.

| prueba | W | p (unilateral) | percentil 95 del nulo |
|---|---|---|---|
| W sobre Y_c (primario) | 0.019 | 0.326 | 0.067 |
| W_adj, residuos tras ajustar por L5 | 0.011 | 0.393 | 0.065 |

- **Datos válidos:** 156 de 156 splits; 780 de 780 trayectorias, sin faltantes de X ni de Y_c; 0 visitas con fallo numérico. No aplica ningún motivo de INCONCLUSIVE.
- **Interpretación:** en estos datos, X (κ_max(Dexp) en r*, update 5) **no anticipa** la cercanía posterior al borde dentro del split, ni en bruto ni ajustado por ρ_borde(u5).
- **Potencia** (0c′, sección 5): era ≥ 0.97 para ρ_X = 0.2 en tres de cuatro escenarios, y de 0.5–0.6 para ρ_X = 0.1. El resultado no es compatible con un efecto moderado (≈ 0.2), pero no descarta uno pequeño (≤ 0.1). La correlación global entre X y L5 es −0.13, lejos del escenario adverso de la sección 5, en el que X se asociaba con L5 en +0.5.

## 2. Secundarios (descriptivos, no deciden)
- **Δ:** W = −0.034 (p = 0.80).
- **G global:** Spearman −0.021, IC95 [−0.154, 0.113].
- **Y_b:** 248 de 780 trayectorias llegan a ρ_borde < r*. En la cola del 10 % de X hay 23 de 78 (precisión 0.29 frente a una incidencia de 0.32; lift 0.93).
- **Comparadores geométricos** (C_A, Λ_0.1 % y −R_eff): ninguno es significativo (p entre 0.17 y 0.37). C_A coincide casi por completo con X (Spearman 0.998).
- **Comparadores no geométricos:** la **precisión en validación en el update 5** da W = 0.154, p ≈ 1·10⁻⁴. Es sin orientación previa y es una observación exploratoria, no un hallazgo. Va en el sentido de que los modelos que generalizan mejor temprano quedan después más cerca del borde (softmax más saturado). Las demás medidas, pérdida y precisión en entrenamiento y norma de pesos, no son significativas. **Confirmarlo exige un prerregistro nuevo con muestra independiente.**

## 3. Qué no se afirma
- No se afirma que X sea inútil en general. El resultado aplica a este desenlace (ρ_borde, una cota superior de la distancia al borde por e-geodésicas), a estas visitas (updates 50, 150 y 250) y a esta familia (WineMLP, 160 splits).
- No reabre T2-A0, que sigue INCONCLUSIVE y tiene otro desenlace, la no inyectividad.
- No se reutilizan estos datos para elegir un predictor nuevo y confirmarlo.

## 4. Desviaciones y declaraciones
- **Revisión adversarial de 0c′:** se omitió por decisión del responsable.
- **Copia de X:** está en el repositorio, sin cifrar, desde `3bb91da`, y hay además una copia de Nemotron en cuarentena. Ninguna decisión de T2-A1 usó su contenido.
- **Desenlaces de desarrollo:** el desenlace se eligió después de ver los de desarrollo (splits 8–11), como declara el diseño v3.

## 5. Decisiones pendientes del responsable
1. Aprobar este cierre (congelarlo como v1).
2. ¿Qué hacer con los estados de la fase 2 y con los checkpoints de T2-A0? Hoy se conservan.
3. ¿Abrir una línea nueva sobre la precisión en validación, con prerregistro y muestra nueva? Hoy solo es exploratorio.
