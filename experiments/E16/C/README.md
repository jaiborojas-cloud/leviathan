# E16-C — Control de mayor precisión del rango

**PASS_NUMERICAL**: 81 configuraciones principales y 18 controles de rango.
Referencia analítica independiente 80/120 dps, autodiff y diferencias finitas de
cuarto orden, con error transportado por la cométrica. No hubo entrenamiento.

E16-B conserva su INCONCLUSIVE original. Este es un reanálisis instrumental de
los mismos estados conocidos, no una muestra confirmatoria de aprendizaje.

- [Diseño congelado](DESIGN_FROZEN.md), commit `1b68c4e` previo al código.
- [Derivaciones y límites de las cotas](mathematical_spec.md).
- [Configuración fija](config.json), [procedencia](sources.json).
- [Conclusión](CONCLUSION.md), [resumen](results/run_v1/summary.json),
  [descriptivos](results/run_v1/descriptive.json), [progreso](progress.md).
- `freeze_manifest.csv`: hashes preejecución del protocolo, datos y fórmulas.
- `manifest.csv`: hashes de archivos propios, salvo el propio manifest.

Desde la raíz del checkout, con entorno propio y Python 3.12:

```sh
python -m pip install -r experiments/E16/C/requirements.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/C/scripts/run.py --output experiments/E16/C/results/replica
python experiments/E16/C/scripts/summarize.py experiments/E16/C/results/replica
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/C/scripts/verify.py
```

El ejecutor rechaza directorios existentes; consultar summary.json para el estado
científico, además del código de retorno (1 sólo si FAIL). El verificador reproduce
cinco tablas/reportes exactamente en este entorno; tiempos no forman parte de
esas tablas. No ejecuta scripts A/B ni T2-A. En Codex, autograd está instalado
fuera del repo, con PYTHONPATH=/workspace/work/e16b-deps; no se versiona ese entorno.
