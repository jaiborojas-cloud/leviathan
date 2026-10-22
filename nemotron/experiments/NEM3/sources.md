# NEM3 — Fuentes y decisiones

## Fuentes documentales

- `docs/theory/04-observables-y-atribucion.md` — energía curvatural, concentración espacial, participación efectiva.
- `docs/theory/03-geometria-diferencial.md` — conexión de Levi-Civita, curvatura de Gauss.
- `docs/theory/01-fundamentos.md` — espacios, funcional, relevancia, Fisher, familia no lineal de E12.
- `docs/theory/02-metrica-y-covariancia.md` — métrica inducida $h = B C B^T$.
- `docs/research-notes/open-questions.md` — marco general de preguntas abiertas del RIPG.
- `nemotron/marco_teorico.md` — síntesis de lectura de Nemotron.
- `nemotron/experiments/NEM1/` y `nemotron/experiments/NEM2/` — precedentes metodológicos (Python puro, reproducible).

## Decisiones tomadas

1. **Enfoque**: observables geométricos $C_A$, $\Lambda_q$, $R_{\text{eff}}$ sobre el espacio de perspectivas.
2. **Familia no lineal**: softmax de rasgos fijos (forma E12), adaptada sin ejecutar E12.
3. **Independencia**: no se reutilizan scripts, datos ni resultados de NEM1, NEM2, E16, E15, T1 o T2-A.
4. **Sin entrenamiento**: modelo lineal pequeño, pesos fijos aleatorios.
5. **Python puro**: biblioteca estándar, sin dependencias externas.
6. **Comparación panel base vs perturbado**: $\epsilon = 0.2$.
7. **Solo escritura en `nemotron/`**: lectura del resto del repositorio sin modificar.

## Decisiones pendientes

- Ninguna pendiente; diseño congelado en DESIGN_FROZEN.md.
