# Conclusión E16-I — Mejoras dentro de una familia de caminos

El diseño fijado encontró caminos de dos tramos más cortos que las rectas en
**18/18 casos no lineales**. Los nueve controles con métrica constante de suma
conservaron la recta. Los 27 casos cumplen validación numérica de longitud,
positividad a lo largo del recorrido y estabilidad entre las dos resoluciones
de búsqueda. Pasan 5533 controles; no hay casos excluidos o inconclusos.

| Métrica | Casos validados | Mejoras >1e-8 relativo | Reducción de longitud | Fronteras activas |
|---|---:|---:|---|---:|
| Suma | 9/9 | 0 | Cero salvo redondeo | 0 |
| Producto | 9/9 | 9 | 0,06006 % a 4,32540 % | 0 |
| Cuadrática | 9/9 | 9 | 0,0001942 % a 17,61535 % | 1 |

Son reducciones respecto al segmento recto bajo **la misma métrica** en cada
caso. No son comparaciones predictivas entre métricas ni porcentajes de mejora
fuera de esta muestra. La ganancia diminuta negativa de suma (≈−1,62e-121)
es redondeo a precisión múltiple, no un empeoramiento sustantivo.

## Qué se optimizó

En los tres primeros estados H y panel P0 se fijó
m(s)=(a+b)/2+s R(b−a), s∈[−1/4,1/4]. La búsqueda sólo modifica ese escalar y
conserva extremos. Se comparan las longitudes a→m(s)→b con a→b. Se incluyen
s=0 y los extremos de la familia como candidatos, además de la salida de la
búsqueda bounded. La segunda resolución sólo evalúa estabilidad; no sustituye
el candidato principal por el mejor de ambos.

Se registran 54 búsquedas científicas (dos por caso) y 1231 evaluaciones,
incluidas las de los controles euclídeos. No se retocaron dominio, umbrales,
semillas o criterios tras medir. La primera corrida se conserva en `b5c1709`;
el diseño fue congelado antes de programar en `acab94e`.

La frontera se alcanza en **h02, camino 2, cuadrática**, s=0,25, con reducción
2,79367 %. Este caso está limitado por el dominio fijado: no se amplió para
buscar una mejora adicional. Tampoco los candidatos interiores constituyen
por sí solos pruebas de mínimo local o global.

## Validación y evidencia

Se conservan 216 registros de tramos: recta y dos tramos principales a 80/120
cifras, más los dos tramos del ajuste de estabilidad a 120 cifras por caso.
La validación principal compara integral cerrada, cuadraturas localizadas
16/32/64, reparametrización, tensor directo y transporte de rapidez bajo tres
cartas lineales. Las fórmulas y cotas provienen de G con hash fijo.

El error normalizado máximo de precisión fue 4,99e-81 y el de integración
2,69e-25, dentro de sus tolerancias. La diferencia de longitud entre las dos
resoluciones de búsqueda fue como máximo 7,40e-17, frente a 1e-8 permitido.
Estas cifras son observaciones numéricas redondeadas hacia arriba, no cotas
rigurosas de error.

Las cotas Bernstein validaron H00 y det H en todos los tramos registrados.
Los mínimos de sus márgenes normalizados fueron 5,52e-7 y 5,82e-14; las
profundidades máximas, seis y siete frente al límite veinte. Esto valida
numéricamente los recorridos elegidos; no certifica SPD en toda la región
que podrían explorar todos los caminos admisibles.

## Interpretación y límites

Encontrar una ruta validada más corta demuestra que la recta no minimiza la
longitud entre todas las rutas admisibles en esos 18 casos, a la precisión
evaluada. **No demuestra que la ruta encontrada sea una geodésica.** Tiene una
esquina permitida y sólo se ha buscado en una familia de una dimensión, con un
algoritmo local de precisión finita. No hay certificado de óptimo global.

La muestra reutiliza H y tres de sus estados; el estudio es exploratorio y las
observaciones comparten datos. No se evalúan entrenamiento, predicción ni una
ley universal RIPG. La positividad se comprueba sin intervalos dirigidos.
T2-A y resultados previos, incluido F INCONCLUSIVE, permanecen intactos.

El siguiente diseño puede enriquecer la familia de caminos o formular la
minimización de energía/geodésicas con controles de convergencia de discretización,
estacionariedad y restricciones. Debe fijarse antes de ejecutarlo y distinguir
siempre una mejora encontrada de una distancia geodésica establecida.
