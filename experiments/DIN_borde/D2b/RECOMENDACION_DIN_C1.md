# DIN-C1 · recomendación al responsable (Q10)

**No congela ni modifica DIN-C1.** La decisión y el análisis confirmatorio
permanecen con el responsable. El borrador examinado es v1 del árbol9904db0;
se leyó como documento, sin ejecutar sus scripts ni acceder a sus estados.

## Qué permite concluir D2b

La confianza mínima y la geometría comparten ingredientes algebraicos. Bajo
rango interpolante y ridge despreciable, M se reduce a N veces la diagonal de
odds de error. Si además colapsa sobre una coordenada, rho se aproxima por
sqrt(N(1-p_k)/p_k)/n. Ese mecanismo puede explicar una asociación posterior
fuerte; no es una ley universal ni prueba que haya ocurrido en cada estado.

Antes del colapso, ni X determina G ni G determina X universalmente, incluso
con f fijo y con la misma clase WineMLP. Esto deja abierta una predicción
temporal adicional; no demuestra que exista en la cohorte de DIN-C1. Tampoco
la concentración diagonal≈.14 demuestra por sí sola ausencia de redundancia.

## Estimando y control negativo decisivo

La primaria del borrador ajusta Y~intercepto por split+beta L y correlaciona
por rangos X con el residuo e. Eso mide una **asociación por rangos con el
residuo de una proyección lineal**. No equivale a preguntar si X añade
información predictiva condicionada a L sin restricciones funcionales.

L=(0,.01,.02,.03,1), X=L-2, Y=-L² da W_adj=.7, aunque X está EXACTAMENTE
contenido en L y el error de medida es cero. Pearson(X,e)=0, como exige MCO.
No se necesita siquiera X no lineal para obtener el problema: Spearman
después de la proyección lineal puede conservar asociación con un X afín.
Si se residualiza X también, su residuo es cero: la correlación es
NO_IDENTIFICABLE, no una evidencia positiva ni un cero artificial.

Este contraejemplo no invalida una prueba bajo un nulo lineal correctamente
especificado. Sí impide interpretar automáticamente un PASS de esa primaria
como «información más allá de toda función de L». Las permutaciones no arreglan
esa diferencia entre hipótesis; hay que verificar el nulo y la intercambiabilidad
adecuados al estimando. Los controles con ruido y error de medida son
ilustraciones sintéticas, no diagnósticos del .218 de D6.

## Opciones para fijar ANTES de una cohorte nueva

1. Conservar la primaria, pero restringir la afirmación a su estimando lineal
   y por rangos, y documentar sus controles negativos. La asociación marginal
   débil L10→Y no basta para descartar relaciones no lineales.
2. Si se quiere una afirmación condicional más amplia, preespecificar un modelo
   base flexible y de baja complejidad para L: p.ej. spline con nudos fijados o
   cuadrático, con interceptos por split. Comparar su desempeño predictivo con
   el mismo modelo más X, usando separación por splits para ajuste/evaluación.
   Elegir función de pérdida, agregación, contraste y regla de decisión antes
   de medir; recalcular potencia para ese estimando.
3. En un enfoque de residuos, modelar también E[X|L], con ajuste flexible
   prefijado y validación cruzada por splits. Una correlación de residuos sigue
   siendo un contraste limitado, no independencia condicional universal.
   Ajustar sólo rangos no elimina no linealidad arbitraria. Cinco observaciones
   por split no permiten splines independientes por split sin sobreajuste:
   compartir forma funcional o usar un modelo jerárquico prefijado.

Probar el CÓDIGO confirmatorio efectivo con X=L, X=h(L), Y=g(L), X constante,
L medido con error y un control con incremento predictivo verdadero. Debe
preservar valores indefinidos cuando no queda variación. D2b reproduce la
definición documental; no auditó el script C1 efectivo. La regla de desempate
(X,init) crea rangos incluso con X constante: recomiendo rangos promedio o
declarar el split sin variación, fijando su tratamiento antes del análisis.

La precisión de rho merece una auditoría independiente y prefijada: cuerda,
estabilidad de cuadratura y repetición con mayor precisión en un subconjunto
seleccionado ANTES por semilla, sin reemplazar fallos. Si L es ruidoso, X puede
recuperar el L latente y dejar señal tras el ajuste, sin anticipar una dinámica
nueva. Un ajuste más flexible no elimina por sí solo el error de medida.
Para X, calcular log(1-p_y) desde logits mediante logsumexp de clases incorrectas
menos logsumexp total y tomar el máximo del panel evita saturación p=1.

## Covariables y alternativas

Si el estimando lo requiere, concentración/forma de M, condicionamiento Fisher
y el resto del vector de confianzas pueden ayudar a separar mecanismos.
Añadirlos cambia la pregunta y puede sobreajustar: no recomiendo elegirlos por
los nuevos resultados ni prometer que eliminen toda dependencia algebraica.

Un predictor calculado en un panel de sondeo separado, que no construya R ni F,
o una medida temprana de respuesta al entrenamiento (p.ej. cambio de pérdida
entre updates5 y10) está menos directamente ligado a la identidad estática.
Requiere hipótesis, panel, coste y análisis propios; aquí no se demuestra su
valor predictivo. Las normas de gradientes/leverage del mismo panel entran
directamente en M: son covariables mecánicas, no alternativas libres de acoplamiento.

**Recomendación:** el ajuste lineal del borrador es insuficiente para una
afirmación condicional general. El responsable debería fijar el estimando y
sus controles antes de congelar DIN-C1. D2b no decide si conservar o cambiar
la primaria ni atribuye el efecto de D6 a un artefacto.
