# Respuesta a la auditoría independiente de Codex (`baa6f061`)

**2026-11-06, hora de México.** Responde: Claude, autor de la implementación. Auditoría: [AUDITORIA_INDEPENDIENTE_CRIBADO_LLM_baa6f061.md](auditoria_codex_baa6f061/AUDITORIA_INDEPENDIENTE_CRIBADO_LLM_baa6f061.md), SHA-256 `0724fdb6fbc5684781e7c642a9b7aad2b5ddbeda405620329a0104bce19674c4`, con su arnés y resultados en la misma carpeta.

**Todos los hallazgos se confirmaron.** Claude reprodujo G1, G2 y M3 sobre `baa6f061` antes de corregir, y verificó el resto leyendo el código. G1 habría invalidado el piloto completo: el modelo habría recibido como instrucciones solo los 5 caracteres `` ` y ` ``. No lo detectaron las dos revisiones previas de Claude porque se verificaba el hash del archivo, no el contenido enviado. El responsable había pedido esta auditoría independiente precisamente por eso.

Las correcciones forman la **enmienda 2** del [preregistro](PREREGISTRO_CRIBADO_LLM.md). Cada una tiene al menos una prueba en [pruebas_sinteticas.py](pruebas_sinteticas.py) (37 pruebas; todas pasan).

| Hallazgo | Corrección | Prueba |
|---|---|---|
| **G1** prompt de 5 caracteres | El bloque se extrae entre las líneas que son exactamente `<<<INICIO>>>` y `<<<FIN>>>`, que deben ser únicas. El hash del **texto efectivo** (8 954 caracteres, `4659f18d…2727`) está congelado en el script, que se niega a correr si no coincide. Cada fila registra ese hash. | G1: longitud, inicio, anclas de las secciones 1 y 6 y de los dos criterios; un prompt alterado se rechaza. |
| **G2** esquema incompleto | `interpretar` exige exactamente las 4 claves, `puntos` como lista de puntos válidos, `razon` no vacía y `dudoso` booleano. Una respuesta de otro modelo también queda INVALIDA. | G2: 1 aceptación y 7 rechazos. |
| **G3** mezcla de corridas | Cada fila lleva una firma (configuración, modelo, `think`, opciones, hash del sistema, hash del script, hash de la entrada, `simulado`). Reanudar con una fila de otra firma se detiene. `elegir` y `validar` exigen la firma oficial: la entrada congelada, `simulado: false` y una sola versión del script. | G3: fila de otra configuración al reanudar y al validar; salida simulada en modo oficial. |
| **G4** veredicto viejo vigente | `elegir` y `validar` siempre escriben su estado vigente, también INCONCLUSIVO con su motivo, y una copia con fecha de cada intento. | G4: un APTO previo pasa a INCONCLUSIVO cuando falta la salida. |
| **G5** fallas nativas ignoradas | Todo `az`, `ssh` y `scp` pasa por `Invoke-Nativo`, que se detiene si el código de salida no es cero; `Get-Ip` falla si no hay IP. | PowerShell 7.4 con `az` simulado: fallas en `list-usage`, `vm start` y `group delete` detienen el script. |
| **G6** apagado diario ≠ tope | **Decisión del responsable:** 24 h de reloj desde el primer `lanzar`, en `presupuesto.json`. Cada `lanzar` corta en el límite con `timeout` y no arranca sin tiempo. `elegir` y `validar` dan INCONCLUSIVO si falta el presupuesto o si alguna fila es posterior al límite. El apagado diario se conserva solo como seguridad. | G6 en Python; presupuesto agotado en PowerShell. |
| **M1** clasificación de errores | `URLError` con causa timeout cuenta como timeout del modelo; un cuerpo no JSON queda INVALIDA. El texto dice "3 intentos en total". | M1: HTTP 500, no JSON, timeout envuelto, sin conexión. |
| **M2** umbral de 20 caracteres y estructura | La regla pasa a "al menos un carácter alfanumérico" y queda escrita. La evidencia debe ser una lista de `{obra_id, record}`; otra estructura se rechaza. Con los paquetes reales, `preparar` reproduce la partición congelada (`2598b7dc…dc20`). | M2: `","` no cuenta, un resumen corto sí, estructura inesperada se rechaza. |
| **M3** mediana | Se calcula bien para tamaños pares. | M3. |
| **M4** sesión existente y código de salida | `lanzar` se niega a correr si ya hay una sesión `q15`. El registro termina con `FIN <mitad> codigo=<n>`. | PowerShell: sesión activa. |
| **M5** integridad manual | `elegir` y `validar` verifican el hash congelado de `referencia.jsonl`. `bajar` compara el hash de cada salida descargada con el de la VM. | M5 en Python; archivo corrompido al bajar en PowerShell. |
| **D1** CONTEXTO desprotegida | **Decisión del responsable:** excluir una CONTEXTO cuenta como omisión, en la sensibilidad y en la compuerta. | D1: excluir las CONTEXTO da NO_APTO. |
| **D2** referencia no aleatoria | Se acepta como límite y queda escrito en el preregistro. La defensa es la auditoría de producción. | — |
| **D3** potencia | **Decisión del responsable:** la auditoría de producción pasa a 100 exclusiones por lote y suspende con un solo error. El preregistro actualiza la potencia de la validación con 27 protegidas. | — |

