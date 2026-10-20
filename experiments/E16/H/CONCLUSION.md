# Conclusión E16-H — Transferencia instrumental en configuraciones nuevas

La hipótesis instrumental congelada se satisface en esta muestra: **324/324
longitudes y 216/216 pares PASS_NUMERICAL**, sin FAIL, INCONCLUSIVE, exclusiones
ni reemplazos. Los 13 102 controles pasan. El resultado apoya transferencia del
método G dentro de la misma familia sintética, con pesos, entradas y perspectivas
nuevos fijados antes de medir.

## Separación respecto al desarrollo G

G fue diseñado para resolver dificultades conocidas de F. H usa los primeros
sorteos de PCG64 con semillas nuevas, sin filtrar por rango, positividad o longitud.
Se conserva la red 2→2→1 sin entrenamiento, cométrica (F+0.01I)^(-1), funciones,
paneles y estructura de tres caminos. Los puntos y sus segmentos concretos son
nuevos; sus resultados no intervinieron en el diseño del método.

El diseño y los datos se congelaron en `3c96c95`, antes del código adaptado y
la primera medición. Las 14 funciones numéricas y auxiliares compartidas son
idénticas por AST a G; un adaptador reproducible limita los cambios a entrada,
procedencia y eliminación del emparejamiento con los casos F. No cambian las
precisiones, tolerancias, reglas de decisión o presupuestos.

## Evidencia instrumental

| Comprobación en los 324 casos | Máximo error normalizado |
|---|---:|
| Cuadratura 16/32 | 3,50e-25 |
| Cuadratura 32/64 | 5,26e-47 |
| Integral cerrada / cuadratura 64 | 6,20e-90 |
| Reparametrización t=u² | 7,19e-66 |
| Precisión 80/120 cifras | 1,54e-80 |

Son máximos observados redondeados hacia arriba; no cotas rigurosas de error.
También pasan las identidades del tensor, transporte bajo tres cartas lineales,
inversión de camino y controles positivos/negativos heredados de G.

Las cotas globales de positividad alcanzan un margen normalizado mínimo de
1,13e-4 para H00 y 2,55e-8 para det H, frente al umbral 1e-30. La profundidad
máxima fue tres y cinco, respectivamente, de veinte disponibles; los máximos
de nodos fueron siete y quince, de 8191 disponibles.
Estos casos exigieron menos subdivisión que los casos diagnósticos G: H no
es una prueba exhaustiva de situaciones próximas a singularidad.

La primera corrida tomó 19,01 s y 39,61 MiB, dentro del presupuesto 180 s/512 MiB.
Código y resultados se conservan en `07107e9`; no hubo ajustes después de medir.

## Longitudes: descripción de la muestra completa

| Composición respecto a suma | Válidas/total | Razón mediana [mín.; máx.] | Más corta / más larga |
|---|---:|---|---:|
| Producto | 108/108 | 0,26450 [0,11136; 0,46391] | 108 / 0 |
| Cuadrática | 108/108 | 0,30556 [0,10190; 0,61719] | 108 / 0 |

La separación numérica respecto a razón 1 es 1e-8. No se había predicho una
dirección de cambio de longitud. Este acortamiento es descriptivo, depende de
las unidades y funciones escogidas y **no demuestra que componer siempre acorte**:
G conserva contraejemplos con razones mayores que uno.

## Alcance y límites que siguen abiertos

El resultado satisface la prueba prospectiva instrumental específica; no estima
una tasa universal de éxito. Las 324 longitudes comparten estados, entradas,
puntos y paneles, por lo que no son 324 réplicas estadísticamente independientes.
Se conserva una misma familia y un solo conjunto nuevo de entradas y perspectivas.
No se ha probado otra arquitectura, datos reales ni comportamiento tras entrenar.

Las longitudes son de caminos prefijados; no se minimizan, no se conocen distancias
geodésicas ni se mide curvatura. La positividad se valida numéricamente con alta
precisión, sin intervalos dirigidos desde las funciones trascendentes: no es
un certificado riguroso. No se evalúa capacidad predictiva ni se demuestra
una ley general RIPG. F conserva INCONCLUSIVE y T2-A permanece intacto.

Con el instrumento transferido en esta muestra, una fase posterior puede fijar
un problema geodésico acotado y sus controles antes de optimizar caminos. Esa
fase necesitaría distinguir un camino más corto hallado de un mínimo global;
no se considera realizada aquí.
