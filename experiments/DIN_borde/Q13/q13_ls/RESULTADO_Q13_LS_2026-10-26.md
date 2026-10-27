# DIN-Q13-LS — resultado del análisis único (2026-10-26)

> **Etiqueta:** análisis de un solo manipulador (*label smoothing*). Se decidió **después** de que la compuerta de manipulación de Q13 v2 fallara en WD (mediana de c250 = 0.740 > 0.70) y **antes** de calcular cualquier D. **No sustituye** el veredicto de Q13 v2 (INCONCLUSIVE_MANIPULACION).

**Veredicto (regla congelada):** **NO_CONCLUYENTE.** LS queda como INTERMEDIO: la señal **baja mucho, pero no desaparece.**

## Procedencia
- **Protocolo:** `PROTOCOLO_Q13_LS_v1_CONGELADO.md`, congelado a las 18:54 y subido en `c222cdf` **antes** de ejecutar.
- **Tabla:** `e88a964f…`, con 8000 de 8000 filas y 0 faltantes; 800 splits comunes.
- **Plan:** `f0651c42…`.
- **Script:** `analisis_Q13.py` (`9998a1b2…`), sin cambios y ejecutado una vez.
- **Resultado:** `resultado/RESULTADO_Q13.json` (`899aae78…`).

## Compuerta
Pasa. A0 tiene c250 = 0.863 y q250 = 9e-5; LS tiene c250 = 0.601. La precisión del panel es 0.926 en ambos.

## Primaria y bootstrap pareado (2000 réplicas, 800 splits)
| brazo | D | p (5000 perm.) | pendiente X | IC95 de D | PASS |
|---|---|---|---|---|---|
| A0 (colapsado) | **0.0393** | 0.0002 | 1.95 | [0.0256, 0.0535] | sí |
| LS (c250 = 0.60) | **0.0083** | 0.0002 | 0.43 | [0.0021, 0.0153] | sí |
| ΔD = A0 − LS | 0.0310 | — | — | **[0.0200, 0.0420]** | — |

- **Por qué no es CAE:** el IC95 superior de D_LS es 0.0153, mayor que 0.006. La señal sigue presente: p = 0.0002 y el IC inferior es mayor que 0.
- **Por qué no es SE_MANTIENE:** el IC95 inferior de ΔD es 0.020, mayor que 0. La señal baja de forma significativa.
- **Con ρ_vert** (secundario): A0 da 0.0390 y LS da 0.0082, el mismo patrón.

## Lectura (descriptiva; no forma parte del veredicto)
1. **La señal temprana se replica con fuerza en A0:** D = 0.039, mayor que el 0.0295 de C2 y que el 0.017 de G3, con semillas nuevas, en la misma familia gaussiana s = 0.8.
2. **Al reducir el colapso con LS, la señal cae en torno al 79 %, pero sobrevive.** Esto **no** apoya que el colapso sea *necesario* en sentido estricto. Sí es compatible con que el colapso **amplifique** la señal.
3. **Amenaza 1 del diseño, presente:** LS reduce a la mitad la variabilidad intra-split del desenlace (DE de log ρ250: 0.61 en A0 frente a 0.29 en LS), mientras la de X10 no cambia (0.062 en ambos). Parte de la caída de D puede deberse a que hay menos rango que predecir y no a la falta de colapso. La pendiente estandarizada también baja a la mitad (0.20 frente a 0.09).
4. **Lo que sigue sin poder separarse:** con un solo manipulador no se distingue el efecto del colapso del efecto propio del *label smoothing*.

## Estado de Q13
- **Q13 v2:** INCONCLUSIVE_MANIPULACION.
- **Q13-LS:** NO_CONCLUYENTE, con la señal atenuada pero presente.
- **Pregunta abierta, reformulada:** ¿el colapso *modula* la intensidad de la señal (relación graduada) en lugar de ser una condición necesaria? Esta lectura nació de este resultado. Contrastarla exigiría un diseño nuevo, por ejemplo varias dosis y un control de la varianza de Y. No se responde con estos datos.

## Errata (2026-10-26 19:20, sin cambiar el veredicto)
El punto 3 de la «Lectura» sobrestimaba la amenaza 1.
- **Por qué:** D = 1 − SSE_full/SSE_base **no depende de la escala de Y**. Si LS solo encogiera log ρ250 de manera uniforme, D no cambiaría.
- **Lo que muestran los datos:** la pendiente cruda baja 4.5 veces (de 1.95 a 0.43), mientras la DE de Y baja 2.1 veces. La relación X→Y se debilita más allá de la escala.
- **Lo que sigue siendo posible:** una restricción de rango **no uniforme**, es decir, que LS comprima justo la parte de Y que X predice. Esa posibilidad no se distingue con estos datos.
- **Corrección:** donde dice «parte de la caída de D puede deberse a que hay menos rango que predecir», léase «la caída no se explica por la escala de Y; una restricción no uniforme no está descartada».
