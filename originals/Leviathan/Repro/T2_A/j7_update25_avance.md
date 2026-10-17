# Leviathan / RIPG — avance recuperable j7/update25

Se retomó split8_j7_true/update25 desde su checkpoint y campo persistentes, sin repetir entrenamiento. Se ejecutó un lote de128 pasos aceptados de la calibración heredada; guardados32,64,96,128. Último radio integrado: **0.074554276173483244**; nfev=2534. CPU de integración: 102.118s.

Estado: **PAUSED_AT_PERSISTED_ACCEPTED_STEP** por presupuesto operacional del lote. La calibración aún no termina; no es radio nominal, no se ha clasificado topología y Y sigue desconocido. La pausa no demuestra fallo de dominio ni no inyectividad. No se extrapola a j7 el diagnóstico de j5.

Cuatro snapshots con SHA256 y CRC verificados. Checkpoint update25 y state.npz coinciden con el parcial original; seis archivos del sello intactos. visits.csv, outcomes.csv, cohorte y registro de incidencias intactos. Continúan1/8000 visitas cerradas y0/800 horizontes completos. J5 queda retenido en139; j6 no se repite; j8 y j9 no se abrieron.

Próxima tarea: **split8_j7_true/update25, paso aceptado129**, recuperando snapshot128 mediante ode_resume_split8_j7_update25.json. Recuperar j7_update25_recovery.zip y el ZIP referido por latest.archive, verificar hashes y restaurar en restore_archive_to/restore_metadata_to. No iniciar desde cero ni volver a entrenar. El pickle contiene solver, historia y salida densa; Driver restaura la vista K/K_extended validada. Preparar dependencias numpy2.3.5/scipy1.17.0/shapely2.1.2/cloudpickle3.1.2. Ajustar sólo rutas operativas y persistencia al nuevo entorno; execute_j7.py usa funciones científicas congeladas e imports limitados para no cargar entrenamiento/comparadores innecesarios.

Una vez completada la calibración faltará la auditoría topológica heredada antes de cerrar visita. No saltar a j8 como si j7 ya estuviera resuelto. No ejecutar el lanzador genérico que seleccionaría j5. El presupuesto128 es una pausa operacional, no cambio de tolerancias o evento.

Archivo de snapshot128: `ode_t025_split8_j7_true_f59408fcaa8eb0ab3c23_step_00000128.zip`.
SHA256: `5e9e138b557c41f302fe4457e5372ab71f726881de25032f7c4734ce19bc7b10`.
Índice y verificaciones: ode_resume_split8_j7_update25.json y j7_update25_verification.json.
