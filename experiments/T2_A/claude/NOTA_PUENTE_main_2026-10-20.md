# Nota puente: estado real de T2-A frente a main (2026-10-20)

Esta nota solo vive en `experiments/T2_A/claude/`. No modifica `docs/`, `codex/` ni el archivo importado. No altera protocolos, tolerancias ni umbrales congelados.

## Por qué existe
`docs/research-status.md`, `docs/roadmap.md` y `experiments/T2_A/README.md` conservan el corte del 2026-10-17 ("1 visita cerrada", j5 retenido, j7 pausado en el paso 128, r=0.07455). Ese corte no refleja el piloto de 20 visitas ni el diagnóstico de escape de rayos.

## Estado real (línea claude)
- Piloto de 20 visitas (update 25): 17 con diagnóstico geométrico, 15 `INJECTIVE_AT_NOMINAL_RADIUS` y 2 `GEOMETRIC_NONINJECTIVITY` (split10_j17, split8_j9).
- 3 en `PAUSED_PENDING_REVIEW`: split8_j5, j7, j8. Compuerta no activada (3/20; 3/5 en split 8). No se asignó ningún Y.
- Diagnóstico de escape: los rayos de la exponencial salen de la carta (|p|→∞, |v|→∞) a distancia intrínseca finita, con comportamiento tipo p≈−C·ln(t*−t) y |v|≈C/(t*−t). Se reproduce en MPFR 169 bits. Detalle en `piloto/diagnostico_escape/RESULTADO_escape_rayos_2026-10-20.md`.
- Anexo operativo E1 v1.1 en BORRADOR 3 (T1–T5, D1–D5). No congelado ni vigente.

## Corroboración independiente (documentos originales importados)
- Cierre original de j5: ya registraba una "frontera de dominio" con mínimo local en r≈0.07447421 (rayos 1775/1776) y área diagnóstica ≈0.01871467 < 0.02.
- Pausa original de j7 en r=0.0745543, a 1.1e-4 del t*≈0.074662 estimado aquí.
Son líneas independientes que describen el mismo fenómeno. No constituyen certificación de T5.

## Alineación con reglas de main
- `AGENTS.md` y prerregistro §5: NUMERICAL_FAILURE e INCONCLUSIVE no son ceros; no se reemplazan ni excluyen estados fallidos retrospectivamente.
- T5 (`NOMINAL_DISK_NOT_CONSTRUCTIBLE_RAY_ESCAPE`) es solo diagnóstico adicional. Las disposiciones originales se conservan hasta E2 (D3).
- Reevaluación de j8 con T4′ (D4): solo después de congelar y validar T4′, conservando el intento original y todas las auditorías. No es un reemplazo.
- j5 y j7 siguen `PAUSED_PENDING_REVIEW`. Certificar T5 exige una cota superior verificable del área en el escape y un argumento que separe la salida del dominio original de una singularidad removible de la carta. Hoy no se cumple.

## Pendiente
Validaciones de la visita con T4′ en el equipo responsable (j6 forzado, j6 cap 22, j17 forzado), congelación de v1.1, E2 con revisión estadística externa.

## E16
E16 (B–H) es una línea independiente sin relación con T2-A. No se usa aquí.
