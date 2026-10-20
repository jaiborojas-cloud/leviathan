# Expediente de revisión de pausas — calibración del piloto, update 25 (2026-10-19 ≈22:21)

Estado de las cuatro visitas: `PAUSED_PENDING_REVIEW`. No son FAIL, ni INCONCLUSIVE, ni evidencia topológica; no se asigna clasificación ni Y. Revisor (anexo v1.0, 3.3): el responsable del protocolo. Indicador de «proximidad a frontera» (a): disparó la alarma de progreso radial → se trata como **sospecha de frontera**.

| Visita | Causa | Paso aceptado | r al pausar | Intentos / rechazos | Alarma | Sesión |
|---|---|---|---|---|---|---|
| split8_j5_true | PAUSED_LOW_RADIAL_PROGRESS | 50 | 0.0721725 | 74 / 24 | 8 | 25.3 s |
| split8_j7_true | PAUSED_LOW_RADIAL_PROGRESS | 47 | 0.0722433 | 73 / 26 | 8 | 26.0 s |
| split8_j8_true | PAUSED_LOW_RADIAL_PROGRESS | 67 | 0.0799241 | 88 / 21 | 8 | 33.6 s |
| split8_j9_true | PAUSED_LOW_RADIAL_PROGRESS | 84 | 0.0891860 | 105 / 21 | 8 | 39.7 s |

Resumen del lote: 16 calibraciones completas, 4 pausadas, 0 errores (`calibracion_piloto.csv/.log`). Las 4 pausas son de split 8; split8_j6 calibró (24 intentos, radio 0.0788355). Ningún tope de intentos o tiempo se acercó a su límite (máximo 105 de 250 intentos; 63 s de sesión). Las calibraciones completas de los splits 9 a 11 usaron entre 17 y 80 intentos.

**Compuerta operacional (provisional):** más de 5 de 20 pausadas, o 5 de 5 de un mismo split. Hoy: 4 de 20 y 4 de 5 en split 8 → **no se dispara**, pero split 8 está a una visita del criterio por split. Dentro de un split las inicializaciones comparten `f`, así que las cuatro pausas no son cuatro observaciones independientes. La compuerta se evalúa tras la revisión y el presupuesto adicional, no sobre esta tabla.

**Opciones del procedimiento (anexo 3.3):** (1) reanudar con el presupuesto adicional (+128 pasos aceptados, +250 intentos, +120 s por integración; uno por visita; la alarma se registra sin pausar); (2) mantener pausado; (3) abrir diagnóstico separado.

**Recomendación del constructor (no es decisión):** mantener las cuatro pausadas y abrir un diagnóstico separado, de solo lectura, que mida el tamaño de paso aceptado por paso en las cuatro (como se hizo con j5), antes de gastar el presupuesto adicional. Razón: la única evidencia de lo que ocurre tras la alarma es j5, donde el paso se mantuvo ≈ 3×10⁻⁵ durante cientos de pasos; 128 pasos adicionales probablemente no alcanzarían un final, y el presupuesto adicional es único por visita. Es una inferencia a partir de un caso.

Nota técnica: el SHA-256 del paquete de checkpoint de j5 difiere del de la prueba anterior (aa75006e… frente a ff4e1d27…) porque el paquete serializado incluye tiempos de pared; no indica un estado distinto (mismos paso 50, r, intentos y contador).

## Decisión del responsable (completar con fecha, revisor y motivo)

| Visita | Decisión (reanudar / mantener pausado / diagnóstico separado) | Fecha | Motivo |
|---|---|---|---|
| split8_j5_true | | | |
| split8_j7_true | | | |
| split8_j8_true | | | |
| split8_j9_true | | | |
