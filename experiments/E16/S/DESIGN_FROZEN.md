# E16-S — Parada física auditada

Protocolo prospectivo exploratorio. R conserva INCONCLUSIVE y es dependencia
sin merge automático. Se incorpora main sin modificar su material T2-A.
Mismos datos sintéticos, sin entrenamiento ni confirmación independiente.

## Fuentes, métodos y presupuesto

Fuentes Q/length/132 de Q0/Q1/C0, las mismas usadas por R. Reference minimiza
L en x y scaled minimiza L(Dy), mismas cajas y extremos. Usar las escalas
diádicas archivadas en R/scales.csv, verificando hash, positividad, potencias
de dos, dimensiones y correspondencia con las fuentes de R. No recalcular ni
seleccionar escalas después. Preparación nueva cero por caché, sin confundirla
con el coste inicial de R.

132/264; cada método refina su propio candidato por todos los puntos medios,
preservando L. No reinicios, fallback ni selección de mejores. L-BFGS-B:
maxiter=4800, maxfun=80000, maxls=40, ftol=1e-14, gtol=1e-9 como R.
900 s/512 MiB por corrida, INCLUIDAS auditorías y validación. No ampliar.

## Monitor y cumplimiento muestreado

Auditar al inicio (iteración 0), sin contarla para la racha. Después auditar
cada 200 ITERACIONES ACEPTADAS del callback. Siempre evaluar AD y FD locales
MP80 de ambas coordenadas, pasos 1e-18/1e-22, sin filtro previo por AD.
Acuerdo AD/MP≤1e-6 y entre pasos≤1e-20. KKT en cajas FÍSICAS normalizado por
max(1,|L|), umbral 1e-5.

STATIONARY: gradiente verificable y KKT≤umbral. NONSTATIONARY: verificación
pasa pero KKT incumple; es observación negativa, no fallo de integridad.
UNVERIFIED: falla evaluación o concordancia; se conserva y hace inconclusa
la validación del camino aunque luego haya otra favorable.

Exigir tres auditorías PROGRAMADAS consecutivas STATIONARY, separadas por 200
iteraciones. Incumplimiento, hueco o falta de verificación reinicia racha.
Al alcanzar tres, pedir parada con StopIteration; conservar ese estado, nunca
uno anterior mejor. Registrar hashes y verificar que SciPy devuelve el estado
auditado y la interrupción de callback, sin alterar su bandera nativa.
Persistencia en muestras no garantiza lo ocurrido entre muestras ni significa
independencia estadística: los puntos están correlacionados.

## Vías de aceptación y validación final

PHYSICAL_SUSTAINED: racha completa, parada explícita, estado final idéntico y
validación final separada del monitor. NATIVE_VERIFIED: éxito nativo antes o
sin racha completa, más la misma validación física; no atribuirle persistencia
no observada. C0 puede terminar a cero iteraciones y se rotula NATIVE_CONTROL
si verifica recta y KKT; no inventar tres muestras de un estado repetido.
Otras terminaciones, incluido límite sin racha, quedan inconclusas. Un estado
final distinto al de la parada solicitada es fallo de identidad. La bandera
False de una interrupción física no se cambia a True ni es fracaso automático.

Todas las vías requieren AD/FD MP final, KKT físico≤1e-5, no empeoramiento de
L, cotas/extremos, precisión 80/120, primitivas/cuadraturas/reparametrización y
SPD heredados de G. C0: error longitud recta≤1e-8, max|s|≤1e-6.
Refinamiento: longitud normalizada≤1e-3, Hausdorff superior≤1e-3, brecha≤1e-5
y ambos candidatos válidos. Comparaciones entre métodos/Q0-Q1 descriptivas.
Hausdorff es euclídea en (t,s), no distancia intrínseca ni certificado riguroso.

## Controles, trazabilidad y coste

Control de rachas: tres éxitos paran; fallo/UNVERIFIED reinicia; la inicial no
cuenta. Control SciPy cuadrático: interrumpir la segunda iteración aceptada,
verificar status=99, success=False y estado final idéntico al callback.
Conservar controles de escalado, inversión, subdivisión, verticalidad, arco
y Hausdorff de R.

Por auditoría guardar sólo escalares, estado, racha, iteración, errores, KKT,
longitud y hash del polígono. No versionar gradientes internos ni checkpoints;
sí polígono/gradiente FINAL. Reproducir logs y hashes reejecutando todo.

Separar evaluaciones/gradientes del solver y auditorías completas. Cada
auditoría usa 4 referencias MP locales por variable (dos pasos, ±), además de
una referencia global para normalizar. Validación final común aparte. Registrar
tiempos del monitor y del solver total, sin llamar aceleración temporal a una
reducción de iteraciones que omita el coste de auditoría.

Comparar descriptivamente con R archivado sin reejecutarlo y conservando sus
estados. Coarse comparte fuente/algoritmo; fine tiene distinta continuación
y R no incluye monitor ni caché. No es benchmark pareado de tiempo total ni
nueva aprobación de R.

Identidades fallidas: FAIL. Validación pendiente, presupuesto o parada no
verificada: INCONCLUSIVE. Global sólo pasa si todos los caminos, controles y
refinamientos pasan. Conservar primera corrida y desconocidos; reproducir
salidas científicas byte por byte, recursos aparte. PASS_NUMERICAL sólo acredita
este protocolo: no mínimos globales, geodésicas, unicidad ni curva límite.
