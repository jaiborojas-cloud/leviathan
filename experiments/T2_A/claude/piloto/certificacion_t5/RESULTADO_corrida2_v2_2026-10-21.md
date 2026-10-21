# Corrida 2 de la certificación de T5 (script v2, `5009cab8…`) — 2026-10-21 ≈15:44–15:57

Corrida del responsable (Windows 11, Python 3.12.10, numpy 2.3.5, scipy 1.18.1, 24 CPU), con salida en `D:\RIPG_DATA\T2_A\expediente\certificacion_t5\salida_v2_2026-10-21\`. Las salidas pequeñas están archivadas en `corrida2_v2/`. **Se conserva tal cual.**

## Resultado oficial de esta corrida
`procedimiento_valido` = falso, porque el control j8 terminó en `ERROR_DE_EJECUCION` y V1 en j8 y V2 no se evaluaron.
- **j5:** `T5_NO_CERTIFICADA`. La única razón es la invalidez del procedimiento; todos sus criterios propios pasaron (abajo).
- **j7:** `T5_NO_CERTIFICADA` por **(iii): U = 0.019744 > 0.0195** (además de la invalidez).

Ningún estado cambia. No asigna Y.

## Valores por caso
| | j5 | j7 |
|---|---|---|
| Cara (j, i \| k) | (13, 6 \| 20), es decir, sobrevivientes 6 y 13, transversal 20 | igual |
| β mín. de los demás | 8.3357 | 8.3357 |
| Tasas f·v (dos sobrevivientes / transversal / cuarto) | 162132 / 161878 / 159684 / 140919 | 153889 / 153636 / 151568 / 133751 |
| C1–C6 | OK | OK |
| T* (rayo designado 1776 / 1828) | 0.07447464619554 | 0.07466422956747 |
| δ_T (tolerancias ×1 frente a ×1/100) | 1.4×10⁻¹⁶ | 1.4×10⁻¹⁴ |
| db/dr en el borde; w_i, w_j | −228.003; 0.0636, 0.9364 | −224.600; 0.0629, 0.9371 |
| Rapidez intrínseca en el borde | 1 + 6×10⁻⁹ | — (C5 OK) |
| t₀; A₀; δ_disc; V3 | 0.07100276; 0.0168796; 4.8×10⁻⁸; 9.4×10⁻⁸ | 0.07150965; 0.0171388; 4.8×10⁻⁸; 1.0×10⁻⁷ |
| Rayos a carta de cara; problemas | 40; 0 | 41; 0 |
| Solape float64/mpmath (máx. rel.) | 8×10⁻¹² | 1×10⁻¹¹ |
| κ̂ (513 = 1025) y rayo del máximo | 1.409×10⁴ (1822) | 2.568×10⁴ (1877) |
| κ = 4 κ̂; Δ; cosh(√κ Δ) | 5.64×10⁴; 3.472×10⁻³; 1.359 | 1.03×10⁵; 3.155×10⁻³; 1.556 |
| L⁺; ε_θ | 0.7334; 3×10⁻¹⁵ | 0.8256; — |
| **U (U/0.02)** | **0.019426 (0.971)** ≤ 0.0195 | **0.019744 (0.987)** > 0.0195 |
| V1: U(t₁) frente a A medida en t₁ | 0.0176388 ≥ 0.0176046 ✓ | 0.0176880 ≥ 0.0176735 ✓ |

**Contraste con el análisis independiente del agente original** (j5, otro estado: M/f de otro entorno). Allí la cara era 6/13 \| 20, el borde del rayo 1776 estaba en 0.07447464621825, db/dr = −228.0027 y w6 = 0.06359. Aquí, con los estados regenerados: 0.07447464619554, −228.0027 y 0.06359. La diferencia en T* (2.3×10⁻¹¹) es del orden del error de reconstrucción de los estados.

## Por qué falló j8 (defecto de robustez del script)
El escape de j8 se resolvió bien: cara con C1–C6 OK y T* = 0.08746544626360, δ_T = 8×10⁻¹⁵. La caída ocurrió en la **continuación en la carta P** hasta T⁺. La métrica en float64 se volvió singular (`LinAlgError: Singular matrix` en `geometry.jet`) dentro de un paso, antes de que algún rayo llegara al umbral de |p| = 150 donde el protocolo pasa a la carta de cara. j8 tiene varios sectores escapando (299 rayos con |p| > 10, no contiguos), a diferencia de j5 y j7. El protocolo no prevé una carta P singular antes de 150, y v2 no manejaba la excepción.

## Corrección (script v3)
Si la carta P se vuelve singular en la continuación (al iniciar o dentro de un paso), los rayos ya en régimen de escape (|p| ≥ 40, el mismo umbral con que arranca el rayo designado) pasan a la carta de cara desde su último estado aceptado. Si no hay ninguno, la continuación se detiene, el muestreo de K se trunca y el caso queda no certificado, con la razón.

**Efecto esperado sobre j5 y j7:** ninguno. Su continuación no tuvo singularidades, así que v3 debe reproducir sus números exactamente; si no, sería una anomalía y se reportaría.

**Efecto sobre la validez del control:** V1 de j8 solo depende de [t₀, t₁], que es anterior al punto de la caída. V2 exige U(j8) ≥ 0.0239 y que j8 no se certifique.

**Declaración:** es el tercer intento y el segundo defecto de implementación corregido después de ver resultados. Ninguno de los dos cambios toca t₀, factores, margen, tolerancias ni los cálculos de j5 y j7. Se reporta tal cual a la revisión de E2.
