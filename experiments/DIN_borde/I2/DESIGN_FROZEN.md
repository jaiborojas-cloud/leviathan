# DIN-I2 · diseño congelado v1

Exploratorio. Base main32536da261569a86ded26b70d9e379bbb69135b7.
Rama research/din-i2-rho-v2. Se compromete ANTES del código del instrumento
y las mediciones. Sólo se modifica I2. No se lee Wine, T2 ni DIN-C1.
El informe de sensibilidad de PR81 NO se abre: su estadística citada por
el usuario se considera contexto aportado, no evidencia auditada aquí.

## Fase0 y fuentes

AGENTS raíz leído, sin instrucciones subordinadas. Se leyeron v1, geometry,
D2 (código de referencias, topología y tablas), AG/AH (teoría, código y
entradas sintéticas) y el diagnóstico angular Iris de G1. Ninguna función
de medición se ejecutó en esta fase. Las fuentes de datos quedan fijadas
por SHA. No se modifica ni reabre el estado de esas etapas.

La validación usa sólo nuestros estados archivados: D2, AG (incluidos sus40
estados AF sintéticos copiados en inputs.json de AG), D2b y G1 Iris. No se
lee un estado AF fuera de ese archivo. No se importa core ni código C1.
geometry.py se importa sin cambios, SHA b4d1e0e4… verificado; se usa jac,
sin invertir G para admitir matrices PSD. v1 d8ec69f8… se ejecuta intacto
sólo como comparador contemporáneo en I2, sin reescribir sus resultados previos.

## Objetos y teoría I1

f tiene rango afín2 y M simétrica PSD (se admite tolerancia de redondeo
1e-10 relativa a max(1,lambda_max)). Se agrupan coordenadas EXACTAMENTE
coincidentes, conservando todos los índices y su multiplicidad. Un vértice
geométrico puede representar varios índices; ese extremo ya pertenece a
rho_vert. Las caras adicionales son las aristas expuestas completas.

rho_vert es el ínfimo en la unión de conos abiertos de vértices. rho_caras
es min(rho_vert,longitudes de TODAS las normales de arista). No se confunde
rho con la distancia geodésica d_borde: en AG d es una cota inferior,
no el objetivo al que debe igualarse rho.

Se demostrará la partición finita y el límite unilateral
L(normal+epsilon*tangente)→L(normal)+L_cola_en_cara_hacia_vértice.
La normal es menor que ese límite si la cola tiene longitud positiva;
la cuerda da condición suficiente de positividad, no necesaria en PSD.
La condición exacta de cola nula es que M anule su velocidad en toda la curva.
No se infiere que una cara supere al mejor rayo genérico de otro cono.

Referencia decisiva: en los40 triángulos AG con tres grupos iguales,
rho_vert=distancia mínima a vértices; rho_caras=distancia mínima a puntos
medios=rho_vert/2. Eso implica que la compatibilidad literal de rho_vert
con un v1 que acertó el mínimo de cara ES IMPOSIBLE. Se reportará I3 literal
como FAIL si sucede; no se fuerza igualdad ni se etiqueta como bug de v2.

## Instrumento nuevo: topología y direcciones exactas

Archivo nuevo rho_borde_v2.py. API recibe M/f; no lee datasets ni checkpoints.
Los floats de f se interpretan como racionales binarios exactos, como D2.
Hull monótono con determinantes Fraction: tolerancia de membresía=0 EXACTA.
Se incluyen todos los índices colineales y duplicados. Tolerancia1e-10,
relativa al rango de proyecciones, sólo alerta de puntos CASI en una cara;
no los fusiona. Se informa esa diferencia: por la discontinuidad no cabe
tratar la fusión de casi empates como un error continuo pequeño.

Las normales se construyen racionalmente de extremos de arista, sin trigonometría.
Para cada cono se interpolan las dos normales limítrofes, normalizadas por
su rango de gaps, con t∈(0,1). Los gaps de cada normal se calculan EXACTOS
antes de convertir a float; su combinación positiva evita cancelación en
conos muy estrechos/near_collinear. Es una parametrización homogénea: escalar
una dirección positivamente no cambia la longitud de la semirrecta.
Se reporta dirección racional y dirección unitaria float sólo para visualización.

Cada cono usa9 puntos interiores, margen1e-8, y3 inicios/brackets acotados
que cubren [0,.5],[.25,.75],[.5,1], respetando el margen. Refinamiento bounded,
maxiter40 y xatol1e-9. Se conservan todos los terminales de los3 optimizadores
y el mejor punto de rejilla; se validan con quad antes de seleccionar.
No se escoge el mínimo sólo por cuadratura rápida ni por la rejilla global.

Se incluyen ambos LÍMITES de cada cono como candidatos al ínfimo:
normal+cola restringida a cara, calculadas por separado. Si ganan, attained=false
y se informa normal/vertice de aproximación, sin afirmar que esa normal
tenga la longitud del límite genérico. No se sustituye una normal por un
ángulo casi empatado. La función no certifica un mínimo global dentro del cono.

## Integración estable y restos

Agrupar duplicados exactamente transforma a=Ew y M_eff=EᵀME, con pesos
iniciales proporcionales a multiplicidades. Se elimina algebraicamente
el modo constante mediante contrastes; eigenvalores negativos sólo al nivel
de redondeo PSD se truncan a0 y se registra tamaño de esa corrección.
No se altera el M archivado. Negatividad por encima del umbral rechaza el input.

