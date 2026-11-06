# Revisión acotada de la enmienda 4 — Q15

Fecha: 2026-11-06, America/Mexico_City. Auditor: Codex (IA). Rango revisado: aaa6a255..a804906f, rama docs/q15-protocolo-sistematico-v1 de jaiborojas-cloud/leviathan. Alcance exclusivo: cambios de docs/research-notes/Q15/ejecucion/cribado_llm/; no se reabren puntos ajenos al diff.

**Resultado:** N1 y N2 resueltos; N4 corregido por inspección del código generado, sin certificación independiente de Bash real; N3 atendido en el camino exitoso, con un residuo menor de trazabilidad en estados INCONCLUSIVO. No encontré un error grave nuevo en este cambio. No es un veredicto APTO del modelo ni una autorización ejecutada de producción.

## Lecturas y restricciones

Se leyó AGENTS.md y la sección Tercera auditoría de RESPUESTA_AUDITORIA_CODEX.md. Se compararon las versiones locales verificadas de Python, PowerShell y preregistro en ambos commits, y se revisó la ampliación de pruebas. La comparación remota contiene dos commits; se respetó ese rango.

No se modificó el repositorio ni hubo commit, push o comentarios. No se abrieron paquetes reales, no se escribió en D:\\RIPG_DATA y no se utilizaron modelos ni Azure. Se trabajó con copias externas y datos inventados en carpetas temporales.

## Hallazgos solicitados

