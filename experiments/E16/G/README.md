# E16-G — Resolución numérica de las limitaciones de F

**PASS_NUMERICAL diagnóstico:** 324/324 longitudes validadas, incluidas las 85
que F dejó inconclusas. Pasan 13 102 controles. **F conserva INCONCLUSIVE** bajo
su protocolo original: G es un método nuevo aplicado a los mismos casos conocidos,
no una confirmación independiente ni un certificado riguroso.

- [Protocolo congelado](DESIGN_FROZEN.md), commit `7049807`.
- [Conclusión, resultados y límites](CONCLUSION.md).
- [Longitudes, rapidez y cotas por caso](results/run_v1/lengths.csv).
- [Comparación explícita F/G](results/run_v1/comparison_F.csv).
- [216 razones emparejadas](results/run_v1/paired_ratios.csv),
  [resumen por panel](results/run_v1/summary.json), [controles](results/run_v1/checks.csv).
- [Procedencia](results/run_v1/provenance.json), [recursos](results/run_v1/resources.json),
  [registro](progress.md), [manifest](manifest.csv).

## Qué cambia respecto a F

La rapidez al cuadrado sobre cada segmento es cuadrática. Su integral cerrada
se contrasta con tres órdenes de cuadratura en una partición concentrada cerca
del mínimo. Las cotas globales de positividad se subdividen mediante de Casteljau
con profundidad y presupuesto fijados antes de medir. No se añaden pisos
espectrales, no se cambian caminos ni se excluyen casos.

Se validan longitudes de caminos prefijados, no distancias geodésicas. No se
entrena ninguna red ni se modifica T2-A o evidencia A–F. La escala depende de
las unidades y de las funciones escalares declaradas en D.

## Reproducción

Python 3.12 y [dependencias fijadas](requirements.txt). Desde la raíz:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/G/scripts/verify.py
```

El verificador comprueba congelación, manifests, alcance y ausencia de cambios
en F y T2-A respecto a la base. Repite el experimento en un directorio temporal
y compara seis salidas científicas byte a byte. Recursos y tiempos se comparan
con el presupuesto, no byte a byte. Requiere el historial Git del diseño.
Para otra corrida sin sobrescribir evidencia:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/G/scripts/run.py --out /tmp/e16-g-nueva-corrida
```

El programa importa con hash fijo el método D, sin ejecutar sus corridas ni
escribir en su directorio. La tabla F se lee con hash fijo para conservar y
comparar los estados anteriores. En interrupción temporal se guardan las tablas
parciales disponibles; una salida incompleta no constituye PASS_NUMERICAL.
