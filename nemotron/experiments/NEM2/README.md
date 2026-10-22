# NEM2 — Curvatura y holonomía en el espacio de perspectivas

Línea independiente, analítica y computacional pequeña. No continúa ni confirma E15/T2/E16/NEM1 y no ejecuta sus scripts.

Pregunta: ¿cómo se distribuye la curvatura escalar $K$ en el espacio de perspectivas para una familia de observables no lineal, y es la holonomía de lazos pequeños coherente con $\int K\, dA$?

- [Diseño congelado](DESIGN_FROZEN.md)
- [Formalización y derivaciones](mathematical_spec.md)
- [Fuentes y decisiones](sources.md)
- [Avance y reanudación](progress.md)
- [Conclusiones y límites](CONCLUSION.md)
- Código en `scripts/`, resultados pequeños en `results/`, entorno en `requirements.txt`.
- `manifest.csv`: SHA-256 de los archivos propios, salvo el propio manifest.

Reproducción desde la raíz del repositorio (Python puro, biblioteca estándar):

```sh
python3 nemotron/experiments/NEM2/scripts/run.py --output nemotron/experiments/NEM2/results/run_v1
python3 nemotron/experiments/NEM2/scripts/verify.py --output nemotron/experiments/NEM2/results/run_v1
```

El ejecutor rechaza directorios con resultados existentes. No requiere datos externos ni dependencias externas.

Estado: EN_DISEÑO. Resultado: pendiente.

Límites: análisis exploratorio, no confirmatorio. T2-A, E16, NEM1 y resultados congelados permanecen intactos.
