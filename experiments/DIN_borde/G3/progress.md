# DIN-G3 · registro prospectivo

## Fase0

AGENTS raíz leído; main091f153. G2 no está en main: se extraen sólo código,
documentación y tablas piloto de0d28bf1,PR85, como snapshots conSHA en G3.
No se cargaron matrices/checkpoints G2 ni datos Wine/Iris/T2/DIN-C1.
Los escalares G2 sirven sólo a la planificación de potencia; no son G3.

Se reconoce selección posterior de niveles. Las medianas c de G2 (.606,.741,
.866) no permiten asumir colapso estricto en los tres; se congela umbral
operacional c≥.8,q≤.05 sobre medianas, sin filtrar individuos posteriormente.

Este commit precede a código/ejecución de potencia y a toda cohorte nueva.
El tamaño se congelará en otro commit, por la regla de planificación YA fijada,
antes de crear código de entrenamiento y antes de entrenar.
