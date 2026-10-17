# Leviathan / RIPG — naturaleza de la frontera del replay139
Fecha: 2026-10-15. Estado: diagnóstico aislado; producción PAUSED139.

## Conclusión
La estructura analítica del constructor y las pruebas locales identifican un borde de soporte de la familia exponencial softmax a distancia métrica finita. La representación P diverge al acercarse al borde; la métrica expresada en una carta de cocientes de pesos admite un límite regular y positivo desde el interior. Los rayos1775 y1776 alcanzan numéricamente ese borde con velocidad transversal no nula. No es evidencia de un punto conjugado, cut locus ni autointersección. No se asigna GEOMETRIC_NONINJECTIVITY ni otra nueva clasificación poblacional.

El resultado distingue dos aspectos: la mala condición de G en P depende de la carta; la ausencia del punto límite en la familia de P finitos es una frontera real del dominio original. Incorporar ese punto al espacio o cruzarlo sería una modificación del modelo, no una mera corrección de precisión.

## Estructura analítica
El instrumento tiene pesos w_k(P)=exp(f_k.P)/sum_l exp(f_l.P), inmersión w(P) y métrica G=J^T M J, con M constante y simétrica. La matriz almacenada es numéricamente definida positiva (autovalor mínimo5.73635e-8, máximo1.13795). La arista relevante de la envolvente convexa de f une componentes6 y13; componente20 es la primera dirección transversal suprimida.

Se construyó la carta exacta, para b>0:

    a = log(w6/w13) = (f6-f13).P
    b = w20/w13 = exp((f20-f13).P)
    P = A^{-1}(a,log(b))

A tiene filas f6-f13 y f20-f13; det(A)≈-0.0158206195, no nulo.
Para cada componente:

    w_k/w13 = exp(alpha_k*a) * b**beta_k,
    (alpha_k,beta_k) = (f_k-f13) A^{-1}.

Componentes13,6,20 tienen pares exactos(0,0),(1,0),(0,1). En los otros24 componentes beta>=8.335714285714..., todos positivos. Los coeficientes se calcularon con100 dígitos desde los datos float64 originales; las identidades de las tres filas base se fijaron algebraicamente, sin alterar datos ni geometría.

Por tanto, al tomar b→0+ con a finito:
- Sólo quedan w6=exp(a)/(1+exp(a)) y w13=1/(1+exp(a)).
- Las primeras y segundas derivadas de los otros24 términos se anulan en el límite.
- Las derivadas de la inmersión respecto de a y b siguen siendo independientes: una modifica la mezcla6/13 y la otra introduce componente20.
- La métrica límite es positiva si M lo es en ese plano tangente. Esto se verifica numéricamente con amplio margen.
- El camino a constante, b→0 tiene longitud finita, porque G_bb tiene límite finito. P diverge como log(b); ningún P finito produce w20=0.

Esto establece una frontera accesible de la completación métrica de la familia abierta. La familia original de P finitos es métricamente incompleta bajo estas condiciones; no hay justificación para añadir o atravesar la frontera dentro del protocolo congelado. La demostración estructural es distinta de una certificación mediante aritmética de intervalos de cada constante numérica.

## Confirmación de las trayectorias
Se usaron copias de los estados130 y139, rayos1775 y1776 (índices desde cero). No se reintegró el haz ni se avanzó su checkpoint.
En la carta equivalente se usó b como variable independiente, integrando a,r,da/dr,db/dr hasta el límite unilateral b=0. Todas las evaluaciones permanecen en b>=0; no se evaluó ni se extendió a b<0.
DOP853 diagnóstico: rtol2e-10 y atol2e-12, más repetición de sensibilidad100 veces más estricta. Estas tolerancias en coordenadas nuevas NO se declaran equivalentes al control de error en P ni sustituyen las tolerancias de producción. Se contrastan mediante solapamiento y repetición; no se ha autorizado este solver para producción.

