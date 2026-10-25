# DIN-G1 · diseño congelado v1

Exploratorio. Fecha de usuario2026-10-25. Base main
a532c3c6f859907888b7fc24ae12521ad64f6abb. Rama research/din-g1-generalizacion.
Este diseño se compromete ANTES del código, carga del dataset y entrenamientos.
Sólo se modifica experiments/DIN_borde/G1/. No se entrenan modelos Wine.

## Fase0, independencia y fuentes

Se leyó AGENTS raíz, sin AGENTS subordinados. Lectura de contexto limitada a
los informes publicados RESULTADO_D1/D3/D4/D5/D6 y conclusiones D2/D2b/D2c;
no se abrieron tablas, estados, checkpoints ni datos de T2/DIN-C1. Las únicas
fuentes ejecutables ajenas a G1 serán core.py, geometry.py y rho_borde.py
con SHA congelado. El import de core define load_wine/load_split pero NO se
llaman esas funciones, ni train_branch. Se usará sólo make_geom_state y
subset_M([0,1,2]) intactos. No se lee C1, ni siquiera su código: las caras
completas se implementan independientemente con la definición geométrica.

La habilidad cloud-environment-runtime se aplicó para comprobar entorno y
red: dos CPU de cuota, tres en afinidad, ~10GB RAM; torch CPU disponible fuera
de Git. No se midió geometría ni se cargó Iris en fase0. Se reserva7200s para
ejecución, con dos procesos y un hilo por librería. No habrá selección de
semillas, sustitución de fallos ni reducción retrospectiva de la cohorte.

## Familias: tres comparaciones, una variable por contraste controlado

Dataset único NUEVO: sklearn.load_iris,150 ejemplos,4 variables,3 clases.
Se elige antes de ver resultados porque tiene3 clases y no exige adaptar
logits_red. No se permite Wine ni otro dataset de T2/DIN-C1.

| Familia | Red ReLU | Panel | Cambio frente a R27 |
|---|---|---:|---|
|R27, referencia externa |4→64→32→3 |27 |Dataset nuevo frente al antecedente Wine; entrada adaptada4 en vez13 |
|P60 |4→64→32→3 |60 |Sólo tamaño/composición anidada del panel |
|W27 |4→128→64→3 |27 |Sólo anchos de las dos capas ocultas |

R27 cambia dataset/cardinalidad y dimensión de entrada respecto a Wine:
no se pretende un contraste causal aislado contra Wine. Los contrastes
P60/R27 y W27/R27 sí mantienen el resto del diseño igual. No se ejecuta el
control opcional de etiquetas aleatorias. Una sola nueva base no representa
todas las familias de datos tabulares.

20 splits×5 inicializaciones POR familia:100 trayectorias,300 en total.
R27/P60 comparten los mismos100 entrenamientos y pesos por visita; no se
entrenan dos veces. W27 añade100 redes:200 entrenamientos físicos,2100 estados
geométricos y120 contrastes de resolución. No son300 trayectorias independientes.

## Dataset, panel, semillas y aprendizaje

Por split s=0..19, train_test_split de índices con train_size90/test_size60,
stratify=y, random_state271000+s. No test separado; todo desenlace geométrico
se mide en el pool de validación. Escala StandardScaler ajustada sólo en train.
f=las dos PRIMERAS variables estandarizadas del panel, sin elegir proyección.
R27 toma9 índices por clase, sin reemplazo, con default_rng274000+s sobre el
pool; orden final por ID original. P60 usa todo el pool ordenado, incluye R27.
W27 usa exactamente R27. Se archivan IDs, scaler y matrices fuera de Git.

Por k=0..4: torch seed272000+5s+k para ambas arquitecturas; RNG de lotes
default_rng273000+5s+k, compartido como regla entre arquitecturas. Capas
torch.nn.Linear estándar, float64,2 ReLU; tres logits sin transformación.
Adam lr=.006, lote64 sin reemplazo dentro de cada update, resto defaults
torch Adam, sin peso de regularización adicional ni scheduler. Se ejecutan
250 updates siempre, incluso si memoriza antes; source train_branch no se
llama porque detendría temprano. Se registra en5,10,20,30,50,150,250.
No se emplea validación para parar, escoger pesos o elegir hiperparámetros.

