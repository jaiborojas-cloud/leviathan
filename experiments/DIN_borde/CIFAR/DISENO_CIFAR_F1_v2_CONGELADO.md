# DIN-CIFAR F1 — descubrimiento y análisis · BORRADOR v2

2026-10-29, hora de México. **No congelado; no autoriza entrenar ni analizar una cohorte real.** Se propone para auditoría y aprobación antes del productor F1. No modifica planes, instrumentos, compuerta, F0/F0b ni sus conclusiones. La [v1](DISENO_CIFAR_F1_BORRADOR_v1.md), su analista y sus 54 resultados se conservan íntegros.

Esta revisión responde a la auditoría del PR #127: asigna los estratos de c por la **mediana de c250 del split**, aclara la aceptación numérica de ρ y corrige el espaciado en todo el documento. El [registro de revisión y pruebas](F1/revision_v2/PROTOCOLO_REVISION_v2.md) se compromete antes del código v2 y de ejecutar pruebas sintéticas. El límite externo de 120 s sigue siendo un requisito del futuro productor.

## 1. Pregunta y antecedentes permitidos

¿X10 mejora fuera de muestra la predicción de log ρ_caras(250) sobre una base cúbica de log ρ_caras(10), dentro del split, en CIFAR-3? Esta es una pregunta predictiva exploratoria sobre una base concreta. No identifica información condicional frente a toda función de la base, causalidad ni utilidad para clasificar imágenes.

Se conservan el [plan v1](PLAN_CIFAR_v1.md), la [enmienda v2](PLAN_CIFAR_v2.md) y la configuración aprobada: gato (clase 3), ciervo (clase 4) y perro (clase 5), con etiquetas 0, 1 y 2; perro es la referencia reducida. CNN de 26.067 parámetros, float64, Adam con lr = .003, lote de 64 sin reemplazo, 250 updates, visitas 5/10/30/250 y sin aumentos. Train: 300 por clase; panel y test: 9 por clase cada uno, disjuntos entre sí en cada split. La normalización por canal se ajusta solo en train. f son las 2 componentes principales del panel, centradas, escaladas y con signos según el plan v1, calculadas una vez por split y compartidas entre inicializaciones y visitas; nunca proceden de rasgos aprendidos.

**Detalle de implementación:** `sistema_cifar3.py` conserva LR por defecto = .001 para reproducir F0. F1 debe llamar explícitamente `iniciar(..., lr=.003)` y archivar ese valor, sin modificar el archivo original. No se cambian clases, ancho, updates, f ni regularización después de medir F1.

