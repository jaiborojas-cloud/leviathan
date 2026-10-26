# DIN-D9g-b — conclusión exploratoria

**ARTEFACTO_DE_BASE_LINEAL_EXPLORATORIO**, según la regla congelada: en s=.8, B3 y B4 tienen D≤0. **c30 no conserva el incremento fuera de muestra con las bases flexibles fijadas.**

**La etiqueta es operacional.** No demuestra que una no linealidad barata sea la causa única del resultado D9g. B3/B4 predicen peor que B1 como bases solas y las mitades muestran D inestables. Es compatible con sobreajuste/variabilidad de las bases no regularizadas, además de posible redundancia de c30. No se separan esas explicaciones aquí.

## s=.8: las cuatro bases prefijadas

| Base | Términos | D adicional c30 | p exploratorio | β c30 | D_base sola | β pares / impares | ¿D>.01, p<.0125 y signo? |
|---|---|---:|---:|---:|---:|---|---|
|B1|4 lineales|0.021854|0.001000|-0.040886|0.075126|-0.041102 / -0.042509|sí|
|B2|+ cuadrados/cubos (12)|-0.016018|0.998501|-0.041604|0.063988|-0.041882 / -0.041454|no|
|B3|+ 6 interacciones (18)|-0.007763|0.862069|-0.044180|0.019266|-0.048143 / -0.035841|no|
|B4|+ margen/entropía/norma (21)|-0.008598|0.885557|-0.054354|0.011801|-0.058812 / -0.041257|no|

B1 reproduce D9g (D=.02185384449, p=.00099950025); no se invalida ni reescribe esa conclusión previa sobre una base lineal. B2/B3/B4 no cumplen la regla de robustez: el incremento es negativo en las tres. Las pendientes siguen negativas y de signo estable; esa estabilidad de coeficiente no basta para mejorar predicción fuera de muestra.

La caída del rendimiento de las bases solas es material: D_base=.075126→.063988→.019266→.011801. No se observa que estas bases flexibles predigan mejor y dejen a c30 sin información. Las bases están anidadas en entrenamiento; su error de CV puede empeorar por estimación y extrapolación. Por eso «artefacto» no debe leerse como demostración de absorción de no linealidad.

## Mitades prefijadas en s=.8

| Base | D adicional pares | D adicional impares | signo β estable |
|---|---:|---:|---|
|B1|0.009146|0.010758|True|
|B2|0.030980|-0.211675|True|
|B3|0.068199|-0.032253|True|
|B4|0.062721|-0.045990|True|

Las mitades flexibles difieren marcadamente en D; no se escogen particiones ni se descartan splits. Rangos efectivos en s=.8:4,12,18,21; condición máxima de términos no nulos≈2.19,19.90,37.86,38.20 respectivamente. No aparece pérdida de rango de la base en ese nivel. Los controles numéricos distinguen error de implementación de inestabilidad estadística.

## Otros niveles y agregado: sólo descriptivos

| Conjunto | B1 D / p | B2 D / p | B3 D / p | B4 D / p |
|---|---|---|---|---|
|s=.25|0.063287 / 0.000500|-0.003558 / 0.526237|-0.004342 / 0.608196|-0.019027 / 0.999000|
|s=.5|0.048894 / 0.000500|0.009926 / 0.037481|-0.240252 / 1.000000|-0.167528 / 1.000000|
|s=.8, decide|0.021854 / 0.001000|-0.016018 / 0.998501|-0.007763 / 0.862069|-0.008598 / 0.885557|
|agregado|0.021345 / 0.000500|-0.032623 / 1.000000|-0.004582 / 0.993503|-0.003367 / 0.968016|

Ningún conjunto cumple robustez con todas las bases flexibles. s=.25/.5 y agregado no cambian la decisión primaria. El agregado centra/permutan en (nivel,split) y deja los tres niveles del mismo split juntos en cada bloque; pendientes comunes. Se conservan los 16 resultados, coeficientes, mitades, controles D_base y transformaciones por bloque.

## Controles e integridad

- Positivo con señal residual independiente: D≈.761/.904/.929/.930 para B1–B4, p=.000500 en las cuatro, pendiente positiva estable. Demuestra detección de una señal grande; no demuestra potencia para D≈.01–.02.
- Negativo: c_hat_j de la MISMA base B_j, ajustado sólo en entrenamiento. |D|≤2.22e-16 en controles artificiales y ≤1.33e-15 en las 16 celdas reales. Coeficiente no identificable por alias; no se interpreta como efecto cero estimado.
- Función barata no lineal: c=q0², Y=q0²+ruido. D≈.995 con B1 y |D|<3e-15 con B2–B4. Una función de medidas baratas puede añadir predicción a B1 si B1 no la representa: no es por sí solo sesgo.
- FWL vs OLS directo: todos los 2.001 D en cuatro controles, error máximo2.89e-15, p idéntica. B1 reproduce los cuatro conjuntos D9g con error≤3.34e-16 y p idéntica.
- Todas las transformaciones se ajustan sólo con entrenamiento exterior, incluyendo mu/sigma, potencias, productos y escalado de términos; mitades reajustadas. No B5, tuning o selección posterior.
- [verification.json](verification.json): **PASS**, 1500 filas, 16 celdas, 3324 archivos externos por SHA. La pérdida test250 y c30/medidas baratas se copiaron exactamente de D9g. 1.500 paneles/pesos u30 restaurados sin fallos; test no se regeneró ni reevaluó.

## Recomendación al responsable y límites

**Posponer el confirmatorio de c30 apoyado sólo en D9g.** La señal no pasó esta prueba de robustez. Si interesa distinguir redundancia real de sobreajuste de bases flexibles, registrar otro estudio de descubrimiento con regularización/suavizado y selección de complejidad mediante CV anidada, antes de mirar sus resultados. No añadir B5 ahora: se excluyó antes del código. El responsable decide si vale la pena ese estudio y si después procede confirmar.

**C2 sigue intacta y reservada.** No se accedió a su cohorte, estados, checkpoints ni test/asociaciones. No Wine/Iris/T2/DIN-C1. No se modificó D9g ni otra etapa. Sin reentrenamiento, nueva geometría ni test nuevo.

Las medidas B4 son resúmenes de logits/probabilidades y de parámetros; no son argumentos nuevos de M, pero comparten información con su construcción. La norma de pesos depende de la parametrización; no es una nueva cantidad geométrica invariante. Las identidades algebraicas de M no demuestran esta lectura de CV ni una causa del resultado.

Exploratorio, sin afirmaciones confirmatorias, causales o de transferencia. La regla evalúa estas bases concretas no regularizadas, no toda función barata. La permutación no garantiza calibración bajo cualquier misspecificación; el negativo sólo valida redundancia en el espacio de cada base. El centrado de Y usa medias finales del split, como D9g; no es un predictor desplegable sin esas medias. La prueba positiva grande no da potencia conocida para efectos pequeños. Todos los splits y salidas se conservan, sin sustituciones ni nuevos umbrales.

[Diseño](DESIGN_FROZEN.md) · [configuración](config.json) · [16 estimaciones](results/run_v1/estimates.csv) · [salida íntegra](results/run_v1/analysis.json) · [controles](results/run_v1/controls.json) · [teoría](THEORY.md).
