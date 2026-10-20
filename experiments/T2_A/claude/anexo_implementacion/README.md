# Implementación instrumentada del anexo operativo E1 v1.0

- `resumable_dop853_instrumentado.py`: copia modificada de `sources/resumable_dop853.py` (el original no se toca) con contador de intentos, topes de intentos y tiempo, alarma de progreso radial y presupuesto adicional, según `E1/ANEXO_OPERATIVO_E1_v1.0_CONGELADO.md`.
- `prueba_driver_instrumentado.py`: pruebas con EDO de juguete (sin geometría ni torch). Resultado en el contenedor (scipy 1.18.1, numpy 2.5.3): PASS en las 8 comprobaciones.
- `validacion_driver_j6.py`: validación sobre j6/update25 (usa la geometría; se ejecuta en Windows).
- Estado: validado sobre j6/update25 (ver `RESULTADO_validacion_driver_j6_2026-10-19.md`); **no integrado** al flujo productivo de visitas. Falta integrarlo al flujo de visitas y validarlo en un caso cercano a frontera (j5).
- Limitaciones: el tope de 900 s por visita lo aplica el llamador; la prueba 1b no ejerce rechazos (rechazados = 0 en el juguete), así que la cuenta de rechazos aún no tiene verificación independiente con rechazos; checkpoints previos sin contadores arrancan en 0.

Ejecución (PowerShell, desde esta carpeta):
`& "D:\RIPG_DATA\T2_A\cribado_borde\venv_torch\Scripts\python.exe" -I ".\prueba_driver_instrumentado.py"`

## Sesión de visita instrumentada (punto 1: integración al flujo)

- `sesion_visita_instrumentada.py`: calibración del radio nominal de una visita con el driver instrumentado (montaje como `margen/run_calibrate.py`: geometría sin auditoría, `geometry.solve_ivp` sustituido por el driver; sin persistencia ni manifiestos). Aplica el tope de visita de 900 s sumando el tiempo guardado de las integraciones terminadas. Si pausa, escribe `REVISION_PENDIENTE.json` (`PAUSED_PENDING_REVIEW`, sin clasificación ni outcome) y termina.
- Prueba en el contenedor (Linux, python 3.13.16, scipy 1.18.1; `core` sustituido por un stub vacío, sin torch): j6/update25 completa en 24 intentos (5 rechazos), radio 0.07883553716312264 (registrado 0.07883553716312919, diferencia 6.5e-15, dentro de xtol 1e-13 de brentq); con `--attempt-cap 10` pausa con `PAUSED_ATTEMPT_CAP` y `REVISION_PENDIENTE.json`; `--extra-budget` suma +10 intentos continuando contadores; un segundo `--extra-budget` se rechaza.
- **No cubre** las integraciones de Jacobi de `audit.py` ni el predictor (siguen con su `solve_ivp` original), y no escribe manifiestos ni `persist`: es la pieza de calibración, no la visita completa. Pendiente: validarla en Windows con el entorno real y decidir si `audit.solve_ivp` también se envuelve.

## Visita completa instrumentada (update 25)

- `visita_completa_instrumentada.py`: replica `followup.one_visit` (entrenar 20 updates desde `checkpoint_005.pt`, estado, `bg.calibrate`, `topological_map.result`) con el driver instrumentado en **ambos** puntos de integración: `geometry.solve_ivp` (rayos) y `audit.solve_ivp` (campos de Jacobi). Tope de visita (900 s) compartido entre ambos drivers. Llamadas que no cumplen las precondiciones del Driver (p. ej. `dense_output=False`) corren sin instrumentar y se listan en `sin_cubrir`. Si hay pausa: `REVISION_PENDIENTE.json` (`PAUSED_PENDING_REVIEW`); si termina: `VISITA_COMPLETA.json`.
- `comparar_visita_j6.py`: compara el `result.json` de j6 con el registro de la corrida original.
- Prueba en el contenedor (Linux, python 3.13.16, `--prueba-sin-torch`: estado regenerado de j6, checkpoint ficticio, sin torch): `VISIT_EVALUATED`, `INJECTIVE_AT_NOMINAL_RADIUS`, 9 integraciones (1 calibración, 4 de frontera, 4 de Jacobi), 187 intentos totales, alarma 0, `sin_cubrir` vacío, 52 s; `comparar_visita_j6.py`: 15 de 15 PASS (diferencias relativas ≲ 5×10⁻¹³ en Jacobi/métrica, 6.5×10⁻¹⁵ en el radio nominal).
- (Validación en Windows hecha; ver abajo.)
- **Validación en Windows (2026-10-19 22:51)**: `VISIT_EVALUATED`, `INJECTIVE_AT_NOMINAL_RADIUS`, 9 integraciones, 187 intentos, alarma 0, `sin_cubrir` vacío, 55 s; `comparar_visita_j6.py`: 15 de 15 PASS contra el registro original (radio nominal 0.0788355371631218, diferencia 7.4×10⁻¹⁵; Jacobi/métrica ≲ 1×10⁻¹²). Archivos en `validacion_visita_j6/`. Con esto la visita completa instrumentada queda validada en un caso sano; no está validada en uno con evento topológico (ningún caso cerrado de update 25 lo tiene todavía) ni en uno con pausas en la etapa de Jacobi.

- **Corrección del driver (2026-10-20):** ver `piloto/visitas/INCIDENCIA_driver_split8_j9_2026-10-20.md` (integración terminada re-pedida con `extra_budget`). Driver SHA-256 9579e411…905f; pruebas f14839d1…27b4f2 (9 PASS, la 2e falla con el código anterior).
