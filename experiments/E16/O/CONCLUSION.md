# Conclusión E16-O

**INCONCLUSIVE.** El refinamiento guiado por el indicador reduce la separación
de Hausdorff entre rondas y el cambio de longitud, pero no alcanza estabilidad
al mismo parámetro longitudinal ni el criterio terminal del indicador.

## Lo observado

- Q0 y Q1 reciben las mismas cuatro bisecciones, conservando todos sus nodos.
  La fracción capturada supera el 50 % requerido sin activar el límite de 32.
- Las ocho transiciones cumplen longitud y Hausdorff. Al final, las cotas
  superiores de Hausdorff son ≈0,0001426 y ≈0,0001424, menores que 0,001.
  Esto es acuerdo numérico entre pares consecutivos, no una demostración de
  convergencia ni una cota del error acumulado respecto al límite.
- El cambio al mismo t sigue alrededor de 0,0212 y el indicador máximo cerca
  de 19. No hay dos transiciones estables conforme a la regla congelada.
- La mayor pendiente aumenta al estrecharse un intervalo que termina en el
  nodo heredado t=0,984375. No corresponde al extremo t=1. La familia actual
  exige que cada curva sea un gráfico de s respecto a t, y esa representación
  puede volverse poco adecuada para tramos casi verticales.
- C0 pasa sin refinar, con indicador cero y camino recto. Q0 y Q1 coinciden
  entre sí, pero ambos conservan las mismas limitaciones de refinamiento.

## Lo que sigue abierto

No se ha aislado si la concentración está determinada por la geometría, por
la restricción de gráficos, por la posición de los nodos heredados o por la
historia de optimización. Los once caminos son numéricamente válidos, con
KKT pequeño en sus variables presentes; eso no impide que un nodo nuevo
ofrezca una mejora. No hay contradicción entre ambos diagnósticos.

El crecimiento de la pendiente no demuestra singularidad, salto en una curva
límite, capa límite, bifurcación ni inexistencia de una geodésica suave. La
velocidad euclídea aquí se refiere al parámetro longitudinal t: depende de la
representación. La velocidad de h se muestrea en extremos y punto medio de
cada segmento; su máximo registrado no es una cota rigurosa de toda la curva.

El indicador local no garantiza error global ni mínimo escalar global. La
longitud y Hausdorff se calculan numéricamente con las comprobaciones heredadas;
no hay aritmética dirigida ni certificado de mínimo global. Hausdorff es
 euclídea en la carta normalizada (t,s), no distancia intrínseca de h.

Se usaron los mismos datos sintéticos sin entrenamiento. No hay confirmación
independiente de una hipótesis descubierta en estas curvas. El presupuesto
finalizó por cuatro rondas fijadas, no por falta de tiempo ni memoria.

La siguiente pregunta útil sería contrastar la restricción de gráficos con
una representación paramétrica que permita mover también las coordenadas
longitudinales. Ese contraste necesitaría otro protocolo previo, controles de
reparametrización y un dominio común; no se ejecutó en E16-O. No se recomienda
continuar estas bisecciones hasta obtener un resultado favorable.
