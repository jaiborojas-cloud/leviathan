# NEM1 — Conclusiones y límites

Estado: COMPLETADO (run_v1 y run_v2_wine). Resultado: exploratorio, no confirmatorio.

## Configuración

- Modelo lineal (regresión logística multiclase) sin entrenamiento.
- Cométrica C: identidad.
- Perturbación del panel: epsilon en [0, 0.2] (11 pasos).
- Umbral de modos débiles de Fisher: tau = 1e-6.
- Implementación: Python puro, sin dependencias externas.

## Resultados

### run_v1 — sintético (4 features, 3 clases, 15 parámetros, 20 entradas)

| Métrica | epsilon = 0 | epsilon = 0.2 | Tendencia |
|---|---|---|---|
| delta_h (Frobenius) | 0.0 | 7.79e-02 | Crecimiento approx. lineal |
| spd_distance(h0, h_eps) | 0.0 | ~2.7e-01 | Decrecimiento leve |
| Modos débiles de Fisher | 0 | 0 | Sin modos débiles |
| Proyección sobre modos débiles | 0.0 | 0.0 | N/A |

### run_v2_wine — dataset Wine de UCI (13 features, 3 clases, 42 parámetros, 178 entradas)

| Métrica | epsilon = 0 | epsilon = 0.2 | Tendencia |
|---|---|---|---|
| delta_h (Frobenius) | 0.0 | 4.71e-02 | Crecimiento approx. lineal |
| spd_distance(h0, h_eps) | 0.0 | ~2.5e-01 | Decrecimiento leve |
| Modos débiles de Fisher | 0 | 0 | Sin modos débiles |
| Proyección sobre modos débiles | 0.0 | 0.0 | N/A |

## Interpretación

La métrica de perspectivas $h = B C B^T$ varía de forma continua y aproximadamente lineal con la perturbación del panel $\mu$, tanto en datos sintéticos como en el dataset Wine real. La magnitud observada (delta_h ~ 4.7e-02 a 7.8e-02 para una perturbación del 20% del panel) sugiere sensibilidad moderada de la métrica de perspectivas al panel de evaluación.

No se detectaron modos débiles de Fisher en ninguna de las dos configuraciones (el autovalor mínimo de Fisher se mantuvo por encima de tau = 1e-6), por lo que el efecto de perturbaciones cercanas al kernel de Fisher no fue probado en esta corrida.

## Límites

- Análisis exploratorio, no confirmatorio. No se adopta como ley.
- Modelo lineal muy pequeño; no se extrapola a redes reales profundas.
- No se detectaron modos débiles de Fisher; no se probó el régimen cerca del kernel.
- La aproximación $B(\mu_\epsilon) = B_0 + \epsilon \cdot \delta B$ es simplificada; no sustituye una derivación exacta de $dB/d\mu$.
- No se modificaron resultados congelados de T2-A, E16 u otros experimentos.
- Resultado independiente de Nemotron; no sustituye evidencia oficial del marco RIPG.
- Verificación: reproducción byte a byte pasada en ambos runs (verify.py).
