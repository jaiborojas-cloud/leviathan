# Leviathan / RIPG — Dictamen técnico sobre la sección 6 de E1 para E2

**Versión:** 1.0  
**Fecha:** 21 de octubre de 2026 (America/Mexico_City)  
**Veredicto técnico:** APROBABLE CON CAMBIOS, exclusivamente como análisis exploratorio de sensibilidad.  
**Estado:** revisión técnica; no congela E2, no autoriza su aplicación ni modifica T2-A0.

## 1. Autoría, alcance y material revisado

**Revisor:** ChatGPT, asistente de IA de OpenAI. Sin afiliación académica ni representación institucional. El asistente participó previamente en el proyecto; esta revisión no es independiente del desarrollo y no acredita el cumplimiento del requisito vigente de dictamen externo independiente.

**Material principal:** `T2-A0 solicitud de dictamen estadístico (sección 6 de E1).md`, documento aportado por el responsable, fechado el 21 de octubre de 2026. La presente revisión responde a sus cinco preguntas y al método allí reproducido.

**Límites:** no se ejecutaron experimentos, no se certificaron los cálculos geométricos de T5 y no se verificaron los hashes abreviados de la solicitud. No se afirma haber auditado íntegramente E2 v2 ni el código de certificación. La recomendación no constituye una decisión del responsable ni una aprobación institucional.

Se mantiene la opción E2-C: predictor, cola, desenlace, compuertas, criterios confirmatorios y bootstrap de T2-A0 permanecen intactos. Ningún resultado de la sección 6 puede convertir un INCONCLUSIVE en PASS.

## 2. Corrección obligatoria de las cotas

La regla general de la solicitud debe corregirse. La asignación «desconocidos dentro de la cola → 0; fuera → 1» minimiza la diferencia entre precisión y tasa base y, cuando está definido, el lift. **No minimiza la tasa base**, que aumenta con cualquier positivo, dentro o fuera de la cola. La precisión no depende de las asignaciones fuera de la cola.

Definiciones, para una cohorte elegible fija y una cola determinada exclusivamente por X:

- N: número de trayectorias elegibles.
- m: tamaño de la cola, con 0 < m ≤ N.
- a, b: positivos confirmados dentro y fuera de la cola.
- u, v: desenlaces no determinados dentro y fuera de la cola.
- x ∈ {0,…,u}, y ∈ {0,…,v}: números de positivos asignados entre los desconocidos de cada grupo.

Las métricas de cada completación son:

$$
P(x,y)=\frac{a+x}{m},\qquad
B(x,y)=\frac{a+b+x+y}{N},\qquad
D(x,y)=P(x,y)-B(x,y).
$$

Cuando B(x,y)>0:

$$
L(x,y)=\frac{P(x,y)}{B(x,y)}
=\frac{N(a+x)}{m(a+b+x+y)}.
$$

Los extremos exactos sobre las completaciones binarias libres son:

| Métrica | Mínimo | Máximo |
| --- | --- | --- |
| Precisión | a/m | (a+u)/m |
| Tasa base | (a+b)/N | (a+b+u+v)/N |
| Diferencia | a/m − (a+b+v)/N | (a+u)/m − (a+b+u)/N |
| Lift, si a+b>0 | Na/[m(a+b+v)] | N(a+u)/[m(a+b+u)] |

Para la diferencia, incrementar x cambia D en 1/m−1/N ≥ 0; incrementar y la cambia en −1/N. Para el lift, añadir positivos dentro no lo reduce y añadirlos fuera no lo aumenta, siempre que esté definido. Esto justifica los extremos correspondientes. La tasa base se minimiza asignando todos los desconocidos a cero y se maximiza asignándolos todos a uno.

Estos son extremos alcanzables sobre completaciones de la cohorte observada, no intervalos de confianza poblacionales. No requieren independencia entre trayectorias para su validez algebraica. Si existen restricciones adicionales sobre las asignaciones, deben declararse; las fórmulas anteriores corresponden al conjunto libre especificado en la solicitud.

### 2.1 Desenlace desconocido frente a desenlace no definido

Un desenlace no observado y un desenlace estructuralmente no definido no son equivalentes. Si T5 impide definir el evento original en una visita, las asignaciones binarias deben describirse como **escenarios hipotéticos de completación**, sin afirmar que recuperan un valor binario necesariamente existente.

