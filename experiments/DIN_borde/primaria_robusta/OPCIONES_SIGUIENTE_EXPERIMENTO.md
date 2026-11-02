# A2 · dos opciones para el siguiente experimento

2026-11-02. **Propuesta para elección del responsable; sin datos nuevos, diseño congelado ni autorización de corridas.** Ambas opciones usan la [primaria robusta](../PRIMARIA_ROBUSTA_v1.md), tras auditar A1. CIFAR-3 sigue cerrado y su reserva F2 no se reasigna.

## 1. Recomendada: Q13, concentración frente a escala de logits

**Pregunta:** ¿se puede variar la escala de logits manteniendo aproximadamente c, y viceversa? [Q13-M2](../Q13M2/resultado/RESULTADO_Q13M2_2026-10-28.md) reprodujo MODULA con LP/WD, pero no identifica al colapso como causa: los mecanismos podrían mover también escala y confianza.

**Propuesta:** piloto con gaussianas s = .8 y MLP de G3, semillas nuevas; por ejemplo 20 splits × 5 inicios × 2 brazos entrenados (A0 y una dosis LP por calibrar), pareados. Aplicar tres temperaturas positivas prefijadas a los logits guardados, iguales en u10/u250: **200 entrenamientos y 600 celdas de geometría**. Recalcular X y el instrumento completo por celda; temperatura cambia probabilidades, gradientes, Fisher y ridge, no es un reescalado de M. Registrar c, tr M, confianza y RMS de logits centrados entre clases por ejemplo. Elegir la calibración mirando solo separación de esas cantidades, nunca D; si no se separan, reportar identificación inconclusa y detener esa vía.

Control algebraico: M → aM conserva c/q y da rho → √a · rho. Para a común dentro de una celda, los desplazamientos constantes de log rho se eliminan al centrar por split y no cambian D. **Esto controla escala métrica, no equivale a temperatura de logits.**

**Coste PC orientativo:** reservar **30–60 min** para el piloto, más preparación; son unidades equivalentes conservadoras, no un benchmark. **Riesgos:** temperatura redefine X/L/Y y puede cambiar c simultáneamente; emparejar resúmenes no identifica causalidad. Veinte splits no prometen potencia. La primaria robusta aplica por celda, conservando NO_APRENDIO e influencia; el diseño deberá fijar el contraste pareado y multiplicidad antes de estudiar señal, sin escoger un PASS entre seis pruebas.

## 2. Otra familia real: Digits-3 con MLP pequeño

**Pregunta:** ¿aparece señal temprana robusta en imágenes sencillas con una red que aprenda frecuentemente, sin reabrir CIFAR?

**Propuesta:** `sklearn.datasets.load_digits`, clases 0/3/8 prefijadas, referencia reducida 8; MLP 64→64→32→3. Train de 100 por clase, panel y test de 9 por clase cada uno, disjuntos. Normalización ajustada en train; f de dos CP del panel, congeladas por split: las primeras columnas crudas de píxeles pueden ser constantes. Instrumento generalizado con cabeza reducida, compuerta y rho r3 intactos. Piloto operacional de **20 × 5**, seguido solo si se aprueba por descubrimiento de aproximadamente **100 × 5**. El diseño posterior fija receta y semillas antes de medir; estas cifras no son N de un confirmatorio.

**Coste PC orientativo:** **5–15 min** para 100 y **25–50 min** para 500, más preparación. **Riesgos:** X saturada por facilidad, falta de colapso o variación entre inicios y PCs inestables con 27 ejemplos. Dataset, entrada y f cambian: es otra familia, no un aislamiento de una variable. A1 fija prospectivamente .5, recorte e influencia; el piloto revisa entrenamiento, validez rho y coste, sin seleccionar clases o receta por D. Un eventual PASS no se transfiere a todas las imágenes.

## Costes y decisión

Referencia del PC: [CIFAR F1](../CIFAR/F1/resultado/RESULTADO_F1_2026-10-29.md), 500 trayectorias en 1.394 s con 12 procesos, **2,8 s de pared por trayectoria** y dos llamadas rho. Los presupuestos extrapolan aproximadamente una a dos veces esa tasa, redondeada; las gaussianas y el entrenamiento compartido podrían abaratarla. No se midieron las opciones ni se usó tiempo del contenedor como tiempo del PC. Una prueba corta deberá actualizar el presupuesto antes de lanzar la muestra.

**Recomendación:** opción 1, limitada primero a separación operacional, por la pregunta explicativa abierta de Q13; opción 2 si se prioriza otra familia. Literatura y diseño auditado antes de novedad o transferencia. El responsable elige; Claude implementa el productor después de congelar. No se invade el piloto Lean de su reparto.
