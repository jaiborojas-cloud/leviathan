# Verificación independiente de DIN-Q13-DR v3

Referencia exacta: PR #106, commit `a8da9046cf0b5e4ba64ef24e03999591f899c4e2`. Analista SHA `cc5524a781b16ac08ef25b86427f8f36bb43c6425d8cf17753c4ae5a9b534b6a`; pruebas SHA `03acf7e7729fdd9c0c0f95a73133e8c313bf74ada06be8ad328c244df93815b8`.

**Resultado: los casos N01–N05 quedan resueltos; la matriz F01–F06 no muestra regresiones.** No se observan defectos nuevos en los cambios examinados. La aprobación para congelar corresponde al responsable.

- [Conclusión y límites](CONCLUSION.md).
- [Resolución N01–N05](MATRIZ_N01_N05.md).
- [Regresión completa F01–F06 y decisiones](MATRIZ_F01_F06.md).
- [Revisión limitada a los diffs](REVISION_DIFFS.md).
- [Diseño de verificación, congelado antes del código](DESIGN_FROZEN.md).
- [Integridad y aserciones](verification_r2.json), [manifest](manifest_v2.csv), [SHA](manifest_v2.sha256).

## Reproducción

Python3.12.14, NumPy2.3.5 y SciPy1.17.0. Desde la raíz del repositorio, con `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`:

```bash
python experiments/DIN_borde/Q13DR/auditoria/verificacion_v3/scripts/cases_v3.py
python experiments/DIN_borde/Q13DR/auditoria/verificacion_v3/scripts/checks_v3.py
python experiments/DIN_borde/Q13DR/auditoria/verificacion_v3/scripts/diffs_v3.py
```

Estos comandos usan exclusivamente los snapshots y generadores sintéticos archivados. Las escrituras son exclusivas: con los resultados ya presentes se detienen; para una repetición se debe conservar la carpeta original y registrar otra versión con rutas nuevas antes de ejecutar. No se borra esta salida para repetir.

Los CSV de entrada CLI y sus salidas completas se inventarían fuera de Git en [external_manifest.csv](external_manifest_r2.csv); los casos, stderr y resultados relevantes se publican aquí en JSON. No se ejecutó la suite del autor ni se leyó su fixture bajo C2. No hubo Monte Carlo nuevo. [Entorno](environment.json).

El inventario vigente es r2. Se corrigió la inclusión de dos cachés locales ignoradas por Git; el [registro anterior y motivo](ENMIENDA_INVENTARIO_r2_CONGELADA.md) se conserva. Las mediciones científicas no se repitieron ni modificaron. `verification.json` y los manifiestos sin sufijo quedan como históricos del commit51ada0ad.
