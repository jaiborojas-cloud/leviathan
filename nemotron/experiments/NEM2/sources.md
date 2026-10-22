# NEM2 — Fuentes y decisiones

## Fuentes documentales

- `docs/theory/03-geometria-diferencial.md` — conexión de Levi-Civita, curvatura, geodésicas, Jacobi, holonomía.
- `docs/theory/01-fundamentos.md` — espacios, funcional, relevancia, Fisher, axioma de admisibilidad, familia no lineal de E12.
- `docs/theory/02-metrica-y-covariancia.md` — métrica inducida $h = B C B^T$.
- `docs/research-notes/open-questions.md` — marco general de preguntas abiertas del RIPG.
- `nemotron/marco_teorico.md` — síntesis de lectura de Nemotron.
- `nemotron/experiments/NEM1/` — precedente metodológico (Python puro, reproducible).

## Decisiones tomadas

1. **Enfoque**: curvatura de Gauss $K$ y holonomía en el espacio de perspectivas (2D).
2. **Familia no lineal**: softmax de rasgos fijos (forma de E12), adaptada sin ejecutar E12.
3. **Independencia**: no se reutilizan scripts, datos ni resultados de NEM1, E16, E15, T1 o T2-A.
4. **Sin entrenamiento**: modelo lineal pequeño, pesos fijos aleatorios.
5. **Python puro**: biblioteca estándar, sin dependencias externas.
6. **Solo escritura en `nemotron/`**: lectura del resto del repositorio sin modificar.

## Decisiones pendientes

- Ninguna pendiente; diseño congelado en DESIGN_FROZEN.md.
