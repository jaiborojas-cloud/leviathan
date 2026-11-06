# Reauditoría independiente Q15 — enmienda 2

Fecha: 2026-11-06 (America/Mexico_City). Auditor: Codex, IA. Repositorio: jaiborojas-cloud/leviathan. Rama: docs/q15-protocolo-sistematico-v1. Commit: d580da24.

**Dictamen: no aprobar todavía la ejecución oficial.** Las correcciones centrales de prompt, esquema y protección de CONTEXTO funcionan, pero quedan fallos de integridad/estado y pérdida de historial. No es un veredicto del modelo ni una conclusión de novedad.

## Alcance y restricciones

Se leyó AGENTS.md del commit, RESPUESTA_AUDITORIA_CODEX.md y el preregistro completo, incluido Historial; se revisaron Python, PowerShell, prompt, README, partición y pruebas. Se contrastó con los hallazgos G1–G6, M1–M5 y D1–D3 de la auditoría anterior. No se modificó el repositorio ni se hicieron commit, push o comentarios. No se abrieron paquetes reales, no se escribió en D:\\RIPG_DATA y no se utilizaron modelos ni Azure.

Las copias y los arneses están fuera del repo; los datos inventados se crearon en carpetas temporales. Los hashes de Python, PowerShell, prompt, partición y suite coinciden con el preregistro. La suite original usa llamadas simular=False a un imitador HTTP local, no a un modelo: su ejecución directa se detuvo por WinError 10013 del sandbox. Se ejecutó entonces el archivo original sin editar mediante un adaptador de transporte enteramente en memoria: el mismo manejador inventado del servidor, sin sockets. **37 comprobaciones pasan, salida 0.** No se presenta esto como ejecución HTTP nativa exitosa.

El arnés independiente etiqueta únicamente con simular=True, bloquea urllib y evalúa fixtures sintéticos. Para probar el validador oficial se construyen deliberadamente metadatos de fixture; eso no convierte las filas en resultados reales. PowerShell 7.6.9 se probó con funciones que sustituyen az, ssh y scp; ninguna invoca esos servicios. Bash local no pudo arrancar por una restricción de objetos del sandbox; tmux/timeout/PIPESTATUS reales permanecen sin verificar.

## Estado de cada hallazgo anterior

