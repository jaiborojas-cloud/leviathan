# Reanudación exacta de la integración

Se perdió el proceso previo: una visita terminada conservada; tres checkpoints futuros y campos recuperados, sin repetir entrenamiento. El coste de integración perdido no puede reconstruirse exactamente.

Cambio únicamente operacional: serializar DOP853 tras pasos aceptados, conservando salida densa, historial, paso adaptativo y contadores. Mismos 2048 rayos, radio de búsqueda inicial 0.09, DOP853 rtol2e-10/atol2e-12 y secuencia de calibración. El límite de 128 pasos nuevos es una pausa de cómputo, no tolerancia, exclusión o fallo geométrico.

La prueba inicial detectó pérdida de alias entre K y K_extended al serializar. Se restauró exactamente la vista definida por SciPy antes de reanudar. La versión corregida reproduce bit a bit tiempos, estados y salida densa en 513 radios, con idéntico nfev, después de una pausa. Las versiones fallidas nunca se usaron en estados futuros. Ver resumable_dop853_validation.json.

Reanudar solo continue_first_pending_geometry.py tras restaurar los ZIP ODE según ode_resume_index.json y verificar hashes; no ejecutar en paralelo con otro proceso de la misma visita. No ejecutar followup_bounded_verified.py sobre esta calibración, porque no carga los checkpoints internos del integrador. Los otros dos estados pendientes se conservan; no se sustituyen ni clasifican.
