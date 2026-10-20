# Anexo operativo de E1 — BORRADOR v2 (no vigente, no congelado)

**Estado:** borrador. Sustituye a v0 y v1. Fija provisionalmente la alarma de progreso radial (decisión del responsable, 2026-10-19 17:24 America/Mexico_City) y registra dónde habría disparado en los casos observados. Los valores marcados **[PENDIENTE]** no se han fijado: los fija el responsable del protocolo con la evidencia de la sección 2, **antes** de aplicar el anexo. Puede congelarse por separado de E1 (ver E1 v6, sección 5.3). Sin hash hasta entonces.
**Naturaleza:** presupuesto **operativo**, no evidencia científica. Ningún disparador clasifica una visita, asigna Y ni equivale a certificar una salida del dominio.

## 1. Alcance

- Aplica a las visitas de integración de rayos (calibración del radio nominal y auditorías) de T2-A0, a partir de su congelación.
- Aplicación a `split8_j5_true/update25`: retrospectiva, solo documental y operacional (E1 v6, sección 3 bis). Su detención histórica no se reinterpreta como fallo. **Reanudarla exige este anexo congelado** y una decisión expresa del responsable; este anexo no la autoriza.
- No modifica A = 0.02, rayos, semillas, tolerancias (DOP853, rtol 2e-10, atol 2e-12), jerarquía de refinamiento ni definición de Y.

## 2. Evidencia disponible (no se proponen valores aquí)

| Hecho | Fuente | Estado |
|---|---|---|
| Presupuesto histórico del Driver: 128 pasos nuevos por defecto, evaluado tras un paso aceptado y persistido | `resumable_dop853.py` (entrega de solo lectura, hash coincide con `script_hashes.json`) | verificado en el código |
| Presupuesto histórico del replay MPFR: `session_seconds` 900 o `session_steps` 60, evaluado tras un paso aceptado; guardado cada 4 pasos | `origin_mpfr_plan.json`, `origin_mpfr_replay.py` | verificado; configuración exacta usada en Windows no acreditada |
| No existe tiempo máximo que interrumpa `solver.step()` | mismas fuentes | verificado |
| Ninguna fuente cuenta intentos ni rechazos | mismas fuentes | verificado |
| 15 evaluaciones por paso aceptado + 12 por rechazo (DOP853, `dense_output`) | `medicion_rechazos.py`: 302 = 16·15 + 5·12 + 2 en j6 | medido, scipy 1.18.1, Windows |
| j6/update25 (sano): 16 pasos aceptados, 21 intentos, 5 rechazos, paso mínimo 7.7×10⁻⁴, 0.30 s/paso | salida de la terminal del usuario | medido |
| j5/update25 (copia regenerada, float64): 469 pasos, 511 intentos, 42 rechazos, paso ≈ 4.6×10⁻⁸ a 0.9331·R_ref tras 180 s, 0.36 s/paso | salida de la terminal del usuario | medido, con tope de tiempo |
| Replay MPFR de j5: ≈ 1–2×10⁻⁵ por paso entre r = 0.0743 y 0.0745; 14–29 s por paso aceptado; paso 139, r = 0.07447265825972331 | `task_log.csv` del retorno del PC | verificado; rechazos no contados |
| j6/update25 en **MPFR 169 bits**: 16 pasos aceptados, 21 intentos, 5 rechazos, 12.000 rhs por intento, nfev 302, paso mínimo 7.70315009666454×10⁻⁴, paso mediano 5.2×10⁻³, 15.5 s por paso (máx. 28.4 s), 308.6 s en total | `medicion_mpfr_j6.py`, salida de la terminal del usuario (CSV `12bf3c08…b1b8`, log `baaa2d69…661c`) | medido |
| j6 float64 frente a MPFR, paso a paso | comparación de ambos CSV | los 16 pasos tienen **los mismos intentos** (21 = 21, mismos pasos con rechazo); |Δt| ≤ 1.1×10⁻⁷ en los pasos; cociente de dt entre 0.99998 y 1.00002 salvo el último (el que ajusta el radio final); MPFR cuesta 50 veces más tiempo en total (306.6 s frente a 6.1 s) |
| j5/update25: dt medio por tramo de r | CSV float64 de j5 (copia regenerada) y `task_log.csv` del replay MPFR | float64 y MPFR **coinciden** en la meseta: ≈ 3.2×10⁻⁵ por paso en r ∈ [0.0725, 0.0743); desde r ≈ 0.0743 divergen (MPFR 2.1×10⁻⁵ → 4×10⁻⁷ hasta el paso 139; float64 4×10⁻⁷ de media en [0.0743, 0.0745) con 352 pasos y 4.6×10⁻⁸ al final) |
| j5 float64: pasos y tiempo hasta r < 0.0743 | CSV de j5 | 117 pasos aceptados, 143 intentos, 50.6 s (la meseta ya se alcanza hacia r ≈ 0.0725: 61 pasos, 29.3 s) |
| Hardware de la medición: AMD64 Family 23 Model 113 (Ryzen 3900X según el usuario), 24 núcleos lógicos, BLAS a 1 hilo, python 3.12.10, numpy 2.3.5, scipy 1.18.1 | salida de la terminal | verificado |
| Hardware y versiones de la corrida original | — | **no registrados** |

