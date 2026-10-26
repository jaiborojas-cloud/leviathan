# DIN-G3 · diseño prospectivo v1

Exploratorio, no confirmatorio. Sólo se modifica G3; instrumentos y etapas
cerradas intactos. Base main y fuentes SHA en config_design/freeze_manifest.
AGENTS raíz leído, sin AGENTS subordinados. No se cargan Wine, Iris ni datos
T2/DIN-C1. Se leen sólo informes agregados y código permitido. G2 PR85 se
copia desde commit0d28bf1 como código/documentos y tabla piloto; no se traen
sus cambios a la rama ni se usan sus estados como cohortes G3.

## Orden de congelación y elección posterior al piloto

1. ESTE diseño y la regla de tamaño se comprometen antes del código de potencia.
2. Código de potencia → simulación/controles → tamaño por regla predefinida.
3. SAMPLE_FROZEN.md y config.json con N se comprometen ANTES de código de
   entrenamiento G3 y de cualquier generación/entrenamiento/medición de cohorte.
4. Código de cohorte → controles → entrenamiento → análisis y documentación.

La potencia es planificación sintética autorizada, no outcome de G3. Adaptar
N conforme a la regla congelada no es seleccionar tras mirar la cohorte.
Si hay defecto propio, conservar salidas/código y congelar enmienda antes de
corregir en versión nueva. No relajar umbrales ni descartar fallos.

**Los niveles .25,.5,.8 se eligieron mirando G2**, a pedido del responsable.
No se finge una selección independiente. G2 mostró medianas c=.606,.741,.866:
los tres niveles NO demostraron por ello colapso estricto uniforme. Se fijará
y aplicará un criterio numérico, sin llamar colapsado a un nivel sólo por s.

## A · potencia antes de entrenar

Único piloto: sources/G2/results/run_v1/trajectories.csv, copia SHA de G2.
Sólo sus100 pares por nivel .25/.5/.8, sin matrices/checkpoints. Se requiere
pair_valid y cinco inicios por split,20 splits exactos; cualquier discrepancia
detiene la planificación. X,L=log rho_caras10,Y=log rho_caras250 del piloto.

Con el algoritmo C1 exacto, centrar X/Y y potencias de z dentro del split,
z=(L−media)/std global. Ajustar Yc~B=(z,z²,z³)c por MCO. Estimar sigma² piloto
=SSE/(n−n_splits−rank B), reconociendo que el centrado quita n_splits grados.
Guardar coeficientes, SSE, grados y escala, sin inferir un efecto real de G2.

Por cada candidato N=100,128,156,200,256,320,512, **todos los niveles**, cuatro
paneles de covariables obtenidos remuestreando N splits completos del piloto
con reemplazo. Cada réplica bootstrap recibe un ID sintético nuevo y mantiene
sus cinco inicios. Semilla SeedSequence([412000,nivel,N,panel]). Cada panel
simula100 ruidos Gaussianos independientes, SeedSequence([413000,nivel,N,panel]);
400 réplicas por nivel/tamaño/efecto. Emparejar los ruidos entre efectos.

Para D_obj∈{0,.015,.020,.026}, definir rX=Xc−Proj_B Xc y

    beta_obj = sqrt(D_obj/(1−D_obj) * .8 sigma²_piloto / mean(rX²)),
    Yc = B alpha_piloto + beta_obj rX + sigma_piloto · ruido_centrado_split.

El .8 es1−1/5, por centrar cinco Gaussianos. D_obj es el incremento ORÁCULO
de varianza centrada bajo ese modelo; el D CV finito puede ser menor por
el coste de estimación. No se identifica D_obj con un efecto estimado en G2.
Se reportarán ambos. La potencia es CONDICIONAL al modelo Gaussiano y al
soporte de covariables piloto, no una garantía universal.

