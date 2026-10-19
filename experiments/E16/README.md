# E16 — Composicionalidad y coarse-graining perspectival

Línea independiente, analítica y computacional pequeña. No continúa ni confirma
E15/T2 y no ejecuta sus scripts. Pregunta: ¿qué estructura se conserva, transforma
o pierde al combinar perspectivas?

- [Diseño congelado](DESIGN_FROZEN.md)
- [Convenciones, derivaciones y ejemplos](mathematical_spec.md)
- [Fuentes y decisiones](sources.md)
- [Avance y reanudación](progress.md)
- [Conclusiones](CONCLUSION.md)
- Código en `scripts/`, tablas en `results/`, entorno en `environment.json`.
- `manifest.csv`: SHA-256 de los archivos propios, salvo el propio manifest.

Reproducción desde la raíz del repositorio (NumPy y SymPy; versiones de la
corrida en environment.json):

```sh
python -m pip install -r experiments/E16/requirements.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/scripts/run_controls.py --output experiments/E16/results/replica
python experiments/E16/scripts/verify.py
```

El ejecutor rechaza directorios con resultados existentes. La tabla científica
se compara con `results/run_v3/checks.csv` y `spectra.csv`; tiempos y plataforma
se registran aparte. No requiere datos externos. No se generarán figuras si las
tablas pequeñas bastan.

Resultado: EXPECTED_GEOMETRIC_CONTROL, 122/122 PASS en v3; fallos v1/v2 conservados.
[Fe de erratas](ERRATA_v2.md) · [Fase posterior candidata](NEXT_PHASE.md).