## Instrumento y registro por estado

make_geom_state y subset_M originales, incluidos parametrización reducida,
promedio Fisher y gamma=1e-4 max(lambda_max(UᵀU),1e-14), sin parches.
Redes con3 clases y dos capas ocultas son compatibles con su forward fijo;
el único cambio de red permitido es tamaño de entrada/anchos.

Por estado: rho_borde, sus diagnósticos/tiempo/avisos, trM, maxdiag/tr, k*,
lambda_max/tr, masa del autovector dominante, norma Frobenius de fuera de
diagonal, espectro, argmin p_y, p_y(k*), log1m_py por logits (sin saturación),
precisión/pérdida train/panel, gamma, espectro/rango numérico Fisher,
M frente a N diag(odds), y cuerda con TODAS las caras completas.
IDs absolutos de k* y del difícil permiten comparar paneles sin confundir
posición del índice. Se conservan M,f,logits,pesos y espectros en arrays
externos con SHA; no se guardan arrays ni checkpoints en Git.

rho_borde se llama con sus argumentos públicos ndir720/orden400. No se
cambia su fuente ni globals. Es resolución distinta del antecedente Wine;
comparación de resolución prevista, no sustitución retrospectiva:
k=0 de CADA split, visitas10/250, CADA familia, ndir1440/orden800. Son120
estados preseleccionados por IDs, nunca por outcome. Estadísticas usan siempre
720/400; no se intercambian por los valores auditados.

Cuerda=min sobre conjuntos S de índices en todas las caras expuestas,
sqrt((1_S/|S|-1/n)ᵀM(1_S/|S|-1/n)). Agrupar todos los duplicados en vértices
y todos los puntos colineales en cada arista, usando ecuaciones ConvexHull
y tolerancia1e-10*max(1,max|f|). Control sintético de26 puntos en una cara
y uno fuera; no se supone que cada cara tiene sólo2 observaciones.

## Elegibilidad numérica, sin excluir fallos del registro

M válida: finita, tr>0, simetría relativa≤1e-12, lambda_min≥-1e-8 max(1,lambda_max),
y h0=J(0)ᵀMJ(0) SPD con lambda_min>1e-12 lambda_max>0; f rango afín2.
No se proyecta M a PSD ni se añade regularización al instrumento.
rho válida: positiva/finita, err_quad/rho≤1e-4, dif_dir y dif_orden≤.01,
y rho≥cuerda*(1-1e-6). Todos los fallos se retienen como no elegibles.
Avisos por sí solos no borran el resultado; se registran íntegros.

Cada familia debe tener≥90% de estados M válidos en cada visita usada para
emitir veredicto. Para H3/H5 además≥90% de las40 auditorías previstas completas
y≥95% de ellas deben concordar≤1% con1440/800 y tener calidad numérica válida.
Fallo de cobertura/control → INDETERMINADO en la H dependiente, no reemplazo.

## Criterios descriptivos previos H1–H5

«APARECE» significa cumplir estos umbrales en ESTA muestra exploratoria;
«NO_APARECE» incumplimiento claro; banda intermedia/censura/insuficiencia
«INDETERMINADO». No se calculan p-valores confirmatorios ni se selecciona
un tiempo temprano después de mirar los datos. Visitas tardías150 y250.

**H1, diagonalidad+colapso.** q=||M-diag(M)||F/||M||F, c=maxdiag/tr.
Colapsado si c≥.8 y q≤.05. Informar mediana de c/q por visita y fracción
colapsada tardía. APARECE si≥80% tardíos colapsados y aumento de esa fracción
respecto a u5≥.5; NO_APARECE si≤20% tardíos colapsados o mediana q tardía≥.2;
otro caso INDETERMINADO. La condición temprana distingue aparición de estado
ya colapsado. Los bloques de n60 cambian Fisher y normalización por N.

