# NEM3 run_v3_collinear — Conclusiones y límites

Estado: COMPLETADO (run_v1). Resultado: exploratorio, no confirmatorio.

## Configuración

- Modelo lineal de regresión logística (5 features, 3 clases, 17 parámetros) sin entrenamiento.
- Dataset sintético con colinearidad: x2 = 0.95*x1 + ruido, x3 = 0.90*x1 + 0.50*x2 + ruido.
- Familia no lineal de perspectivas (softmax de rasgos fijos, m=2).
- Grid: 9×9 puntos en p = (p^1, p^2) ∈ [-1, 1]².
- Diferencias finitas: ε = 1e-5.
- Perturbación del panel: ε = 0.2.
- Umbral modo débil: tau = 1e-6.
- Implementación: Python puro, sin dependencias externas.

## Resultados

### Fisher y modos débiles

| Métrica | Panel base | Panel perturbado |
|---|---|---|
| max eigenvalue | 2.20e+00 | 2.28e+00 |
| min eigenvalue | 2.55e-06 | 3.65e-06 |
| n_weak_modes (tau=1e-6) | 0 | 0 |

El autovalor mínimo de Fisher es 2.55e-06, aproximadamente 7000× menor que en run_v1 (Wine, 1.81e-02). Esto confirma que la colinearidad induce direcciones casi-nulas en Fisher, aunque estén justo por encima del umbral tau=1e-6.

### Observables geométricos

| Observable | Panel base | Panel perturbado | Cambio relativo |
|---|---|---|---|
| C_A = sqrt(E_K) | 2.43e+00 | 2.41e+00 | -8.3e-03 |
| R_eff | 1.96e-02 | 2.11e-02 | +7.9e-02 |
| Lambda_0.25 | 0.9976 | ~1.0 | ~1.0 |
| Lambda_0.50 | 0.9999 | ~1.0 | ~1.0 |
| Lambda_0.75 | 1.0 | ~1.0 | ~1.0 |

## Interpretación

1. **Estabilidad bajo perturbación**: A diferencia de run_v1 (donde C_A aumentaba ×12 y R_eff caía 99% bajo perturbación), en run_v3_collinear los observables geométricos son casi invariantes (cambio < 10% en todos los casos). Esto sugiere que los modos débiles de Fisher (direcciones casi-nulas) amortiguan la respuesta de la geometría de perspectivas ante perturbaciones del panel.

2. **Concentración de curvatura**: Lambda_q ya está saturado (≥0.9976 para q=0.25) en el panel base, indicando que la energía curvatural está concentrada en una fracción muy pequeña del dominio incluso antes de la perturbación.

3. **Comparación run_v1 vs run_v3**: La colinearidad cambia cualitativamente el comportamiento: de un sistema altamente sensible (run_v1) a uno muy estable (run_v3_collinear).

## Límites

- Modelo lineal muy pequeño; no se extrapola a redes reales.
- Los autovalores mínimos (2.55e-06, 3.65e-06) están justo por encima del umbral tau=1e-6; un tau más pequeño detectaría modos débiles.
- Grid de 9×9 limitada para caracterizar integrales.
- No se modificaron resultados congelados de otros experimentos.
- Resultado independiente de Nemotron; no sustituye evidencia oficial del marco RIPG.
