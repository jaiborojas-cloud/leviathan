# E16-AC · diseño prospectivo congelado

Leer primero [fase 0](progress.md). Síntesis S–AB documental independiente, sin
reabrir etapas. Universo: doce finales AB, sin filtrar KKT/testigos; AB cubre12,
no se necesitan reemplazos Z. Comparandos normales de Z/AB UNKNOWN porque no
están medidos allí; no recalcular auditorías cerradas ni importar T sobre S.

Shooting por fuente: ángulo inicial del primer segmento físico, velocidad
normalizada por h(A); incógnitas ángulo y log L en tiempo afín t∈[0,1].
least_squares TRF, diferencias de Jacobiano 3-point, xtol/ftol/gtol1e-12,
max_nfev30, ángulo inicial±pi/3, L entre0.1 y4 veces longitud AB.
Resolver separadamente con DOP853 rtol1e-10 y1e-12, atol=rtol*.01,
max_step=.01, sin multistart ni reemplazos. Error extremo≤1e-8 max(1,|B−A|).
Registrar todos los intentos y fallos; sin convergencia INCONCLUSIVE.

Christoffel y Gauss a partir de h,d h,d²h exactos. SPD comprobada en cada RHS;
fallo det≤0/primitiva o excepción conserva fallo. Jacobi normal en arco:
j''+Kj=0,j(0)=0,j'(0)=1; integrar en t con jtt+L²Kj=0 y jt(0)=L.
Eventos j=0 interiores con margen1e-6 L; raíces cerca de extremos son ambiguas
INCONCLUSIVE. Conteo estable entre tolerancias y ubicaciones relativas≤1e-5.

Contraste K con MP50/80 en cinco puntos y a cada raíz y ±1e-6 L de ella;
agreement relativo float/MP≤1e-8 y MP50/80≤1e-40. Contraste adicional de
Jacobi con RK4 MP50 y80 sobre K exacta en256/512 nodos de la trayectoria
densa float (interpolación lineal de K); mismo conteo y raíces dentro1e-5 L,
j(L) relativo≤1e-5. Es contraste condicionado a la trayectoria float,
no shooting MP independiente ni certificado. Si no converge el contraste,
INCONCLUSIVE; no forzar ceros. Guardar perfiles escalares y puntos de K.

Hausdorff euclidiano bidireccional aproximado mediante distancia punto-segmento
sobre1025 muestras de la geodésica y todos los vértices AB. Registrar ambos
sentidos y diferencia de longitud. Asociación si Hausdorff≤.01 max(1,|B−A|),
sin identificar la rama como minimizante global. Control deriva velocidad≤1e-7.

Controles obligatorios integran geodésica/Jacobi: C0 K0 (las cuatro fuentes),
esfera unidad en coordenadas (latitud,longitud), h=diag(1,cos²(lat)), ecuador:
L=.75pi índice0 y1.5pi índice1 con raíz pi; hiperbólico h=diag(1,exp(2x)),
K=−1, geodésica eje x, L=1,10 índice0. Raíz/control±1e-8,
K controles±1e-10 y j analítico relativo1e-8. Cualquier control falla →
corrida INVALID, conservar todas las salidas. Presupuesto1800s; restantes UNKNOWN.

Regla cerrada: H1 si alguna cuadrática tiene conjugado interior estable
(tolerancias y contraste MP), shooting/asociación válidos y negativos normales
**archivados del mismo punto**. H2 si todas las cuadráticas AB con KKT≤1e-7
convergen, se asocian y tienen índice0 y sus testigos negativos son tangenciales.
Comparandos faltantes UNKNOWN impiden afirmar H1/H2. Todo otro patrón
INCONCLUSIVE, sin seleccionar supervivientes. Reportar índices aun sin decisión.

No afirmar certificado con intervalos, mínimo global, causa única, ni igualdad
entre una geodésica continua y un polígono aproximadamente estacionario.
Guardar entorno, tiempos, hashes, controles, perfiles, intentos y fallos.
Código se congela por commit antes de medir; cualquier corrección de defecto
va a versión nueva sin sobrescribir código ni resultados anteriores.
Una corrida y repetición exacta de tablas científicas excluyendo tiempos.
Sólo experiments/E16/SINTESIS_S_AB.md y experiments/E16/AC/**.
AD propuesto: H2 cociente por reparametrización/velocidad constante; H1 shooting
multiángulo/locus de corte; INCONCLUSIVE cerrar comparandos faltantes primero.
