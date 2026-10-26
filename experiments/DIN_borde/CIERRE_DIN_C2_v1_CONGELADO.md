# DIN-C2 — cierre, v1 CONGELADO (2026-10-26)

**Estado:** **CONGELADO** el 2026-10-26 a las 10:00 (hora de México) por aprobación del responsable («apruebo cierre, sí conserva cohortes…»). El contenido es el de `CIERRE_DIN_C2_BORRADOR_v0.md`, que se conserva; la única diferencia es la sección 5, con las decisiones. El resultado confirmatorio es definitivo.

## 1. Veredicto confirmatorio: **PASS**
- **Análisis:** un único análisis con `C2/analisis_C2.py` (`d24ac5a7…`), congelado en `C2/MANIFIESTO_DIN_C2_v1_CONGELADO.sha256`; se verificó antes de correr.
- **Entradas:**
  - tabla `afd4783c…ca19` (publicada en el PR #89 por el agente de cohorte, que no calculó D ni p);
  - plan `ad320ac9…aed8` (N = 200, fijado por la regla de potencia antes de entrenar);
  - resumen vinculado por SHA.
- **Salida íntegra:** `C2/resultado/RESULTADO_C2.json`, SHA `011841fb…a6be8`, y la consola en `C2/resultado/salida_consola.txt`.
- **Ejecución:** Claude, en el contenedor (Python 3.13.16, numpy 2.5.3, scipy 1.18.1), el 2026-10-26 hacia las 09:55 (hora de México). Fue la única corrida.

| | valor |
|---|---|
| **Compuerta de régimen** | mediana de c250 = 0.858 (≥ 0.8) y mediana de q250 = 9.7·10⁻⁵ (≤ 0.05): **cumple** |
| fracción individual colapsada (descriptiva) | 57.8 % (58 % en G3) |
| **D** (incremento fuera de muestra de X10 sobre la base cúbica de log ρ_caras(10)) | **0.0295** |
| p (5000 permutaciones dentro del split) | **0.0002** (= 1/5001, el mínimo) |
| percentil 95 del nulo de D | 0.0024 |
| pendiente de X | **+1.72** |
| datos | 1000/1000 trayectorias válidas, 200/200 splits, 0 faltantes |

## 2. Secundarios (no deciden)
| | C2 | G3 (s = 0.8, descubrimiento) | DIN-C1 (Wine) |
|---|---|---|---|
| D (primaria) | **0.0295** | 0.0173 | 0.0256 |
| D con ρ_vert | 0.0288 | 0.0173 | — |
| D_X \| R250 | **0.0285** | 0.0025 | (D7, descubrimiento: 0.042 de 0.078) |
| W_adj legado | 0.157 | 0.069 | 0.199 |
| D en el subconjunto colapsado individualmente (457 trayectorias, 113 splits) | 0.056 | — | — |

- **Tamaño del efecto:** es **mayor** que el de G3 y comparable al de DIN-C1. No hubo encogimiento respecto del descubrimiento.
- **Paso por R250, con resultado opuesto a G3:** casi nada del incremento pasa por R250 (D cae de 0.0295 a 0.0285). En G3, en cambio, R explicaba ≈ 85 %. El papel de la confianza final del dominante como vía **no es estable** entre cohortes de la misma familia. Es una observación descriptiva, no una prueba de mecanismo.
- **Subconjunto colapsado:** el efecto es mayor (D = 0.056) en las trayectorias que colapsan individualmente. Va en el sentido de H-colapso, pero es descriptivo y el subconjunto no se eligió al azar.

## 3. Interpretación (alcance congelado)
- **Lo que se confirma:** es una **réplica confirmatoria independiente en la familia gaussiana explorada por G3** (s = 0.8). En esa familia, la incertidumbre temprana sobre el ejemplo de validación más difícil (update 10) mejora fuera de muestra la predicción de la distancia perspectival al borde en el update 250, más allá de una base cúbica de ρ_caras(10), con el sentido anticipado.
- **Con DIN-C1**, el resultado queda confirmado en **dos familias**: una real (WineMLP) y una sintética (mezclas gaussianas en régimen de colapso).
- **Lo que no se afirma:**
  - que el colapso sea **necesario**, porque C2 no lo manipula (Q13);
  - causalidad;
  - transferencia a otros datos reales u otras arquitecturas;
  - información nueva sobre toda función de ρ(10), porque la comparación es contra una base cúbica;
  - la vía por la que actúa X: R250 no la explica en C2.

## 4. Desviaciones y declaraciones
- **Ejecución:** Claude corrió el análisis en el contenedor. La cohorte la generó y publicó otro agente sin analizarla, como fija el diseño.
- **Elección del nivel:** s = 0.8 se eligió por G3. Las semillas de C2 son disjuntas de G2 y G3, y el plan con N = 200 salió de la regla de potencia antes de entrenar.
- **Verificador:** el fallo de rutas del verificador v1 del agente se conservó, con una enmienda previa a la v2. Ninguna medición se repitió.

## 5. Decisiones del responsable (2026-10-26 10:00)
1. **Cierre aprobado.** DIN-C2 queda cerrado con veredicto **PASS**.
2. **Cohortes conservadas** (C2 y las anteriores), con una **nota de depuración** en `docs/data-retention.md`: más adelante se revisará qué conservar, preguntando antes si sigue siendo relevante. No se borra nada sin esa revisión y sin la aprobación del responsable.
3. **Siguiente paso:** **D9**, el colapso como predictor de la generalización. Si no sale como se espera, se mide **Q13**: si el colapso es necesario, manipulándolo.
