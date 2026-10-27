# DIN-Q13-M2: calibración de LP y WD

Calibración registrada antes de medir. Solo c250,q250 y acc_panel250; no X,rho,D ni asociaciones.**7.000/7.000 ejecuciones medidas, cero fallos. LP y WD cumplen los tres criterios de elegibilidad.** Diseño de calibración: A0 y13 dosis,100 splits×5 inicializaciones pareadas por condición. No se eligen dosis confirmatorias.

- [Protocolo de referencia](../PROTOCOLO_CALIBRACION_M2_v1.md), SHA08551c58…; permanece intacto.
- [Procedimiento operativo previo](PROCEDIMIENTO_v1_CONGELADO.md) y [configuración](config_v1.json).
- [Implementación publicada antes de medir](IMPLEMENTACION_v1.sha256), commit16139f48651eb798b50606a64b33e3cf916ec801.
- [Resultado y elegibilidad](RESULTADO_v1.md), [resumen por condición](resumen_condiciones.csv) y [criterios por manipulador](elegibilidad.json).
- [Tabla de todos los IDs](results_v1/calibracion.csv), [resumen completo](results_v1/summary.json), [controles](results_v1/controls.json), [pareado](results_v1/pairing.json).
- [Verificación](verification.json), [pruebas independientes de resumen](unit_summary_v1.json), [manifest](manifest.csv), [SHA](manifest.sha256) y [arrays externos](external_manifest.csv).

La receta base recipe_v1.py está copiada byte por byte. A0/WD llaman su update original; LP usa el adaptador recipe_m2.py con CE+lambda·media(||z||²),Adam sin decay. El soporte original se conserva como fuente,con soporte de ejecución nuevo para esta carpeta. core y geometry se verifican por SHA; rho no se importa ni calcula.

Semillas nuevas:901000+s para datos,902000+5s+k para inicialización y903000+5s+k para lotes. Las14 condiciones usan las mismas semillas por par. Los arrays/pesos,matrices M y f y datos generados se archivan fuera de Git; los JSON de registros guardan SHA,warnings,errores y tiempos. No se leen datos de otras cohortes.

## Alcance de los resúmenes

IC95 percentil de la mediana c:2000 remuestreos de100 splits completos con sus cinco k,semilla904001. Los mismos draws se aplican a todas las condiciones. Una condición incompleta conserva los fallos y deja medianas/IC oficiales desconocidos; la fracción tiene límites según los faltantes. No se sustituyen ni excluyen retrospectivamente trayectorias fallidas.

Se aplican los tres criterios exactos de§5. Las dosis testigo solo muestran el cumplimiento de un criterio; no son dosis seleccionadas del confirmatorio. No se interpolan dosis ni se amplía la rejilla. La monotonía es descriptiva de las medianas de esta calibración, no un certificado de la curva poblacional.

## Reproducción

Python3.12.14;torch2.9.1+cpu,numpy2.3.5,scipy1.17.0,scikit-learn1.8.0. Dos procesos spawn,un hilo BLAS por proceso. Las dependencias deben estar instaladas previamente; ningún script usa red o datos externos al generador sintético.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python experiments/DIN_borde/Q13M2/calibracion/scripts/calibrate_v1.py
```

La ejecución usa carpetas exclusivas y se detiene si ya existen; no borrar resultados para repetir. Cualquier repetición o corrección requiere conservar esta versión y registrar rutas/código nuevos. La publicación posterior verifica IDs,hashes,pareado,bootstrap y c/q de las matrices archivadas sin entrenar de nuevo.
