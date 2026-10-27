# DIN-Q13-DR: procedimiento operativo de potencia previo al código

Aplica íntegramente el diseño v3 CONGELADO (SHA e3ebe060…). Este protocolo operacional no lo sustituye ni cambia sus decisiones. Solo se añaden archivos en Q13DR/cohorte/. Los seis c de planificación son [.84,.70,.61,.54,.42,.36], como el encargo. Pendiente objetivo .031/.26; d_l=max(0,.039+(.031/.26)*(c_l−.86)).

## Potencia y sensibilidad

Método Q13 v2/C2: piloto G3 s=.8 por SHA,500 filas,100 splits×5. Base cúbica de L10 intra-split; sigma² del residuo de Y250 respecto de esa base, con500−100−rango grados de libertad. No se ajusta una asociación X–Y del piloto. Cuatro marcos remuestreados completos de N splits,100 réplicas gaussianas por marco:400/N. Seeds de covariables SeedSequence([412000,2,N,marco]) y ruido [413000,2,N,marco], como Q13. Señal= X residual a base; b_l=sqrt(d_l/(1−d_l)*.8*sigma²/var(señal)).

Ruido por réplica en las seis respuestas: sqrt(rho)*Z_común+sqrt(1−rho)*Z_l; generador normal de forma(5N,7,100), primero factor común y luego seis independientes. Se centra intra-split. Los escenarios usan los mismos normales y covariables; rho=0 es el ÚNICO que decide. Correlaciones fijas .3/.6 y rho estimada solo sensibilizan el N elegido (o400 si ninguno es elegible). No se escoge tamaño ni se cambia modelo por esas sensibilidades.

**Única lectura autorizada de Q13 real:** tabla q13_cohorte.csv por SHA. Extraer únicamente brazo,split,k,error y rho_caras_250 de A0/LS; emparejar por(split,k), exigir rho positiva finita y errores vacíos; usar splits con≥3 pares válidos. Calcular Pearson entre los dos log rho250 centrados dentro de cada split pareado. No leer/construir X10,L10,R ni D,p u otra asociación. No se estima una matriz6×6. Esta correlación observada incluye señal compartida, no identifica covarianza de ruido condicional: sensibilidad descriptiva. Si no se identifica rho o queda fuera de[0,1], detener y reportar sin recortar ni sustituirla.

## Estadístico simulado

C1 exacto: base cúbica,10 bloques260010,1999 permutaciones260001, PASS conp<.05,D>0,pendiente>0. Motor agrupado Q13/C2 por AST intacto para obtener D y p en respuestas SIMULADAS, contrastado con la función congelada. Bootstrap500, seed860001, mismos splits en los seis niveles; copias centradas como splits nuevos, bloque original, recálculo D/beta. c_l fijo por escenario; pendiente y clasificaciones MODULA, equivalencia secundaria y extremo se llaman del analista DR congelado solo con estadísticas SIMULADAS.

Se conservan errores y réplicas; una réplica no definida es INCONCLUSIVE y no se redibuja. Controles de equivalencia numérica antes de aceptar potencia: D y bootstrap frente a funciones originales≤1e−10; p idéntico, reglas y beta/IC coherentes. Un control fallido detiene la corrida. Campos observados del piloto no se pasan al analista como desenlace de prueba.

## Regla y publicación

Primer N∈{200,256,320,400} con Wilson95 inferior≥.8 para MODULA, de400 réplicas. Reportar también NO_MODULA secundaria y extremo PERSISTE/DESAPARECE/INDETERMINADO, incluyendo INCONCLUSIVE. No se exige potencia de equivalencia. Si ninguno cumple, publicar y detener: sin plan ni productor ni cohorte. No repetir o ampliar semillas buscando elegibilidad.

Diseño/procedimiento→código→potencia publicada por commit+push→plan publicado por SHA→productor. Si cumple se prepara, sin entrenar, el productor Windows con receta/support Q13 byte por byte y sus controles de IO/reproducción sin entrenamiento. Esas comprobaciones no son cohorte. La ejecución final y prueba corta quedan al responsable. Cambios por defecto: conservar fallo y enmienda antes de corregir.
