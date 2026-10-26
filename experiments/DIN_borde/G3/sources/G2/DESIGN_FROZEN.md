# DIN-G2 · diseño v1 congelado antes de código y mediciones

Exploratorio, sin p-valores confirmatorios ni transferencia. Sólo G2 se
modifica. AGENTS raíz leído; no hay AGENTS subordinados. Base main y fuentes
permitidas están en config.json/freeze_manifest.csv. No se cargó ningún dato
ni se entrenó, midió rho o probó una generación piloto antes de congelar.

## Lectura previa y separación de objetos

Se leyeron CIERRE_DIN_C1_v1_CONGELADO.md, RESULTADO_D7 y su plan, G1/CONCLUSION,
D2b/THEORY, core, geometry, I2 r3 y el código matemático C1_v2. Se usan sólo
informes publicados y código; NO tablas/estados Wine, Iris, T2 o DIN-C1.
No se reabre ninguna etapa ni se sustituye ningún resultado anterior.

core.make_geom_state y subset_M se importan BIT A BIT verificando SHA; la red
conserva l1/l2/l3 y salida3. No se llama load_split ni train_branch ni ningún
cargador de datasets. Importar la definición load_wine no carga sus datos;
una guarda de acceso bloquea todos los archivos de datasets y datos ajenos.
I2/rho_borde_v2.py r3 se importa intacto (SHA2ac015a2…), sin cambiar argumentos
por defecto. geometry b4d1e0e4 intacto. No se usa rho v1 en esta tarea.

## Cohorte completamente fijada

Seis niveles s=(.25,.5,.8,1.2,2,4),20 splits sintéticos independientes,
5 inicializaciones por split/nivel:600 entrenamientos y4200 visitas.
d=13; clases equiprobables con117 observaciones estratificadas por split:
30 train y9 validación POR clase. El panel completo de validación tiene27.
No se hace selección de ejemplos ni búsqueda del nivel que dé señal.

Medias: primeras dos coordenadas (2,0),(-1,sqrt(3)),(-1,-sqrt(3)); otras11=0.
Covarianza s²I13. Cada split genera117 vectores epsilon~N(0,I13), con
default_rng(311000+split), y etiquetas/índices fijos por clase (39 cada una,
primeras30 train,últimas9 panel). Se reutilizan EXACTAMENTE esos epsilon en
los seis niveles: X_s=mu_y+s·epsilon. StandardScaler se ajusta SÓLO sobre90
train, separado por nivel; f son primeras dos variables estandarizadas del
panel. Las variables nuisance quedan iguales salvo redondeo tras escalar.

Los20 splits son20 réplicas sintéticas independientes; las inicializaciones,
niveles y visitas de cada split NO son independientes entre sí. La distancia
entre medias es2sqrt(3); aumentar s degrada analíticamente la separación,
sin consultar entrenamientos ni escapes. No se garantiza que la variación
de resolución observada cubra todos los regímenes: eso tendrá compuerta propia.

Red13→64→32→3, ReLU, parámetros double; torch.manual_seed(312000+5split+k).
Adam lr.006 y valores por defecto de PyTorch, lote64 sin reemplazo en cada
update por default_rng(313000+5split+k). Misma semilla de pesos/lotes a través
de s. Entrenar EXACTAMENTE250 updates sin early stopping, visitas
5,10,20,30,50,150,250. Dos procesos,BLAS/Torch1; presupuesto total14400s.
Si se agota, conservar UNMEASURED/FAILED para TODOS los pendientes, sin
reemplazar estados ni cambiar presupuesto. No hay dataset real opcional.

## Variables por visita y conservación

R,U,M con funciones originales y todos los bloques[0,1,2]. Guardar M/f,
logits, log p(y), log(1−p(y)), espectro M y pesos/momentos Adam/RNG/lotes
fuera de Git con SHA. Las probabilidades y X se calculan por logsumexp para
evitar saturación; no log(1−p) mediante resta flotante. No se altera M para
forzar PSD ni se añade regularización. El ridge es el de core.

Registrar rho_caras (PRIMARIO) y rho_vert (SECUNDARIO) de I2 r3 intacto,
ganador racional/soporte, errores/restos, diagnóstico externo completo con
SHA, tiempo y fallos. trM, c=maxdiag/tr, q=fracción Frobenius no diagonal,
k*=argmax diag M, argmin p(y), p(y_k*), log1m_star, etiqueta predicha y Mal
del dominante, precisión/pérdida train/val. Empates por argmax/argmin de menor
índice, coincidencias probabilísticas con tolerancia1e-10 descriptiva.

Validez para log rho: salida VALID_NUMERICAL_ESTIMATE, valor finito>0,
rho_caras≤rho_vert, error quad≤1e-6·rho más restos≤1e-6·rho; fuente SHA
correcta, M finita y tr>0. La corrección PSD flotante INTERNA del instrumento
se registra; no se cambia su umbral ni se la presenta como certificado.
El espectro y los valores brutos se conservan incluso si falla la validez.

La guarda permite sólo G2/arrays propios y los cuatro archivos de código
permitidos. Bloquea el resto de experiments, archivos de datasets y arrays
ajenos. No importa ni reutiliza datos Iris G1 como confirmación.

## Estadísticos exactos y compuertas, antes de medir

