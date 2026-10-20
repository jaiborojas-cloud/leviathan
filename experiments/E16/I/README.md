# E16-I — Caminos quebrados acotados

**PASS_NUMERICAL instrumental:** 27 casos validados y 5533 controles pasan.
Se encuentran caminos más cortos en 18/18 casos no lineales; los nueve controles
con suma conservan el camino recto. **No se ha probado un mínimo global ni una
geodésica suave.** Un caso alcanza el límite del desplazamiento permitido.

- [Diseño congelado](DESIGN_FROZEN.md), commit `acab94e`.
- [Conclusión y límites](CONCLUSION.md).
- [Casos y ganancias](results/run_v1/cases.csv), [resumen](results/run_v1/summary.json).
- [Validación de tramos](results/run_v1/segments.csv), [controles](results/run_v1/checks.csv).
- [Dos resoluciones de búsqueda](results/run_v1/optimizers.csv),
  [todas las evaluaciones](results/run_v1/search_trace.csv).
- [Procedencia](results/run_v1/provenance.json), [recursos](results/run_v1/resources.json),
  [registro](progress.md), [manifest](manifest.csv).

Se usan los primeros tres estados H, P0 y sus tres pares de extremos, sin
entrenamiento. El camino tiene un punto intermedio desplazable normalmente a
la cuerda hasta un cuarto de su longitud. La búsqueda usa float64; las longitudes
y positividad de los caminos elegidos se validan después con el instrumento G
sin modificarlo. La familia está fijada en la carta original y se transporta
completa para los controles de coordenadas.

## Reproducción

Python 3.12 y [dependencias fijadas](requirements.txt). Desde la raíz:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/I/scripts/verify.py
```

Comprueba hashes, protocolo previo, fuentes y alcance; repite en un directorio
temporal y compara siete salidas científicas byte a byte. El tiempo se verifica
contra el presupuesto, no byte a byte. Se requiere historial Git del diseño.
La reproducción exacta se comprobó en el entorno y versiones declarados; la
búsqueda float64 no garantiza idénticos parámetros entre plataformas distintas.

Para una corrida separada, sin sobrescribir evidencia:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/I/scripts/run.py --out /tmp/e16-i-nueva-corrida
```

No se ejecutan corridas anteriores: se importan únicamente sus funciones, con
hashes fijados y sin escribir en sus directorios. T2-A y evidencia A–H intactos.
