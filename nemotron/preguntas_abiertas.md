# Preguntas abiertas del marco RIPG — mapeo Nemotron

Mapeo de las preguntas Q01–Q09 de `docs/research-notes/open-questions.md` y qué tipo de nota podría aportar Nemotron como lectura documental. Esto no autoriza ejecución de experimentos ni entrenamiento de redes.

| ID | Pregunta | Tipo | Enfoque posible desde Nemotron |
|---|---|---|---|
| Q01 | ¿Qué hacía exactamente `relevance_covariant_derivative` y cuál fue la secuencia E6? | Procedencia | Nota de lectura sobre la ausencia de la fuente; no reconstruir la implementación. |
| Q02 | ¿Qué elecciones de familia, $H$ y regularización tienen justificación canónica? | Matemática/metodológica | Análisis de que la covariancia no selecciona una referencia única; comparar elecciones explícitas y transportadas. |
| Q03 | ¿Qué parte de la geometría es estable frente al panel y modos débiles? | Instrumental | Lectura sobre rango, tamaño de panel y error de estimación; no ejecutar protocolo de estabilidad. |
| Q04 | ¿Qué dominio admite inyectividad y minimización con garantías suficientes? | Geométrica/instrumental | Síntesis de que conjugado, corte, frontera y error numérico son fenómenos distintos. |
| Q05 | ¿La señal de magnitud/localización replica fuera de las tareas de descubrimiento? | Empírica | Nota de que se requiere réplica prospectiva con faltantes conservados; no ejecutar. |
| Q06 | ¿Cuándo cambia de forma estable el rango por composición en redes? | Matemática/empírica | Lectura de contraejemplos analíticos; no confundir término mixto con pérdida de rango. |
| Q07 | ¿La señal temprana anticipa eventos futuros con utilidad incremental? | Predictiva | Lectura del diseño T2-A0 (prerregistro); no evaluar la cohorte completa. |
| Q08 | ¿Cuál es la definición operacional completa de $s_\ell$, $H_\phi$ y juego vacío? | Procedencia/definición | Nota de que la nota seleccionada reporta cifras pero no todas las reglas de normalización. |
| Q09 | ¿Puede otro colaborador reproducir cada etapa con sus datos externos? | Reproducibilidad | Síntesis sobre disponibilidad y permisos de paquetes/checkpoints, no solo URL. |

## Dependencias entre preguntas

Q01 y Q08 son faltantes de fuente: no se rellenan mediante nuevos experimentos. Q02–Q04 afectan la interpretación de Q05–Q07. El control instrumental de precisión no resuelve por sí solo Q02, Q04 ni Q06.

## Cómo mantener el registro

Añadir fuente y fecha/corte al resolver una pregunta; conservar su formulación anterior y la evidencia que motivó el cambio. Distinguir «sin respuesta», «inconcluso por instrumento» e «hipótesis no respaldada con instrumento válido».
