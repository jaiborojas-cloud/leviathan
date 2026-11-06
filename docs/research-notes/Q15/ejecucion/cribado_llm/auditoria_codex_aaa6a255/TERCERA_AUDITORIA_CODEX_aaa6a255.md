# Tercera auditoría independiente Q15 — enmienda 3

Fecha: 2026-11-06 (America/Mexico_City). Auditor: Codex, IA. Commit auditado: aaa6a255, rama docs/q15-protocolo-sistematico-v1, repositorio jaiborojas-cloud/leviathan.

**Dictamen: las reproducciones originales de R1–R4 y los seis menores están atendidas; R5 está corregido en el código inspeccionado y en la prueba de --hasta, con ejecución Bash real no certificada. No recomiendo cerrar todavía la auditoría sin corregir los controles de presupuesto y duración descritos en N1–N2.** Estos son casos con metadatos inválidos: no se afirma que el flujo normal haya producido esos archivos ni que haya ocurrido una corrida real.

## Alcance, restricciones y pruebas

Se leyó AGENTS.md del commit, la sección Reauditoría de d580da24 de RESPUESTA_AUDITORIA_CODEX.md y el preregistro, incluido Historial. Se revisaron el Python completo, PowerShell, prompt, partición, README y suite nueva. No se modificó el repo; no hubo commit, push ni comentarios. No se abrieron paquetes reales, no se escribió en D:\\RIPG_DATA y no se llamó a modelos ni Azure.

Se trabajó con copias externas y datos inventados en carpetas temporales. El arnés propio etiqueta con simular=True; usa fixtures sintéticos para comprobar el evaluador oficial y bloquea la red. Las salidas APTO de las pruebas son resultados de software sobre datos inventados, nunca aprobación de un modelo.

- **Suite de Claude: 52 comprobaciones pasan**, exit code 0. Se ejecutó el archivo sin modificar mediante el adaptador de transporte en memoria usado en la reauditoría anterior. La suite original utiliza simular=False para su imitador HTTP; el adaptador ejecuta ese mismo manejador sobre buffers, sin sockets ni modelos. No se afirma que se haya ejecutado con HTTP real.
- **Arnés independiente:** reproducciones anteriores y nuevos casos de presupuesto, calendario, duración, líneas corruptas y --hasta. Exit code 0; resultados detallados adjuntos.
- **PowerShell 7.6.9:** análisis sintáctico sin errores; az/ssh/scp sustituidos por funciones locales. Se comprobó error nativo, sesión activa, presupuesto vencido, descarga corrupta y se capturó el correr.sh realmente generado por lanzar.
- **Bash real no verificado:** el intento de arrancar Git Bash local falló con NtCreateDirectoryObject / 0xC0000022 por el sandbox. No se ejecutaron tmux, timeout ni el shell de instalación reales. Los resultados de Claude sobre Bash se consideran declaración del autor, no verificación independiente propia.

Hashes recuperados y recalculados:

| Archivo | SHA-256 |
|---|---|
| cribado_llm.py | a2825a37f2aae5897cfcf74d120844d26dff1e5ca8c3bb05dbf34195ab090afa |
| cribado_llm_azure.ps1 | ab2f9c437fe32429c76f9c0439d1ff8f956e2adfc1aecf0b3a0ea2ce2415db39 |
| pruebas_sinteticas.py | e1d3e54be8422aa8de123397b8c01894eddeb11310177e3044c07bd190585052 |

## Estado de los hallazgos solicitados

