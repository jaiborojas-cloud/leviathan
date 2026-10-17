# Leviathan / RIPG — existencia del dominio nominal, paso139
Fecha: 2026-10-16. Estado: diagnóstico numérico terminado; certificación nominal INCONCLUSIVE. No es un nuevo outcome topológico.

## Respuesta
Los cálculos disponibles indican que el disco radial completo no alcanza A=0.02 antes de encontrar la frontera del dominio softmax. Estimación cerca del borde: A≈0.01871467 (93.5734% del objetivo), déficit≈0.00128533 (6.4266%). Esto es evidencia numérica fuerte de falta de dominio nominal dentro de la familia original, no una demostración con cotas certificadas sobre todo el continuo angular.
No promover a calibración validada, A_embed certificado ni GEOMETRIC_NONINJECTIVITY. No reducir el área, sustituir el estado ni completar la familia con puntos de frontera. Mantener la visita sin desenlace resuelto bajo el protocolo congelado.

## Recuperación
Se recuperaron los paquetes persistentes WindowsCP90, frontera139 y RIPG_RESULTADOS_PC.zip. Se verificaron SHA-256, manifests y CRC. La continuación del usuario comprende13 segmentos91–139; no se recalculó la integración original. Los cálculos temporales de área del15oct no sobrevivieron al reinicio y se reconstruyeron desde la salida densa guardada. El checkpoint de producción no se modificó.

## Área del prefijo r139=0.07447265825972331
Misma geometría, M,f y salida densa original. Dunavant7 sobre triángulos en P:

| Anillos | Rayos | Área |
|---:|---:|---:|
|32 (regla heredada)|2048|0.0187458234241393|
|64 (diagnóstico)|2048|0.0187191280736838|
|128 (diagnóstico)|2048|0.0187142715845957|
|256 (diagnóstico)|2048|0.0187139753856378|

Los refinamientos son pruebas de sensibilidad; no reemplazan retrospectivamente la regla de32 anillos ni su tolerancia. La regla heredada tampoco encuentra el objetivo en este prefijo.

## Contraste en la inmersión
Se integró independientemente el elemento de área parametrizado por r,theta:

    sqrt((w_r^T M w_r)(w_theta^T M w_theta)-(w_r^T M w_theta)^2).

w_r se obtiene del estado y velocidad guardados; w_theta mediante diferencias centrales periódicas sobre los rayos existentes. Simpson radial; los niveles512/1024 rayos son submuestreos del mismo haz2048, no rayos nuevos ni fases independientes.

| Rayos | Intervalos radiales | Área del prefijo |
|---:|---:|---:|
|512|1024|0.0187109781667300|
|1024|1024|0.0187131629061721|
|2048|256|0.0187137178078781|
|2048|512|0.0187137178064128|
|2048|1024|0.0187137178039691|

Error máximo observado en rapidez cuadrada frente a1:5.256e-8. La diferencia angular1024→2048 es5.55e-7 de área; Dunavant256 difiere del cálculo inmerso2048 en2.58e-7. No son cotas rigurosas de error. Ambas son pequeñas frente al déficit≈1.285e-3.

## Tramo restante
Se integraron copias diagnósticas de LOS2048 rayos desde r139 hasta r=0.07447440058752453, a1e-10 por debajo del límite estimado del rayo1775 (0.07447440068752452). No se atravesó ninguna frontera de carta en las evaluaciones.
Cada rayo usa una carta de cocientes de pesos construida determinísticamente: peso máximo como base, primera pareja en orden descendente de pesos con determinante absoluto>1e-8. Este umbral es una selección operacional de carta del diagnóstico, no un criterio científico, exclusión ni cambio del protocolo. Todos los rayos se incluyen. El cambio es algebraicamente equivalente en el interior.
Solapamiento de Jacobianos: error relativo máximo7.42e-14. Condición máxima de métrica en cartas locales≈29097. DOP853 de diagnóstico usa rtol2e-10/atol2e-12; estos controles en coordenadas distintas no se afirman equivalentes al error de producción en P. No se promueve este instrumento a producción.

| Rayos del área | Área adicional |
|---:|---:|
|512|9.51917e-7|
|1024|9.52445e-7|
|2048|9.52590e-7|

Densidad angular integrada al extremo≈0.54674348. El hueco final1e-10 en radio aportaría aproximadamente5.47e-11 si mantiene ese límite regular; esto es una extrapolación local explícita, no una cota.
Suma del prefijo inmerso2048 con el tramo:0.0187146703941937. Incluso usando el mayor prefijo (regla heredada32), suma≈0.0187467760143639, aún6.266% por debajo de0.02.

## Alcance lógico
Para que exista el disco radial nominal completo, todas las direcciones deben permanecer definidas hasta su radio. Basta una terminación anterior para impedir ese disco a radios posteriores. El área parametrizada acumulada es no decreciente, por lo que un borde más temprano en otra dirección no rescataría el dominio. Pero estos muestreos no certifican ausencia de estructura angular no resuelta ni ofrecen una cota superior rigurosa del área continua.
La integral parametrizada no presupone inyectividad: si hay solapamientos puede contar multiplicidades. No debe llamarse A_embed ni utilizarse para probar inyectividad.

Conclusión operacional: no continuar ciegamente hacia0.09, ni forzar una raíz de área cruzando el borde. La existencia de D_0.02 no queda validada y los cálculos apuntan a su ausencia dentro del dominio original. Certificación completa: INCONCLUSIVE; clasificación topológica y outcome futuro permanecen sin asignación nueva. El protocolo excluye convertir fallos no resueltos en negativos o eliminarlos del análisis.

## Qué falta si se requiere certificar la no existencia
Control independiente de resolución/fase angular y del error global desde el origen; una cota de área suficientemente conservadora hasta la frontera, o una auditoría equivalente conforme a las compuertas congeladas. No hace falta perseguir0.09 más allá de la frontera. Cualquier extensión del espacio de perspectivas requeriría un diseño separado.

## Reanudación y archivos
Producción float64 histórica512 intacta. Replay MPFR del usuario confirmado139, siguiente140 pero PAUSADO por revisión de dominio. 800 basales/800 selladas; visitas cerradas1/8000; sin nuevos outcomes ni horizontes completos. No hay procesos activos.
Código: common.py (recuperación y hashes), areas.py (áreas y sensibilidad), local_bundle.py (copias en cartas locales). ResultadosJSON y densidadesNPZ; hashes de todos los archivos en manifest.json. Reproducir desde la raíz que contiene Windows_RIPG_T2A_CP90/ y upload/RIPG_RESULTADOS_PC.zip. No ejecutar scripts de continuación de producción.