Lectura permitida (corrige la de v0):
- El tiempo por paso y la fracción de rechazos **no distinguen** un caso sano de uno cercano a la frontera: j6 y j5 cuestan lo mismo por paso en float64 (≈ 0.3 s) y los rechazos no explican la lentitud de j5.
- Lo que sí distingue es el **tamaño del paso aceptado**: en j6 es ≈ 5×10⁻³ (mínimo 7.7×10⁻⁴, en el primer paso) y en j5 cae a una meseta de ≈ 3.2×10⁻⁵ desde r ≈ 0.0725 (t/R_ref ≈ 0.909; a ≈ 2.6 % por debajo del radio 0.07447 de la frontera diagnosticada), unas 150 veces menor que el paso típico sano. Esa meseta aparece **igual en float64 y en MPFR**.
- Por tanto, el disparador de contracción del paso puede alcanzar a j5 en la meseta, tras ≈ 61 pasos y ≈ 29 s en float64, **antes** de que float64 y MPFR diverjan. La divergencia (paso final de 4.6×10⁻⁸ en float64 frente a 10⁻⁵ a 10⁻⁷ en MPFR) ocurre después de r ≈ 0.0743.
- Corrección: en v0 se afirmó que float64 y MPFR difieren 200–400 veces al mismo radio; eso solo es cierto para r ≳ 0.0744, no en la meseta.
- La causa de la divergencia final (¿redondeo en float64?) sigue siendo una **hipótesis no probada**: en el caso sano ambos regímenes toman las mismas decisiones de paso, y la diferencia solo aparece cerca de la frontera, lo que es compatible con la hipótesis pero no la prueba (además las aceleraciones se calculan con fórmulas distintas en cada régimen). No se escalan tiempos entre hardware distinto.
- Con un caso sano y uno cercano a la frontera, la ventana disponible para el umbral del paso aceptado es **(≈ 3.2×10⁻⁵, ≈ 5×10⁻³)** y en relación con R ≈ (4×10⁻⁴ R, 6×10⁻² R); fijar el valor es decisión del responsable y debe acompañarse de una ventana de pasos consecutivos.

## 3. Disparadores (regla de pausa)

Cada disparador produce **pausa y checkpoint** y registra la causa. Valores **[PENDIENTE]**.

| # | Disparador | Qué se mide | Valor |
|---|---|---|---|
| 1 | Tope de intentos por visita | intentos de paso, **contando rechazados** (contador alrededor del paso del solver, como en `medicion_rechazos.py`) | [PENDIENTE] por régimen |
| 2 | Presupuesto de tiempo por visita | tiempo de pared, con hardware, hilos y precisión registrados; **aplicado por intento**, no solo tras un paso aceptado | [PENDIENTE] por régimen |
| 3 | **Alarma de progreso radial** (absorbe el antiguo 4) | Δr_n = r_n − r_{n−1} de **pasos aceptados**; dispara si **Δr_n < 10⁻⁴ durante 8 pasos aceptados consecutivos**; estado `PAUSED_LOW_RADIAL_PROGRESS` | **FIJADO provisionalmente**: 10⁻⁴ (unidades absolutas del radio intrínseco; ≈ 0.00125·R_ref con R_ref = 0.0797751845662646) y 8 pasos; el mismo valor en float64 y MPFR |
| 4 | (absorbido por el 3) | — | — |
| 5 | Alarma auxiliar: condición de G | max cond(G) en una carta fijada y declarada | [PENDIENTE]; solo alarma |

Regímenes: **float64 DOP853** y **MPFR 169 bits**. Los disparadores 1 y 2 (intentos y tiempo) se declaran **por régimen**, porque MPFR cuesta ≈ 50 veces más tiempo por paso. El colapso posterior de float64 (r ≳ 0.0743) no se usa para decidir.

### 3.1 Especificación de la alarma de progreso radial

- Δr_n = r_n − r_{n−1}, **únicamente para pasos aceptados**. Los intentos rechazados no entran.
- El contador vuelve a cero cuando Δr_n ≥ 10⁻⁴.
- El contador se **guarda y restaura** entre sesiones (forma parte del checkpoint).
- Se **excluye** del contador el paso recortado solo para alcanzar el extremo final de la integración.
- Al dispararse: guardar checkpoint y registrar `PAUSED_LOW_RADIAL_PROGRESS`. **No** se asigna clasificación ni outcome; no certifica salida del dominio.
- Esta alarma **no interrumpe** un `solver.step()` prolongado: ese caso lo cubren, por separado, los presupuestos de intentos y de tiempo (disparadores 1 y 2), que deben evaluarse **por intento**, no solo tras un paso aceptado.
- El umbral está en unidades absolutas, sin normalizar por un radio nominal aún desconocido. Está ligado a las tolerancias DOP853 (rtol 2e-10, atol 2e-12): si cambian, el umbral deja de estar justificado y debe revisarse en un anexo versionado.
- **Estatus:** alarma operacional provisional, informada por j5 y j6. No es una validación independiente ni demuestra que los estados que la disparen sean irresolubles. La ventana de 8 pasos no está validada poblacionalmente; una visita sana podría disparar la alarma, y eso se registra como pausa, no como evento.
- **Tras un disparo:** la visita queda pausada. Continuarla requiere una autorización expresa y registrada del responsable. **[DECIDIR]** si esa autorización es caso a caso o si se define un procedimiento de revisión.

