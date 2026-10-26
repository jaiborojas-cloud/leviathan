# DIN-C2: potencia previa a la cohorte

Piloto exclusivo G3 s=0.8 (100×5); código comprometido dd34a6b.
No se ha generado ni entrenado la cohorte C2. Cuatro controles FWL contra C1: PASS.

El **primer tamaño, N=200 splits**, satisface ambas reglas congeladas:

| D_obj | PASS / 400 | tasa | Wilson95 inferior | Wilson95 superior |
|---:|---:|---:|---:|---:|
|0|11|0.0275|0.01542|0.04857|
|0.010|312|0.7800|0.73685|0.81783|
|0.012|347|0.8675|0.83075|0.89725|
|0.015|373|0.9325|0.90357|0.95320|
|0.017|385|0.9625|0.93906|0.97714|

Para .012, inferior≥.8; para 0, superior≤.10. No se probaron N posteriores.
400 réplicas por celda y 1999 permutaciones, con el procedimiento G3.
Potencia condicional al modelo gaussiano y soporte del piloto; no garantía de
potencia real. [Tabla y D_CV finito](results_v1/power_table.csv),
[salidas completas](results_v1/summary.json), [controles](results_v1/controls.json).
Los arrays originales y todos los valores simulados quedan fuera de Git, con SHA
por marco en las salidas. La inferencia de C2 aún no se ha ejecutado.
