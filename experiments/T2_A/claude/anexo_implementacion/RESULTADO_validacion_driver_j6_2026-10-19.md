# Resultado de la validación del driver instrumentado (2026-10-19, Windows, AMD64 Family 23 Model 113, scipy 1.18.1)

Script: `validacion_driver_j6.py` (SHA-256 a10774107d87a2f6c3893b669aac4723b0574d50757be8b7ec96162ac8782253). Caso: split8_j6_true/update25, copia regenerada, 2048 rayos, DOP853 rtol 2e-10 atol 2e-12. Salida transcrita de la terminal del usuario:

| Radio | Soluciones idénticas a solve_ivp | Aceptados / intentos / rechazos | nfev = 2+15·acc+12·rej | Alarma de progreso |
|---|---|---|---|---|
| 0.07883553716312919 | PASS | 16 / 21 / 5 | 302 PASS | no dispara (contador 0) |
| 0.09 | PASS | 19 / 24 / 5 | 347 PASS | no dispara (contador 0) |

RESULTADO GLOBAL: PASS. Pruebas con EDO de juguete (`prueba_driver_instrumentado.py`): PASS en contenedor y en Windows.

Alcance: valida el contador y el reproducido de la solución en un caso sano. No prueba el comportamiento en un caso cercano a frontera (j5), no integra el driver al flujo de visitas ni valida los umbrales. Exploratorio; no clasifica ni asigna outcomes.
