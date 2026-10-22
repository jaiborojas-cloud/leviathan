# Conclusión E16-N

**INCONCLUSIVE:** las mallas graduadas mejoran la discrepancia observada,
pero todavía incumplen las tolerancias de forma y Hausdorff.

## Lo que la evidencia permite decir

1. Una parte de la separación al mismo parámetro longitudinal es sensible al
   criterio de comparación: en N64→128, el máximo transversal ≈0,0287 contrasta
   con Hausdorff ≈0,00185. Se miden magnitudes diferentes.
2. Los nuevos nodos y su continuación producen una menor separación 64→128
   que la malla uniforme archivada (≈0,00658), bajo esta configuración concreta.
3. Persiste una diferencia entre las imágenes de las curvas por encima de
   0,001: el intervalo Hausdorff queda enteramente sobre el umbral. El resultado
   no se explica sólo por emparejar puntos al mismo t.
4. La estabilidad de longitud, el acuerdo Q0/Q1 y los nueve caminos válidos
   no bastan para declarar convergencia de forma. C0 pasa y permanece recto.

## Alcance y límites

No se aisló causalidad exclusiva de la distribución de nodos: al graduarlos
cambian los subespacios de polígonos admisibles y la historia de optimización.
El remuestreo de M32 cambia la forma en ≈0,00401 para Q0 y ≈0,00795 para Q1;
se conservan las mediciones iniciales y ambos linajes. No se equipara la menor
longitud encontrada en N con un mínimo global.

Los cambios entre 64/128 tienen máximos cerca de t≈0,982, pero la regla
heredada de concentración en la cola no los declara localizados. No se deduce
una singularidad, una bifurcación, unicidad ni una capa límite demostrada.
La métrica h sólo recibe las comprobaciones numéricas heredadas de G; no se
aportan certificados con aritmética dirigida. Hausdorff es euclídea en la carta
de perspectivas declarada y no una distancia geodésica de h.

Se trabajó sobre el mismo estado sintético, sin entrenamiento y sin datos
independientes nuevos. M conserva su INCONCLUSIVE. No se modifica ningún
protocolo ni resultado previo, ni material de T2-A.

Un siguiente protocolo podría estudiar el comportamiento de la curva límite
cerca del extremo y un estimador de error que guíe el refinamiento. Requeriría
criterios previos nuevos; esta corrida no autoriza declarar resuelta la
convergencia ni continuar refinando hasta obtener un resultado favorable.
