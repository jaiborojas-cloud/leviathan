# Apertura del piloto operativo de 20 visitas (update 25) — 2026-10-19 22:01 America/Mexico_City

**Decisión:** el responsable del protocolo (Jaibo Rojas) ordenó abrir el piloto el 2026-10-19 ≈22:01 (hora de Ciudad de México), tras el congelamiento del anexo operativo v1.0 y de E1 v8.

**Reglas que lo rigen (congeladas):**
- `E1/ANEXO_OPERATIVO_E1_v1.0_CONGELADO.md`, SHA-256 `a7cb20d87f0c96b1962ccc56da15d0df23338c908659f3c469c12d5d93d84085`.
- `E1/Leviathan_RIPG_T2-A0_enmienda_E1_v8_CONGELADA.md`, SHA-256 `faf6db032e95e03e7422efb0a38012ccc715803d948b8971c6b746067aa05c23` (sección 6 sin aprobar: no se aplica a datos).
- Driver `anexo_implementacion/resumable_dop853_instrumentado.py`, SHA-256 `285a9120afb48545df9e73959fc240c05daca23520106959cfce86e0aa9c62d1`; sesión `anexo_implementacion/sesion_visita_instrumentada.py`, SHA-256 `9a8e2cc5cd98014746ad6b7046fa897b935d7fc6ef1ca46c8f06c84321796fc9`.

**Qué es:** prueba de viabilidad operativa. No estima frecuencias, no establece el veredicto predictivo (solo update 25) y no asigna outcomes. Orden de cohorte, sin selección por facilidad ni por X: las 20 visitas de `PILOTO_20_visitas_update25.csv` (split8_j5_true a split11_j24_true), incluyendo las ya abiertas (j5 parcial, j6 clasificada, j7 y j8 parciales según el inventario fechado 2026-10-19).

**Compuerta operacional (provisional, anexo 5):** detener nuevas aperturas y revisar el diseño si más de 5 de las 20 visitas siguen en `PAUSED_PENDING_REVIEW` tras el presupuesto adicional y la revisión, o si las 5 de un mismo split quedan sin resolver. Consecuencia: detener y revisar; nunca asignar outcomes.

**Ejes por visita (no excluyentes):** diagnóstico geométrico, estado operacional, desenlace de trayectoria. Al abrir, todas están `SIN_DIAGNOSTICO` / estado del inventario / `NO_DETERMINADO`; el CSV se actualiza con fecha y hash en cada paso.

**Alcance actual de la tubería (limitaciones declaradas):**
- Cubierto y validado: calibración del radio nominal con topes y alarma (`sesion_visita_instrumentada.py`: j6 sano 24 intentos; j5 pausa en el paso 50).
- **No cubierto todavía:** regeneración del estado de update 25 con la puerta del prefijo (Δθ ≤ 1e-12) para las visitas sin estado regenerado, integraciones de Jacobi de `audit.py`, predictor, clasificación topológica y registro de visita completa. Hasta que esa tubería esté lista y validada, **ninguna visita nueva se clasifica**; abrir el piloto fija reglas y lista, no produce resultados.
- Toda pausa sigue el procedimiento de revisión del anexo (3.3); el revisor es el responsable del protocolo.

**Siguiente paso operativo:** preparar y validar la regeneración de estados update 25 (con puerta del prefijo) para las visitas del orden de cohorte, empezando por las que ya tienen registros; luego la calibración con la sesión instrumentada; luego la auditoría con el mismo mecanismo.
