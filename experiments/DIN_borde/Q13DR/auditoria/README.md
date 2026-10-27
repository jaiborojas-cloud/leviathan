# Auditoría independiente de DIN-Q13-DR, antes de congelar

**Corregir antes de congelar.** Sólo se reporta: ningún cambio al diseño, analista,
pruebas originales ni instrumentos. Revisión vigente78a7d2e, analista SHA c9159325…,
idéntico al snapshot iniciale7dfc435. Todo se generó sintéticamente; sin Wine,
C2/Q13 reales, redes, entrenamiento ni geometría.

- [Conclusión](CONCLUSION.md): defectos y decisiones necesarias.
- [Casos mínimos, líneas y correcciones propuestas](DEFECTOS.md).
- [Tasas nominales](TASAS.md):1.400 réplicas,5.000 permutaciones/2.000 bootstrap.
- [Diseño de auditoría congelado antes del código](DESIGN_FROZEN.md) y [config](config.json).
- [Fuentes por SHA](sources/provenance.json), [revisión posterior](REVISION_OBJETIVO.md).
- [Verificación](verification.json), [manifiesto](manifest.csv), [arrays externos](external_manifest.csv).

Falsos MODULA en los nulos D=.02:2.0% (N200),2.5% (N400); no inflación sobre5%
observada en estos modelos. Potencia NO_MODULA:0/400 por tamaño. No extrapolar
esa tasa a otras dependencias, datos o patrones de faltantes.

Reproducción con Python3.12, NumPy2.3.5 y SciPy1.17.0, en un clon/entorno limpio
con directorios de salida nuevos, nunca sobrescribir resultados existentes:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python experiments/DIN_borde/Q13DR/auditoria/scripts/cases_v1.py
python experiments/DIN_borde/Q13DR/auditoria/scripts/cases_v2.py
python experiments/DIN_borde/Q13DR/auditoria/scripts/cases_scale_v1.py
python experiments/DIN_borde/Q13DR/auditoria/scripts/monte_carlo_v1.py
```

Los scripts exigen código/configuración comprometidos y snapshots íntegros. La
suite original no se ejecuta porque abre un fixture bajo C2. El motor nominal
independiente se contrasta con las funciones auditadas antes de usarlo; sus arrays
están fuera de Git y conservan cada réplica, sin descartes ni redibujos.