| Rayo | Radio límite desde139 | db/dr en límite | Condición G en carta límite | w6 en límite |
|---|---:|---:|---:|---:|
|1775|0.07447440068752452|-228.1933218|131.49884|0.06436715|
|1776|0.07447464621825482|-228.0026912|128.38584|0.06359021|

Ambas velocidades normales son negativas y no nulas: encuentro transversal con el borde, no aproximación asintótica en r infinito.

Desde130, los radios respectivos son0.07447440068751267 y0.07447464621824641. Diferencias con inicio139:1.19e-14 y8.41e-15. No interpretar esas diferencias como cotas rigurosas de error global desde el origen.
La repetición con tolerancias100 veces más estrictas coincide a precisión mostrada. La extrapolación lineal en el plano de pesos6/13/20 da los mismos radios a precisión float64; los otros pesos suman ~1e-25 en130 y ~1e-32 en139. Esa coincidencia verifica consistencia local, no constituye un test independiente completo del origen.

## Solapamiento y precisión
- Identidad de Jacobianos J_nuevo*d(a,b)/dP frente a J_original: error relativo máximo1.88e-14 en cuatro puntos130/139.
- La integración desde130 al valor b de139 reproduce r con errores<=1.14e-14; a con errores<=2.67e-12; velocidad transformada relativa<=2.60e-10.
- Evaluación independiente de jets y aceleraciones en mpmath100 dígitos confirma la métrica regular. Diferencias absolutas en aceleración de carta<=4.66e-10 para aceleraciones~1e5.
- Autovalores límite: rayo1775,9.54815e-6 y1.25557e-3; rayo1776,9.56244e-6 y1.22768e-3.
- Rapidez intrínseca cuadrada en límite≈0.99999999766 y0.99999999773.
- Por la estructura del límite, las segundas derivadas de la inmersión quedan en el mismo plano de los tres componentes y la curvatura gaussiana tiende a0. La evaluación de100 dígitos es consistente con ese límite. Esto NO excluye conjugados producidos por curvatura acumulada anteriormente ni colisiones globales.

## Consecuencias operativas
No continuar intentando llegar a r=.09 en la carta P para estos rayos: los cálculos locales sitúan un borde anterior. La carta nueva permite describir y localizar el límite; no ofrece una continuación legítima más allá de él en la familia original.
Esto tampoco determina todavía si el área objetivo .02 puede alcanzarse antes del borde: falta esa calibración válida, y no debe sustituirse por extrapolación ni por recorte del dominio.
La comprobación cubre dos rayos; el mínimo sobre todos los ángulos puede ser menor. No se ha certificado el primer radio de terminación de todo el haz, ni r_inj, ni r_conj, ni A_embed.
Siguiente trabajo propuesto: registrar la compuerta de dominio incompleto dentro de las reglas existentes, revisar el tratamiento de casos no evaluables del preregistro y auditar si el dominio nominal existe antes de la frontera. Si el protocolo no contempla este fallo de dominio, conservarlo como pendiente/INCONCLUSIVE documentado y diseñar por separado cualquier extensión del modelo; no modificar retrospectivamente el evento confirmatorio.

## Persistencia y reanudación
El replay permanece PAUSED139,r=.07447265825972331, siguiente140. No nuevos outcomes ni visitas, no reemplazo de estados, no cambio de protocolo. Esta carpeta es un diagnóstico separado; no está promovida a instrumento de producción.
Entradas: RIPG_RESULTADOS_PC.zip (SHA256 f082f89bd76f94e5bd8060021939008363228aabd0f377d0cd4cfa6eb1ca555b) y datos/fuentes del paquete WindowsCP90. Código analyze.py, independent_precision.py; plan.json escrito antes de la integración en la carta; resultados y hashes adjuntos. Reproducir desde la raíz del proyecto con upload/ y Windows_RIPG_T2A_CP90/ disponibles.
