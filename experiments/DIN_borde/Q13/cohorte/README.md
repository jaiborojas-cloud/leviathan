# DIN-Q13 — agente de cohorte

**INCONCLUSIVE_MANIPULACION en calibración; sin cohorte confirmatoria.**
Ninguna dosis de LS ni de WD logra la mediana c250 en [.55,.70]. Conforme al
diseño congelado, se detiene antes de potencia, plan y entrenamiento de cohorte.

900/900 ejecuciones de calibración válidas; cero errores. LS queda por debajo del
rango (c=.216–.417); WD por encima (c=.728–.807). Sólo se midieron c, q y precisión
del panel, sin X, rho ni asociaciones. No se accedió a la cohorte C2.

- [Resultado completo y tabla de dosis](RESULTADO_CALIBRACION_v1.md).
- [Tabla de 900 filas](calibracion_v1/calibracion.csv) y [resumen](calibracion_v1/summary.json).
- [Procedimiento](PROCEDIMIENTO_v1.md), [configuración](config_v1.json) y [scripts](scripts/).
- [Verificación](verification.json), [manifiesto](manifest.csv), [hashes de publicación](PUBLICACION_v1.sha256).
- [Arrays externos](external_manifest.csv): 900 archivos de pesos/M/f/datos preservados fuera de Git.

Reproducción en una copia separada y sin salidas previas, nunca sobrescribir:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
python experiments/DIN_borde/Q13/cohorte/scripts/calibrate_v1.py
```

El script exige código y configuración comprometidos y verifica los SHA originales.
No ejecutar la potencia ni el análisis Q13 sobre esta calibración. Una continuación
necesita otro protocolo autorizado; no se usa el piloto como cohorte confirmatoria.
