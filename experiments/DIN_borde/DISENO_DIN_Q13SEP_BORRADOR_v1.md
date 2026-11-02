# DIN-Q13-SEP · piloto de separabilidad entre concentración y escala

**BORRADOR v1 · 2026-11-02, hora de México. Para auditoría de Claude antes de congelar.** No autoriza ejecutar el piloto. Decisión del responsable: opción 1 de A2, registrada a las 11:22 en el [PR #133](https://github.com/jaiborojas-cloud/leviathan/pull/133), commit `168352e84bfb9b45610ba3e66836ad455751fe44`; [snapshot](Q13SEP/fuentes/decision_PR133.md). Base main `259fac77c21190c0753fd7087062d1578e58ef0d`. A1 está auditado, pero su implementación continúa en BORRADOR en el PR #132. No se reabre CIFAR-3, no se cambian etapas cerradas y no se calcula señal aquí.

## 1. Pregunta y alcance de «identificable»

¿El factorial de dos brazos entrenados (A0/LP) y tres temperaturas permite **(E)** comparar concentraciones distintas con escala aproximadamente igual y **(C)** comparar escalas distintas con concentración aproximadamente igual, de forma reproducible en u10 y u250?

Un éxito significa **separabilidad operacional entre las celdas de este factorial**, no identificación causal del colapso, independencia de todas las demás variables ni una señal temprana demostrada. Se exige que ambos contrastes principales crucen los brazos entrenados; se distingue si necesitan temperaturas distintas. Las comparaciones solo por temperatura se informan aparte y nunca bastan para pasar. Con dos brazos, el mismo par a temperatura igual no puede tener simultáneamente escala casi igual y muy distinta: no se promete esa separación puramente atribuible al entrenamiento.

## 2. Familia, receta e instrumento intactos

Receta de [G3](G3/scripts/run_v1.py) y [Q13/Q13-M2](Q13/cohorte/scripts/recipe_v1.py), sin Wine ni otros datos reales:

- Tres gaussianas en d = 13. Medias: primeras dos coordenadas (2, 0), (−1, √3), (−1, −√3); restantes cero. Por split: 117 ruidos normales estándar, 39 ejemplos por clase; x = media_y + .8 · ruido. Train: primeros 30 por clase, **90** en total; panel: últimos 9, **27**. StandardScaler ajustado solo en train. Sin test ni datos externos.
- Red float64 **13→64→32→3**, ReLU y capas `l1/l2/l3`, inicialización original de la receta. Adam lr = .006, sin decay; lote 64 sin reemplazo, 250 updates, sin parada por precisión, sin aumentos. Visitas de medida **u10 y u250**. Datos, pesos iniciales y secuencia de lotes iguales entre brazos de cada (split, k); cada temperatura reutiliza el mismo checkpoint, no otro entrenamiento.
- **A0:** CE normal. **LP:** CE(z, y) + λ · mean_n sum_c z_nc², con z = model(x_train[lote]); no centrar los logits en esta penalización, como Q13-M2. La escala que se mide más abajo sí elimina la media entre clases. No cambiar optimizador, dosis durante la trayectoria, receta de lotes ni regularización geométrica.
- `core.make_geom_state(model_T, Xpanel, ypanel)` y `core.subset_M(Rb, Ub, [0,1,2])` **sin cambios**, core SHA `b5251d2f1f082ae014596574e9ab827dde04aec785bf76091005f8149ba31ffd`. El core opera sobre el **panel de 27**, no sobre train: N = 27 en U. Cabeza reducida con clase 2 de referencia, RHO = 1e−4, máximo autovalor del Gram con piso 1e−14 y fórmula Woodbury originales. No se sustituye por una aproximación diagonal o por logits calibrados con gradientes antiguos.
- f = primeras dos variables estandarizadas del panel, exactamente las devueltas por el core, fija por split y común a brazos/temperaturas. No PCA ni perspectivas aprendidas.
- Geometry SHA `b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3` y rho r3 SHA `2ac015a263afb44616de0fceebd3b1d2a36ad0a76cd466adcdcc7e3adb8b8df0` permanecen congelados. **El piloto verifica sus SHA pero no llama a rho, exp-map ni curvatura.**

Fuentes y SHA completos en [provenance](Q13SEP/fuentes/provenance.json). No usar `scores`/`measure` de G3 ni el productor antiguo completo: calculan X o rho. Se reutiliza la receta de entrenamiento y se implementa después un recolector mínimo de estas variables, auditado por Claude.

### Temperatura: punto del espacio de parámetros

Temperaturas fijas y positivas: **T ∈ {0.5, 1, 2}**, en ese orden de registro; misma rejilla para todas las dosis, fases, visitas y trayectorias. Para cada celda, cargar una **copia fresca** del checkpoint original y, sin gradiente, dividir `l3.weight` y `l3.bias` completos entre T. No acumular divisiones entre temperaturas, no tocar `l1/l2`, no entrenar la copia ni modificar el optimizador/checkpoint original.

Salir del bloque `no_grad` tras escalar la cabeza: el core necesita autograd para Rb/Ub. Recalcular Rb, Ub, su Gram/Fisher, ridge, M y todas las métricas **desde esa copia** con las funciones congeladas. Es una medida en el punto con cabeza escalada, en la carta de parámetros original del core. No equivale a dividir los logits en un wrapper conservando otra parametrización, ni a un pullback por T, ni a M/T²: las probabilidades, gradientes y regularización cambian. No se cambian solo las probabilidades manteniendo M.

## 3. Dos fases independientes, sin señal

| Fase | Splits × k | Brazos entrenados | Entrenamientos máximos | Celdas brazo–T–trayectoria | Medidas M (dos visitas) |
|---|---|---|---:|---:|---:|
| Calibración | 10 × 5 | A0 + LP con λ = .0001, .0003, .001, .003 | 250 | 750 | 1.500 |
| Validación de separabilidad | 20 × 5 | A0 + una LP elegida | 200 | 600 | 1.200 |
| Total máximo | fases con semillas distintas | | **450** | **1.350** | **2.700** |

Las cifras M de la tabla cuentan medidas principales; se añaden **tres reconstrucciones de control** prefijadas (§6), para un máximo de **2.703 llamadas al core/M**. La rejilla LP toma las cuatro primeras dosis de la [calibración M2](Q13M2/calibracion/RESULTADO_v1.md), que publicó solo c/q/precisión; no se eligió mirando D. La escala conjunta aún debe medirse en este piloto. Todos los IDs planificados se conservan, incluidos fallidos. No se aumenta la rejilla o N tras mirar resultados. Si no hay dosis apta en calibración, no se entrena validación. La selección de λ usa **solo c y escala S** mediante el §5, sin q, tr M, confianza, precisión o ningún desenlace de señal para ordenar las dosis. La calidad del §6 es previa y común a toda la fase: no se descarta una dosis por calidad para escoger otra. La precisión < .5 es un motivo de invalidez operacional predeclarado, no un criterio para favorecer una dosis.

Después de calibrar se publica por SHA `DOSIS_Y_CONTRASTES_Q13SEP.json`: λ, los dos pares principales, sus orientaciones, resultados de los criterios y vinculación a tabla/plan/productor. Ese archivo se compromete **antes** de entrenar validación. No hay reelegir dosis, temperaturas, orientaciones o pares con la validación. Las fases tienen la misma receta y reglas.

## 4. Variables y prohibiciones por celda

Una fila por fase, condición entrenada, split, k, T y visita. c significa concentración **diagonal** maxdiag/tr; no se sustituye por λ_max/tr ni por rango efectivo. q se informa sin convertirlo en otro selector de dosis. **S se calcula sobre el panel**:

S = sqrt((1/(27·3)) · sum_{n,c} (z_nc − mean_d z_nd)²).

Es invariante a añadir una constante por ejemplo. Reportar también S_train con la misma definición sobre los 90 de train, solo descriptiva; **no entra** en selección o separabilidad. No confundir S con la norma de la cabeza o sqrt(tr M).

Medir: **c = max diag M/tr M; q = ||M − diag(diag M)||_F/||M||_F; tr M; S; S_train; confianza media verdadera del panel = mean p_y; confianza media máxima del panel = mean max_c p_c; precisión train y panel** (argmax, primer índice en empates), estado, error, tiempos y memoria. Conservar M/f, pesos sin escalar y copia escalada o receta/hash verificable, RNG/Adam, datos/índices/escalador, warnings y entorno en archivos externos con SHA. Escala, confianza y precisión se miden desde los logits completos del modelo_T; el core conserva internamente su gauge reducido.

**No calcular X, R del ejemplo difícil, mínimo de p_y, rho_caras, rho_vert, L/Y del desenlace rho, D, p-valores, W ni asociaciones de señal**, tampoco «para verificar». No ejecutar el analista robusto. Las tablas no tienen esas columnas. Se verifican los SHA de instrumentos futuros como archivos, sin llamar a rho. Puede reconstruirse después una medida en otro diseño, pero el piloto no será su cohorte de señal.

El [esquema](Q13SEP/ESQUEMA_Y_DECISION_v1.md) fija columnas, denominadores y decisiones; [configuración](Q13SEP/config_BORRADOR_v1.json) fija valores. No se generan aquí un productor o datos.

## 5. Criterio de separabilidad predeclarado

Sea r = (split, k), v ∈ {10,250}, a = (A0, T_a), b = (LP_λ, T_b). Comparaciones pareadas: nunca se emparejan redes de otro r para encontrar coincidencias. Las constantes **no se calibran**:

- «Misma escala»: |log(S_a/S_b)| ≤ log(1.10), es decir, razón dentro de [1/1.10, 1.10].
- «Concentración distinta»: diferencia **orientada** de c ≥ **.15**.
- «Misma concentración»: |c_a − c_b| ≤ **.05**.
- «Escala distinta»: razón orientada de escala ≥ **1.5** (diferencia orientada de log S ≥ log 1.5).

**Pregunta E:** un r cumple si, **en ambas visitas**, tiene misma S y σ_E(c_a − c_b) ≥ .15. **Pregunta C:** cumple si, en ambas visitas, tiene misma c y σ_C log(S_a/S_b) ≥ log 1.5. Cada σ es +1 o −1 y se elige una sola vez en calibración. De ese modo no se mezclan diferencias de signo contrario entre visitas o unidades para aparentar una separación.

Las tolerancias son operacionales: 10 % permite un emparejamiento de escala aproximado; .15 es tres veces el margen de c considerada igual (.05); 1.5 es mayor que el margen de escala igual (1.10). No son umbrales de efecto de D ni constantes universales. Implementar log(S_a/S_b) como log(S_a) − log(S_b) para evitar desbordar el cociente. Todas las comparaciones usan valores sin redondear, límites inclusivos y log natural; no se añaden tolerancias a posteriori.

### Resumen por split y decisión de calibración

Un split cumple una pregunta si al menos **3 de sus 5 r planificados** la cumplen en ambas visitas. Un r inválido o sin medida es un fracaso operativo del criterio, no se elimina de ese denominador. Cada split pesa una vez; no se tratan 50/100 inicializaciones como splits independientes.

Para cada λ, enumerar los nueve pares (T_a,T_b) en este orden fijo:

**(1,1), (.5,.5), (2,2), (1,.5), (.5,1), (1,2), (2,1), (.5,2), (2,.5)**;

y, dentro de cada par, σ = **+1 antes que −1**. Para cada pregunta, es apto el primer par/orientación que cumpla en **≥ 8 de los 10 splits** de calibración. Una dosis es apta si tiene un par apto para **cada pregunta**; pueden ser pares diferentes, siempre A0 frente a LP de esa misma dosis. Elegir la **λ más pequeña apta**, no la de mayor separación. Congelar en el archivo de decisión los dos primeros pares aptos de esa dosis. Si ninguna dosis es apta: **NO_IDENTIFICABLE**, motivo CALIBRACION_SIN_DOSIS; no entrenar validación ni ampliar la búsqueda.

### Validación y distinción de mecanismos

Usar solo los dos pares/orientaciones publicados. Cada pregunta debe cumplir en **≥ 16 de los 20 splits** de validación. **SEPARABILIDAD_LOGRADA** exige calidad y controles válidos, y que **E y C** cumplan; cualquier otro patrón da **NO_IDENTIFICABLE** con sus motivos y se detiene esta vía bajo este diseño.

Para cada contraste principal se reporta su procedencia:

- **ENTRE_BRAZOS_T_FIJA** si T_a = T_b: diferencia entre modelos entrenados a temperatura común.
- **ENTRE_BRAZOS_T_DISTINTA** si T_a ≠ T_b: requiere entrenamiento y temperatura; no atribuir la separación solo al entrenamiento.

Adicionalmente se tabulan los pares de temperaturas **(.5,1), (.5,2), (1,2) dentro de un mismo brazo**, con las mismas reglas E/C y ambas orientaciones, como **SOLO_TEMPERATURA**. No se seleccionan contrastes con esa tabla ni rescatan las principales. Si solo C funciona por temperatura y no existen ambos contrastes principales entre brazos, el global es NO_IDENTIFICABLE. Como S(T) = S(1)/T, dos temperaturas distintas de esta rejilla no pueden satisfacer la tolerancia de «misma S» dentro del mismo modelo: se espera E = 0 en esa sensibilidad, como consecuencia algebraica, no como fallo del instrumento.

No se declara «dos intervenciones independientes sobre c y escala» ni que ambos ejes se separaron solo por entrenamiento cuando algún par requiere T distinta. El resultado permite o impide diseñar contrastes de señal con esos soportes; no identifica causalidad ni mantiene fija toda la confianza/distribución de logits.

## 6. Calidad, controles y fallos

Una medida válida tiene valores finitos, tr M > 0, ||M||_F > 0, c ∈ (0,1], q y precisiones/confianzas ∈ [0,1], S > 0 y S_train > 0. Sin clipping, jitter, diagonalización forzada o normalización por traza. Se conservan valores inválidos y sus motivos como FALLIDA, sin incorporarlos a ratios/logs. No se logaritma S ≤ 0.

**NO_APRENDIO:** precisión train en u250 < .5, medida en T = 1, invalida operacionalmente ese entrenamiento en todas sus temperaturas/visitas; .5 exacto pasa. No se sustituyen fallidas. Se conservan los estados MEDIDA y valores originales: NO_APRENDIO es una etiqueta de elegibilidad de la unidad, no una reescritura retrospectiva de visitas. En calibración se exigen **≥ 48/50 r completos conjuntamente en todos los cinco brazos y seis medidas por brazo**, y ≥ 8/10 splits con al menos tres r completos. En validación, ≥ 95/100 r completos conjuntamente en A0/LP y ≥ 16/20 splits con al menos tres completos. Calidad insuficiente impide elegir dosis o seguir: NO_IDENTIFICABLE con motivo CALIDAD_INSUFICIENTE; **no se interpreta como ausencia física de separabilidad**. Se informan también todos los parciales y faltantes por brazo/T/visita, siempre contra lo planificado.

Controles obligatorios para el productor posterior:

1. SHA de core, geometry, rho r3 y receta; versiones exactas torch 2.9.1+cpu, numpy 2.3.5, scipy 1.17.0, sklearn 1.8.0; un hilo BLAS/torch por proceso. No llamar a `core.load_split`, funciones de Wine ni a antiguos medidores de X/rho.
2. Pareado: mismos datos, f, pesos iniciales y hashes de lotes entre brazos; checkpoint original idéntico antes/después de medir temperaturas. En los tres estados de reconstrucción prefijados del punto 4, T = 1 reproduce M/c/q/f de la ruta original mínima de receta, con error relativo ≤ 1e−12 y f idéntica; esa misma reconstrucción comprueba ambos controles, sin duplicarla.
3. `z_T = z_1/T` y `S_T = S_1/T`, error máximo normalizado por max(1, norma del esperado) ≤ 1e−12; precisión de train/panel idéntica entre T de un mismo checkpoint. No exigir invariancia de M, c, q, confianza o tr M.
4. Tres reconstrucciones de M desde pesos, sin entrenar de nuevo, fijadas: calibración s0/k0/A0/u10/T1; s0/k0/A0/u250/T1; s0/k0/LP mínima/u250/T1. Error relativo Frobenius 0 y f idéntica con versiones/hilos fijados. Cualquier discrepancia se conserva y se reporta antes de continuar.

Un control fallido produce estado de corrida **INVALIDA**, sin interpretación de separabilidad, y NO_IDENTIFICABLE como decisión operativa de detener la vía. Se preservan todos los fallos, warnings, versiones y salidas; una corrección requiere enmienda comprometida antes del código nuevo y carpeta nueva. No reintentos, reemplazos ni ampliación de presupuesto para recuperar un resultado.

## 7. Semillas propuestas y universos

[Inventario y rangos](Q13SEP/SEMILLAS_PROPUESTAS_v1.md): calibración **71.000.000+s / 71.100.000+5s+k / 71.200.000+5s+k**, s = 0..9; validación **72.000.000+s / 72.100.000+5s+k / 72.200.000+5s+k**, s = 0..19. Reutilización intencional dentro de cada fase solo para el pareado entre brazos/T; **ningún entrenamiento se repite**. Fases disjuntas y semillas nuevas frente a G2/G3, C2, Q13, Q13-DR, Q13-M2, F0/F0b/F0c, F1, reserva CIFAR-F2 y otros registros visibles. Se evita conservadoramente toda la banda 0..30.000.000 de los registros históricos revisados, incluidos E16 y las pruebas A1.

Se propone reservar para la futura señal, sin N elegido ni ejecución, **73.000.000+s / 73.100.000+5s+k / 73.200.000+5s+k**, capacidad hasta 10.000 splits. Si hicieran falta más, revisar la reserva antes de usarla; nunca reutilizar las fases piloto o CIFAR-F2. La comprobación estática y sus límites se documentan; no afirma independencia matemática de flujos PRNG. El productor debe repetir el cotejo con registros actualizados antes de publicar el plan congelado.

IDs de entrenamiento: `q13sep_cal_{condicion}_s{split:04d}_k{k}` y `q13sep_val_{A0|LP}_s{split:04d}_k{k}`. Condiciones de calibración: A0, LP01, LP02, LP03, LP04 en orden de dosis. Celda = ID + T05/T10/T20; medida = celda + u010/u250. Ejecución: split → k → condición → visita, midiendo T desde copias; tabla ordenada fase → split → k → condición → T → visita. La tarea del pool es un entrenamiento (split,k,condición), no el grupo completo de cinco inicios; así las 15 tareas de la prueba corta pueden ocupar 12 procesos. Orden de encolado prefijado, finalización asíncrona sin cambiar IDs o reglas. El universo definitivo y sus SHA los publicará el productor después de congelar, antes de medir; esta configuración es un borrador, no ese plan autorizado.

## 8. Coste del PC y prueba corta

Referencia publicada de CIFAR F1: **unos 33 s de pared por trayectoria individual**, con **12 procesos** y rendimiento global de unas 500 trayectorias en 1.394 s (≈ una terminada cada 2,8 s). No confundir latencia individual con throughput ni con CPU. Aquí no se mide rho y el MLP es menor, pero se recalcula M seis veces por entrenamiento: no se promete la misma latencia.

Proxy conservador: 450 × 33 / 12 = **1.237,5 s ≈ 20,6 min ideales**. Presupuestar inicialmente **30–60 min**, más preparación/IO y separación entre fases; no es un benchmark ni una garantía. Se informan por separado tiempo de entrenamiento y coste de cada `make_geom_state/subset_M`; T_total ≈ (450·t_train + 2.703·t_M + t_IO)/(12·eficiencia). La calibración puede detener el trabajo sin gastar validación. Memoria de referencia CIFAR ≈ 741 MB/proceso, unos 8,9 GB para doce; medir la del MLP y no asumirla.

**Prueba corta prefijada:** primeras tres unidades (calibración s0, k = 0,1,2), todos sus cinco brazos: **15 entrenamientos, 45 celdas y 90 medidas M principales**, más las tres reconstrucciones de control (93 llamadas M), sin añadir semillas. Forman parte del universo y nunca se repiten. Usar 12 procesos spawn, un hilo cada uno, salida exclusiva/reanudable; conservar también fallidas. Publicar medianas y máximos de latencia/CPU/M/memoria, total transcurrido y rendimiento global, sin extrapolar solo desde el primer proceso.

Antes de continuar, actualizar el presupuesto operacional con esos tiempos. Si la proyección de ambas fases supera **90 min** o no caben 12 procesos en memoria, detener y pedir al responsable una decisión operacional; no ampliar N ni reducir silenciosamente la receta o las medidas. Ajustar procesos exige registrar el motivo y nuevo tiempo, sin cambiar muestras o criterios. No se solicita aquí permiso para ejecutar: ese productor aún no existe.

## 9. Qué vendría después, solo si hay separación

SEPARABILIDAD_LOGRADA permite **proponer**, no lanzar, un experimento de señal con cohortes nuevas de la reserva y los pares/orientaciones ya fijados, sin reutilizar calibración/validación. El responsable debe decidir si acepta un contraste factorial que requiera T distintas; eso no se convierte automáticamente en un efecto causal de c. Confianza y otras propiedades pueden seguir variando.

El siguiente diseño debe fijar antes de datos nuevos hipótesis, exposición temporal, desenlace rho_caras, X10 por celda, controles, compuertas de régimen, multiplicidad, potencia/N y semillas. Adoptará y congelará el [analista robusto auditado del PR #132](https://github.com/jaiborojas-cloud/leviathan/blob/1faf1b7530d7b29a796a7ad55f0b949e763fbbdd/experiments/DIN_borde/primaria_robusta/analisis_robusta_v1.py), SHA `1e2d903bfba8fa18a5eb6ecf5d93a759bc247009365c56ac561bc9b46604114d`, todavía BORRADOR: NO_APRENDIO < .5, recorte de prueba, D_sin_max y NO_ROBUSTO. Esta fase sin X/rho/D **no estima el efecto ni la potencia de la señal**; haría falta descubrimiento nuevo y potencia prospectiva antes del confirmatorio.

Se predeclara para el diseño siguiente una familia de **dos contrastes primarios**, uno por dirección de separación, con **Holm α = .05** y remuestreo pareado por split común. Ese diseño fijará signos, estadísticos y, si busca ausencia de efecto de escala, un margen de equivalencia y su potencia; p > .05 por sí solo no probará ausencia. No son seis PASS independientes por celda, ni se rescata el contraste con la mejor temperatura. El analista A1 univariado no implementa esa comparación entre D: deberá añadirse y auditarse un analista de contraste antes de congelar el experimento de señal. Se conserva la regla individual robusta y se declara por separado el contraste entre celdas. Aquí no se calculan esos p ni se fija su efecto objetivo.

**Roles:** este agente entrega solo el diseño borrador; Claude lo audita, el responsable congela, Claude implementa/publica el productor y el responsable ejecuta. NO_IDENTIFICABLE detiene esta vía bajo el protocolo: ningún ajuste de dosis, T o umbrales tras validación sin un nuevo diseño explícito y sus antecedentes declarados.
