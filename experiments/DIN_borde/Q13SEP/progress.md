# Q13-SEP · diseño del piloto, 2026-11-02

Se leyeron AGENTS.md, receta G3/Q13, adaptador LP M2 y funciones core congeladas. Se tomó la decisión del PR #133 (`168352e8`) por snapshot con Git blob idéntico; aún estaba pendiente. PR #132 auditado y listo, no fusionado al iniciar: su analista 1e2d903b sigue BORRADOR y no se importa o ejecuta aquí.

Se fijan dos fases nuevas: 250 entrenamientos máximos de calibración y 200 de validación, tres temperaturas y dos visitas. El productor futuro divide W/b de l3 en copias frescas, sale de no_grad y recalcula R/U/Gram/ridge/M con core intacto. No se calculan X/rho/D ni peores ejemplos. Las fórmulas, criterios E/C, orientaciones y selección por menor λ apta se documentan antes de medir. Se diferencia separación entre brazos a T fija, a T distinta y solo por temperatura; esta última no rescata. No se afirma identificación causal.

Se cotejaron registros visibles de semillas en fuentes/protocolos/configuraciones, sin abrir tablas o checkpoints. Propuesta 71/72 millones y reserva futura 73 millones; ninguna colisión literal detectada. Se evita además la banda histórica y las reservas CIFAR-F2. Se documentan los límites de la comprobación estática y se exige actualizarla antes de congelar.

Commit de diseño inicial 8bea1624, antes de productor o mediciones. La validación de esta entrega es solo aritmética, esquemas, hashes y enlaces: no se ejecutaron modelos, PRNG, geometría o estadística. Los únicos artefactos nuevos son documentos, JSON y CSV de metadatos de semillas. No hay dosis elegida o resultado de separabilidad.

El responsable debe aprobar tras la auditoría de Claude. Claude implementará y publicará el productor después de congelar; lo ejecutará el responsable. El analista robusto solo se congelaría en un diseño de señal posterior con datos nuevos y familia de dos contrastes/Holm. Nada se fusiona ni se activa automáticamente.
