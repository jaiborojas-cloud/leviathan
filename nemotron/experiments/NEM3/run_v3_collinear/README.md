# NEM3 — run_v3_collinear: Observables geométricos con dataset sintético colineal

Extensión de NEM3 run_v1 con dataset sintético que induce colinearidad entre características, para probar el régimen de modos débiles de Fisher (autovalores cercanos a cero).

No continúa ni confirma otros experimentos. No ejecuta sus scripts.

- [Diseño congelado](DESIGN_FROZEN.md)
- [Formalización](mathematical_spec.md)
- [Fuentes y decisiones](sources.md)
- [Avance y reanudación](progress.md)
- [Conclusiones y límites](CONCLUSION.md)
- Código en `scripts/`, resultados en `results/`, entorno en `requirements.txt`.
- `manifest.csv`: SHA-256 de archivos propios, salvo el propio manifest.

Reproducción desde la raíz del repositorio (Python puro):

```sh
python3 nemotron/experiments/NEM3/run_v3_collinear/scripts/run.py --output nemotron/experiments/NEM3/run_v3_collinear/results/run_v1
python3 nemotron/experiments/NEM3/run_v3_collinear/scripts/verify.py --output nemotron/experiments/NEM3/run_v3_collinear/results/run_v1
```

Estado: EN_DISEÑO.
