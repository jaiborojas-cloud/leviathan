# DIN-Q13 v2 — especificación operativa de potencia, antes de simular

Se aplica §6 del diseño v1, sin cambiar criterios, efecto objetivo ni rejilla.
Calibración v2 completa y publicada primero: LS=.005, WD=.2. Esta simulación no
usa estados de esos pilotos ni datos de cohorte Q13/C2. Sólo el CSV G3 s=.8 por
SHA, como piloto de covariables y varianza residual del método C2.

Método C2 sin cambios: cuatro remuestreos de N splits completos (100 réplicas
gaussianas por marco), semillas SeedSequence([412000,2,N,marco]) para covariables
y [413000,2,N,marco] para ruido. Ajustar la base cúbica del piloto; sigma² con
500−100−rango grados de libertad. Centrar ruido dentro de split; efecto por
beta=sqrt(d/(1−d)*.8*sigma²/var(X_residual)), d∈{0,.006,.012}.
Como C2, los tres efectos comparten covariables y ruido dentro de una réplica:
se compara el mismo resultado gaussiano con distinto término de señal. Es un
modelo de potencia condicional pareado, no potencia universal para LS o WD.

PASS simulado: estimando C1 exacto, 1999 permutaciones 260001; 10 bloques 260010,
signo positivo. Reutilizar el motor batched C2 extraído por AST sin cambios,
contrastado contra la primaria original en tablas exclusivamente simuladas.

Bootstrap: 500 remuestreos de splits completos, seed760001, mismos remuestreos
en los tres efectos; cada copia se centra como un split nuevo y conserva el
bloque de su original. Las funciones congeladas bloques, D_punto y clasificar
de Q13 se cargan sin ejecutar main/analizar. Se comparan el cálculo agrupado
y D_punto en simulaciones antes de aceptar la implementación.

Para hacerlo factible se agregan productos cruzados por split y ponderan por
sus multiplicidades bootstrap; no se cambia el ajuste OLS ni sus predicciones.
Un cambio invertible de base mejora el condicionamiento: QR de los tres términos
y residuo global de X. La base cúbica de L reestandarizada en cada remuestreo
tiene el mismo espacio; se contrasta esa identidad numéricamente con D_punto.
No se aproximan intervalos por errores estándar ni se omiten remuestreos.

Regla de selección sin cambios: primer N∈{200,256,320,400,512,640,800} con Wilson95
inferior≥.8 tanto para PASS del efecto .012 como para CAE completo (IC95 superior
del efecto 0 <.006 y límite inferior de su diferencia respecto a .012 >0).
Clasificar se usa literalmente. Se conservan también los otros efectos simulados.
400 réplicas por N, 500 bootstrap cada una; no se selecciona por una réplica.

Si no hay N, no entrenar. Si N>400, publicar y pedir confirmación en el PR antes
de entrenar. Guardar todas las simulaciones y fallos; sin sobreescribir ni corregir
código después de medir sin una enmienda. Dos procesos y un hilo BLAS por proceso.
En el PR sólo se comunica planificación operacional, no asociaciones de cohorte.
