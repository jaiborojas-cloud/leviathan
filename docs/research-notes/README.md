# Evidencia, decisiones y continuidad de RIPG

Esta carpeta conecta la [teoría](../theory/README.md) con las fuentes y decisiones
que permiten interpretarla. Es una síntesis documental: no ejecuta experimentos,
no añade evidencia confirmatoria ni modifica estados científicos.

| Necesidad | Documento |
|---|---|
| ¿Qué afirmación está respaldada y bajo qué condiciones? | [Mapa de afirmaciones y evidencia](claims-and-evidence.md) |
| ¿Por qué cambió la formulación matemática? | [Historia de decisiones](mathematical-decisions.md) |
| ¿Qué resultados negativos conviene conservar? | [Catálogo de límites y resultados negativos](negative-results.md) |
| ¿Qué ejemplos delimitan la teoría? | [Atlas de ejemplos y contraejemplos](example-atlas.md) |
| ¿Qué puede verificarse o reproducirse con los archivos disponibles? | [Guía de reproducción](reproduction-guide.md) |
| ¿Qué falta resolver y qué evidencia permitiría hacerlo? | [Registro de preguntas abiertas](open-questions.md) |

Las afirmaciones usan identificadores `A01`…`A20`; las decisiones `D01`…`D09`;
las limitaciones `N01`…`N09`; los ejemplos `E01`…`E11`; las preguntas
`Q01`…`Q09`. Son identificadores de
este inventario documental, no experimentos ni nuevos outcomes.

## Procedencia y alcance

Base: commit `f640620b308c4be72119412bdf2c8ecddf961061`, que incluye el compendio
propuesto en PR #12. No se presupone que ese PR esté integrado en main. Los
informes históricos se leen como fuentes, no como estado operacional en vivo.
E16-C se referencia por commit fijo externo a esta base, sin importar su código.
`source_manifest.csv` registra bytes y hashes de las fuentes locales consultadas;
`review.json` conserva la revisión documental y la protección de archivos.

La documentación específica de T2-A se añade únicamente en
[`experiments/T2_A/codex`](../../experiments/T2_A/codex/README.md), conforme a la
indicación del usuario. No se altera `claude/`, ni protocolos, predictores,
clasificaciones, visitas u outcomes existentes.
