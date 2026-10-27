# DIN-Q13 — productor portátil r2 publicado, sin entrenamiento de cohorte

**PASS en Linux con spawn y python -I. No se ejecutó Windows.** Se entrega el
productor para que el responsable ejecute compuerta y prueba corta en su equipo.
No se inicializó ni entrenó ningún modelo de cohorte en este entorno. La prueba
`--parte cohorte --limite 15` sólo se documenta, no se ejecuta aquí.

Plan publicado 0135813 antes del primer código 2ed9090. R1 se preserva por SHA en
validacion_portable_v2/r1. La enmienda 9e98119 se congeló antes de corregir su cola;
r2 se publicó en a2557a6 antes de sus reconstrucciones y pruebas de IO.

- Ambas fuentes embebidas coinciden byte por byte con recipe_v1.py/support_v1.py.
- Tres reconstrucciones **sin entrenar** en r2: error relativo M=0 y f idéntica.
  Tres controles anteriores r1 también se conservan, sin sustituirlos.
- El ejecutor falso recorre 12.000 IDs una vez, con un máximo de12 tareas en
  vuelo. Ante interrupción, sólo envía12 y no repone ninguna; no llama al worker
  científico. Reanudar omite éxitos, fallos, JSON truncados y reclamos interrumpidos.
- Carrera de dos escrituras: sólo una obtiene el archivo, nunca lo sobreescribe.
  Bloqueo simultáneo rechazado; SHA del plan incorrecto rechazado antes de modelos.
- CLI aislada `--limite 0`: cero entrenamiento, sin arranque de workers de cohorte.
- Tabla de fixture: las 12.000 filas, orden exacto y 15 columnas; ausentes/fallidas
  siguen presentes. Copia de valores y vínculos SHA correctos. Reexportar la misma
  tabla no cambia sus bytes; publicar impide nuevos entrenamientos en esa carpeta.

Las tablas y registros de fixture **no son cohorte ni evidencia científica** y
permanecen en la carpeta externa de validación; no se publican como datos Q13.
Los logs archivados se identifican como pruebas. La compuerta Linux archivada
tampoco reemplaza COMPUERTA_q13.json que generará el equipo Windows.

Un intento de preflight usó por error el Python base sin torch y abortó antes
de modelos. Se conservó el registro operacional y se repitió con el venv correcto;
no fue un defecto de la receta. No se cambió ningún diseño, semilla, dosis,
instrumento, calibración o resultado previo. Sin asociaciones ni análisis Q13.

[Resultados r2](validacion_portable_v2/r2/verification.json) ·
[prueba de cola](validacion_portable_v2/r2/scheduler_tests.json) ·
[enmienda previa](ENMIENDA_PORTABLE_r2_CONGELADA.md) ·
[comandos Windows](EJECUCION_WINDOWS_v2.md) · [SHA](PUBLICACION_PRODUCTOR_v2.sha256).
