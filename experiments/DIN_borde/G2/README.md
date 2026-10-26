# DIN-G2 · resolución variable del ejemplo difícil

Exploratorio. Seis mezclas gaussianas de tres clases,20 splits×5 inicios
por nivel,600 entrenamientos y4200 visitas previstas. Sin Wine, Iris,
datos T2 ni DIN-C1. No cambia instrumentos ni etapas previas.

- [Diseño congelado](DESIGN_FROZEN.md), [configuración](config.json).
- [Fuentes/SHA](freeze_manifest.csv), [registro de lectura](progress.md).
- [Teoría y alcance del estimando](THEORY.md).

Primario: rho_caras de I2 r3; secundario rho_vert. Se pregunta si D de C1
es mayor donde la clasificación final del dominante varía entre inicios
del mismo split. No implica causalidad ni transferencia.

## Método

s=(.25,.5,.8,1.2,2,4), d13, tres medias de triángulo equilátero de radio2
y covarianza s²I. Train90 y panel27 balanceados; estandarización ajustada
sólo en train. Misma realización gaussiana, pesos iniciales y lotes entre
niveles;20 réplicas sintéticas independientes, cinco inicios por réplica.
Red13→64→32→3, Adam lr.006/lote64,250 updates sin parada temprana.

core.make_geom_state/subset_M, geometry e I2/rho_borde_v2.py r3 se importan
intactos con SHA verificado. C1/cen,D_cv,primaria se reutilizan como funciones
matemáticas sobre nuestros datos, sin CLI ni archivos de cohorte. Son999
permutaciones por ajuste, exclusivamente exploratorias. D no cambia respecto
al estimando C1; la menor cantidad de permutaciones reduce su resolución p.

## Reproducibilidad y archivos

Los4200 estados contienen escalares, errores y referencias SHA. Matrices,
scores, pesos, momentos Adam, RNG y diagnósticos rho completos permanecen
fuera de Git en `/workspace/work/din-g2-v1-arrays`. Los sintéticos se regeneran
desde las semillas; no se necesita ni descarga un dataset externo. Todos los
archivos se crean en modo exclusivo: no sobrescribir ni repetir una corrida
sobre resultados existentes.

En una copia independiente y entorno limpio, el commit `cc75471` conserva
todos los scripts antes de archivar salidas. Con sus dependencias y fuentes
congeladas, desde la raíz, ejecutar con BLAS/OMP1 y sin pycache:

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python experiments/DIN_borde/G2/scripts/run_v1.py --part prepare
python experiments/DIN_borde/G2/scripts/run_v1.py --part cohort
python experiments/DIN_borde/G2/scripts/verify_v1.py --part reconstruct
python experiments/DIN_borde/G2/scripts/analysis_v1.py
python experiments/DIN_borde/G2/scripts/verify_v1.py --part final
python experiments/DIN_borde/G2/scripts/plot_v1.py
python experiments/DIN_borde/G2/scripts/report_v1.py
```

Presupuestos fijos:14400s globales y los predeterminados60s/4096 evaluaciones
de I2 por estado; dos procesos y un hilo por proceso. No se reanuda ni extiende
el entrenamiento tras inspeccionar outcomes. Una falla requiere versión nueva
y registro prospectivo; los UNKNOWN/UNMEASURED conservan su significado.

## Resultado y consulta

**H-var: CONTRADICE_DESCRIPTIVAMENTE**, por la regla primaria congelada.
La variación fue máxima en s=.5 y el incremento D fue negativo; los
incrementos positivos aparecieron con V=0 en s=2/4. No es una refutación
universal: las medianas de concentración de M también cambian con s.

- [Conclusión y límites](CONCLUSION.md), [tabla seis niveles](results/run_v1/levels.csv).
- [Análisis C1/D7](results/run_v1/analysis.json), [figura](figures/resolucion.png).
- [Verificación](verification.json), [manifest SHA](manifest.csv).
- [Archivo reversible](ARCHIVO.md), [4200 registros completos](results/run_v1/state_records.jsonl).
- [SHA por registro original](state_records_manifest.csv), [inventario externo](external_manifest.csv).

Los JSON originales individuales se conservan en la ejecución; en Git se
versionan en JSONL reversible bit a bit. El script archive_v1.py --part unpack
los comprueba/restaura sin sobrescribir. Los diagnósticos rho completos y
arrays permanecen externos, con sus SHA y rutas; las semillas permiten
recrear la cohorte sintética en un entorno limpio sin datos protegidos.
