# E16-C — Control de mayor precisión del rango

Nuevo protocolo instrumental; conserva el INCONCLUSIVE de E16-B y no usa datos
nuevos para confirmar hipótesis de aprendizaje.

- [Diseño congelado](DESIGN_FROZEN.md)
- [Derivaciones y límites de las cotas](mathematical_spec.md)
- [Configuración fija](config.json), [procedencia](sources.json)
- [Progreso](progress.md)

Tres métodos: autodiff, referencia analítica 80/120 dígitos y FD de cuarto orden.
Error transportado por la cométrica antes de clasificar el rango. Sin entrenamiento.
Estado inicial: diseño previo a implementación; ningún resultado nuevo abierto.
