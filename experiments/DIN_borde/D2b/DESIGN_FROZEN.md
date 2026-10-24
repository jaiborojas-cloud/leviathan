# DIN-D2b · diseño congelado v1

Exploratorio, teórico y sintético. Fecha: 2026-10-24. Base main:
`85c5f3509401bc7822c9c2349d84a75efa101ccb`. Rama `research/din-d2b-algebra`.
Este archivo se compromete ANTES del primer código de medición y de ejecutar
redes. Orden: diseño → implementación → mediciones. No se entrena una cohorte.

## Alcance y acceso

Sólo se escribe en `experiments/DIN_borde/D2b/`. No se cambia ningún estado,
instrumento ni DIN-C1. Los únicos archivos científicos externos ejecutables
son `core.py`, `geometry.py` y `rho_borde.py`, importados por compilación de sus
bytes intactos y contrastados con los SHA de `freeze_manifest.csv`.
No se llama `load_split`, `load_wine`, `train_branch` ni se leen datos T2.
Un audit hook restringe las lecturas en T2 a la fuente de rho y en el archivo
histórico a las dos fuentes autorizadas. No se cargan checkpoints ni NPZ.
Los únicos datos nuevos son paneles y pesos sintéticos.
Contexto descriptivo: D1/D3/D4/D5 y D6/C1 del árbol
`9904db0392f52ecc05b17c67977e0f892c901d4a`, sin importar sus datos.

## Preguntas y reglas previas

**Q6.** PASS si se demuestra la factorización residual exacta de M, la identidad
Fisher sin ridge BAJO rango completo y su cota con ridge, y se reproducen las
identidades en todas las redes evaluables. Deben existir contraejemplos a
diagonalidad universal y a argmax diagonal = argmin confianza. FAIL si una
identidad es contradicha de forma resuelta; fallo de cálculo → INCONCLUSIVE.
El exponente del barrido homogéneo se contrasta descriptivamente con 1 para
tr M y 1/2 para rho; no se extrapola a entrenamiento.

**Q7.** PASS si se demuestra la fórmula condicionada de rho y se comprueba la
aproximación coordenada en los estados de un difícil con epsilon fácil=1e-8:
cota de cuerda y testigo de extinción deben encerrar sqrt(Mkk)/27 dentro de
un margen relativo de 0.05. Si no, la aproximación sintética es FAIL, sin
invalidar la identidad algebraica condicional. No se usa sólo el mínimo nativo
como prueba de optimalidad. Falta de resolución → INCONCLUSIVE.

**Q8.** PASS a «no hay redundancia algebraica universal» si: (a) misma confianza
y distinta G/rho, (b) distinta X pero MISMO campo G en régimen precolapso.
Para (b), error relativo de G ≤1e-5 en [-1,0,1]^2, |Delta X|≥0.5,
lambda_max/tr<0.14 y rango efectivo espectral>10 en ambas redes.
La prueba del campo completo es analítica, la rejilla sólo audita el código.
También se exige reproducir W_adj=0.7 (error≤1e-12) con X exactamente afín
a L y sin información adicional. La causa del W_adj observado en D6 queda
INCONCLUSIVE: no se inspeccionan sus estados ni se hacen inferencias causales.

**Q9.** PASS si las 86 redes terminan, las identidades y los contraejemplos
primarios pasan; FAIL ante contradicción numérica resuelta; errores propios,
fuentes alteradas o controles inválidos → INCONCLUSIVE. La fidelidad de
rho_borde nativo se informa APARTE: tolerancia relativa 1e-4 frente a una
integral independiente en su ángulo; no es certificación del mínimo angular.
Se conservan avisos y fallos, incluido rho≈0; log(0) es indefinido.

**Q10.** PASS_DESCRIPTIVE si se entrega recomendación motivada, distinguiendo
el estimando lineal del condicional general, sin decidir por el responsable.
No se afirma transferencia a T2, causalidad, mínimo global ni intervalos.

## Panel y redes fijados

n=27, tres semillas: 2026102700, 2026102701, 2026102702.
Panel principal: x=linspace(-1,1,27), segunda variable normal estándar centrada
y escalada por su desviación poblacional. y=0 salvo indicación. No se exploran
semillas ni se seleccionan por rho. Todas las redes tienen 2 capas ReLU y
salida softmax de 3 clases, parametrización reducida EXACTA de core.

Por semilla se construyen 28 redes, todas analizadas:

1. lookup 2→27→27→3: primera capa de bisagras con t0=x0-gap/2 y
   tj=(x[j-1]+x[j])/2. Segunda capa interpola H=a I+0.1·11ᵀ.
   Salida inicialmente W3=0, sesgo log(p0/p2),log(p1/p2),0.
   Dos redes p=(.7,.18,.12), a=1 y .05.
2. Dos redes de igual G: p0=.7 y .85, otros=.6(1-p0),.4(1-p0).
   a se obtiene ANTES de rho por brentq en [1e-4,1] para que
   d_perp=27 tᵀ[C+1e-4 lambda_max(C)((a+2.7)^2+27)/a² I]⁻¹t=4.
   Dos sensibilidades con el mismo a y ruido W3 normal de escala1e-4,
   sin reajuste (descriptivas). Se mantienen las cuatro redes.
