# E16-AB · región de confianza sobre el gradiente

AB estudia si un método distinto permite alcanzar KKT físico≤1e-7 desde las
doce curvas finales de [AA](../AA/README.md). Resuelve mínimos cuadrados del
gradiente AD con Jacobiano Hessiana, TRF, SVD densa y escalado por columnas.
La aceptación depende de una auditoría física MP separada del solver.

- [Diseño congelado](DESIGN_FROZEN.md), [configuración](config.json) y
  [formulación](THEORY.md).
- [Resultados y límites](CONCLUSION.md), [tablas](results/run_v1),
  [figura](figures/trust_region_comparison.svg) y [registro](progress.md).

**Resultado:** cinco de ocho cuadráticos y cuatro controles cumplen el criterio;
tres cuadráticos siguen INCONCLUSIVE. Reproducción exacta de once salidas
aprobada; [registro](verification.json).

No se subdivide de nuevo ni se recalcula la masa de Y/Z/AA. Los nombres132/264
identifican las fuentes S; las mallas actuales tienen264/528 segmentos.
reference/scaled son etiquetas de procedencia, no dos métodos AB.
No hay entrenamiento ni datos independientes.

## Parada y estados

Cada punto aceptado distinto recibe un monitor. Los descartes AD se conservan
sin llamarlos auditorías MP. Tres aceptados consecutivos verificados con
KKT≤1e-7 solicitan StopIteration; least_squares devuelve status−2/successFalse,
que se preservan separados de la aceptación del protocolo. Un éxito nativo
por xtol necesita validación física final. El límite de evaluaciones conserva
INCONCLUSIVE. C0 verificado inicialmente puede quedar INITIAL_CONTROL sin
llamar a SciPy y con campos nativos vacíos. No se inventa éxito nativo.

Si el solver aborta se conserva SOLVER_ERROR y el último punto aceptado,
sin seleccionar el mejor. No se exige disminuir L: el objetivo del solver es
el residuo del gradiente. Ver [teoría](THEORY.md) para esta distinción.

## Reproducción

Python3.12 y versiones de [requirements.txt](requirements.txt). Desde la raíz,
con dependencias instaladas:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/AB/scripts/run.py --out /tmp/e16-ab-nuevo
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/AB/scripts/verify.py
```

La primera orden escribe resultados nuevos fuera de los archivos versionados.
La segunda verifica congelación, hashes, alcance, rachas, KKT, elegibilidad,
espectros y costes, y ejecuta una sola repetición temporal de once salidas
científicas: nueve CSV más summary/provenance JSON. resources.json registra
recursos y queda excluido de igualdad exacta por sus tiempos variables.

Se archivan componentes de gradiente, vértices y diagnósticos escalares.
No se publican Hessianas, autovectores ni checkpoints. Una verificación de
integridad aprobada puede coexistir con resultado científico INCONCLUSIVE.

## Interpretación

El éxito numérico no certifica mínimo, silla exacta, geodésica o convergencia.
Una raíz puede ser mínimo, máximo o silla; una salida de mínimos cuadrados
puede incluso tener gradiente físico no nulo. Se conservan todos los estados,
y sólo se interpreta la comparación estacionaria en puntos elegibles.
