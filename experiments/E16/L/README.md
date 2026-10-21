# E16-L — Refinamiento de longitud y del camino completo

**INCONCLUSIVE global:** la longitud del caso pendiente cumple el umbral original,
pero la forma no alcanza el acuerdo fijado y en 32 segmentos los reinicios dan
candidatos diferentes. El control de suma pasa. Los 36 reinicios validan gradiente,
estacionariedad y positividad; eso no demuestra estabilidad del camino completo.

- [Diseño congelado](DESIGN_FROZEN.md), commit `0212bcf`.
- [Conclusión y distinción longitud/forma](CONCLUSION.md).
- [Casos](results/run_v1/cases.csv), [resoluciones](results/run_v1/resolutions.csv),
  [resumen](results/run_v1/summary.json).
- [Todos los reinicios](results/run_v1/searches.csv),
  [parámetros finales](results/run_v1/vertices.csv),
  [diferencias de forma por nodo](results/run_v1/shapes.csv).
- [Gradientes contrastados](results/run_v1/gradients.csv),
  [tramos](results/run_v1/segments.csv), [controles](results/run_v1/checks.csv).
- [Procedencia](results/run_v1/provenance.json), [recursos](results/run_v1/resources.json),
  [registro](progress.md), [manifest](manifest.csv).

![Comparación de caminos y reinicios](figures/path_comparison.svg)

La figura deriva sólo de parámetros ya guardados. La ordenada es el desplazamiento
normal como fracción de la cuerda; no representa una distancia intrínseca RIPG.

Se refina h00/0/cuadrática en mallas anidadas 16/32/64 y se conserva h00/0/suma
como control. Se reutiliza sin modificar el objetivo de primitiva K, se contrastan
sus gradientes mediante diferencias MP80 locales equivalentes al objetivo completo
y se valida el recorrido elegido a 80/120 cifras con el instrumento G.
No hay entrenamiento, geodésicas certificadas ni cambios a K o T2-A.

## Reproducción

Python 3.12 y [dependencias fijadas](requirements.txt). Desde la raíz:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/L/scripts/verify.py
```

Verifica hashes, fuentes, congelación y alcance; reproduce diez salidas científicas
byte a byte en un directorio temporal. Recursos se comparan con presupuesto.
Requiere historial Git. **PASS_REPRODUCTION también reproduce los inconclusos.**
No garantiza igualdad entre plataformas distintas para la optimización float64.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/L/scripts/run.py --out /tmp/e16-l-nueva-corrida
```

No sobrescribir evidencia. Leer el estado en summary.json aunque el proceso termine
normalmente; ante tiempo agotado conserva las tablas parciales disponibles.
La figura se puede regenerar sin optimizar con dependencias opcionales de
[requirements-plot.txt](requirements-plot.txt):

```sh
python experiments/E16/L/scripts/plot_paths.py
```