Normalizar gaps a max1 no cambia el rayo. Integrar en x=log s usando
z_i=exp(x)*gap_i, w_i∝m_i exp(-z_i), beta_x=w*(media(z)-z).
Esto evita perder transiciones tardías cuando un gap es minúsculo.
Límite inferior x=-32, superior log(48/gap_min). Cuadratura rápida GL12 en
intervalos de anchura≤4; validación quad epsrel1e-10,epsabs1e-11×escala métrica.
Se archivan estimación de quad y ambos restos:

    prefijo ≤2 sqrt(lambda_contraste) exp(-32),
    cola ≤2 sqrt(lambda_contraste)/m_S sum_fuera m_i exp(-gap_i S).

La cota de cola sale de ||w'||1≤2 sum_fuera w_i gap_i y Z≥m_S;
no necesita suponer monotonicidad individual de todas las probabilidades.
La longitud reportada suma integral y los dos restos superiores. Los errores
de quad son estimaciones flotantes, no intervalos rigurosos.
Todo0 en el contraste métrico es un caso analítico exacto, no división por0.

Presupuesto por estado60s y4096 evaluaciones de búsqueda, sin descartar casos.
Si se agota, registrar candidatos y fallo/INCONCLUSIVE, no devolver un certificado.
Dos procesos/BLAS1; presupuesto total7200s. Fuentes/versiones/fallos se conservan.

## Validación fijada:302 estados y controles

1. TODOS los210 D2 con sus M originales y f de inputs.json. Se conservan
   referencias conocidas, cotas/testigos y sus estados MP (incluidos desconocidos).
   Incluye27 modos coordenados de las12 formas/semillas, mass_face y near_collinear.
2. TODOS los80 AG:40 triángulos y40 AF sintéticos ya archivados EN AG.
   En triángulos, referencias analíticas/MP80 de seis cuerdas, y d sólo inferior.
3. Ocho D2b del seed2026102700: uniform_a1,uniform_a005,matched_q070,
   matched_q085,matched_pert_q070,matched_pert_q085,grouped3,aligned.
4. Cuatro Iris G1: R27/P60/W27_s00_k0_u010 y P60_s02_k0_u010.
   Se comparan todos los rayos axiales conocidos archivados de esos cuatro.

No se exige rho_caras≤rho1 quebrada de AH ni≤d_borde: esos son objetos
distintos que pueden ser menores. No se lee ningún input de T2/C1.

Controles adicionales sintéticos: triángulo unitario M=I (rho_vert=sqrt(2/3),
rho_caras=sqrt(1/6), salto=sqrt(1/2)); límite de cono t=1e-2,1e-4,1e-6,1e-8;
misma cara con M coordenado fuera de ella (salto0); M constante/rho0;
homogeneidad4M; invariancia por carta afín dyádica; rechazo M indefinida y
f de rango afín<2. No se toman éstos como estados reales independientes.

## Reglas de veredicto y tolerancias

**I1 PASS** si se demuestra la partición/límite con condiciones y los controles
de salto/equivalencia lo reproducen. Fallo matemático resuelto FAIL; otro INC.
**I2 PASS** si todas las referencias conocidas D2/AG cumplen
|v-ref|≤2e-7 sqrt(lambda_max(M))+2e-5 |ref| y todos los testigos válidos conocidos
se respetan por ese margen. Referencias previas UNKNOWN no se convierten en
conocidas. Triángulos deben cumplir d≤rho_caras, no igualdad. Contradicción
resuelta FAIL; presupuesto o referencia no resuelta INCONCLUSIVE según alcance.
**I3 literal:** rho_vert frente al v1 archivado, en D2 gaussian/interior con
Q5 PASS y referencia exacta, y en triángulos donde v1 contemporáneo acierte
rho_caras analítica. Tolerancia2e-7×escala+2e-4×|v1|. FAIL si difiere en alguno,
clasificando separación de estimandos frente a discrepancia numérica. AF y
los demás casos se describen: no se conoce su mínimo global sólo porque v1
esté estable o dentro de cotas.
**I4 PASS_DESCRIPTIVE** si mediana v2≤5s,p95≤15s y mediana v2/v1≤5 en benchmark
contemporáneo fijado; FAIL_DESCRIPTIVE si excede, INC si no se completa.
No se promete tiempo universal de miles de estados ni certificado global.
**I5 PASS_DESCRIPTIVE** si recomendación distingue desenlaces, deriva de
evidencia y no decide por el responsable ni reescribe estudios previos.

v1 contemporáneo1440/800: todos80 AG,4 G1, D2b uniform_a1/aligned y16 D2
(primera semilla, cada forma, primer caso de cada kind coordinate/constant/
isotropic/random_rank1).102 comparaciones; los demás usan el v1 YA archivado.
Los tiempos históricos se distinguen de este benchmark con los mismos recursos.

Sensibilidad v2 en24 estados: esos16 D2,primer AG de cada grupo,4 G1 y D2b
uniform_a1/aligned. Rejilla17,6 ventanas/inicios,maxiter64,margen1e-12,
GL24/intervalos≤2. Debe coincidir por tolerancia I2; discrepancias se preservan.

MP80 numérico independiente en4 ganadores: D2 random_rank1 de mass_face y
near_collinear primera semilla, primer AF en AG y testigo G1 P60_s02.
GL32/64 sobre log s, partición≤2; registrar ambas y errores, no reutilizar
factor espectral double de v2 como referencia MP. Presupuesto separado300s
por contraste, sin ocultar inconclusos. Las40 referencias triangulares y27
coordenadas se calculan además analíticamente en MP, sin búsqueda global MP.

Entrega: instrumento, README/THEORY/DESIGN/config, código/pruebas/resultados,
manifest/SHA/verification, arrays propios fuera de Git, push y PR BORRADOR.
Defecto propio → enmienda congelada ANTES de corregir, versión nueva y
salidas previas intactas. No se toca rho_borde.py v1 ni otra etapa.