Por trayectoria X=max_i log(1−p_i,y(10)), L=log rho_caras(10),
Y=log rho_caras(250), R=log(1−p_y(k*(250))(250)), Mal=1[pred≠y] del k* final.
La identidad del dominante puede cambiar entre inicializaciones; se reporta
su frecuencia modal intra-split y la coincidencia difícil10/dominante250.
No se atribuye la variación a un mismo individuo fijo ni a causalidad.

Por nivel, el estimando C1 exacto usa las funciones originales cen, D_cv y
primaria de analisis_C1_v2.py sin cambios: Y/X centrados intra-split;
z=(L−media_global)/std_global; columnas centradas intra-split z,z²,z³;
10 bloques por default_rng(260010).permutation(splits), posición mod10;
D=1−SSE_completo/SSE_base fuera de muestra. Pendiente X del ajuste completo.
999 permutaciones X DENTRO de split, semilla260001, empate1e-15 como C1;
se publica p_EXPLORATORIO y nulo, nunca decide H-var ni confirma nada.
999 reduce el coste frente a5000; el estimando D no cambia.

Una compuerta por nivel adapta C1 al universo100/20: faltantes>5/100 o
splits con≥3 trayectorias válidas<16/20 → INDETERMINADO. Los splits con<3
se excluyen del ajuste, siempre se cuentan como faltantes inicialmente; si
el conjunto final no alcanza95/100, también INDETERMINADO. X sin variación
intra-split atol1e-8, L sin variación o SSE_base0 → INDETERMINADO. No se
seleccionan niveles por D, ni se imputan log rhos o etiquetas desconocidos.
Se publica D computable exploratorio aun si la compuerta falla, marcado.

Para D7, D_X es EXACTAMENTE el anterior D. D_X|R usa los mismos10 bloques,
Yc, B=[z,z²,z³]c pero añade Rc LINEAL a la base; el completo añade Xc.
La permutación mantiene R y cambia X dentro del split,999/260001; publicar
pendiente y p exploratorios. La fracción1−D_X|R/D_X sólo si D_X>.01;
sin recortarla a[0,1], sin llamarla mediación causal. R es contemporánea
de Y y casi algebraicamente ligada a rho tras colapso.

El secundario rho_vert repite todo el análisis definido (con sus L/Y), con
la misma semilla/permutaciones. Nunca rescata una primaria fallida.

Resolución por nivel: fracción Mal250 sobre100; cada split con las cinco
inicializaciones da p_s=media(Mal), var_s=p_s(1−p_s), denominador5.
V=media20(var_s). Con5 Bernoulli el máximo empírico es.24, no.25. Si falta
un Mal final, V completo es desconocido: publicar V_completos y cobertura,
sin reemplazar el V requerido por la regla primaria.

## Regla descriptiva H-var fijada

Sólo decide la primaria rho_caras y los seis niveles COMPLETOS, con todas
las compuertas válidas y las20 variancias por nivel disponibles. De otro
modo INDETERMINADO. Alta variación:V≥.08; baja:V≤.04. Exigir al menos un
nivel de cada grupo y maxV−minV≥.04; si no, INDETERMINADO por manipulación
insuficiente. Estos cortes separan aproximadamente5 splits variables de
10 o más (dependiendo de p_s), no son significancia estadística.

APOYO_DESCRIPTIVO si TODAS:
1. Spearman entre los seis D y V≥.6;
2. el máximo D (empates≤1e-10) tiene al menos un ganador INTERIOR (s=.5,.8,
   1.2,2) con V≥maxV−.02, D≥.02 y pendiente X positiva;
3. media D(altaV)−media D(bajaV)≥.02.
El2% de incremento es una magnitud descriptiva fijada por la escala del
antecedente C1≈.026, no una potencia garantizada ni un contraste confirmatorio.

CONTRADICE_DESCRIPTIVAMENTE si la compuerta/manipulación pasan Y Spearman
≤−.3 Y max D(bajaV)≥max D(altaV)+.02 Y ese D bajo≥.02 con pendiente positiva.
Ése es un patrón inverso, no meramente ausencia de significancia.
Si la manipulación pasa pero no se cumple ninguna regla: NO_APOYO_DESCRIPTIVO.
Todos los patrones se describen aunque no activen una etiqueta favorable.

No se deduce una identidad entre var(Mal) y D de la fórmula estática de M.
D2b fuerza factores residuales y sólo bajo condiciones da n·diag(odds);
no fuerza dinámica, colapso ni incremento predictivo temporal. Se reportan
c y q por nivel para saber si la aproximación coordenada es plausible.

## Controles y entrega

Antes de cohorte: controles I2 triángulo M=I (vert sqrt(2/3),caras sqrt(1/6)),
mass_face26 coordenado (1/702), fuente r3/SHA; generador balance, ausencia
de solapamiento de índices train/panel y estandarización train; igualdad
de D/p originales frente a implementación independiente en≥4 tablas
sintéticas con999 permutaciones, tolerancia D1e-10 y p idéntico. Control
reconstrucción de M desde pesos en tres estados fijados (s=.25,1.2,4,
split0,k0,u10), relativo≤1e-10; no reentrena ni repite rho.
Fallo de control invalida la corrida correspondiente, no se oculta.

Entorno, tiempos, semillas, fallos, manifest/SHA, verification.json,
CONCLUSION y recomendación se archivan. Cualquier defecto propio obliga
a enmienda congelada ANTES de código nuevo y nuevas salidas/versiones;
no se sobrescriben las anteriores ni se flexibilizan umbrales.
Rama research/din-g2-resolucion; push y PR BORRADOR, no fusionar.
