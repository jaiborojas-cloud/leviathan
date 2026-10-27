# Verificación independiente v3 — diseño congelado

2026-10-26 (America/Mexico_City). Exploratoria, únicamente sintética. Referencia: PR #106, commit `a8da9046cf0b5e4ba64ef24e03999591f899c4e2`. El diseño científico aplicable sigue siendo el borrador v2; no se modifica ni se congela aquí.

## Alcance y secuencia

Este commit precede a código de verificación y a mediciones. Solo se añaden archivos en esta carpeta. Se conservan intactas las auditorías anteriores. Snapshots por Git, SHA completos en [provenance](sources/provenance.json), sin abrir datos reales ni ejecutar la suite del autor, que lee un fixture bajo C2.

1. Reejecutar los 51 casos de la verificación v2 con su generador sintético y semillas originales, contra el analista v3. Parámetros B39/NB16/B2=19/BQ=19 para aislar lógica; la CLI usa los nominales del analista. El caso N05 usa NB300. Nombres históricos se conservan aunque el resultado esperado cambie.
2. N01: las siete constantes decimales deben rechazarse; el caso N200 de punto constante debe dar INCONCLUSIVE. Añadir un punto identificable con réplicas de c constante, comprobando su rechazo y ausencia de redibujos. N02: rango positivo max−min y diferencia L0−L5 separada. N03/N04: ABORTA solo con código3, prefijo ABORTA y sin traceback. N05: igualdad de todos los índices y errores guardados con la traza independiente.
3. Matriz completa F01–F06 y decisiones: población común, emparejamiento, bloque original, recálculo D/c/beta, degeneraciones, plan, Spearman, márgenes, exactitud binaria, precisión, comunes, dominio y JSON estricto. Repetir también las 27 comprobaciones de dominio y cuatro de Spearman de v2.
4. Buscar regresiones solo en los diffs de pendiente, rango_c, validar_plan y main: planes JSON inválidos y extremos (tipos, finitud, dosis, N); archivos ausentes/directorios, UTF-8 y JSON malformados y error CSV; slopes finitas/no finitas y rango no ordenado. Separar contratos internos no alcanzables desde las seis medianas físicas de defectos reproducibles por CLI. No ampliar a datos reales ni defectos ajenos al diff.
5. Compatibilidad: comparar v2/v3 en diez tablas sintéticas no degeneradas, seeds910400..910409, N20, con los parámetros reducidos anteriores; comparar exactamente D, p, pendientes, c, beta, IC, veredictos y secundarios, normalizando solo campos nuevos de diagnóstico (fallos y diferencia L0−L5). Comprobar mediante AST que el cuerpo del estimando y los referidos C1/Q13 no cambian fuera de las protecciones descritas. Registrar cada discrepancia sin sustituir tablas.

## Reglas previas

RESUELTO por hallazgo si los casos reproducibles ya devuelven el contrato esperado y las verificaciones independientes concuerdan. PARCIAL o NO_RESUELTO si permanece un contraejemplo. Cualquier crash se conserva, distinguiendo un Aborta intencional del defecto. No aprobar ausencia universal de bugs ni afirmar validación estadística nueva.

No repetir Monte Carlo si las comparaciones exactas no muestran cambio en casos no degenerados y los diffs solo añaden validación/diagnósticos. Si se altera ese estimando, detener esa parte y documentar una enmienda antes de ejecutar simulaciones adicionales. No se recalculan tasas con los pocos casos de regresión.

JSON, logs, entorno, tiempos y manifests se conservan; fixtures CSV temporales fuera de Git se inventarían por SHA. Escrituras nuevas exclusivas y resultados de versiones previas de solo lectura. Si hay un defecto del verificador: preservar salida y enmienda comprometida antes de corregir.
