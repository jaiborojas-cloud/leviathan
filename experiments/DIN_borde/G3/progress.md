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

## Planificación terminada antes de cohorte
Controles FWL/C1 PASS. PrimerN válido=100;potencia.026=.905,.8925,.89;
límites inferiores≥.8555. Nulo=.03,.0175,.025 (pasa control).
Se congela config/SAMPLE antes de crear código de entrenamiento.
1500 entrenamientos nuevos,10500 visitas; no se entrenó aún.

## Cohorte en curso · primer avance conservado
Prepare bajo2048dd4: PASS semillas disjuntas,triángulo,cara26,r3,C1 ygenerador.
Tres reconstrucciones prefijadas de M: error relativo0,f idéntica, sin
reentrenar ni repetir rho. Cohorte iniciada;primeras330 trayectorias sin
errores/invalidaciones. No se calcularon D ni veredictos parciales.
Se versionan controles, entorno ymetadata de generación antes de finalizar
la cohorte; las mediciones siguen con el código de entrenamiento intacto.
