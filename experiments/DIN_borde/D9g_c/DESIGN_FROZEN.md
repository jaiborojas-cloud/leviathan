# DIN-D9g-c — diseño exploratorio CONGELADO antes del código

Fecha2026-10-26 (México). Rama research/din-d9g-c, base main0dbc973.
Este commit precede a todo código/resultado nuevo de ridge. [Config exacta](config.json).
Fuentes D9g/D9g-b por commits8996c2c/417b80c y SHA, sin modificar originales.
C2 permanece RESERVADA: prohibido leer su cohorte, estados/checkpoints/test ni
calcular asociaciones. No Wine/Iris/T2/DIN-C1. No instrumentos, entrenamiento,
regeneración o reevaluación. Sólo tablas numéricas ya archivadas:1.500 filas.

## Objetivo, candidato y decisión explícita del responsable

Desenlace pérdida test250 de D9g, candidato c30, decide s=.8 (500 filas,100splits).
s=.25/.5 y agregado sólo descriptivos. Mismo test seeds711000..711099, covariables
u30 de B4 ya medidas. No se restauran pesos ni se hace forward ni test nuevo.

Antes de congelar se explicó que añadir c cruda sin penalización puede eludir el
ridge aun si es una función barata. **El responsable eligió añadir c30 residualizada,
sin penalizar**, mediante respuesta explícita a la aclaración. Por tanto se pregunta
por información fuera del ESPACIO LINEAL DEL DICCIONARIO completo (polinómico),
no por cualquier beneficio de cambiar la penalización de una función ya contenida.

## Diccionario y transformaciones por bloque

Exactamente B4 de D9g-b:21 términos. q=(loss_train30,loss_panel30,acc_panel30,X30).
Estandarizar q con mu/sigma poblacional de ENTRENAMIENTO; z=(q−mu)/sigma,
usando sigma1 si constante. Términos:4 z,4 z²,4 z³,6 productos z_i z_j (i<j),
y margen firmado medio panel, entropía media panel y norma L2 de todos los pesos/
sesgos, como quedaron fijadas en D9g-b. Estas3 extras sólo lineales, estandarizadas
con mu/sigma train. Centrar cada término dentro del grupo de5 inicializaciones;
escalar por RMS de las columnas centradas en train. Sin términos nuevos ni selección.

Cada bloque externo Y cada subbloque interno vuelven a ajustar mu/sigma/RMS sólo
con sus filas train. Nunca usar estadísticas externas para normalizar un subbloque.
Y y candidato se centran por grupo como D9g. No intercepto tras centrar. En agregado,
grupos=(nivel,split), pero todos los niveles del mismo split en el mismo bloque;
pendientes comunes y100splits, no300splits independientes. Filas/orden iguales a D9g-b.

## Ridge, CV anidada y forma de añadir el candidato

Objetivo base: min_beta ||Yc−Z beta||²/n_train + lambda ||beta||².
Penalizar los21coeficientes; ceros/rango reducido resueltos por SVD. Rejilla fija
lambda=10^(−4+i/4), i=0..32:33valores de1e-4 a1e4. Media-SSE, no suma-SSE:
la escala de lambda es comparable entre tamaños. Sin ridge adaptado por resultado.

10bloques externos: default_rng(260010).permutation(splits), posición mod10.
Dentro de cada train externo:5bloques por split, seed260011, posición mod5.
Elegir lambda que minimiza SSE interno total (igual peso por fila); empates EXACTOS:
mayor lambda. Reajustar la base con ese lambda y sólo el train externo. Guardar
pérdidas de los33valores, elecciones, transformaciones, tamaños y predicciones.

Después, a_c=argmin_a ||c_train,c−Z_train a||² por OLS/SVD rcond=None.
r_train=c_train,c−Z_train a_c, r_test=c_test,c−Z_test a_c. Añadir r SIN penalizar
al predictor ridge ya ajustado; gamma=r_train^T(Y_train,c−BR_train)/||r_train||².
Es el ajuste conjunto penalizado en Z y no penalizado en r, porque Z^T r=0.
La base ridge no cambia al añadir r; no se elude su penalización. Coeficiente de
r se reporta en unidades originales de c. Residuo relativo≤1e-10 → alias:
sin nuevo componente, gamma0 por definición del modelo, D0 (no coeficiente identificado).
Registrar ese evento, no interpretarlo como estimación de efecto cero.

B1: las4medidas lineales, OLS sin penalizar, más candidato residualizado en B1
(equivalente al ajuste completo OLS anterior). Reproducir D9g B1 para cuatro
conjuntos con errorD≤1e-10; nueva p usa999permutaciones, no se exige p idéntica a2000.
β descriptivo completo: lambda elegido por5bloques internos en todas las filas,
transformaciones ajustadas en ese conjunto, proyección OLS y gamma como arriba.
Mitades par/impar: repetir TODOS los pasos/CV en cada mitad, no conservar lambda
ni normalización del completo. Se reportan β,D,D_base,lambda de ambas bases.
La estabilidad usa la MISMA clase de base de lectura elegida en el completo;
no elegir otra base por mitad. Signo estable =par·impar>0 y consistente con completo.

## Adecuación y selección de base de lectura

D_base=1−SSE(base)/SSE(0), SSE0=sum Yc², mismas filas y10bloques para B1/BR.
BR adecuada si D_base(BR)≥D_base(B1)−.005; en ese caso BR es base de lectura.
Si BR es peor por MÁS de.005, la base de lectura es B1, como fija la tarea.
La igualdad conserva BR. No decidir la base por D del candidato ni por su p.
Si se lee B1, declarar que la flexibilidad NO ayudó y que no se demostró incremento
sobre una base flexible adecuada. No ocultarlo bajo la etiqueta ROBUSTO.

