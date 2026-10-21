# Corrida 1 de la certificación de T5 (script v1, `afc23c71…`) — 2026-10-21 ≈15:35

Corrida del responsable en su equipo (Windows 11, Python 3.12.10, numpy 2.3.5, scipy 1.18.1, 24 CPU), con salida en `D:\RIPG_DATA\T2_A\expediente\certificacion_t5\salida_2026-10-21\`. Bajo el protocolo v1 congelado. **Se conserva tal cual; no se descarta ni se sobrescribe** (sección 9).

## Resultado oficial de esta corrida
`procedimiento_valido` = falso. **j5 y j7: `T5_NO_CERTIFICADA`**, razón «(i) no se pudo obtener T* del rayo designado». V1 falla en los tres casos y V2 en j8, porque nada llegó a la etapa de la cota. Ningún estado cambia: j5 y j7 siguen `PAUSED_PENDING_REVIEW`. No asigna Y.

## Lo que sí se midió (etapas anteriores al escape)
| caso | t₀ (paso) | A₀ | δ_disc | V3 (rel.) | rayos con j ≤ 0 en (0, t₀] | rayo designado | t₁ |
|---|---|---|---|---|---|---|---|
| j5 | 0.0710027622 (37) | 0.0168795981 | 4.8×10⁻⁸ | 9.4×10⁻⁸ | 0 | 1776 | 0.0724031375 |
| j7 | 0.0715096529 (37) | 0.0171388416 | 4.8×10⁻⁸ | 1.0×10⁻⁷ | 0 | 1828 | 0.0725530027 |
| j8 | 0.0782622414 (53) | 0.0195428515 | 1.1×10⁻⁷ | 1.7×10⁻⁶ | 0 | 1822 | 0.0814532144 |

Coinciden con el diagnóstico de escape ya publicado: t₀ difiere en ≈ 5×10⁻¹⁰ y A₀ en ≈ 10⁻⁸, y los rayos designados 1776 y 1828 son los esperados. (ii) y V3 cumplen sus tolerancias en los tres casos.

## Causa del fallo: defecto de implementación en la identificación de la cara
En los tres casos el script eligió la cara (j, i | k) = (13, 20 | 6): sobrevivientes 13 y 20, transversal 6. El análisis independiente del agente original (`FRONTERA_CONFIRMACION.md`) identificó, para la misma familia, sobrevivientes **6 y 13** y transversal **20**. En el borde, w6 → 0.064, mientras que w20 → 0.

La regla de v1 tomaba los dos pesos mayores en el último estado (|p| ≈ 150). Ahí w20 todavía supera a w6, porque w6 es pequeño en el límite y w20 aún no ha decaído. Con esa carta, b = w6/w13 no tiende a 0 y la integración en b se atasca («Required step size is less than spacing between numbers»). El protocolo (4.4.1) pide «la arista **hacia la que se dirige** el rayo». La regla de v1 no implementaba eso, y las sintéticas de 3 componentes no podían revelarlo.

## Corrección (script v2)
La cara se decide por la **dirección de avance**: log w_q crece a razón f_q·v. Sobreviven los dos componentes con mayor f·v, y el transversal es el tercero. Se registran las tasas f·v en el resultado para verificarlo. Nada más cambia: ni t₀, ni factores, ni margen, ni tolerancias. Esto no es un reajuste tras ver la cota, porque esta corrida no llegó a calcular ninguna cota.

**Riesgo declarado:** la corrida 2 es un segundo intento sobre los mismos casos. Se declara que este es el único cambio y que, si la corrida 2 falla por cualquier otra razón, el resultado se reporta como no certificado, salvo un nuevo defecto de implementación igual de demostrable, que se documentaría de la misma forma.
