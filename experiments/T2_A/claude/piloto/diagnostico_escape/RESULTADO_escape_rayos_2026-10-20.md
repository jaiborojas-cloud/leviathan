# Diagnóstico de escape de rayos — split8_j5, j7, j8 (update 25) — 2026-10-20
Solo lectura. No clasifica, no asigna Y. Script `anexo_implementacion/diagnostico_escape_rayos.py` (SHA-256 037e6a53e478ca6d3a86b3601181ce7827bfac349c0aa3a77b885e3b1676e264), float64, nt=2048, DOP853 rtol 2e-10 atol 2e-12, ejecutado en el contenedor sobre los estados regenerados (hash verificado contra regeneracion_u25.csv); contrastado con el CSV de MPFR de 169 bits (t de cruce de umbrales de max|p| coincide a ~1e-8 en j7 y ~1e-10..1e-8 en j8). Falta repetirlo en Windows (hardware del responsable).

| caso | rayos que escapan (índice, ángulo) | t* (escape) | A(t) al paro | ¿A llega a 0.02 antes del escape? |
|---|---|---|---|---|
| j5 | 1775–1776 (≈5.45 rad) coincide con el diagnóstico del agente original | ≈0.0745–0.0747 (borde local 0.07447 del agente original) | 0.018467 en t=0.07402 (max\|p\|=150); original 0.018714 en 0.07447 | NO |
| j7 | ≈1828 (≈5.61 rad), sector contiguo 1780–1877 | ≈0.074662 (MPFR: colapso geométrico dt×0.85, \|v\|×1.25, max\|p\|+11 por paso) | 0.018531 en t=0.07418 (max\|p\|=150); crecimiento ≈0.53/unidad → ≈0.0188 en t* (extrapolación, no medida) | NO (estimado) |
| j8 | ≈1822 (≈5.59 rad) más otros sectores (|p|>10 en 299 rayos, no contiguos) | ≈0.087459 (MPFR) | 0.0239 en t=0.0861 | SÍ: A=0.02 en t≈0.0792 |

Lectura (descriptiva): el crecimiento de |p| ≈ −C·ln(t*−t) y de |v| ≈ C/(t*−t) indica que los rayos salen de la carta (frontera de la familia softmax) a distancia intrínseca finita, no que haya ruido de precisión (MPFR reproduce). En j5 y j7 el área alcanzable dentro del dominio parece < 0.02: el disco nominal no existiría. En j8 el disco nominal (t≈0.0792) existe y queda ANTES del escape (0.0875), pero la cota de búsqueda de la calibración (0.09) queda DETRÁS: ningún cómputo hasta 0.09 puede terminar; la pausa de j8 sería consecuencia de esa cota y no del disco nominal. Reducir la cota de búsqueda no reduce el área nominal 0.02.
Pendiente de decisión del responsable (no está en el anexo v1.0 ni en E1 v8): qué estado corresponde a «A_max dentro del dominio < 0.02» y cómo se trata en el análisis; regla de cota adaptativa para calibrate.
