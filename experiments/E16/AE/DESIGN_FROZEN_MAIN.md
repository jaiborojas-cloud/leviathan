# E16-AE · congelación principal tras fase0, antes de geodésicas

Fase0 PASS_GEOMETRY; malla90 puntos K∈[−6.6438351,+.0465519], dos positivos.
Los9 candidatos de centro tienen K<0; regla previa conserva P0=(0,0),
K0=−.1325705. No mover centro después de geodésicas ni seleccionar otra red.
Región[-4,4]² fijada previamente; rmax4 y radio descriptivo fijo1.
Este campo no garantiza que existan conjugados observables en la región.

## Instrumento y censura

Rayos equiespaciados512 y1024, v0=chol(h0)⁻ᵀ(cosθ,sinθ), norma métrica1.
DOP853 rtol1e-12,atol1e-14,max_step.05; estado(p,v,j,j',I), I'=j.
Jacobi j''+Kj=0,j0=0,j'0=1. Registrar primer cero interior s>1e-7.
No detener al conjugado para permitir índice posterior, pero no usar área
más allá de primera degeneración. Salida del cuadrado: RIGHT_CENSORED_DOMAIN;
condición>1e12 o error numérico: INCONCLUSIVE_NUMERICAL. No llamarlas eventos
geométricos. Preservar todas las trayectorias finales muestreadas y fallos.

Colisiones separadas: polígonos del frente a radios comunes linspace(0,4,129),
intersecciones propias de segmentos NO adyacentes, r≥.05. La primera detección
da intervalo entre nivel previo y actual, no instante exacto ni prueba de corte.
Sólo cerrar frente mientras TODOS los rayos cubren el radio; no unir huecos de
rayos censurados. Conjugado y colisión se reportan por separado aunque coincidan.
Señalar contactos tangentes/entre muestras como no resueltos; no ausencia probada.

A(r)=ΔθΣIθ(r) antes de eventos y con cobertura angular completa. Integral de
Jacobi es área geométrica embebida sólo si la exponencial es inyectiva;
la prueba de no intersección muestreada no certifica inyectividad continua.
Si no hay evento completo, rdeg y A(rdeg)=UNKNOWN: reportar censura y radio
seguro muestreado r_safe=.95 min cobertura de ambas resoluciones, área allí.
No rellenar rdeg con radio de salida ni con rmax. Fracción al radio1: éxitos
sin evento **observado** y con cobertura; separar censurados y fallos, todos
los rayos permanecen en denominador. Puente con T2-A1 sólo descriptivo.

Comparar eventos compartidos en ángulos comunes y áreas en r_safe común;
agreement relativo de radios/áreas≤.02. Contraste MP50/80: cuatro rayos
θ=0,π/2,π,3π/2, RK4 geodésica/Jacobi completo512/1024 pasos hasta.95 de su
cobertura (o hasta1.1 del conjugado si está disponible y cabe); comprobar
endpoint,j,I relativos≤1e-5 entre mallas y frente a DOP853. Gauss MP en
origen y cerca de cada primer conjugado global, con tolerancia fase0.
El contraste MP sólo cubre rayos declarados, no certifica todos los rayos.

## Q1: predicción de conjugados y disco

π/√K0 es una escala heurística sólo si K0>0. Predicción operacional: en esos
casos los cuatro rayos fijados tienen primer conjugado entre.5 y2 veces esa
escala si toda ventana cabe en rmax/región. PASS si eventos/área y MP convergen
y la predicción se cumple en ambos n. FAIL si ventana completa y ausencia/radio
contrario persisten con MP y ambas n. Sin aplicabilidad positiva, censura,
contactos sin resolver o contraste fallido: INCONCLUSIVE. Por K0<0, la prueba
primaria de esa predicción será INCONCLUSIVE; aun así se miden disco y eventos.
No transferir K positiva puntual a una garantía de conjugado futuro.

## Q2: índice discreto prospectivo

Dos rayos fijados θ0,π/2. Si hay conjugado estable propio c, extremos a
(.75,1.05,1.25)c; si no, extremos exploratorios a(.25,.5,.75) unidades métricas,
con UNKNOWN si no hay cobertura. Mallas16/32/64. Muestrear IVP y construir
normales métricas unitarias; carta lineal p_j=p_j0+q_j n_j, extremos fijos.
Objetivo de longitud por segmentos rectos de coordenadas con Gauss-Legendre8,
contraste16. Hessiana AD por arista, ensamblaje tridiagonal NN; no reemplazar
por el operador de Jacobi para la medición principal. Guardar bloques/bandas,
espectros y modos negativos. Registrar gradiente normal; tolerancia1e-3 para
calificar aproximación estacionaria (sin optimización ni reestacionarización).
Los nodos son discretización de una geodésica continua, no mínimo discreto exacto.

Umbral tau=max(1e-8,1e-7 max|λ|), cuadratura H relativa1e-5. Testigo MP80
mínimo normal con dos pasos1e-8/1e-10 y cuadratura16; acuerdo AD/MP relativo
1e-4. No usar FD float para decidir el índice. Archivar normal fijo y vértices.
PASS si índice0 antes y1 después del conjugado en TODAS las tres mallas,
ambas resoluciones de rayos y contraste MP; FAIL si índice distinto estable en
todas esas comprobaciones. Sin conjugado estable, cobertura o estacionariedad,
INCONCLUSIVE aun si todos los extremos exploratorios tienen índice0.

## Q3: búsqueda de ramas y corte

Para cada rayo seleccionado con conjugado estable, objetivos a1.05c y1.25c
con cobertura. Shooting TRF multiángulo:16 arranques θ uniformes, log L inicial
log distancia del rayo original; θ en arranque±π/8, L∈[.1,1.5 rmax],20 nfev,
endpoint≤1e-7. No reemplazar fallos ni seleccionar sólo convergidos. Registrar
cada solución, rama, longitud y distancia al extremo. Diferencia corta si
Lalt<Lbase−1e-4 max(1,Lbase); contraste MP de rama candidata y entre n.
PASS si alternativa más corta contrastada en todos los objetivos disponibles y
n; FAIL operacional de búsqueda finita si todos los arranques convergen y no
hay más corta estable, sin inferir inexistencia global. Cualquier falta de
conjugado, objetivo censurado, fallo o rama sin contraste: INCONCLUSIVE.
Registrar cambio del candidato más corto entre distancias como estimación
muestreada del corte, no locus exacto ni mínimo global. Sin objetivos elegibles,
no inventar un B más allá de un conjugado inexistente observado.

## Controles obligatorios

DOP853/Jacobi: esfera K1 hasta1.5π, primer ceroπ (1e-8), área I hastaπ
→4π (1e-7); hiperbólico K−1 sin cero hasta4, I=cosh4−1 (1e-7);
cuadrática AD con parámetros AC en región regular: K≈0,j=s (1e-7).
Colisiones: polígono cruzado debe detectarse y círculo regular no; esfera
exponencial3D aπ: rayos opuestos coinciden≤1e-8. La carta plana de AE no se
usa para dibujar toda la esfera: se explicita el control3D.
Índice: esfera0.75π/1.25π en mallas16/32/64, misma integración por segmentos,
NN debe tener0/1 negativas; hiperbólico y plano en las mismas mallas índice0.
Si cualquier control falla, corrida INVALID, veredictos INCONCLUSIVE.

Presupuesto2400s total; si excede, conservar parciales y restantes UNKNOWN;
no aumentar n/radio/centro por falta de eventos. Una corrida y reproducción
exacta de tablas científicas excluyendo recursos/tiempos. Geometría fase0
permanece congelada; defecto exige versión nueva, sin sobrescribir.
Sólo AE y síntesis S–AD. Sin instrumentos/datos T2, entrenamiento, certificados,
causa única, locus de corte exacto o minimizante global. Todo exploratorio.
