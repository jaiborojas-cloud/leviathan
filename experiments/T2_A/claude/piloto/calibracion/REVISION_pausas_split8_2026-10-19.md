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
| split8_j5_true | Mantener pausado y abrir diagnóstico separado | 2026-10-19 22:23 (America/Mexico_City) | Decisión del responsable (Jaibo Rojas): medir el tamaño de paso aceptado por paso, solo lectura, antes de gastar el presupuesto adicional |
| split8_j7_true | Mantener pausado y abrir diagnóstico separado | 2026-10-19 22:23 (America/Mexico_City) | Decisión del responsable (Jaibo Rojas): medir el tamaño de paso aceptado por paso, solo lectura, antes de gastar el presupuesto adicional |
| split8_j8_true | Mantener pausado y abrir diagnóstico separado | 2026-10-19 22:23 (America/Mexico_City) | Decisión del responsable (Jaibo Rojas): medir el tamaño de paso aceptado por paso, solo lectura, antes de gastar el presupuesto adicional |
| split8_j9_true | Mantener pausado y abrir diagnóstico separado | 2026-10-19 22:23 (America/Mexico_City) | Decisión del responsable (Jaibo Rojas): medir el tamaño de paso aceptado por paso, solo lectura, antes de gastar el presupuesto adicional |

El diagnóstico no consume presupuesto adicional, no reanuda los checkpoints pausados y no clasifica ni asigna Y.

## Resultado del diagnóstico separado (2026-10-19 22:27–22:37, Windows, solo lectura)

`anexo_implementacion/diagnostico_split8.py` (SHA-256 5b2dcda47d2ed0325865fc1c5f85c2108819a78fca4dee1f5abbad1567426aef), float64, DOP853 rtol 2e-10 atol 2e-12, 2048 rayos, hasta r = 0.09 o 180 s por visita. Datos en `../diagnostico_split8/`. La alarma de progreso, aplicada a estos pasos, cae exactamente donde pausó la calibración (pasos 50, 47, 67 y 84; mismos intentos 74, 73, 88, 105).

| Visita | Resultado de la medición | Pasos / intentos | t alcanzado | dt mín / mediano / últimos 20 | Pasos tras la alarma | Intentos tras la alarma |
|---|---|---|---|---|---|---|
| split8_j5_true | tope de 180 s | 481 / 523 | 0.074439 | 4.41e-08 / 1.75e-07 / 4.60e-08 | 431 | 449 |
| split8_j7_true | tope de 180 s | 463 / 513 | 0.074629 | 4.64e-08 / 1.74e-07 / 4.96e-08 | 416 | 440 |
| split8_j8_true | tope de 180 s | 419 / 529 | 0.087386 | 1.75e-07 / 2.51e-05 / 1.83e-07 | 352 | 441 |
| split8_j9_true | **completa hasta 0.09** | 124 / 151 | 0.090000 | 1.03e-05 / 5.26e-04 / 2.08e-05 | 40 | 46 |

Lectura (descriptiva, sin clasificación): j5 y j7 muestran la misma meseta de paso ≈ 5×10⁻⁸ a r ≈ 0.0744–0.0746; j8 llega más lejos (0.0874) con paso ≈ 2×10⁻⁷; j9 baja a ≈ 10⁻⁵ pero **completa** la integración hasta 0.09 en 51 s. La alarma disparó en j9 aunque la integración terminó: es sensible pero no específica en este caso. La medición no distingue frontera de redondeo en float64 (hipótesis declarada pendiente).

Presupuesto adicional del anexo (+128 pasos, +250 intentos, +120 s): j5, j7 y j8 necesitaron 350–430 pasos y ≈ 440 intentos tras la alarma sin terminar → el presupuesto adicional no alcanzaría; j9 necesitó 40 pasos y 46 intentos → cabría con holgura. Que la integración llegue a 0.09 no garantiza que la calibración termine (queda por comprobar que el área alcance 0.02 o que sea necesario ampliar la cota).

Decisión pendiente del responsable sobre el resultado (completar):

| Visita | Decisión | Fecha | Motivo |
|---|---|---|---|
| split8_j5_true | Mantener pausado | 2026-10-19 22:40 (America/Mexico_City) | Decisión del responsable (Jaibo Rojas). Gastar el único presupuesto adicional no resolvería nada (431 pasos tras la alarma sin terminar) |
| split8_j7_true | Mantener pausado | 2026-10-19 22:40 (America/Mexico_City) | Decisión del responsable (Jaibo Rojas). Ídem (416 pasos tras la alarma sin terminar) |
| split8_j8_true | Mantener pausado | 2026-10-19 22:40 (America/Mexico_City) | Decisión del responsable (Jaibo Rojas). Ídem (352 pasos tras la alarma sin terminar) |
| split8_j9_true | Reanudar con el presupuesto adicional del anexo (+128 pasos, +250 intentos, +120 s por integración; sin reiniciar contadores) | 2026-10-19 22:40 (America/Mexico_City) | Decisión del responsable (Jaibo Rojas). Única visita donde la medición indica que cabe en el presupuesto (40 pasos y 46 intentos tras la alarma hasta 0.09) |

El estado de j5, j7 y j8 se queda como está (`PAUSED_PENDING_REVIEW`). La reanudación de j9 queda condicionada a las condiciones del anexo 3.3: checkpoint verificado por hash, mismas versiones y tolerancias, decisión registrada (esta) y presupuesto adicional aún sin usar.

Aviso de procedimiento: `sesion_visita_instrumentada.py --extra-budget` aplica el flag a toda la sesión. Si, tras completar la integración a 0.09, la calibración necesitara otra integración (cota ampliada), esa nueva integración correría también con topes duplicados. Se informará si ocurre; el archivo `REVISION_PENDIENTE.json` previo queda en la carpeta como registro de la pausa, y el resultado de la reanudación se escribe en `SESION_COMPLETA.json` o en un nuevo `REVISION_PENDIENTE.json`.
