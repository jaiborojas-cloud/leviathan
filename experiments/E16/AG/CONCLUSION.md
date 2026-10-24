# E16-AG · conclusión exploratoria v1

**Q1 PASS · Q2 FAIL · Q3 FAIL · Q4 INCONCLUSIVE · Q5 FAIL_DESCRIPTIVE.**
Corrida VALID_EXPLORATORY: 80/80 estados analizados, 80 escapes refinados,
11/11 controles previos PASS y 40/40 contrastes de respuesta analítica PASS.
No hubo sustituciones, fallos numéricos ni casos de DRAG_5000. La corrida
completa tardó480.724688s con dos procesos; los tiempos por estado se conservan.

## Qué se midió y qué se conoce realmente

Se distinguieron ANTES de medir tres objetos: ρ_borde (semirrectas hasta el
infinito), d_borde (frontera de la completación métrica) y d_esc (umbral finito
||P||∞=150). **Un escape a150 no es, en general, una cota superior demostrada
de d_borde.** La cota teórica es d_borde≤ρ; Q1 es una comparación operacional
entre instrumentos y no una prueba nueva de esa desigualdad.

Los40 nuevos estados tienen27 componentes en tres grupos de nueve rasgos
iguales, tres vértices no colineales, M SPD con Q de rango2 y ε positivo,
y cuatro amplitudes métricas fijadas sin observar escapes. Su imagen es un
triángulo plano: d_borde se obtiene proyectando el baricentro a sus aristas;
ρ exacta es el mínimo de distancias a tres vértices y tres puntos medios.
Se incluyeron las direcciones de empate exacto de logits, que una rejilla
angular sola puede omitir. Véanse [prueba](THEORY.md) y [diseño](DESIGN_FROZEN.md).
Es una subfamilia deliberadamente plana y con rasgos duplicados, no una réplica
general de la curvatura ni de la patología de T2.

Los40 AF conservan exactamente sus M/f sintéticos archivados. Aquí se usa un
horizonte nuevo1.5ρ, no el Rmax=.2 de AF. Que todos escapen ahora no cambia
su estado histórico «sin escape observado hasta.2». Su d_borde real sigue
**UNKNOWN**; no se sustituye por d_esc.

## Comparación operacional por grupo

| Grupo | Estados | Escapes | Pares válidos | Mediana ρ/d_esc | Máximo ρ/d_esc | Spearman(ρ,d_esc) | Mediana tρ/texp |
|---|---:|---:|---:|---:|---:|---:|---:|
| Triángulos nuevos | 40 | 40/40 | 40 | 1.999025 | 4.266810 | 0.939212 | 70.3593 |
| AF | 40 | 40/40 | 40 | 17.069014 | 210.885907 | 0.122326 | 0.568964 |
| Todos | 80 | 80/80 | 80 | 2.440186 | 210.885907 | 0.882747 | 17.1733 |

**Q1 PASS:** ρ≥d_esc en los80, con los errores fijados y refinamiento angular.
Los contrastes de cuatro combinaciones720/1440×GL400/800 y escape coarse/refinado
mantienen el veredicto. No certifica el mínimo de todas las direcciones.

**Q2 FAIL:** se exceden los umbrales congelados de mediana≤1.2 y máximo≤2.
La comparación con respuesta real conocida también muestra falta de ajuste:
en los40 triángulos, **mediana ρ/d_borde=1.998884 y máximo4.266419**.
No es sólo un artefacto de la frontera finita. d_esc/d_borde cae entre
0.9998696563 y0.9999946379: en este grupo el proxy finito está cerca de la
distancia real. El error relativo máximo de ρ numérica frente a su respuesta
analítica es8.27e-16. En AF, los cocientes grandes no miden por sí solos la
holgura respecto al borde verdadero: el umbral fijo de carta puede estar muy
lejos de la frontera al infinito, especialmente con rasgos pequeños.

