# Índice experimental

## Etapas iniciales

La [revisión estática E1–E8](archive/review-before-import/docs/experiment-index.md) conserva población, método y referencias por celda del [notebook](../Perspectivas.ipynb). Sus limitaciones no se resuelven mediante esta organización.

## Fuentes posteriores recuperadas

| Etapa | Alcance documental | Fuente |
|---|---|---|
| E9/E10 | Síntesis y axioma; cierre autónomo E9 pendiente | [Contexto](archive/import-2026-10-17/originals/RIPG_contexto_vigente_axioma.md) |
| E11 | Cierre y paso al campo perspectival | [Cierre](archive/import-2026-10-17/originals/Cierre_E11_RIPG_y_apertura_E12.md) |
| E12 | Campo, conexión, curvatura y holonomía como control | [Cierre](archive/import-2026-10-17/originals/E12E_holonomia_control_derivado_y_cierre_E12.md) |
| E13 | Normalización intrínseca y fallo instrumental que motiva E14 | [Cierre](archive/import-2026-10-17/originals/E13_cierre_y_punto_de_partida_E14.md) |
| E14 | Cierre primario autónomo pendiente | [Faltantes](handoff/missing-sources.md) |
| E15-B6/B7/B8/C1/A2 | Auditorías y cierres, C1-A INCONCLUSIVE | [Índice E15](../experiments/E15/README.md) |
| T1-A/B | Panel histórico y análisis descriptivo a radio común | [Índice T1](../experiments/T1/README.md) |
| T2-A0/A | Diseño prospectivo congelado y seguimiento incompleto | [Índice T2-A](../experiments/T2_A/README.md) |

Consultar los protocolos originales para poblaciones y tolerancias; esta tabla no sustituye sus diseños.

## Fichas de cierre

[Selección mínima por experimento: README, conclusión y evidencia](../experiments/README.md).

## Línea independiente: E16

[E16](../experiments/E16/README.md): cartas, subfamilias, descenso de métricas y
composición escalar. Primera fase analítica EXPECTED_GEOMETRIC_CONTROL;
[conclusión y fallos conservados](../experiments/E16/CONCLUSION.md). No continúa E15/T2.

## E16-B — Red sintética sin entrenamiento

[E16-B](../experiments/E16/B/README.md): identidades y derivadas PASS; validación
independiente del rango INCONCLUSIVE en 81 configuraciones. Estado, scripts y
resultados nuevos separados de T2-A y de los controles analíticos E16.

## E16-D — Réplica instrumental prospectiva

[E16-D](../experiments/E16/D/README.md): pesos, entradas y puntos nuevos sin
entrenamiento; 396/396 decisiones PASS_NUMERICAL y 216/216 negativos detectados.
La suma, producto y cuadrática dieron rango 2 en los 324 casos principales.
No reescribe B/C ni establece una ventaja predictiva.

## E16-E — Distancias y anisotropía

[E16-E](../experiments/E16/E/README.md): 216 comparaciones exploratorias respecto
a la suma. El rango 2 coexiste con cambios de escala y forma; 10 176 controles
numéricos pasan. Distancia entre tensores SPD, no geodésicas entre perspectivas.

## E16-F — Longitudes de caminos

[E16-F](../experiments/E16/F/README.md): 324 longitudes de tres segmentos fijados
bajo suma, producto y cuadrática. 239 PASS_NUMERICAL y 85 INCONCLUSIVE por
integración y/o comprobación global de positividad. No son distancias geodésicas.

## E16-G — Resolución numérica diagnóstica

[E16-G](../experiments/E16/G/README.md): 324/324 longitudes y 216/216 pares
validados con primitiva/cuadratura localizada y cotas Bernstein subdivididas.
Resuelve bajo G los 85 inconclusos F, sin alterar F. No es confirmación
independiente ni certificado intervalar.

## E16-H — Transferencia prospectiva del instrumento

[E16-H](../experiments/E16/H/README.md): pesos, entradas y perspectivas nuevos,
sin selección ni entrenamiento. 324/324 longitudes y 216/216 pares pasan con
el método y tolerancias G intactos. Evidencia de transferencia dentro de la
familia sintética, no de capacidad predictiva ni geodésicas.

## E16-I — Caminos quebrados acotados

[E16-I](../experiments/E16/I/README.md): 27 casos validados; 18/18 caminos
no lineales más cortos que sus rectas, nueve controles de suma sin mejora.
Búsqueda de un punto intermedio acotado, sin certificado de mínimo global.

## E16-J — Refinamiento y estacionariedad discreta

[E16-J](../experiments/E16/J/README.md): 2/4/8 puntos interiores, tres reinicios
y controles de gradiente. Estado global INCONCLUSIVE: 24/27 casos pasan, tres
no. 22 interiores estables discretamente (incluyen nueve controles), dos
limitados por frontera y tres no resueltos; no se certifican geodésicas.
