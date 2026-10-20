# Anexo operativo de E1 — versión 1.1 (BORRADOR, no vigente, no congelado)

**Estado:** borrador propuesto el 2026-10-19 ≈23:40 (America/Mexico_City) a petición del responsable. **No está en vigor.** El anexo v1.0 congelado (SHA-256 `a7cb20d87f0c96b1962ccc56da15d0df23338c908659f3c469c12d5d93d84085`) sigue rigiendo todo hasta que este borrador se congele con hash y E1 lo cite en una versión nueva.
**Naturaleza:** presupuesto **operativo**, no evidencia científica. No clasifica, no asigna Y.

## 1. Alcance y motivación (declarados para que no se confundan)
- **Motivo único:** el piloto produjo una visita con evento candidato (`split10_j17_true`, `GEOMETRIC_NONINJECTIVITY`) y reveló que los topes de v1.0, calibrados con visitas sanas (j6: 60–145 s por visita, 187–653 intentos), quedan ajustados para el camino de refinamiento: 65 integraciones, 3341 intentos, 563 s de integración sobre un tope de visita de 900 s (63 %), y una integración de 8192 rayos de ≈ 99 s sobre un tope de 120 s (83 %). Una visita candidata con 16384 rayos pausaría por tiempo sin que haya fallo.
- **Qué NO es:** no es un rescate de las visitas pausadas. Las decisiones sobre `split8_j5`, `j7` y `j8` (mantener pausadas, 2026-10-19 22:40) **no cambian** y v1.1 **no se aplica retroactivamente** a ellas; el diagnóstico muestra que su obstáculo no es el presupuesto (paso ≈ 5×10⁻⁸–2×10⁻⁷ durante 350–430 pasos tras la alarma; ≈ 3×10⁵ pasos hasta r = 0.09). Tampoco cambia la alarma de progreso, el tope de intentos, el presupuesto adicional ni las reglas de revisión.
- **Evidencia de una sola visita candidata** (j17). Los valores son provisionales y no validados estadísticamente.

## 2. Cambios respecto a v1.0 (solo estos)
| # | v1.0 | v1.1 propuesto | Regla |
|---|---|---|---|
| T1 | Tope de tiempo por integración, float64: 120 s | **max(120 s, 0.04 s × n_rayos)** (n_rayos = número de ángulos de la integración: 2048 → 120 s; 4096 → 164 s; 8192 → 328 s; 16384 → 655 s) | j17 midió ≈ 0.012–0.014 s/ray (13 s a 1024, 28 s a 2048, 57 s a 4096, 99 s a 8192); 0.04 s/ray ≈ 3× lo medido. Para ≤ 2048 rayos el valor no cambia |
| T2 | Tope de tiempo por visita: 900 s | **900 s si la visita no entra a la etapa de refinamiento; 3600 s si entra** («candidata» = la condición `candidate` que ya calcula `topological_map.result`) | j17: 563 s de integración, 895 s de sesión; 3600 s ≈ 6× la integración medida y ≈ 4× la sesión |
| T3 | Reanudación | Sin cambio; el presupuesto adicional duplica los topes vigentes (T1 y T2 incluidos) | — |

Sin cambio: tope de intentos (250 por integración; la integración con más intentos en j17 usó ≈ 72), alarma de progreso (10⁻⁴ durante 8 pasos), presupuesto adicional de pasos e intentos, procedimiento de revisión (3.3), compuerta del piloto, tolerancias DOP853, A = 0.02.

## 3. Limitaciones
- Los múltiplos son una regla de margen sobre una visita candidata; una candidata de otro split podría necesitar más. La comprobación de memoria/E-S de los checkpoints con 16384 rayos (paquetes crecientes) no está medida.
- Aplica a float64. Para MPFR el tope por integración sigue siendo 3600 s.
- Requiere cambios en `visita_completa_instrumentada.py` (T1 por n_rayos y T2 por etapa); se implementarán y validarán **después** de congelar este anexo, repitiendo la prueba sobre j6 (debe seguir dando 15/15 PASS) y j17 (clasificación y radios sin cambio).

## 4. Para congelar
1. Revisión y aprobación (o ajuste) de T1 y T2 por el responsable, **antes** de ejecutar nuevas visitas candidatas con v1.1.
2. SHA-256 del anexo final → nueva versión de E1 que lo cite → SHA-256 → manifiesto y commit de congelación (orden de sellado de v1.0).