**Q3 FAIL:** el umbral era≥.9 global y por grupo. Se cumple en triángulos,
pero no en AF ni globalmente, de forma estable entre las variantes archivadas.
En los triángulos, Spearman(ρ,d_borde real)=0.939212, igual al orden frente
a d_esc en esta muestra. **No se sabe si ρ ordena la distancia real de AF:**
su baja correlación frente al umbral150 no demuestra desorden frente al borde
infinito. Hay escalas emparejadas por semilla, sin p-valores de80 réplicas
independientes ni validación externa.

**Q4 INCONCLUSIVE:** no hubo estados que agotaran5000 pasos. Máximo AF187
pasos; nuevos40. La carta plana de cara de los nuevos evita la singularidad de
las coordenadas naturales; no permite concluir ausencia de arrastre en éstas.
No se reprodujo ni se refutó el patrón0.6–1.0ρ de casos con arrastre del
diagnóstico. Un escape no se reclasifica como arrastre.

**Q5 FAIL_DESCRIPTIVE:** el cálculo completo de ρ fue más rápido que la
exponencial en AF (razón mediana.568964), pero más lento en los triángulos
(70.3593). Aquí la exponencial se integra en una carta plana de respuesta
conocida. El coste de cuatro cuadraturas y refinamientos de ρ se compara con
el haz y su refinamiento, no con una integral geométrica idéntica. No hay una
ventaja universal de coste establecida ni benchmark de procesos aislados.

## Controles, precisión y conservación

11/11 PASS: binario 1D con d=ρ=1/√2 (GL400/800 y MP80); triángulo unitario
con d=ρ=1/√6 y escape de cara; cambio afín del origen y ρ en un nuevo y
primer AF; K plano AD y lectura de longitud continua AC archivada. No se
reejecutaron AD/AC ni se alteraron sus fuentes. Los40 nuevos además pasan
la igualdad analítica de ρ, la transformación métrica de carta y d_esc≤d_borde.

La diferencia máxima relativa entre ρ refinada y las cuatro cuadraturas es
0.000867074 (<.5% congelado). Los contrastes MP80 de velocidad direccional
tienen error≤9.46e-16; no constituyen una integral MP ni búsqueda angular
certificada. Los avisos de quad se preservan en [execution.log](execution.log),
con todas las salidas. La verificación MP de respuestas triangulares usa sólo
los inputs sintéticos, sin reintegrar geodésicas.

Diseño e9e4034 → código6f814a2 → resultados. SHA de geometry.py verificado
antes de importar, fuente intacta y guarda AF sin excepciones de acceso T2.
Se leyó únicamente el documento contextual autorizado en la referencia fija
de [progress.md](progress.md); ningún estado ni tabla adicional T2.
El archivo [arrays.csv](results/run_v1/arrays.csv) permite verificar los arrays
originales conservados fuera de Git. [Diccionario](DATA_DICTIONARY.md),
[recursos](results/run_v1/resources.json) y [errata de dependencias](ERRATA_ENTORNO.md).

## Lo que permanece abierto

ρ es una cota superior útil, pero en esta subfamilia no resulta ajustada al20%
típico. La distancia real y su orden en familias no planas como AF siguen sin
resolverse. Hace falta un protocolo nuevo con borde real identificable y
arrastre natural observable, que separe la truncación finita de la completación
geométrica y preserve fallos. No se afirma certificado riguroso, transferencia
a T2, mínimo global de la exponencial ni igualdad ρ=d_borde.

Verificación final PASS:480 hashes de arrays y80 estados, contraste MP80
independiente de respuestas triangulares con error relativo máximo7.20e-15,
resúmenes y24 variantes derivadas coherentes. Los mínimos seleccionados de
quad tienen error relativo estimado máximo5.79e-14; se conservan los2566
intentos y sus avisos. [Registro](verification.json). No se reintegró geometría.
