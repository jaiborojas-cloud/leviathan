# E16-D — Cierre de réplica instrumental

**PASS_NUMERICAL: 396/396 decisiones de rango y 216/216 negativos detectados.**
Diseño congelado en `c360f56` antes del código y resultados. Nuevos pesos,
entradas y puntos principales frente a B/C; reutilización explícita del método
C y de sus tres rutas de cálculo. No hubo entrenamiento, reemplazos ni filtrado.

## Pregunta y resultado

Se puso a prueba la transferencia instrumental fuera de las configuraciones
usadas para seleccionar el método. Doce estados nuevos de red 2→2→1,
tres paneles y tres puntos/composiciones dieron 324 configuraciones principales.
Se añadieron 36 controles de rango 0 y 36 de rango 1. Todos cumplieron los
criterios congelados de precisión, margen y concordancia. El criterio conjunto
incluía detectar las 216 omisiones deliberadas de términos mixtos, también cumplido.

[Resumen](results/run_v1/summary.json): 5004 registros, de los cuales 3420 son
comprobaciones PASS y 1584 descriptores; cero FAIL e INCONCLUSIVE. No hay
correcciones de implementación ni corridas descartadas en esta fase.

| Observable | Resultado |
|---|---|
| Suma, producto y cuadrática | Rango 2 en 108 casos cada una |
| Tríos comparables con precisión validada | 108/108 |
| Cambios de rango producto vs suma | 0/108 |
| Cambios de rango cuadrática vs suma | 0/108 |
| Grupos estado/punto/composición estables entre paneles | 108/108 |
| Menor σ_min de configuraciones principales | ≈0.0193687 |
| Menor σ_min/τ principal | ≈1.937e6 |
| Error transportado autodiff máximo | ≈3.863e−14 |
| Error transportado FD4 máximo, δ=0.002 | ≈1.154e−10 |
| Error transportado FD4 máximo, δ=0.001 | ≈7.214e−12 |
| Diferencia U a 80/120 dígitos máxima | ≈3.532e−80 |

El error FD4 máximo relativo al límite τ/10 de su caso ocupa ≈2.622% del mismo.
Al dividir el paso por dos, los cocientes de error están entre 15.99974 y
16.00004, compatibles con orden cuatro. Los valores singulares principales
quedan muy separados del corte y se transportan errores de B y L antes de
compararlos. No se relajó la tolerancia del método C para hacer pasar D.

## Qué respalda y qué no

El método pasó una réplica instrumental preespecificada sobre configuraciones
nuevas. Eso respalda su uso numérico en este rango moderado de pesos y entradas
para este estimando regularizado g=F+0.01I. Reutilizar código no añade otra
implementación independiente: las tres rutas son las mismas del método C.
Los cambios explícitos de adaptación quedan en
[scripts/adaptation_from_C.patch](scripts/adaptation_from_C.patch).

Los términos mixtos son detectables, pero no produjeron diferencia de rango
frente a la suma. No se observó reducción dimensional por estas composiciones.
Ese resultado no demuestra imposibilidad universal ni emergencia; sí impide
atribuir a esta réplica un efecto de rango que no apareció. Aumentar estados
retrospectivamente para buscarlo cambiaría el diseño.

Los 396 casos no son 396 réplicas estadísticas independientes: hay 12 vectores
de pesos que comparten datos, paneles y perspectivas. No se calcula intervalo
binomial de población ni se estima causalidad o generalización. Las etiquetas
son sintéticas y no se optimizó la red.

La referencia 80/120 dps no es aritmética intervalar: las cotas de normas son
entre matrices computadas, no certificados rigurosos frente al valor exacto.
No se prueba rango constante sobre un abierto ni canonicidad de C. El outcome
INCONCLUSIVE de B y el PASS_NUMERICAL de C se conservan bajo sus protocolos.

## Persistencia y continuación

Tablas: [checks](results/run_v1/checks.csv), [rangos](results/run_v1/ranks.csv),
[negativos](results/run_v1/negative_controls.csv),
[comparaciones](results/run_v1/paired_compositions.csv),
[paneles](results/run_v1/panel_sensitivity.csv),
[descriptivos](results/run_v1/descriptive.json),
[resumen secundario](results/run_v1/secondary_summary.json).
[Entorno](results/run_v1/environment.json) y [recursos](results/run_v1/resources.json):
≈13.981 s, 38588 KiB máximos registrados; presupuesto 120 s cumplido.
Autodiff emitió su aviso esperado de independencia en p para el control constante;
no se ocultó ni se excluyó ese control. Las tres rutas comprobaron su rango cero.

Los scripts reproducen la entrega en salidas nuevas, sin reabrir ni ejecutar
A/B/C o T2-A. Para continuar la ciencia hace falta una pregunta distinta y
operacionalmente definida sobre geometría, con diseño previo. Este resultado
no justifica entrenar automáticamente ni repetir la misma búsqueda de rango
hasta obtener un cambio. [Decisiones y pasos posteriores](NEXT_PHASE.md).
