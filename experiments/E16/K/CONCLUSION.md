# Conclusión E16-K — Dos casos resueltos y refinamiento aún insuficiente

**Estado global INCONCLUSIVE.** Bajo el protocolo nuevo, pasan h01/1/producto
y h01/1/cuadrática; h00/0/cuadrática sigue sin alcanzar el criterio de refinamiento.
Los dos controles de suma pasan. J conserva sus tres casos INCONCLUSIVE originales.

| Caso | Estado K | Error normalizado 8→16 |
|---|---|---:|
| h00/0/cuadrática | INCONCLUSIVE | 0,0010237404 |
| h01/1/producto | PASS_NUMERICAL | 0,0000192997 |
| h01/1/cuadrática | PASS_NUMERICAL | 0,0001377818 |
| h00/0/suma | PASS_NUMERICAL | 0 |
| h01/1/suma | PASS_NUMERICAL | 0 |

El umbral 8→16 fue fijado en 0,001. No se redondeó el primer error para hacerlo
pasar, no se cambió el umbral ni se añadieron mallas después de observarlo.
Las quince resoluciones cumplen sus controles individuales; el acuerdo entre
ellas constituye un requisito adicional y no queda validado en ese caso.
Normalizar por max(1,|L_a|,|L_b|) no equivale a un porcentaje relativo cuando L<1.

## Integración y gradiente

La búsqueda usa la primitiva de cada tramo en lugar de cuadratura fija. El
residual ortogonal δ=||u−((u·d)/||d||²)d||² evita restar dos cantidades cercanas.
Autograd diferencia esta fórmula y su gradiente se contrasta con diferencias
centrales de alta precisión desde las fuentes D, a pasos 1e-18 y 1e-22.

Los 85 reinicios cumplen los controles de longitud, gradiente, residual KKT y
positividad global numérica. El error normalizado máximo autograd/MP80 fue
5,45e-15 frente a 1e-6 permitido. El máximo desacuerdo entre los dos pasos MP
fue 2,00e-34 frente a 1e-20. El mayor residual KKT entre los reinicios fue
9,93e-7 frente a 1e-5. Estas cifras son máximos observados redondeados hacia arriba,
no garantías rigurosas de derivación.

Para los candidatos elegidos se repiten primitiva G, cuadraturas localizadas,
reparametrización, positividad y acuerdo 80/120. Se conservan 290 registros de
tramos y los gradientes por coordenada. Todos los tramos y las salidas de los
reinicios pasaron la comprobación SPD. No se usaron pisos espectrales.

## Reinicios y diagnóstico de ramas

Se ejecutaron cinco inicializaciones fijas en la primera malla y seis en cada
malla posterior, incluyendo el camino anterior prolongado: 85 búsquedas en total.
Las 15 resoluciones presentan acuerdo de longitudes entre reinicios; el mayor
rango normalizado fue 3,40e-14 frente al umbral 1e-5. Ningún reinicio quedó fuera
del reporte ni se eligió una salida por pasar controles posteriores.

No se detectaron candidatos estacionarios de longitudes distintas bajo estos
reinicios y estas mallas K. La Hessiana simetrizada tuvo mínimo autovalor libre
normalizado positivo en todas las salidas de reinicios; el mínimo observado fue
0,0839. Esto es diagnóstico de segundo orden, no prueba de mínimo local o global.
Ningún candidato final de estos cinco casos alcanzó frontera.

**No se deduce que la dispersión J fuese exclusivamente un error de integración.**
J empleaba otras mallas y K cambió simultáneamente objetivo, reinicios y refinamiento.
No se volvió a optimizar la misma familia J con una sola variable cambiada.
El resultado establece acuerdo y gradientes contrastados en K, no una causa
única retrospectiva ni unicidad de la solución continua.

## Refinamiento anidado y comparación histórica

Las mallas 4/8/16 segmentos contienen los caminos anteriores mediante interpolación
lineal. Se verificó la conservación de longitud al prolongar y que la selección
no empeorara la recta o el camino heredado. Esto evita la falta de anidamiento
que limitaba la interpretación de las mallas J.

En h00/0/cuadrática, L16≈0,5075772923 y el cambio 8→16 sigue siendo mayor que el
criterio fijado, aunque todas las búsquedas y gradientes pasen. La estacionariedad
para una malla no implica que esa malla resuelva suficientemente el camino.

En h01/1/cuadrática, L16≈0,0449376268, ligeramente mayor que L_J8≈0,0449152266.
Las familias no coinciden y K no exigía superar J. Una longitud anterior menor
no demuestra una geodésica ni subsana sus controles fallidos; tampoco este
resultado autoriza declarar inválida aquella longitud validada como recorrido.
Las comparaciones completas están conservadas por caso.

## Evidencia y límites

Pasan 2085 controles y uno queda INCONCLUSIVE; cero FAIL. La primera corrida
consumió 36,81 s y 68,60 MiB, dentro de 300 s/512 MiB. Diseño congelado en
`2a1a9d3`; código y primera evidencia preservados en `49ee934`.
No se alteraron tolerancias, mallas o muestras después de medir.

El caso aún abierto requiere otro diseño de refinamiento, sin relajar su criterio
ni reetiquetar K. Esta fase no certifica Euler–Lagrange continua, distancia mínima,
una ley general RIPG ni capacidad predictiva. La muestra es diagnóstica y conocida;
no hay entrenamiento ni certificación intervalar de positividad.
T2-A y evidencia anterior permanecen intactos.