Para hablar de identificación parcial de un parámetro binario latente se requiere que ese parámetro esté bien definido. Mientras esto no se establezca para todos los casos T5, el nombre recomendado es **análisis exploratorio de sensibilidad por completaciones binarias**.

## 3. Respuestas a las preguntas del dictamen

### 3.1 Cobertura de la envolvente bootstrap

La expresión

$$
[Q_{0.025}(L^*),\;Q_{0.975}(U^*)]
$$

puede reportarse como **envolvente exploratoria de remuestreo de cotas; cobertura nominal no validada**. Aquí L* y U* designan los extremos de la métrica en cada réplica, no necesariamente el lift. No debe denominarse «IC95 %» del parámetro ni de toda la región identificada.

Imbens y Manski distinguen la cobertura del parámetro de la cobertura de su región identificada [1]. Esa distinción es pertinente, pero citar o adoptar el nombre del método no valida automáticamente este diseño.

Una interpretación inferencial exige justificar el mecanismo de muestreo de splits, el comportamiento de los estimadores de los extremos, la selección de cola con empates y los denominadores. La discontinuidad de la selección por rango y los casos degenerados requieren atención expresa. Veinte mil remuestreos reducen error Monte Carlo; no garantizan cobertura estadística.

Para este análisis exploratorio puede conservarse el remuestreo de splits completos, con 20 000 réplicas, semilla 220020 y recálculo de la cola en cada réplica, sin atribuirle cobertura nominal validada.

### 3.2 Lift no definido

Se recomienda conservar el tratamiento prudente propuesto:

- No asignar cero, infinito ni un denominador artificial cuando la tasa base sea cero.
- Registrar las completaciones y réplicas donde el lift no esté definido.
- No eliminarlas silenciosamente para calcular percentiles sobre las restantes.
- Si alguna completación compatible tiene tasa base cero, el intervalo global del lift queda **NO EVALUABLE** bajo el procedimiento propuesto.

Pueden presentarse extremos restringidos a completaciones con tasa base positiva, declarando esa restricción y sin describirlos como extremos sobre todas las completaciones. Si no existe ninguna completación con tasa positiva, tampoco existen esos extremos restringidos. Precisión, tasa base y diferencia siguen siendo reportables cuando N y m son positivos.

### 3.3 Informatividad con muchos desenlaces no determinados

Se deben publicar siempre las cotas, aunque sean amplias. No se recomienda un umbral nuevo para suprimir resultados.

Reportar amplitud, número y ubicación de desconocidos, y si las cotas permiten determinar el signo de la diferencia o la posición del lift respecto de 3. Cruzar esos valores indica falta de resolución para esa pregunta; no produce un PASS o FAIL. Una cota amplia sigue documentando el límite informativo del estudio.

### 3.4 Dependencia y concentración por split

La concentración por split no invalida las cotas algebraicas de la cohorte. Sí afecta la incertidumbre y la extrapolación.

Remuestrear splits completos conserva la dependencia interna de las inicializaciones, pero su interpretación exige justificar los splits como unidades de remuestreo bajo el mecanismo de partición e inicialización. El solapamiento de ejemplos Wine limita la interpretación a ese dataset y mecanismo; no equivale a disponer de tareas o datasets independientes.

Con solo cuatro splits en el piloto no se atribuye cobertura nominal al procedimiento. Se recomienda reportar los conteos por split y la sensibilidad al retirar cada split, recalculando la cola y las cotas conforme a la regla declarada.

### 3.5 Historial de las cuatro corridas de certificación T5

Las cuatro corridas constituyen un historial de desarrollo y corrección de implementación; no son cuatro réplicas independientes.

Deben conservarse los defectos detectados, cambios, resultados y hashes de cada versión. La coincidencia desde la segunda corrida aporta estabilidad frente a esas correcciones; no demuestra ausencia de errores compartidos ni satisface por sí sola E1 §5.1.

Mientras j5 mantenga la misma disposición confirmatoria, cambiar su etiqueta diagnóstica no modifica las cotas. Deben separarse el estándar numérico del protocolo T5 y el estándar de certificación de E1 §5.1.