| ID | Estado | Archivo/línea y caso comprobatorio |
|---|---|---|
| G1 | Resuelto | [cribado_llm.py:163](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L163): mensaje de 8 954 caracteres, SHA efectivo 4659f18ddde2d7634ffc2aa4ec0db857c955d1176993f5b5dacb97307cd42727. Un prompt alterado se rechaza. |
| G2 | Resuelto para la interpretación local | [cribado_llm.py:222](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L222): sin puntos, puntos como string o punto 99 se rechazan; también claves extra, razón vacía y dudoso no booleano. Véase observación menor sobre el esquema enviado a Ollama. |
| G3 | Parcial | [cribado_llm.py:259](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L259) y [cribado_llm.py:330](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L330): se rechaza config ajena al reanudar y simulado=true al evaluar oficialmente. Pero un script_sha256 desconocido uniforme termina APTO; véase R1. |
| G4 | Parcial | [cribado_llm.py:394](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L394) y [cribado_llm.py:419](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L419): falta de salida pasa a INCONCLUSIVO. eleccion.json truncado deja APTO vigente; dos intentos en el mismo segundo sobrescriben la copia histórica. R2–R3. |
| G5 | Resuelto para códigos de comandos nativos locales | [cribado_llm_azure.ps1:47](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm_azure.ps1#L47): az simulado con código 9 lanza excepción. No garantiza detectar fallos internos de un pipeline remoto cuyo shell devuelve 0. |
| G6 | Parcial | [cribado_llm_azure.ps1:153](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm_azure.ps1#L153) y [cribado_llm.py:339](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L339): presupuesto vencido impide lanzar; fila posterior al límite da INCONCLUSIVO. El timeout se calcula antes del arranque/copias y puede exceder el límite absoluto; R5. |
| M1 | Resuelto en los casos reportados | [cribado_llm.py:184](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L184) y [cribado_llm.py:198](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L198): HTTP 500 y cuerpo no JSON producen error tras tres intentos; URLError(timeout) se reconoce; fallo de conexión detiene sin fila. Casos de suite con transporte en memoria. |
| M2 | Parcial | [cribado_llm.py:77](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L77) y [cribado_llm.py:94](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L94): resumen corto aceptado y estructura anidada inesperada rechazada. Pero ___ se acepta aunque no tiene caracteres alfanuméricos. No se verificaron estructuras reales. |
| M3 | Resuelto | [cribado_llm.py:308](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L308): mediana([1,100])=50.5 y mediana([3,1,2])=2. |
| M4 | Resuelto para sesión activa; código remoto pendiente | [cribado_llm_azure.ps1:168](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm_azure.ps1#L168): ssh simulado devuelve SI y lanzar se detiene. Construcción de FIN/código inspeccionada; no se ejecutó tmux/PIPESTATUS real. |
| M5 | Resuelto para los casos originales | [cribado_llm.py:321](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L321): referencia alterada da INCONCLUSIVO. [cribado_llm_azure.ps1:193](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm_azure.ps1#L193): hash remoto distinto al de la descarga simulada detiene bajar. No se certificó una transferencia real. |
| D1 | Resuelto | [cribado_llm.py:28](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L28) y [cribado_llm.py:367](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L367): con 24 inclusiones y 3 CONTEXTO protegidas, excluir las 3 CONTEXTO produce 3 omisiones, sensibilidad 24/27 y compuerta fallida, aunque el acuerdo sea 0.96. |
| D2 | Reconocido, no eliminado | [PREREGISTRO_CRIBADO_LLM.md:76](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/PREREGISTRO_CRIBADO_LLM.md#L76): se declara que no es una muestra aleatoria de las pendientes. Una familia temática ausente sigue sin quedar validada. |
| D3 | Mitigado, no eliminado | [PREREGISTRO_CRIBADO_LLM.md:75](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/PREREGISTRO_CRIBADO_LLM.md#L75) y [PREREGISTRO_CRIBADO_LLM.md:87](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/PREREGISTRO_CRIBADO_LLM.md#L87): 100 exclusiones y suspensión con un error; 0.95^100=0.00592053 bajo independencia. En validación 0.9^27=0.05814974. Son cálculos del diseño, no tasas observadas. |

## Hallazgos graves pendientes o recién detectados

### R1. La firma oficial no fija la versión autorizada ni verifica la coherencia de la respuesta

[cribado_llm.py:335](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L335)–364. Residuo de G3 en el nuevo verificador. El hash de script solo se agrega a un conjunto y se exige que el conjunto no tenga más de un elemento por archivo; no se compara con el script congelado ni se exige una versión común entre todos los archivos/configuraciones. El modelo_respuesta y el crudo tampoco se vuelven a validar.

**Reproducido:** fixture que pasa la validación → cambiar script_sha256 a 64 ceros en su única fila → APTO. Cambiar además modelo_respuesta a wrong-model y crudo a texto que no es JSON, manteniendo la decisión tabulada → APTO. El conjunto de prueba es inventado; se demuestra que el evaluador no detecta la incompatibilidad, no que haya ocurrido contaminación real.

La reanudación sí compara el hash con el script actual y constituye una mejora. La evaluación oficial necesita una comprobación equivalente y coherencia entre decisión tabulada, respuesta cruda y modelo, además de validar la estructura de las filas. Rechazar simulado=true no basta para garantizar la procedencia.

### R2. Excepciones de integridad dejan vigente un APTO viejo

[cribado_llm.py:401](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L401), [cribado_llm.py:426](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L426) y [cribado_llm.py:432](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L432). Residuo de G4. Solo se captura Inconclusivo; JSONDecodeError, claves ausentes y tipos inválidos escapan. La declaración de que siempre se escribe el estado no se cumple.

**Reproducido:** validar fixture correcto → APTO; sustituir eleccion.json por un único carácter {; volver a validar → JSONDecodeError, y veredicto.json continúa APTO. Debe registrarse el fallo del intento, preservando el resultado histórico y sin confundirlo con el vigente.

### R3. El nuevo historial pierde intentos dentro del mismo segundo

[cribado_llm.py:55](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L55) y [cribado_llm.py:64](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L64)–68. Introducido por el nuevo mecanismo de archivo histórico. La hora tiene resolución de segundos y escribir abre en modo w.

**Reproducido con reloj fijado:** validación APTO y otra INCONCLUSIVO en 2026-11-06T12:00:00Z → ambas apuntan a veredicto_20261106T120000Z.json; queda un solo archivo INCONCLUSIVO y se pierde la copia APTO. Incumple conservar una copia de cada intento. Usar identificadores únicos y escrituras atómicas/exclusivas evita colisiones y estados parciales.

### R4. La reanudación falla si el corte ocurre dentro de un carácter UTF-8

[cribado_llm.py:274](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L274)–281; también [cribado_llm.py:347](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L347)–351. Recién detectado, pero el patrón defectuoso ya existía: no se atribuye su introducción a la enmienda.

**Reproducido:** archivo que termina en los bytes de {"razon":" seguidos del byte 0xC3, primera mitad de un carácter acentuado. Reanudar con simular=True agrega LF y después lanza UnicodeDecodeError al iterar el archivo. El try está dentro del bucle y no captura la decodificación del iterador. Relanzar vuelve a fallar; la recuperación de líneas truncadas solo se probó con un corte que conserva UTF-8 válido.

No se observa pérdida de filas completas en este caso, pero la recuperación automática prometida queda bloqueada. Recuperar por líneas en bytes, conservar la cola dañada y rehacer solo lo incompleto es una posible solución.

### R5. El timeout relativo puede rebasar el presupuesto absoluto

[cribado_llm_azure.ps1:153](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm_azure.ps1#L153)–177. Defecto del nuevo control de G6; deducción estática a partir del comando construido, sin ejecutar Azure ni timeout.

Caso: quedan 120 s al calcular restante; arrancar la VM, consultar IP, revisar sesión y copiar archivos consume 90 s; luego se lanza timeout 120. La ejecución puede llegar 90 s después del límite. Con 180 s de preparación incluso arranca después de vencer el presupuesto. No se recalcula restante ni se vuelve a comprobar la fecha al lanzar.

El filtro Python de filas posteriores limita su admisión al veredicto, pero no impide el gasto ni la ejecución fuera de plazo, y puede invalidar una salida que mezcla filas a tiempo y tardías. Recalcular inmediatamente antes del lanzamiento y controlar el límite absoluto en el proceso es necesario. El apagado diario continúa siendo una protección diferente, no un cierre de VM al vencer este presupuesto.

## Hallazgos menores y reservas adicionales

1. **Desempate final dependiente del orden de probar.validas.** [cribado_llm.py:411](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L411) frente a preregistro:62. Con métricas y tiempos iguales y validas=[C2,C1], se elige C2; el criterio 5 exige C1. Reproducido. El probar actual genera normalmente el orden C1..C4, de modo que es un caso borde, no una divergencia observada en su flujo normal. Añadir la configuración al criterio de orden hace la regla explícita.
2. **Alfanumérico no equivale a \\w.** [cribado_llm.py:79](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L79). tiene_texto('___') devuelve true. La nueva regla documental dice al menos un carácter alfanumérico; guion bajo no lo es. Reproducido; impacto en paquetes reales no comprobado.
3. **Esquema enviado menos estricto que el intérprete.** [cribado_llm.py:30](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L30)–39 no contiene additionalProperties:false ni minLength para razon, mientras interpretar exige exactamente cuatro claves y razón no vacía. Una respuesta con clave extra es admisible por el esquema enviado pero localmente INVALIDA. La defensa local está bien; conviene que el esquema de generación exprese las mismas restricciones. No se llamó a Ollama para medir la frecuencia del caso.
4. **Tipos de firma no estrictos.** [cribado_llm.py:352](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L352): Python considera 0 igual a False. Un fixture con think=0 y simulado=0 pasa como APTO. No equivale a aceptación de simulado=true; es una debilidad de esquema en archivos de resultados.
5. **Pipeline remoto puede ocultar fallos internos.** [cribado_llm_azure.ps1:116](https://github.com/jaiborojas-cloud/leviathan/blob/d580da24/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm_azure.ps1#L116) usa curl | sh sin pipefail: curl fallido y sh con entrada vacía pueden devolver éxito global. Invoke-Nativo solo observa el código final de ssh. Es un residuo operativo, no un fallo de su nueva comprobación local. No se reprodujo en Bash porque su arranque fue bloqueado.
6. **Auditoría de producción con menos de 100 exclusiones.** Preregistro:87 no explicita qué hacer si un lote tiene 40 exclusiones: una muestra sin reemplazo de 100 no es posible. Fijar censo cuando N<100, semilla concreta y marco de muestreo antes de producción. El cálculo 0.95^100 es ilustrativo bajo independencia, no garantía universal.

## Revisión amplia: puntos correctos y límites

- El prompt de archivo no cambió y su hash coincide con el previamente contrastado con protocolo y decisiones. La extracción ahora entrega el bloque completo, y el hash del texto efectivo impide aceptar cambios inadvertidos.
- El algoritmo de partición conserva agrupación por título normalizado, estrato conservador, semilla y alternancia. Los duplicados sintéticos permanecen en una mitad; las correcciones del lote02 se leen del lote03. La partición real no se regeneró porque los paquetes estaban fuera del alcance autorizado.
- La referencia por obra no se sube a la VM. La nueva subida incluye particion.json, con hashes y conteos agregados, pero no etiquetas por obra; ese archivo tampoco se añade a los mensajes del modelo. No se observó una fuga de la mitad de validación hacia la elección en las funciones: referencia se filtra por mitad, elegir usa selección y validar usa la elegida en validación.
- Las configuraciones no evaluadas quedan fuera de la elección; el límite de inválidas se aplica antes de ordenar; INVALIDA no cuenta como exclusión, pero penaliza acuerdo e inválidas según lo declarado. La prueba de NO_EVALUADAS de la suite pasa.
- Los dos criterios del responsable y la regla prudente de incluir ante duda siguen compatibles con el tratamiento de producción. Las cambios de protección CONTEXTO, tiempo y muestreo están declarados en Historial como decisiones del responsable; no se tomaron como cambios silenciosos.
- format, think y options están en los campos documentados de /api/chat. No se verificó compatibilidad real de etiquetas, versión, memoria, salida estructurada o razonamiento. [API oficial](https://docs.ollama.com/api/chat).
- PowerShell no presenta errores de sintaxis. Los mocks confirman propagación de error nativo, sesión activa, presupuesto vencido, hash de descarga inválido y construcción de la cadena remota. No certifican SSH/SCP reales, shell de tmux, drivers ni Azure. El uso de PIPESTATUS requiere un shell que lo soporte; no se verificó el shell efectivo de la VM. [Manual de tmux](https://man.openbsd.org/tmux.1).
- D2 sigue siendo un límite de representatividad. D3 reduce el riesgo de no detectar errores en producción, sin convertir la referencia IA en referencia humana ni garantizar cobertura de familias ausentes. APTO solo puede significar superar los controles declarados del piloto, una vez corregida la implementación.

## Artefactos de reproducción

- [Suite original](pruebas_sinteticas.py), sin editar.
- [Adaptador sin red](ejecutar_suite_sin_red.py).
- [Log suite directa bloqueada](suite_claude.log).
- [Log de las 37 comprobaciones con transporte en memoria](suite_claude_sin_red.log).
- [Arnés independiente](arnes_independiente.py) y [resultados](resultados_independientes.json).
- [Arnés PowerShell con az/ssh/scp simulados](arnes_powershell.ps1) y [resultados](resultados_powershell.json).

Las salidas APTO de los arneses son exclusivamente fixtures de software. No constituyen aprobación de un modelo, ejecución oficial ni modificación del estado de Q15.

