# E16-AC · Índice de Morse por campos de Jacobi

Doce finales AB, sin seleccionar por KKT o testigos. Shooting continuo con la
métrica exacta de la composición, Gauss analítica, Jacobi normal y contraste
MP50/80. [Síntesis S–AB](../SINTESIS_S_AB.md).

- [Fase0 antes de diseñar](progress.md).
- [Diseño v1](DESIGN_FROZEN.md), [enmienda v2](DESIGN_FROZEN_v2.md),
  [defecto y conservación v1](progress_v1.md).
- [Teoría y límites](THEORY.md), [conclusión](CONCLUSION.md).
- [Resultados v1 inválidos](results/run_v1), [resultados v2](results/run_v2).

Los bloques normales y la tangencialidad de los testigos no se archivaron en
Z/AB: quedan UNKNOWN. Los bloques T pertenecen a S y no se trasladan a AB.
Índice0 sin esos comparandos no satisface la regla H2 solicitada.

## Ejecución

Python3.12, [dependencias](requirements.txt). Desde la raíz:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/AC/scripts/run_v2.py --out /tmp/e16-ac-nuevo
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/AC/scripts/verify.py
```

El runner rechaza sobrescribir un directorio existente. El verificador comprueba
congelación y hashes, fuentes, alcance exclusivo E16 y estados, y realiza una
repetición exacta de v2 excluyendo tiempos. No reejecuta las etapas S–AB ni v1.
Cada versión conserva su código, diseño, manifest y resultados.

Estado final: INCONCLUSIVE; v2 válida con12 índices0 y8/8 controles PASS.
[Reproducción exacta de diez salidas](verification.json).
