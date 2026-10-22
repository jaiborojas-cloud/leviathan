# NEM2 — Conclusiones y límites

Estado: COMPLETADO (run_v1). Resultado: exploratorio, no confirmatorio.

## Configuración

- Modelo lineal de regresión logística (3 features, 2 clases, 8 parámetros) sin entrenamiento.
- Familia no lineal de perspectivas (softmax de rasgos fijos, forma E12), m=2.
- Grid: 9×9 puntos en p = (p^1, p^2) ∈ [-1, 1]^2.
- Diferencias finitas: ε = 1e-5.
- Holonomía: lazos cuadrados con δ ∈ {0.1, 0.2}, 20 pasos de transporte.
- Implementación: Python puro, sin dependencias externas.

## Resultados

| Métrica | Valor |
|---|---|
| Puntos evaluados | 81 |
| Puntos SPD (det h > 1e-12) | 81/81 |
| Rango de curvatura K | [-2.34e+02, 4.42e+01] |
| Holonomía calculada | 6/6 casos |
| Reproducción byte a byte | OK |

## Interpretación

La curvatura de Gauss K varía significativamente sobre el espacio de perspectivas, tomando tanto valores positivos como negativos. Esto indica que la geometría de perspectivas inducida por la familia no lineal no es plana: la métrica h = B C B^T tiene curvatura no trivial que depende de p.

La holonomía se pudo calcular en todos los casos probados. Los valores de θ_hol no nulos indican que el transporte paralelo alrededor de lazos pequeños produce rotación, consistente con un espacio de perspectivas curvo.

No se puede afirmar una ley universal sobre el signo o magnitud de la curvatura a partir de esta única configuración pequeña. Los resultados son exploratorios.

## Límites

- Modelo lineal muy pequeño; no se extrapola a redes reales.
- Diferencias finitas con ε = 1e-5 pueden introducir error numérico en derivadas de orden superior.
- Grid de 9×9 es limitada para caracterizar la curvatura globalmente.
- No se modificaron resultados congelados de T2-A, E16, NEM1 u otros experimentos.
- Resultado independiente de Nemotron; no sustituye evidencia oficial del marco RIPG.
