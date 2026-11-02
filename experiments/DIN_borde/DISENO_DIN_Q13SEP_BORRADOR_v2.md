# DIN-Q13-SEP · piloto de separabilidad · BORRADOR v2

**2026-11-02, hora de México. Para revisión de Claude; no congelado ni autorizado para ejecutar.** Responde a la auditoría del PR #134. Se conservan íntegros el [borrador v1](DISENO_DIN_Q13SEP_BORRADOR_v1.md), su configuración, fuentes y manifiestos. La decisión de estudiar esta vía sigue siendo la del responsable, PR #133, commit `168352e84bfb9b45610ba3e66836ad455751fe44`.

Cambios: criterio principal **solo u250**; u10 descriptivo. Para igualar escala se construye una temperatura T* de LP por unidad/visita. Para aproximar c se usa una rejilla fina y una minimización predeterminada, sin escoger por D ni por diferencia de escala. Se actualizan cantidades, tiempos, controles y alcance de una futura señal. No se ejecutan modelos ni se obtienen mediciones en esta entrega.

## 1. Pregunta, alcance y momento principal

En las gaussianas s = .8, ¿el protocolo A0/LP permite comparar **E: distinta concentración diagonal con igual escala** y **C: distinta escala con concentración aproximadamente igual**, en **u250**, que es el modulador estudiado por Q13-DR/M2?

Solo u250 determina dosis, orientaciones, calidad principal y separabilidad. La falta de Δc en u10 **no** impide pasar. u10 se mide con reglas homólogas por visita y se reporta como descriptor de evolución, sin requisito de separación ni influencia en la elección de λ. No se exige un mismo T para u10 y u250.

Un éxito es **separabilidad operacional del factorial y sus algoritmos de emparejamiento**. No demuestra identificación causal del colapso ni mantiene fijas confianza, traza o toda la distribución de logits. Los dos contrastes principales cruzan los brazos entrenados; la separación disponible dentro de LP solo por temperatura se informa aparte y nunca los rescata.

## 2. Familia, receta y fuentes congeladas

Se conservan los de v1, detallados aquí para evitar una dependencia ambigua:

- Tres gaussianas en d = 13. Medias (2,0), (−1,√3), (−1,−√3) en las primeras dos coordenadas; restantes cero. Por split, 39 ruidos estándar por clase y x = media_y + .8·ruido. Primeros 30 por clase en train (**90**); últimos 9 en panel (**27**). StandardScaler ajustado solo en train. Sin Wine, datos externos o test.
- MLP float64 **13→64→32→3**, ReLU, `l1/l2/l3`. Adam lr = .006, lote 64 sin reemplazo, 250 updates sin parada por precisión. Visitas **10/250**. Entre brazos de cada r=(split,k): mismos datos, pesos iniciales y lotes. Cada temperatura usa el checkpoint de ese brazo, no otro entrenamiento.
- **A0 = CE normal**. **LP = CE(z,y)+λ·mean_n sum_c z_nc²** sobre el lote de train. LP no centra z en la penalización; es la receta M2. S sí centra los logits entre clases al medir. No cambiar receta, optimizador o dosis durante el entrenamiento.
- Core `make_geom_state(model_T,Xpanel,ypanel)` y `subset_M(Rb,Ub,[0,1,2])` sin modificar, SHA `b5251d2f1f082ae014596574e9ab827dde04aec785bf76091005f8149ba31ffd`. N = **27** en U; cabeza reducida con clase 2 de referencia; RHO = 1e−4 y piso del máximo autovalor del Gram 1e−14 originales. Recalcular R/U/Gram/Fisher/ridge/M, sin aproximación diagonal ni gradientes reutilizados.
- f = primeras dos columnas estandarizadas del panel, devueltas por core, fija por split y común a brazos/T. No PCA o perspectivas aprendidas.
- Geometry SHA `b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3` y rho r3 SHA `2ac015a263afb44616de0fceebd3b1d2a36ad0a76cd466adcdcc7e3adb8b8df0` intactos. Se verifican como archivos; **no se llama a rho, exp-map o curvatura**.

[Fuentes y SHA heredados](Q13SEP/fuentes/provenance.json). Versiones: torch 2.9.1+cpu, numpy 2.3.5, scipy 1.17.0, sklearn 1.8.0. El productor no puede usar `core.load_split`, datos Wine ni los medidores altos de G3 que calculan X/rho.

### Temperatura como punto de parámetros

