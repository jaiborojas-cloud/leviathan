# DIN-Q13-DR — resultado del análisis único (2026-10-26)

**Veredicto primario (regla congelada v3):** **MODULA.** Al reducir el colapso de M con *label smoothing*, la señal temprana baja con tendencia lineal: β = 0.077, con IC95 [0.028, 0.140].

**Secundarios predeclarados:**
- equivalencia: **NO_ESTABLECIDA**;
- extremo (L5): **INDETERMINADO**. L5 no da PASS, pero el IC95 superior de D_L5 es 0.0061, apenas por encima de 0.006.

## Procedencia
- **Diseño:** `DISENO_DIN_Q13DR_v3_CONGELADO.md` (`e3ebe060…`), congelado a las 22:24 antes de cualquier dato.
- **Análisis:** `analisis_Q13DR.py` v3 (`cc5524a7…`), verificado por el auditor en el PR #107 y ejecutado **una sola vez**.
- **Cohorte:** generada en el equipo del responsable con `cohorte_v3.py` (`7b855802…`) y las versiones exactas.
  - Tabla `ed00364f…`, plan `e7c99a01…` y resumen vinculados; compuerta de reproducción PASA.
  - **6000 de 6000** trayectorias, 0 errores y 0 faltantes; los **200 de 200** splits son comunes.
- **Resultado:** `RESULTADO_Q13DR.json` (`0f74669d…`), sin réplicas de bootstrap fallidas (0 de 2000).

## Compuerta de manipulación (pasa)
| nivel | ε | mediana c250 | mediana q250 | precisión del panel |
|---|---|---|---|---|
| L0 | 0 | 0.869 | 8.6e-5 | 0.926 |
| L1 | 0.002 | 0.694 | 1.5e-4 | 0.926 |
| L2 | 0.005 | 0.612 | 1.9e-4 | 0.926 |
| L3 | 0.01 | 0.556 | 2.3e-4 | 0.926 |
| L4 | 0.02 | 0.501 | 2.7e-4 | 0.889 |
| L5 | 0.05 | 0.399 | 3.4e-4 | 0.889 |

c baja de forma estricta. El rango es 0.470, por encima de 0.30. En L4 y L5 la pérdida de precisión es de 0.037, por debajo de 0.10.

## Primaria por nivel (5000 permutaciones) e IC95 del bootstrap pareado
| nivel | c250 | D | p | pendiente X | PASS | IC95 de D |
|---|---|---|---|---|---|---|
| L0 | 0.869 | **0.0343** | 0.0002 | 2.00 | sí | [0.010, 0.062] |
| L1 | 0.694 | **0.0110** | 0.0016 | 0.70 | sí | [−0.002, 0.028] |
| L2 | 0.612 | **0.0037** | 0.026 | 0.36 | sí | [−0.006, 0.016] |
| L3 | 0.556 | 0.0013 | 0.086 | 0.24 | no | [−0.007, 0.012] |
| L4 | 0.501 | −0.0004 | 0.23 | 0.13 | no | [−0.008, 0.008] |
| L5 | 0.399 | −0.0010 | 0.36 | 0.08 | no | [−0.009, 0.006] |

**Pendiente dosis-respuesta:** β = **0.0769**, con IC95 **[0.0278, 0.1403]**.
- **Equivalencia:** el margen es 0.02 × 0.470 = 0.0094. El IC queda fuera, así que la equivalencia es NO_ESTABLECIDA.

## Descriptivos (no deciden)
- **Monotonía:** Spearman(D, c) = **1.0**. Las seis D están ordenadas como c.
- **Con ρ_vert:** el patrón es el mismo, de 0.034 a −0.002.
- **Varianza tras la base:** la fracción que queda es ≈ 1.00 en los seis niveles. La base cúbica de ρ10 casi no explica Y fuera de muestra en ningún nivel. Por eso la caída de D **no** viene de un cambio en lo que explica la base.
- **Dentro de L0, por cuartiles de c250** (observacional, n pequeño): Q1 da −0.023, Q2 −0.016, Q3 0.054 y Q4 0.128. Va en la misma dirección que la manipulación.

## Lectura
1. **La señal temprana depende de forma graduada del colapso.** Con LS, a menos colapso, menos señal, y la caída es monótona en los seis niveles.
2. **La señal ya no se distingue de cero desde c250 ≈ 0.56** (L3–L5 sin PASS). Aun así, el extremo es INDETERMINADO: no se demuestra que desaparezca (IC superior 0.0061 frente al criterio de 0.006), solo que deja de detectarse.
3. **Coherencia con lo anterior:**
   - L0 replica la señal por cuarta vez (D = 0.034; Q13 A0 dio 0.039).
   - L2 (ε = 0.005, c = 0.61) da D = 0.0037, en línea con Q13-LS, donde el mismo ε y c = 0.60 dieron D = 0.0083 con cohortes y semillas distintas. Los IC se solapan.
4. **Lo que no dice:**
   - Hay un solo manipulador, así que no separa el colapso del efecto propio de LS sobre la confianza.
   - Prueba una tendencia lineal (aquí también monótona), no un mecanismo causal del colapso.
   - Es una sola familia: gaussianas s = 0.8 con el MLP 13→64→32→3.
