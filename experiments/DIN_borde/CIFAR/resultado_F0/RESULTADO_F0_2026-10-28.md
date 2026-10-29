# DIN-CIFAR F0 — resultado de factibilidad (corrida del 2026-10-28)

**Fuente:** la consola y el `resumen_F0.json` que el responsable corrió en su equipo y pegó en la conversación (el resumen, el 2026-10-29). El archivo original está en `D:\RIPG_DATA\DIN_CIFAR_F0\corrida\`, fuera de Git. Los valores de abajo son una transcripción; no se registra el SHA del archivo original.

**Código:** el de la fusión del PR #124 (commit `0c41b1d5`).
- `instrumento_general.py` `54da1c56…`
- `sistema_cifar3.py` `1da9c33c…`
- `f0_factibilidad.py` `7becf900…`
- versiones fijadas (torch 2.9.1+cpu, numpy 2.3.5, scipy 1.17.0, scikit-learn 1.8.0)

**Configuración:** plan v1 §3–§4, con lr = 0.001 y 250 updates; semillas 1 010 000 / 1 020 000 / 1 030 000.

## Compuerta de equivalencia (oficial, en el equipo del responsable)
**PASA.** Error relativo máximo frente al instrumento congelado: **0.000e+00**. Los 9 controles salieron OK y la corrida tardó 30.2 s.

## F0
- **100 de 100** trayectorias medidas, **0 fallidas**.
- **Reproducción exacta:** sí, en (s0, k0) y (s1, k3).
- `rho_borde_v2` en u250: 100 de 100 con estado `VALID_NUMERICAL_ESTIMATE`. El valor no se guardó.

| visita | mediana de c | cuantiles de c (0, 10, 25, 50, 75, 90 y 100 %) | mediana de q |
|---|---|---|---|
| u5 | 0.0495 | 0.041, 0.044, 0.046, 0.050, 0.055, 0.062, 0.141 | 0.0086 |
| u10 | 0.0533 | 0.042, 0.045, 0.048, 0.053, 0.061, 0.072, 0.104 | 0.0097 |
| u30 | 0.0872 | 0.046, 0.065, 0.074, 0.087, 0.109, 0.141, 0.237 | 0.0122 |
| u250 | 0.2876 | 0.098, 0.150, 0.208, 0.288, 0.389, 0.617, 0.810 | 0.0065 |

| medida (mediana) | valor |
|---|---|
| precisión de entrenamiento en u250 | 0.751 |
| precisión del panel en u250 | 0.556 (15 de 27) |
| precisión de test en u250 | 0.556 |
| CPU por trayectoria | 28.4 s (máximo 31.0 s) |
| tiempo de entrenamiento | 25.5 s |
| geometría por visita | 0.31 s |
| una llamada a ρ en u250 | 0.83 s |
| memoria máxima | **sin medir**: el valor 0.0 se debe a un defecto del medidor de Windows, corregido en la enmienda v2 |

## Regla descriptiva del plan v1 §4
| criterio | resultado |
|---|---|
| mediana de la precisión del panel ≥ 0.55 | cumple (0.556), por un pelo |
| mediana de c250 en [0.30, 0.97] | **no cumple** (0.288) |
| CPU ≤ 60 s por trayectoria | cumple (28.4 s) |
| compuerta y reproducción | cumplen |

## Lectura y decisión
- **El modelo está subentrenado:** la precisión de entrenamiento es de 0.75 en u250, y c sigue subiendo entre u30 y u250 sin estabilizarse. Con 250 updates, el «estado final» es todavía un punto a media trayectoria.
- **Decisión del responsable (2026-10-29):** enmienda v2 del plan con lr = 0.003 y 250 updates, verificada con un F0b de semillas nuevas antes de F1 (ver [PLAN_CIFAR_v2](../PLAN_CIFAR_v2.md)).
- **Sin contaminación:** F0 no midió X10, ρ ni D, así que la decisión se tomó sin ver nada de la señal temprana.
