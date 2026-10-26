# DIN-D9g: lectura previa al diseño

Leídos AGENTS.md, el plan D9 completo, el cierre C2 congelado y G3/CONCLUSION.md.
Main al inicio: 0dbc973. El plan D9 y cierre congelado aún no están en main;
se consultaron en claude/din-d9 y se conservan por commit/SHA en sources/.
No se abrió la cohorte C2 ni sus resultados tabulares/estados/checkpoints.

G3 contiene 100 splits × 5 inicializaciones × 3 niveles, con 7 visitas. El inventario
externo tiene los 7.500 checkpoints requeridos de u10/20/30/50/250 presentes.
Se leyó código de G3 y del estimando C1, y sólo cabeceras de sus tablas para conocer
la estructura. No se cargaron pesos ni se calculó test o asociación D9g.

El generador usa 117 puntos por split; 30/clase train y 9/clase panel. Estandariza
con media/escala train guardadas. La red 13→64→32→3 (ReLU, double) no tiene dropout.
Los checkpoints tienen weight_l1/l2/l3.weight/bias, Adam y RNG. Se reutilizan M y
rho_caras r3 ya medidos en G3; no hay reentrenamiento ni nueva medición de rho.

El plan D9 y la tarea dicen 12 candidatos, pero enumeran 9+2=11. Se preguntó al
responsable. En ausencia de otra preferencia se conservarán los 11 enumerados y
el divisor Bonferroni 12, sin añadir un candidato ni elegirlo después de mirar test.
Delta10→20 se condicionará a la base barata u20 y Delta20→30 a u30.
