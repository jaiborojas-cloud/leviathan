# NEM1 — Estabilidad de la métrica de perspectivas frente al panel y modos débiles de Fisher

Línea independiente, analítica y computacional pequeña. No continúa ni confirma E15/T2/E16 y no ejecuta sus scripts.

Pregunta: ¿qué tan estable es la métrica de perspectivas $h = B C B^T$ cuando el panel de evaluación $\mu$ se perturba ligeramente o cuando se activan direcciones casi-degeneradas (modos débiles) de Fisher?

- [Diseño congelado](DESIGN_FROZEN.md)
- [Formalización y derivaciones](mathematical_spec.md)
- [Fuentes y decisiones](sources.md)
- [Avance y reanudación](progress.md)
- [Conclusiones y límites](CONCLUSION.md)
- Código en `scripts/`, resultados pequeños en `results/`, entorno en `requirements.txt`.
- `manifest.csv`: SHA-256 de los archivos propios, salvo el propio manifest.

Reproducción desde la raíz del repositorio (NumPy y SymPy; versiones en requirements.txt):

```sh
python -m pip install -r nemotron/experiments/NEM1/requirements.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python nemotron/experiments/NEM1/scripts/run.py --output nemotron/experiments/NEM1/results/run_v1
python nemotron/experiments/NEM1/scripts/verify.py
```

El ejecutor rechaza directorios con resultados existentes. No requiere datos externos. No se generarán figuras si las tablas pequeñas bastan.

Estado: EN_DISEÑO. Resultado: pendiente.

Límites: análisis exploratorio, no confirmatorio. No se adoptan como ley ni como evidencia de generalización. T2-A, E16 y resultados congelados permanecen intactos.