Para cada medida, cargar una **copia fresca** del checkpoint original y dividir **W y b completos de `l3` entre T** bajo no_grad; salir de ese bloque antes del core, que necesita autograd. No modificar `l1/l2`, el checkpoint, RNG u optimizador originales, ni encadenar divisiones. Recalcular todo el instrumento desde la copia. No equivale a un wrapper de probabilidades con otros gradientes, un pullback por T o M/T².

A0 se mide como ancla a **T=1**, en ambas visitas. La v2 reemplaza la rejilla gruesa .5/1/2 de v1 por los roles de LP de los §§4–5. No se ejecutan además las medidas de v1.

## 3. Fases, muestra y variables

| Fase | Splits × inicios | Brazos entrenados | Entrenamientos |
|---|---|---|---:|
| Calibración | 10 × 5 | A0 + LP λ ∈ {.0001,.0003,.001,.003} | 250 |
| Validación independiente | 20 × 5 | A0 + menor λ apta | 200 |
| Máximo | semillas distintas entre fases | | **450** |

La rejilla LP toma las cuatro primeras dosis de la [calibración M2](Q13M2/calibracion/RESULTADO_v1.md), basada en métricas de concentración, no en D. La calibración nueva usa **solo c y S de u250** para elegir λ y las orientaciones de los dos contrastes. No usa u10, q, tr M, confianza o precisión para ordenar dosis. La calidad es una compuerta común de fase, no una excusa para descartar una dosis y favorecer otra.

Variables por medida: c=max diag M/tr M, q=||M−diag(diag M)||_F/||M||_F, tr M; **S_panel = sqrt(mean_{n,c}(z_nc−mean_d z_nd)²)** sobre 27×3; S_train descriptiva; confianza media verdadera y media máxima del panel; precisión train/panel. c es concentración diagonal, no λmax/tr ni rango efectivo. No normalizar M por traza.

Guardar estado/error, λ, T y rol, índices, hashes de M/f/checkpoints originales y transformados, lotes, tiempos y memoria; pesos/RNG/Adam/datos/M completos fuera de Git. No reescribir estados MEDIDA por un NO_APRENDIO final. **No calcular X, R de confianza del difícil, mínimo de p_y, rho, L/Y del desenlace rho, D, p-valores, W ni asociaciones de señal.** El core usa internamente probabilidades y Rb de gradientes, lo cual no es calcular esos estadísticos.

## 4. E: emparejamiento exacto de escala por unidad y visita

Para cada LP_λ, r y visita v, medir las escalas sin temperatura S_A0(1) y S_LP(1). Definir:

**T*_E(r,v,λ) = S_LP(1)/S_A0(1)**, aplicado **a LP**, manteniendo A0 a T=1.

Así S_LP(T*) = S_A0(1) algebraicamente. Implementar log T* = log S_LP(1) − log S_A0(1), y obtener T* sin redondeo si es representable. T* no se proyecta a la rejilla de C, no se recorta a un intervalo y no se refina mirando c. Si escalas o T* no son finitas y positivas, conservar el fallo; no inventar un piso o una temperatura sustitutiva.

Medir el modelo LP con esa cabeza escalada y recalcular M. Verificar **|S_LP(T*)−S_A0(1)|/S_A0(1) ≤ 1e−12**. Es una comprobación numérica de la construcción, reemplaza el margen de 10 % de v1 y no se usa para buscar otra T. Los fallos numéricos de esta igualdad se reportan, no se convierten en «falta física de separación».

Unidad r cumple E principal si en **u250** el emparejamiento es válido y **σ_E[c_A0(1)−c_LP(T*)] ≥ .15**, con σ_E fijada en calibración. u10 tiene su propio T*_10 y se reporta con la misma σ_E de u250, sin elegir dosis/orientación con esa visita. **No se exige que E pase en u10**, ni que T*_10=T*_250.

## 5. C: concentración emparejada por rejilla fina prefijada

Para cada LP_λ, r y visita v, medir la rejilla completa:

**T_j = 2^(j/8), j = −16,…,16**, **33 puntos** desde .25 a 4, incluido T=1. Evaluar en orden j ascendente, con W/b de l3 y M nuevos por punto. LP(T=1), j=0, proporciona también S_LP(1) para E; no hace falta otra medida de referencia LP.

Elegir **j_C = argmin_j |c_LP(T_j)−c_A0(1)|**. Resolver empates exactos, sin redondeo, por **menor |j| y después menor j**: se prefiere la intervención menor. El orden es, por tanto, la clave lexicográfica **(|Δc|, |j|, j)**. Publicar los empates y las 33 medidas.

