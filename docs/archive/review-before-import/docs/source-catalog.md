# Catálogo de fuentes

Inventario del checkout inicial: sólo `README.md` y `Perspectivas.ipynb`; sin AGENTS.md, protocolos, manifests ni cierres. Inspección del workspace: no se encontraron otras fuentes científicas fuera del notebook; se excluyeron dependencias instaladas y configuración generada. No se consultaron bibliotecas ni conversaciones externas.

| ID | Ruta | Procedencia / versión | Sustenta | SHA-256 |
| --- | --- | --- | --- | --- |
| S1 | [Perspectivas.ipynb](../Perspectivas.ipynb) | Checkout base, commit 2592f910e4d2ece8bfd1cde2cbcd58224958068b; fecha científica no establecida | Fundamentos parciales, índice y salidas E6–E8 | `8e8145c37fceaadc9ead53c19617459ce337c791d8b55916acb5bf9cfc933ad4` |
| S2 | [docs/archive/README.original.md](archive/README.original.md) | README inicial UTF-16, preservado sin cambios | Nombre inicial del repositorio | `2f1ce39830717b8fc7b88833b1d05e053cce73a759695b815f616337c0b9127e` |
| S3 | [docs/archive/solicitud-documental.txt](archive/solicitud-documental.txt) | Bytes del archivo aportado por el usuario; fecha de autoría no establecida | Alcance, pistas posteriores no corroboradas y temas futuros | `7d5c7deb690c076a54d11dbc61b15754bf801b7162240ab56a40fc56e8549f66` |

Los hashes corresponden a bytes disponibles; no se inventan hashes de fuentes ausentes. El README actual es un resumen nuevo; S2 conserva los bytes anteriores. S3 es una solicitud y contexto orientativo, no un cierre experimental.

## Correspondencia y discrepancias

- [Fundamentos](foundations/mathematical-framework.md): S1, celdas 26, 41, 65, 138–159; ω_P y B generales proceden de S3 y requieren fuente formal.
- [Estado](research-status.md) e [índice](experiment-index.md): S1; celdas 129, 132, 159, 169–176 para cifras históricas. E9–T2 se señalan ausentes según inventario y S3.
- [Roadmap](roadmap.md) y [direcciones](research-directions.md): necesidades de S3; propuestas nuevas etiquetadas, sin atribución histórica ficticia.
- E6: dos errores diferentes para el resumen a radio 0.15, sin secuencia de ejecución verificable. No se corrigen los originales.
- E8: `relevance_covariant_derivative` invocada sin definición localizada. La presencia de salidas no resuelve esa dependencia.
- No hay fuentes locales para contrastar INCONCLUSIVE, GEOMETRIC_NONINJECTIVITY, ≈0.9549, 38 estados, 800 basales o frontera update25. No se detecta una contradicción demostrada con esos datos: falta evidencia para compararlos.

La [lista agrupada de faltantes](handoff/missing-sources.md) es el registro de recuperación. Los originales recibidos en adelante se conservarán en archivo histórico con procedencia y hash, sin reescribirlos.
