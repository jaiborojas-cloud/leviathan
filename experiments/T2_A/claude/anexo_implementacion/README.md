# Implementación instrumentada del anexo operativo E1 v1.0

- `resumable_dop853_instrumentado.py`: copia modificada de `sources/resumable_dop853.py` (el original no se toca) con contador de intentos, topes de intentos y tiempo, alarma de progreso radial y presupuesto adicional, según `E1/ANEXO_OPERATIVO_E1_v1.0_CONGELADO.md`.
- `prueba_driver_instrumentado.py`: pruebas con EDO de juguete (sin geometría ni torch). Resultado en el contenedor (scipy 1.18.1, numpy 2.5.3): PASS en las 8 comprobaciones.
- `validacion_driver_j6.py`: validación sobre j6/update25 (usa la geometría; se ejecuta en Windows).
- Estado: validado sobre j6/update25 (ver `RESULTADO_validacion_driver_j6_2026-10-19.md`); **no integrado** al flujo productivo de visitas. Falta integrarlo al flujo de visitas y validarlo en un caso cercano a frontera (j5).
- Limitaciones: el tope de 900 s por visita lo aplica el llamador; la prueba 1b no ejerce rechazos (rechazados = 0 en el juguete), así que la cuenta de rechazos aún no tiene verificación independiente con rechazos; checkpoints previos sin contadores arrancan en 0.

Ejecución (PowerShell, desde esta carpeta):
`& "D:\RIPG_DATA\T2_A\cribado_borde\venv_torch\Scripts\python.exe" -I ".\prueba_driver_instrumentado.py"`