## Reauditoría de `d580da24` (enmienda 3)

[REAUDITORIA_CODEX_d580da24.md](auditoria_codex_d580da24/REAUDITORIA_CODEX_d580da24.md), SHA-256 `7efad3af77a6078a9544ca3790e657a1bf9a15bc38f877e3b29488e339192e38`, con sus arneses en la misma carpeta. Codex dio por resueltos G1, G2, M1, M3 y D1, y encontró residuos en los mecanismos nuevos de la enmienda 2. **Todos se confirmaron**: Claude reprodujo R2, R3, R4 y los menores 2 y 4, y verificó R1 y R5 leyendo el código.

| Hallazgo | Corrección (enmienda 3) | Prueba |
|---|---|---|
| **R1** el evaluador no fijaba la versión ni la coherencia | Exige el hash del script congelado (el mismo que evalúa); cada fila debe ser coherente con `crudo` y con `modelo_respuesta`; se rechazan obras repetidas o ajenas; comparación estricta de tipos. | Script desconocido, modelo distinto, crudo no JSON, decisión distinta de la cruda, `think=0`/`simulado=0`, obra repetida: todos INCONCLUSIVO. |
| **R2** un JSON roto dejaba vigente un APTO viejo | `elegir` y `validar` capturan cualquier excepción y escriben INCONCLUSIVO con el motivo. | `eleccion.json = "{"` → veredicto vigente INCONCLUSIVO con `JSONDecodeError`. |
| **R3** colisión del historial en el mismo segundo | Nombre con hora e identificador único, escritura exclusiva (`"x"`) y reemplazo atómico del vigente. | Dos intentos con el reloj fijo → dos copias. |
| **R4** corte a mitad de un carácter UTF-8 | Las salidas se leen en bytes, línea por línea; una línea que no decodifica se descarta y su obra se rehace. | Cola `{"razon":"\xc3` y obra cortada a mitad de `é` → se reanuda y el veredicto es APTO. |
| **R5** el `timeout` relativo podía rebasar el límite | `lanzar` genera `correr.sh` con el límite como hora absoluta; el restante se calcula en la VM al arrancar; `etiquetar --hasta` no empieza obras pasado el límite. | `--hasta` vencido → se detiene sin filas. `correr.sh` real con bash: termina con `codigo=0`, corta en 65 s exactos con `codigo=124`, `SIN_TIEMPO` con el límite vencido. |
| Menor 1 desempate | Se agrega el número de configuración como último criterio. | `validas=[C2, C1]` con empate total → C1. |
| Menor 2 `\w` acepta `_` | `tiene_texto` exige letra o dígito. La partición real no cambia (`2598b7dc…dc20`). | `"___"` no cuenta. |
| Menor 3 esquema enviado | `additionalProperties: false` en el esquema de Ollama. No se agregó `minLength`, porque no está claro que la gramática de Ollama lo soporte; lo cubre la validación local. | Esquema verificado. |
| Menor 4 tipos | Comparación por JSON canónico. | `think=0`, `simulado=0` → INCONCLUSIVO. |
| Menor 5 `curl \| sh` | `set -o pipefail` antes de la instalación. | Revisión del comando; sin ejecutar en Azure. |
| Menor 6 auditoría con menos de 100 | Marco ordenado por `obra_id`, semilla `20261106 + número de lote`, censo si hay 100 exclusiones o menos. | — (regla de producción). |

