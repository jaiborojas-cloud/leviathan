# E16-M — Seguimiento de candidatos y localización del cambio

**INCONCLUSIVE global por forma.** Los dos candidatos cuadráticos distintos L32
coinciden dentro de tolerancia en 64 y 128 segmentos al seguirlos por separado,
pero cada linaje sigue cambiando de forma al refinar. El control de suma pasa.
Los nueve recorridos validan longitud, gradiente, KKT y positividad numérica.

- [Diseño previo](DESIGN_FROZEN.md), commit `eacfa4d`, [grupos congelados](groups.json).
- [Conclusión y límites](CONCLUSION.md).
- [Corrección de lectura y v1 preservada](ERRATA_IMPLEMENTACION_v1.md).
- [Resumen v2](results/run_v2/summary.json), [linajes](results/run_v2/lineages.csv),
  [recorridos](results/run_v2/trajectories.csv), [parámetros](results/run_v2/vertices.csv).
- [Refinamiento](results/run_v2/transitions.csv),
  [comparación entre candidatos](results/run_v2/cross_candidates.csv),
  [localización](results/run_v2/localization.csv), [diferencias por nodo](results/run_v2/shape_nodes.csv).
- [Gradientes](results/run_v2/gradients.csv), [tramos](results/run_v2/segments.csv),
  [controles](results/run_v2/checks.csv), [referencias redondeadas](results/run_v2/source_reference_intervals.csv).
- [Procedencia](results/run_v2/provenance.json), [recursos](results/run_v2/resources.json),
  [registro](progress.md), [manifest](manifest.csv).

![Seguimiento y localización](figures/lineage_comparison.svg)

La figura se deriva de tablas guardadas. Los identificadores siguen el origen de
la inicialización; no certifican continuidad de una rama matemática, unicidad,
una bifurcación ni geodésicas. El cambio de forma es normalizado por la cuerda,
no una distancia intrínseca RIPG.

## Qué se preserva

El agrupamiento usa todos los candidatos L32, ordenados por índice; representante
primero de cada grupo, sin elegir el más corto. Hay dos grupos cuadráticos y un
control. Cada uno se prolonga por separado a 64/128, sin reinicios adicionales.
No se altera L. La primera implementación v1 trató una referencia de 40 cifras
como exacta: se conserva íntegra y se corrige sólo su lector en v2 mediante un
intervalo de redondeo, sin cambiar tolerancias o parámetros científicos.
Siete tablas de geometría y gradientes son idénticas byte a byte entre v1/v2.

## Reproducción

Python 3.12 y [dependencias](requirements.txt). Desde la raíz:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/M/scripts/verify.py
```

Verifica hashes, agrupamiento, diseño y corrección congelados, v1 intacta,
igualdad de geometría v1/v2, alcance y trece salidas científicas v2 reproducidas
byte a byte. Tiempo separado contra presupuesto; requiere historial Git.
**PASS_REPRODUCTION no elimina los cuatro incumplimientos de forma.**

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/M/scripts/run.py --out /tmp/e16-m-nueva-corrida
```

No sobrescribir resultados. Leer summary.json: el proceso puede finalizar
normalmente con INCONCLUSIVE. Ante tiempo agotado conserva tablas parciales.
La igualdad se comprobó en el entorno declarado, sin garantía entre plataformas.
La figura se regenera sin optimizar mediante [dependencias opcionales](requirements-plot.txt):

```sh
python experiments/E16/M/scripts/plot_lineages.py
```

L, evidencia anterior y T2-A permanecen intactos. No hay entrenamiento ni
certificados intervalares o de mínimo global.
