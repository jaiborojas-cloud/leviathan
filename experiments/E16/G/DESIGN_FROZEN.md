# E16-G — Resolución numérica diagnóstica: protocolo nuevo

## Estatus y muestra

F permanece INCONCLUSIVE bajo su diseño original. G evalúa otro método sobre los
324 casos de F (12 estados × 3 paneles × 3 caminos × 3 composiciones), incluidos
sus 239 validados y 85 inconclusos. No hay exclusiones, pesos nuevos, entrenamiento,
selección ni confirmación independiente. La motivación y los casos difíciles ya
son conocidos. Los hashes fijan fuentes D y la tabla F para comparación posterior.
Rama sobre F, aún pendiente de integración al diseñar G. No se toca T2-A ni A–F.

## Rapidez e integral cerrada

Para γ(t)=p0+t v, C constante y B(t)=B0+tΔB, se conserva exactamente
H(t)=H0+tH1+t²H2 y q(t)=vᵀH(t)v=c+b t+a t².
En suma, a=b=0 y L=sqrt(c). En composiciones no lineales exigir a>0 y
δ=c−b²/(4a)>0, sin clipping, regularización adicional ni pisos numéricos.
Si no se cumplen estas condiciones, el caso queda INCONCLUSIVE.
Con t*=−b/(2a), x=t−t* y w=sqrt(δ/a),
P(x)=[x sqrt(a x²+δ)+(δ/sqrt(a)) asinh(x/w)]/2,
L=P(1−t*)−P(−t*). La fórmula evita inferir convergencia sólo entre cuadraturas.

## Contraste por cuadratura independiente de la primitiva

Evaluar sqrt(c+b t+a t²) directamente mediante Gauss–Legendre de órdenes
16,32,64 en una partición determinista que contiene 0,1 y todos los puntos
t*±w·2^k que estén dentro de (0,1), k=0,…,40; incluir t* si es interior.
En suma usar sólo [0,1]. Esta regla concentra resolución cerca de mínimos de
rapidez sin seleccionar casos ni modificar tolerancias según resultados.
Si el mínimo está fuera del intervalo, la misma regla sigue siendo aplicable.
Exigir error normalizado |A−B|/max(1,|A|,|B|):
16/32≤1e-12; 32/64≤1e-24; primitiva/64≤1e-24.
Todas las longitudes y márgenes de positividad deben coincidir a 80/120 cifras
con tolerancia 1e-40. No es una cota rigurosa de error de cuadratura.

Reparametrizar t=u² y usar las raíces cuadradas de los mismos puntos como
partición en u; integrar 2u sqrt(q(u²)) a orden 64 y contrastar con primitiva
a 1e-24. Invertir camino mediante q(1−t), aplicar de nuevo la primitiva y
contrastar a 1e-40. Bajo cada carta lineal fijada, transportar H y v, comprobar
los tres coeficientes q a 1e-40. Comprobar H polinómico contra B directo en los
cinco puntos 0,1/4,1/2,3/4,1. No se reclaman cartas no lineales arbitrarias.

## Positividad global: Bernstein con subdivisión acotada

Para H00(t) de grado 2 y det H(t) de grado 4, construir coeficientes de Bernstein
en [0,1] mediante b_i=Σ_{k≤i} a_k binom(i,k)/binom(n,k).
Usar escala global max(1,max|b_i|). Aceptar una hoja si todos los coeficientes
superan 1e-30 veces esa escala; si no, dividir por de Casteljau en 1/2 y visitar
primero la izquierda. Profundidad máxima 20 y 8191 nodos por polinomio.
No cambiar límites durante la corrida. Si se agotan, INCONCLUSIVE; una cota
insuficiente no prueba singularidad. Conservar mínimo normalizado de las hojas,
profundidad y nodos. No confundir el mínimo de una cota con el mínimo exacto.
Sylvester implica SPD si H00 y det son positivos en todo el intervalo.
Los coeficientes se calculan a precisión múltiple, sin intervalos dirigidos:
PASS_NUMERICAL es validación numérica global, no certificado riguroso de SPD.

## Controles previos

- q=5 y q=20: longitudes sqrt(5) y 2sqrt(5).
- q=(t−1/2)²+1e-12: primitiva/cuadraturas con los mismos criterios.
- H=diag(1,(t−1/2)²+1e-12): positividad global debe validarse.
- H=diag(1,(t−1/2)²): extremos positivos, interior singular; no validar SPD.
- H=diag(1,(t−1/2)²−1e-6): no validar SPD.
- Suma constante: primitiva/cuadratura/fórmula cerrada deben coincidir.

## Decisiones, comparación con F y salidas

FAIL si una identidad o control matemático esperado falla; INCONCLUSIVE si
fórmula no admisible, precisión, integración o cotas globales insuficientes;
PASS_NUMERICAL sólo si todos sus criterios pasan. La fase global prioriza FAIL,
después INCONCLUSIVE, después PASS_NUMERICAL. Conservar todos los casos y causas.
Un presupuesto agotado conserva lo disponible y no puede producir PASS global.

Guardar longitudes y q por caso, márgenes, cuadraturas, razones de los 216 pares,
controles y resumen por panel con denominadores. Comparar estado G con F sin
reescribir F. Las diferencias L_G−L_F son diagnósticas; incluso un F validado
puede diferir de G porque las tolerancias y los métodos son distintos.
Comparar repetición byte a byte de salidas científicas; recursos separados.
180 s y 512 MiB por corrida, un hilo. No ampliar muestra ni ajustar umbrales
para lograr resolver los 85 casos. Si persisten límites, conservarlos explícitos.

No se minimizan caminos, no se miden geodésicas ni curvatura y no se evalúa
predicción. Un futuro certificado riguroso requeriría propagar intervalos desde
los datos y funciones trascendentes hasta las desigualdades, no sólo redondear
las matrices calculadas. Congelar diseño y configuración antes de implementar.
