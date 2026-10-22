# Escalado que conserva la longitud y el dominio

Estas identidades explican el método de R. No son certificados de mínimo ni
una demostración de la causa del límite de iteraciones.

## Cambio de variables

Las coordenadas físicas son x=(t_1,s_1,...), con cajas [0,1] y [-0,25;0,25].
Sea D diagonal estrictamente positivo y x=Dy. Entonces

$$\widetilde L(y)=L(Dy),\qquad
\mathcal B_y=D^{-1}\mathcal B_x,\qquad
\nabla_y\widetilde L=D\nabla_x L,\qquad
H_y=DH_xD.$$

La correspondencia entre cajas es biyectiva: los caminos admisibles y el valor
de su longitud se conservan. No se añade energía ni penalización. En aritmética
exacta, la congruencia conserva la inercia del Hessiano. Puede cambiar su
condicionamiento, pero no convierte por sí sola un Hessiano indefinido en uno
positivo definido ni elimina modos nulos exactos.

R usa D_ii=2^e_i, e_i entero entre -7 y 7. La multiplicación/división por esas
potencias conserva exactamente las coordenadas binarias en el rango numérico
utilizado, evitando redondeos innecesarios al transformar las cotas diádicas.
Las identidades se comprueban también en la implementación.

## Qué residuo permite comparar métodos

La condición KKT exacta de una caja es equivalente tras un escalado diagonal
positivo. Sin embargo, un residuo finito no conserva su tamaño:

$$r_x=\frac{\|x-\Pi_{\mathcal B_x}(x-\nabla_xL)\|_\infty}
{\max(1,|L|)},\qquad
r_y=\frac{\|y-\Pi_{\mathcal B_y}(y-\nabla_y\widetilde L)\|_\infty}
{\max(1,|L|)}.$$

En el interior, los componentes de gradiente se multiplican por D. Cerca de
una cota interviene además la proyección. Por eso R exige r_x≤1e-5 en ambos
métodos y sólo informa r_y como descriptor. El gtol interno en y no representa
la misma tolerancia física que el gtol en x. El éxito del solver sigue siendo
un requisito separado, fijado antes de medir.

## Control recto y espectros numéricos

Si la métrica es constante y positiva definida, en el marco (t,s) es G. En
una arista de la recta ordenada, delta z=(delta t,0) y delta t>0:

$$\nabla^2\sqrt{\Delta z^TG\Delta z}
=\frac1{\sqrt{G_{tt}}\,\Delta t}
\begin{pmatrix}0&0\\0&G_{ss}-G_{ts}^2/G_{tt}\end{pmatrix}.$$

Así, el Hessiano exacto de longitud conserva los modos tangenciales nulos y
es semidefinido positivo en ese control. Un D positivo conserva esos modos.
No deben interpretarse negativos pequeños de una matriz AD transformada en
float64 como prueba de curvatura negativa real del control matemático.

R calcula espectros numéricos con umbral relativo a cada matriz. Tanto ese
umbral como la amplificación de errores por D pueden alterar la clasificación
de modos cercanos a cero. Las razones del espectro positivo no se denominan
números de condición SPD si hay modos negativos o casi nulos. No se ajusta el
umbral después para obtener una clasificación favorable.

## Alcance del precondicionador

La diagonal se obtiene una vez por linaje/malla en una referencia común. Su
valor absoluto y piso sólo construyen D; no se aplican a h ni al objetivo.
Esto equilibra algunas escalas locales, pero no resuelve necesariamente el
acoplamiento entre nodos, la curvatura negativa, la redundancia paramétrica o
el crecimiento de condicionamiento con la malla. R estudia este escalado
concreto, no todos los métodos de precondicionamiento.
