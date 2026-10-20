# Resultado de la validación del driver instrumentado (2026-10-19, Windows, AMD64 Family 23 Model 113, scipy 1.18.1)

Script: `validacion_driver_j6.py` (SHA-256 a10774107d87a2f6c3893b669aac4723b0574d50757be8b7ec96162ac8782253). Caso: split8_j6_true/update25, copia regenerada, 2048 rayos, DOP853 rtol 2e-10 atol 2e-12. Salida transcrita de la terminal del usuario:

| Radio | Soluciones idénticas a solve_ivp | Aceptados / intentos / rechazos | nfev = 2+15·acc+12·rej | Alarma de progreso |
|---|---|---|---|---|
| 0.07883553716312919 | PASS | 16 / 21 / 5 | 302 PASS | no dispara (contador 0) |
| 0.09 | PASS | 19 / 24 / 5 | 347 PASS | no dispara (contador 0) |

RESULTADO GLOBAL: PASS. Pruebas con EDO de juguete (`prueba_driver_instrumentado.py`): PASS en contenedor y en Windows.

Alcance: valida el contador y el reproducido de la solución en un caso sano. No prueba el comportamiento en un caso cercano a frontera (j5), no integra el driver al flujo de visitas ni valida los umbrales. Exploratorio; no clasifica ni asigna outcomes.

## Sesión de visita instrumentada, Windows (2026-10-19 ≈21:55)

`sesion_visita_instrumentada.py` (SHA-256 9a8e2cc5cd98014746ad6b7046fa897b935d7fc6ef1ca46c8f06c84321796fc9), caso split8_j6_true, copia regenerada del estado, python 3.12.10, scipy 1.18.1, AMD64 Family 23 Model 113. Salida transcrita de la terminal del usuario: `CALIBRATION_COMPLETE`, 19 pasos aceptados, 24 intentos, 5 rechazos, contador de alarma 0, 36.8 s de pared, radio 0.07883553716312264, área 0.020000000000000007.

El radio coincide con el obtenido en el contenedor (Linux, python 3.13) y difiere en 6.5×10⁻¹⁵ del registrado en la corrida original (0.07883553716312919), dentro de xtol 1e-13 de brentq; hardware y versiones de la corrida original no están registrados. Alcance: solo la calibración (rayos); no cubre audit.py ni el predictor. Exploratorio; no clasifica ni asigna outcomes.

## Sesión instrumentada sobre j5/update25 (copia regenerada, float64), Windows (2026-10-19 ≈21:59)

`sesion_visita_instrumentada.py` (SHA-256 9a8e2cc5…6fc9) con `state_025_regen.npz` (SHA-256 845c2251…4776), python 3.12.10, scipy 1.18.1, AMD64 Family 23 Model 113. Salida transcrita de la terminal del usuario: `PAUSED_PENDING_REVIEW`, causa `PAUSED_LOW_RADIAL_PROGRESS`, en el paso aceptado 50, t = 0.07217254011594085, 74 intentos (24 rechazos), contador de alarma 8, 27.1 s de pared; checkpoint `step_00000050.zip` SHA-256 aa75006e7ff4444eab4508573899b41700dc962b8d90054c6a750770d36b06ef.

Coincide con la simulación retrospectiva del anexo (paso 50, 74 intentos, r = 0.07217) y con la ejecución en el contenedor (paso 50, t = 0.07217254760…, 74 intentos); la diferencia en t es del orden de 7×10⁻⁹ entre plataformas. Alcance: la alarma dispara con el código real donde la simulación decía; no clasifica ni asigna outcomes sobre j5, no cambia la naturaleza de su pausa histórica y no valida los umbrales.
