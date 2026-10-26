# Reproducción de la generación C2 v1

Sólo generación y publicación. **No ejecutar `analisis_C2.py` ni sus pruebas con C2.**

## Entorno y semillas

Python 3.12, NumPy/SciPy/PyTorch CPU y sklearn, como G3. Las versiones exactas se
registran en `cohorte/run_v1/environment.json`. Exportar para cada comando
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`.
Intérprete usado: `/workspace/.venvs/leviathan/bin/python`.

La potencia ya se comprometió: dd34a6b (código), 58558b8 (salidas), 0e167f4
(plan publicado). Para una reproducción desde cero usar un clon separado; no
sobrescribir salidas existentes. El método exige revisar los mismos SHA de fuentes.
El piloto es sólo la CSV G3 s=.8. No se debe leer como datos nuevos ni reentrenar G3.

Código inicial de cohorte: df248d5. Antes de cualquier entrenamiento:

```bash
python experiments/DIN_borde/C2/cohorte_scripts/reproduce_v1.py
```

La compuerta original está comprometida en 24c8a39: tres reconstrucciones M de
modelos sin entrenar, error 0 y f idéntica. Este commit es la referencia previa al
entrenamiento. La reproducción exige que la compuerta esté comprometida antes de
invocar cohort; en un clon nuevo se puede restaurar la compuerta archivada y sus
arrays verificados, o preservar una nueva versión sin sobrescribir la original.
No sustituir IDs, semillas, visitas ni estados fallidos.

Después de una compuerta válida y comprometida:

```bash
python experiments/DIN_borde/C2/cohorte_scripts/run_v1.py --part prepare
python experiments/DIN_borde/C2/cohorte_scripts/run_v1.py --part cohort
python experiments/DIN_borde/C2/cohorte_scripts/archive_v1.py --part pack
python experiments/DIN_borde/C2/cohorte_scripts/archive_v1.py --part unpack
# Comprometer el archivo completo de cohorte antes del paso de publicación.
python experiments/DIN_borde/C2/cohorte_scripts/publish_v1.py
python experiments/DIN_borde/C2/cohorte_scripts/verify_v1.py
```

Todos los scripts escriben en modo exclusivo. La repetición de una ejecución
requiere una versión nueva explícita y preservar la original. No volver a medir
para reemplazar fallos. `publish` copia datos y cuenta; no calcula asociaciones.
`verify` valida SHA, copia exacta, universo y cronología; no ejecuta análisis.

## Archivo

Los JSON crudos por estado se conservan localmente en `cohorte/run_v1/states/`
(ignorados por Git) y se publican como JSONL reversibles en
`cohorte/run_v1/state_records/`, con SHA/bytes por registro en
`state_records_manifest.csv`. La restauración comprueba cada byte y no sobrescribe.
Los JSON individuales de trayectorias se publican sin transformación.

Arrays de datos sintéticos, pesos/Adam/RNG, M/f/logits y diagnósticos completos de
rho: `/workspace/work/din-c2-cohorte-v1-arrays/`. Tres arrays de la compuerta:
`/workspace/work/din-c2-compuerta-v1-arrays/`. Cuatro arrays de potencia:
`/workspace/work/din-c2-power-v1-arrays/`. Se conservan fuera de Git con manifiesto
SHA/tamaño; las rutas son locales, no un alojamiento externo descargable.

`script_sha256` de RESUMEN_c2 identifica el generador; `publicador_sha256` identifica
la escritura de la tabla. El manifiesto original identifica el analista congelado,
que este agente no ejecuta. El responsable conserva la decisión de cierre.
