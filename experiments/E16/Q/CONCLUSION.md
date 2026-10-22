# Conclusión E16-Q

**INCONCLUSIVE.** La energía afín controla parte de la distribución de nodos,
pero no proporciona candidatos cuadráticos que pasen la estacionariedad de
longitud y la terminación del optimizador conforme al protocolo.

## Hallazgos

1. La equivalencia continua de energía y longitud requiere controlar la
   velocidad métrica. En el polígono afín con tiempos fijos, E_aff y L son
   problemas discretos distintos. La reducción de la brecha de energía no
   autoriza a aceptar el candidato como estacionario de longitud.
2. En `energy/264`, Q0/Q1 pasan KKT de energía pero no KKT de longitud. Los
   ocho resultados cuadráticos llegan al límite de iteraciones. Las
   validaciones numéricas de gradientes e integración pasan; no se resuelve
   el problema cambiando retrospectivamente el criterio de parada.
3. El control constante demuestra la diferencia entre redistribución y
   geometría: L conserva una recta con nodos no uniformes; E_aff distribuye
   nodos casi uniformemente y conserva la recta. L²/2 mantiene los 131 modos
   casi nulos de L; E_aff los elimina en ese control. Las identidades se
   verifican con expresiones analíticas y MP, no sólo con una apariencia
   favorable del espectro.
4. Las curvas length/energy de 264 tienen acuerdo descriptivo según
   longitud/Hausdorff, pero sus estados de optimización siguen inconclusos.
   Coincidencia de curvas o longitudes no sustituye la estacionariedad.

## Alcance

Las fuentes son las mismas sintéticas, sin entrenamiento ni validación
independiente. La variante length continúa los resultados P/free/132 con un
presupuesto nuevo previamente fijado; P no se modifica. No se seleccionan
supervivientes ni se ocultan candidatos que agotan iteraciones.

Los espectros son locales, calculados en float64 sobre el bloque de variables
no activas y clasificados con un umbral relativo. Se verifican identidades y
dos Rayleigh por objetivo, pero no hay certificados de autovalores ni de
mínimos. Un Hessiano positivo al umbral en un punto no estacionario no acredita
un mínimo. Los espectros indefinidos no reciben un número de condición SPD.

La degeneración tangencial exacta del control constante no se puede atribuir
sin más a Q0/Q1: en sus fuentes hay curvatura negativa y razones espectrales
positivas grandes, sin el mismo conteo de modos nulos al umbral declarado.
No se ha aislado cuál de estos efectos determina la detención del optimizador.

Hausdorff es euclídea en la carta normalizada, no distancia intrínseca de h.
Los controles SPD de las curvas son numéricos, sin intervalos dirigidos.
Dos mallas no demuestran convergencia ni existencia de una curva límite.
No se certifican geodésicas, regularidad, singularidad, unicidad ni mínimos
 globales.

V1 queda abortada por una omisión de escala en el FD de energía; sus valores
erróneos no se reinterpretan como geometría. La corrección se congeló antes
de v2 y no cambió los candidatos comunes. La primera corrida, sus límites y
la contradicción detectada se conservan para revisión.

La siguiente pregunta útil sería estudiar un precondicionamiento que conserve
el objetivo L, con controles de malla y criterios de parada definidos antes
de medir. Esa es una propuesta posterior, no una solución implementada en Q
ni una conclusión de que el condicionamiento sea la única causa.
