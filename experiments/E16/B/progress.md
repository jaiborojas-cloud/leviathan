# E16-B — Progreso

2026-10-19: checkout limpio de E16, rama nueva research/e16-b-instrumentacion.
Se leyó AGENTS.md y NEXT_PHASE.md. Se comprobó main remoto ce0b970 sin modificar
ni ejecutar el trabajo ajeno T2-A. PR #5 continúa sin fusionar automáticamente.

Inventario de pesos locales: ninguno en extensiones habituales .npz/.pt/.pth/
.safetensors/.pkl del repositorio y directorios compartidos. Los documentos
históricos no sustituyen un checkpoint independiente. PyTorch y JAX no están
instalados. Hay NumPy, SymPy y SciPy.

Se preparó formalización candidata y se pidió elección de artefacto. Pendiente:
resolver red existente frente a red mínima nueva sin entrenamiento; después
fijar pesos, paneles, perspectivas, métrica, tolerancias, presupuesto y criterios
antes del código experimental y de observar resultados. No modificar la fase A.

Se concretó DESIGN_CANDIDATE.md: red 2→2→1, tres estados explícitos nuevos,
tres paneles sintéticos, tres puntos y composiciones, cartas y criterios
numéricos propuestos. Sin cálculo de observables, sin código experimental y
sin afirmar congelación. La elección del artefacto sigue pendiente.

## Elección resuelta y congelación

El usuario autorizó explícitamente «Crear una red mínima nueva, sin entrenamiento,
con pesos y datos sintéticos fijados antes de medir». Se congela el candidato
como DESIGN_FROZEN.md v1 y config.json; autograd 1.8.0 disponible en entorno
local work/e16b-deps, sin instalar ni modificar código histórico. No hay
resultados científicos abiertos. Próximo: implementar ejecutor y controles.
