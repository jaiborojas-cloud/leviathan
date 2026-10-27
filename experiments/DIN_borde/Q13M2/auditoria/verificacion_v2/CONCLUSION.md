# Verificación independiente de DIN-Q13-M2 v2

**F01–F04 quedan resueltos en las comprobaciones funcionales**, con dos observaciones antes de congelar: **N01, registro incompleto de fallos múltiples**, y **N02, redacción residual sobre igualdad exacta de β_LS**. No se demostró un nuevo veredicto equivocado en los casos probados. Se recomienda completar la traza N01 y armonizar N02; la aprobación de congelación corresponde al responsable.

Objetivo auditado: commit `ac63574f60bcd5bee2aa444dbd57ac88d68e76b7`, analista `512737ddb3c546f7151deafc51750b1e8deaf8ef39363facf692a8f8eceec865`, pruebas `6e7b836ca08f0c7f5123c24ae1b0de7948fe5bd70e7d77f5ee337b5f30445d7e`. No se modificaron esos archivos, el diseño ni la auditoría #117.

| Hallazgo de #117 | Resultado v2 | Evidencia |
|---|---|---|
| F01: aislamiento de fallos | **RESUELTO** | Nueve casos WD3/LP3/A0 × Y/X/L. En los seis exclusivos, el sano conserva exactamente sus primarias, β, IC y veredicto; conjunto PARCIAL. A0 produce inconcluso global. |
| F02: sobreescritura | **RESUELTO** | CLI original: marcador intacto y ABORTA3. Directorio intacto. Inyección operacional: enlace colgante y carrera tras la precomprobación también se rechazan sin sustitución. |
| F03: evidencia vinculada | **RESUELTO, vinculación documental** | Informe y JSON nuevos contienen los SHA finales; registran25 casos y18 reglas, sin fallos declarados. No se ejecutó aquí la suite del autor, que usa un fixture entrenado. |
| F04: igualdad literal LS | **RESUELTO numéricamente** | β=0.07692466151365296, diferencia3.747×10⁻¹⁶ ≤10⁻¹²; la prueba v2 usa esa tolerancia. N02 es solo una inconsistencia del texto del diseño. |

Casos y matriz completa en [MATRIZ_VERIFICACION.md](MATRIZ_VERIFICACION.md). Los detalles de las observaciones nuevas, su severidad y correcciones propuestas están en [HALLAZGOS_NUEVOS.md](HALLAZGOS_NUEVOS.md).

## Regresiones

Se reejecutaron los23 casos de #117 con **el mismo script byte a byte**, semillas y presupuestos. **19 resultados son exactamente idénticos**; los otros cuatro son precisamente las correcciones esperadas de F01. La [comparación](regression_matrix.json) no ignora salidas o excepciones fallidas.

Las trazas confirman draws compartidos960001, copias en el bloque original, A0 idéntico, recálculo D/c/β, cuantiles .0125/.9875 y la misma réplica LS para ambos contrastes. Se conservan los94/300 fallos inducidos por WD4/A0 y los23/64 de LS, sin redibujar ni suprimir errores. La referencia LS mantiene2000 draws960002: su archivo de réplicas tiene **el mismo SHA `6629f1b1…` que en #117**. No se cambia el cierre oficial de Q13-DR.

**No se repitió el Monte Carlo.** El AST del bloque de bootstrap y clasificación, de las siete funciones no cambiadas y de las dependencias reutilizadas es idéntico; también lo son los resultados no afectados por F01. Los cambios de flujo no alteran el estimando en esos casos. Las tasas nominales de #117 siguen siendo las de aquella ejecución; aquí no se presentan nuevas tasas ni una certificación universal.

## Nuevas rutas del diff

Una referencia LS con error deja la compatibilidad explícitamente no definida, conserva todas las primarias y LP−WD; se comprobó tanto por API como pasando por `main` con una excepción inyectada. Réplicas de tamaños discordantes producen `ValueError` claro. Una inyección de fallo no equivale a afirmar que la tabla publicada LS sea defectuosa.

N01: al invalidar un brazo, las condiciones `estado[m] is None` impiden registrar otros niveles fallidos del mismo brazo. Se demuestra con WD2+WD3, sin cambiar el resultado correcto `LP=MODULA, WD=INCONCLUSIVE`. N02: las líneas84 y106 del borrador v2 aún dicen «exactamente» aunque cabecera y pruebas establecen tolerancia10⁻¹². No se corrigieron fuentes ajenas.

## Integridad y alcance

[verification.json](verification.json): **63 comprobaciones**, `PASS_VERIFICATION_WITH_FINDINGS`. [verification_publicacion.json](verification_publicacion.json) y [manifest.sha256](manifest.sha256) verifican la entrega. Solo archivos nuevos bajo `auditoria/verificacion_v2/`; #117 queda intacto en su rama. Las excepciones esperadas y mensajes LAPACK del caso LS sintético degenerado se conservan en salidas/logs.

Solo sintéticos y la tabla LS publicada autorizada, verificada por SHA. Sin entrenamiento, datos reales nuevos ni lectura de cohortes restringidas. El estado PASS describe las comprobaciones de esta verificación y no constituye aprobación del confirmatorio.
