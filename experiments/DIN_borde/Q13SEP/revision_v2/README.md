# DIN-Q13-SEP · v2 para revisión

**BORRADOR, sin congelar.** Responde a la auditoría de Claude del PR #134, conservando íntegramente la v1.

- [Diseño v2](../../DISENO_DIN_Q13SEP_BORRADOR_v2.md), [configuración](../config_BORRADOR_v2.json), [esquema/decisiones](../ESQUEMA_Y_DECISION_v2.md) y [respuesta a la auditoría](../REVISION_DOCUMENTAL_v2.md).
- Principal solo **u250**; u10 descriptivo, sin veto o selección de dosis.
- E iguala escala aplicando **T*=S_LP/S_A0 a LP**, por unidad/visita, ancla A0/T1.
- C usa **33 temperaturas 2^(j/8)** y minimiza |Δc|; solo después comprueba distinta escala. Regla y desempate prefijados, sin segundo candidato de rescate.
- Misma receta, instrumento, fases y [semillas heredadas](../SEMILLAS_PROPUESTAS_v1.md); sin X/rho/D, productor o piloto ejecutado.
- Máximo **450 entrenamientos y 20.703 llamadas M**; prueba corta integrada de 15 con 825 llamadas máximas. Presupuesto inicial 30–75 min a confirmar, no un benchmark.

Se aclara el control 0 frente a ≤1e−12 y que una futura señal con temperatura cambia X10/L/Y, con una política temporal predeclarada que evite información futura en u10. La primaria robusta no se congela aquí. Solo verificaciones documentales y de aritmética, no resultados científicos.
