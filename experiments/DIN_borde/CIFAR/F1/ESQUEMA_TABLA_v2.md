# Tabla larga de CIFAR F1 · propuesta v2

CSV UTF-8, LF, un registro por trayectoria y visita, orden split → k → visita; 2.000 filas planificadas. Conservar ausentes y fallidas como filas con estado y error. El analista también contabiliza los IDs y visitas ausentes, sin eliminarlos del denominador. Archivo propuesto: `cifar_f1_visitas.csv`.

**Las columnas y sus dominios no cambian respecto de v1.** Esta copia revisa los espacios, aclara la auditoría rho y enlaza el diseño v2.

Columnas exactas, en este orden:

```text
trajectory,split,k,update,estado,error,X,R,c,q,tr_M,acc_train,acc_panel,acc_test,ce_train,ce_panel,ce_test,k_star,k_star_wrong,frac_panel_wrong,rho_caras,rho_vert,rho_status,rho_reason,rho_caras_quad_error,rho_caras_prefix_bound,rho_caras_tail_bound,rho_vert_quad_error,rho_vert_prefix_bound,rho_vert_tail_bound,rho_evaluations,rho_seconds,model_sha256,f_sha256,split_sha256,diagnostic_sha256
```

- Estados MEDIDA / INVALID_RHO / FALLIDA y auditoría rho según el [diseño v2](../DISENO_CIFAR_F1_BORRADOR_v2.md). No usar strings NaN/inf como valores válidos. Vacío es desconocido, no cero.
- X/R, c/q/tr_M y precisiones/CE se guardan por visita. X10 se toma exclusivamente de la fila update = 10. k_star es entero de 0 a 26; indicador mal clasificado: 0/1; fracción mal clasificada = 1 − acc_panel, dentro de 1e−12.
- Rho se solicita solo en 10/250. En 5/30, `rho_status=NO_SOLICITADA`, con campos rho numéricos y diagnostic_sha256 vacíos. En 10/250 MEDIDA, rho_status = VALID_NUMERICAL_ESTIMATE y todos sus campos numéricos y digest de diagnóstico son válidos. INVALID_RHO conserva los parciales, motivo y diagnóstico; no se usan sus rho en el ajuste.
- Para cada ganador, «longitud» = su propio valor de ρ: rho_caras o rho_vert. Quad_error debe ser finito y no negativo; **`quad_error = None` es inválido**, nunca cero. Lo mismo vale para los términos de prefijo y cola. Se mantienen los límites de 1e−6 · longitud para quad_error y para la suma de prefijo y cola.
- `model_sha256` identifica los pesos; `f_sha256` e `split_sha256` deben ser comunes a todas las inicializaciones y visitas del split cuando hay métricas válidas. Una discordancia entre filas es un error estructural ABORTA, no un nuevo split inferido ni una selección de la fila conveniente.
- Campos de coste no tabulados, pesos, M, espectro, logits/etiquetas, f y cargas PCA, índices, RNG, warnings y resultado rho completo se conservan por visita en archivos externos con manifest. `diagnostic_sha256` enlaza el resultado rho completo. El watchdog externo de 120 s debe implementarlo el productor; el CSV no demuestra su ejecución.

`RESUMEN_F1.json` propuesto: campos obligatorios tabla_sha256, plan_sha256, productor_sha256, compuerta_sha256, dataset_sha256, fuentes (SHA por clave del plan), versiones (torch/numpy/scipy/sklearn) y tipo_datos (`PRUEBA_SINTETICA` o `CIFAR3_DESCUBRIMIENTO`). Puede añadir conteos operacionales y tiempos; no asociaciones. Los SHA del productor y del dataset se pasan además explícitamente a la CLI desde su publicación previa. El analista no lee imágenes ni checkpoints.

La compuerta se entrega como JSON original de `compuerta_equivalencia.py` con sus 9 checks, veredicto PASA, error ≤ 1e−12, fuentes core/rho y versiones. Se enlaza por SHA; no se sustituye por la transcripción F0/F0b. No se ejecuta la compuerta en este borrador ni en sus pruebas.

## Reporte secundario de estratos v2

El analista no cambia las c individuales del CSV. Calcula la mediana de c250 entre los IDs elegibles de cada split usado por la primaria y asigna todo el split a bajo (< .4), intermedio ([.4, .8)) o alto ([.8, 1]). Todos sus IDs elegibles permanecen juntos.

En `secundarios.estratos_c250`, cada estrato incluye `n_splits`, `ids_splits`, `ids_trayectorias`, `mediana_c_por_split`, `n_elegibles_por_split`, conteos de entrada y uso, medianas de c/q y mediana de las medianas de split. D y pendiente solo se definen con al menos 20 splits de ≥ 3 elegibles y ajuste identificable; los conteos se conservan si el resultado es NO_DEFINIDO. `secundarios.asignacion_estratos_c250` documenta la regla, los cortes, los empates hacia el estrato superior y los splits fuera de la primaria. Sin permutaciones adicionales, sin tendencia causal y sin rescatar la primaria.
