# Decisión del responsable: exclusión por título sin resumen (2026-11-09, 16:20, hora de México)

**Estado:** VIGENTE. La autorizó el responsable el 2026-11-09 a las 16:20, a propuesta de Claude en la auditoría del lote H01 ([comentario 6752999192, PR #138](https://github.com/jaiborojas-cloud/leviathan/pull/138#issuecomment-6752999192)). Se registra **antes** de aplicarse. No cambia la pregunta, las consultas, los topes, el corte ni los criterios de inclusión.

## Alcance
Solo cubre los registros que, después de A0 y de la lectura de todas sus posiciones elegibles, **siguen sin resumen de autor**:
- los `PENDIENTE_ACCESO` de la cola A2: `SIN_RESUMEN_EN_FUENTES` y `SIN_IDENTIFICADOR` de A0;
- los pendientes de acceso que salgan de los lotes H (heredadas) o de lotes posteriores;
- los textos de A0 que resulten no ser un resumen de autor.

No cubre los `CONFLICTO_IDENTIDAD`: primero se resuelve la identidad. Tampoco cubre a nadie que tenga resumen.

## Regla
1. Se puede excluir **solo si el título es inequívocamente ajeno a todos los puntos de Q15**. Por ejemplo, un dominio claramente fuera del aprendizaje automático y de la estadística de modelos, como la clínica sin modelos predictivos, la educación, las ciencias sociales o la física aplicada, **y** ningún término del vocabulario de Q15:
   - calibración, confianza, sobreconfianza, temperatura, softmax, logit;
   - Fisher, geometría de la información, símplex, gradiente natural, curvatura;
   - curvas o dinámica de aprendizaje, fase temprana, predicción temprana;
   - R² fuera de muestra, pronóstico, evaluación incremental;
   - redes neuronales, aprendizaje profundo.
2. **Ante cualquier duda, el registro queda PENDIENTE.** Entran en la duda los títulos genéricos o ambiguos, los que contienen un término del vocabulario anterior y los métodos estadísticos o de aprendizaje automático de propósito general.
3. **Estado propio:** `EXCLUIR_POR_TITULO_SIN_RESUMEN`, distinto de `EXCLUIR_FUERA_TEMA`. Cada caso lleva una razón individual que explica por qué el título es inequívocamente ajeno, además de la fecha UTC real y el revisor.
4. **Es reversible.** Si después aparece el resumen y sugiere pertinencia, el registro se reabre y se criba normalmente.
5. **Informe final:** estas exclusiones se cuentan aparte en el embudo y se declaran como limitación («excluidas por título sin resumen»). Nunca cuentan como evidencia de ausencia en la adjudicación de novedad.

## Auditoría
- Claude audita cada lote con una **muestra aleatoria con semilla fija**: al menos el 20 % de las exclusiones por título y como mínimo 30, o todas si son menos. También revisa todas las que el revisor marque como dudosas.
- Si en la muestra aparece **una sola exclusión que no era inequívoca**, se reabren todas las exclusiones por título del lote y se repiten con la regla.

## Origen
En el lote H01, 51 obras heredadas pasaron de una exclusión por título sin fundamento a PENDIENTE_ACCESO. Muchas son ajenas de forma evidente, como catálogos genómicos o estudios clínicos y educativos. La cola de búsqueda manual (A2) suma además 234 + 340 registros. Sin esta regla, buscar a mano el resumen de obras ajenas consumiría el cupo de los agentes sin cambiar ninguna conclusión.