### 3.2 Dónde habría disparado (retrospectivo, simulado con los CSV de medición)

| Caso | Resultado de la simulación | Fuente |
|---|---|---|
| j6/update25, float64 | **no dispara**; Δr mínimo 7.70×10⁻⁴ (7.7 veces el umbral), sin contar el paso final | `medicion_rechazos_j6.csv` |
| j6/update25, MPFR | **no dispara**; mismo mínimo 7.70×10⁻⁴ | `medicion_mpfr_j6.csv` |
| j5/update25, float64 (copia regenerada) | **habría disparado en el paso aceptado 50**, r = 0.07217 (t/R_ref = 0.9047), tras 74 intentos y 25.2 s acumulados; de los 469 pasos de la medición, 427 estaban bajo el umbral | `medicion_rechazos_j5.csv` |
| j5/update25, replay MPFR | **no determinable paso a paso** con los registros que tengo: el `task_log.csv` da el radio cada 4 pasos desde el paso 94; el promedio por bloque (3.2×10⁻⁵ a 3.4×10⁻⁵ hasta el paso 118) está por debajo del umbral, pero los pasos 1–93 no se pueden inspeccionar sin deserializar los paquetes | `RIPG_RESULTADOS_PC.zip` |

Esto documenta retrospectivamente dónde habría disparado en una **copia regenerada**; no cambia la naturaleza de la pausa histórica de j5 ni de ningún otro caso.

## 4. Checkpoint al pausar

Pesos, estado de Adam, RNG y estado del integrador (como el esquema ya existente de `ode_resume_*`), con hash del paquete, contadores de pasos, intentos y rechazos, tiempo de pared y de CPU, hardware, hilos y versiones. Una pausa no es FAIL, ni INCONCLUSIVE, ni evidencia topológica.

## 5. Piloto operativo de 20 visitas (aprobado, **no abierto**)

- Las 20 visitas son las primeras del orden de cohorte en update 25: `split8_j5` a `split11_j24` (splits 8, 9, 10 y 11, cinco inicializaciones cada uno), **incluyendo las ya abiertas**: se reutiliza j6 y se conservan los parciales (j5, j7, j8). No se eligen por facilidad ni por X.
- **Qué es:** una prueba de viabilidad operativa. **No estima frecuencias**: son 4 splits y, dentro de un split, `f` es idéntico entre inicializaciones, con mucha varianza entre splits en los basales (0.346 en el `min_eff` y 0.894 en el `cond` de cribado).
- **Qué no es:** no establece el veredicto predictivo (solo cubre update 25; los negativos requieren las diez visitas). El resultado confirmatorio depende íntegramente de T2-A0.
- **Compuerta de viabilidad operacional:** número de visitas aún sin resolver tras el presupuesto y el procedimiento de revisión definidos. Valor **[PENDIENTE]**. Consecuencia: detener nuevas aperturas y revisar el diseño; **nunca** asignar outcomes ni clasificar.
- Registro por visita en tres ejes no excluyentes: diagnóstico geométrico, estado operacional, desenlace de trayectoria (E1 v6, sección 7).
- Si la revisión concluye que el evento exige dominios que el constructor no puede auditar de forma fiable, se cierra T2-A con el resultado que corresponda bajo su protocolo y se abre otro diseño prospectivo conservando todos los casos. Cambiar el evento o el dominio sería un estudio nuevo.

## 6. Pendientes antes de congelar

1. Instrumentar el conteo de intentos y rechazos en la corrida productiva (o justificar su equivalencia: en j6 el contador y el solver de la medición dieron los mismos intentos en float64 y MPFR).
2. Fijar los valores que siguen [PENDIENTE] en la sección 3 (disparadores 1, 2 y 5), por régimen, con la evidencia de la sección 2. El disparador 3 ya está fijado provisionalmente.
3. (Resuelto) Hipótesis del redondeo: decidido (2026-10-19) **no probarla ahora**; queda declarada como pendiente y el criterio de paso no depende de ella.
4. Inventario fechado de visitas abiertas y reconciliación con los registros locales posteriores al corte (2026-10-17 03:46 UTC).
5. SHA-256 de cada archivo final y commit de congelación.

## 7. Qué no se afirma

No se afirma que algún disparador indique frontera, conjugado o pérdida de inyectividad. No se afirma la frecuencia de pausas ni de salidas de dominio en la cohorte. Las mediciones son de una sola corrida por caso, sobre copias regeneradas, en un hardware concreto.