**H2, coincide con el difícil.** Sólo estados colapsados tardíos, mínimo40
y≥10 splits. Difícil se define por máximo log(1-p_y) estable; empates dentro
de1e-10 en ese log aceptan todos los índices. APARECE si fracción coincidencia
k*≥.9; NO_APARECE si≤.7; otro caso INDETERMINADO. Reportar también la fracción
sin condicionar al colapso, sin cambiar la regla.

**H3, rho sigue incertidumbre del dominante.** Sólo tardíos colapsados con
rho válida, mínimo40 y≥10 splits;≥90% de los colapsados deben tener rho válida.
Spearman agrupada entre log rho y log(1-p_y(k*)); W=media Spearman intra-split
entre inicializaciones de u250 (al menos3 por split,≥10 splits, sin constantes).
APARECE si Spearman≥.9 y W≥.5; NO_APARECE si Spearman≤.5 o W≤0;
otro caso INDETERMINADO. No se identifica eso con una ley lineal o causal.

**H4, sincronía con memorizar train.** t_mem primera visita con trainacc≥.99
que permanece≥.99 en TODAS las visitas siguientes. t_col primera visita
colapsada que permanece así en todas las siguientes. Eventos de visitas
5..250 están censurados por intervalos (visita previa,visita actual]; ausencia
es censura derecha>250. No se inventa evento en250 para una no ocurrencia.
Mínimo40 trayectorias con ambos y≥10 splits, todas7 visitas completas.
APARECE si≥.8 de esos pares distan a lo sumo UNA posición de la malla de
updates; NO_APARECE si≤.4; otro caso INDETERMINADO. Reportar también número
sin memorizar/sin colapsar; no afirmar misma ventana Wine10–30 ni causa única.

**H5, incertidumbre temprana más allá de rho temprano.** Tiempo fijo u10,
desenlace u250; X=max log1m_py(u10), L=logrho10, Y=logrho250. Se exige≥90
pares completos y≥18 splits con≥3 inicializaciones, auditoría rho aprobada,
y≥80% de u10 no colapsados para llamar «precolapso» al régimen.
Modelo base: Y centrada por split sobre potencias1–3 de z global de L,
también centradas por split. Completo añade X centrada. Cinco folds de splits
por default_rng275010, posición mod5; D=1-SSEfull/SSEbase fuera de fold.
Signo beta de X en ajuste completo de toda la familia. Mismo procedimiento
en mitades de split pares/impares (recalcula folds dentro de la mitad).
APARECE si D≥.02, beta>0 y ambos D de mitades>0; NO_APARECE si D≤0 y ambos
D de mitades≤0, o beta≤0 y ambos beta de mitades≤0; otro caso INDETERMINADO.
Si SSEbase0 o covariables no identificables: INDETERMINADO.
W_adj lineal-rangos legado se reporta sólo descriptivamente: D2b/D2c muestran
que no prueba información condicional nueva. Tampoco D cúbico prueba esa
afirmación general; compara clases predictivas prefijadas, sin p-valores.

## Interpretación algebraica, conservación y entrega

No se tratan diagonalidad y dependencia de p como hallazgos independientes
de la construcción. D2b: con rango interpolante y ridge despreciable,
M≈N diag(odds); en todos los rangos0≤M≤N diag(odds). Tras colapso coordenado
y caras pequeñas, rho≈sqrt(Mkk)/n≈sqrt(N odds_k)/n si leverage≈1. Se reportan
condición Fisher y error a esa diagonal para separar régimen algebraico de
dinámica empírica. El colapso, su dominancia temporal y la predicción no están
forzados universalmente. Un «no aparece» en Iris no reescribe Wine ni D2b.

Preservar TODOS los300 IDs,2100 estados previstos, fallos, tiempos, entorno,
fuentes/hashes y arrays en /workspace/work/din-g1-v1-arrays. Incidencia propia
→ enmienda congelada antes de corregir código, versión nueva sin sobrescribir.
Guardas de código comprometido y acceso impiden repetir el fallo de orden
documentado en D2b. El presupuesto7200s no permite seleccionar supervivientes:
si se agota, faltantes quedan censurados y H afectadas INDETERMINADO.
Push de rama research/din-g1-generalizacion y PR en borrador, sin fusión.
