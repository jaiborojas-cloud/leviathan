# E16-D — Réplica instrumental en configuraciones nuevas

**PASS_NUMERICAL: 396/396 rangos y 216/216 negativos detectados.**
Doce vectores nuevos de pesos, doce entradas nuevas y tres puntos principales
nuevos; red sintética sin entrenamiento. Mismo método instrumental C, con
procedencia y adaptación explícitas. No hay cambio de rango entre composiciones.

- [Diseño congelado](DESIGN_FROZEN.md), commit `c360f56` previo al código/resultados.
- [Formalización](mathematical_spec.md), [configuración](config.json).
- [Procedencia](provenance.json), [diff de adaptación](scripts/adaptation_from_C.patch).
- [Conclusión](CONCLUSION.md), [resumen](results/run_v1/summary.json),
  [comparación de composiciones](results/run_v1/secondary_summary.json).
- [Progreso](progress.md), [pasos posteriores](NEXT_PHASE.md).
- `freeze_manifest.csv`: hashes del protocolo, datos, fórmulas y procedencia previos.
- `manifest.csv`: hashes de archivos propios, salvo el propio manifest.

Desde la raíz del repositorio, en entorno propio:

```sh
python -m pip install -r experiments/E16/D/requirements.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/D/scripts/run.py --output experiments/E16/D/results/replica
python experiments/E16/D/scripts/summarize.py experiments/E16/D/results/replica
python experiments/E16/D/scripts/compare_compositions.py experiments/E16/D/results/replica
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/D/scripts/verify.py
```

El ejecutor rechaza salidas existentes. Código 0 significa ausencia de FAIL;
consultar summary.json para distinguir PASS de INCONCLUSIVE. El verificador
vuelve a ejecutar D en temporal y compara ocho tablas/reportes; no ejecuta las
etapas históricas. Requiere los commits de procedencia en el historial Git,
incluido C (`4fd7eb5`), para comprobar hashes. C está referenciado por commit,
sin copiar su carpeta completa a esta base.

En Codex se usó PYTHONPATH=/workspace/work/e16b-deps para autograd ya instalado
fuera del repo. No se suben entornos, cachés, checkpoints ni arrays binarios.
No son 396 ensayos estadísticamente independientes. Sin entrenamiento ni T2-A.
