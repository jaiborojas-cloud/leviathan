# T2-A — diagnóstico del atasco en split8/j5/update25

Diagnóstico cerrado, no visita cerrada. Se examina el snapshot oficial de 512 pasos sin avanzarlo. Las 800 basales y el sello de predictores permanecen intactos. Sigue habiendo una visita completa de 8000 y tres parciales. No se asigna clasificación topológica ni desenlace nuevo.

## Hallazgo principal

La lentitud tiene una contribución numérica demostrada: unos pocos rayos entran en una región donde la métrica es casi degenerada en las coordenadas actuales. Sus velocidades coordenadas crecen, la evaluación float64 de la aceleración pierde precisión y el control adaptativo reduce el paso de todo el haz de 2048 rayos. No se ha demostrado una singularidad geométrica exacta, incompletitud geodésica, conjugado o cut locus.

| Evidencia al paso512 | Resultado |
|---|---:|
| Radio integrado (no radio nominal) | 0.07444033865530993 |
| Límite inicial de búsqueda conservado | 0.09 |
| Paso siguiente propuesto | 4.62224e-8 |
| Condición máxima de G | 8.91557e8 |
| Condición mediana de G | 22.7542 |
| Contribución de 5 rayos al término cuadrático del error E5 | 87.30% |
| Contribución de 10 rayos | 98.48% |
| Área diagnóstica del prefijo integrado | 0.01871507219 |
| Área requerida, sin cambios | 0.02 |

La condición indicada es la de G, no κ(Dexp), el predictor primario. Las fracciones de error corresponden al término E5 del último paso aceptado; no son fracciones de tiempo ni de probabilidad de fallo.

## Mecanismo observado

En el rayo1777, la norma de coordenadas aumenta de0 a286.44 y la velocidad coordenada de40.14 a1.379e6. La condición de G pasa de12 a7.252e8. Dos pesos softmax de la inmersión perspectival concentran99.21% del peso; esto es compatible con pérdida de rango efectiva del diferencial y mal acondicionamiento. No son probabilidades de salida del clasificador.

La velocidad intrínseca al cuadrado permanece aproximadamente cerca de1, pero su deriva acumulada alcanza ~6.9e-5 en el haz. Esa observación no certifica exactitud global: la tolerancia local del integrador no controla por sí sola el error al evaluar su ecuación diferencial.

Se comparó la aceleración de la fórmula congelada con la misma expresión matemática evaluada con80 y120 dígitos, manteniendo exactamente los mismos datos almacenados M,f,P,v. Ambas precisiones altas coinciden al redondear el resultado a float64. En el centro el desacuerdo relativo es2.39e-16; en los tres rayos difíciles examinados al paso512 es6.96e-7 a1.43e-6. Hay amplificación de redondeo y cancelaciones en la evaluación de la aceleración, no solamente necesidad de más pasos.

## Prueba local independiente

Se efectuó un único paso diagnóstico por rayo, desde el mismo estado, con DOP853 y las tolerancias originales. En el rayo1777, la fórmula original necesitó97 evaluaciones y aceptó8.27e-9. La evaluación de alta precisión necesitó13 y aceptó el ensayo4.62e-8, proponiendo después4.62e-7. Los otros dos rayos examinados mostraron el mismo patrón cualitativo.

Estas pruebas son de un rayo aislado (4 componentes), frente al haz oficial de8192 componentes. No equivalen a un benchmark de la visita completa ni prueban que toda la integración pueda completarse. La evaluación de alta precisión cuesta más por llamada. No se alteró ningún checkpoint oficial con sus resultados.

Como candidato puramente algebraico se evaluó a=-solve(G,Jᵀ M H[v,v]), evitando formar explícitamente G⁻¹ y contraer todo Γ. Mejoró el error puntual a5.38e-9…4.43e-8 en los tres puntos difíciles y evitó rechazos en la prueba local. Aún no hay validación suficiente para sustituir la implementación oficial o afirmar cumplimiento global de las tolerancias congeladas.

## El área aún no está alcanzada

La cuadratura original de32 anillos y grado5, aplicada solo a la salida densa disponible (sin extrapolar), da0.018715 al último radio. Los polígonos de los siete radios diagnósticos son simples. No se presenta esa cifra como A_embed certificado ni como límite geométrico: hay distorsión y no se efectuó una auditoría de convergencia/topología completa. Tampoco puede declararse alcanzada A=0.02 ni reducirse el objetivo a ese valor menor.

## Decisión y siguiente trabajo

No sumar pasos a ciegas ni aumentar tolerancias. Conservar la visita pendiente y el snapshot512. Separar tres preguntas: estabilidad de la evaluación de aceleración, dificultad de las coordenadas y posible límite geométrico real.

El siguiente trabajo adecuado es una validación instrumental aislada de la formulación estable y/o precisión selectiva, contrastada con referencia de alta precisión en regiones bien y mal condicionadas y con las compuertas congeladas. Solo después podrá decidirse si es una mejora equivalente de implementación o si exige una enmienda metodológica explícita. No se eliminan estados difíciles, no se cambia el dominio y no se convierte este diagnóstico exploratorio en evidencia predictiva.

## Persistencia y alcance

Se recuperaron y verificaron únicamente los archivos necesarios para este diagnóstico; no se repitió la auditoría histórica de800 basales. El diagnóstico anterior no había sobrevivido al reinicio del entorno: se reprodujo desde el snapshot verificado y se guardó por etapas en esta sesión. No se repitió entrenamiento ni ninguna visita cerrada. Proceso detenido; el checkpoint oficial sigue en512.

Fuentes reproducibles: stall_diagnostic_reproducible.py, stall_diagnosis_s512.json, rhs_precision_diagnostic_s512.json, stall_one_step_probe.py, stall_one_step_probe.json. Las tolerancias, umbrales, datos y clasificaciones oficiales permanecen sin cambios.
