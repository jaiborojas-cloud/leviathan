# Tabla larga de CIFAR F1 · propuesta v1

CSV UTF-8, LF, un registro por trayectoria/visita, orden split→k→visita;2.000 filas planificadas. Conservar ausentes/fallidas como filas con estado y error. El analista también contabiliza IDs/visitas ausentes, nunca los elimina del denominador. Archivo propuesto `cifar_f1_visitas.csv`.

Columnas exactas, en este orden:

```text
trajectory,split,k,update,estado,error,X,R,c,q,tr_M,acc_train,acc_panel,acc_test,ce_train,ce_panel,ce_test,k_star,k_star_wrong,frac_panel_wrong,rho_caras,rho_vert,rho_status,rho_reason,rho_caras_quad_error,rho_caras_prefix_bound,rho_caras_tail_bound,rho_vert_quad_error,rho_vert_prefix_bound,rho_vert_tail_bound,rho_evaluations,rho_seconds,model_sha256,f_sha256,split_sha256,diagnostic_sha256
```

- Estados MEDIDA / INVALID_RHO / FALLIDA y auditoría rho según el [diseño](../DISENO_CIFAR_F1_BORRADOR_v1.md). No usar strings NaN/inf como valores válidos. Vacío es desconocido, no cero.
- X/R, c/q/tr_M y precisiones/CE se guardan por visita. X10 se toma exclusivamente de la fila update10. k_star es entero0..26; indicador mal clasificado0/1; fracción mal clasificada=1−acc_panel dentro de1e−12.
- rho se solicita solo en10/250. En5/30 `rho_status=NO_SOLICITADA`, campos rho numéricos y diagnostic_sha256 vacíos. En10/250 MEDIDA, rho_status=VALID_NUMERICAL_ESTIMATE y todos sus campos numéricos/digest de diagnóstico válidos. INVALID_RHO conserva los parciales, motivo y diagnóstico; no se usan sus rho en el ajuste.
- `model_sha256` identifica pesos; `f_sha256` e `split_sha256` deben ser comunes a todas las inicializaciones/visitas del split cuando hay métricas válidas. Una discordancia entre filas es un error estructural ABORTA, no un nuevo split inferido ni una selección de la fila conveniente.
- Campos de coste no tabulados, pesos, M, espectro, logits/etiquetas, f/cargas PCA, índices, RNG, warnings y resultado rho completo se conservan por visita en archivos externos con manifest. `diagnostic_sha256` enlaza el resultado rho completo.

`RESUMEN_F1.json` propuesto: campos obligatorios tabla_sha256, plan_sha256, productor_sha256, compuerta_sha256, dataset_sha256, fuentes (SHA por clave del plan), versiones (torch/numpy/scipy/sklearn) y tipo_datos (`PRUEBA_SINTETICA` o `CIFAR3_DESCUBRIMIENTO`). Puede añadir conteos operacionales/tiempos; no asociaciones. SHA del productor y dataset se pasan además explícitamente a la CLI desde su publicación previa. El analista no lee imágenes ni checkpoints.

La compuerta se entrega como JSON original de `compuerta_equivalencia.py` con sus9 checks, veredicto PASA, error≤1e−12, fuentes core/rho y versiones. Se enlaza por SHA; no se sustituye por la transcripción F0/F0b. No se ejecuta la compuerta en este borrador ni sus pruebas.
