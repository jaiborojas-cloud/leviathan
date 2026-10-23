# E16-AA · continuación a KKT físico 1e-7

Estudio exploratorio prospectivo de las doce curvas finales de
[Z](../Z/README.md). Se exige un residuo cien veces menor, sin cambiar la malla
ni recalcular la masa. Los pesos de la red permanecen fijos.

- [Protocolo congelado](DESIGN_FROZEN.md) y [configuración](config.json).
- [Formulación y límites](THEORY.md).
- [Conclusión y resultados](CONCLUSION.md).
- [Registro](progress.md), [tablas](results/run_v1),
  [figura](figures/tolerance_comparison.svg).

Los identificadores terminados en132/264 proceden de S; las curvas actuales
tienen264/528 segmentos. reference/scaled son procedencias, no dos métodos AA.

## Reproducción

Usar Python3.12 y las versiones de [requirements.txt](requirements.txt).
Con dependencias instaladas, desde la raíz:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/AA/scripts/run.py --out /tmp/e16-aa-nuevo
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/AA/scripts/verify.py
```

La primera orden escribe una corrida nueva fuera de los resultados versionados.
La segunda reconstruye rachas, KKT, costes, hashes, clases y elegibilidad desde
los archivos, verifica congelación y alcance, y ejecuta una sola repetición
temporal comparando once salidas científicas byte a byte. Un resultado científico
INCONCLUSIVE puede ser reproducible y superar esta verificación de integridad.
resources.json registra tiempos y memoria, excluidos de igualdad exacta.

No se versionan Hessianas, autovectores ni checkpoints. Se preservan nueve CSV
(checks, paths, vertices, gradients, monitor, spectra, audits, comparisons, costs),
summary.json y provenance.json. manifest.csv cubre archivos finales; los manifests
de diseño e implementación son independientes y permanecen congelados.

## Interpretación

El residuo no es certificado riguroso. Los espectros de puntos que no cumplen
1e-7 se conservan como diagnósticos, sin convertirlos en evidencia estacionaria.
C0 es control; no permite promover los casos cuadráticos inconclusos.
No se certifican mínimos, sillas exactas, geodésicas ni convergencia.
