# E16-R — Escalado diagonal conservando longitud

Diagnóstico exploratorio prospectivo. Mismos datos y pesos sintéticos, sin
entrenamiento. Conservar Q0, Q1 y C0, incluidos sus estados inconclusos.

## Fuentes y contraste

Fuentes Q/length/132, sin reejecutar Q. Dos métodos independientes desde esa
misma fuente: reference usa L-BFGS-B en x=(t_1,s_1,...); scaled aplica el mismo
algoritmo a f(Dy), con x=Dy y D diagonal positivo, fijo durante cada búsqueda.
En ambos el objetivo es exactamente L: no energía, penalización, suelo de h
ni regularización. Mismos extremos, rectángulo de P/Q, aristas nulas rechazadas
y tolerancias de validación. No se cambia longitud por su cuadrado.

132 y 264 segmentos. Cada método refina su propio candidato por todos los
puntos medios antes de optimizar; comprobar que preserva la longitud. No hay
reinicios, elección retrospectiva de mejor candidato ni fallback entre métodos.
El método reference es una continuación nueva, no una modificación de Q.

## Precondicionador congelado

Para cada linaje/malla, construir un polígono común: fuente Q132 o su bisección
sin reoptimizar. Calcular su Hessiano AD H de L una vez. Sea a_i=|H_ii| y
mu=mediana de los a_i estrictamente positivos; si no hay ninguno, mu=1.
Definir r_i=sqrt(mu/max(a_i,1e-8 mu)); e_i=clip(rint(log2 r_i),-7,7), con rint
al par en los empates. D_ii=2^e_i. Si un Hessiano no es evaluable, conservar
inconcluso y no sustituirlo por un precondicionador elegido después.

El valor absoluto, piso y límite se aplican SÓLO al precondicionador; no se
modifica H en el objetivo ni la métrica h. D no garantiza que H sea positiva
definida ni trata todos los modos de redistribución de nodos.

El precondicionador de 264 se calcula en la bisección de la fuente ORIGINAL,
no en el resultado de un método. Ambos métodos tienen las mismas referencias
comunes y sólo scaled utiliza D. Transformar y0=D^-1 x0, cotas_y=D^-1 cotas_x,
f_y(y)=L(Dy) y grad_y=D grad_x. Las potencias de dos y las cotas diádicas
permiten controlar exactamente el viaje ida/vuelta de coordenadas binarias.
No proyectar ni recortar x después para disimular un error de transformación.

## Controles y criterio de éxito

Registrar las escalas y diagonales como escalares, sin guardar matrices densas.
Comprobar identidad de coordenadas iniciales y cotas, identidad del objetivo,
regla de la cadena y positividad/invertibilidad de D. Verificar en cada
candidato el objetivo/gradiente que recibió el solver frente a su evaluación
en coordenadas originales. El factor para FD local sigue siendo el de
longitud, sin la escala temporal de energía que causó la errata de Q.

Validar gradiente físico AD/FD MP80, pasos 1e-18/1e-22, acuerdo 1e-20,
AD/MP 1e-6, y KKT proyectado en las cajas físicas≤1e-5. Informar también el
residual en y pero NO usarlo para aprobar. Mantener además éxito del optimizador,
no empeoramiento de L y validación de longitud/SPD de G (80/120, cuadraturas,
reparametrización y tolerancias heredadas). Se preserva como inconcluso el
candidato que agota iteraciones aunque cumpla otro descriptor favorable.

C0 debe conservar longitud recta (error≤1e-8) y max|s|≤1e-6; no exigir que
redistribuya t uniformemente. Control analítico cuadrático con escalas diádicas
para objetivo, cotas y regla de la cadena, más controles de inversión,
subdivisión, verticalidad, arco y Hausdorff heredados.

Refinamiento 132/264: longitud normalizada≤1e-3, Hausdorff superior≤1e-3 y
brecha≤1e-5. Un refinamiento sólo pasa si ambos candidatos pasan. Comparaciones
entre métodos y Q0/Q1 son descriptivas y no condicionan éxito por coincidencia.
Hausdorff es euclídea en la carta (t,s), no distancia intrínseca de h.

## Condicionamiento y coste

En las seis referencias comunes, guardar resúmenes espectrales de H y DHD en
el bloque de variables no activas (tolerancia 1e-6); nunca matrices. Umbral de
casi nulos: 1e-10 max(1,max|lambda|). Registrar negativos, casi nulos, positivos
y razón del espectro positivo. No llamarla condición SPD cuando hay negativos
o casi nulos. La congruencia conserva la inercia en aritmética exacta; las
clasificaciones al umbral numérico pueden diferir y no certifican un mínimo.

Mismo maxiter=4800, maxfun=80000, maxls=40, ftol/gtol de config.json para ambos.
El gtol interno cambia de escala en y; por eso se exige el mismo KKT físico.
Informar iteraciones, evaluaciones de función/gradiente, rechazos y una llamada
de Hessiano inicial por búsqueda scaled frente a cero para reference. Los
espectros comunes son instrumentación del experimento, no coste necesario de
reference. Tiempos de preparación y optimización por separado en resources.json.
No afirmar presupuesto total idéntico: el precondicionador requiere preparación.

900 s y 512 MiB por corrida, incluyendo instrumentación y validación. No
ampliar para hacer pasar casos. PASS_NUMERICAL sólo si todos los caminos,
controles y refinamientos pasan. Identidades fallidas son FAIL; limitaciones
de optimización/validación son INCONCLUSIVE. Conservar primera corrida,
fallos y desconocidos; reproducir salidas científicas byte por byte, recursos
aparte. No certificar geodésicas, mínimos globales ni convergencia de una curva.