La búsqueda usa **solo |Δc|**: no filtrar primero por S, confianza, signo de escala o criterio C. Si el ganador no separa la escala, C falla; **no se pasa al segundo mejor**. Si falta algún punto de la rejilla o su c es inválida, no se conoce el mínimo de la rejilla completa: C queda no definido para esa unidad/visita, sin tratar puntos fallidos como +∞ ni repetirlos. No interpolar, ampliar la rejilla o ejecutar otro optimizador.

Unidad r cumple C principal si en **u250** el ganador es válido, **|c_LP(T_C)−c_A0(1)| ≤ .05** y **σ_C[log S_A0(1)−log S_LP(T_C)] ≥ log(1.5)**, con σ_C fijada en calibración. El ratio se calcula como diferencia de logs para evitar desbordes. S entra solo **después** de seleccionar T_C por c.

u10 obtiene su propio mínimo T_C10 y su diagnóstico con σ_C de u250, sin rescatar o vetar la principal. Una falta de cobertura en [.25,4] se reporta como límite de esta rejilla, no como inexistencia de una temperatura útil fuera de ella.

## 6. Calibración, calidad y decisión final

Para cada λ y pregunta, probar orientaciones **+1 antes que −1**. Un split cumple si al menos **3 de sus 5 unidades planificadas** cumplen la pregunta **en u250**. Inválidas y ausentes permanecen en el denominador de cinco. Es apta la primera orientación que cumpla en **≥8/10 splits** de calibración. λ es apta si E y C tienen orientación apta; elegir la **λ más pequeña apta**. Si no existe: NO_IDENTIFICABLE/CALIBRACION_SIN_DOSIS y no entrenar validación.

Publicar por SHA antes de validación `DOSIS_Y_REGLAS_Q13SEP_v2.json`: dosis, σ_E/σ_C, ancla A0/T1, fórmula T*, rejilla y clave de argmin C, márgenes, calidad y conteos. Lo que se fija es **la regla de emparejamiento**, no un par constante de temperaturas. En validación cada unidad aplica esa misma regla a su geometría; no se cambian λ, orientaciones, rejilla, desempate o umbrales con los resultados.

En validación se exige **E en ≥16/20 splits y C en ≥16/20**, con calidad y controles principales válidos. Cumplidos ambos: **SEPARABILIDAD_LOGRADA**. Cualquier otro patrón: **NO_IDENTIFICABLE** y detener la vía bajo este diseño. Los .15/.05/1.5, inclusivos, no cambian ni se estiman con D; la igualdad de escala E pasa a ser la construcción numérica del §4.

### Calidad principal solo u250

Dominios: métricas finitas, tr M>0, norma de M>0, c∈(0,1], q/confianzas/precisiones∈[0,1], escalas positivas. Sin clipping/jitter o sustitución. Acc_train en u250 de T1 **<.5** produce NO_APRENDIO de ese entrenamiento; .5 exacto se admite. La etiqueta afecta elegibilidad, sin borrar datos ni reescribir visitas.

Un r completo principal tiene todos sus **brazos, puntos de rejilla, ancla y E** válidos en **u250**, sin NO_APRENDIO; los criterios de separación pueden fallar con datos completos. Se exige calidad conjunta de toda la fase: **≥48/50 r completos y ≥8/10 splits con ≥3 completos en calibración**, considerando los cinco brazos; **≥95/100 y ≥16/20** en validación, A0/LP. No se descartan dosis selectivamente por falta de datos. Calidad insuficiente detiene con NO_IDENTIFICABLE/CALIDAD_INSUFICIENTE, sin concluir ausencia física de separación.

**u10 es descriptivo:** fallos o falta de separación puntuales de u10 no entran en estos denominadores ni vetan u250. Se conservan todos sus estados y motivos, y el informe distingue los diagnósticos disponibles de las 50/100 unidades planificadas. No buscar otra dosis porque u10 no separe. Un fallo de medición u10 no debe abortar el entrenamiento sano: se continúa hacia u250 sin repetir la medida fallida. Un defecto global de código/fuentes o fallo de controles oficiales sí invalida la corrida completa.

### Procedencia y temperatura sola

Cada par E/C sigue siendo **A0 frente a LP**, con A0/T1. Reportar por unidad si LP usa T=1 o T distinta y las distribuciones de T*, T_C y j_C. Etiquetas: ENTRE_BRAZOS_T_FIJA / ENTRE_BRAZOS_T_EMPAREJADA; se resume cuántas unidades requieren ajuste, sin atribuir el resultado solo al entrenamiento.

