# E16-J — Refinamiento y estacionariedad discreta

**INCONCLUSIVE global:** 24/27 casos cumplen los criterios y tres no.
De 81 resoluciones, 78 pasan y tres quedan inconclusas. Hay 22 casos interiores
estables discretamente (nueve son controles de suma), dos limitados por frontera
y tres no resueltos. No se afirman geodésicas continuas ni mínimos globales.

- [Diseño congelado](DESIGN_FROZEN.md), commit `c2cd4a8`.
- [Conclusión y causas de los inconclusos](CONCLUSION.md).
- [Casos y refinamiento](results/run_v1/cases.csv), [resumen](results/run_v1/summary.json).
- [Longitudes y residuales por resolución](results/run_v1/resolutions.csv).
- [Todas las búsquedas](results/run_v1/searches.csv),
  [parámetros finales de todos los candidatos](results/run_v1/vertices.csv).
- [Tramos y positividad](results/run_v1/segments.csv), [controles](results/run_v1/checks.csv).
- [Procedencia](results/run_v1/provenance.json), [recursos](results/run_v1/resources.json),
  [registro](progress.md), [manifest](manifest.csv).

Se conservan los 27 casos de I y el mismo corredor, con 2,4,8 puntos interiores
y tres inicializaciones fijas por resolución. El objetivo de búsqueda usa
cuadratura 32 y gradiente autograd; su gradiente se contrasta con orden 64 y
diferencias finitas. Las longitudes elegidas se validan con el instrumento G
a 80/120 cifras, sin modificarlo. Todos los tramos evaluados pasaron SPD numérica.

Los fallos de gradiente, reinicios y refinamiento no se ocultan tras longitudes
más cortas. Las mallas no son anidadas; el acuerdo finito no es una prueba de
convergencia al continuo. Se reutiliza H sin entrenamiento: estudio exploratorio.

## Reproducción

Python 3.12 y [dependencias fijadas](requirements.txt). Desde la raíz:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/J/scripts/verify.py
```

Comprueba hashes, protocolo previo y alcance; repite en un directorio temporal
y compara ocho salidas científicas byte a byte. Tiempo y memoria se verifican
contra el presupuesto. Se necesita historial Git de la congelación.
**PASS_REPRODUCTION reproduce también los inconclusos; no cambia su estado.**
La igualdad exacta se comprobó en el entorno declarado, sin garantía entre
plataformas distintas para la optimización float64.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/J/scripts/run.py --out /tmp/e16-j-nueva-corrida
```

No sobrescribir evidencia existente. El proceso puede finalizar normalmente
con INCONCLUSIVE: leer summary.json. Ante tiempo agotado conserva tablas parciales.
La advertencia SciPy sobre la clave redundante `method` en `options` queda
registrada en el [registro](progress.md); el método se fija explícitamente como
L-BFGS-B en la llamada. No se ejecutan experimentos anteriores ni se modifica T2-A.
