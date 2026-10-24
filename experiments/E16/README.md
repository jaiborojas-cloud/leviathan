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

## Etapas AC–AF

- [E16-AC — Índice de Morse por campos de Jacobi](AC/README.md):
  INCONCLUSIVE; 12 índices continuos 0, sin los bloques discretos de Z/AB.
  [Conclusión oficial](AC/CONCLUSION.md).
- [E16-AD — Bloques discretos y carta normal](AD/README.md):
  INCONCLUSIVE; suma/producto/cuadrática planas, bloques normales positivos;
  tres LIBRE cuadráticos no cumplen la ruta de estacionariedad.
  [Conclusión oficial](AD/CONCLUSION.md).
- [E16-AE — Familia no plana tipo E12](AE/README.md):
  Q1/Q2/Q3 INCONCLUSIVE; curvatura mayormente negativa, todo censurado.
  [Conclusión oficial](AE/CONCLUSION.md).
- [E16-AF — Réplica sintética de la familia geométrica T2](AF/README.md):
  Q1 PASS, Q2 INCONCLUSIVE, Q3 PASS exploratorio, Q4 FAIL; cinco eventos y
  35/40 censurados, sin escapes en la rejilla.
  [Conclusión oficial](AF/CONCLUSION.md).

[Síntesis S–AD](SINTESIS_S_AD.md) · [Síntesis AC–AF y preguntas abiertas](SINTESIS_AC_AF.md).
