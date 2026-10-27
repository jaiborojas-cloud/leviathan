# Verificación independiente DIN-Q13DR v2

Revisión245d735ffae59fa28e6458d1cb8a9bd21387d278. Analista SHA afb807aa…,
pruebas7e16fa29…. **Corregir casos residuales antes de congelar**; no se modifica
ningún original ni se sobrescribe la auditoría v1.

- [Dictamen](CONCLUSION.md) y [matriz de resolución](MATRIZ_HALLAZGOS.md).
- [Casos nuevos/residuales y correcciones propuestas](NUEVOS_DEFECTOS.md).
- [Repetición nominal](TASAS.md):1000 réplicas,5000 permutaciones/2000 bootstrap.
- [Protocolo previo](DESIGN_FROZEN.md), [configuración](config.json), [fuentes SHA](sources/provenance.json).
- [Verificación](verification.json), [manifiesto](manifest.csv), [arrays](external_manifest.csv).

Resultados nominales: MODULA2.0%,2.5% y37%; NO_MODULA secundaria0 en las tres
celdas. Las dos primeras son nulos; la tercera es alternativa β=.03. Los
contraejemplos de c constante y rango negativo siguen requiriendo corrección.

Reproducción con Python3.12/NumPy2.3.5/SciPy1.17.0, código comprometido y salidas
nuevas. Nunca sobrescribir versiones ni resultados anteriores:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python experiments/DIN_borde/Q13DR/auditoria/verificacion_v2/scripts/cases_v2.py
python experiments/DIN_borde/Q13DR/auditoria/verificacion_v2/scripts/checks_v2.py
python experiments/DIN_borde/Q13DR/auditoria/verificacion_v2/scripts/monte_carlo_v2_r2.py
```

El contraste por bytes requiere los arrays **sintéticos** archivados de #104 en
la ruta declarada por config.json. Si no están, se regeneran en un entorno separado
con el script/configuración originales de #104, sin datos reales. Las rutas de
manifiesto son locales, no enlaces de hosting. El intento r1 se conserva como
fallo de infraestructura; para la repetición válida usar r2, no r1.

La suite del autor no se ejecuta ni se abre su fixture C2. El motor estadístico
está contrastado con funciones v2; la guarda sólo permite snapshots/resultados y
los arrays sintéticos declarados. Ver [tasas](TASAS.md) para límites y denominadores.
