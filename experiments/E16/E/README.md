# E16-E — Distancias y anisotropía relativa

**PASS_NUMERICAL instrumental; análisis exploratorio.** El rango 2 de E16-D
coexiste con cambios de tamaño y forma. En 216/216 comparaciones, tanto la
distancia entre métricas como su componente de forma superaron 1e-8.

- [Diseño congelado antes del código y resultados](DESIGN_FROZEN.md), commit `f9a1b58`.
- [Conclusión y límites](CONCLUSION.md).
- [Observables por caso](results/run_v1/comparisons.csv), [resumen](results/run_v1/summary.json)
  y [controles](results/run_v1/checks.csv).
- [Procedencia](results/run_v1/provenance.json), [recursos](results/run_v1/resources.json).

Se reutilizan los estados y datos de D sin entrenamiento. No es una muestra
independiente ni una continuación de T2-A. Se comparan producto y cuadrática
con la suma, con autovalores generalizados invariantes bajo cambio de carta.
La distancia calculada es entre tensores SPD en el mismo punto; no es la
distancia geodésica entre dos perspectivas.

## Reproducción

Python 3.12 y las versiones de [requirements.txt](requirements.txt). Desde la raíz:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/E/scripts/verify.py
```

El verificador calcula una repetición en un directorio temporal y compara cuatro
salidas científicas byte a byte. Comprueba hashes, congelación y ausencia de
cambios propios en T2-A respecto a `47f0eff`. Recursos y tiempos no se comparan
byte a byte. Una corrida aislada, sin sobrescribir evidencia:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/E/scripts/run.py --out /tmp/e16-e-nueva-corrida
```

El método analítico se importa de D con hash fijo; no se ejecuta su experimento
ni se escribe en su directorio. La verificación requiere el historial Git del
diseño. [Manifest local](manifest.csv); no modifica manifests históricos A–D.
