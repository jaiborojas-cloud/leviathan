# DIN-CIFAR F0b — resultado de verificación de la enmienda v2 (2026-10-29)

**Fuente:** la consola que el responsable corrió en su equipo y pegó en la conversación el 2026-10-29. Los valores de abajo son una transcripción. Los archivos originales están en `D:\RIPG_DATA\DIN_CIFAR_F0\corrida_F0b\`, fuera de Git.

**Configuración:** [plan v2](../PLAN_CIFAR_v2.md), con lr = 0.003, 250 updates y semillas 1 040 000 / 1 050 000 / 1 060 000. El código es el de la fusión del PR #125.

## Resultados
- **100 de 100** trayectorias medidas, **0 fallidas**, y reproducción exacta.
- **Memoria:** se midió en las 100 trayectorias (la corrección de Windows funciona). Mediana de 707 MB por proceso y máximo de 735 MB, así que con 12 procesos son unos 8.5 GB.

| medida (mediana) | F0 (lr 0.001) | F0b (lr 0.003) |
|---|---|---|
| precisión de entrenamiento en u250 | 0.751 | **0.912** |
| precisión del panel en u250 | 0.556 | 0.556 |
| precisión de test en u250 | 0.556 | 0.556 |
| c en u5 / u10 / u30 / u250 | 0.050 / 0.053 / 0.087 / 0.288 | 0.052 / 0.057 / 0.122 / **0.561** |
| CPU por trayectoria | 28.4 s | 36.3 s |

**Cuantiles de c250 en F0b** (0, 10, 25, 50, 75, 90 y 100 %): 0.151, 0.323, 0.434, 0.561, 0.783, 0.884, 0.981.

## Criterios del plan v2 §3 (fijados antes de correr)
| criterio | resultado |
|---|---|
| mediana de la precisión de entrenamiento ≥ 0.90 | cumple (0.912) |
| mediana de la precisión del panel ≥ 0.55 | cumple (0.556) |
| mediana de c250 en [0.30, 0.97] | cumple (0.561) |
| CPU ≤ 60 s por trayectoria | cumple (36.3 s) |
| compuerta y reproducción | cumplen |

**Cumple todos los criterios.** No hace falta F0c. La configuración para F1 es la del plan v2 (lr = 0.003). El paso a F1 lo decide el responsable.

## Notas descriptivas (no son criterios)
- **La generalización no mejoró:** el panel y el test siguen en 0.556, mientras el entrenamiento llega a 0.91. La brecha es grande, como cabe esperar con 900 imágenes y clases que se confunden entre sí.
- **c250 tiene una dispersión amplia,** de 0.15 a 0.98. Algunas trayectorias quedan muy concentradas: el 10 % superior pasa de 0.88.
- **Costo estimado de F1** (500 trayectorias, 12 procesos): unos 25 min, con unos 8.5 GB de memoria.
