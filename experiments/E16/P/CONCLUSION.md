# Conclusión E16-P

**INCONCLUSIVE:** la representación influye en los candidatos observados,
pero la optimización de la familia ampliada queda pendiente bajo el presupuesto
congelado. No se concluye que la restricción de gráficos explique por sí sola
toda la inestabilidad anterior.

## Evidencia que aporta el contraste

1. Las fuentes de O no son estacionarias al liberar t: el gradiente
   longitudinal ronda 0,0031. Su pequeño gradiente transversal no controlaba
   estas direcciones. Esto delimita el alcance de la validación anterior.
2. Permitir mover ambos ejes produce retrocesos y desplaza el nodo previamente
   fijo. Las imágenes fixed/free difieren en Hausdorff ≈0,0035 pese a que sus
   longitudes difieren menos de 1e-5. No basta conservar o comparar longitud.
3. C0 permanece recto y pasa en ambas familias; Q0/Q1 conservan acuerdo
   descriptivo entre sí. Estos controles no certifican que los casos
   cuadráticos libres hayan resuelto su optimización.
4. Las cuatro optimizaciones libres alcanzan 4800 iteraciones. En 132, además,
   el KKT incumple 1e-5; en 264 sí lo cumple. La regla congelada no permite
   convertir las dos últimas en resultados aprobados a posteriori.

## Límites

La variante libre amplía las curvas admisibles dentro del mismo rectángulo;
no representa únicamente una reparametrización. Sus gradientes, número de
variables y condicionamiento difieren de `fixed`. El presupuesto común no
iguala el esfuerzo efectivo de optimización en ambas familias. No se comparan
mínimos globales, y la mayor flexibilidad no demuestra por sí sola cuál es
la causa geométrica de la concentración previa.

Todos los candidatos devueltos pasan las comprobaciones de integración,
positividad y concordancia AD/MP, pero sólo ocho pasan el protocolo completo.
No se excluyen los cuatro inconclusos ni se adopta el mejor como confirmación.
Los datos son los mismos sintéticos y sin entrenamiento; no hay validación
independiente de una hipótesis descubierta en O.

No se certifica singularidad, regularidad, unicidad ni existencia de una curva
límite. El conteo de retrocesos y la posición de nodos dependen de la carta
normalizada. Hausdorff no es la distancia geodésica de h. Dos resoluciones
con acuerdo no aportan un estimador certificado de error respecto al límite.

P no altera el resultado histórico de O ni sus criterios. Que `fixed` pase
longitud/Hausdorff en P no resuelve el criterio adicional de forma/indicador
que O conservó inconcluso.

La siguiente cuestión útil sería separar el condicionamiento de la
parametrización del criterio de terminación del optimizador, con controles y
un protocolo nuevo. No se ha demostrado aquí que la redundancia paramétrica
sea la causa del límite de iteraciones; tampoco se amplió el presupuesto ni
se cambió la regla de éxito para hacer pasar esta corrida.
