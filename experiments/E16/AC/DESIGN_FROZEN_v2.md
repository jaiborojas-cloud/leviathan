# Enmienda v2 congelada antes del código v2

Se conserva íntegro [diseño v1](DESIGN_FROZEN.md), salvo resolución del
contraste RK4 MP de controles sintéticos:2048 pasos en lugar de512.
No cambiar tolerancias, fuente científica, mallas científicas256/512 ni reglas
H1/H2. Defecto y corrida inválida: [registro v1](progress_v1.md).
Añadir instrumentación: error MP explícito de controles, tabla de shooting
con estados nativos, Hausdorff dirigido y deriva de velocidad en paths,
y tabla de eventos con cabecera aunque esté vacía.
Esta nueva versión no sobrescribe código, diseño ni resultados v1.