F0 y F0b no archivaron X, valores de ρ ni D; F0 cronometró una llamada rho y conservó solo su estado. [F0](resultado_F0/RESULTADO_F0_2026-10-28.md) y [F0b, snapshot del PR #126](F1/fuentes/RESULTADO_F0b_PR126.md) son transcripciones publicadas: no se dispone aquí del SHA de sus archivos originales. El PR #126 estaba pendiente al leerlo para la v1. Se usan como contexto de factibilidad, no como datos de F1 ni evidencia de señal. El responsable aprobó pasar a F1 con lr = .003.

## 2. Muestra, universo y semillas

**100 splits × 5 inicializaciones = 500 trayectorias**, todas planificadas y reportadas. IDs `cifar_f1_s{split:04d}_k{k}`, split de 0 a 99 y k de 0 a 4; orden de tabla y hash: split → k → visita, con visitas 5, 10, 30 y 250. La tabla larga tiene 2.000 filas esperadas. No hay parada por señal ni ampliación al ver D o p.

| Uso | Split | Inicialización | Lote |
|---|---|---|---|
| F1 | 1.100.000 + s | 1.110.000 + 5s + k | 1.120.000 + 5s + k |
| F2, reserva sin ejecutar | 1.200.000 + s | 1.300.000 + 5s + k | 1.400.000 + 5s + k |

F2 reserva hasta 10.000 splits, sin fijar N ahora; si necesitara más, se documentaría otra reserva antes de entrenar. Los rangos son disjuntos de F0 (1.010/1.020/1.030 millones), F0b (1.040/1.050/1.060 millones) y F0c reservado (1.070/1.080/1.090 millones). No usar sus estados o pesos como F1. Las semillas del análisis se separan conceptualmente de las del entrenamiento.

El [plan borrador legible por máquina](F1/plan_F1_BORRADOR_v2.json) contiene parámetros, versiones, fuentes e `ids_sha256`. No es todavía un plan de cohorte autorizado. Al congelar se conserva la ciencia, se cambia el estado a CONGELADO, se publica el plan por SHA antes del productor y se vincula su SHA a cada registro. **Semillas nuevas no garantizan imágenes diferentes:** splits de una misma base finita pueden solaparse entre sí y con F0/F2. El estimando es sobre particiones e inicializaciones de CIFAR-3, no sobre datasets o imágenes nuevas independientes.

## 3. Datos y trazabilidad por trayectoria

Se conserva el archivo oficial CIFAR con MD5 `c58f30108f718f92721af3b95e74349a` y SHA-256 publicado por el productor antes de medir. No descargarlo ni leer imágenes para escribir o probar este analista. El futuro productor guarda índices train/panel/test, hashes de esos índices, f y cargas PCA, preprocesamiento, semillas, pesos o checkpoint por visita y versiones. Sin dataset externo adicional ni optimización del panel.

En **cada visita** registrar:

- X(t) = max_n [logsumexp de logits de clases ≠ y_n − logsumexp de los 3 logits], sin calcular `log(1−softmax)` por resta; X10 es la única primaria. **Sí conviene guardar X5 y X30:** salen de logits ya calculados y diagnostican saturación y tiempo sin más entrenamiento; no se elige la visita ganadora para rescatar la primaria. También se guarda X250.
- M, f y logits/etiquetas en arrays externos; tr M, c = max diag M / tr M y q = norma Frobenius fuera de diagonal / norma Frobenius M. M no se normaliza por su traza para medir ρ. Guardar espectro y diagnóstico del instrumento, sin alterar M para hacerlo pasar.
- k_star = primer argmax diag M, R(t) = log(1−p_y(k_star)) por la misma fórmula estable, indicador de mala clasificación de k_star y fracción mal clasificada del panel. Esto permite interpretar el ejemplo difícil; no cambia X10 ni define otra primaria.
- Precisión y CE media de train, panel y test. Son descriptivas, no filtros de inclusión ni desenlaces primarios de generalización. El test de 27 imágenes es pequeño; no prueba generalización poblacional.
- Estado y error por visita, tiempos de CPU y pared de entrenamiento, geometría y rho, pico de memoria o null si no se midió; hashes de checkpoint, f, índices y diagnósticos, warnings y entorno. Arrays y checkpoints fuera de Git.

En u10 y u250, **solo una llamada** a `rho_borde_v2` r3 por estado: conservar ρ_caras, ρ_vert, ganador, cara, dirección, errores de cuadratura, cotas de prefijo y cola, evaluaciones, tiempo y resultado completo con SHA. No medir rho5 ni rho30 en este protocolo; el ahorro no afecta a X5/X30 ni c/q.

La tabla, sus columnas y el resumen de enlace se definen en [ESQUEMA_TABLA_v2.md](F1/ESQUEMA_TABLA_v2.md). Los campos de coste y arrays adicionales permanecen en los registros externos enlazados; no es necesario inflar el CSV para cada diagnóstico.

## 4. Instrumento, presupuesto y estados

`make_geom_state_general` con cabeza reducida se usa sin cambiar su SHA; `subset_M` y rho r3 siguen congelados por sus SHA. La compuerta oficial reportó PASA con error 0, pero el productor debe recibir su JSON oficial, registrar su SHA y verificar las 9 comprobaciones, fuentes y versiones, junto al SHA del código de compuerta e instrumento. No se vuelve a entrenar Wine para este diseño o sus pruebas.

Rho usa **sus opciones actuales explícitas**: grid = 9, starts = 3, margin = 1e−8, order = 12, log_step = 4, maxiter = 40, xatol = 1e−9, max_evaluations = 4096 y seconds = 60 de **pared**, no CPU. El watchdog externo de **120 s de pared** para esa llamada es un **requisito del productor**: permite conservar un cuelgue como fallo; no es una llamada con un presupuesto mayor. El productor deberá implementar esa interrupción aislada, conservar lo disponible y seguir el entrenamiento si este sigue sano. El analista de CSV comprueba el tiempo registrado, pero no implementa ni demuestra el watchdog. No reintentar ni cambiar presupuesto, precisión o búsqueda según c o éxito. Un timeout es falta de medida, no censura que se pueda sustituir por una cota en el log.

Para aceptar rho: status = `VALID_NUMERICAL_ESTIMATE`, versión r3, ambos valores finitos y positivos, ρ_caras ≤ ρ_vert y, **para cada ganador por separado**, quad_error ≤ 1e−6 · longitud y prefix_bound + tail_bound ≤ 1e−6 · longitud. **«Longitud» significa el valor de ρ de ese ganador:** ρ_caras para el ganador de caras y ρ_vert para el ganador de vértices; no significa el módulo de su dirección ni otra longitud auxiliar. Los tres términos de auditoría deben ser finitos y no negativos. **`quad_error = None` es inválido**, al igual que un término ausente, vacío, NaN o infinito; nunca se interpreta como cero. Guardar los términos separados y el rho_status original; no aceptar un candidato parcial cuando se agotó el presupuesto. No añadir jitter, normalización, clipping de c o rho ni un nuevo piso. Las tolerancias internas del instrumento siguen intactas.

| Estado por visita | Significado |
|---|---|
| MEDIDA | Logits, métricas y dominios válidos; en 10/250, además rho aceptado. En 5/30, rho_status = NO_SOLICITADA y campos rho vacíos. |
| INVALID_RHO | En 10/250, métricas del modelo disponibles pero rho con presupuesto agotado, watchdog, excepción o auditoría fallida. Se guardan todos los diagnósticos; no aporta un log rho válido. |
| FALLIDA | Fallo de entrenamiento, geometría, PCA, logits o métrica, o visita no alcanzada. Conservar todos los campos obtenidos y el error; las visitas posteriores no alcanzadas llevan FALLIDA y causa. |

No hay sustituciones. Un error de medición en 5/30 no invalida por sí solo 10/250 si estas visitas se obtienen válidas; un fallo de entrenamiento sí deja sin medir las visitas no alcanzadas. El analista conserva el estado declarado y los motivos de invalidez, sin reescribir los registros originales.

## 5. Riesgos y reglas de inclusión

**Panel con muchos errores:** no exigir que el difícil esté bien clasificado ni filtrar por precisión. Guardar argmax, logits y etiquetas, y usar logsumexp. X ≈ 0 y empates son posibles y se reportan; no se añaden pseudocuentas ni se cambia a margen después de observarlos. Valores de X/R positivos hasta 1e−12 se toleran solo como error de redondeo declarado, sin truncarlos; mayores son dominio inválido. R ≤ X + 1e−12. La constancia intra-split de X usa el mismo atol = 1e−8 que C1; si impide identificar el ajuste, INCONCLUSIVE.

**c cercano a 1:** no excluirlo ni usar c ≥ .8 como compuerta primaria. Los dominios físicos de c ∈ (0, 1], q y precisiones ∈ [0, 1] son exactos; tr M es positiva y finita. Se informan las colas c ≥ .8 y c ≥ .95, espectro, relación ρ_caras/ρ_vert y fallos rho por esos grupos; ninguna comparación selecciona parámetros del instrumento. Estos perfiles operacionales conservan la c de cada estado; no son los estratos por split del §7. Se admiten c = 1 y X = 0; rho = 0, infinito o NaN nunca se logaritma ni se eleva a un piso.

**Pérdidas de medida:** una trayectoria es elegible para la primaria si 10 y 250 son MEDIDA y satisfacen los dominios definidos. Numerador de faltantes: IDs sin ambos extremos válidos, una vez por trayectoria, contra 500 planificadas, incluyendo ausentes, estados fallidos e INVALID_RHO. Duplicados de (trajectory, update), IDs ajenos, visitas no planificadas o split/k incompatibles: ABORTA, sin resultado científico. Se conserva un libro de motivos completo por ID y visita, no solo el primero.

Como C1: faltantes > 25/500 (5 %) o menos de 80/100 splits con ≥ 3 trayectorias elegibles ⇒ INCONCLUSIVE. En los splits con < 3, las filas no se usan en el ajuste; se cuentan y reportan separadas de los faltantes de medida. Si se superan las compuertas se calcula el estimando sobre ese subconjunto explícito, sin declarar que las 500 están medidas. La falta de integridad o de compuerta también impide el ajuste. No se amplía la muestra, reemplazan IDs, descartan outliers ni relajan reglas al ver D.

Reportar siempre: flujo de 500 IDs y 2.000 visitas, estados por visita, motivos completos, elegibles y no usados, fallos por c y precisión disponible, tiempos, saturación de X y variación intra-split. La dependencia de faltantes respecto de geometría puede sesgar los casos completos: estas compuertas son de calidad, no una corrección estadística de esa selección ni garantía de ausencia de sesgo. Sin imputación ni ponderación aprendida tras observar Y.

## 6. Primaria descriptiva C1 exacta

X = X10, L = log ρ_caras10, Y = log ρ_caras250. Se reutiliza **solo** la función primaria del C1 SHA `8711f468…`; no su wrapper de IDs o datos Wine. Se registran los splits y bloques efectivamente analizados.

1. Centrar Y, X y cada término de la base dentro de cada split, con pendientes comunes. Base: [z, z², z³] centrados, z = (L − media L) / DE L, ddof = 0. Como el código original, esa estandarización usa los L elegibles; no se estima con Y ni selecciona hiperparámetros. El espacio cúbico centrado es invariante a cambios afines no degenerados de L.
2. **Se reutilizan exactamente las semillas de C1:** `default_rng(260010).permutation` de splits analizados; bloque = posición mod 10. Todas las filas del split caen en su bloque. Ajustes OLS en entrenamiento de cada bloque; SSE se calcula solo fuera de muestra.
3. D = 1 − SSE_completo / SSE_base; completo = base + X centrada. No truncar D negativo. Informar también la pendiente de X del ajuste completo global, como C1.
4. **5.000 permutaciones dentro del split, semilla 260001**, reasignando X y recalculando D con los mismos bloques. p_descriptiva = (1 + #{D_perm ≥ D − 1e−15}) / 5001. La holgura es solo de empates numéricos. Reusar semillas algorítmicas no reutiliza datos de Wine ni genera cohortes compartidas.

Con calidad suficiente: **PASS_DESCRIPTIVO** si p < .05, D > 0 y pendiente > 0; en otro caso **NOT_MET_DESCRIPTIVO**. Si X no tiene variación, L es constante, Y o SSE_base son degeneradas, el ajuste no es finito o hay un fallo técnico: **INCONCLUSIVE**, con todos los motivos. No dar PASS a NaN ni convertir falta de medida en NOT_MET.

No es confirmatorio: no se interpreta p como validación externa ni se rescata el resultado escogiendo otro rho, visita, base o estrato. La salida dice siempre DESCUBRIMIENTO y conserva el estado del plan (BORRADOR/CONGELADO). La CLI borrador solo admite entradas etiquetadas como pruebas sintéticas; los datos reales requerirán un plan CONGELADO y vínculo al productor y dataset publicados.

## 7. Secundarios predeclarados, sin decisiones ni p adicionales

Todos se reportan, incluidos los no definidos; no rescatan la primaria ni producen MODULA/NO_MODULA.

- D y pendiente con rho_vert, sobre la misma población primaria, sin nuevas permutaciones. Sensibilidad a base de grado 5, misma población. Solo compara el ajuste a esas bases, no toda función de L.
- D y pendiente de X5 y X30 usando siempre L10/Y250; requieren su visita válida, ≥ 3 trayectorias por split y ≥ 20 splits. No sustituir X10 por el mejor. La lectura de X30 es posterior a u10 y no la misma predicción temprana.
- **Relación con c, por split:** para cada split usado por la primaria (≥ 3 trayectorias elegibles), calcular la mediana de c250 **entre sus trayectorias elegibles para la primaria**. Asignar todo el split a un único estrato según esa mediana: bajo si < .4; intermedio si ≥ .4 y < .8; alto si ≥ .8 (incluido 1). Las medianas exactamente .4 o .8 entran en el estrato superior. **Conservar todas las trayectorias elegibles de cada split asignado**, aunque su c250 individual cruce uno o ambos cortes. No usar las trayectorias inválidas para calcular la mediana, no imputar las inicializaciones ausentes ni dividir un split entre estratos. La mediana de un número par de valores es el promedio de los dos centrales, como `numpy.median`.
- Para cada estrato de c se reportan explícitamente **número e IDs de splits**, N de trayectorias, sus IDs, mediana de c250 por split y número de trayectorias que la determina, medianas de c/q individuales, mediana de las medianas de split y D/pendiente de la misma primaria. El mínimo sigue siendo **20 splits con ≥ 3 elegibles**; si no se alcanza, NO_DEFINIDO, conservando todos los conteos y asignaciones. Se reportan también los splits fuera del conjunto usado por la primaria. Sin p ni prueba de tendencia, sin juntar estratos después de mirar. La selección por c250 es posterior y potencialmente endógena: no equivale a β de los niveles manipulados de Q13-DR/M2 ni identifica que el colapso module causalmente la señal.
- D y pendiente en mitades de splits pares e impares (mismo protocolo de bloques sobre cada subconjunto), descriptivos sin exigir significación en mitades. No se cambia muestra por su signo.
- Distribuciones de c/q, precisiones, CE y R, saturación de X y fracción de k_star mal clasificada; perfiles de fallo rho por c de los estados donde esa métrica existe. Se archivan R y logits para una futura exploración explícita, sin convertirla en primaria aquí.

Un secundario puede quedar no definido sin contaminar una primaria válida. Su fallo conserva error y denominador propio. No se calculan «pendientes de D sobre c» con unos pocos estratos como si fueran intervenciones pareadas.

## 8. Qué decide F1 y qué queda para F2

F1 decide si hay **señal descriptiva prometedora** en esta configuración y si el instrumento y la muestra permiten estimarla. PASS_DESCRIPTIVO justifica proponer F2 global al responsable; no lo activa automáticamente. NOT_MET no demuestra ausencia con potencia suficiente. INCONCLUSIVE pide resolver la limitación instrumental o de muestra, conservando todo y con una nueva versión aprobada antes de cualquier repetición; no reclasificar esta F1.

Si solo un estrato, visita o rho muestra señal, eso es una **hipótesis descubierta diferente**, que exige declararla como tal y definir F2 para ella con corrección de multiplicidad si corresponde. No se presenta como reproducción de la primaria global. F1 no afina de nuevo arquitectura, lr, clases o f ni cambia el significado de X10.

F2: splits, inicializaciones y lotes de la reserva nueva; tamaño elegido **antes de entrenar** mediante potencia con F1 como piloto, con efecto objetivo conservador, varianza residual y dependencia intra-split, fallos y precisión Monte Carlo documentados. No usar el máximo entre secundarios como efecto objetivo sin descuento. Deben congelarse hipótesis, base y desenlace, multiplicidad, compuertas, N, semillas, analista y productor; auditoría independiente y autorización del responsable. No fijamos ahora N ni prometemos potencia. La reproducción en CIFAR-3 no prueba transferencia a todas las imágenes, arquitecturas o datasets.

## 9. Entrega de este borrador

[Analista v2](F1/analisis_F1_v2.py), [pruebas sintéticas v2](F1/pruebas_F1_v2.py), esquema y plan borradores, y [referencias por SHA heredadas](F1/fuentes/provenance.json). La [revisión v2](F1/revision_v2/README.md) enlaza la trazabilidad y las pruebas de los cambios. Ningún dato real F1, descarga CIFAR, entrenamiento, geometría o nueva ejecución de Wine forma parte de esta tarea. Los resultados de pruebas no son resultados científicos F1. Tras auditoría y aprobación, el productor se encarga por separado y publica sus SHA antes de medir.

## 10. Congelación aprobada · 2026-10-29, 16:04

**Estado oficial: CONGELADO v2.** El responsable aprobó la congelación el **2026-10-29 a las 16:04, hora de México (`America/Mexico_City`, UTC−06:00)**, según su instrucción explícita en esta conversación. Esta sección formaliza esa aprobación; el texto anterior reproduce íntegramente el borrador auditado y conserva sus referencias históricas a BORRADOR. La ciencia, el universo, las semillas, el estimando, los estados, los criterios rho, los estratos y el requisito de watchdog de 120 s no cambian.

- Borrador aprobado: [DISENO_CIFAR_F1_BORRADOR_v2.md](DISENO_CIFAR_F1_BORRADOR_v2.md).
- SHA-256 del borrador: `b608a6b325401404a4947d57d907c337a62d98b5f55927309ce2d2dcd0dfd5a0`.
- Commit de la versión aprobada en el PR #127: `183e2fa2e0c61ad8407c0dc81f76c5e877f67a4e`.
- Plan oficial: [F1/plan_F1_v2_CONGELADO.json](F1/plan_F1_v2_CONGELADO.json), idéntico al [plan borrador v2](F1/plan_F1_BORRADOR_v2.json) salvo `estado = CONGELADO`.
- SHA-256 del plan congelado: `4347857e83fba828fda5910ffc9fd10feff8f4c14d37c27ac40e935b28ef34ae`.
- Analista v2, conservado sin cambios: `0c4d03b539fce2c115580c2928c6f5b9470e8b4b121c45c13b054a3934b9eb27`.
- Pruebas v2, conservadas sin cambios: `6b8a7f127b5f04da7f59ed29fc1c39c3f048e943c5708276ffad3097bf0e868b`.
- [Manifiesto congelado](F1/MANIFIESTO_CIFAR_F1_v2_CONGELADO.sha256) y [verificación documental](F1/VERIFICACION_CONGELACION_v2.json). Las 71 pruebas sintéticas archivadas permanecen como tales; no se repiten ni se presentan como medidas F1.

### Verificación del plan por el analista existente

Para datos reales se usará exclusivamente el plan congelado y su SHA publicado. El analista mantiene su SHA: `main` recalcula el SHA-256 de `--plan` y exige igualdad exacta con `--plan-sha` antes de leer la tabla; después valida el contenido científico contra la plantilla v2 conservada por SHA. `integrity` rechaza datos reales con estado BORRADOR. El resumen del productor también debe vincular `plan_sha256` a este mismo valor. No se añade ni se cambia ninguna ruta de análisis.

Al invocar el analista con los demás argumentos ya exigidos por su CLI, fijar literalmente:

```text
--plan experiments/DIN_borde/CIFAR/F1/plan_F1_v2_CONGELADO.json
--plan-sha 4347857e83fba828fda5910ffc9fd10feff8f4c14d37c27ac40e935b28ef34ae
```

El SHA esperado se toma de esta publicación, no se recalcula a partir de un archivo recibido para convertirlo en su propia referencia. Se conserva `plan_F1_BORRADOR_v2.json` porque el analista lo usa como plantilla de contenido inmutable. El manifiesto se verifica desde `experiments/DIN_borde/CIFAR/F1/` mediante `sha256sum -c MANIFIESTO_CIFAR_F1_v2_CONGELADO.sha256` o una comprobación SHA-256 equivalente.

### Entrega al productor

**Claude implementará el productor F1 a partir de este diseño congelado.** Debe publicar sus propios SHA antes de medir y cumplir el watchdog externo de 120 s. Esta entrega formaliza el diseño; no crea ni ejecuta el productor, no entrena y no analiza ninguna cohorte. F1 sigue siendo descubrimiento exploratorio; esta congelación no lo convierte en F2 ni fija el tamaño de F2. El PR #127 se marca listo para revisión, sin fusionarlo automáticamente.
