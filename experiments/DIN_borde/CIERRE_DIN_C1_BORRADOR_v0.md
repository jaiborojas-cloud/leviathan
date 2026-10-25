# DIN-C1 — cierre, BORRADOR v0 (2026-10-25)

**Estado:** borrador para el responsable. El resultado confirmatorio es definitivo y no se modifica.

## 1. Veredicto confirmatorio: **PASS**
- **Análisis:** un único análisis con `C1/analisis_C1_v2.py` (`8711f468…`), el script congelado en `C1/MANIFIESTO_DIN_C1_v3_CONGELADO.sha256`.
- **Entradas** (todas verificadas por hash): tabla `554f354e…` (publicada en el commit `69f7e3d` antes del análisis), resumen de cohorte `dc9ab200…` y compuerta v3 `eed9af07…`.
- **Salida íntegra:** `C1/resultado/RESULTADO_C1.json`, SHA `6541bc7e…fc44`, y la consola en `C1/resultado/salida_consola.txt`.
- **Ejecución:** a pedido del responsable («¿puedes ejecutarlo tú? no estoy en mi PC»), Claude lo corrió en el contenedor de la sesión el 2026-10-25 hacia las 12:55 (hora de México), con Python 3.13.16, numpy 2.5.3 y scipy 1.18.1. Tardó 20 s. El diseño no fija el entorno del análisis; el script es determinista con las semillas congeladas. Fue **la única corrida confirmatoria**.

| | valor |
|---|---|
| **D** (reducción del error fuera de muestra al añadir X a la base cúbica de log ρ(10)) | **0.0256** |
| p (5000 permutaciones de X dentro del split) | **0.0002** (= 1/5001, el mínimo posible) |
| percentil 95 del nulo de D | 0.0033 |
| pendiente de X | **+0.81** |
| datos | 780/780 trayectorias válidas, 156/156 splits, 0 faltantes; compuerta y resumen vinculados |

Se cumplen las tres condiciones: p < 0.05, D > 0 y pendiente > 0. Ningún motivo de INCONCLUSIVE.

## 2. Secundarios (no deciden)
| | cohorte nueva | descubrimiento (D6, splits 12–167) |
|---|---|---|
| D con base de grado 5 | 0.0260 (p 0.0005) | 0.074 |
| W_adj lineal-rangos | 0.199 (p 5·10⁻⁵) | 0.218 |
| W_adj flexible por rangos | 0.198 (p 5·10⁻⁵) | 0.225 |
| A: W de log ρ(30) frente a log ρ(250) | 0.638 (p 5·10⁻⁵) | 0.580 |
| auditoría de ρ(10) (40 IDs) | diferencia relativa máxima 8.3·10⁻¹⁵ | — |
| cota de cuerda en u10 | 0 violaciones; cara máxima 2 | — |

- **D es un tercio del de descubrimiento** (0.026 frente a 0.078). Coincide con la inflación por selección que el diseño anticipaba.
- **W_adj** (0.20) queda cerca del descubierto (0.22).
- **El resultado no depende de la base:** con grado 5, D apenas cambia.

## 3. Interpretación (alcance congelado en el diseño v3, sección 4)
- **Lo que se confirma:** en WineMLP, con splits e inicializaciones nuevos, la incertidumbre del modelo sobre su ejemplo de validación más difícil en el update 10 **mejora fuera de muestra la predicción** de la distancia perspectival al borde en el update 250, más allá de una base cúbica de ρ_borde(10). El sentido es el anticipado: más incertidumbre temprana, más lejos del borde al final.
- **El tamaño:** el efecto es modesto. Reduce el error de predicción dentro del split en un 2.6 %.
- **Lo que no se afirma:**
  - información nueva sobre *toda* función de ρ(10), porque la comparación es con una base cúbica;
  - causalidad: si ρ(10) mide con ruido la variable que mueve el desenlace, X podría ganar por medirla mejor;
  - transferencia a otras redes, datos o paneles (eso lo explora DIN-G1);
  - nada sobre T2-A0 o T2-A1, que conservan sus cierres.
- **Contraste con T2-A1:** la curvatura temprana X de T2 (update 5) no anticipaba el borde (NOT_MET). La **confianza** temprana en el ejemplo difícil (update 10) sí lo anticipa. Lo que se puede leer temprano no está en la curvatura de la geometría, sino en qué tan resuelto está el ejemplo que después dominará M.

## 4. Desviaciones y declaraciones
- **Ejecución en el contenedor:** el análisis lo corrió Claude en el contenedor y no el responsable en su equipo, a su pedido.
- **Historia del diseño:**
  - la primaria cambió de W_adj (v1) a D (v2) por el contraejemplo de D2b, **antes** de entrenar la cohorte;
  - las correcciones de entrada vinieron de la auditoría D2c, también antes de entrenar;
  - la compuerta pasó de exacta a numérica después de diagnosticar diferencias de redondeo entre entornos (`DIAG_compuerta_2026-10-24.md`).
- **Selección:** la primaria se eligió en D6 entre 18 combinaciones. La cohorte es independiente de esa selección.

## 5. Decisiones del responsable
1. Aprobar el cierre y congelarlo como v1.
2. Qué hacer con los estados de la cohorte. Hoy se conservan.
3. Siguiente paso: ¿esperar DIN-G1 (generalización exploratoria) o diseñar un confirmatorio en otra familia?
