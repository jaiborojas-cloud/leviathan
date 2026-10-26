# DIN-C2: ejecución de generación y publicación, v1

Se aplica íntegro el [diseño congelado](../DISENO_DIN_C2_v1_CONGELADO.md),
SHA `d00abbad3ff4cfd2dbd34ba3c3a4ff4321a16d862e2f639e98802faca562ff80`.
Base: main `9be9352`, con PR #87 fusionado. No se modifica el diseño,
el análisis congelado ni sus pruebas. Este documento concreta la ejecución del agente de cohorte.

## Secuencia que se compromete antes de avanzar

1. Diseño ya congelado y verificado; este procedimiento y configuración de potencia.
2. Código de potencia → simulación piloto → resultados comprometidos.
3. Primer tamaño válido → `cohorte/c2_plan.json`, SHA y lista de IDs comprometidos.
4. Adaptación mínima de G3 y utilidades operacionales comprometidas.
5. Compuerta previa al entrenamiento: tres modelos **sin entrenar**, con semillas
   de control 641000..641002 (pesos), 651000..651002 (datos), ajenas a la cohorte.
   Guardar pesos y M, cargar pesos en otro modelo y recalcular M con las fuentes
   intactas. Exigir error relativo **0** y f idéntica; no calcular rho ni asociaciones.
   Es una reproducción de serialización/construcción, no entrenamiento de prueba.
   Comprometer las tres salidas antes del primer entrenamiento C2.
6. Entrenar todo el universo planificado, conservar fallos y publicar tabla, SHA,
   resumen, verificación de integridad y manifiestos. No ejecutar el análisis.

## Potencia, exclusivamente sobre descubrimiento G3

[Método/configuración](potencia/config_v1.json): sólo s=0.8 de G3, 100 splits
completos de cinco inicializaciones; no se reutiliza como cohorte. Se conserva el
método G3: cuatro soportes bootstrap y 100 ruidos gaussianos por soporte, 400
réplicas por celda; base cúbica centrada intra-split, ruido y calibración oráculo
idénticos a G3, 1999 permutaciones exactas del estimando C1. Se valida el motor
FWL contra las funciones intactas de C1 en cuatro tablas artificiales.

Varianza piloto: SSE residual de Y centrada tras la base cúbica, dividida por
500−100−rango(base). Calibración: beta² var(rX) = D_obj/(1−D_obj) × 0.8 sigma².
Semillas de potencia G3 412000/413000 con SeedSequence [base, nivel=2, N, marco].
Se remuestrean 100 splits, no 20. D_obj es el efecto oráculo del modelo; no es
idéntico al D de validación cruzada finito. Guardar ambos. Potencia condicional
al soporte piloto y al modelo gaussiano, no garantía universal.

Evaluar en orden N=200,256,320,400,512,640 y todos los efectos 0,.010,.012,.015,.017
para cada N visitado. Elegir el PRIMER N con Wilson95 inferior≥.8 para .012 y
Wilson95 superior≤.10 bajo 0. Detener tamaños siguientes. Si no hay N válido,
no generar ni entrenar cohorte. No se calcula potencia con datos de C2.

## Separación de funciones

Este agente no ejecuta `analisis_C2.py` ni sus pruebas sobre C2. No calcula D, p,
W, correlaciones ni asociaciones entre X10 y rho/Y de C2. La potencia usa sólo
el piloto G3. Los scripts de cohorte no importarán el motor estadístico de potencia
ni C1/C2. Sólo conteos, errores, tiempos, hashes y reconstrucción; se deja también
la compuerta c/q agregada al analista. Claude ejecuta una sola vez el análisis
congelado tras la publicación; el responsable decide el cierre.

Arrays, pesos, estados del optimizador y diagnósticos completos quedan fuera de Git.
No se leen Wine, Iris, datos T2/DIN-C1 ni estados G2/G3. Fuentes originales intactas.
Si aparece un defecto se conserva la versión y se congela una enmienda antes de corregir.
