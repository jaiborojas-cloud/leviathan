# Validación del productor, sin entrenamiento

**PASS en Linux/Python3.12.14 con -I y spawn. Windows nativo no ejecutado.** El responsable debe generar su compuerta Windows; la copia Linux archivada es un control de instrumentación, no una cohorte ni sustituto de esa compuerta.

Tres modelos aleatorios sin entrenar: reconstruir M desde los pesos produce error relativo0 y f idéntica en los tres. Cero updates de entrenamiento y cero trayectorias de cohorte entrenadas; la CLI cohorte se invocó solo con limite0. [Compuerta](validacion/results_v1/COMPUERTA_linux_sin_entrenar.json), [verificación](validacion/results_v1/verification.json).

El ejecutor falso envía los6.000 IDs en el orden exacto split→k→nivel, sin llamar al worker científico. Ante un fallo temprano solo envía12 y no repone tareas. Se comprobó omisión de registros exitosos, fallidos y truncados; un claim interrumpido se registra como fallo y luego se omite. No se sustituyó ningún fallo.

La tabla de fixture tiene6.000 filas, orden de universo y15 columnas exactas; copia los valores y errores, conserva faltantes y es idempotente. La publicación bloquea nuevos entrenamientos. Dos escrituras concurrentes solo permiten una; el bloqueo simultáneo se rechaza. Todos estos archivos son fixtures operacionales fuera de Git, no datos experimentales.

Receta y soporte embebidos byte por byte. La función measure es idéntica por AST al productor Q13; rho r3, core y geometry permanecen intactos. Las únicas adaptaciones científicas del coordinador son las previstas: nivel→LS/dosis y semillas811000/821000/831000, pareadas entre6 niveles. Las nuevas semillas no colisionan con los rangos usados por G2/G3,C2 ni Q13.

Durante la preparación hubo un fallo de extracción AST en memoria antes de escribir el productor; se registra en [preparación](PREPARACION_PRODUCTOR.md). No hubo fallo del productor publicado ni cambios posteriores a sus mediciones. La etiqueta v2 inicial del docstring procede del padre; FORMAT y SHA vinculan inequívocamente la versión DRv3.
