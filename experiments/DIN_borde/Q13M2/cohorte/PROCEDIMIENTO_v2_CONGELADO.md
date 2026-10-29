# DIN-Q13-M2: preparación del productor para la cohorte v2

2026-10-28, hora de México. Se aplica el diseño v2 congelado SHA `5c6c238e…`, analista `190e3e87…`, main posterior a #119. Solo añadir en `Q13M2/cohorte/`; no modificar diseño, analista, instrumentos, calibración, potencia ni etapas previas. Papel de productor: no calcular D, p o asociaciones ni ejecutar el analista sobre cohortes reales.

## Orden autorizado

1. Verificar por AST/diff la correspondencia de potencia N320 (`2e69516e…`) con el analista congelado. Las funciones del estimando, llamada primaria, constantes, bootstrap y clasificación deben coincidir para entradas no degeneradas. Distinguir cambios de errores/salida/traza de cambios científicos. Si el estimando difiere, detener la preparación y documentar antes de repetir la potencia simulada; nunca usar una cohorte real para ello.
2. Plan fijo:320 splits ×5 inicializaciones ×11 niveles,17.600 IDs. Niveles/dosis exactamente los del diseño/analista; universo nivel→split→k. Publicar el plan y su SHA en un commit enviado al remoto **antes del código del productor**.
3. Adaptar el productor Q13-DR `cohorte_v3.py` por SHA. Receta/soporte Q13 y adaptador LP de la calibración, embebidos byte a byte y verificados contra originales. A0/WD delegan la receta intacta; LP ejecuta el mismo cuerpo `update_m2`, con `original_update` enlazada a la receta original. Solo cambian brazo/dosis y semillas911000/921000/931000, pareadas. Orden de envío split→k→nivel; orden de tabla nivel→split→k. Visitas5/10/30/250.
4. Verificación de SHA al arrancar: plan, diseño, analista como archivo (sin importarlo), core, geometry, rho r3, receta, soporte y adaptador LP; cuatro versiones exactas. `python -I`, pathlib, spawn, sin red al ejecutar. Reanudación exclusiva, registros y errores por ID, vínculo plan/script/versiones; no sustituir fallos ni claims interrumpidos. Progreso cada500.
5. Validar sin entrenar cohorte: sintaxis, identidad de fuentes/AST, universo, programación/limitación/reanudación, exclusión de escrituras, fallos y tabla usando registros artificiales claramente separados fuera de Git. Compuerta Linux con3 reconstrucciones desde pesos sintéticos sin pasos de optimización. No ejecutar `--parte cohorte` aquí, ni la prueba33, ni un análisis. LP se verifica por código idéntico y espías sin entrenamiento.
6. Publicar productor por SHA; instrucciones PowerShell posteriores fijarán ese commit de ejecución, evitando un hash circular en el propio archivo. Venv `D:\RIPG_DATA\venv_q13`, clon `D:\leviathan-q13`, autocrlf=false, salida `D:\RIPG_DATA\DIN_Q13M2_v2`. Compuerta Windows→prueba33→tres invocaciones con límite5900→tabla. Los33 cuentan dentro del universo y no se repiten. El último límite ejecuta solo los pendientes.

## Conservación y límites

Diseño/plan antes del productor; código de validación antes de ejecutarlo. Guardar fallos y versiones; si se necesita corregir un defecto de implementación después de ejecutar, enmienda comprometida antes del cambio y resultados nuevos sin sobrescribir. Arrays/checkpoints/fixtures fuera de Git; manifest, verification.json, requisitos exactos y PR en borrador sin fusión. Esta entrega no contiene cohorte medida ni tabla final real: las produce el responsable en Windows.

El resumen final de Windows contiene exactamente tabla_sha256, plan_sha256, script_sha256. La tabla tiene todas las filas planificadas, incluidas faltantes/fallidas con error. Publicarla cierra esa carpeta a más entrenamiento. No mezclar salidas de otros protocolos, versiones o scripts.
