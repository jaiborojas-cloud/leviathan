# Conclusión E16-G — Limitaciones numéricas resueltas en los casos de F

El protocolo nuevo valida **324/324 longitudes y 216/216 razones emparejadas**.
Los 85 casos antes inconclusos cumplen los criterios G; los otros 239 también.
No hay casos omitidos, reemplazados, fallidos ni inconclusos en esta corrida.
F sigue siendo INCONCLUSIVE con su protocolo y resultados originales.

| Estado en F | Estado en G | Casos |
|---|---|---:|
| PASS_NUMERICAL | PASS_NUMERICAL | 239 |
| INCONCLUSIVE | PASS_NUMERICAL | 85 |

## Cómo se resolvieron las limitaciones

**Integración.** Para q(t)=a t²+b t+c, el método usa la primitiva de sqrt(q),
contrastada con Gauss–Legendre 16/32/64 sobre intervalos fijados mediante el
mínimo y su anchura característica. La diferencia normalizada máxima 16/32 fue
6,77e-25; 32/64, 1,02e-46. El máximo contraste primitiva/64 fue 1,21e-89,
y el de reparametrización t=u², 2,86e-72. Todos cumplen sus tolerancias previas.
Estos máximos corresponden a los 324 casos, no a garantías universales del método.

**Positividad a lo largo de todo el segmento.** La subdivisión Bernstein
validó los dos criterios de Sylvester, H00>0 y det H>0. La máxima profundidad
fue nueve para H00 y doce para el determinante, frente al límite fijado de veinte.
Los máximos fueron 19 y 41 nodos, respectivamente, frente a 8191 disponibles.
El menor margen normalizado fue 1,79e-6 para H00 y 4,19e-13 para det H,
superiores al umbral 1e-30. Son mínimos de cotas suficientes, no mínimos exactos
de autovalores ni distancias a singularidad.

Estos resultados muestran que las cotas insuficientes de F no obligaban a
concluir pérdida de rango. El método nuevo consigue cotas positivas en todos
los casos evaluados. Se sigue trabajando con números de precisión múltiple:
**no se ha propagado un recinto intervalar desde las funciones trascendentes**,
por lo que no se anuncia un certificado riguroso de positividad.

## Evidencia y controles

Pasan 13 102 comprobaciones: 9862 de identidades y controles, 1944 de precisión
y 1296 de integración. El acuerdo 80/120 cifras tiene error normalizado máximo
1,21e-78 en los casos. Pasan transporte de rapidez bajo tres cartas lineales,
representación del tensor, inversión y reparametrización del recorrido.
Los controles positivo casi singular e integral estrecha pasan; los controles
singular e indefinido no reciben validación SPD, como se exigía.

La primera corrida se conserva en `f59b952`; no hubo ajuste retrospectivo del
protocolo, criterios, muestra o límites. El diseño está congelado en `7049807`.
La comparación conserva L_F y L_G por caso: resolver la validación no requiere
que la aproximación anterior sea idéntica a la nueva.

## Comparación completa de longitudes

| Composición respecto a suma | Válidas/total | Razón mediana [mín.; máx.] | Más corta / más larga |
|---|---:|---|---:|
| Producto | 108/108 | 0,42165 [0,16773; 1,28015] | 103 / 5 |
| Cuadrática | 108/108 | 0,63108 [0,29544; 1,48596] | 97 / 11 |

La separación numérica respecto a razón 1 es 1e-8. Son resultados descriptivos
de esta muestra completa, no de supervivientes filtrados por convergencia.
No permiten afirmar que la composición siempre acorta caminos: existen casos
más largos. Los paneles comparten estados y las diferencias entre ellos están
conservadas; no se presentan como observaciones independientes.

## Qué sigue abierto

El método se diseñó con conocimiento de las dificultades de F. Su éxito es una
resolución diagnóstica, **no confirmación empírica independiente** de RIPG ni de
una tendencia poblacional. Se conservan funciones, cométrica regularizada,
unidades y caminos particulares. No hay entrenamiento ni evaluación predictiva.
Tampoco se minimizan longitudes: no se han calculado distancias geodésicas.

Para comprobar transferencia del método, corresponde congelar configuraciones
independientes antes de medirlas. Para certificación rigurosa, hace falta otro
desarrollo con intervalos dirigidos y propagación completa. Ninguna de esas
dos tareas se da por realizada en G. T2-A y evidencia anterior permanecen intactas.
