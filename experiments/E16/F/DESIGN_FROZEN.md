# E16-F — Longitudes de caminos: diseño congelado

## Pregunta y muestra

¿Los cambios locales de escala y forma se traducen en cambios de longitud de
caminos prefijados? Análisis exploratorio sobre los 12 estados y tres paneles
sintéticos de D, sin entrenamiento, filtrado ni muestra independiente.
Se conservan exactamente las funciones y C=(F+0.01I)^(-1) de D, con hashes fijos.
Los tres puntos p0=(0.8,0.3), p1=(-0.4,0.9), p2=(0.2,-0.6) definen los segmentos
orientados 0→1, 1→2 y 2→0. No se cambia un camino si resulta problemático.
Son 324 longitudes y 216 razones respecto a la suma, con mismo estado/panel/camino.
No hay hipótesis direccional ni pruebas de significación estadística.

## Matemática

γ(t)=a+t(b−a), v=b−a, 0≤t≤1. Para cada composición,
L_h(γ)=∫sqrt(vᵀh(γ(t))v)dt. Los B de suma son constantes; los de producto y
cuadrática son lineales en p. Con B(t)=B0+tΔB y C constante en el camino:
H(t)=H0+tH1+t²H2, H0=B0CB0ᵀ, H1=ΔBCB0ᵀ+B0CΔBᵀ, H2=ΔBCΔBᵀ.
La rapidez al cuadrado es un polinomio cuadrático q(t)=vᵀH(t)v.
Comprobar esta representación contra B directo en t=0,1/4,1/2,3/4,1.

## Positividad durante todo el recorrido

No basta muestrear extremos o nodos. En cada uno de 64 subintervalos uniformes,
representar H00(t) (grado 2) y det H(t) (grado 4) en base de Bernstein.
Para p(t)=Σ a_k t^k, trasladar al subintervalo t=u+w s y usar
b_i=Σ_{k≤i} a'_k binom(i,k)/binom(n,k).
El mínimo de los coeficientes acota p en el subintervalo en aritmética exacta.
Exigir ambos mínimos globales positivos con margen relativo >1e-30 respecto a
max(1,max|coeficientes|), y acuerdo 80/120 cifras de los mínimos escalados.
Sylvester implica SPD en todo el camino si se cumplen esas desigualdades.
Aquí se evalúan con precisión múltiple, sin intervalos dirigidos: son
comprobaciones numéricas globales de positividad, no certificados rigurosos.
Cota no positiva o margen insuficiente → INCONCLUSIVE, no prueba de singularidad.
No subdividir más ni añadir pisos espectrales según el resultado.

## Integración y controles

Gauss–Legendre de orden 16 compuesto en 4,8,16 paneles, a 80 y 120 cifras.
La longitud reportada es la de 16 paneles a 120 cifras. Dos diferencias sucesivas
4/8 y 8/16, normalizadas por max(1,|L1|,|L2|), deben ser ≤1e-10.
Acuerdo entre precisiones para las tres estimaciones ≤1e-40.
Comparar longitud con camino invertido y con reparametrización t=u²
(integrando 2u sqrt(q(u²))) mediante la regla de 16 paneles, tolerancia 1e-10.
Bajo p=Jq, transformar camino y velocidad por J^(-1) y H por JᵀHJ:
los tres coeficientes de rapidez deben coincidir a 1e-40 para cada carta fija.
Así se verifica la longitud del mismo camino, no se elige otro segmento tras
un cambio de coordenadas. Cartas lineales invertibles, no se prueba cualquier carta.

Controles: métrica identidad y segmento (0,0)→(1,2), longitud sqrt(5);
métrica 4I, longitud 2sqrt(5); suma constante coincide con fórmula cerrada.
Negativo: H(t)=diag(1,(t−1/2)²), positivo en extremos y singular en el interior,
debe quedar sin positividad global validada.

## Clasificación y salidas

FAIL: identidad/control incumplido. INCONCLUSIVE: convergencia, precisión o
positividad global insuficiente. PASS_NUMERICAL: todos los criterios satisfechos.
No omitir longitudes inconclusas del CSV ni contarlas como evidencia validada;
resúmenes de razones válidas con denominadores e inconclusos explícitos.
Razones >1+1e-8 o <1−1e-8 indican separación numérica, no relevancia científica.
Guardar longitudes por caso, razones emparejadas, controles, resumen por panel y
composición, procedencia, recursos y hashes. Repetir y comparar salidas científicas
byte a byte. Presupuesto 120 s/512 MiB, un hilo, por corrida.

Una longitud de camino no es una distancia geodésica: no se minimiza sobre caminos.
Incluso la suma, constante y con segmento minimizante en el plano completo, no
establece una geodésica de las métricas no lineales. No se infiere curvatura,
capacidad predictiva ni ley universal. No se modifica T2-A ni evidencia A–E.
Congelar este documento y config en Git antes de implementar o medir.
