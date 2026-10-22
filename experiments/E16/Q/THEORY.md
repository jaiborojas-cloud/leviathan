# Longitud, energía y parametrización

Estas identidades son derivaciones matemáticas del protocolo, no resultados
empíricos ni certificados sobre un mínimo de RIPG. Se supone h simétrica
positiva definida a lo largo del camino y velocidad métrica integrable. Para
parametrizar por arco sin tramos estacionarios, se supone además velocidad
positiva. Se trabaja en un intervalo de parámetro de longitud uno.

## Equivalencia que sí se puede usar

Sea v(u)=sqrt(p'(u)^T h(p(u))p'(u)), L=integral v y E=1/2 integral v².
Cauchy–Schwarz implica

$$E\geq\frac{L^2}{2},\qquad
E-\frac{L^2}{2}=\frac12\int_0^1(v(u)-L)^2\,du.$$

La igualdad requiere velocidad métrica constante casi en todas partes. Un
mismo camino regular recorrido por arco métrico puede satisfacerla sin cambiar
su imagen. En ese caso, como función de las variables geométricas del polígono,

$$E_{arc}=\frac12L^2,\qquad
\nabla E_{arc}=L\nabla L,\qquad
H_{arc}=LH_L+\nabla L\nabla L^T.$$

En un punto estacionario interior con L>0, el Hessiano se escala por L:
no desaparecen sus modos nulos ni mejora su razón espectral por ese mero
cambio escalar. Con restricciones activas, la misma afirmación se aplica al
bloque de direcciones libres donde el gradiente restringido sea cero; no debe
confundirse KKT proyectado con gradiente completo nulo.

## Energía de un polígono con tiempos fijos

En Q, cada segmento se recorre linealmente en un intervalo de duración 1/m.
Con parámetro local x de 0 a 1, q_i(x)=c_i+b_i x+a_i x² y

$$A_i=\int_0^1q_i(x)\,dx=c_i+\frac{b_i}{2}+\frac{a_i}{3},\qquad
E_{aff}=\frac m2\sum_i A_i.$$

La fórmula es exacta para las métricas polinómicas consideradas, incluida la
métrica constante del control. La longitud usa integral sqrt(q_i), que no
coincide generalmente con sqrt(A_i). Si se dejan variar sólo las duraciones
positivas tau_i, sum tau_i=1, manteniendo los segmentos afines,

$$E(\tau)=\frac12\sum_i\frac{A_i}{\tau_i},\qquad
\tau_i^*=\frac{\sqrt{A_i}}{\sum_j\sqrt{A_j}},\qquad
E_{dur}=\frac12\left(\sum_i\sqrt{A_i}\right)^2.$$

Por tanto,

$$E_{aff}\geq E_{dur}\geq E_{arc}=L^2/2.$$

La primera brecha refleja diferencias de velocidad cuadrática media entre
segmentos; la segunda incluye la variación de velocidad dentro de ellos.
Minimizar E_aff a m fijo **no es, en general, minimizar L**. Q registra ambas
brechas y comprueba por separado la estacionariedad de longitud. Una energía
menor no autoriza declarar resuelto el problema geométrico original.

## Control de métrica constante

En coordenadas z=(t,s), sea G la matriz constante de h en el marco de la
cuerda. Con extremos (0,0)/(1,0),

$$E_{aff}=\frac m2\sum_i(z_{i+1}-z_i)^TG(z_{i+1}-z_i).$$

Si G es positiva definida, su solución analítica es z_i=(i/m,0). Su Hessiano
interior es

$$H_E=m\,T\otimes G,\qquad
T=\operatorname{tridiag}(-1,2,-1).$$

La longitud de la misma recta no cambia al redistribuir nodos colineales sin
invertir el orden; esas direcciones generan modos nulos. La energía afín sí
penaliza la redistribución a tiempos fijos. Esto no es añadir una penalización
a L: es optimizar el objetivo distinto E_aff.

Además, para el Hessiano constante anterior,

$$\kappa_2(H_E)=\kappa_2(G)\cot^2\!\left(\frac{\pi}{2m}\right).$$

Eliminar los modos nulos no elimina el deterioro de condicionamiento con la
malla. Esta identidad se refiere al control constante, no demuestra la causa
del límite de iteraciones en Q0/Q1.

## Gradientes locales de energía

La contribución de dos aristas al objetivo global conserva el factor m/2.
Evaluar una función de energía como si esas dos aristas fueran toda la malla
introduce en cambio m_local/2=1. Para diferencias finitas locales hay que
multiplicar por m/m_local. Esta distinción explica
[la errata de implementación conservada](ERRATA_IMPLEMENTACION_v1.md).
