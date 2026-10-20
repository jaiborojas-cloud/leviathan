# E16-H — Transferencia prospectiva del instrumento

**PASS_NUMERICAL:** 324/324 longitudes nuevas y 216/216 pares validados;
13 102/13 102 controles pasan con el método y las tolerancias de G intactos.
Se satisface la hipótesis instrumental predefinida para esta muestra sintética.
No constituye una ley general de RIPG ni una evaluación predictiva.

- [Diseño previo](DESIGN_FROZEN.md), commit `3c96c95`.
- [Datos nuevos congelados](data.json), [configuración](config.json).
- [Conclusión y alcance](CONCLUSION.md).
- [Longitudes por caso](results/run_v1/lengths.csv),
  [razones emparejadas](results/run_v1/paired_ratios.csv),
  [resumen por panel](results/run_v1/summary.json), [controles](results/run_v1/checks.csv).
- [Procedencia](results/run_v1/provenance.json), [recursos](results/run_v1/resources.json),
  [registro](progress.md), [manifest](manifest.csv).

Se usan 12 estados, 12 entradas y tres perspectivas nuevos, con semillas
20261022/20261023/20261024, sin selección ni entrenamiento. Se mantiene la misma
familia de red, cométrica regularizada y escalares de D/G. Los tres segmentos
unen los puntos nuevos. Se calculan longitudes, no mínimos geodésicos.

## Método intacto

[Adaptador explícito desde G](scripts/adapt_from_G.py): cambia entrada y procedencia,
y elimina la comparación por caso con F porque son configuraciones distintas.
El verificador reconstruye el programa desde G y compara por AST las 14 funciones
compartidas, incluidos primitiva, cuadratura, partición y Bernstein. Comprueba
que las opciones numéricas y controles sigan siendo los de G.

## Reproducción

Python 3.12 y [dependencias fijadas](requirements.txt). Desde la raíz:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/H/scripts/verify.py
```

Comprueba hashes, congelación previa, regeneración de los sorteos sin filtrado,
ausencia de coincidencias exactas con datos D, identidad de método/configuración,
alcance y reproducción byte a byte de cinco salidas científicas. La repetición
no cuenta como muestra adicional. Tiempo y memoria se verifican contra el
presupuesto. Se requiere el historial Git del diseño y las fuentes D/G intactas.
Una corrida aparte, sin sobrescribir evidencia:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/H/scripts/run.py --out /tmp/e16-h-nueva-corrida
```

El programa importa el método analítico D con hash fijo y ρ verificado; no ejecuta
corridas previas ni escribe en sus directorios. T2-A y evidencia A–G intactas.

Para comprobar sólo integridad y alcance sin repetir mediciones:

```sh
python experiments/E16/H/scripts/verify.py --integrity-only
```

La base de integración remota está fijada en [integration.json](integration.json);
no sustituye la congelación científica. Los tres índices conservan las entradas
E/F/G/H tras resolver su actualización concurrente.
