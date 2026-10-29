# DIN-CIFAR F1 · revisión v2 para auditoría

**BORRADOR, sin congelar.** Esta revisión responde a los tres cambios solicitados tras la auditoría del PR #127. La v1 y sus 54 salidas quedan intactas.

- [Diseño v2](../../DISENO_CIFAR_F1_BORRADOR_v2.md): espacios revisados, estratos por mediana del split y definición explícita de longitud y `quad_error = None`.
- [Plan v2](../plan_F1_BORRADOR_v2.json): mismo universo, semillas, primaria y opciones rho; regla de estratos explícita.
- [Protocolo de revisión](PROTOCOLO_REVISION_v2.md): comprometido antes del código y las nuevas pruebas.

La mediana de c250 se calcula entre las trayectorias elegibles de cada split usado por la primaria. Los cortes son .4 y .8, y se conservan juntas todas las trayectorias elegibles. Se reportan los splits de cada estrato, incluidos los que no llegan al mínimo de 20 splits para calcular D. El límite de 120 s queda como requisito del futuro productor.

[Analista v2](../analisis_F1_v2.py), [pruebas v2](../pruebas_F1_v2.py), [esquema v2](../ESQUEMA_TABLA_v2.md), [reporte de 71 pruebas](PRUEBAS_F1_v2.md), [verification.json](verification.json) y [manifest](manifest.sha256). La primaria se conserva exactamente en las 20 tablas de comparación. No se crea productor ni se usa ninguna cohorte real.

Para una reproducción sintética, con los [requisitos heredados](../requirements.txt), usar una copia donde las rutas de salida nuevas estén vacías; el script nunca sobrescribe una corrida existente:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python -I experiments/DIN_borde/CIFAR/F1/pruebas_F1_v2.py
```

Los fixtures se conservan fuera de Git en `/workspace/work/din-cifar-f1-pruebas-v2`, enlazados por SHA. La v1 sigue accesible desde su [índice histórico](../README.md).
