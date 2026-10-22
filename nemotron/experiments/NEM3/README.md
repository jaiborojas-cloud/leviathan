# NEM3 — Observables geométricos: energía curvatural y concentración espacial

Línea independiente, analítica y computacional pequeña. No continúa ni confirma E15/T2/E16/NEM1/NEM2 y no ejecuta sus scripts.

Pregunta: ¿cómo se distribuye la energía curvatural $C_A = \sqrt{\mathcal E_K}$, la concentración espacial $\Lambda_q$ y la participación efectiva $R_{\text{eff}}$ sobre el espacio de perspectivas, y cómo varían ante perturbaciones del panel de evaluación?

- [Diseño congelado](DESIGN_FROZEN.md)
- [Formalización y derivaciones](mathematical_spec.md)
- [Fuentes y decisiones](sources.md)
- [Avance y reanudación](progress.md)
- [Conclusiones y límites](CONCLUSION.md)
- Código en `scripts/`, resultados pequeños en `results/`, entorno en `requirements.txt`.
- `manifest.csv`: SHA-256 de los archivos propios, salvo el propio manifest.

Reproducción desde la raíz del repositorio (Python puro, biblioteca estándar):

```sh
python3 nemotron/experiments/NEM3/scripts/run.py --output nemotron/experiments/NEM3/results/run_v1
python3 nemotron/experiments/NEM3/scripts/verify.py --output nemotron/experiments/NEM3/results/run_v1
```

El ejecutor rechaza directorios con resultados existentes. No requiere datos externos ni dependencias externas.

Estado: EN_DISEÑO. Resultado: pendiente.

Límites: análisis exploratorio, no confirmatorio. T2-A, E16, NEM1, NEM2 y resultados congelados permanecen intactos.
