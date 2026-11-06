# Q15: cambios v1 → v2 para la segunda auditoría

**2026-11-02. BORRADOR, sin autorización de búsquedas todavía.**

La v1 del commit `cbdba97865ed94917bb5ed0430db8b7bd92ebc62` y sus 18 entradas de manifiesto permanecen idénticas. Esta v2 responde a la auditoría de Claude trasladada por el responsable. No es una revisión de resultados; no se ejecutaron búsquedas, lectura primaria ni experimentos.

| Observación | Cambio v2 | Ubicación |
|---|---|---|
| Recuperación/cribado ilimitados inviables | N=500 resultados por consulta; si >500, primeros K=200 en orden fijo; sondeo acotado cuando no hay total; TRUNCADA_DECLARADA | Protocolo §4.1, LIMITES_v2.json, plan_busquedas_v2.csv |
| Anclas con miles de citas | Umbral >500; filtro OR DIN sobre título/resumen; campos ausentes quedan pendientes. Ruta con filtro nativo o, si no existe, primeras 200 posiciones antes del filtro local, declarado explícitamente | Protocolo §5.1 |
| Falta de extrapolación/predicción temprana del rendimiento | T08–T10 | consultas_v2.csv |
| Falta de sesgo implícito CE y crecimiento de norma/margen | L12–L15 | consultas_v2.csv |
| Falta de NTK y Fisher empírica frente a modelo | G11–G14 | consultas_v2.csv |
| No ocultar alcance reducido | «Nuevo» solo dentro de búsqueda acotada; informe por punto de truncamientos y riesgo de omisión; huecos críticos siguen PENDIENTE | Protocolo §8 y plantillas_v2 |

## Consultas añadidas

| ID | Punto | Expresión lógica exacta |
|---|---|---|
| T08 | 2: (a) Extrapolación de curvas | `("learning curve extrapolation" OR "learning curve prediction") AND ("neural network" OR "deep learning")` |
| T09 | 2: (a) Predicción final desde el inicio | `("early performance prediction" OR "predicting final performance" OR "predicting final accuracy") AND ("learning curve" OR "training")` |
| T10 | 2: (a) Curvas y parada temprana | `"learning curves" AND ("extrapolation" OR "performance prediction" OR "early stopping")` |
| L12 | 4: (b) Sesgo implícito de CE | `"implicit bias" AND ("cross entropy" OR "cross-entropy" OR "logistic loss")` |
| L13 | 4: (b) Margen máximo | `("max margin" OR "maximum margin" OR "max-margin") AND ("logit" OR "logits" OR "gradient descent")` |
| L14 | 4: (b) Norma divergente y separabilidad | `"separable" AND ("logistic regression" OR "cross entropy" OR "cross-entropy") AND ("gradient descent" OR "norm" OR "implicit bias")` |
| L15 | 4: (b) Crecimiento de logits | `("logit norm" OR "logit norms" OR "logit growth") AND ("cross entropy" OR "cross-entropy" OR "margin")` |
| G11 | 3: (c) NTK frente a kernels Fisher | `("neural tangent kernel" OR "NTK") AND ("Fisher" OR "gradient kernel")` |
| G12 | 3: (c) Fisher empírica y limitaciones | `"empirical Fisher" AND ("natural gradient" OR "limitations" OR "neural network")` |
| G13 | 3: (c) Fisher del modelo frente a empírica | `("true Fisher" OR "expected Fisher" OR "model Fisher") AND ("empirical Fisher" OR "neural network")` |
| G14 | 3: (c) Gauss–Newton, Fisher y NTK | `("generalized Gauss-Newton" OR "generalised Gauss-Newton" OR "Gauss Newton") AND ("Fisher" OR "neural tangent")` |

## Conteos planificados, no resultados de búsqueda

| Versión | Temáticas | Resolución | Consultas | Combinaciones | Obligatorias | Scholar opcionales |
|---|---|---|---|---|---|---|
| v1 | 32 | 12 | 44 | 228 | 184 | 44 |
| v2 | 43 | 12 | 55 | 294 | 239 | 55 |

Son 66 combinaciones nuevas (11 × 6). Las cadenas previas y las 16 candidatas heredadas no cambian; no se añaden referencias presuntamente verificadas para cubrir los temas nuevos. No se modifica el corte, las preguntas ni el diccionario de objetos.

Los cupos se aplican por combinación, antes de deduplicación y postfiltros. No se repone un cupo vacío ni se aumenta K tras observar las conclusiones. Un caso con >500 citas y sin filtro nativo queda doblemente acotado por orden y filtro local; no se presenta como recuperación de todos los citantes DIN. Esto hace factible la ejecución a cambio de cobertura explícitamente menor.

El README original y ESTADO_PROTOCOLO.json describen v1 y se preservan por integridad de su manifiesto. Las entradas vigentes propuestas son README_v2.md, ESTADO_PROTOCOLO_v2.json y PROTOCOLO_BORRADOR_v2.md; la v2 sigue pendiente de revisión de Claude.
