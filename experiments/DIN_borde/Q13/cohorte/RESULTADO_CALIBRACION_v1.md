# DIN-Q13 — cierre de calibración

**INCONCLUSIVE_MANIPULACION. Ambos manipuladores descartados por la regla
congelada; no se genera cohorte.** No es un veredicto sobre la hipótesis científica.

Se completaron las nueve condiciones de 20 splits × 5 inicializaciones: **900/900
ejecuciones medidas, cero errores**. Datos, pesos iniciales y secuencia de lotes
coinciden exactamente entre condiciones pareadas. Sólo se midieron c250, q250 y
acc_panel250. No se calcularon X ni rho en el piloto, ni asociaciones.

| Brazo | Dosis | Mediana c250 | Mediana q250 | Mediana acc_panel250 | Elegible |
|---|---:|---:|---:|---:|---|
| A0 | 0 | .807580 | .000115496 | .925926 | Referencia |
| LS | .02 | .417018 | .000332055 | .888889 | No: c<.55 |
| LS | .05 | .355565 | .000403275 | .888889 | No: c<.55 |
| LS | .1 | .291260 | .000490452 | .888889 | No: c<.55 |
| LS | .2 | .216429 | .000601527 | .851852 | No: c<.55 y diferencia de acc≥.05 |
| WD | .001 | .807307 | .000115738 | .925926 | No: c>.70 |
| WD | .01 | .799057 | .000114272 | .925926 | No: c>.70 |
| WD | .05 | .784899 | .000126140 | .925926 | No: c>.70 |
| WD | .1 | .727703 | .000128058 | .925926 | No: c>.70 |

La dosis elegida es **ninguna para LS y ninguna para WD**. No se extrapolan dosis,
no se cambia [.55,.70], no se añade otra rejilla ni se seleccionan trayectorias.
El rango de precisión tampoco reemplaza el criterio de colapso. Tiempo de las
900 ejecuciones y cierre: 110.322 segundos, dos procesos de un hilo BLAS cada uno.

## Detención exigida por el diseño

[§3 y §8 del diseño congelado](../../DISENO_DIN_Q13_v1_CONGELADO.md) establecen que,
si caen los dos brazos, Q13 termina INCONCLUSIVE_MANIPULACION sin cohorte.
Por ello:

- N no se determina: no se ejecutó la simulación de potencia.
- No hay universo confirmatorio, plan, compuerta de cohorte ni entrenamiento Q13.
- Faltantes confirmatorios por brazo: no aplica; no hay IDs planificados. En la
  calibración hay 0 faltantes y 0 errores en cada condición.
- No se crean q13_plan.json, q13_cohorte.csv ni RESUMEN_q13.json ficticios.
- Se conservan tabla y resumen de **calibración**, claramente identificados.

Cualquier continuación con una rejilla distinta requiere una nueva autorización
y un protocolo prospectivo del responsable. Este agente no cambia el diseño.
La cohorte C2 queda intacta, sin lectura. El análisis Q13 no se ejecutó: su código
sólo se leyó para preparar una eventual simulación que no llegó a realizarse.

[Tabla completa](calibracion_v1/calibracion.csv) ·
[resumen de calibración](calibracion_v1/summary.json) ·
[verificación](verification.json) · [publicación por SHA](PUBLICACION_v1.sha256).
