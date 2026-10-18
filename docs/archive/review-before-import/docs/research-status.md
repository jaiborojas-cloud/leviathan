# Estado científico reconstruible

Corte documental: 2026-10-16 (America/Mexico_City). Base local: commit `2592f910e4d2ece8bfd1cde2cbcd58224958068b`. Fuentes y hashes en el [catálogo](source-catalog.md). La fecha de corte describe esta revisión, no la fecha de ejecución histórica.

## Evidencia disponible

La inspección estática encuentra 178 celdas, 176 de código. Hay salidas históricas aunque algunos contadores son nulos; no permiten establecer una secuencia completa de ejecución. No se ejecutaron nuevos experimentos para esta reconstrucción documental.

| Bloque | Evidencia localizada | Interpretación permitida |
| --- | --- | --- |
| E1–E5 | Código de gradientes, covariancia, trayectorias, Fisher y transporte; celdas 1–101 | Controles instrumentales previstos; faltan cierres y salidas completas para declarar aprobación global |
| E6 | Salida celda 129: holonomía −4.9079063797176975e−05, curvatura integrada −4.908088737666005e−05, error absoluto de magnitudes 1.8235794830762423e−09; celda 132 contiene otro resumen | Observación numérica histórica en rebanada 2D; no certificado riguroso ni cierre independiente |
| E7/E7b | Celdas 138–159; celda 159 almacena PASS para covectores, Fisher y ángulo; error angular 2.1510571102112408e−15 | Control esperado de covariancia en el ejemplo; no validación predictiva |
| E8 | Celdas 160–176; error relativo RFD 0.015084783666466916 en celda 174 y circulación 2.5987892393608547e−14 en celda 176 | Observaciones exploratorias almacenadas; dependencia ausente impide afirmar reproducción limpia |

## Limitaciones y discrepancias

La celda 169 llama a `relevance_covariant_derivative`, pero no se localiza su definición en el código del notebook. Su salida almacenada no prueba autosuficiencia del archivo. Los errores de E6 para radio 0.15 en celdas 129 y 132 difieren (1.8235794830762423e−09 frente a 2.178107e−09); falta la secuencia/versionado para explicar la discrepancia. Se conservan ambas fuentes sin elegir una por intuición.

No hay protocolos externos, manifests ni cierres que permitan clasificar E9–E15, T1 o T2-A como concluidos, pausados o incompletos. Su estado es **no verificable con las fuentes locales**, no automáticamente pendiente o fallido.

## Contexto posterior sin corroborar

La [solicitud](archive/solicitud-documental.txt) menciona C1-A INCONCLUSIVE; C1-A2 GEOMETRIC_NONINJECTIVITY en split0/true/j1 y j3; correlación descriptiva T1-B ≈0.9549 en 38 estados true admisibles; 800 basales T2-A; e indicios de frontera en split8_j5_true/update25. Se registran como pistas, no resultados verificados. La correlación indicada correspondería a EXPECTED_GEOMETRIC_CONTROL, no predicción prospectiva. Las visitas futuras y outcomes son desconocidos.

Una frontera de dominio no equivale a conjugado, cut locus ni autointersección. La evidencia exploratoria y los supervivientes no deben convertirse en confirmación. No hay hipótesis predictiva prospectiva verificada en este checkout.

## Procedencia de la sesión

Antes de recibir la solicitud documental se inició una ejecución para validar el entorno. Al recibir la prohibición se detuvieron el ejecutor y su kernel. No se usa esa ejecución parcial como fuente científica; los originales se mantienen intactos. La instalación local de herramientas fuera del checkout tampoco demuestra resultados científicos.
