# Auditoría independiente del piloto de cribado LLM de Q15

- Fecha: 2026-11-06, America/Mexico_City.
- Auditor: Codex, lector IA único.
- Implementación auditada: Claude.
- Repositorio: `jaiborojas-cloud/leviathan`.
- Rama: `docs/q15-protocolo-sistematico-v1`.
- Commit auditado: `baa6f061`.
- Dictamen: **no aprobar la ejecución de esta versión todavía**.
- Alcance: auditoría de implementación y diseño; no evaluación del corpus ni conclusión de novedad.

## Restricciones y método

Se leyó AGENTS.md, los seis archivos de `docs/research-notes/Q15/ejecucion/cribado_llm/`, las secciones 1 y 6 de `PROTOCOLO_OPERATIVO_v3.md` y las decisiones `DECISION_CRITERIO_CONTEXTO_Y_LOTES_2026-11-05.md` y `DECISION_CRITERIO_MEDIDAS_DIFICULTAD_2026-11-05.md`.

No se modificó el repositorio, no hubo commit, push ni comentarios en el PR. No se abrieron los paquetes reales, no se escribió en `D:\RIPG_DATA`, no se llamó a modelos y no se utilizó Azure. Se recuperaron los archivos del commit mediante el conector GitHub y se trabajó con copias externas. Las pruebas del etiquetado usaron datos sintéticos y `--simular`; las funciones de análisis se probaron con esos datos. El arnés bloqueó las llamadas de red de urllib. Las comprobaciones PowerShell fueron de sintaxis, construcción de cadenas y comportamiento de un proceso local, sin ejecutar el ciclo Azure.

Los hallazgos distinguen reproducción sintética de revisión estática. Las líneas corresponden al commit auditado. Las propuestas de corrección no fueron implementadas y cualquier modificación del diseño congelado requiere el procedimiento de enmienda aplicable.

## Hallazgos graves

### G1. El modelo no recibe el prompt: recibe cinco caracteres

