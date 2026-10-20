# E16-B — Instrumentación en red nueva sin entrenamiento

Estado: **identidades PASS; validación independiente del rango INCONCLUSIVE**.
Red sintética 2→2→1, tres estados de pesos fijados antes de medir, sin reutilizar
T1/E15/T2-A. El usuario eligió crear esta red tras documentarse el faltante inicial
de un checkpoint independiente. No se afirma validación del aprendizaje.

- [Diseño congelado](DESIGN_FROZEN.md), commit `d05f31b` previo al código.
- [Formalización](mathematical_spec.md) y [configuración fija](config.json).
- [Conclusión](CONCLUSION.md), [resumen](results/run_v1/summary.json),
  [descriptivos](results/run_v1/descriptive.json), [progreso](progress.md).
- [Candidato histórico](DESIGN_CANDIDATE.md) e [inventario inicial](results/artifact_inventory.json).
- `freeze_manifest.csv`: hashes previos de protocolo, datos, fórmulas y dependencias.
- `manifest.csv`: archivos propios y hashes, salvo el propio manifest.

Desde la raíz del checkout, con Python 3.12 y entorno propio:

```sh
python -m pip install -r experiments/E16/B/requirements.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/B/scripts/run.py --output experiments/E16/B/results/replica
python experiments/E16/B/scripts/summarize.py experiments/E16/B/results/replica
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/B/scripts/verify.py
```

El ejecutor rechaza salidas existentes. Código de retorno 0 significa ejecución
sin FAIL; consultar summary.json para distinguir PASS de INCONCLUSIVE. El
verificador reproduce tablas en un directorio temporal; no repite ni modifica
outcomes históricos. En el entorno Codex se instaló autograd en
`/workspace/work/e16b-deps`; se usó PYTHONPATH apuntando allí. Ese directorio no
forma parte de la entrega. Sin binarios, entornos virtuales ni checkpoints.

La fase analítica [E16](../README.md) conserva sus archivos originales. El PR de
E16-B se abre dependiente del PR #5; no se fusiona ninguno automáticamente.
