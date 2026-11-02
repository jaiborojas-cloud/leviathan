# Cierre de la rama DIN-CIFAR-3 (2026-11-02)

**Decisión del responsable (2026-11-02, 10:31):** «adoptar la primaria robusta y cerrar CIFAR-3».

## Estado final
- **F1 (descubrimiento):** el veredicto congelado, **PASS_DESCRIPTIVO** (D = 0.460, p = 0.0002), se conserva sin reclasificar ni excluir trayectorias. Ver el [resultado](F1/resultado/RESULTADO_F1_2026-10-29.md).
- **Lectura:** el PASS lo produce casi entero una trayectoria que no aprendió (`cifar_f1_s0009_k0`), por palanca de la base cúbica. En la [revisión exploratoria de la primaria](../revision_primaria/REVISION_PRIMARIA_2026-10-29.md), con bases robustas D baja a 0.009–0.015. Sin esa trayectoria queda en 0.004–0.008, con p entre 0.025 y 0.068, y una sola observación aporta todavía del 31 al 49 % de la mejora.
- **Conclusión de la rama:** **en CIFAR-3, con esta CNN, no se detecta de forma robusta la señal temprana en descubrimiento.** El efecto residual es pequeño (alrededor de una cuarta parte del D de Wine) y frágil. Esto **no** demuestra que la señal esté ausente, porque no hubo un confirmatorio con potencia para un D tan chico.
- **No se hace F2.** La reserva de semillas de F2 (1 200 000 / 1 300 000 / 1 400 000) queda sin usar y sigue reservada; no se reasigna.

## Qué deja la rama
1. **El instrumento generalizado y su compuerta,** que PASA con error 0 frente al core congelado: sirven para cualquier red de cuerpo más cabeza de 3 clases.
2. **El productor y el analista de CIFAR,** reutilizables.
3. **La lección de método,** que llevó a adoptar la [primaria robusta](../PRIMARIA_ROBUSTA_v1.md) para los diseños nuevos.
4. **Datos:** la tabla de F1 está publicada con su SHA. Los arrays, pesos y resultados de ρ completos quedan en `D:\RIPG_DATA\DIN_CIFAR_F0\` y `D:\RIPG_DATA\DIN_CIFAR_F1\`, fuera de Git; no se borran.

## Lo que queda abierto
- Si la señal aparece en arquitecturas o datos estándar, que es la parte (c) de la Q15, sigue abierto. CIFAR-3 aporta un descubrimiento sin señal robusta, no una ausencia demostrada.
- Una nueva familia, si se elige, se diseña desde el principio con la primaria robusta.