## Permutación de TODO el procedimiento

999permutaciones, seed340001, c dentro de cada grupo de cinco; resolución p=1/1000.
No permutar q/extra/Y ni mezclar niveles/splits. Por cada permutación repetir:
selección interna de lambda en TODOS los train externos → ajuste BR → proyección
OLS del candidato permutado → ajuste gamma → predicción/SSE → control adecuación
y elección B1/BR. Evaluar D=1−SSE(base+r)/SSE(base) con la base seleccionada.
p=(1+#{D_perm≥D_obs−1e-15})/1000, sin truncar D negativos. También reportar p
para B1 y BR individualmente, nunca elegir la que favorezca c.

Como lambda de BR depende sólo de q/extra/Y train y no del candidato, su elección
DEBE ser idéntica al permutar c. No se impone lambda observada: cada repetición
vuelve a evaluar los33scores internos y elegir argmin. Se permite cachear SVD y
transformaciones de datos invariantes al permutar c, estrictamente dentro de train;
volver a computar scores/argmin en cada repetición. Validar contra reejecución sin
cache en controles (scores relativos≤1e-10, mismos lambdas). Conservar matriz de
lambda/score por repetición; la proyección y gamma SÍ se recomputan para cada c_perm.
Se permite vectorizar cálculos idénticos en las999columnas, sin fijar a posteriori
parámetros que dependan de candidatos. Guardar todos D/SSE y predicciones.

## Controles obligatorios y señal pequeña

Negativos sintéticos: c=q0² y c=q1q2; Y=c+.5epsilon, q y extras normales con
offsets de split. Los dos candidatos pertenecen al diccionario; con residualización
y r sin componente numérico deben dar |D_BR|≤1e-8. Registrar alias y que el cero
se debe a la definición del componente fuera del diccionario; no es prueba de
calibración universal. Sin esta residualización, el negativo no tendría D0 garantizado.

Positivos sintéticos:100splits×5, siete q/extra normales con offsets; r,epsilon,xi
independientes N(0,1). c=r+.2xi; Y=.5q0−.2q1²+.1q2q3+b r+epsilon.
Para D_oraculo=theta, b²=theta·1.04/(1−theta·1.04). theta=.20 grande y .02 pequeño;
semillas801001/801002, respectivamente. El oráculo supone base poblacional perfecta;
el D de CV finito no tiene por qué coincidir. Usar el pipeline completo y999perms.
Grande: exigir D_BR>.05,p_BR<.05 y signo positivo estable. Pequeño: **reportar si
cumple D>.01,p<.05 y signo estable**, sin exigir éxito ni cambiar semilla; no es
potencia conocida ni experimento de400réplicas. Si falla, limita una lectura de ausencia.

Negativos seeds801003/801004. Control numérico seed801005: comparar pipeline
vectorizado con reejecución directa de regresión ridge/residuo sin atajos en tabla
artificial, incluidos al menos999D nulos en20splits×5. |errorD|≤1e-9, p idéntica;
para lambda, al menos observado y primeras2permutaciones sin cache completa, scores
relativos≤1e-10 y misma elección. Validar centramiento/bloques y no acceso a C2.
Si negativos/grande/numerical/reproducción fallan: INVALIDA y conservar; no interpretar
ni seguir a una cohorte confirmatoria. El pequeño no es compuerta de validez.

## Regla de lectura fijada antes de medir, sólo s=.8

Con controles válidos y B1 reproducida, elegir base por adecuación anterior.
- **ROBUSTO_EXPLORATORIO** si D_lectura>.01, p_lectura<.05 y signo β estable
  en mitades par/impar, consistente con completo.
- **REDUNDANTE_EXPLORATORIO** si BR es la base de lectura y D_BR≤0.
- **NO_CONCLUYENTE_EXPLORATORIO** en otro caso; controles fallidos se señalan
  como INVALIDA, nunca REDUNDANTE. Alias real se informa; no inventar β/p.

ROBUSTO → proponer al responsable diseño confirmatorio en C2; REDUNDANTE o
NO_CONCLUYENTE → proponer Q13, como indica la tarea. **No ejecutar ninguno aquí.**
No convertir el test en confirmatorio ni afirmar equivalencia/causa por D≤0.
Niveles .25/.5 y agregado descriptivos; no rescatan ni alteran decisión en .8.
No buscar otra rejilla/diccionario/semilla/penalización después de ver resultados.

## Conservación, datos completos y límites

1.500filas previstas,1.500copias numéricas exactas; validar IDs únicos y dominios.
Si falta>5% o quedan<80%splits con≥3filas/<95%filas tras ajustar: NO CONCLUYENTE.
Conservar todos los fallos, versiones, entorno, tiempos, SHA, arrays fuera de Git.
Dos procesos, un hilo BLAS; presupuesto14.400s. Escrituras exclusivas. Cualquier
defecto: enmienda congelada antes de corregir, sin sobrescribir original.
Sólo D9g_c se modifica. No se evalúa red, test ni geometría; ni se entrena.

Exploratorio y última prueba de descubrimiento en estos datos para esta decisión.
No afirmación confirmatoria, causal o transferencia. La p no prueba calibración
universal; la selección de lectura se repite pero sigue siendo exploratoria.
Proyección OLS de c puede añadir variabilidad; ridge en Y no regulariza esa proyección.
Un resultado atañe a este diccionario/regresión, no a toda función barata. El test
finito se reutiliza y está gastado para descubrir; C2 permanece independiente para
el estimando reservado, sin acceso en esta etapa. El centrado usa media final del
grupo completo como C1/D9g: no predictor desplegable sin esa media.
