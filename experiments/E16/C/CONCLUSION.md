# E16-C — Cierre de precisión de rango

**PASS_NUMERICAL: 99/99 resultados de rango; 54/54 controles negativos detectados.**
Nuevo protocolo instrumental congelado en `1b68c4e` antes del código y ejecución.
[E16-B](../B/CONCLUSION.md) permanece INCONCLUSIVE bajo su propio protocolo;
ningún archivo ni outcome de B se modifica. No se pretende confirmación empírica
nueva: se reusan explícitamente sus estados y datos conocidos para diagnosticar
instrumentación con otro método, autorizado por el usuario.

## Resultado principal

La referencia analítica explícita a 80/120 dígitos, autodiff float64 y diferencias
finitas centrales de cuarto orden concuerdan bajo todos los criterios congelados.
La comparación de errores se hace sobre U=B L, C=L Lᵀ, no sobre B aislada.

| Control u observable | Resultado |
|---|---|
| Configuraciones principales | 81/81 PASS_NUMERICAL, rango 2 |
| Constante en p (B=0) | 9/9, rango 0 |
| Filas duplicadas de B | 9/9, rango 1 |
| Omisión deliberada del término mixto | Detectada en 54/54 |
| Decisiones agregadas | 855 PASS; 0 FAIL; 0 INCONCLUSIVE |
| Descriptores sin criterio de decisión | 396 |
| Error transportado máximo autodiff, cota triangular | ≈1.577e−14 |
| Error transportado máximo FD4, δ=0.002 | ≈6.152e−11 |
| Error transportado máximo FD4, δ=0.001 | ≈3.845e−12 |
| Diferencia máxima U a 80 frente a 120 dígitos | ≈2.407e−80 |
| Menor σ_min entre las 81 configuraciones principales | ≈0.00250293 |
| Menor σ_min/τ principal | ≈250292.8 |

El error FD4 más desfavorable ocupa ≈3.2475% del límite τ/10 correspondiente.
Al dividir el paso a la mitad, el error cae por factores 15.99985–15.99997,
compatibles con orden cuatro. Esto contrasta con el factor ≈4 del método de B.
El prefactor de rango sigue siendo 1e−8; el método de derivación y el tratamiento
del error fueron fijados en un protocolo nuevo, sin relajar el anterior.

Producto, cuadrática y suma conservan rango 2 en los 27 casos de cada composición.
Los términos mixtos cambian las derivadas, pero aquí no cambian ese rango.
La validación de precisión no produce evidencia nueva de reducción dimensional,
emergencia ni ventaja predictiva. Las configuraciones tampoco son 81 réplicas
estadísticamente independientes.

## Qué permite afirmar el control

Se reconstruyeron de forma explícita los gradientes del logit y del log-likelihood,
las relevancias y los términos mixtos de B. La ruta FD evalúa sólo escalares del
forward, con caché de valores, sin usar gradientes de referencia. Autodiff deriva
directamente el escalar compuesto por una implementación nueva. La cométrica
regularizada se calcula en cada ruta, y se separan los errores transportados
de B y de L.

Se verificó la identidad

Uhat−U*=(Bhat−B*)L*+Bhat(Lhat−L*)

y la desigualdad triangular Frobenius entre esas matrices computadas. Los
márgenes espectrales están muy separados del corte. Los controles de rango cero
y uno impiden interpretar «todo tiene rango dos» como prueba de la instrumentación.
Los negativos muestran que conservar rango no basta para validar una derivada.

## Alcance de las cotas y límites

La desigualdad de normas es matemática. La referencia evaluada a alta precisión
es numérica: la concordancia 80/120 dps no da por sí sola una cota rigurosa de
error respecto del valor exacto. No hubo aritmética intervalar, certificado global,
ni demostración de rango constante en un abierto. PASS_NUMERICAL sólo se refiere
a los 99 puntos/configuraciones fijados y a los márgenes operacionales entre métodos.

Se usa g=F+0.01I y C=g⁻¹, no F⁺. El significado depende de esa regularización y
carta declaradas. No se entrenó ni se tocó T2-A. Este control resuelve la precisión
instrumental en estos puntos; no valida aprendizaje, generalización ni predicción.

## Ejecución, integridad y reanudación

[Resumen](results/run_v1/summary.json), [checks](results/run_v1/checks.csv),
[rangos](results/run_v1/ranks.csv), [negativos](results/run_v1/negative_controls.csv),
[descriptivos](results/run_v1/descriptive.json), [entorno](results/run_v1/environment.json),
[recursos](results/run_v1/resources.json). Corrida v1: ≈2.523 s, 36156 KiB máximos
registrados. No hubo fallos ni correcciones de implementación. Autodiff emitió
un aviso de independencia respecto de p para el control constante; ese cero es
esperado y fue contrastado con las otras rutas, no excluido.

Scripts, configuración, fórmulas y hashes permiten reproducir las tablas; tiempos
y entorno se guardan aparte. No se necesitan figuras ni binarios. La siguiente
pregunta científica exigiría un diseño sobre estados/paneles nuevos y una
hipótesis que vaya más allá de esta identidad algebraica. No se amplía de forma
automática a entrenamiento; el rango 2 observado no motiva por sí solo un
estudio predictivo. Los resultados de A/B siguen intactos.
