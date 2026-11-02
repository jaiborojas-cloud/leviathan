# Progreso A1/A2 · 2026-11-02

Leídos AGENTS.md, adopción robusta, revisión metodológica y cierre CIFAR-3, C1 como código por SHA y reparto de PR #130 (pendiente al iniciar). Solo documentos publicados para A2; ninguna tabla real ni checkpoint se abrió. Base main `5eff9b5e`.

`c3573a13`: contrato y pruebas prospectivas antes de código. `3be81cb1`: analista y pruebas v1 antes de su ejecución. Corrida v1: 56/57, conservada. El fallo era una expectativa indebida del fixture de degeneración, no una corrección del analista. `c4be8b9b`: enmienda anterior a cambios. `6d153497`: pruebas v1.1 con rutas nuevas, antes de ejecutarse; 58/58 PASS. Los 56 casos comunes conservaron resultados idénticos. Analista SHA 1e2d903b sin cambios en ambas corridas.

A2 ofrece dos opciones sin datos nuevos: piloto para separar concentración y escala de logits en gaussianas, o una nueva familia Digits-3. Costes orientativos extrapolados del PC, no benchmarks ni promesa de potencia. El responsable elige y congela; Claude audita y luego implementa el productor. No se toca el piloto Lean.

Se entregan ambas versiones de pruebas, fallo, logs, fuentes, hashes y manifest en un PR de borrador. No se cambia la especificación adoptada, ningún estado previo ni instrumento; no se congela esta implementación, no se ejecuta una cohorte y no se fija un N confirmatorio.
