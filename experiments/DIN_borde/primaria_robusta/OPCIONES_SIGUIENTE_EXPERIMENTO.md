# A2 · dos opciones para después de CIFAR-3

2026-11-02. **Propuesta para elección del responsable; no diseño congelado ni autorización de corridas.** No se generan ni reanalizan datos. La [primaria robusta](../PRIMARIA_ROBUSTA_v1.md) se adopta desde el inicio del experimento elegido, después de auditar A1. CIFAR-3 queda cerrado y sus semillas F2 siguen reservadas.

## 1. Prioridad recomendada: Q13, concentración frente a escala de logits

**Pregunta:** ¿se puede cambiar la escala de logits manteniendo aproximadamente la concentración de M, y viceversa? Si se consigue, ¿qué cambio acompaña a la señal temprana? [Q13-M2](../Q13M2/resultado/RESULTADO_Q13M2_2026-10-28.md) reprodujo MODULA con LP y WD, pero declara que no identifica c como causa; los tres mecanismos podrían mover también escala y confianza.

**Propuesta:** misma familia gaussiana s = .8 y MLP de G3, con semillas nuevas. Primero un piloto de separación, por ejemplo 20 splits × 5 inicios × 2 brazos entrenados (A0 y una dosis LP que se fijaría con calibración), pareados. Aplicar además tres temperaturas positivas prefijadas a los logits guardados, con la misma temperatura en u10 y u250. Son 200 entrenamientos y 600 celdas de geometría, no 600 entrenamientos. Recalcular X y el instrumento completo en cada celda: temperatura modifica probabilidades, gradientes, Fisher y ridge; **no equivale a multiplicar M por un escalar**. Registrar c, tr M, confianza y escala de logits, definida como RMS de los logits después de restar su media entre clases por ejemplo. Calibrar la separación usando esas cantidades, sin mirar D para elegir dosis o temperatura. Si no se separan, el piloto es INCONCLUSIVE para la identificación; no forzar un estudio de señal.

Como control algebraico previo: M → aM, con a > 0 común a las trayectorias de una celda, conserva c/q y produce rho → √a · rho. Los desplazamientos constantes de log rho desaparecen al centrar por split; no deberían cambiar D. Es un control de escala de la métrica, **no** una manipulación equivalente de logits ni una respuesta a la pregunta causal.

**Por qué aplica A1:** la primaria se calcula por celda, con NO_APRENDIO predeclarado, recorte y compuerta de influencia. El diseño debe fijar contraste principal entre celdas, dependencia pareada y multiplicidad antes de medir. Se empieza por factibilidad de separación, no por seis pruebas para elegir un PASS. No se reutilizan Q13-M2 o G3 como cohorte del nuevo estimando.

**Coste orientativo en el PC:** para el piloto, reservar **30–60 min**, más preparación y análisis. Es una extrapolación conservadora de 600 unidades completas al ritmo de CIFAR F1, no una medición de este factorial; las gaussianas y el entrenamiento compartido pueden abaratarlo. Un confirmatorio sería otra fase, con N fijado por potencia nueva.

**Riesgos:** la temperatura puede cambiar c y escala simultáneamente y redefine X/L/Y; emparejar dos resúmenes no prueba una intervención causal sobre c. El ridge depende de la carta y de gradientes, por lo que el control homogéneo de M debe separarse del experimento de logits. Veinte splits por celda no prometen potencia para detectar D pequeño. El piloto podría demostrar que el contraste propuesto no identifica la pregunta, lo cual también sería útil.

## 2. Otra familia real: Digits-3 con MLP pequeño

**Pregunta:** ¿hay señal temprana robusta en un conjunto estándar de imágenes sencillo, con una red que aprenda con suficiente frecuencia, sin reabrir CIFAR-3?

**Propuesta:** `sklearn.datasets.load_digits`, clases 0/3/8 fijadas antes de observar señal; referencia reducida = 8. MLP 64→64→32→3; 100 ejemplos de train por clase, panel de 9 por clase y test de 9 por clase, disjuntos dentro del split. Normalización ajustada en train y f de dos CP del panel, congeladas por split, como convención explícita del nuevo diseño. Evitar las primeras dos columnas crudas de píxeles como f: pueden ser constantes. Reutilizar el instrumento generalizado con cabeza reducida y su compuerta, sin cambiar rho r3. No se fijan aquí lr o dosis mirando resultados: el diseño posterior debe fijar receta, semillas y fase de factibilidad. Piloto operacional de 20 × 5, seguido, solo si se aprueba, por descubrimiento de aproximadamente 100 × 5.

**Por qué aplica A1:** mismo problema de tres clases, X10/L10/Y250 y universo por split; .5 es el criterio prospectivo de no aprender, no una exclusión elegida después. La fase operacional revisa entrenamiento, validez rho y costes; no selecciona clases o receta por D. El descubrimiento usaría la primaria robusta auditada y todas sus trayectorias planificadas. El MLP, la entrada y f cambian respecto de G3: se declara como otra familia, no como aislamiento de una sola variable.

**Coste orientativo en el PC:** reservar **5–15 min para el piloto de 100** y **25–50 min para 500**, más preparación; reconfirmar con una prueba corta antes de aprobar N. No se promete que 500 den potencia ni que el dataset muestre señal. El test pequeño solo describe clasificación, no generalización poblacional.

**Riesgos:** problema demasiado fácil (X saturada), falta de colapso o de variación entre inicios, PCs poco estables con 27 ejemplos y panel con pocos errores. La función de perspectivas es una elección nueva; no confundir cambio de f con transferencia de una geometría universal. No se puede extrapolar un eventual PASS a todas las imágenes.

## Cómo leer los costes y elegir

Referencia medida en el equipo del responsable: [CIFAR F1](../CIFAR/F1/resultado/RESULTADO_F1_2026-10-29.md), 500 trayectorias en 1.394 s con 12 procesos, aproximadamente **2,8 s de pared por trayectoria**, incluyendo dos llamadas rho; mediana de CPU 26,4 s y unos 741 MB por proceso. Las cifras anteriores reservan aproximadamente una a dos veces esa tasa para las unidades equivalentes, redondeadas y con margen operativo; **no son benchmarks de las opciones**. Geometría, saturación de CPU y paralelismo pueden cambiar el coste. El primer paso autorizado de una opción sería medir su coste con una prueba corta, nunca lanzar todo con esta estimación. No se han usado mediciones del contenedor como si fueran tiempos del PC.

**Recomendación:** opción 1 primero, limitada al piloto de separación, por su valor explicativo sobre una pregunta que Q13 dejó abierta; opción 2 si se prioriza transferencia a otra familia. En ambos casos, revisión de literatura y diseño auditado antes de afirmaciones de novedad o transferencia. Claude implementaría el productor tras la elección y congelación; no se instala Lean ni se invade esa tarea del reparto.
