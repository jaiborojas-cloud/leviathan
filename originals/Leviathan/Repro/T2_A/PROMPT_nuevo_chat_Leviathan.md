Continúa Leviathan / RIPG. No supongas que recuerdas el chat anterior: reconstruye el estado desde los artefactos persistentes y verifica sus hashes. No reinicies ni repitas auditorías cerradas.

OBJETIVO DE ESTA SESIÓN: ejecutar el primer punto del roadmap: documentar y dejar recuperable el caso split8_j5_true/update25 como no resuelto, pendiente/INCONCLUSIVE, sin cambiar el evento confirmatorio ni asignar un outcome.

Lee:
1. /Leviathan/Repro/T2_A/progress.md
2. /Leviathan/Repro/T2_A/Leviathan_RIPG_roadmap.md
3. /Leviathan/Repro/T2_A/protocol.json y Leviathan_RIPG_T2-A0_preregistro.md
4. /Leviathan/Repro/T2_A/cohort_manifest.csv, task_log.csv, manifest.csv, outcomes.csv y visits.csv (estado actual, no snapshots antiguos).
5. /Leviathan/Repro/T2_A/Leviathan_T2A_limite_dominio139.zip
6. /Leviathan/Repro/T2_A/Leviathan_T2A_dominio_nominal139.zip
7. /Leviathan/Repro/T2_A/Leviathan_T2A_frontera_paso139.zip
8. /RIPG_RESULTADOS_PC.zip y, sólo si necesitas reconstruir los estados numéricos, /Leviathan/Repro/T2_A/Leviathan_T2A_Windows_CP90.zip.

ESTADO DE PARTIDA (verificar contra archivos):
-800/800 basales, predictores globales sellados. Cohorte natural Wine true,160 splits8..167×5 inicializaciones. Checkpoint temprano update5, visitas25,50,...250.
-1/8000 visitas cerradas: split8_j6_true/update25, INJECTIVE_AT_NOMINAL_RADIUS;0/800 horizontes completos. Otros casos abiertos incluyen j5,j7,j8 del split8/update25. No confundir una visita con una trayectoria completa.
-Caso actual split8_j5_true/update25: integración float64 histórica512 intacta. Replay MPFR aislado desde origen: paso139 verificado en PC, r=.07447265825972331, PAUSED. Siguiente paso contable140; NO reanudar hacia.09.
-Retorno PC SHA256 f082f89bd76f94e5bd8060021939008363228aabd0f377d0cd4cfa6eb1ca555b;13 segmentos91–139,17 hashes válidos. Base90 SHA256 de0f854646e9da24402b7adf5ce5ad055cea48230008d622bc0097d44244a987. El índice antiguo90 no es el último avance del PC.
-Estructura del borde de soporte softmax certificada algebraicamente para M,f almacenados. Mínimo LOCAL numérico≈.07447421006513 entre rayos1775/1776; no mínimo global certificado. Controles desde origen~1e-12; coincidencia local130/139~1e-14 no es cota global.
-Área diagnóstica muestreada≈.01871467<.02; no es A_embed ni certificación de existencia/no existencia del disco nominal. Evidencia fuerte de terminación del dominio antes del objetivo, pero clasificación topológica y outcome siguen sin resolver.

TRABAJO A REALIZAR:
1. Reconciliar el estado actual y citar los criterios congelados que rigen fallos no resueltos. Distinguir fallo de dominio, incertidumbre instrumental y GEOMETRIC_NONINJECTIVITY.
2. Crear un cierre documental versionado del incidente. Registrar pendiente/INCONCLUSIVE en el nivel que permita el protocolo; no inventar etiqueta confirmatoria ni representar unknown como0/False. Preservar el historial.
3. Mantener la trayectoria en la cohorte y los predictores sellados. No sustituir estado, reducir A=.02, excluir rayos, aflojar tolerancias ni ampliar el espacio softmax.
4. Actualizar progress.md, task_log.csv, manifest.csv y registro de incidencias de forma consistente. Modificar tablas de visitas/outcomes sólo si es necesario y conforme a su esquema y protocolo; nunca cambiar una observación desconocida a negativo.
5. Identificar la siguiente tarea pendiente en el orden congelado y dejar un plan concreto de continuación de cohorte. No abrir ni calcular nuevas visitas automáticamente en esta sesión: primero completar este cierre documental.
6. Guardar resultados incrementalmente y verificar hashes antes de finalizar. Informar qué se actualizó, qué sigue desconocido y el próximo identificador exacto.

REGLAS:
-Resultados históricos T1 son descubrimiento/control esperado; no validación de nuevas hipótesis con esos mismos80 estados.
-C1-A permanece INCONCLUSIVE.
-Una frontera de dominio no implica punto conjugado, cut locus ni autointersección.
-La certificación rigurosa del borde y la revisión de dominios históricos son líneas separadas del avance descriptivo de cohorte.
-El usuario hará pruebas locales con copias de los800 basales. No incorporar resultados exploratorios locales como confirmación ni modificar el prerregistro sin diseño prospectivo nuevo.
