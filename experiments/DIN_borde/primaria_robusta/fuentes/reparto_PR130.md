# Reparto de trabajo tras el cierre de CIFAR-3 (2026-11-02)

**Contexto:**
- Se adoptó la [primaria robusta](../../experiments/DIN_borde/PRIMARIA_ROBUSTA_v1.md) para los diseños nuevos y se cerró CIFAR-3 ([cierre](../../experiments/DIN_borde/CIFAR/CIERRE_CIFAR3_2026-11-02.md)).
- El responsable pidió repartir el trabajo con el otro agente y añadir la posibilidad de usar Lean.
- Los dos caminos científicos abiertos son:
  - **(a)** la señal en otra familia, diseñada con la primaria robusta;
  - **(b)** la pregunta de Q13: si lo que modula la señal es la concentración de M o la escala de los logits.

| quién | tarea | entrega | depende de |
|---|---|---|---|
| **Otro agente** | **A1.** Analista genérico de la primaria robusta v1 (criterio de no aprendió, base recortada, compuerta de influencia, veredicto NO_ROBUSTO), con fixtures sintéticos obligatorios: una trayectoria que no aprende, una L con \|z\| > 10 y equivalencia exacta con C1 sin recorte (por SHA `8711f468…`). Borrador, pruebas y auditoría de Claude antes de congelar. | PR con el analista, las pruebas y su resultado | — |
| **Otro agente** | **A2.** Propuesta de 2 o 3 opciones para el siguiente experimento, cubriendo (a) y (b). Para cada una: pregunta, familia o manipulación, costo estimado en el equipo del responsable, riesgos y por qué la primaria robusta aplica. Sin datos nuevos. | Documento corto de opciones | — |
| **Claude** | **C1.** Piloto de Lean: proyecto `lean/` con Mathlib fijada y los teoremas L1, L2, L4 y L7 de la [propuesta](lean-formalizacion.md). Antes, comprobar que la instalación es factible. | PR con el proyecto y las pruebas que compilan | aprobación del responsable para instalar |
| **Claude** | **C2.** Auditar A1 y A2. | Revisión en la conversación | A1, A2 |
| **Claude** | **C3.** Implementar el productor del experimento elegido, como en CIFAR F1. | PR del productor | elección del responsable y diseño congelado |
| **Responsable** | Elegir la opción de A2, aprobar las congelaciones y ejecutar en su equipo. | Decisiones y corridas | A2 |

**Orden:** A1, A2 y C1 van en paralelo. Con la elección del responsable, el otro agente diseña, Claude audita, se congela, Claude implementa el productor y el responsable lo ejecuta.