| Hallazgo | Estado y ubicación | Caso comprobatorio |
|---|---|---|
| R1: firma y coherencia | Resuelto para los casos originales. [cribado_llm.py:368](https://github.com/jaiborojas-cloud/leviathan/blob/aaa6a255/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L368)–399. | Hash de script desconocido, modelo distinto, crudo no JSON, decisión incoherente y obra duplicada producen INCONCLUSIVO. Se compara con el hash del script que evalúa, cuya copia aquí fue verificada contra el congelado. |
| R2: JSON roto deja APTO | Resuelto. [cribado_llm.py:452](https://github.com/jaiborojas-cloud/leviathan/blob/aaa6a255/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L452)–469; elegir:425–441. | APTO sintético previo y eleccion.json con un solo carácter { → INCONCLUSIVO vigente con JSONDecodeError. |
| R3: colisión del historial | Resuelto para la colisión reportada. [cribado_llm.py:60](https://github.com/jaiborojas-cloud/leviathan/blob/aaa6a255/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L60)–75. | Dos intentos con el reloj fijo en el mismo segundo → dos archivos históricos distintos, uno APTO y otro INCONCLUSIVO. El vigente se reemplaza mediante os.replace. |
| R4: UTF-8 cortado | Resuelto para la recuperación reportada. [cribado_llm.py:265](https://github.com/jaiborojas-cloud/leviathan/blob/aaa6a255/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L265)–275 y 297–304. | Cola terminada en byte 0xC3 → lectura en bytes sin UnicodeDecodeError y reanudación. La suite comprueba además que se rehace la obra incompleta. |
| R5: timeout anterior al arranque | Corregido en código; prueba Bash real pendiente. [cribado_llm_azure.ps1:173](https://github.com/jaiborojas-cloud/leviathan/blob/aaa6a255/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm_azure.ps1#L173)–193 y [cribado_llm.py:310](https://github.com/jaiborojas-cloud/leviathan/blob/aaa6a255/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L310). | correr.sh calcula LIMITE - date +%s en la VM, después de las copias. --hasta vencido en el arnés propio se detiene con cero filas. Véase N1 sobre entradas temporales inválidas. |
| Menor 1: desempate | Resuelto. [cribado_llm.py:444](https://github.com/jaiborojas-cloud/leviathan/blob/aaa6a255/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L444). | validas=[C2,C1] y métricas/tiempos iguales → C1. |
| Menor 2: guion bajo | Resuelto. [cribado_llm.py:83](https://github.com/jaiborojas-cloud/leviathan/blob/aaa6a255/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L83)–85. | tiene_texto('___') es false; letras como ñ siguen contando. |
| Menor 3: esquema enviado | Claves extra resueltas; razón vacía cubierta localmente. [cribado_llm.py:30](https://github.com/jaiborojas-cloud/leviathan/blob/aaa6a255/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L30)–39 y 228–239. | additionalProperties es false y el intérprete rechaza razón vacía. No se añadió minLength; es una decisión explícita del autor, no una ausencia de validación local. No se certificó soporte de gramática Ollama. |
| Menor 4: tipos | Resuelto en firmas. [cribado_llm.py:278](https://github.com/jaiborojas-cloud/leviathan/blob/aaa6a255/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L278) y 372. | think=0/simulado=0 → INCONCLUSIVO; ya no se confunden con false. |
| Menor 5: curl y pipefail | Código corregido; runtime no certificado. [cribado_llm_azure.ps1:116](https://github.com/jaiborojas-cloud/leviathan/blob/aaa6a255/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm_azure.ps1#L116)–117. | Se antepone set -o pipefail al pipeline curl/sh; bajo Bash, curl fallido deja estado no cero aunque sh termine bien. Revisión estática/documental, sin ejecutar instalación. |
| Menor 6: menos de 100 exclusiones | Resuelto en el diseño documental. [PREREGISTRO_CRIBADO_LLM.md:87](https://github.com/jaiborojas-cloud/leviathan/blob/aaa6a255/docs/research-notes/Q15/ejecucion/cribado_llm/PREREGISTRO_CRIBADO_LLM.md#L87). | Un lote con 40 exclusiones requiere censo de 40. Con más de 100, marco ordenado por obra_id y random.Random(20261106+número de lote).sample. No se ejecutó producción. |

## Hallazgos graves condicionados a metadatos inválidos

### N1. El evaluador puede emitir APTO sin un límite temporal válido

**Ubicación:** [cribado_llm.py:361](https://github.com/jaiborojas-cloud/leviathan/blob/aaa6a255/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L361)–378. El archivo presupuesto.json debe existir, pero su limite_utc no se valida como fecha obligatoria. La condición if limite desactiva el control cuando el valor es null o vacío. La hora de cada fila solo se verifica con una expresión regular, no con un calendario.

**Reproducido:** fixture completo y coherente que da APTO → cambiar únicamente limite_utc a null → validar sigue dando APTO. Otro caso: utc='2026-00-00T99:99:99Z' pasa el patrón y puede dar APTO.

**Impacto:** el veredicto oficial puede superar la compuerta temporal sin un presupuesto verificable. No se afirma que PowerShell genere null normalmente; el defecto es aceptar como oficial un insumo temporal inválido, cuando el preregistro exige INCONCLUSIVO ante fallos de integridad.

**Corrección sugerida:** analizar inicio, límite y horas de fila como fechas UTC reales; exigir límite no nulo, intervalo coherente y duración presupuestada. No usar la veracidad del valor para decidir si se aplica un requisito obligatorio.

**Caso relacionado, menor por estar protegido en el camino normal de PowerShell:** [cribado_llm.py:310](https://github.com/jaiborojas-cloud/leviathan/blob/aaa6a255/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L310) y 483 aceptan --hasta sin parsearlo. --hasta not-a-date permite escribir una fila simulada; --hasta 2000-01-01T00:00:00Z sí se detiene. El generador PowerShell suministra una fecha bien formada, pero la CLI debería rechazar valores inválidos.

### N2. Duraciones negativas o no finitas pueden cambiar la elección

**Ubicación:** [cribado_llm.py:389](https://github.com/jaiborojas-cloud/leviathan/blob/aaa6a255/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L389)–390, 412 y 444. La nueva comprobación acepta int/float, pero no exige finitud ni valor no negativo. Python json acepta NaN por defecto.

**Reproducido:** C1 y C2 tienen iguales sensibilidad, acuerdo e inválidas; segundos C1=1 y C2=2 → elige C1. Cambiar solo segundos de C2 a -1 → elige C2. Tanto una duración negativa como NaN se aceptaron en un archivo de validación y produjeron APTO en los fixtures.

**Impacto:** metadatos inválidos intervienen directamente en el desempate congelado; la configuración elegida puede cambiar sin cambiar las decisiones científicas. La etiqueta grave se refiere a ese efecto, no a evidencia de que se haya producido en una ejecución real. Además, las duraciones se obtienen con time.time, que no es un reloj monotónico.

**Corrección sugerida:** rechazar segundos negativos o no finitos como INCONCLUSIVO y medir intervalos con un reloj monotónico. Mantener el reloj UTC para la fecha de decisión y el presupuesto absoluto.

## Hallazgos menores nuevos y límites de los mecanismos nuevos

### N3. lineas_json ignora corrupción en cualquier posición sin informarla

[cribado_llm.py:265](https://github.com/jaiborojas-cloud/leviathan/blob/aaa6a255/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L265)–275. No distingue una cola de desalojo de una línea corrupta anterior; descarta ambas sin contador ni registro.

**Reproducido:** anteponer {garbage} seguido de LF a un archivo con todas las filas correctas → validar devuelve APTO. En esta prueba no cambió ninguna decisión, por eso no se presenta como una omisión demostrada. La recuperación de una cola rota está autorizada y funciona; falta visibilidad de qué se ignoró y por qué. Conviene registrar línea, hash y motivo, y diferenciar corrupción inesperada de restos documentados de reanudación. No basta con rechazar toda línea intermedia: una cola antigua cerrada al reanudar puede quedar legítimamente en medio.

### N4. correr.sh registra el fallo, pero devuelve éxito si el echo final funciona

[cribado_llm_azure.ps1:187](https://github.com/jaiborojas-cloud/leviathan/blob/aaa6a255/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm_azure.ps1#L187)–188, líneas 8–9 del correr.sh capturado. El pipeline tiene pipefail; el echo siguiente expande su $? y registra correctamente ese código. Después, el estado final del script es el del echo, normalmente cero.

**Caso estático:** primera configuración termina con código 7, tee funciona → log FIN seleccion codigo=7; correr.sh termina con 0 si el echo funciona. No cambia actualmente las compuertas Python y el preregistro exige registrar el código, por lo que se considera menor. Si un futuro orquestador usa el código del script, será engañoso. Guardar rc, escribirlo y exit rc conserva ambos canales. No se ejecutó Bash real para esta comprobación.

## Revisión específica de escribir y escribir_estado

La escritura vigente en temporal y os.replace evita publicar JSON a medio escribir durante el reemplazo. El identificador único y apertura x evitan la colisión reproducida. La prueba independiente dejó el valor nuevo completo y ningún temporal residual en una escritura exitosa.

No se confunde atomicidad del reemplazo con una transacción duradera entre histórico y vigente: el histórico se escribe primero y directamente, y no hay fsync. Una caída de proceso o disco durante esas escrituras no está cubierta por una prueba de persistencia. No se declara un nuevo bloqueo por esa posibilidad general ni se exige garantizar escrituras cuando el disco falla; simplemente el comentario «nunca» excede lo verificado. La reproducción original de colisión queda cerrada.

## Revisión específica de correr.sh y --hasta

El archivo capturado se genera con LF y Bash explícito. Lleva epoch absoluto, calcula restante en la VM, no ejecuta si quedan 60 s o menos, encadena configuraciones con &&, utiliza timeout y tee con pipefail, y pasa el mismo límite UTC a cada etiquetador. Esto corrige el desfase concreto de R5: el tiempo de arrancar/copiar ya no se suma a una duración calculada en la PC.

--hasta protege el inicio de obras, no cancela por sí solo una llamada en curso ni sus reintentos; el límite duro depende del timeout externo. No se presenta esa división como un fallo, porque está declarada. El timeout de GNU envía TERM por defecto; no se verificó su comportamiento sobre los procesos reales ni el servidor Ollama. [Documentación GNU timeout](https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html).

pipefail hace que el código del pipeline sea el último no cero; por ello el log puede reflejar un fallo de tee en vez del etiquetador si ambos fallan. Es comportamiento correcto de Bash, no necesariamente el código exclusivo de Python. [Documentación Bash](https://www.gnu.org/s/bash/manual/html_node/Pipelines.html).

## Revisión amplia: lo que está bien y lo no certificado

- Prompt, preguntas, criterios y opciones permanecen congelados. El mensaje efectivo conserva 8 954 caracteres y el hash esperado; no volvió el error de extracción.
- La partición conserva algoritmo y semilla; los duplicados sintéticos permanecen en una mitad. La suite prueba las estructuras de evidencia inventadas y correcciones del lote02. No se regeneró la partición real ni se certificó la estructura de los paquetes originales.
- No se observó envío de etiquetas por obra a la VM. Se suben código, prompt, partición con hashes/conteos y entrada sin referencia. El contenido de particion.json no se agrega al prompt del modelo. elegir usa selección; validar usa validación y la configuración elegida.
- R1 ahora compara la firma con el evaluador verificado, comprueba coherencia de la respuesta y rechaza duplicados o IDs ajenos. Se rechazan simulaciones en modo oficial. Las pruebas adversas anteriores ya no producen APTO.
- INVALIDA continúa contando como no exclusión y penaliza acuerdo/inválidas según el preregistro. NO_EVALUADAS quedan fuera de competencia. CONTEXTO está protegida. Las pruebas correspondientes pasan.
- Las llamadas a la API no cambiaron en su estructura fundamental. No se verificó compatibilidad real de modelos/etiquetas, formato estructurado, think, versión, memoria GPU o drivers. No hubo llamadas a modelos.
- La comprobación de códigos nativos y hashes de descarga permanece operativa en mocks. No se certificaron SSH/SCP ni Azure reales. El shell remoto de instalar debe soportar pipefail; correr.sh sí fuerza Bash.
- El refuerzo del muestreo de producción está explicitado, pero el piloto sigue basado en una referencia IA no aleatoria y pequeña. No se convierte APTO en garantía general ni en conclusión de novedad.

## Archivos de reproducción

- [Suite original de Claude](pruebas_sinteticas.py), sin editar.
- [Adaptador HTTP en memoria](ejecutar_suite_sin_red.py) y [log de 52 comprobaciones](suite_claude_sin_red.log).
- [Arnés independiente](arnes_independiente.py), [resultados JSON](resultados_independientes.json) y [log](arnes_independiente.log).
- [Arnés PowerShell](arnes_powershell.ps1), [resultados](resultados_powershell.json), [log](powershell.log) y [correr.sh capturado](correr_generado.sh).

El correr.sh adjunto es solo evidencia de una generación con mocks y fecha de prueba; no debe usarse para lanzar una corrida real. Todos los artefactos están fuera del repositorio.

