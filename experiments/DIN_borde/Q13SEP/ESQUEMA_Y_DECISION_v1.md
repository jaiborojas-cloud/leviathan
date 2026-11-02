# Q13-SEP · tablas y archivo de decisión propuestos

**BORRADOR**, complemento del [diseño](../DISENO_DIN_Q13SEP_BORRADOR_v1.md). Claude implementará el productor después de congelar. No hay datos o productor en esta entrega.

## Una fila por medida

`q13sep_medidas.csv`, UTF-8 y LF, con columnas exactas propuestas:

```text
phase,trajectory,condition,lambda,split,k,T_code,T,update,c,q,tr_M,S_panel,S_train,conf_media_verdadera_panel,conf_media_maxima_panel,acc_train,acc_panel,estado_medida,error,no_aprendio_final,checkpoint_original_sha256,checkpoint_T_sha256,M_sha256,f_sha256,dataset_sha256,batches_sha256,cpu_seconds,wall_seconds,M_seconds,memory_peak_mb
```

Fase = cal/val; condiciones cal = A0/LP01/LP02/LP03/LP04, val = A0/LP; lambda de A0 = 0. T_code/T = T05/.5, T10/1, T20/2. Updates 10/250. No X, mínimo de p_y, rho o estadísticos de señal. Son 1.500 filas planificadas de calibración y 1.200 de validación si esta procede; los entrenamientos son 250 y 200 respectivamente. Las tres reconstrucciones se archivan en el JSON de controles, sin duplicar esas filas principales. Una fila fallida conserva valores parciales y error; nada se rellena con cero.

`estado_medida` = MEDIDA/FALLIDA; MEDIDA exige dominios del diseño. Los valores y estados originales no se reescriben si después se observa NO_APRENDIO. `no_aprendio_final` = true/false/unknown según acc_train u250 de T1; si falta, la unidad no es completa. El registro final de entrenamiento enlaza todas sus medidas y sus errores. Un error de entrenamiento marca las visitas no alcanzadas como FALLIDA, nunca crea otro ID para reemplazarlas. Un fallo de medida no implica reentrenar o repetir ese punto.

Las decisiones operacionales usan el universo planificado, aun si falta alguna fila. La tabla final debe incluirla como FALLIDA/AUSENTE en error; no deducir el denominador de las filas recibidas. Datos, índices, pesos, optimizador/RNG y M completos van fuera de Git con hashes. Resúmenes con `tabla_sha256`, `plan_sha256`, `script_sha256`, SHA de controles y entorno, conteos y tiempos. El productor verifica las fuentes y el plan por SHA.

## Criterios E/C

Cada resultado se calcula en las mismas unidades r = (split,k). Se conservan las dos visitas juntas; una unidad pasa solo si cumple ambas. Un split pasa con ≥ 3/5 unidades **planificadas**, manteniendo inválidas en el denominador. Calibración: ≥ 8/10 splits; validación: ≥ 16/20. Escalas no positivas se reportan y no se logaritman. La calidad conjunta del diseño se aplica antes de la selección de dosis y de decidir separabilidad.

Para cada par/orientación de calibración, reportar dosis, pregunta E/C, temperaturas, orientación, procedencia (T fija o distinta), r válidos/fallidos/pasan, IDs y los conteos por split, número de splits que pasan y diferencias/ratios de cada visita. Tabular los nueve pares y ambas orientaciones, no solo el ganador. No calcular significación estadística ni seleccionar por confianza o precisión.

`DOSIS_Y_CONTRASTES_Q13SEP.json`, tras calibración y **antes de entrenar validación**, debe contener:

- SHA del diseño, plan, productor, tabla de calibración y controles; universo de calibración completo.
- Calidad de toda la fase; estado de cada dosis según E/C, sin eliminación discrecional.
- λ elegida por la regla de menor apta, o null y NO_IDENTIFICABLE con motivo.
- Para E y C: primer par/orientación aptos, sus márgenes y conteos, con T_a, T_b y σ, y su etiqueta de procedencia. Reglas sin cambios en validación.
- Rejilla, orden de desempate y criterios del diseño; no claves X, rho o D.

La validación informa exclusivamente esos dos principales para su veredicto; registra todos los parciales y faltantes. Las otras comparaciones entre brazos pueden archivarse como métricas de c/S, pero no sustituir el par prefijado. La sensibilidad SOLO_TEMPERATURA usa solo (.5,1), (.5,2), (1,2) por brazo y σ±, sin rescate. No se buscan coincidencias entre redes no pareadas.

## Decisión final

| Calidad/controles | E entre brazos | C entre brazos | Veredicto operativo |
|---|---|---|---|
| Válidos | cumple ≥ 16/20 | cumple ≥ 16/20 | SEPARABILIDAD_LOGRADA |
| Válidos | cualquier otro patrón | | NO_IDENTIFICABLE; detener vía |
| Calidad insuficiente o control fallido | desconocido | desconocido | NO_IDENTIFICABLE por falta de evidencia válida; estado INVALIDA si falla un control |

Si no hubo dosis apta en calibración, no existe validación y se reporta NO_IDENTIFICABLE/CALIBRACION_SIN_DOSIS. No se cambia esa decisión porque una dosis no elegida o un contraste SOLO_TEMPERATURA parezca favorable.

El informe distingue ENTRE_BRAZOS_T_FIJA y ENTRE_BRAZOS_T_DISTINTA **por cada dirección**. La segunda no demuestra separación atribuible solo al entrenamiento. Ningún veredicto identifica el colapso como causa o autoriza un análisis de señal con estos datos.
