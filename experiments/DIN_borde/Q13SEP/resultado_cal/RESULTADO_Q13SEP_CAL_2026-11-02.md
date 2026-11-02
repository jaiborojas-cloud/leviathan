# DIN-Q13-SEP v2 — resultado de la calibración (2026-11-02)

**Decisión oficial (regla congelada): NO_IDENTIFICABLE, motivo CALIBRACION_SIN_DOSIS.** Ninguna de las cuatro dosis de LP logró una orientación apta para **E** y otra para **C** en al menos 8 de 10 splits. Según el [diseño congelado](../../DISENO_DIN_Q13SEP_v2_CONGELADO.md), **no se entrena la validación y esta vía se detiene**. Tampoco se cambian dosis, temperaturas ni umbrales después de ver el resultado.

## Corrida e integridad
- Corrida en el equipo del responsable: Windows 11, Python 3.12.10 y las versiones fijadas, con `permitir_versiones = false`. Usó 12 procesos y tardó 123 s.
- **Fuentes por SHA:**
  - configuración congelada `e8074d50…`;
  - productor `f6ba5faf…` y analista `da66def7…`, los dos publicados antes de medir (PR #135).
- **Estados:** 13 700 de 13 700 medidas MEDIDA.
- **Calidad:** 50/50 unidades completas y 10/10 splits con al menos 3 completas.
- **Controles oficiales:** OK. Las tres reconstrucciones dan error 0 y el contraste de rutas T1 da error 0.
- **Prueba corta previa:** 822/822 medidas. La proyección de las dos fases fue de 11 min.

| archivo | SHA-256 |
|---|---|
| tabla `q13sep_medidas_v2.csv` (fuera de Git, en `D:\RIPG_DATA\DIN_Q13SEP\cal\`) | `94c842c87d2e6b0eadf41284dfa899f75cb562b5e4ade6764f9b20e962ea4e08` |
| [DOSIS_Y_REGLAS_Q13SEP_v2.json](DOSIS_Y_REGLAS_Q13SEP_v2.json) | `9b89150e443c342aae10be3c1fa7caef33ebc787c2db3531f3936fd68d8aae3e` |
| [q13sep_emparejamientos_v2.csv](q13sep_emparejamientos_v2.csv) | `715fa95086eebc989c6ee167601bc1d6c283c4ec8d3a6f7459208fc41dee2b23` |
| [controles.json](controles.json) | `8970df120705bca516a461e11844b456ca51641f1089ff9c5a9c817320268310` |
| [RESUMEN_Q13SEP.json](RESUMEN_Q13SEP.json) | `a84647541e53859d13e12db2dfcb37aecfa4d81cff04a4ce23f7c12cf1f0dd9e` |

## Splits que pasan cada pregunta en u250 (se necesitan 8/10)
| dosis | E, σ = +1 | E, σ = −1 | C, σ = +1 | C, σ = −1 |
|---|---|---|---|---|
| LP01 (λ = 0.0001) | 0 | 1 | 2 | 0 |
| LP02 (0.0003) | 0 | 2 | 4 | 1 |
| LP03 (0.001) | 0 | 1 | **5** | 0 |
| LP04 (0.003) | 0 | **3** | 2 | 0 |

## Lectura descriptiva (exploratoria, posterior; no cambia la decisión)
Las cifras salen de las filas u250 de la [tabla de emparejamientos](q13sep_emparejamientos_v2.csv), con 50 unidades por dosis.

- **E, escala igualada con T\*:**
  - LP siempre necesitó afilarse para alcanzar la escala de A0: la mediana de T\* va de 0.34 a 0.60.
  - Con la escala igualada, la **mediana** de Δc = c_A0 − c_LP(T\*) es **casi 0** en las cuatro dosis (−0.040 a −0.002). Las diferencias por unidad son grandes, pero **simétricas**: los percentiles 10 y 90 rondan −0.36 y +0.22 a +0.31.
  - **No hay una dirección consistente:** una vez igualada la escala, LP no cambia la concentración de forma sistemática.
- **C, concentración igualada:**
  - entre 38 y 44 de las 50 unidades encuentran una temperatura con |Δc| ≤ 0.05;
  - en esa temperatura, la razón de escalas tiene una mediana de **1.11 a 1.22**, lejos del factor 1.5 exigido. Igualar c iguala también, en buena medida, la escala.
- **Lectura conjunta:** en esta familia, y con LP más temperatura, **la concentración c y la escala de los logits se mueven casi juntas**, como si c fuera aproximadamente una función de la escala. Por eso el diseño no las pudo separar. Es coherente con [E-escala](../../E_escala/RESULTADO_E_escala_2026-10-28.md), donde tampoco se separaron (correlación de 0.97 entre niveles).
- **Heterogeneidad:** los splits 7 y 9 casi nunca pasan ninguna pregunta.

## Qué significa y qué no
- **Sí:** con este manipulador (LP a 4 dosis, emparejamiento por temperatura) y estos umbrales, concentración y escala **no se pudieron mover por separado** de forma reproducible.
- **No:** no demuestra que sean inseparables en general, ni dice nada sobre la señal temprana, porque X, ρ y D no se midieron. Que la mediana de Δc salga casi 0 con la escala igualada **sugiere**, sin confirmarlo, que el efecto de LP sobre c pasa por la escala.
- La pregunta de la Q13 (si lo que modula la señal es la concentración o la escala) **sigue abierta**. Para separarlas haría falta un manipulador que mueva c a escala constante por construcción, por ejemplo una intervención sobre la geometría y no sobre los logits. Eso sería un diseño nuevo.
- La reserva de semillas de validación (72 millones) y la de señal (73 millones) quedan sin usar.
