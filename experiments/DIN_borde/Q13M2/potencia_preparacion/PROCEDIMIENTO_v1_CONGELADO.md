# Potencia preparatoria M2: procedimiento previo al código y simulaciones

Preparación contra borrador v1 y analista del PR#114,commit525c7455; analistaSHA15ca7b42…. No se congela el estudio confirmatorio. La decisión de truncar se recibió antes de este commit. Se conserva el primer estado de preparación pendiente.

## Escenario y tamaños fijos

N200,400 réplicas por rho,cuatro marcos de100; rho=[0,.3,.6,.615]. Solo rho0 decide el cumplimiento de la regla de preparación: Wilson95 inferior≥.8 para cada manipulador; potencia conjunta se reporta sin exigirla. No se aumenta N ni se generan plan/cohorte.

11 niveles:A0 único,LP1..LP5,WD1..WD5. c=[.864,.688,.61,.56,.50,.40,.69,.61,.56,.50,.438]. d(c)=max(0,−.038434071244996953+.077c),con intercepto ajustado a los seis pares D/c del resultado JSON oficial de Q13DR. No se abre su tabla ni se recalcula D real. LP5 y WD5 se truncan a0; LP4/WD4=.00006592875500304601 permanecen positivos. Documentar la pendiente MCO efectiva y la curva por tramos.

## Generador heredado de Q13DR/C2

Piloto G3s=.8 por SHA,500 filas; solo sus covariables X10,L=log rho10 y varianza residual de Y=log rho250 respecto de base cúbica intra-split. No se calcula D del piloto ni se ajusta X frente a Y reales. sigma²=SSE/(500−100−rango). Covariables: remuestrear N splits completos,semilla SeedSequence([412000,2,N,marco]). Ruido: SeedSequence([413000,2,N,marco]),matriz normal(5N,12,100): un factor común y11 independientes. Reusar los mismos normales/covariables en todos los escenarios rho,con sqrt(rho)·Z_común+sqrt(1−rho)·Z_nivel.

Centrar ruido intra-split; base cúbica del piloto y señal X residual a esa base. Amplitud b_l=sqrt(d_l/(1−d_l)*.8*sigma²/var(señal)),como Q13DR/C2. Y_l=base+b_l·señal+sqrt(sigma²)·ruido_l. Un solo A0 se genera y evalúa por réplica: se reutiliza exactamente en LP/WD. El modelo es condicional a soporte/varianza piloto y compuertas operacionales válidas; d nominal no es el valor esperado exacto de un D CV finito. Se conservan los D simulados negativos, sin recortarlos.

## Análisis simulado

C1 exacto,1999 permutaciones260001,10 bloques260010,base cúbica y PASS del control con p<.05,D>0,pendiente>0. Motor C2 agrupado y bootstrap Q13 por AST intactos,contrastados contra funciones originales únicamente en tablas simuladas. Bootstrap500,seed960001,los mismos draws de splits en los11 niveles,copias en bloque original. c fijos por nivel; volver a calcular D y beta en cada draw. Primaria IC97.5,cuantiles.0125/.9875,código q del analista M2. MODULA si límite inferior>0; compuerta A0 sin señal→ambos INCONCLUSIVE_SIN_SENAL_CONTROL. LP usa índices[0..5];WD[0,6..10]. Reportar también cualquier fallo sin excluir ni redibujar. No compatibilidad LS ni secundarias que requieran datos reales.

La dependencia entre las dos pruebas incluye el A0 compartido incluso con rho0. No calcular la potencia conjunta como producto: contar las réplicas donde ambos MODULA. Wilson95 individual y conjunto con denominador400,incluyendo inconclusas.

## Controles previos y conservación

Dos controles sintéticos,N20/N40: comparar motor agrupado con analista M2 completo(B1999,NB500,ls=None),incluyendo IC y veredicto por manipulador y conjunto. D/IC/beta deben coincidir≤1e−10;p idénticos. La función replica del borrador se contrasta en draws de los once niveles para confirmar emparejamiento y bloque. Comparar exactamente los draws con960001; A0 no se duplica. Si falla un control,detener,preservar y enmendar antes de corregir.

Código/procedimiento por commit+push antes de medir. Dos procesos,un hilo BLAS. Escrituras exclusivas; arrays diagnósticos fuera de Git con SHA. Toda réplica y fallo se conserva; no se cambian semillas o métodos buscando potencia. Al congelar: verificar SHA del analista y el estimando; si cambia,repetir o demostrar equivalencia. No se usa una nueva cohorte real ni se calcula D real. Solo se añade Q13M2/potencia_preparacion/.