| Hallazgo | Estado | Archivo, línea y caso |
|---|---|---|
| N1: presupuesto/fechas inválidos | Resuelto | [cribado_llm.py:60](https://github.com/jaiborojas-cloud/leviathan/blob/a804906f/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L60), [cribado_llm.py:381](https://github.com/jaiborojas-cloud/leviathan/blob/a804906f/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L381) y [cribado_llm.py:413](https://github.com/jaiborojas-cloud/leviathan/blob/a804906f/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L413). limite_utc=null y hora 2026-00-00T99:99:99Z producen INCONCLUSIVO. La suite comprueba ventanas de 48 h, límite desplazado una hora y filas anteriores al inicio. --hasta inválido se rechaza; ya no se compara lexicográficamente. |
| N2: tiempos negativos/no finitos | Resuelto | [cribado_llm.py:431](https://github.com/jaiborojas-cloud/leviathan/blob/a804906f/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L431)–433; medición monotónica en 268 y 341. segundos=-1 o NaN producen INCONCLUSIVO. El caso de empate que antes pasaba de C1 a C2 al poner -1 en C2 ahora termina INCONCLUSIVO y no elige configuración. |
| N3: descartes silenciosos | Parcial, residuo menor | [cribado_llm.py:286](https://github.com/jaiborojas-cloud/leviathan/blob/a804906f/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L286)–304 y [cribado_llm.py:458](https://github.com/jaiborojas-cloud/leviathan/blob/a804906f/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L458). Una línea basura junto a todas las obras completas queda en metricas.lineas_descartadas con número, bytes, hash y motivo. Cuando falta una obra, el detalle no llega al estado; véase abajo. |
| N4: código final de correr.sh | Corregido en el código generado; ejecución real no certificada | [cribado_llm_azure.ps1:187](https://github.com/jaiborojas-cloud/leviathan/blob/a804906f/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm_azure.ps1#L187)–190. El archivo capturado contiene rc=$?, echo con codigo=$rc y exit $rc. Para un pipeline que termina con 7, la semántica del código propaga 7, en vez del cero del echo. Es revisión estática y de generación mediante mocks, no una prueba Bash independiente. |

## Única observación menor pendiente

**Se pierde el detalle de descartes al emitir INCONCLUSIVO por obras faltantes.**

Ubicación: [cribado_llm.py:408](https://github.com/jaiborojas-cloud/leviathan/blob/a804906f/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L408) y [cribado_llm.py:440](https://github.com/jaiborojas-cloud/leviathan/blob/a804906f/docs/research-notes/Q15/ejecucion/cribado_llm/cribado_llm.py#L440)–443; manejo del estado de validar en su except.

Caso reproducido: la salida contiene únicamente una línea {garbage} y se espera la obra X. lineas_json construye correctamente un registro con línea 1, SHA-256 y JSONDecodeError. Después leer_salida_oficial lanza Inconclusivo por la obra ausente antes de devolver descartadas. El estado final contiene INCONCLUSIVO y «faltan 1 obras: X», pero no contiene lineas_descartadas.

El veredicto es correcto y conservador; no hay aceptación falsa ni pérdida de la salida original. Es una omisión de trazabilidad frente a la nueva promesa del preregistro de registrar los descartes en el estado. Lo mismo puede ocurrir si otra validación lanza una excepción antes del retorno. Propagar descartadas con el error o conservarlas en un registro de diagnóstico resolvería este residuo, sin cambiar decisiones o compuertas.

No lo clasifico como bloqueo científico nuevo. N3 queda cerrado para el caso exitoso probado por Claude, pero no completamente para estados fallidos.

## Pruebas ejecutadas

1. **Suite original de Claude: 64 comprobaciones pasan**, código de salida 0. El archivo fuente no fue modificado. Se reutilizó el adaptador HTTP en memoria: ejecuta el manejador ficticio de la suite sobre buffers, sin sockets ni modelos. La suite utiliza internamente simular=False contra ese imitador; no se presenta como una llamada a Ollama ni como prueba HTTP real.
2. **Arnés independiente actualizado al cambio de interfaz:** presupuesto sintético de exactamente 24 horas y adaptación de lineas_json/metricas a sus nuevos retornos. Etiquetado mediante simular=True, red bloqueada y fixtures inventados para evaluar metadatos. Código de salida 0. Reproduce N1/N2 resueltos, reporte de cola UTF-8 dañada y la observación menor de N3.
3. **Arnés PowerShell:** az, ssh y scp sustituidos por funciones locales. Captura el correr.sh de esta versión, incluidos rc y exit; comprueba error nativo, sesión activa, presupuesto vencido y hash de descarga incorrecto. No se ejecutó Azure ni transporte remoto.

El entorno no ha permitido ejecutar Bash local en estas auditorías. No volví a convertir ese límite en una afirmación de ejecución: la prueba Bash de código 7 declarada por Claude sigue siendo del autor, no una comprobación independiente mía. La enmienda lo declara correctamente.

## Coherencia del cambio y hashes

No observé cambios nuevos en prompt, configuración de modelos, partición, compuertas o regla de elección. La sustitución por time.monotonic no cambia el criterio de tiempo, sino su medición. La lectura estricta de constantes JSON se integra con el registro de descartes y las obras faltantes no se consideran completas. La nueva firma de retorno de lineas_json está adaptada en sus consumidores del script.

Los hashes recalculados coinciden con el preregistro:

| Archivo | SHA-256 |
|---|---|
| cribado_llm.py | d9288eaba8fcc94aa34cb07eb489cbf804cec0dc0ca4a0445720405bf8d29475 |
| pruebas_sinteticas.py | 66ac98f8140c79b1e5b3233902d84563eccd3d628c14156ba1d49144d9be0342 |
| cribado_llm_azure.ps1 | 5944fe0ae99279aec8b84a0e7d39ac56c29ad53978812788106b6eebb264531a |

No se certifican modelos, Azure, paquetes reales, ni el comportamiento de la VM. La conclusión se limita al diff revisado y a las pruebas sintéticas descritas.

## Evidencia adjunta

- [Suite original](pruebas_sinteticas.py), [adaptador sin red](ejecutar_suite_sin_red.py), [log de 64 comprobaciones](suite.log).
- [Arnés independiente](arnes_independiente.py), [resultados](resultados_independientes.json), [log](independiente.log).
- [Arnés PowerShell](arnes_powershell.ps1), [resultados](resultados_powershell.json), [log](powershell.log), [correr.sh capturado](correr_generado.sh).

Las salidas APTO de los fixtures son pruebas de software sobre datos inventados. El correr.sh adjunto es evidencia de generación con mocks y no debe utilizarse para ejecutar una corrida real.

