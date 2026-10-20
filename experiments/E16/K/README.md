# E16-K — Diagnóstico de gradiente y mallas anidadas

**INCONCLUSIVE global:** dos de los tres casos difíciles J cumplen el protocolo K;
uno sigue inconcluso por refinamiento. Los dos controles de suma pasan.
Los 85 reinicios pasan validación de objetivo, gradiente, estacionariedad y SPD;
las 15 resoluciones pasan individualmente, pero un caso no alcanza el acuerdo
exigido entre 8 y 16 segmentos. **J conserva sus resultados originales.**

- [Protocolo previo](DESIGN_FROZEN.md), commit `2a1a9d3`.
- [Conclusión y límite conservado](CONCLUSION.md).
- [Casos y refinamiento](results/run_v1/cases.csv), [resumen](results/run_v1/summary.json).
- [Resoluciones y acuerdo entre reinicios](results/run_v1/resolutions.csv).
- [Todas las búsquedas](results/run_v1/searches.csv), [parámetros finales](results/run_v1/vertices.csv).
- [Gradientes independientes](results/run_v1/gradients.csv),
  [tramos](results/run_v1/segments.csv), [controles](results/run_v1/checks.csv).
- [Procedencia](results/run_v1/provenance.json), [recursos](results/run_v1/resources.json),
  [registro](progress.md), [manifest](manifest.csv).

El objetivo usa la integral cerrada diferenciada por autograd, contrastada
mediante diferencias centrales MP80. La fórmula calcula el residual ortogonal
para evitar cancelación en la rapidez mínima; no añade pisos numéricos.
Las mallas tienen 4/8/16 segmentos y prolongación del mismo camino anterior.
Se conservan todos los reinicios y no se relajan umbrales después de medir.

El estudio es diagnóstico sobre casos conocidos, sin entrenamiento. El acuerdo
entre reinicios en K no demuestra unicidad ni explica por sí solo la dispersión
de J: cambiaron tanto la integración como las familias de caminos.
No se certifican geodésicas continuas ni mínimos globales.

## Reproducción

Python 3.12 y [dependencias fijadas](requirements.txt). Desde la raíz:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/K/scripts/verify.py
```

Comprueba hashes, congelación, selección explícita de los casos, fuentes y alcance;
repite en un directorio temporal y compara nueve salidas científicas byte a byte.
Tiempo y memoria se verifican contra el presupuesto. Requiere historial Git.
La igualdad exacta se verifica en el entorno declarado, no entre cualquier plataforma.
**PASS_REPRODUCTION no elimina el caso inconcluso.**

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/K/scripts/run.py --out /tmp/e16-k-nueva-corrida
```

No sobrescribir evidencia. El proceso puede finalizar normalmente con INCONCLUSIVE;
leer summary.json. Si agota tiempo conserva tablas parciales.
No ejecuta fases anteriores ni modifica sus directorios. T2-A permanece intacto.
