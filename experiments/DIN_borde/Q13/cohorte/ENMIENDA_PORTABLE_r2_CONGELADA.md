# DIN-Q13 portátil — enmienda r2 congelada antes de corregir

Se conserva r1, SHA 9ddc8fbca85cad0f7c0814e4fc3bce2d5f7913916046cd3316481b0e3a157c21,
en validacion_portable_v2/r1/cohorte_v2_r1.py.txt con sus pruebas. No se entrenó
ninguna trayectoria de cohorte, ni se ejecutó la prueba de 15.

Defecto de robustez identificado por revisión del flujo: r1 envía todo el universo
a ProcessPoolExecutor y su contexto usa shutdown(wait=True) al interrumpirse.
Cancelar el coordinador puede esperar a todas las tareas encoladas, perjudicando
la reanudación. No es un defecto de la receta ni del instrumento científico.

Corrección autorizada dentro de la tarea: mantener como máximo una tarea enviada
por worker, reponer sólo al completar otra y cancelar pendientes ante excepción.
No enviar nuevas tareas después de una interrupción. Los workers que ya estén
activos pueden finalizar; sus registros se conservan y no se repiten. Claims sin
registro final siguen convirtiéndose en fallos, sin reentrenar.

Antes de volver a publicar: contrastar con un ejecutor falso una interrupción
temprana (máximo procesos tareas enviadas, ninguna reposición tras el fallo), y
la secuencia normal (cada ID una vez, progreso cada500). Repetir compuerta spawn
sin entrenamiento y pruebas de IO en otra carpeta porque el SHA del script cambia.
No modificar diseño, dosis, semillas, instrumento, visitas, datos ni tolerancias.
