# Resultados negativos, fallos y límites que deben conservarse

No todos los registros son refutaciones: se distingue efecto no respaldado,
fallo del instrumento, pérdida de cobertura e interpretación no autorizada.
Las fuentes y dominios están en el [mapa de afirmaciones](claims-and-evidence.md).

| ID | Registro conservado | Tipo | Lo que impide concluir | Qué haría falta para avanzar |
|---|---|---|---|---|
| N01 | E10-C: accuracy se separó antes que la geometría | Anticipación no respaldada en ese diseño | RIPG no quedó validado como señal funcional más temprana | Otra pregunta y datos nuevos con comparación temporal prospectiva |
| N02 | E10-D/E: desplazamiento no monótono con corrupción; pico no replicado | Regularidad propuesta no sostenida | No hay máximo universal de «frustración» establecido | Hipótesis definida antes de otro barrido, sin elegir pico retrospectivo |
| N03 | E10-F/G y E11: predictor incremental no robusto y signos dependientes de alcance | Límite empírico condicionado | Mayor $D_G$ no equivale a mejor aprendizaje; tampoco se prueba independencia condicional | Baselines, panel y validación externa nuevos |
| N04 | E11-E: misma red, métricas distintas bajo reescala no ortogonal | Fallo del estimador de rango crudo | Un contraste estadístico no subsana un defecto de covariancia | Referencia transportada y control de panel/rango; preservar resultado original |
| N05 | E13: réplica externa con 3/40 pares incluidos | Pérdida instrumental de cobertura, INCONCLUSIVE | Los supervivientes no confirman la hipótesis primaria; no se demuestra fallo del campo exacto | Construcción regional positiva validada y réplica independiente |
| N06 | C1-A2: dos casos GEOMETRIC_NONINJECTIVITY; C1-A sigue INCONCLUSIVE | Obstrucción geométrica del dominio nominal | No reducir el área ni excluir estados para rescatar C1; no se certifica corte exacto | Observables de dominio bajo diseño propio, sin alterar C1 |
| N07 | T1-B: asociación simultánea compatible con Jacobi | Límite de interpretación | Correlación alta no es predicción temporal ni evidencia causal nueva | Cohorte y evento futuros, con seguimiento completo y criterio congelado |
| N08 | E16-B: diferencias finitas insuficientes para su compuerta de rango | INCONCLUSIVE instrumental | Autodiff rango 2 no reemplaza validación independiente | Otro protocolo de precisión, preservando el outcome de B |
| N09 | E16: agregaciones sin descenso y agregación válida con rango conservado | Contraejemplos matemáticos | Ni toda agregación define métrica heredada ni toda agregación reduce estrictamente rango | Declarar mapa, horizontalidad y dependencia de representante |

| N10 | T2-A0: visitas sin cerrar (pausas, disco, T5) | INCONCLUSIVE instrumental | No hay veredicto sobre la no inyectividad futura | Instrumento viable (lo resolvió el cambio de desenlace a ρ_borde) |
| N11 | T2-A1: X (update 5) no predice ρ_borde futuro | Efecto no respaldado (confirmatorio) | X no anticipa la degeneración en Wine | Otro predictor u otro momento (DIN-C1 mostró que la confianza en el update 10 sí) |
| N12 | DIN-D5: ningún candidato del update 50 aporta más allá de la persistencia | Límite empírico exploratorio | Medir en el 50 es demasiado tarde: ya es casi el desenlace | Ventana más temprana (D6) |
| N13 | DIN-G1: la señal temprana no se reproduce en Iris (D < 0) | No replicado (exploratorio) | El PASS de DIN-C1 no se generaliza automáticamente | Confirmatorio propio en otra familia, con la variación en la resolución final como posible condición |
| N14 | ρ_borde v1: falla en paneles degenerados sintéticos (D2 Q5) y no alcanza las normales de las aristas (G1) | Límite del instrumento | La «distancia al borde» de v1 es el mínimo de rayos a un vértice | ρ_borde v2 con caras completas (DIN-I2) y reevaluación declarada |

## Fuentes por registro

- N01–N03: [cierre E10](../archive/import-2026-10-17/originals/Cierre_E10_RIPG_y_ruta_E11.md)
  y [estado E11-C](../archive/import-2026-10-17/originals/Estado_hipotesis_RIPG_E11C.md).
- N04: [invariancia E11-E](../archive/import-2026-10-17/originals/E11E_invariancia_de_carta_y_rango_Fisher.md).
- N05: [cierre E13](../archive/import-2026-10-17/originals/E13_cierre_y_punto_de_partida_E14.md).
- N06: [cierre C1-A2](../archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_E15-C1-A2_cierre.md).
- N07: [cierre T1-B](../archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_E15-T1-B_cierre.md).
- N08: [conclusión E16-B](../../experiments/E16/B/CONCLUSION.md).
- N09: [especificación E16](../../experiments/E16/mathematical_spec.md).
- N10: [cierre T2-A0](../../experiments/T2_A/claude/CIERRE_T2A0_v1_CONGELADO.md).
- N11: [cierre T2-A1](../../experiments/T2_A1/CIERRE_T2A1_v1_CONGELADO.md).
- N12: [D5](../../experiments/DIN_borde/RESULTADO_D5_2026-10-24.md).
- N13: [G1](../../experiments/DIN_borde/G1/CONCLUSION.md).
- N14: [D2](../../experiments/DIN_borde/D2/CONCLUSION.md), [G1](../../experiments/DIN_borde/G1/CONCLUSION.md), [sensibilidad C1](../../experiments/DIN_borde/C1/sensibilidad_aristas/SENSIBILIDAD_ARISTAS_2026-10-25.md).

## Errores corregidos sin borrar historia

E16 conserva una interrupción de escritura de progreso y una referencia manual
cuadrática fallida, con [fe de erratas](../../experiments/E16/ERRATA_v2.md).
E16-B conserva un verificador que comparaba indebidamente la duración como
resultado determinista; su [diagnóstico](../../experiments/E16/B/results/verification_v1_diagnostic.json)
muestra la fila diferente. Son errores de implementación/documentación registrados,
no refutaciones de pullback, regla de cadena o rango. La corrección se evalúa en
su versión nueva; no reemplaza el archivo fallido.

No hay aquí una nueva decisión FAIL/INCONCLUSIVE sobre ninguna etapa. El catálogo
organiza cierres existentes y evita que una conclusión antigua se promocione por
selección de estados o por un cambio retrospectivo de lenguaje.
