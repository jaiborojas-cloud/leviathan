# Potencia M2 N320: procedimiento previo a código y simulación

Decisión del responsable09:23,opciónB,N320 y eventual ejecución de cohorte en su PC Windows. Aquí solo se prepara potencia: no plan ni cohorte. El diseño sigue en PR#114,commit66f5de58; no se modifica. Se congela este procedimiento de simulación, no el confirmatorio.

Se conserva íntegra la preparación N200 de la carpeta padre. Solo se añaden archivos en N320_v1/. Analista SHA2e69516e…,fuentes completas y SHA en sources/provenance.json. La comparación AST confirma que respecto del analista anterior solo cambian docstring y N_MAX218→320. Se vuelve a contrastar el motor con este analista en controles exclusivamente sintéticos.

## Único cambio de tamaño

N320 fijo. Misma generadora autorizada max(0,−.038434071244996953+.077c),mismos11niveles,c,amplitudes por método Q13DR,pilotoG3s=.8 por SHA,400 réplicas por rho en4 marcos×100,rhos0/.3/.6/.615,bootstrap500,IC97.5(cuantiles.0125/.9875),1999 permutaciones C1. A0 único,remuestreos compartidos LP/WD,conjunta contada directamente. Misma metodología del procedimiento N200 en la carpeta padre,que se preserva.

Semillas: se conserva la fórmula SeedSequence([412000,2,N,marco]) para covariables y[413000,2,N,marco] para normales; aquí N=320. No se mantienen índices N=200 dentro de una simulación N320. Bootstrap960001,permutaciones260001,bloques260010 y controles954000/954001 sin cambios. Se usa el mismo ruido base entre escenarios rho de este N. No se buscan semillas nuevas ni otroN.

La truncación solo afecta objetivos LP5/WD5; no se recortan D estimados. LP4/WD4 en c=.50 siguen positivos,casi0. Pendientes MCO efectivas de objetivos inalteradas:LP.06495278262015627,WD.0699508052937943. El rango de WD es menor; no se presupone una menor pendiente o potencia en todas las sensibilidades.

## Verificación y regla

Controles completos del analista,N20/N40,B1999/NB500: mismos p y etiquetas individuales/conjuntas; D,réplicas e IC coinciden≤1e−10. Se mantiene la prueba de réplica con bloque original. Verificación independiente MCO de archivos,draws960001,11niveles únicos y conjunta por intersección. El cambio del analista se verifica estructuralmente y por SHA; no se usa tabla de cohorte real.

Rho0 decide: Wilson95 inferior≥.8 para cada manipulador. La conjunta se reporta sin exigirse. Si no cumple con320,se publica y se detiene; no se prueba otroN. Si cumple,tampoco se genera plan ni cohorte en esta tarea. Registrar inconclusas,fallos y todos los marcos sin sustituir o redibujar.

Código+push antes de simular. Dos procesos de un hiloBLAS,arrays externos exclusivos y SHA. Si hay un defecto,preservar salidas y enmienda antes de corregir. Fuentes y resultados N200 intactos. Al congelar el analista,se debe verificar el SHA/estimando o repetir,si aún no es el utilizado aquí.
