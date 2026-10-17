# Límite del dominio — certificado estructural y auditoría numérica
2026-10-16. Caso split8_j5_true/update25. Producción PAUSED139.

## Veredicto
CERTIFICACIÓN GLOBAL DEL PRIMER RADIO DE SALIDA: INCONCLUSIVE.
CERTIFICACIÓN ALGEBRAICA DE LA ESTRUCTURA DEL BORDE: obtenida para el modelo de datos almacenados.
No se asignan nuevos outcomes ni una categoría topológica alternativa.

## Qué queda certificado exactamente
El script exact_structure.py convierte cada entrada binary64 almacenada de M y f a su fracción racional exacta.
1. Simetría exacta de M y27 pivotes LDL estrictamente positivos: M es definida positiva como matriz racional, sin tolerancia flotante en las comparaciones.
2. Se verifican las ocho aristas expuestas del polígono de f: todos los demás puntos están estrictamente a un lado y sólo los dos extremos pertenecen a cada arista. Por ello el borde de soporte de la clausura de la familia exponencial está compuesto por las mezclas de los dos extremos de esas aristas, incluyendo sus vértices.
3. En la arista6–13 la carta a=log(w6/w13), b=w20/w13 tiene determinante exactamente distinto de cero. Los exponentes transversales de los otros24 componentes son todos mayores que8; beta20=1 y beta6=beta13=0 exactamente.
4. La inmersión posee un límite unilateral regular de rango2 y métrica positiva en b=0; los puntos de ese borde están a longitud finita por caminos a constante y no pertenecen a la familia de P finitos.
Este certificado trata el modelo fijado por los archivos; no incluye la incertidumbre de construir esos archivos desde una red ni certifica los errores de integración de sus geodésicas.

## Barrido del frente guardado: los2048 rayos y las8 aristas
Se calculó para cada w(r139,theta_j) la distancia en la norma M a cada segmento de borde. Esta distancia ambiental es matemáticamente una cota inferior de cualquier longitud intrínseca hasta el borde (para puntos exactos). Se usa proyección al segmento, no el menor peso como proxy de distancia.
Mínimo calculado en float64:1.74242011008e-6, rayo1775, arista13–6. Sumado a r139:0.0744744006798334. Concuerda con la llegada del rayo1775, cercana a0.07447440068. La tabla contiene2048 filas y todas las8 caras participan.
Las evaluaciones son flotantes sobre estados numéricos; no se convierten en intervalos certificados. Tampoco acotan direcciones entre rayos. La prueba previa del haz en cartas locales hasta1e-10 antes del borde1775 no encontró cruce en los rayos muestreados; no se considera una prueba del continuo angular.

## El mínimo anterior NO era el mínimo angular
Se reintegraron desde el origen41 direcciones uniformes entre índices angulares1773 y1778, paso1/8 del espaciado original. No se interpolaron estados entre rayos.
La integración usa la aceleración MPFR169 original hasta r=.07, después una carta interior equivalente hasta b=0 mediante b como variable independiente. Sólo son copias diagnósticas. El protocolo y checkpoint de producción quedan intactos.
Mínimo de esta malla: índice1775.375, r≈0.07447421070185.
Optimización local posterior (exploratoria, no compuerta confirmatoria) entre1775.25 y1775.5:

    índice angular ≈1775.39798298
    theta≈5.44685279347401 rad
    r_borde≈0.07447421006513

Este borde es aproximadamente1.9062e-7 anterior al estimado originalmente para1775. Por tanto no es correcto seguir llamando mínimo global al radio de1775.
La velocidad transversal en el mínimo es≈-228.1189, claramente no nula. No prueba por sí misma la ausencia de un mínimo más temprano en otro sector.

## Control desde el origen
Se repitieron1775,1776 y1775.375 con266 bits y tolerancias100 veces más estrictas. Radios:

| Dirección | MPFR169 / tolerancias heredadas |266 bits / tolerancias100x estrictas|
|---|---:|---:|
|1775|0.07447440068377846|0.07447440068259376|
|1775.375|0.07447421070184969|0.07447421070080043|
|1776|0.07447464621423219|0.07447464621320699|

La diferencia entre controles desde el origen es del orden1.0–1.2e-12. La diferencia con la predicción anterior iniciada en139 alcanza aproximadamente5e-12. Esto muestra por qué la coincidencia local130/139 (~1e-14) NO era una cota de error global.
En la carta transformada los valores de tolerancia no equivalen a la misma norma de error en P. Los contrastes sólo validan convergencia empírica local/global de estas rutas, no un integrador de intervalos. Las condiciones iniciales siguen usando la normalización original del instrumento.

## Qué falta para certificar el primer borde del continuo
- Integración validada (envolventes con redondeo dirigido y control de error global) desde el origen, incluyendo la normalización inicial.
- Cotas sobre la dependencia angular y una cobertura de TODO [0,2pi), con subdivisión de intervalos que descarte cualquier llegada anterior fuera del sector encontrado.
- Localización encerrada del encuentro transversal y propagación de la incertidumbre al radio.
Una malla más fina, más dígitos o minimizar una curva muestreada no reemplazan estas condiciones. No se dispone aún de ese certificado y no se inventa un intervalo riguroso a partir de diferencias entre ejecuciones.

## Consecuencia para área y reanudación
El candidato más temprano refuerza la restricción del dominio; no rescata el área0.02. La estimación anterior de área(~0.01871467) se calculó hasta un radio ligeramente posterior a este nuevo candidato, por lo que no debe llamarse área de un disco completo certificado. Sirve como diagnóstico muestreado; la conclusión de área sigue INCONCLUSIVE en sentido certificador.
No reducir área, eliminar rayos ni añadir puntos del borde a la familia congelada. Mantener producción en139; siguiente paso contable140 sin ejecutar. La existencia del dominio nominal no está validada, tampoco hay nuevo GEOMETRIC_NONINJECTIVITY ni negativo confirmado.

## Reproducción y persistencia
plan.json fija el barrido antes de nuevas integraciones; refine.py guarda cada dirección al terminar. complete.py realiza minimización local exploratoria y distancias de los2048 estados a las8 caras. exact_structure.py contiene las verificaciones racionales. Resultados, CSV y hashes en este paquete. Dependencias: numpy2.3.5,scipy1.17.0,gmpy2 2.3.2,mpmath1.3.0. Entradas: Windows_RIPG_T2A_CP90/, upload/RIPG_RESULTADOS_PC.zip y boundary139/ del paquete previo. No se recalculan auditorías cerradas; los rayos nuevos son diagnósticos.
