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

## Segundo avance · cohorte por encima de la mitad
804/1500 trayectorias completas, cero errores e invalidaciones acumuladas.
No se calculan D, V_cont ni veredictos por anticipado. Continúa el universo
original; sin cambios de código, semillas, presupuesto o selección de casos.

## Cohorte cerrada sin selección
1500 entrenamientos,10500 visitas completas, cero errores e invalidaciones.
Tiempo2849.66s,CPU2/BLAS1. Sin parada temprana ni extensión de presupuesto.
No se usaron estados ni inicializaciones G2 como datos G3; sólo piloto de potencia.

## Análisis prefijado
Todas las compuertas500/500 y100/100. s=.25:NOT_MET,D=.00019082,p=.1655;
s=.5:NOT_MET,D=.00272154,p=.0895; s=.8:PASS_DESCRIPTIVO,D=.01734778,
p=.003,beta=1.37323. Sólo.8 cumple colapso operacional por medianas
(c=.864214,q=.000104165),con290/500(58%) colapsados individualmente.
Veredicto global SENAL_PRESENTE_FUERA_DE_WINE_DESCRIPTIVA en este sintético;
no confirmatorio, sin corrección por tres niveles ni transferencia a datos reales.
V_cont=1.115638,.698187,.099995; Spearman(D,V_cont)=−1 con sólo3 puntos;
no establece dependencia entre varios regímenes igualmente colapsados.
D_X|R en.8=.00254397,razón descriptiva.85335,sin mediación causal.
rho_vert secundario D=.01727239,p=.0055; W legado.069,p=.085.
La lectura editorial añadida a CONCLUSION no cambia números,reglas o estados.

## Integridad y archivo
verification PASS:10500 registros,1500 trayectorias,31912 archivos externos
conSHA;500 grupos de pesos iniciales y3500 de lotes emparejados,300 paneles.
Fuentes originales y configuración del tamaño intactas;cronología verificada.
Archivo reversible10500/10500 bit a bit, originales conservados; matrices,
pesos, scores, RNG/Adam, rho completo y MonteCarlo fuera de Git conSHA.
Figura inspeccionada, sin avisos de caché. Consolas/resultados conservados.
La publicación push+PR borrador está autorizada por el usuario; no se fusiona.