Estadístico y decisión simulados: C1 exacto,10 bloques/260010,1999 permutaciones
de X dentro del split/260001, p=(1+#Dperm≥D−1e-15)/2000; éxito si p<.05,D>0,
pendiente>0. La implementación vectorizada FWL debe igualar las funciones
originales en≥4 tablas sintéticas, tolerancia D1e-10 y p IDÉNTICA con1999.
No se sustituye el estadístico por una prueba paramétrica de correlación.

Por candidato, guardar400 éxitos por efecto/nivel, estimación y Wilson95%.
El D_obj0 calibra tamaño: el extremo superior Wilson de falsos PASS debe≤.10.
Seleccionar EL PRIMER N común cuyos TRES niveles tengan límite inferior
Wilson95% de potencia≥.8 para D_obj=.026 y control nulo aprobado. Esto es
más conservador que exigir sólo frecuencia≥.8. .015/.020 no deciden tamaño.
No se prueban candidatos mayores después del primero válido. Si ninguno
cumple hasta512, no se entrena: registrar planificación insuficiente y
necesidad de nueva versión prospectiva; no simular una potencia favorable.

## B · cohorte nueva, mismo protocolo G2

N por nivel, cinco inicializaciones, niveles .25/.5/.8,3N5 entrenamientos,
7 visitas cada uno. Configuración final incluirá el N sin reescribir este
diseño o el archivo de planificación. Los N splits son realizaciones
independientes entre sí; niveles, inicios y visitas están emparejados.

Generador G2 exacto:117 epsilon~N(0,I13) por split, clases estratificadas39
cada una; primeras30 train y últimas9 validación POR clase. Medias de radio2:
(2,0),(-1,sqrt3),(-1,−sqrt3), otras11=0; X_s=mu_y+s epsilon. Epsilon se
comparte entre niveles. StandardScaler sólo train; panel27; f=primeras dos
variables estandarizadas del panel. No hay dataset real opcional.

SEMILLAS NUEVAS: dataset=511000+split, pesos=521000+5split+k, lotes=531000+5split+k.
No coinciden con G2 (311000,312000,313000) ni se reutilizan sus observaciones,
inicializaciones o checkpoints. IDs0..N−1 son réplicas nuevas, no los splits G2.
Se conservan epsilon, pesos iniciales, lotes y SHA para comprobar independencia
de semillas y emparejamiento interno. El rango usado se publicará.

Red13→64→32→3,ReLU,double; Adam lr.006, lote64 sin reemplazo por update,
250 updates SIN early stopping, visitas5/10/20/30/50/150/250. Copia de código
G2 con cambios declarados de ruta/semillas/N/niveles/1999 y análisis G3;
generación, entrenamiento, make_geom_state/subset_M y medición I2 no cambian.
Dos procesos, BLAS/Torch1, presupuesto global43200s. Pendientes o fallos
se conservan como UNMEASURED/FAILED, sin sustitución ni extensión posterior.

core/geometry/I2 r3 se importan intactos por SHA. No se llama load_split ni
load_wine ni otro cargador. Guarda de acceso: sólo G3/arrays propios y los
cuatro códigos fuente autorizados; potencia puede leer sólo la tabla piloto
copiada en G3. Cohorte NO carga filas G2, ni siquiera como datos auxiliares.

Medidas/controles de calidad G2 sin cambios: rho_caras primario, rho_vert
secundario, salida r3 válida/positiva/finita y errores/restos≤1e-6 relativo;
M original sin corrección externa, trM,c=maxdiag/tr,q,k*,argmin p(y),p_y(k*),
log1m_star,Mal,precisión/pérdida. Log probabilidades por logsumexp; snapshots
de pesos/Adam/RNG/M/f/scores y diagnóstico completo externo, todos con SHA.

## Primaria y reglas de señal

Por nivel, X=max log(1−p_y)10,L=log rho_caras10,Y=log rho_caras250.
Usar las funciones originales C1 cen,D_cv,primaria, sin CLI ni datos C1:
centrado intra-split, base cúbica, normalización global L,10 bloques260010,
1999 permutaciones260001. El universo se adapta a N×5 sin alterar D.
Compuerta: faltantes>5%,splits con≥3 válidos<ceil(.8N),conjunto ajustado<95%,
Xc sin variación atol1e-8,L constante oSSEbase0 → INCONCLUSIVE.

Por nivel: **PASS_DESCRIPTIVO** si compuerta válida,p<.05,D>0,betaX>0;
**NOT_MET** si compuerta válida y falla alguna; INCONCLUSIVE si no es evaluable.
Es EXPLORATORIO incluso con p pequeño y cohortes nuevas: selección de niveles
por G2 y tres análisis, sin convertirlos en confirmación ni ajustar el diseño.

Régimen por nivel: COLAPSO_OPERACIONAL si mediana c250≥.8 Y mediana q250≤.05.
Publicar además fracción individual c≥.8,q≤.05,Mal,precisión panel y toda
la distribución resumida. No seleccionar individuos por colapso para la
primaria; ningún nivel que falle el régimen se llama colapsado.

Lectura global:
- SENAL_PRESENTE_FUERA_DE_WINE_DESCRIPTIVA si≥1 nivel tiene PASS_DESCRIPTIVO
  y COLAPSO_OPERACIONAL. Sigue siendo sólo este sintético, no datos reales.
- AUSENTE_CON_POTENCIA_SIMULADA_DESCRIPTIVA si TODOS los niveles NOT_MET,
  todos con potencia inferior Wilson≥.8 para.026, pares COMPLETOS y al menos
  un nivel COLAPSO_OPERACIONAL. La afirmación sobre colapso se limita a esos
  niveles elegibles; no implica ausencia de efectos<.026 ni prueba del nulo.
- Si aparece PASS sólo fuera del régimen, compuertas fallan o no hay ningún
  nivel elegible: INDETERMINADO_PARA_COLAPSO. Otros patrones se describen.

## Variación continua y secundarios

R=log(1−p_y(k*(250))) en250. Por split con5 observaciones, var_pop(R)=
mean((R−media R)²), denominador5. V_cont=media sobre N splits completos.
Si falta un R, V_cont requerido es desconocido; informar cobertura y agregado
de completos sin sustituirlo. V_bin de G2=p_split(Mal)(1−p_split(Mal)),
secundario; frecuencia modal k* y coincidencia difícil10/dominante250.
La identidad del dominante puede cambiar entre inicios; no se afirma medir
la resolución del mismo individuo preseleccionado.

D–V_cont: tabla, gráfico y Spearman entre TRES niveles, sólo descriptivos,
sin p ni regla de confirmación. Mostrar qué niveles cumplen el régimen;
no inferir una tendencia universal mezclando formas de M diferentes.

Secundarios prefijados: D7 D_X|R, misma base+Rc lineal, mismos bloques y
1999 permutaciones; razón1−Dcond/D sóloD>.01, sin recorte ni causalidad.
rho_vert repite D,regla descriptiva yD7 (no rescata primaria). W_adj legado:
W_perm de X frente a resid(Y,[L],split), semillas260002 y1999, etiquetado
LEGADO sin afirmar información condicional nueva (contraejemplo D2b).

## Controles y entrega

Controles antes de cohorte: potencia/FWL vs fuente; triángulo I2 ycara26;
balance, índices disjuntos, estandarización train; fuente r3 SHA; no solapamiento
de semillas G2/G3. Reconstruir M desde pesos en tres estados prefijados
(todos los niveles,split0,k0,u10), relativo≤1e-10, sin reentrenar ni repetirrho.
Fallo de control invalida corrida. Conservar todo, no excluir fallos.

No se afirmará certificado de rho, causalidad, equivalencia exacta de M a
n diag(odds), transferencia a datos reales ni confirmación de H-var/DIN-C1.
La identidad de construcción de D2b no obliga a colapso o señal temporal.

Código/protocolos/manifests/resultados/tablas versionados; arrays/checkpoints
y diagnósticos voluminosos fuera de Git. Registros individuales se agrupan
reversiblemente en JSONL con SHA por original, sin borrar originales.
Rama research/din-g3-potencia; push y PR BORRADOR contra main, no fusionar.
