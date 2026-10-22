# NEM3 — Conclusiones y límites

Estado: COMPLETADO (run_v1). Resultado: exploratorio, no confirmatorio.

## Configuración

- Modelo lineal de regresión logística (3 features, 2 clases, 8 parámetros) sin entrenamiento.
- Familia no lineal de perspectivas (softmax de rasgos fijos, forma E12), m=2.
- Grid: 9×9 puntos en p = (p^1, p^2) ∈ [-1, 1]^2.
- Diferencias finitas: ε = 1e-5.
- Perturbación del panel: ε = 0.2.
- Implementación: Python puro, sin dependencias externas.

## Resultados

### Panel base

| Observable | Valor |
|---|---|
| Área A | 6.44e-01 |
| Energía total E | 1.59e+02 |
| Energía media E_K | 2.47e+02 |
| C_A = sqrt(E_K) | 1.57e+01 |
| R_eff | 1.77e-02 |
| Lambda_0.25 | 0.9893 |
| Lambda_0.50 | 0.9984 |
| Lambda_0.75 | 0.9997 |

### Panel perturbado (ε = 0.2)

| Observable | Valor | Cambio relativo |
|---|---|---|
| Área A | 5.78e-01 | -1.0e-01 |
| Energía media E_K | 3.56e+04 | +1.4e+02 |
| C_A = sqrt(E_K) | 1.89e+02 | +1.1e+01 |
| R_eff | 1.49e-04 | -9.9e-01 |
| Lambda_q | ≈ 1.0 | ≈ 1.0 |

## Interpretación

1. **Energía curvatural**: La energía media E_K y C_A aumentan drásticamente bajo perturbación del panel (×144 en E_K, ×12 en C_A). La métrica de perspectivas se vuelve mucho más curvada cuando el panel cambia.

2. **Participación efectiva**: R_eff cae de 1.77e-02 a 1.49e-04 (~-99%), indicando que la energía curvatural se concentra en una fracción mucho menor del dominio después de la perturbación.

3. **Concentración espacial**: Lambda_q ya es muy alto en el panel base (≥0.989 para q=0.25), lo que indica que casi toda la energía curvatural está concentrada en una pequeña subregión incluso antes de la perturbación. Después de la perturbación, la concentración se acerca a 1.0.

4. **Reproducibilidad**: La reproducción byte a byte pasa en verify.py.

## Límites

- Modelo lineal muy pequeño; no se extrapola a redes reales.
- Diferencias finitas con ε = 1e-5 pueden introducir error numérico.
- Grid de 9×9 es limitada para caracterizar integrales sobre el dominio.
- Lambda_q ya saturado en el panel base dificulta observar cambios por perturbación.
- No se modificaron resultados congelados de T2-A, E16, NEM1, NEM2 ni otros experimentos.
- Resultado independiente de Nemotron; no sustituye evidencia oficial del marco RIPG.
