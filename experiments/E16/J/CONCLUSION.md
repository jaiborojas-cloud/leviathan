# Conclusión E16-J — Estabilidad discreta parcial

**Estado global INCONCLUSIVE.** De los 27 casos, 24 cumplen todos los criterios
y tres no. No hay fallos de identidad, exclusiones ni ajustes retrospectivos.
Las 243 búsquedas científicas terminaron con éxito declarado por el optimizador;
eso no bastó para validar estacionariedad y estabilidad en todos los casos.

| Puntos interiores | PASS_NUMERICAL | INCONCLUSIVE | Total | Casos con frontera activa |
|---|---:|---:|---:|---:|
| 2 | 25 | 2 | 27 | 2 |
| 4 | 27 | 0 | 27 | 2 |
| 8 | 26 | 1 | 27 | 2 |

El estado por caso incluye las tres resoluciones y ambos criterios de refinamiento:
no se ocultan dificultades de una malla porque otra dé un resultado favorable.

## Tres límites preservados

| Caso | Causa del estado INCONCLUSIVE |
|---|---|
| h00/0/cuadrática | Cambio normalizado 4→8 de 0,00169167, mayor que 0,001 permitido. Las resoluciones pasan individualmente, pero no el acuerdo exigido. |
| h01/1/producto | En N=2, dispersión entre inicializaciones de 0,00054543, mayor que 0,00001. Todas declaran éxito y el candidato tiene pequeño residual, pero encuentran longitudes diferentes. |
| h01/1/cuadrática | En N=2 falla acuerdo de gradientes 32/64, residual KKT y contraste objetivo/referencia; en N=8 sigue fallando acuerdo de gradientes. |

Para h01/1/cuadrática, en N=2 la diferencia normalizada de gradiente fue
7,2920e-5 frente a 1e-6 permitido, y el residual KKT 7,2921e-5 frente a 1e-5.
El objetivo de búsqueda difirió de la referencia de alta precisión en 2,2074e-8,
frente a 1e-8. En N=8 la diferencia de gradiente fue 4,8469e-6, aún superior
a 1e-6, aunque el residual KKT sí quedó dentro de 1e-5.
No se aumentó el orden de integración del optimizador ni el número de reinicios
para resolver estos casos después de observarlos.

La normalización usa max(1,|L_a|,|L_b|): los umbrales de refinamiento no son
porcentajes relativos de longitud cuando L<1. Dependen de las unidades declaradas.

## Interiores y fronteras: interpretaciones distintas

22 casos quedan INTERIOR_STABLE_DISCRETE: **nueve son controles de suma y trece
son no lineales**. Pasan las tres resoluciones, los reinicios, la comparación
de gradientes, residual discreto y refinamiento. No es una prueba de Euler–Lagrange
continua: sólo se variaron desplazamientos normales de vértices de una familia.

Dos casos cuadráticos quedan BOUNDARY_LIMITED, ambos con dos nodos activos en N=8:

| Caso | Residual KKT discreto | Norma del gradiente libre |
|---|---:|---:|
| h01/2/cuadrática | 6,54e-9 | 0,01574 |
| h02/2/cuadrática | 5,50e-9 | 0,04313 |

Pasan los criterios restringidos, pero su gradiente libre no es pequeño.
El segundo es el caso que ya alcanzó frontera en I. No se amplió su dominio;
no se presenta ninguno como geodésica libre. Los tres casos restantes son UNRESOLVED.
Las etiquetas geométricas se conservan separadas del éxito del optimizador.

## Qué sí pasó

Se registraron 252 búsquedas (243 científicas y nueve euclídeas), 81 resoluciones
y 972 registros de tramos, incluyendo las evaluaciones de referencia a 80/120 cifras.
Todos los tramos registrados tuvieron primitiva admisible y cotas numéricas
positivas para H00 y det H. Los contrastes de precisión pasaron; no se interpretan
los inconclusos de refinamiento o gradiente como evidencia de singularidad.

De 5913 controles, 5907 pasan y seis quedan inconclusos; cero FAIL. Los controles
euclídeos y los de suma constante pasan. La primera corrida tomó 14,60 s y
70,38 MiB, dentro del presupuesto 300 s/512 MiB. El diseño quedó congelado en
`c2cd4a8`; código y primera evidencia se conservaron en `d1a342a`.

Las comparaciones con I están guardadas por caso y son descriptivas. Las mallas
2/4/8 no están anidadas ni contienen necesariamente la esquina I en t=1/2:
no se asumió monotonía de longitudes ni se exigió superar I como aceptación.
Una reducción adicional no subsana el incumplimiento de los criterios J.

## Alcance y siguiente trabajo

Se obtiene evidencia de estabilidad a resolución finita en una parte de esta
muestra, no una distancia geodésica demostrada ni un mínimo global. La familia
sólo incluye gráficas transversales sobre la cuerda, dentro del mismo corredor.
Los datos se reutilizan y comparten estados/paneles; no hay entrenamiento,
evaluación predictiva ni confirmación de una ley universal RIPG.
La positividad no está certificada mediante intervalos dirigidos.

Antes de aumentar la familia otra vez, conviene un protocolo diagnóstico nuevo
que controle el error **del gradiente** de integración y la multiplicidad de
resultados entre reinicios, además de fijar refinamientos más informativos.
J conserva sus tres casos inconclusos; resolverlos no consistiría en relajar
sus umbrales. T2-A y evidencia anterior permanecen intactos.
