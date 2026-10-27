# Auditoría independiente DIN-Q13-M2: diseño congelado antes de código

2026-10-27,America/Mexico_City. Se audita PR#114,commit66f5de58;analista2e69516e…,pruebas063c15e4…. No se modifica el diseño ni el analista. Solo archivos nuevos en Q13M2/auditoria/. Este es el diseño de auditoría,no la congelación del confirmatorio.

## Lectura y permisos de datos

Snapshots completos y SHA en sources/provenance.json; referencias#104/#105/#107. La suite del autor se lee,pero no se ejecuta su main,que usa un fixture G3 entrenado. Todos los casos/MC se generan desde cero. Único dato de cohorte permitido:tabla Q13-DR SHAed00364f… como referencia LS,leída exclusivamente por un script separado y para una prueba CLI. No se usan Wine,T2,C2,Q13 ni la futura cohorte M2. Sin entrenamiento/geometría.

## Casos mínimos y trazas

Caso base N20/40,11niveles,semilla1010100,Gaussianas X/L y señal decreciente por nivel sobre ruido. Parámetros B39/NB64 para lógica,NB32 para trazas,NB300 para registrar>20fallos. Se conservan todos los casos aunque contradigan expectativas. Demostración de defecto requiere entrada reproducible,resultado observado,contrato y propuesta; distinguir ambigüedad/diseño de fallo de código.

- Bootstrap:capturar draws960001,argumentos de replica/D_punto y pendiente. Mismos draws LP/WD,A0 idéntico,bloques del split original,copias nuevas,recálculo D/c/beta y cuantiles. c varía por split para que el control no sea trivial.
- Independencia:compuertas por separado,X/L constante en nivel exclusivo,fallo de SSE_base en un nivel;comparar con tabla idéntica salvo ese nivel. Fallos en A0 deben afectar ambos. Separar de las validaciones de faltantes/comunes11 declaradas globales; no cambiar esa población retrospectivamente.
- Herencia Q13DR:c constante decimal en punto y réplicas,rango común invertido,comunes exactamente80%,constancia L en bootstrap de un nivel exclusivo y A0,lista completa de fallos sin redibujar.
- Referencia LS:reproducir exactamente beta=.07692466151365258;NB2000,seed960002,captura de c/D/beta/draws para MCO independiente. Funciones sintéticas de LS para fallos de bootstrap,punto no definido y longitudes discordantes;distinguir API no alcanzable con tabla SHA fija de un defecto CLI real. Verificar misma réplica LS para LP/WD y diferencia bm−bls,seed independiente de960001. Los fallos LS deben quedar explícitos sin cambiar primarias.
- Plan:nombres,brazos,dosis exactas,tipos,NaN/inf/entero enorme,tope320 y321,IDs,dominio;lecturas ausentes/directorio/UTF8/JSON inválidos. CLI ABORTA solo con3,prefijoABORTA y sin traceback. JSON estricto,resultado previo conservado o demostrar sobreescritura. La CLI válida usa una tabla M2 sintética y referencia LS real permitida,conservando todos los archivos fuera de Git.
- Revisar que los hashes/resultados del informe de pruebas correspondan al commit auditado;documentar cualquier diferencia sin inventar ejecución de la suite del autor.

## Monte Carlo nominal

N320,400 réplicas en cada rho0/.6;D generador constante=.02 en los11niveles,true beta_LP=beta_WD=0. X/L independientes nuevos por réplica,con el mismo X/L en todos los niveles;ruido11independientes más un factor común para rho. A0 único. Señal X residual a base cúbica,normalizada a varianza1;amplitud sqrt(.02/(1−.02)*.8);ruido gaussiano centrado por grupos de5. Base cúbica con coeficientes[.3,−.05,.02]. SeedSequence([1010300,índice_rho,réplica]);sin repetir semillas buscando resultados.

Estimando C1 exacto:5000permutaciones260001,10bloques260010;bootstrap2000seed960001 compartido LP/WD,cuantiles.0125/.9875. Motor independiente de#104 por SHA,sin modificar;validado frente a analista/funciones originales en controles sintéticos antes de MC. Algebra agrupada para viabilidad,con mismo espacio OLS y bloque original. No se usa G3 como piloto en esta auditoría.

Reportar falsos MODULA por manipulador y familia(al menos uno),ambos,eventos condicionados y no condicionados a PASS de A0;Wilson95 con denominadores explícitos. El control puede fallar y se cuenta como inconcluso,sin excluirlo del denominador global. Réplicas degeneradas o fallidas se preservan;la corrida no se declara válida si no se completan las fijadas. No se truncan D estimados.

Bonferroni bilateral97.5 proporciona cobertura simultánea nominal95 si los IC son válidos;la decisión positiva usa una cola1.25% por manipulador,por lo que el límite direccional nominal es2.5% por unión. Reportar contra5% solicitado y ese matiz;no afirmar control universal de un bootstrap por una simulación finita. Lectura prefijada:familiar Wilson superior≤.05 compatible con control bajo este modelo;inferior>.05 evidencia de inflación;de otro modo tamaño no resuelto. No se cambian umbrales ni se amplían celdas a posteriori.

## Conservación y entrega

Diseño comprometido antes del código/mediciones. Escrituras exclusivas,arrays externos por SHA,fallos completos y nuevas versiones/enmiendas antes de corregir un defecto de implementación. Dos procesos de un hilo. PR aparte en borrador con defectos,cases,tasas,verificación,manifest;no fusionar ni cambiar estados previos. La auditoría propone correcciones,no decide por el responsable.