**Ubicación:** [cribado_llm.py:157–159](https://github.com/jaiborojas-cloud/leviathan/blob/baa6f061/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L157-L159), en combinación con [PROMPT_CRIBADO_LLM.md:3](https://github.com/jaiborojas-cloud/leviathan/blob/baa6f061/docs/research-notes/Q15/ejecucion/cribado_llm/PROMPT_CRIBADO_LLM.md#L3).

**Estado: reproducido.** El primer split encuentra la marca mencionada en la introducción del archivo, no la marca independiente de la línea 5. El segundo encuentra también la marca introductoria.

Entrada: archivo congelado del prompt. Salida exacta de `prompt_sistema()[0]`:

```text
` y `
```

Son cinco caracteres. No llegan las preguntas, el diccionario ni los criterios. El hash del archivo coincide, por lo que verificarlo no detecta el fallo. `probar` tampoco comprueba el contenido del mensaje de sistema.

**Corrección sugerida:** extraer delimitadores que ocupen líneas completas, exigir un único bloque y comprobar el contenido efectivo enviado, además del hash del archivo.

### G2. La validación local no exige el esquema obligatorio

**Ubicación:** [cribado_llm.py:195–203](https://github.com/jaiborojas-cloud/leviathan/blob/baa6f061/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L195-L203).

**Estado: reproducido.** `interpretar` comprueba decision, razon y dudoso, pero no puntos.

Entrada:

```json
{"decision":"CONTEXTO","razon":"Sintética","dudoso":false}
```

Salida: respuesta aceptada. También acepta `"puntos":"INVALID"` y `"puntos":["99"]`. Según el esquema congelado deberían quedar INVALIDA. Esto puede hacer pasar probar y reducir artificialmente la tasa de inválidas, alterando la elección o las compuertas.

**Corrección sugerida:** validar localmente todos los requisitos del esquema. Pedir structured output a Ollama no sustituye esa validación.

### G3. Reanudación y evaluación aceptan resultados de otra configuración o simulación

**Ubicación:** [cribado_llm.py:210–226](https://github.com/jaiborojas-cloud/leviathan/blob/baa6f061/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L210-L226), [264–296](https://github.com/jaiborojas-cloud/leviathan/blob/baa6f061/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L264-L296) y [326–344](https://github.com/jaiborojas-cloud/leviathan/blob/baa6f061/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L326-L344).

**Estado: reproducido.** Para reanudar basta encontrar obra_id. Para evaluar bastan el nombre del archivo y algunos campos. No se exige coincidencia de configuración, modelo, prompt u opciones; tampoco se registra una marca inequívoca de simulación.

Caso: una fila sintética en `salida_validacion_C1.jsonl` contiene `config="C4"`, modelo y hash de prompt incorrectos. Al reanudar C1 se omite como ya realizada; validar emite APTO. También se obtuvo APTO con una salida íntegramente generada con `--simular`.

Esto demuestra una contaminación posible, **no un resultado del piloto real**. verificar imprime metadatos pero no rechaza incompatibilidades.

**Corrección sugerida:** vincular cada fila a una ejecución, entrada, prompt, script, modelo y configuración verificados; distinguir simulaciones y rechazarlas en el veredicto oficial.

### G4. Una corrida incompleta puede dejar disponible un APTO anterior

**Ubicación:** [cribado_llm.py:299–344](https://github.com/jaiborojas-cloud/leviathan/blob/baa6f061/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L299-L344).

**Estado: reproducido.** Con archivo presente pero filas faltantes, validar produce INCONCLUSIVO correctamente. Si falta todo el archivo, sale antes de escribir el estado. En selección sucede algo equivalente cuando falta una configuración o alguna obra.

Caso sintético: existe `veredicto.json` con APTO y falta `salida_validacion_C1.jsonl` → se informa «Falta…», pero el archivo de veredicto continúa diciendo APTO.

**Corrección sugerida:** registrar el estado del intento actual, con identificador de ejecución y conservación del historial; evitar que un resultado anterior pueda confundirse con el actual.

### G5. Los fallos de comandos nativos no detienen sistemáticamente el ciclo Azure

**Ubicación:** [cribado_llm_azure.ps1:78–89](https://github.com/jaiborojas-cloud/leviathan/blob/baa6f061/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm_azure.ps1#L78-L89) y [160–166](https://github.com/jaiborojas-cloud/leviathan/blob/baa6f061/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm_azure.ps1#L160-L166).

**Estado: semántica reproducida localmente; Azure no ejecutado.** ErrorActionPreference=Stop no convierte por sí solo todo código nativo distinto de cero en excepción. Se comprueba LASTEXITCODE en los envoltorios de ssh y scp, pero no en az ni en el ssh de bajar.

Caso: falla `az vm auto-shutdown` → puede anunciarse que la VM tiene apagado programado aunque no exista. Si falla el ssh que recoge hashes, puede escribirse información vacía o parcial y anunciar éxito.

Con un proceso local que terminó con código 9, PowerShell continuó pese a ErrorActionPreference=Stop y con PSNativeCommandUseErrorActionPreference=false, valor predeterminado documentado. [Documentación oficial](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_preference_variables#psnativecommanduseerroractionpreference).

**Corrección sugerida:** comprobar explícitamente cada código nativo y no anunciar éxito hasta verificar la operación.

### G6. El apagado diario no implementa seis horas acumuladas

**Ubicación:** [cribado_llm_azure.ps1:87–88](https://github.com/jaiborojas-cloud/leviathan/blob/baa6f061/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm_azure.ps1#L87-L88) y línea 142.

**Estado: revisión estática y documentación oficial.** auto-shutdown --time HHmm fija una hora diaria; lanzar vuelve a arrancar sin comprobar presupuesto acumulado.

Caso: creación a las 10:00 UTC → apagado a las 16:00; reanudación a las 17:00 → siguiente apagado al día siguiente a las 16:00. No existe control que cierre el piloto como INCONCLUSIVO al agotar seis horas. [Semántica oficial de --time](https://learn.microsoft.com/en-us/cli/azure/vm#az-vm-auto-shutdown).

**Corrección sugerida:** definir y controlar el presupuesto temporal del piloto entre reinicios, distinguiéndolo de la programación diaria.

## Hallazgos menores y casos borde

### M1. Clasificación incompleta de errores y ambigüedad de reintentos

[cribado_llm.py:179–192](https://github.com/jaiborojas-cloud/leviathan/blob/baa6f061/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L179-L192). Un URLError cuyo reason sea TimeoutError cae en «sin conexión», no en timeout que termina como INVALIDA. Un cuerpo HTTP no JSON también cae en infraestructura genérica. Son observaciones estáticas, sin llamadas de red. Python puede envolver errores de timeout en URLError: [CPython](https://github.com/python/cpython/blob/3.12/Lib/urllib/request.py).

Caso: tres URLError(TimeoutError(...)) → detención sin fila, no INVALIDA. Además, son tres intentos totales, no un intento inicial más tres reintentos; conviene precisar el texto.

### M2. El extractor descarta resúmenes cortos y depende de la estructura

[cribado_llm.py:78–93](https://github.com/jaiborojas-cloud/leviathan/blob/baa6f061/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L78-L93). Reproducido con evidencia inventada: `abstract="A short abstract."` → ningún resumen por el umbral no preregistrado len(a)>20. Una estructura con obra_id en el padre y records con abstract en hijos sin repetir el ID pierde esos resúmenes.

**No se afirma que los paquetes reales tengan esa estructura.** Su compatibilidad efectiva no se verificó porque abrirlos estaba prohibido. Debe verificarse contra fixtures representativos y reglas explícitas, sin inferir éxito a partir de esta auditoría.

### M3. Mediana incorrecta para tamaño par

[cribado_llm.py:284](https://github.com/jaiborojas-cloud/leviathan/blob/baa6f061/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L284). Caso: tiempos [1,100] → 100 en lugar de 50.5. No afecta al desempate de la selección congelada completa, de 79 obras; sí al uso general de la función.

### M4. Lanzar puede anunciar una fase que no arrancó

[cribado_llm_azure.ps1:149–151](https://github.com/jaiborojas-cloud/leviathan/blob/baa6f061/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm_azure.ps1#L149-L151). Si existe cualquier sesión q15, has-session tiene éxito y no se ejecuta el comando nuevo.

Caso: selección aún activa + solicitud de validación → se anuncia validación corriendo, aunque sigue selección. El pipeline con tee tampoco conserva explícitamente el código fallido del etiquetador. Revisión estática; no se ejecutó tmux real.

### M5. Integridad parcialmente manual

[README.md, paso 2](https://github.com/jaiborojas-cloud/leviathan/blob/baa6f061/docs/research-notes/Q15/ejecucion/cribado_llm/README.md) y [cribado_llm_azure.ps1:128–129](https://github.com/jaiborojas-cloud/leviathan/blob/baa6f061/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm_azure.ps1#L128-L129), línea 165.

Las entradas se verifican antes de subir; elegir y validar no verifican el hash congelado de referencia.jsonl. bajar registra hashes remotos sin compararlos automáticamente con los descargados.

Caso: referencia local modificada después de la comparación manual → evaluación con etiquetas distintas sin rechazo automático. Es una debilidad de control, no evidencia de que haya ocurrido ni una negación del paso manual explícito del README.

## Límites del diseño, aun corrigiendo el código

### D1. Las compuertas permiten eliminar todo CONTEXTO

[Preregistro:63–70](https://github.com/jaiborojas-cloud/leviathan/blob/baa6f061/docs/research-notes/Q15/ejecucion/cribado_llm/PREREGISTRO_CRIBADO_LLM.md#L63-L70).

Caso sintético con los conteos congelados: 24 inclusiones correctas, 48 exclusiones correctas y las tres obras CONTEXTO excluidas → sensibilidad 1, acuerdo 0.96 y cero inválidas. Pasan las tres compuertas. El código cumple el diseño; APTO no garantiza preservar esta clase.

### D2. La referencia no es una muestra aleatoria de las 2 998 pendientes

[Preregistro:10–31](https://github.com/jaiborojas-cloud/leviathan/blob/baa6f061/docs/research-notes/Q15/ejecucion/cribado_llm/PREREGISTRO_CRIBADO_LLM.md#L10-L31).

Partir aleatoriamente los primeros lotes evita parte del sobreajuste entre mitades, pero no elimina el sesgo del conjunto inicial. Caso: una familia conceptual aparece solo en obras posteriores → el piloto puede aprobar y fallar sistemáticamente en esa familia. La referencia de IA y la posible afinidad entre familias de modelos están reconocidas correctamente.

### D3. Potencia limitada para detectar omisiones

[Preregistro:70–81](https://github.com/jaiborojas-cloud/leviathan/blob/baa6f061/docs/research-notes/Q15/ejecucion/cribado_llm/PREREGISTRO_CRIBADO_LLM.md#L70-L81).

Bajo un supuesto binomial independiente, una tasa de omisión real del 10 % tiene probabilidad 0.9^24 = 0.07977 de producir cero omisiones entre 24 inclusiones. Con 5 % de errores entre exclusiones, una muestra de 50 tiene probabilidad 0.95^50 + 50·0.05·0.95^49 = 0.27943 de encontrar cero o uno y no suspender el uso.

Son cálculos ilustrativos del diseño, no estimaciones del corpus. Duplicados y heterogeneidad pueden debilitar los supuestos. El preregistro reconoce la limitación de 24; APTO debe interpretarse dentro de ella.

## Aspectos correctos y límites de verificación

- Los hashes del script, prompt, PowerShell y partición recuperados del commit coinciden con los declarados (tabla abajo).
- Las secciones 1 y 6 están copiadas literalmente en el archivo del prompt. Los dos criterios del responsable están presentes sin los ejemplos etiquetados de las decisiones. El defecto G1 está en extraer el bloque.
- La agrupación por título normalizado, estrato conservador, semilla y alternancia corresponde al algoritmo descrito. No se reprodujo la partición real desde los paquetes.
- En el recorrido previsto no se encontró transferencia de referencia a la VM: se suben código, prompt y entrada sin etiquetas. Esto es una verificación del código, no una inspección de una VM existente.
- elegir filtra selección y validar filtra validación. Las configuraciones fuera de probar.validas se reportan como no evaluadas. El límite de inválidas y el orden principal de elección están implementados.
- Recuperar una última línea JSON truncada funcionó con datos sintéticos: se separa la línea dañada y se vuelve a generar la obra.
- La ubicación de format, think y options en /api/chat corresponde a la [API documentada de Ollama](https://docs.ollama.com/api/chat). La compatibilidad concreta de modelos y versión no fue verificada; debe comprobarse con el entorno real autorizado.
- PowerShell no presentó errores de sintaxis en 7.6.9. Las cadenas inspeccionadas de lanzamiento y rutas scp se construyen como se espera. No se certificó transporte SSH/SCP, compatibilidad con otras versiones de PowerShell ni ejecución remota.
- Incluir ante duda es compatible con las reglas de producción; la cola de exclusiones dudosas es una protección adicional. No se encontró una contradicción normativa necesaria entre ambas reglas.
- No se certificó la extracción de paquetes reales, los modelos, drivers, capacidad GPU ni el ciclo efectivo de Azure.

| Archivo | SHA-256 verificado |
|---|---|
| cribado_llm.py | a7d9a718af41966587cdd04944d5b5fa0e751c1eb3a53bf7833c66edd047fb40 |
| PROMPT_CRIBADO_LLM.md | 0d102764a522b0d09cbfd60fbc0d1fff375a99c40d254b52dafa9592a9d593f0 |
| cribado_llm_azure.ps1 | 38dbb19616089d3af0e0ebe0f77469c21d7bff2d2104f2ceef6cc4001009c30f |
| particion.json | 2598b7dc6a03026d55e0e7b45b4644035132ea50bb857d62920d512052fddc20 |

## Evidencia sintética y entrega al siguiente agente

El arnés y los resultados están junto a este informe: [pruebas_sinteticas.py](pruebas_sinteticas.py) y [resultados_sinteticos.json](resultados_sinteticos.json). Si se comparte solo este Markdown, los casos reproducibles esenciales ya están descritos arriba; compartir también esos dos archivos permite inspeccionar el arnés.

Prioridad sugerida para la respuesta a la auditoría: G1, G2 y G3 antes de cualquier llamada a modelos; luego estados de ejecución e integridad, control de errores nativos y presupuesto de reanudación. Conservar el diseño congelado y registrar las correcciones o enmiendas según corresponda. Esta auditoría no autoriza cambios, ejecución de producción ni publicación.
