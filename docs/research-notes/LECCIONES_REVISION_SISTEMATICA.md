# Lecciones de proceso: revisión sistemática Q15 (2026-11)

**Estado:** documento vivo, escrito durante el cribado de Q15, cuando estaban auditados los lotes 01–10.
**Naturaleza:** solo documental. No cambia el protocolo de Q15 ([PROTOCOLO_OPERATIVO_v3](Q15/PROTOCOLO_OPERATIVO_v3.md)), no adjudica novedad y no aporta evidencia científica.
**Para qué sirve:** guardar qué decisiones de proceso funcionaron, cuáles hubo que rehacer y por qué, para que la próxima revisión o el próximo experimento empiece mejor. Cada entrada remite a evidencia verificable: commits y comentarios del [PR #138](https://github.com/jaiborojas-cloud/leviathan/pull/138).

Reparto de roles durante Q15:
- el responsable decide y ejecuta en su PC;
- el otro agente (Codex) diseñó el protocolo y hace el cribado;
- Claude implementó la revisión y audita.

---

## 1. Decisiones que funcionaron

| # | Decisión | Por qué funcionó | Evidencia |
|---|---|---|---|
| B1 | Congelar el protocolo, las consultas y los topes (N = 500, K = 200) **antes** de buscar, con SHA y manifiestos | Ninguna decisión posterior pudo ajustarse a los resultados. Cada enmienda quedó fechada y registrada antes de aplicarse | protocolo v3 (`a9b85e64`); enmienda S2 v3.1; enmienda de identidad por metadatos registrada antes de R4 ([comentario](https://github.com/jaiborojas-cloud/leviathan/pull/138#issuecomment-6744475206)) |
| B2 | Un ejecutor con **identidad de salida** (script, insumos y modo), caché reanudable y estados explícitos | Cortes con Ctrl+C, 429 y reintentos sin perder ni mezclar datos. Un intento con el script equivocado fue **rechazado** por el propio ejecutor («Salida pertenece a otro script») | ejecutor v2.1 (`505e4239`); [cierre de la recuperación](Q15/ejecucion/CIERRE_RECUPERACION_v31_1_2026-11-05.md) |
| B3 | **Lo pendiente nunca cuenta como cero.** Lo truncado, lo parcial y lo omitido se declaran | ICLR, A08, S03/S20 y las referencias incompletas de S2 quedaron visibles como limitaciones, no escondidas | cierre de la recuperación, inventario |
| B4 | **Separar a quien hace de quien audita** | Detectó errores reales en los dos sentidos: el lote 05 hecho con plantilla (rechazado), tres exclusiones incoherentes en el lote 04 y un error de atribución de run de Claude, detectado por el otro agente | [lote 05 rechazado](https://github.com/jaiborojas-cloud/leviathan/pull/138#issuecomment-6743205571); [lote 04 O1](https://github.com/jaiborojas-cloud/leviathan/pull/138#issuecomment-6742954894); corrección del run (`4a95e721`) |
| B5 | **Corregir con un paquete aparte**, sin sobrescribir lo aprobado ni borrar lo rechazado | Siempre se puede reconstruir qué se decidió primero y qué se cambió después | correcciones O1, 05/06 y cercanía del 08 |
| B6 | Entregar lotes cerrados de 100, con selección **fijada antes de leer**, manifiesto y SHA | Cada lote se audita por separado. Un corte por límite de uso perdió como mucho un lote, y quedó documentado | lotes 04–09 |
| B7 | La auditoría **recalcula de forma independiente**, no se limita a leer el informe | Así se verificaron 72/72 identidades por metadatos, las 23 decisiones repetidas del lote 07 y las sumas del balance (4 513) | [R4](https://github.com/jaiborojas-cloud/leviathan/pull/138#issuecomment-6744475206); [lote 07](https://github.com/jaiborojas-cloud/leviathan/pull/138#issuecomment-6743902974) |

## 2. Errores y retrabajo

| # | Qué pasó | Costo | Lección |
|---|---|---|---|
| E1 | Las pruebas del ejecutor pasaban en Linux y fallaron en Windows (87/91) por separadores de ruta | Una versión nueva (v2.1) y una corrida extra | **Probar en la plataforma donde se va a ejecutar**, antes de entregar |
| E2 | No se probó el acceso real a cada fuente antes de congelar: ICLR/OpenReview exigía cuenta (403), una espera de 45 s no alcanzaba para los índices grandes de NeurIPS y sin clave de S2 hubo muchos 429 | ICLR quedó fuera como limitación, y se agregó una desviación operativa (120 s) | **Hacer un piloto de acceso por fuente** (una consulta y un volumen) antes de congelar. Tramitar claves de API con anticipación |
| E3 | Las estimaciones de tiempo y volumen de Claude fallaron varias veces (horas de descarga, número de artículos, número de lotes) | Expectativas equivocadas y replanificación | **Medir con una muestra** antes de dar cifras, y dar rangos explícitos |
| E4 | Las consultas amplias ordenadas por citas metieron mucho ruido: homónimos de «Fisher», temas ajenos muy citados | Más cribado manual | **Probar cada consulta** con los primeros 20 resultados antes de congelar y anotar la precisión estimada |
| E5 | El criterio de identidad de duplicados se definió tarde y demasiado estricto (solo DOI o arXiv). Las actas sin identificador no se unían | 23 de 100 obras del lote 07 eran repetidas. Hizo falta una enmienda (R4) | **Definir el criterio de identidad antes de cribar**, incluyendo registros de actas sin identificadores |
| E6 | La escala de cercanía (ALTA/MEDIA/BAJA) se inventó a medio cribado y se recalibró dos veces: todo ALTA en el lote 05, ALTA inflada en el punto 4 en el lote 08 | Correcciones de cercanía y relectura de un lote | **Definir la rúbrica con ejemplos de cada nivel y calibrarla con el auditor** en una muestra antes del primer lote |
| E7 | El lote 05 se hizo con plantilla: primera oración del resumen copiada, justificación idéntica, la misma hora en todo y ninguna variación en la cercanía | Rechazo y relectura completa | Con cribado hecho por IA, **auditar los primeros lotes con lupa** y vigilar esas señales. Un ritmo muy rápido por sí solo no prueba nada, pero es motivo para revisar |
| E8 | Claude atribuyó el inventario final de citas a `run_000011` en vez de `run_000012`, porque el comando de resumen tomaba «el más reciente» sin mostrar su nombre | Hubo que regenerar el paquete (A → B) y corregir el reporte | **Imprimir siempre el identificador exacto** del artefacto resumido. No resumir «el último» sin nombrarlo |
| E9 | Comandos para PowerShell entregados en varios bloques y con variables de sesiones anteriores: se mezclaron versiones (v2 contra v2.1) y una carpeta quedó con la identidad de otro script | Corridas fallidas y carpetas con sufijo `_B` | Entregar **un solo bloque autocontenido** para una ventana nueva, que verifique los SHA antes de ejecutar |
| E10 | **Trazabilidad dispersa entre sesiones y agentes.** Los lotes 01–03 (Codex el 01; Antigravity/Argon el 02 y el 03) **sí estaban auditados** por Claude en otra sesión (`AUDITORIA_CRIBADO_C_LOTE0{1,2,3}_2026-11-05.md`, con los SHA de sus paquetes). Sus originales estaban en la carpeta de trabajo de Antigravity, y esta sesión los dio por no auditados hasta encontrarlos. Aparte, 466 de las 492 decisiones heredadas de B tienen razones de plantilla basadas en el título y deben recribarse | Búsqueda de paquetes y una afirmación errónea, ya corregida, en el PR #138 | **Un índice único** en el repo con cada paquete, su SHA, su revisor y su auditoría, que se consulte antes de afirmar que algo falta. Las decisiones heredadas se auditan o se marcan como no auditadas |
| E11 | Un solo lector de IA por lote, con revisores distintos según el lote (Codex o Antigravity/Argon). Un piloto de cribado con modelo abierto local (gemma4:31b) se declaró **NO APTO**: tuvo 3 omisiones de 27 obras protegidas, con umbral 0 (`ecfffd49`) | No se puede medir la concordancia entre revisores; el modelo local no sirve como cribador principal | Para la próxima: **un segundo revisor independiente sobre una muestra aleatoria** (por ejemplo 10 %) con concordancia reportada. Validar todo cribador nuevo con obras protegidas y umbral de omisión preregistrado, como en ese piloto |

## 3. Lista de verificación para la próxima revisión o experimento

**Antes de congelar**
- [ ] Pregunta descompuesta en puntos verificables y diccionario de términos para evitar equivalencias falsas (como el §1.1 de Q15).
- [ ] Piloto de acceso por fuente: autenticación, límites de tasa, tiempos de respuesta de las páginas grandes y claves de API tramitadas.
- [ ] Piloto de cada consulta (primeros 20 resultados) y precisión anotada.
- [ ] Criterio de identidad y duplicados definido, incluyendo registros sin DOI ni arXiv.
- [ ] Rúbrica de inclusión y de cercanía con ejemplos por nivel, calibrada con el auditor en una muestra.
- [ ] Estimación de volumen y tiempo medida con una muestra, en rangos.

**Herramientas**
- [ ] Pruebas que pasan en la plataforma de ejecución real (Windows del responsable).
- [ ] Identidad de salida, caché reanudable y pendientes que nunca se cuentan como cero.
- [ ] Comandos entregados en un solo bloque autocontenido que verifica los SHA.

**Durante**
- [ ] Lotes cerrados con selección fijada antes de leer, manifiesto y SHA.
- [ ] Auditoría intensiva de los primeros lotes, con señales de plantilla revisadas.
- [ ] Segundo revisor sobre una muestra y concordancia reportada.
- [ ] Correcciones en paquete aparte, con la hora real.
- [ ] Todo resumen o reporte nombra el artefacto exacto (run, SHA).

**Al cerrar**
- [ ] Balance que cuadra contra el total del universo, con todas las categorías.
- [ ] Toda decisión del corpus con auditoría registrada.
- [ ] Limitaciones (fuentes excluidas, pendientes, un solo lector) escritas en la conclusión.
- [ ] Actualizar este documento con las lecciones nuevas.

## 4. Reutilizar el corpus descargado

La recuperación de Q15 (unos 51 000 registros de actas NeurIPS/ICML más los resultados de S2 y arXiv, guardados en `D:\RIPG_DATA\Q15_v31_1_RED`, fuera de Git) puede servir para **explorar** líneas nuevas, con estos límites:
- El corpus lo eligieron las consultas de Q15 y hereda su sesgo. Una revisión **confirmatoria** de otra pregunta necesita consultas propias, congeladas antes de mirar, conforme a AGENTS.md: no usar los mismos datos para descubrir y para confirmar.
- Los datos crudos no se suben al repositorio ni se redistribuyen (licencia de la API de Semantic Scholar). En Git solo van los reportes, los SHA y los índices derivados que se permitan.
- Si un hallazgo exploratorio motiva una línea nueva, se registra como hipótesis exploratoria, con su procedencia, no como evidencia.

**Ideas futuras registradas (2026-11-09, decisión del responsable: anotarlas sin diseñarlas, para después de cerrar Q15):**
1. **Buscador semántico local (RAG)** sobre los resúmenes del corpus, con *embeddings* generados en el PC del responsable, por ejemplo con Ollama, para explorar líneas nuevas de RIPG.
2. **Clasificador afinado con las decisiones auditadas de Q15** (decisión, razón propia y cercanía) para **ordenar o priorizar** artículos en revisiones futuras. No decidiría solo: para usarlo como cribador tendría que pasar una validación con obras protegidas y umbral de omisión preregistrado, como la que el piloto con gemma4:31b no superó (`ecfffd49`).

Las dos son de uso exploratorio y no implican redistribuir resúmenes.

---

*Pendiente al redactar:* recribado de las 466 decisiones heredadas con plantilla; plan para las 857 obras pendientes de acceso, verificación o fecha; lotes restantes de la cola principal. Los lotes 01–10 están auditados.
