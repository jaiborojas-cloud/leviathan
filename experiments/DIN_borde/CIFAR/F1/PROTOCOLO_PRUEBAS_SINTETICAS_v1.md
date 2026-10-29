# Protocolo de desarrollo y pruebas del analista

2026-10-29. Se compromete antes del código y ejecución de pruebas. **Se fija este protocolo de validación, no se congela la cohorte F1:** el diseño científico sigue BORRADOR para auditoría y aprobación. Solo archivos nuevos de diseño/F1; no modificar planes, instrumentos ni etapas previas.

Datos exclusivamente sintéticos:500 IDs×4 visitas por tabla, sin imágenes, entrenamiento, geometría, Wine, C2/T2 ni cohortes reales. Semillas de prueba2.010.001 para caso base y2.010.100+i para≥20 tablas; no se usarán como semillas de entrenamiento. Referencia C1 solo como código por SHA, nunca sus datos/wrapper CLI.

Pruebas fijadas:

- Equivalencia del estadístico y p frente a cálculo OLS independiente, centrado por split y10 bloques260010, permutación260001. ≥20 tablas sintéticas con B39; tolerancia D≤1e−10 y p idéntico, no evaluación nominal de tamaño/potencia. Un caso nominal de5000 permutaciones y un caso idéntico por llamada C1, sin cambiar la CLI científica.
- Universo/IDs/visitas duplicadas o ajenas, identidad split/k, plan corrupto/tipos/bool, semillas o lr incorrectos, enlaces de resumen/compuerta, fuentes/versiones y lecturas ausentes/directorio/JSON inválido. ABORTA3 controlado, sin sobrescribir resultado.
- Casos positivos, sin señal, pendiente negativa, X constante intra-split, L constante, Y constante, empates/saturación X=0 y extremos X/R, c=1/q=0. NaN/inf/rho≤0 no se logaritman.
-25/500 faltantes permitidas frente a26; se reportan todas las causas. Splits con<3 no entran al ajuste; pérdidas en5/30 no excluyen automáticamente10/250. INVALID_RHO, presupuesto/timeout, parciales positivos pero status inválido, cola/cuadratura fuera de tolerancia; no imputación ni rescate.
- Perfil completo de estados y motivos, múltiples errores por fila conservados. Inconsistencias f/índices por split abortan. Falta de secundaria no contamina primaria, estratos pequeños quedan no definidos y c no filtra primaria.
- CLI con CSV/plan/resumen/compuerta sintéticos: salida válida etiquetada descubrimiento; BORRADOR rechaza tipo de datos reales; marker existente y colisión final conservados; JSON estricto sin NaN. La CLI mantiene5000 permutaciones; APIs de pruebas pueden usar B39 explícito.

Conservar todas las salidas, excepciones y fallos. Fixtures/arrays fuera de Git con SHA, código/protocolo/resultados/manifest dentro. Si hay defecto del verificador/analista tras ejecutar, enmienda comprometida antes de corregir y nueva versión de resultados; no sobrescribir. Sin Monte Carlo de potencia ni decisiones de F2 en estas pruebas. Crear un PR de borrador revisable, sin fusionar.
