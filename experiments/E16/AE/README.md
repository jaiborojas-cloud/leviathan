# E16-AE · familia no plana sobre E16 sin entrenamiento

Familia softmax de rasgos fijos, m=2, forma E12-B/C; red2→2→1 y Fisher+.01I
de E16. [Cierre documental S–AD](../SINTESIS_S_AD.md).

- [Congelación inicial de fase0](DESIGN_FROZEN.md) antes del primer código.
- [Congelación principal](DESIGN_FROZEN_MAIN.md) después de fase0 y antes de geodésicas.
- [Preparación y selección](progress.md), [teoría](THEORY.md).
- [Resultados de geometría](results/phase0_v1), [resultados principales v1](results/main_v1).
- [Conclusión](CONCLUSION.md).

La región y el centro no se ajustan a eventos observados. La censura se conserva
separada de conjugados/colisiones; sin conjugado observado no se sustituye la
pregunta por otro extremo que aparente estar más allá de él.

Los runners rechazan sobrescribir directorios existentes. Instalar las versiones
de [requirements.txt](requirements.txt), y usar BLAS/OMP de un hilo. El protocolo
principal y la geometría se versionan por separado. La corrección del puente
será derivada de perfiles archivados, sin repetir ni reemplazar rayos v1.

Corrección derivada: [diseño v2](DESIGN_FROZEN_BRIDGE_v2.md),
[resultados del puente](results/bridge_v2). V1 permanece intacta.
Q1/Q2/Q3: INCONCLUSIVE por falta de aplicabilidad/eventos y censura.
