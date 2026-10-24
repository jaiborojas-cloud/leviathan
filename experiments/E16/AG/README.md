# E16-AG · ρ_borde frente a distancia real al borde

[Diseño previo](DESIGN_FROZEN.md) · [Teoría](THEORY.md) · [Fase0](progress.md).

80 estados:40 triángulos sintéticos de respuesta conocida y40 AF originales.
No equiparar el umbral de carta150 con el borde al infinito. Sólo fuentes
autorizadas, guarda AF, sin estados ni tablas T2.

**Estado v1:** Q1 PASS, Q2 FAIL, Q3 FAIL, Q4 INCONCLUSIVE,
Q5 FAIL_DESCRIPTIVE. Ochenta escapes refinados y11/11 controles previos PASS.
En los40 triángulos, ρ/d_borde real tiene mediana1.998884 y máximo4.266419;
en AF la distancia real permanece UNKNOWN. El umbral150 no es el borde infinito.

- [Conclusión y límites](CONCLUSION.md), [diccionario de datos](DATA_DICTIONARY.md).
- [Resultados v1](results/run_v1), [comparación por grupo](results/run_v1/groups.csv).
- [Respuesta conocida](results/run_v1/known_truth_summary.json),
  [estabilidad desde archivos](results/run_v1/stability_from_archives.csv).
- [Registro de ejecución](progress_run.md), [stdout/stderr original](execution.log).
- [Declaración inicial de entorno](requirements.txt),
  [dependencias completas v2](requirements_runtime_v2.txt), [errata](ERRATA_ENTORNO.md).

Desde la raíz, Python3.12; BLAS/OMP de un hilo:

```sh
python -m pip install -r experiments/E16/AG/requirements_runtime_v2.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/AG/scripts/run_v1.py --out /tmp/ag-salidas-nuevas --arrays /tmp/ag-arrays-nuevos
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/AG/scripts/verify.py
```

El runner rechaza sobrescribir directorios. Los originales .npy permanecen en
la ruta externa de resources.json; el verificador requiere esa copia para
comprobar hashes, y no integra geodésicas ni reejecuta etapas cerradas.
El diagnóstico contextual no se lee durante medición; su referencia y SHA
están congelados, porque todavía no estaba en main al preparar AG.

[Verificación desde archivos](verification.json):480 arrays con SHA y MP80
de la respuesta analítica, sin reintegrar. `scripts/derive.py` comprueba los
dos suplementos descriptivos y permite generarlos en un directorio nuevo.
