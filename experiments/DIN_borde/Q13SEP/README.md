# DIN-Q13-SEP · piloto de separabilidad, BORRADOR v1

**Diseño para auditoría de Claude, sin congelar ni ejecutar.** Elección de la opción 1 de A2 en el PR #133. Solo fuentes y verificaciones estáticas; no existe productor ni resultado de piloto en esta entrega.

- [Diseño completo](../DISENO_DIN_Q13SEP_BORRADOR_v1.md), [configuración legible por máquina](config_BORRADOR_v1.json), [esquema y decisiones](ESQUEMA_Y_DECISION_v1.md).
- [Semillas propuestas](SEMILLAS_PROPUESTAS_v1.md), [inventario de fuentes por SHA](fuentes/semillas_archivos_revisados.csv) y [cotejo estático](fuentes/semillas_verificacion_estatica.json).
- [Comprobaciones y puntos para auditoría](REVISION_DOCUMENTAL_v1.md); [decisión PR #133](fuentes/decision_PR133.md), conservada byte a byte por su Git blob.

Gaussianas s=.8, red 13→64→32→3 y core congelado. Calibración independiente de λ LP entre .0001/.0003/.001/.003; validación con A0 y la menor dosis apta. Tres temperaturas prefijadas .5/1/2, escalando W/b de l3 desde copias frescas y recomputando el instrumento en u10/u250. **No se calculan X, rho o D.**

El criterio exige ambos sentidos entre brazos: misma escala (factor 1.10) y c distinta (≥.15), y misma c (≤.05) y escala distinta (factor ≥1.5), con orientaciones fijadas en calibración. Al menos 3/5 unidades por split en ambas visitas y 16/20 splits de validación, más calidad. Se distingue T fija, T distinta y SOLO_TEMPERATURA; esta última nunca rescata. Si no se cumple: NO_IDENTIFICABLE y se detiene la vía bajo este diseño.

Máximo 250 + 200 entrenamientos; 1.350 celdas y 2.700 medidas M principales más tres reconstrucciones de control. La prueba corta de 15 entrenamientos forma parte de calibración. Presupuesto orientativo 30–60 min en el PC con 12 procesos, usando **33 s individuales**, no el rendimiento global de 2,8 s como latencia. Medir y publicar tiempos antes de continuar; límite operacional 90 min proyectados.

Si hay separación, el responsable decidirá un experimento de señal con datos nuevos, primaria robusta del PR #132 congelada entonces y dos contrastes principales con Holm α=.05. No se usa el piloto para estimar D o su potencia. Esta entrega no altera estados, instrumentos, semillas reservadas o resultados previos, ni implementa el trabajo de Claude.
