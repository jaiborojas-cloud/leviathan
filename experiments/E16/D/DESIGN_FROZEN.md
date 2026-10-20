# E16-D — Diseño congelado v1, previo al código y resultados

2026-10-20. Nueva réplica instrumental de C, elegida tras su diagnóstico positivo
sobre datos conocidos. Pregunta primaria: ¿los tres métodos conservan concordancia
y margen de rango en estados, entradas y puntos principales no usados para
seleccionar el método? No se propone entrenar ni validar generalización.

## Congelación y procedencia

config.json es la fuente normativa de todos los números. Antes de calcular
cualquier observable se generaron 12 vectores θ∈[−0.8,0.8]⁹ con PCG64 semilla
20261020 y 12 entradas z∈[−1.2,1.2]² con PCG64 semilla 20261021, redondeados
a seis decimales. Se persistieron sin filtrar por rango, salida, error, etiqueta
ni resultado favorable. Se usan los valores guardados, no se requiere regenerar
el RNG. No se alteran después de abrir resultados.

Tres paneles: P0 completo, P1 índices pares y P2 impares (base cero).
Tres puntos nuevos: (0.8,0.3),(−0.4,0.9),(0.2,−0.6).
Red 2→2→1 tanh/Bernoulli, nueve parámetros, sin entrenamiento. Se mantiene
la definición de S₁,S₂, suma/producto/cuadrática y cométrica de mathematical_spec.md.

12 estados×3 paneles×3 puntos×3 composiciones=324 configuraciones principales.
Dos controles por estado/panel=72; total 396 decisiones de rango.
Negativos por omisión de mixtos en las 216 configuraciones no lineales.
Sin exclusiones, reemplazos ni ampliación según resultados. El tamaño 12 es
presupuesto de cobertura instrumental, no cálculo de potencia predictiva.

## Métodos y criterios

Reutilizar la implementación de referencia C identificada en provenance.json,
con adaptación explícita de rótulos, configuración y la lógica que distingue
rango discordante inequívoco de falta de precisión. No se ejecutan scripts de C
sobre sus antiguos estados, ni se modifica el outcome INCONCLUSIVE de B.
Se declara reutilización de código: es réplica del método, no cuarta implementación
independiente. Persistir hash del código base y diff de la adaptación.

Mismos métodos: autodiff float64, referencia explícita 80/120 dps, FD4 a 80 dps
con δ=0.002 y 0.001. Mismo corte τ=1e−8 max(1,σ_max(U_ref)).
Positivo si σ>10τ, nulo operacional si σ<τ/10; banda restante INCONCLUSIVE.
Precisión 80/120: ||U80−U120||F≤1e−50 max(1,||U120||F).
Autodiff: cota triangular transportada≤τ/10 y error B máximo
≤1e−10+1e−9 max|B_ref|. FD4: error transportado≤τ/10 en AMBOS pasos.
Márgenes σ±error deben quedar del mismo lado del corte y todos los métodos
deben dar igual rango. La identidad de descomposición del error y su desigualdad
triangular se contrastan a tolerancia 1e−60 max(1,||U_ref||F), a 120 dps.
Control conocido: rango 0 y rango 1, respectivamente. Negativo: discrepancia
transportada del B truncado >τ; de lo contrario INCONCLUSIVE de sensibilidad.

Justificación: funciones suaves, entradas/pesos moderados, regularización SPD
≥0.01I y FD4 O(δ⁴); se conserva la tolerancia del método validado C en vez de
calibrarla sobre D. Esta expectativa no acota a priori todas las constantes de
truncamiento: si un caso no pasa, se conserva como tal.

PASS_NUMERICAL por configuración sólo si todas las comprobaciones y márgenes
aplican y pasan. Una identidad incumplida es FAIL. Precisión insuficiente o rango
en banda ambigua es INCONCLUSIVE, incluso si los métodos difieren en rango.
Cuando la referencia está separada y las cotas cumplen, distinto rango inequívoco
o control conocido incumplido es FAIL. Márgenes insuficientes son INCONCLUSIVE.
La implementación aplicará estas prioridades explícitas; no ajustarlas al ver D.

Objetivo instrumental conjunto: 396/396 PASS_NUMERICAL y 216/216 negativos
detectados. Cualquier FAIL impide el PASS conjunto; cualquier INCONCLUSIVE lo
mantiene inconcluso, sin eliminar estados. Preservar corrida y código fallidos
antes de corregir; versión y resultados nuevos, sin retocar el diseño.

## Observables, presupuesto e interpretación

Primarios: estado de cada control, rango, errores transportados, separación del
corte y sensibilidad de negativos. Secundarios descriptivos: cambio de rango de
producto/cuadrática respecto de suma (108 tríos por panel/punto/estado), errores
absolutos/relativos de B y h y sensibilidad entre paneles. No se fija un efecto
mínimo o dirección empírica que se pueda seleccionar retrospectivamente.

CPU, una hebra BLAS, float64 y mpmath; presupuesto 120 s/corrida, memoria objetivo
512 MiB. Versiones: Python 3.12.14, NumPy 2.3.5, autograd 1.8.0, mpmath 1.3.0.
No entrenamiento, checkpoints T1/E15/T2-A, integración geodésica ni curvas de
accuracy. Sin modificar A/B/C, protocolo ni carpeta claude de T2-A.

Guardar diseño, configuración, derivación, procedencia, código y diff, tablas,
resumen, entorno/tiempos, manifest y progreso después de cada estado/panel.
Tiempos fuera de tablas deterministas. Una réplica numérica independiente de
las configuraciones previas no equivale a evidencia predictiva de aprendizaje.