Sensibilidad descriptiva, sin rescate: dentro de LP comparar cada punto T_j≠1 con LP(T1) y tabular cuáles conservan c dentro de .05 y cambian S por factor ≥1.5 en cada visita, con ambas orientaciones. No se elige un ganador de esta tabla. Para E, dentro del mismo checkpoint igualar S requiere T*=1 y no cambia c: no puede producir la separación E por temperatura sola. No hace falta medir la rejilla de A0 para estos diagnósticos; **A0 se mide únicamente en T1**. Si solo hay separación SOLO_TEMPERATURA, el global sigue NO_IDENTIFICABLE.

## 7. Controles y semillas

Fuentes/receta/pareado/versions de v1 permanecen; un hilo por proceso. Verificar datos/f y hashes de pesos iniciales y lotes pareados, checkpoint original inmutable y copias frescas. Para cada medida, z_T=z_1/T y S_T=S_1/T con error normalizado por max(1,norma del esperado) **≤1e−12**, y precisión train/panel idéntica entre T. No exigir invariancia de c/q/traza/confianza.

**Control de rutas T1 (antes control 2):** comparar con la ruta mínima original de receta a partir de los mismos datos/pesos, con error relativo Frobenius M **≤1e−12**, f idéntica y c/q coherentes; se verifica junto con las reconstrucciones siguientes. Esta tolerancia permite diferencias de redondeo entre rutas de construcción/copia algebraicamente equivalentes, no acepta cambiar el instrumento.

**Tres reconstrucciones lossless, todas u250:** calibración s0/k0/A0/T1; s0/k0/LP01/GRID j0; s0/k0/LP01/GRID j−16 (T=.25). Recargar pesos/panel float64 sin pérdida y ejecutar **la misma ruta congelada**, con el mismo orden, versiones, dispositivo e hilos. Se exige **error Frobenius relativo 0 y f idéntica**, como test de reproducibilidad exacta de idénticos bytes/algoritmo en el entorno fijado. No es una afirmación de exactitud matemática o de intervalos. A diferencia del control T1 entre rutas, aquí no debería cambiar el camino de operaciones. Si no reproduce 0, conservar el fallo y revisar implementación/entorno; no relajar a 1e−12 después de verlo. Las primeras dos reconstrucciones sirven también para el contraste de rutas T1; no añadir llamadas no presupuestadas.

Las tres comprobaciones oficiales se concentran en u250, para no convertir un objetivo descriptivo de u10 en compuerta biológica. Anomalías de u10 se conservan y reportan; un defecto global de implementación se corrige solo mediante enmienda y nueva versión. Un control oficial fallido deja la corrida INVALIDA y la vía detenida, sin interpretación física del no emparejamiento.

Semillas **sin cambios**: calibración 71.000.000+s / 71.100.000+5s+k / 71.200.000+5s+k; validación 72.000.000+s / 72.100.000+5s+k / 72.200.000+5s+k. [Inventario v1](Q13SEP/SEMILLAS_PROPUESTAS_v1.md), 330 entradas escalares del piloto, reserva futura 73 millones intacta. La nueva rejilla y T* son deterministas, no necesitan semillas nuevas. Actualizar el cotejo de registros publicados antes de congelar, excluyendo solo las propias definiciones Q13SEP. No se usa la reserva CIFAR-F2 ni datos de etapas anteriores.

## 8. Cantidades, coste revisado y prueba corta

A0 tiene **1** punto por visita. Cada LP tiene **33 GRID + 1 E_MATCH** por visita, **34**. El C elegido **referencia una fila GRID ya medida**; no calcula M otra vez. E_MATCH es una evaluación adicional prefijada desde copia fresca, incluso si T* coincide exactamente con un GRID: no es reintento de una medida fallida. El LP de referencia T1 es GRID j0. Así el universo no depende del éxito del emparejamiento.

| Fase | Entrenamientos | Medidas/celdas u250 principales | Medidas u10 descriptivas | Máximo total M de fase |
|---|---:|---:|---:|---:|
| Calibración, 50 r | 250 | 50·(1+4·34)=**6.850** | 6.850 | **13.700** |
| Validación, 100 r | 200 | 100·(1+34)=**3.500** | 3.500 | **7.000** |
| Total | **450** | **10.350** | **10.350** | **20.700** |

Añadir tres reconstrucciones de control: **20.703 llamadas M máximas**, frente a 2.703 de v1. La celda v2 se identifica por **entrenamiento, visita y rol/punto**, porque T* puede variar entre visitas; no usar el antiguo conteo de 1.350 celdas compartidas por u10/u250. Filas fallidas se conservan aunque no se pueda determinar T* o ejecutar M; son máximos de llamadas, no medidas observadas.