3. grouped3: H=onehot(grupo)+.1, tres grupos consecutivos de nueve,
   mediante cuatro bisagras que implementan dos escalones en las brechas.
   p=(.7,.18,.12), W3=0. aligned: dos capas de ancho1 constantes,
   misma p; M tiene sólo modo constante invisible a J, rho verdadero=0.
4. lopsided: grouped3 con tamaños25,1,1, p=(.6,.3,.1), etiquetas1
   en los25 primeros y0 en los dos restantes. Contraejemplo de dominancia.
5. near_duplicate: tres grupos de nueve, puntos alrededor de (-1,0),(0,1),
   (1,0), ruido normal1e-3; escalones de grupo; W3 ruido normal1e-3.
6. random_tiny: 2→8→8→3, inicialización aleatoria fijada, etiquetas n mod3.
7. pre_mixed: lookup a=20, p_y lineal de .45 a .8 y reparto .6/.4 del resto;
   W3 se fija por interpolación de logits, no por entrenamiento.
8. Cuatro lookup a=1, W3=0, p_y=1-epsilon, epsilon=1e-2,1e-4,1e-6,1e-8.
9. Doce lookup a=20, p_y del índice0=.3,.6,.9 y los otros1-epsilon,
   epsilon=1e-2,1e-4,1e-6,1e-8. Salidas interpoladas; no se ajusta ridge.

Dos redes más: insertar las dos lookup de igual G de la primera semilla en
la clase `core.WineMLP`, usando sólo sus primeras27 unidades por capa y
dos entradas, con unidades sobrantes inactivas (sesgo−1), resto de pesos0.
No se leen datos Wine. Total86, sin sustituciones ni entrenamiento.

## Instrumentos y contrastes

Cada red: probabilidades conocidas por forward; make_geom_state y subset_M
con bloques[0,1,2] SIN CAMBIOS. Jacobianos reducidos independientes, SVD de
A para resolver F+ridge en rango≤54 y comparar M sin la cancelación Woodbury.
Error R/U≤1e-10; M relativo≤1e-7; PSD tol1e-8 max(1,lambda_max).
La identidad sin ridge se contrasta sólo si rangoA=54 y lambda_min(F)/lambda_max(F)
>1e-10; los demás casos se conservan como no resueltos para esa identidad.
No se cambia el ridge de core, ni se proyecta M a PSD.

rho_borde(Geometry(M,f)) nativo por red, defaults1440/800 y sus diagnósticos.
Referencia independiente: factor PSD de la solución directa, integral quad
partida en 1/gap,8/gap,32/gap para cada brecha de proyección, epsrel1e-10,
epsabs1e-11; cola ≤2 sqrt(lambda_max(M)) sum exp(-gap U)/multiplicidad.
Se compara al ángulo devuelto, sin certificar mínimo angular. Cota inferior
de cuerda sobre vértices/aristas de ConvexHull; cota superior de extinción
u=(mean(f)-f0)/norm para los estados de un difícil. Ninguna EDO geométrica.
Se archivan R/U, M, f, probabilidades, Jacobianos, espectros y factores fuera
de Git, con SHA; resultados escalares/JSON en Git.

## Control del estimando de DIN-C1

Reproducción documental, sin ejecutar el código C1 ni usar sus datos:
MCO Y~intercepto por split+beta L, e=Y residual, media Spearman(X,e) por split.
Control exacto L=[0,.01,.02,.03,1], X=L-2, Y=-L²: W_adj=.7,
Pearson(X,e)=0 y residuoX tras ajuste lineal=0 (NO_IDENTIFICABLE).
64 splits×5, semilla2026102717: exacto anterior; Y+ruido .001; no lineal
L=[-1,-.5,0,.5,1], X=-2+.25L², Y=X+ruido .001; error de medida
Z,T independientes normales, L=Z+.7T, X=-2+.2Z,Y=.5Z+ruido .05;
control positivo L,T independientes normales,X=-2+.2T,Y=.5L+.4T+ruido .1.
Se comparan residuos lineales y cuadráticos y residualización de X.
Los efectos con ruido son DESCRIPTIVOS; no se eligen umbrales tras medir.
No se interpreta un residuo casi cero como correlación definida ni se
desempatan constantes por inicialización. Rangos promedio en diagnósticos.

## Recursos y conservación

Dos procesos numéricos, torch/BLAS/OMP1. Presupuesto7200s total; ninguna red
se reemplaza al vencerlo. Entorno Python3.12, numpy2.3.5, scipy1.17.0,
torch2.9.1+cpu, sklearn1.8.0. Arrays en /workspace/work/din-d2b-v1-arrays.
Cada salida se crea exclusivamente; hashes y tiempo por red. No sobrescribir
versiones. Defecto propio → enmienda congelada ANTES de corregir código,
nueva versión y conservación íntegra del fallo. Resultados sujetos a auditoría
de integridad posterior, sin repetir mediciones de etapas cerradas.
