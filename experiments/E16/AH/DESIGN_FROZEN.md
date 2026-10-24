# E16-AH · diseño previo a código y mediciones

Sólo AH/**, base main con AG fusionado, datos únicamente sintéticos E16.
Leer los80 M/f exactos de AG:40 triángulos y40 AF, todos incluidos sin
selección ni regeneración. SHA de inputs en config. geometry.py intacto,
SHA comprobado al importar, guarda AF sin excepciones para datos T2.

## Familia, parametrización y significado de la cota

P0=0, camino P(t)=tQ (0≤t≤1), seguido por P(s)=Q+su (s≥0).
La cantidad matemática es inf_{Q,u} L(Q,u). El instrumento finito reporta
hatρ1=min de longitudes **validadas** de curvas concretas, incluyendo Q=0.
No afirmar que se resuelve el mínimo global. Esas curvas dan cota superior
a d_borde; la inclusión explícita del camino nulo asegura hatρ1≤ρ0 validada.
No se corta en ||P||=150: la cola llega al infinito.

Para acotar Q de modo afín coherente, elegir pares de índices j,k cuyo
|det(fj−f0,fk−f0)| sea máximo; empates relativos1e-12 se resuelven
lexicográficamente. B tiene esas diferencias por filas. Coordenadas q=BQ,
v=Bu; Q=B⁻¹q, u=B⁻¹(cosθ,sinθ). q∈[−12,12]². Transformar B→BA
bajo P=Az+b y transformar el origen físico; el dominio es el mismo.
No elegir coordenadas usando d_borde ni éxitos. Reutilizar los mismos80 M/f.

La envolvente de fB⁻¹ define ramas: normales de aristas con empates EXACTOS
y sectores de vértice entre normales consecutivas, excluyendo1e-4 rad de
los extremos. La semirrecta basal no sufre esa exclusión. Para una arista,
θ fijo y q libre; para sector, q yθ libres dentro del sector.
Inicializaciones: q=0 y4 radios(.25,.75,2,6)×8ángulos; paraθ usar punto
medio del sector, rejilla8 direcciones y dirección basal cuando pertenece.
Elegir el menor objetivo rápido por rama, sin descartar estados. Añadir
siempre el candidato inicial de cada rama y el camino basal. Optimizar una
vez cada rama con L-BFGS-B: maxfun120,maxiter40,ftol1e-10,gtol1e-6;
presupuesto GLOBAL4096 evaluaciones rápidas por estado, incluidos inicios.
Registrar agotamientos y salidas nativas; no reinicios adaptativos.
Un optimizador no convergente puede producir una curva factible: no se
presenta como punto estacionario ni hace inválida su longitud validada.
Sin dos quiebres; se omite la sensibilidad opcional.

## Longitud y colas, sin falsa convergencia angular

Usar J de geometry.py para contrastar velocidades; la fórmula equivalente
β_i=a_i(z_i−Σa_jz_j), L'=sqrt(βᵀMβ), permite integrar sin invertir g.
Los rasgos duplicados pueden agruparse algebraicamente y agregar M, sin
cambiar la curva ni seleccionar estados. Todas las pruebas conservan M/f
originales. En una rama de arista imponer sólo los empates del soporte
calculado geométricamente; nunca convertir un casi empate genérico en empate.
El extremo a∞ tiene pesos∝exp(f_iQ) en el soporte dominante, cero fuera.
Guardar Q,u, soporte y extremo junto a las longitudes.

Segmento: GL32 para objetivo rápido; cola: particiones según gaps de logits,
con GL8 por intervalo. Incluir escalas1/gap,8/gap,32/gap y cruces de offsets
con márgenes0,4,12 por gap. Para toda dirección desplazada se consideran los
offsets fQ, no la cola de AG desde0. Para un corte U, añadir la cota de cola
2√λmax(M)Σ_fuera exp(b_i−logΣ_soporte exp(b)−gap_i U).
Elegir U para que esa cota≤1e-14ρ0. No es truncar sin resto.

Validar con quad epsrel1e-10,epsabs=1e-13ρ0, segmento y cola particionada:
camino basal y candidatos inicial/optimizado de TODAS las ramas. Guardar
cada resultado/aviso. Validar en MP80 los tres menores candidatos quad
(no sólo el que favorezca Q2) y también el basal. MP: GL64/128 en segmento,
GL16/32 por intervalo de cola, nodos/pesos calculados a80 dígitos; comparar
órdenes y quad con error relativo≤1e-7. Resto de cola agregado como arriba.
Si un candidato falla, conservarlo y no tratar su valor como longitud válida.
De los validados MP elegir el menor; si ninguno pasa, UNKNOWN (no reemplazar
estado). Si falla la base no se afirma el orden≤ρ0; estado INCONCLUSIVE.
Por estado600s, total18000s, dos procesos, BLAS/OMP1. Conservar todos fallos,
intentos, candidatos y recursos. Un timeout deja UNKNOWN, no cero mejora.

## Basal, controles y reglas previas

Recalcular ρ0 en AH con rho_measure de AG como función pura: mismas720/1440,
GL400/800, normales y quad. No ejecutar sus runners ni escribir en AG.
Su tiempo contemporáneo t0 incluye esa búsqueda completa; t1_total=t0+
búsqueda de quiebres+validaciones. Reportar también coste incremental.
Comparar con valores AG archivados con tolerancia relativa1e-5, sin cambiarlos.

Controles obligatorios; cualquier fallo→corrida INVALID y Q1–Q5 INCONCLUSIVE:
- Triángulo equilátero M=I, baricentro: d=ρ0=1/√6; no debe bajar de d;
  un camino nulo debe alcanzarlo dentro de1e-7.
- Quiebre nulo, en TODOS los80: segmento0 y cola que reproduce la base quad
  dentro1e-7; contraste MP y valor AG archivado en1e-5.
- Invariancia afín de curvas de una rama de arista y una genérica de los
  primeros triángulo/AF: A=[[2,.3],[−.2,.7]],b=(.6,−.4), origen transformado.
  Tanto Q como u y dominio se mapean; diferencias≤1e-7.
- Plano AD: evaluar sólo K y longitud en fuentes/archivos sintéticos AC/AD,
  no reejecutar sus etapas ni atribuirles un borde softmax.

Q1: PASS si40/40 triángulos tienen testigo válido y hatρ1≥d exacta dentro
1e-7 relativo; FAIL si algún testigo válido viola de forma estable; resto
INCONCLUSIVE. Sin redondear una longitud inválida al d exacto.
Q2: PASS si40/40 válidos, mediana(hatρ1/d)≤1.2 y máximo≤1.5; FAIL si el
máximo supera1.5 o la mediana completa supera1.2 de forma estable; resto
INCONCLUSIVE.20% típico y50% peor caso son compromisos operacionales de ajuste,
fijados antes de medir, no una ley universal.
Q3: PASS si40/40 válidos y Spearman(hatρ1,d)≥.95; FAIL si40/40 válidos y<.95
estable ante errores/órdenes MP; datos faltantes→INCONCLUSIVE. Exige mejor
orden que≈.94 de AG; sin p-valores de40 independientes (escalas emparejadas).
Q4 descriptivo: PASS_DESCRIPTIVE si mediana t1_total/t0≤10 en AMBOS grupos,
FAIL_DESCRIPTIVE si excede10 con completos; faltantes→INCONCLUSIVE.
Factor10 es presupuesto aceptable de trabajo adicional, no se predice que
el método con quiebres sea más rápido. Mostrar segundos y factor incremental.
Q5 descriptivo AF: PASS_DESCRIPTIVE si40/40 válidos y todos hatρ1/ρ0≤1+1e-7;
FAIL_DESCRIPTIVE si viola alguno estable; resto INCONCLUSIVE. Informar mediana,
máximo, Spearman(hatρ1,ρ0) y número de pares cuyo orden cambia; no concluir
orden con d_borde real de AF, que permanece UNKNOWN.

Veredictos se contrastan con intervalos numéricos quad/MP (no intervalos
rigurosos); un cruce de umbral→INCONCLUSIVE. Guardar arrays de nodos/perfiles
fuera de Git con SHA y todas las entradas/candidatos escalares en Git.
Una corrida y verificación desde archivos, sin reintegrar etapas previas.
Defecto exige enmienda/nueva versión congelada antes del código corregido,
conservando original. No certificados, mínimo global, igualdadρ1=d o
transferencia T2. No se leerán datos T2.