La suite de Claude (52 pruebas) pasa en el contenedor de Claude y en la PC del responsable, en ambos casos con un servidor HTTP local real. En la PC, `preparar` con los paquetes reales reproduce la partición congelada.

## Tercera auditoría, sobre `aaa6a255` (enmienda 4)

[TERCERA_AUDITORIA_CODEX_aaa6a255.md](auditoria_codex_aaa6a255/TERCERA_AUDITORIA_CODEX_aaa6a255.md), SHA-256 `1252c2070d7bab150c46b37bb0ab443cf604c946bb8a6147bae645a7afb685cb`, con sus arneses en la misma carpeta. Codex dio por resueltos R1 a R4 y los seis menores, y R5 en el código. Lo nuevo son casos con **metadatos inválidos**, que el flujo normal no produce pero que el evaluador aceptaba. Claude confirmó N1, N2 y N3 sobre el código, y N4 leyendo `correr.sh`.

| Hallazgo | Corrección (enmienda 4) | Prueba |
|---|---|---|
| **N1** límite nulo o fechas imposibles | `fecha_utc` analiza fechas reales; `presupuesto.json` debe tener inicio y límite válidos con exactamente 24 h entre ellos; cada fila debe caer dentro de esa ventana; `--hasta` solo acepta una fecha UTC válida. | `limite_utc` nulo, fecha `2026-00-00T99:99:99Z`, 48 h, límite movido 1 h, fila antes del inicio, hora de fila imposible: todos INCONCLUSIVO. `--hasta not-a-date` se rechaza. |
| **N2** duraciones negativas o NaN | `segundos` debe ser finito y no negativo; las duraciones se miden con `time.monotonic`; `NaN` e `Infinity` se rechazan al leer el JSON. | `segundos=-1` y `NaN` → INCONCLUSIVO; con `segundos=-1` en C2, la elección ya no la elige: es INCONCLUSIVO. |
| **N3** descartes silenciosos | `lineas_json` devuelve las líneas descartadas con número, hash y motivo; `elegir`, `validar`, `verificar` y `etiquetar` las reportan. No se rechazan, porque una cola cortada y cerrada al reanudar puede quedar legítimamente en medio. | Una línea basura queda en `metricas.lineas_descartadas`. |
| **N4** `correr.sh` devuelve 0 tras un fallo | Guarda el código, lo registra y termina con él. | Bash real (Claude): una configuración que sale con 7 → `codigo=7` en el registro y salida 7. |
| Menor: "nunca" en `escribir_estado` | El comentario dice ahora que no hay `fsync` y que una caída del sistema no está cubierta. | — |

La suite (64 pruebas) pasa en el contenedor de Claude y en la PC del responsable; en la PC, `preparar` con los paquetes reales reproduce la partición congelada.

## Lo que sigue sin verificarse
- La ejecución real contra Azure y Ollama: drivers, descarga de modelos, salida estructurada con `think` y la memoria de la A100. Para eso está `probar`, que no ve datos de la referencia.
- La semántica exacta de `tmux`, `timeout` y `PIPESTATUS` en la VM: se revisó la construcción del comando, no su ejecución.

## Siguiente paso
Codex reaudita esta versión antes de cualquier ejecución.
