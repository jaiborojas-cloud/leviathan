# Primaria robusta de DIN · v1 (adoptada el 2026-11-02)

**Decisión del responsable (2026-11-02, 10:31):** «adoptar la primaria robusta». Se basa en la [revisión exploratoria de la primaria](revision_primaria/REVISION_PRIMARIA_2026-10-29.md).

**Alcance:** rige **solo para diseños nuevos**. C1, C2, Q13 (todas sus variantes) y CIFAR F1 conservan sus primarias congeladas y sus veredictos. Esta página fija la especificación. Su implementación (analista, pruebas y SHA) se congela y audita dentro del primer diseño que la use, antes de ver sus datos.

## Lo que se mantiene de la primaria de C1
- X = X10, L = log ρ_caras(10) e Y = log ρ_caras(250).
- Todo centrado dentro del split, con pendientes comunes.
- D = 1 − SSE_completo / SSE_base, fuera de muestra, sin truncar.
- Base de grado 3; 10 bloques de splits con `default_rng(260010)`.
- 5000 permutaciones de X dentro del split con `default_rng(260001)`.
- p = (1 + #{D_perm ≥ D − 1e−15}) / 5001.
- Compuertas de calidad: faltantes ≤ 5 % y al menos 80 % de los splits con 3 o más trayectorias elegibles.

## Tres cambios
1. **Criterio de entrenamiento fallido, predeclarado.**
   - Si la precisión de entrenamiento en la última visita es **menor que 0.5**, la trayectoria es **«no aprendió»**: con 3 clases, eso está cerca del azar.
   - Cuenta como **faltante** con ese motivo: entra en el umbral del 5 %, se reporta con su ID y nunca se sustituye.
   - El umbral no se ajusta después de ver datos. En CIFAR F1 solo lo cumplía una trayectoria, y la siguiente estaba en 0.77; en Wine, ninguna.
2. **Base cúbica recortada, sin extrapolación.**
   - z = (L − media) / DE, con ddof = 0 y la media y la DE de las L elegibles, como en C1.
   - Dentro de cada bloque, la z de prueba se **recorta al intervalo [min, max] de las z de entrenamiento** de ese bloque, antes de formar z, z² y z³ y centrarlas dentro del split.
   - Dentro del rango observado es idéntica a la de C1: en Wine da el mismo D (±0.001).
3. **Compuerta de influencia.**
   - Contribución de cada trayectoria a la mejora: g_i = e_base,i² − e_completo,i², con los errores fuera de muestra de la propia primaria.
   - Se reporta la fracción max g_i / Σ g_i, y **D_sin_max**, es decir, D recalculado sin la trayectoria de mayor g_i (bloques recalculados con la misma regla).
   - **PASS = p < 0.05, D > 0, pendiente > 0 y D_sin_max > 0.** Si las tres primeras se cumplen pero D_sin_max ≤ 0, el veredicto es **NO_ROBUSTO**: no es PASS, aunque se reportan todos los valores.

## Secundarios recomendados (descriptivos)
- La misma primaria con la base de rangos (puntajes normales del rango de L) y con el spline natural.
- La base de grado 5 con la misma regla de recorte.

## Pendiente
El primer diseño que la use debe implementarla y probarla con fixtures sintéticos que incluyan:
- una trayectoria que no aprende;
- una L extrema (|z| > 10);
- equivalencia exacta con C1 cuando no hay recorte.
