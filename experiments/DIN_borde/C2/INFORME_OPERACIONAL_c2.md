# DIN-C2: informe operacional de generación y publicación

Fecha: 2026-10-26 (México). PR #89, rama research/din-c2-cohorte; borrador sin fusión.
Diseño congelado SHA d00abbad…ff80; no se modifica ni se interpreta el resultado.

| Elemento | Conteo o estado operacional |
|---|---:|
|Splits planificados / paneles sintéticos|200 / 200|
|Inicializaciones por split|5|
|Trayectorias previstas / terminadas / publicadas|1.000 / 1.000 / 1.000|
|Visitas por trayectoria|5,10,30,250|
|Estados previstos / medidos|4.000 / 4.000|
|Filas con error / ausentes|0 / 0|
|Estados inválidos|0|
|Reconstrucciones previas exactas|3 / 3|
|Archivos externos verificados|12.407|
|Tiempo de entrenamiento y medición|1427.855433 s (≈23,80 min)|
|Verificación operacional final|PASS (v2)|

Todas las trayectorias previstas tienen fila, sin sustituciones ni exclusiones.
Se conservan datos sintéticos, pesos/Adam/RNG, M/f/logits, rho completo, JSON,
shards, logs, hashes y tiempos. Los arrays grandes quedan fuera de Git.

Potencia: se aplicó la secuencia congelada, y N=200 fue el primer tamaño válido.
Sólo se usó el piloto G3 s=.8. No hubo entrenamiento de prueba con semillas C2.
La compuerta anterior al entrenamiento utilizó tres controles sin entrenar distintos
de C2. El análisis no forma parte de esta ejecución.

Incidente conservado: verify_v1.py bloqueó su propio manifiesto por una ruta fuera
de la lista permitida. Se congeló la enmienda 205635e antes de implementar verify_v2
(89cea82). V2 precarga el manifiesto propio y escribe salidas en cohorte/; las mismas
comprobaciones pasan con la guarda intacta. No se reentrenó ni se recomputó rho,
ni se alteró la tabla SHA `afd4783c2505251a1456aed9b3f8583d8f98c186908d2611be7f3dedd64eca19`.

Se dejan SIN CALCULAR el régimen agregado (c/q), D, p, W y toda asociación entre X10
y rho/Y. El análisis único corresponde a Claude y el cierre al responsable. Este
informe no afirma PASS/NOT_MET de la hipótesis, colapso de la cohorte ni transferencia.