## 4. Criterios 3–6: límite de la evaluación «bajo todas las asignaciones»

No debe agruparse el criterio inferencial 5 con los criterios puntuales como si todos se resolvieran mediante las mismas fórmulas.

- **Criterio 3:** el mínimo de eventos y de splits con eventos se evalúa contando únicamente positivos confirmados; las completaciones pueden añadir positivos, no eliminarlos.
- **Criterio 4:** el lift mínimo permite evaluar el umbral puntual de 3 cuando el lift está definido para todas las completaciones.
- **Criterio 6:** se retira cada split, se recalcula la cola y se obtiene la diferencia mínima; esto permite comprobar el signo bajo todas las completaciones de cada muestra reducida.
- **Criterio 5:** una cota puntual de la diferencia no demuestra que el límite inferior del intervalo original sea positivo bajo todas las completaciones. La optimización por réplica y el bootstrap de una completación fija no deben confundirse. Cualquier afirmación universal sobre este criterio requiere un procedimiento especificado y validado por separado.

Se recomienda dejar la evaluación universal del criterio 5 como **NO EVALUADA POR ESTE MÉTODO**, sin sustituirla por la envolvente exploratoria. Nada de lo anterior levanta la compuerta técnica global de T2-A0.

## 5. Texto propuesto para incorporar a E2

> La sección 6 se admite exclusivamente como análisis exploratorio de sensibilidad por completaciones binarias. Se corrigen los extremos por métrica conforme a las fórmulas especificadas en el dictamen técnico. Cuando el desenlace sea estructuralmente indefinido, las completaciones se interpretarán como escenarios hipotéticos, no como recuperación de un desenlace latente demostrado.
>
> La envolvente bootstrap se reportará con cobertura nominal no validada y no se denominará intervalo de confianza del 95 %. Los casos de lift indefinido se conservarán y contabilizarán. Se publicarán las cotas independientemente de su amplitud.
>
> No se afirmará que el criterio inferencial 5 se cumple bajo todas las asignaciones a partir únicamente de las cotas puntuales o de la envolvente exploratoria. Cualquier evaluación de esa afirmación requiere especificación y validación separadas. Ningún resultado de la sección 6 modifica el veredicto confirmatorio de T2-A0.
>
> La revisión por ChatGPT es una revisión técnica por IA con participación previa en el proyecto. No se presenta como dictamen humano independiente ni como acreditación del requisito vigente de revisión externa independiente.

## 6. Condiciones de implementación y cierre

Antes de aplicar la sección 6:

1. Incorporar las correcciones matemáticas y el alcance interpretativo anteriores.
2. Resolver documentalmente el requisito vigente de revisión externa; este documento no lo satisface por sí solo.
3. Especificar y congelar el análisis exploratorio antes de aplicarlo a datos, conforme al orden de autorización de E2.
4. Verificar el script contra enumeración exhaustiva de completaciones binarias en ejemplos sintéticos pequeños, incluyendo denominadores cero, desconocidos dentro y fuera, empates y remuestreo de bloques completos con multiplicidades.
5. Registrar versión y SHA-256 del script validado antes de su aplicación. No ajustar reglas a los resultados reales.
6. Conservar las disposiciones de visitas y el análisis confirmatorio original.

**Conclusión:** valoración favorable condicionada a los cambios anteriores para un análisis exploratorio. No se valida cobertura nominal, no se certifica T5, no se congela E2 y no se declara cumplido el requisito de revisión externa independiente.

## 7. Referencias

1. Imbens, G. W. y Manski, C. F. (2004). *Confidence Intervals for Partially Identified Parameters*. Econometrica, 72(6), 1845–1857. DOI: https://doi.org/10.1111/j.1468-0262.2004.00555.x . Texto del autor: https://scholar.harvard.edu/files/imbens/files/confidence_intervals_for_partially_identified_parameters.pdf
2. Solicitud aportada por el responsable: `T2-A0 solicitud de dictamen estadístico (sección 6 de E1).md`, 21 de octubre de 2026. Fuente de las cinco preguntas y del método examinado. Los enlaces y hashes abreviados incluidos en esa solicitud son referencias de procedencia; no se presentan como integridad verificada en este dictamen.
