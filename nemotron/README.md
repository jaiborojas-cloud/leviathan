# Nemotron — perspectiva independiente sobre el marco RIPG

Esta carpeta contiene la línea de trabajo de Nemotron sobre el marco general de RIPG (*Relevance-Induced Perspective Geometry*). No modifica `docs/theory/`, `docs/research-notes/`, `experiments/` ni `experiments/T2_A/claude/`. Todo lo aquí es **exploratorio** y no sustituye resultados oficiales, sellos ni criterios congelados.

## Estructura

| Ruta | Contenido |
|---|---|
| [`marco_teorico.md`](marco_teorico.md) | Síntesis de lectura de los capítulos de `docs/theory/` (admisibilidad, métrica, curvatura, observables, composicionalidad, hipótesis) |
| [`preguntas_abiertas.md`](preguntas_abiertas.md) | Mapeo de las preguntas abiertas del marco y qué abordan las notas de Nemotron |
| [`analisis_rip_general.md`](analisis_rip_general.md) | Análisis del marco general de RIPG sin centrarse en T2-A |
| [`HASHES_SHA256.txt`](HASHES_SHA256.txt) | SHA-256 de cada archivo de esta carpeta |
| [`notas/`](notas/) | Notas incrementales de análisis (vacío al iniciar) |

## Datos y cómputo pesado

- **Datos pesados, checkpoints y arrays diagnósticos** se mantienen fuera de Git en `D:\RIPG_DATA\` (enmienda local, no versionada en el repo).
- Este repositorio conserva solo código, protocolos, manifiestos, hashes, reportes y documentación.
- No se subirán archivos ZIP, checkpoints ni `.npz` a `leviathan/nemotron/`.

## Reglas aplicables

- Solo escritura dentro de `leviathan/nemotron/`.
- Lectura de `docs/`, `archive/`, `experiments/` sin modificar nada.
- Documentación no autoriza experimentos, entrenamientos ni auditorías geométricas sobre datos de terceros.
- Escribir en español, conservar identificadores técnicos, usar enlaces relativos.
- No inventar fuentes, resultados, fechas ni hashes.
