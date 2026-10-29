# DIN-Q13-M2: productor de cohorte v2

**Preparado para ejecutar en Windows por el responsable.**320 splits,11 niveles pareados,5 inicializaciones:17.600 trayectorias. No se entrenó la cohorte aquí. [Comandos PowerShell completos](EJECUCION_WINDOWS_v2.md), con venv `D:\RIPG_DATA\venv_q13`, clon `D:\leviathan-q13` y salida `D:\RIPG_DATA\DIN_Q13M2_v2`.

| Archivo | Función |
|---|---|
| [q13m2_plan.json](q13m2_plan.json) | Universo fijo y dosis, publicado antes del productor |
| [q13m2_plan.sha256](q13m2_plan.sha256) | SHA del plan `4b0aa95f…d90d7` |
| [scripts/cohorte_v2.py](scripts/cohorte_v2.py) | Productor único portable; compuerta/cohorte/tabla |
| [scripts/cohorte_v2.sha256](scripts/cohorte_v2.sha256) | SHA del script `87dbc9ee…24bbe1` |
| [requirements_windows_v2.txt](requirements_windows_v2.txt) | Cuatro versiones exactas |
| [PROCEDIMIENTO_v2_CONGELADO.md](PROCEDIMIENTO_v2_CONGELADO.md) | Procedimiento comprometido antes de plan/productor |
| [POTENCIA_CONGELADO.md](POTENCIA_CONGELADO.md) | Correspondencia con el analista congelado, sin repetir potencia |
| [power_frozen_equivalence.json](power_frozen_equivalence.json) | Prueba AST/SHA, sin ejecutar analistas |
| [fuentes/provenance.json](fuentes/provenance.json) | Fuentes originales intactas por SHA |
| [validacion/results_v1/verification.json](validacion/results_v1/verification.json) | Pruebas sin pasos de entrenamiento |
| [verification.json](verification.json) | Verificación de entrega; no resultado de cohorte |
| [manifest.sha256](manifest.sha256) | Integridad de los miembros publicados |

## Receta y versiones

Red13→64→32→3 en float64, gaussianas s=.8,90 train/27 panel por split, Adam lr=.006 y lote64 sin reemplazo,250 updates, visitas5/10/30/250. A0 no cambia; LP usa CE+λ·media(sum(z²,dim=1)), Adam; WD usa AdamW con la dosis de cada nivel. Los11 niveles comparten semillas de datos, pesos y lotes:911000+s,921000+5s+k,931000+5s+k.

La receta Q13 y el soporte original se embeben byte a byte; el adaptador LP es el mismo archivo de la calibración, también embebido/verificado. Su función intacta se carga con `original_update` enlazada al update original; A0/WD delegan sin cambios. Se mantienen la construcción de M y rho r3, con sus SHA. El productor no importa el analista ni usa datos de otras cohortes.

Versiones exigidas: torch2.9.1+cpu, numpy2.3.5, scipy1.17.0, scikit-learn1.8.0; Python3.12 recomendado. Se probó Linux con3.12.14, `python -I` y spawn. La compuerta Windows debe ejecutarse en el PC del responsable antes de entrenar. No se afirma que se haya ejecutado Windows en este entorno.

## Orden, reanudación y publicación

Orden de envío split→k→nivel; orden de tabla/hash nivel→split→k. Máximo12 tareas activas por defecto, progreso cada500. Vínculo fijo entre carpeta, plan, script, diseño, fuentes y versiones. Escrituras exclusivas y bloqueos del SO; una ejecución no sobrescribe otra. Registros truncados y claims interrumpidos se preservan como fallo; registros con SHA alterado detienen el proceso. No se sustituyen trayectorias.

La prueba33 cuenta dentro del universo. Después, tres sesiones `--limite 5900`: la última toma solo lo que falta. La exportación conserva las17.600 filas, incluidas faltantes/fallidas con error, y escribe resumen de tres SHA. Publicar la tabla impide añadir entrenamiento en esa carpeta. Todos los checkpoints/arrays/diagnósticos quedan en la salida externa, fuera de Git.

## Verificación ya realizada

Tres reconstrucciones desde pesos sintéticos, sin optimización: error relativo M=0 y f idéntica en las tres. Identidad AST de medición/checkpoints frente al productor Q13-DR; receta, soporte y LP byte a byte. Programación completa de17.600 IDs, límite33, reanudación, claims/fallos/truncados, tabla artificial completa e idempotente, colisión exclusiva, bloqueo y coordinador con interrupción. Fórmula LP y delegación A0/WD probadas con espías sin tensores ni optimizador reales.

**0 trayectorias de cohorte entrenadas y0 updates reales.** La tabla del fixture IO es artificial y permanece fuera de Git; no es `q13m2_cohorte.csv` del confirmatorio. No se ejecutó el modo CLI cohorte, ni la prueba33, ni un analista; tampoco se calcularon asociaciones. [Resultados](validacion/results_v1/verification.json) y [manifest externo](validacion/results_v1/external_manifest.csv).

## Secuencia de commits

- Plan efectivo enviado al remoto en `b75448d28a41753f2287b44d79db9febc6c95434`, antes de crear el productor.
- Productor, requisitos y validación comprometidos en **`0c00de9362252aa3f51aa2e619b4b36848870ed4`**, commit de ejecución Windows fijado en los comandos.
- Resultados de controles y documentación se añaden después, sin modificar el productor.

Se conserva [un incidente de preparación del plan](INCIDENTE_PLAN_v1.md): una aserción de orden AST falló antes de emitir archivos; el commit anterior tiene un título anticipado. No cambió el protocolo ni hubo medición afectada. No se reescribe esa historia.

La congelación científica permanece en el diseño v2 aprobado. Esta entrega es únicamente el productor y la publicación operativa; no contiene el desenlace del estudio ni autoriza análisis desde el papel de cohorte.