El crecimiento está en M, **no** en entrenamientos; no multiplicar toda la duración de 33 s por el factor de rejillas. Con 12 procesos y eficiencia ilustrativa .8:

T_pared ≈ [450·t_train + 20.703·t_M + t_IO]/(12·.8).

Escenarios aritméticos, **sin medición del MLP**, usando 33 s por entrenamiento como proxy conservador tomado de la latencia individual de CIFAR (que incluía otras tareas):

| t_M por llamada supuesto | Proyección sin IO |
|---:|---:|
| .1 s | **29,4 min** |
| .5 s | **43,8 min** |
| 1 s | **61,7 min** |

El proxy asigna todo el tiempo CIFAR al entrenamiento y vuelve a presupuestar M: es deliberadamente conservador, **no un límite demostrado**. El MLP es pequeño y no hay búsqueda rho; se espera un coste por M manejable, pero solo la prueba corta lo confirmará. Presupuesto orientativo revisado: **30–75 min**, más preparación/IO. Se mantiene la parada operacional si la proyección supera **90 min** o no cabe el paralelismo; informar al responsable antes de continuar, sin ampliar/reducir muestras o rejilla silenciosamente. El rendimiento global de ≈2,8 s por finalización con 12 procesos no es una latencia individual.

**Prueba corta:** primeras tres unidades de calibración (s0,k0/1/2), todos los cinco brazos: **15 entrenamientos**; 3·[2+4·2·34]=**822 medidas M** más tres controles = **825 llamadas máximas**. Son parte del universo, sin repetir IDs ni semillas. Tarea del pool = un entrenamiento; pueden ocuparse 12 procesos, spawn y un hilo. Registrar tiempo de entrenamiento sin medidas, tiempo M, resto de medidas/IO, latencia individual total sin cola y elapsed global con arranque de procesos. Publicar mediana/máximo de t_M por rol/visita y memoria; proyectar fases pendientes con sus cantidades reales, conservando fallos. No deducir coste de una única llamada o del contenedor del agente.

## 9. Después del piloto: temperaturas y estimando de señal

Solo SEPARABILIDAD_LOGRADA permite **proponer** un estudio de señal con datos nuevos y una versión auditada/final de la primaria robusta del PR #132, actualmente BORRADOR, SHA `1e2d903bfba8fa18a5eb6ecf5d93a759bc247009365c56ac561bc9b46604114d`. Este piloto no calcula X, rho o D ni estima la potencia de señal.

**Si un contraste usa temperatura, cambian con ella X10, L=log rho(10) e Y=log rho(250)**: se deben recomputar probabilidades, gradientes, Fisher/ridge/M y rho de cada celda. No basta cambiar c o usar X/rho de T1. Sería un estimando explícito entre celdas calibradas, no exactamente la primaria de la red sin temperatura ni un cambio puro de concentración. No se reescriben las confirmaciones anteriores.

El diseño de señal deberá fijar **antes de entrenar** cómo obtiene T10 y T250, si la regla es por unidad o global, cuáles modelos sirven de ancla, y qué datos pueden usarse. **No aplicar T_C250 a u10 y llamar tempranos a X10/L sin reconocer que se usó información futura.** Una alternativa será una regla T10 obtenida solo de información disponible en u10 o de calibración independiente, y una regla T250 publicada de antemano; los valores pueden diferir y definen otra trayectoria de calibración. No elegir entre esas políticas después de mirar D. Las dependencias por usar un A0 pareado como ancla también deben quedar explícitas: no se presupone un predictor desplegable de una red aislada.

Se conserva la familia propuesta de **dos contrastes primarios E/C, Holm α=.05**, con remuestreo pareado por split y analista de contraste entre D auditado. El analista robusto univariado no basta por sí solo para ese contraste; hay que fijar signo, hipótesis, potencia/N, régimen y, si se busca ausencia de efecto de escala, margen de equivalencia y potencia apropiados. No comparar significaciones independientes de celdas ni interpretar p>.05 como equivalencia. Los datos del piloto no se reutilizan como cohorte de señal; la reserva 73 millones sigue sin N elegido.

**Roles:** este agente entrega solo el borrador; Claude audita, el responsable congela, Claude implementa/publica el productor y el responsable ejecuta. No se crea productor ni se corre piloto aquí. NO_IDENTIFICABLE detiene esta vía bajo este protocolo; no se amplía la rejilla, cambia el momento principal o se buscan otros algoritmos con los mismos resultados sin un nuevo diseño explícito.
