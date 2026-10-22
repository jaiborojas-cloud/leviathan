# Qué acredita una parada física auditada

S conserva exactamente el objetivo de longitud, el dominio y los métodos de
R. Cambia la regla prospectiva de terminación y añade auditorías. No es una
reinterpretación de los resultados de R.

## KKT físico

Para las variables físicas x y caja B, se usa

$$r(x)=\frac{\|x-\Pi_B(x-\nabla L(x))\|_\infty}{\max(1,|L(x)|)}.$$

El residuo cero equivale a KKT de primer orden para la caja. Un residuo menor
que 1e-5 es una tolerancia numérica elegida previamente; no una prueba exacta.
En coordenadas escaladas x=Dy, grad_y=D grad_x, pero el tamaño del residuo
proyectado cambia. Por eso el monitor siempre calcula r en x.

La derivada AD se contrasta con diferencias finitas locales MP80, en ambas
coordenadas y con dos pasos. Independencia se refiere aquí a procedimientos
de cálculo del gradiente; no a datos nuevos ni a independencia estadística.
La concordancia entre pasos no es aritmética de intervalos ni certificado
riguroso de error.

## Racha observada

Se audita cada 200 iteraciones aceptadas. La evaluación inicial no cuenta.
Sea A_j la condición: gradiente verificable y r(x_200j)≤1e-5. La racha satisface

$$c_j=\begin{cases}c_{j-1}+1,&A_j\\0,&\text{en otro caso.}\end{cases}$$

Un hueco entre auditorías también reinicia la racha. La primera vez que c_j
alcanza 3 se solicita parada en ese mismo estado, nunca en uno anterior mejor.
El hash del estado se compara con el del resultado devuelto y se realiza una
validación física final separada.

Tres observaciones consecutivas no implican que el umbral se cumpliera entre
ellas ni que se cumplirá después. Las observaciones son correlacionadas.
No se estima una probabilidad de falso positivo ni un nivel de confianza.

## Vías y banderas

PHYSICAL_SUSTAINED requiere la racha, interrupción explícita y validación final.
La API de SciPy marca la interrupción con status=99 y success=False. S conserva
esos datos nativos; su estado de protocolo es un campo separado.

NATIVE_VERIFIED permite la convergencia nativa más validación física final,
sin atribuirle una racha no observada. NATIVE_CONTROL identifica el caso recto
que termina naturalmente, incluso sin iteraciones. Un límite de iteraciones
sin racha no satisface la nueva regla.

En un problema no convexo, KKT de primer orden no garantiza mínimo local o
global. S no comprueba una condición suficiente de segundo orden en cada
resultado ni prueba existencia o unicidad de una geodésica. La validación de
positividad, longitud y Hausdorff sigue siendo necesaria, pero tampoco sustituye
esas pruebas.

## Coste

La auditoría requiere una evaluación AD adicional y una referencia MP global.
Cada variable usa dos pasos con sus evaluaciones ±, es decir, cuatro llamadas
MP locales de dos aristas. El monitor guarda contadores reales, incluidos
intentos no verificables. Su tiempo forma parte del coste total; reducir
iteraciones del solver no implica reducir tiempo total.

R archivado no incluye este monitor, y S reutiliza precondicionadores de R.
Además, sus caminos finos parten de resultados gruesos distintos. La comparación
histórica no es un benchmark temporal pareado ni una nueva validación de R.
