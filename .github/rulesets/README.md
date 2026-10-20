# Protección propuesta de main

`main-protection.json` es una regla importable de GitHub Rulesets para exigir
pull requests antes de integrar en `main`, bloquear borrado y force-push, y
requerir resolver conversaciones de revisión. No incluye excepciones de bypass.

**Guardar o fusionar este archivo no activa la protección en GitHub.** La
conexión usada para preparar esta entrega devuelve `403: Resource not accessible
by integration` al consultar protección de ramas; tampoco ofrece una operación
de administración para aplicarla. No se afirma que main esté protegida.

## Aplicación por un administrador

1. Abrir Settings → Rules → Rulesets del repositorio.
2. Revisar las reglas existentes para evitar duplicar una regla equivalente.
3. Usar New ruleset → Import a ruleset e importar `main-protection.json`.
4. Comprobar objetivo `main`, estado Active y ausencia de bypass; guardar.
5. Verificar que los cambios requieren PR y que borrado/force-push estén bloqueados.

La regla exige PR, con cero aprobaciones externas obligatorias: permite trabajar
sin depender de otro revisor y no permite integrar mediante push directo. Si se
requiere revisión independiente, elevar `required_approving_review_count` a 1
y disponer de un revisor distinto del autor. No se exigen checks de CI cuyos
nombres o disponibilidad no se hayan verificado. Las otras reglas del repositorio
siguen aplicándose; esta propuesta no pretende reemplazarlas ni debilitarlas.
