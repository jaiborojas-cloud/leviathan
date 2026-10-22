# NEM1 — Fuentes y decisiones

## Fuentes documentales

- `docs/theory/01-fundamentos.md` — espacios, funcional, relevancia, Fisher, axioma de admisibilidad.
- `docs/theory/02-metrica-y-covariancia.md` — métrica inducida $h = B C B^T$, caso ideal y degenerado.
- `docs/theory/03-geometria-diferencial.md` — conexión de Levi-Civita, curvatura, geodésicas, Jacobi.
- `docs/theory/04-observables-y-atribucion.md` — distancia SPD, energía curvatural $C_A$, concentración espacial.
- `docs/research-notes/open-questions.md` — Q03: estabilidad de la geometría frente al panel y modos débiles.
- `nemotron/marco_teorico.md` — síntesis de lectura de Nemotron.
- `nemotron/preguntas_abiertas.md` — mapeo de Q01–Q09 desde Nemotron.

## Decisiones tomadas

1. **Enfoque en Q03**: estabilidad de la métrica $h$ frente a perturbaciones del panel y modos débiles de Fisher.
2. **Independencia**: no se reutilizan scripts, datos ni resultados de E16, E15, T1 o T2-A.
3. **Sin entrenamiento**: red sintética pequeña, sin ajustar pesos.
4. **Exploratorio**: resultados no se adoptan como ley ni como evidencia confirmatoria.
5. **Solo escritura en `nemotron/`**: lectura del resto del repositorio sin modificar.

## Decisiones pendientes

- Umbral exacto de "modo débil" $\tau$ (declarado en `mathematical_spec.md` antes de ejecutar).
- Familia concreta de perspectivas $\{p_a\}$ y observables $o_\ell$.
- Forma de la perturbación $\delta\mu$.
