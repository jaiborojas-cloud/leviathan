# Enmienda E1 al preregistro T2-A0 — BORRADOR v4 (no vigente, no congelado)

**Estado:** borrador para revisión del responsable del protocolo; sin efecto hasta que se congele con hash. Sustituye a v1, v2 y v3.
**Advertencia de procedimiento:** el análisis complementario de la sección 6 se define **después** de observar un caso (split8_j5_true, update 25, paso 139). El preregistro prohíbe corregir el contrato retrospectivamente tras resultados; por eso esta enmienda no modifica nada confirmatorio y se registra como desviación documentada.
**Condiciones previas de aplicación:** no se aplica hasta que existan (i) el anexo operativo de la sección 5 y (ii) el inventario fechado de la sección 8. Los puntos **[DECIDIR]** son del responsable del protocolo.

## 1. Hechos que motivan la enmienda

1. split8_j5_true, régimen true, update 25 (integración MPFR; el paso aceptado 139 no es un update). Radio integrado r₁₃₉ = 0.07447265825972331. El radio nominal de esa visita no está determinado.
2. En los rayos 1775 y 1776 las coordenadas P divergen (velocidad en coordenadas de 7.3×10⁴ a 2.89×10⁷ entre los pasos 94 y 139) con rapidez intrínseca ≈ 1 (vᵀGv = 0.99999999766); la condición de G alcanza 3.32×10¹¹ y 2.50×10¹¹. Las aceleraciones coinciden con referencias de 80 y 120 dígitos en 14 rayos.
3. Datos compatibles con una frontera de la familia softmax a distancia intrínseca finita (solo permanecen los componentes 6 y 13), fuera del dominio original. Radio de llegada local mínimo ≈ 0.07447421007, entre los rayos 1775 y 1776. Certificación global: **INCONCLUSIVE**.
4. Área diagnóstica del prefijo ≈ 0.0187 (< 0.02), **no** certificada como A_embed. No se ha demostrado punto conjugado ni pérdida de inyectividad.
5. Reproducción exploratoria en doble precisión, desde las semillas del manifiesto tras pasar la compuerta del update 5 (state_025_regen.npz; R_ref = 0.0797751845662646, radio nominal basal): max cond(G) = 95.8 a 0.80·R_ref, 256 a 0.85·R_ref y 1.05×10⁵ a 0.90·R_ref; la integración se atasca a 0.95·R_ref. split8_j6_true update 25 no muestra señales de borde hasta 0.95·R_ref. Evidencia exploratoria, no certificación.
6. La integración heredada (`rays`) no impone límite de pasos ni de tiempo: ante esta frontera se arrastra con pasos cada vez menores en vez de lanzar excepción.
7. El caso observado demuestra una posibilidad. **No estima su frecuencia en la cohorte.**

## 2. Decisión del responsable del protocolo

Se elige la opción **C** para el resultado confirmatorio de T2-A0 y la opción **A corregida** como análisis complementario. No se adopta la opción B porque cambia la pregunta científica.

> Se conserva el análisis confirmatorio y la compuerta técnica de T2-A0. Las visitas no resueltas mantienen su disposición INCONCLUSIVE conforme al contrato original. La eventual certificación de una salida del dominio se registra como diagnóstico adicional, sin convertirla en evento ni en resultado negativo.
> Se incorpora un análisis complementario de identificación parcial, definido después de observar split8_j5_true/update25. Este análisis evalúa la sensibilidad a los desenlaces no determinados mediante cotas sobre todas las asignaciones compatibles. Sus resultados no sustituyen el veredicto de T2-A0 ni permiten declarar PASS_PROSPECTIVE_PILOT cuando la regla original lo impide.
> Esto no obliga a detener la recopilación de datos: se pueden completar las visitas previstas y reportar los hallazgos, aunque la compuerta original impida un veredicto confirmatorio concluyente.

## 3. Lo que NO cambia

Predictor X y r* = 0.05697156262709151; predictores y comparadores sellados; cola 10 %; elegibilidad basal; definición de Y; criterios íntegros T1-A/C1-A2; jerarquía de refinamiento; calibración heredada del radio nominal A = 0.02, **sin reducirlo para rescatar un caso**; horizonte 250 y visitas 25, 50, …, 250; bootstrap de splits completos (20000, semilla 220020); criterios 1–6 de PASS_PROSPECTIVE_PILOT y compuerta técnica global; clasificaciones de visitas ya cerradas. split8_j5_true update 25 **permanece INCONCLUSIVE** y no cuenta como Y = 0.

## 4. Sentido de «fallo técnico» en el contrato

«Fallo técnico» significa que **no se pudo completar la auditoría exigida por el contrato**. No afirma que la causa sea un defecto numérico: la causa puede ser geométrica, pero requiere certificación. Hasta tenerla, la visita permanece INCONCLUSIVE y mantiene la compuerta técnica global.

## 5. Diagnóstico adicional y regla operativa de pausa

**5.1 Diagnóstico adicional: salida del dominio certificada (no clasifica).** Cuando exista evidencia certificada, se anota sobre la visita INCONCLUSIVE un diagnóstico «salida del dominio nominal»: no es evento (Y = 1), no es negativo (Y = 0) y no levanta la compuerta. Requiere ambas:
- (a) cota superior certificada r₀ del radio de llegada de al menos un rayo a la frontera de la familia, con r₀ < R_nom (aritmética exacta o integración con error acotado; la coincidencia numérica entre precisiones no basta);
- (b) cota superior certificada del **área inmersa** barrida hasta r₀ (integral del elemento de área sobre el disco de radio r₀, que acota por arriba el área embebida), con valor < 0.02.

**5.2 Regla operativa de pausa (separa presupuesto operativo de evidencia científica).** Debe incluir, como mínimo:
- (i) máximo de pasos intentados por visita, **contando los rechazados**;
- (ii) presupuesto de tiempo por visita, con hardware, hilos y precisión registrados;
- (iii) detección de falta de progreso radial, con escala y ventana explícitas;
- (iv) condición de G como **alarma auxiliar**, en una carta fijada y declarada.

Todo disparador produce **pausa y checkpoint** (pesos, Adam, RNG, estado del integrador); **ninguno** clasifica ni equivale a certificar una salida del dominio.

**5.3 Anexo operativo.** Los valores numéricos no se fijan aquí. Primero evidencia: inspección de solo lectura de `rays` y de los registros (controles existentes, pasos aceptados y rechazados, progreso radial, tiempos, precisión, condiciones de salida y capacidad de reanudación). Después, los valores se declaran en un anexo operativo, versionado y con hash, **antes de aplicar la regla**. Hasta que exista ese anexo, la regla no está en vigor. Hash del anexo: [ ].

## 6. Análisis complementario de identificación parcial (exploratorio-descriptivo)

**6.1 Desenlace no determinado (Y_ND).** Trayectoria sin Y = 1 confirmado y con al menos una visita no clasificada INJECTIVE_AT_NOMINAL_RADIUS (INCONCLUSIVE por cualquier causa, NUMERICAL_FAILURE, pausa, faltante o interrumpida). Un positivo confirmado resuelve Y = 1 aunque otra visita sea desconocida (contrato original). Y_ND no equivale a salida de dominio certificada.

**6.2 Asignaciones compatibles.** Todo vector en {0,1}^{n_ND} para las trayectorias Y_ND. La cola (10 % superior de X, empates completos) depende solo de X y no cambia con la asignación.

**6.3 Cotas.** Precisión en cola, tasa base, lift y diferencia (precisión − tasa base) son monótonas en cada Y_ND, con signo opuesto según esté dentro o fuera de la cola. Sus extremos se alcanzan en asignaciones **adversas por posición**, no en «todos a 0» y «todos a 1»:
- cota inferior: Y_ND dentro de la cola → 0; Y_ND fuera de la cola → 1;
- cota superior: Y_ND dentro de la cola → 1; Y_ND fuera de la cola → 0.

*Ejemplo ilustrativo (números inventados):* N = 800, cola = 80, positivos confirmados 12 dentro y 28 fuera, Y_ND = 10 dentro y 100 fuera. «Todos a 0»: lift 3.00; «todos a 1»: lift 1.47. Asignación adversa inferior: lift 0.86; superior: 4.40.
El efecto de los Y_ND sobre las cotas depende de **dónde** están (dentro o fuera de la cola) y no solo de cuántos son.

**6.4 Intervalos (exploratorios).** Se reporta el intervalo bootstrap percentil [Q₀.₀₂₅(L*), Q₀.₉₇₅(U*)], con L* y U* las cotas inferior y superior de cada réplica, como **intervalo exploratorio con cobertura no validada para este diseño**. Que use extremos de cotas no garantiza por sí solo una cobertura mínima del 95 %. Hay que distinguir la cobertura del parámetro de la cobertura de toda la región identificada; métodos de tipo Imbens–Manski los distinguen y requieren condiciones adicionales (no verificadas en este documento) **[revisión estadística externa pendiente]**.
Se mantienen 20 000 remuestreos de splits completos y la semilla 220020, recalculando la cola y las cotas en cada réplica.
*Definición del lift.* Con tasa base positiva y cola no vacía, el lift está definido (aunque pueda ser muy inestable). Con tasa base igual a cero, muestra vacía o cola vacía, **no está definido**. Si alguna asignación compatible de Y_ND produce tasa base cero, se informa esa posibilidad y no se presenta una cota del lift como si estuviera definida en todas las asignaciones. En el bootstrap se registran el número y la proporción de réplicas no definidas; **no se eliminan** para calcular percentiles sobre las restantes como si fueran el procedimiento original. Hasta que ese tratamiento se especifique y valide, el **intervalo del lift queda no evaluable** bajo el método propuesto; las cotas puntuales que sí estén definidas pueden reportarse. No se introduce ningún porcentaje de réplicas inválidas elegido tras ver resultados. La diferencia (precisión − tasa base) está definida con tasa base cero siempre que la cola no esté vacía.
*Estatus del procedimiento.* Es una **propuesta exploratoria sin cobertura validada**; no ha sido aprobada por revisión estadística y no debe presentarse como tal. La revisión estadística externa es necesaria antes de atribuirle cobertura nominal o de usarla para decisiones inferenciales; puede quedar pendiente mientras E1 conserve el veredicto original.
Este intervalo no decide PASS/FAIL de T2-A0.

**6.5 Resultados descriptivos.** Se reportan: n_ND por update, por split y por causa; fracción de la cola con Y_ND; cotas de precisión, tasa base, lift y diferencia con sus intervalos; retirada de cada split bajo la cota inferior; el criterio de ≥ 30 eventos en ≥ 10 splits evaluado solo con Y = 1 confirmado. Se informa si cada criterio 3–6 se cumple **bajo todas** las asignaciones compatibles. Ninguna cifra sustituye el veredicto de T2-A0 ni permite declarar PASS_PROSPECTIVE_PILOT cuando la regla original lo impide.

## 7. Reporte de incidencia y estructura del informe

Se reporta siempre la incidencia, **independientemente de su magnitud**, separando:
1. salidas de dominio certificadas (diagnóstico de 5.1);
2. sospechas de salida pendientes de certificación;
3. pausas por presupuesto y otras auditorías irresueltas;
4. trayectorias con Y no determinado.

El informe final **abre con el resultado bajo T2-A0**, incluso si es INCONCLUSIVE. Después puede desarrollar la incidencia de salida de dominio como hallazgo descriptivo central, sin sustituir la pregunta original y sin equiparar Y_ND con salida certificada.
No se detiene la recopilación: se completan las visitas previstas y se reportan los hallazgos aunque la compuerta original impida un veredicto confirmatorio concluyente.

## 8. Inventario previo y aplicación

Antes de aplicar E1 debe existir un **inventario fechado** que distinga visitas **clasificadas**, **abiertas** y **aún no iniciadas**: basta un manifiesto con identificadores, estado, fecha de corte y hash, sin duplicar resultados. «Visitas aún no clasificadas» se entiende según ese inventario.
- No se usa para elegir, excluir ni reemplazar trayectorias, ni para modificar X, comparadores, umbrales, cola o Y.
- El mecanismo exploratorio de la escala de la métrica (cociente de Rayleigh ρ_min) **no forma parte** de esta enmienda.
- Los análisis exploratorios sobre estados de update 25 de split8_j5_true y split8_j6_true son copias regeneradas desde semillas y no sustituyen ninguna corrida confirmada. Verificación del prefijo de 5 updates exigida por A0 (parámetros ≤ 1e−12): reportada para j5 (max|Δθ| = 6.9×10⁻¹⁶); **pendiente para j6** (solo se reportó max|ΔM| = 2.1×10⁻¹¹). **Mientras siga pendiente, j6 queda fuera de las comparaciones exploratorias admitidas**; el acuerdo en M no sustituye la comprobación exigida sobre θ. Esta verificación no es requisito para certificar una salida del dominio ni, necesariamente, para congelar E1.
- El inventario puede mantenerse en un manifiesto separado, referenciado por su hash. Toda visita no listada se considera NO_INICIADA a la fecha de corte.

## 9. Qué no se afirma

No se afirma que la salida del dominio sea un evento geométrico intrínseco, ni su frecuencia, ni que prediga o evite la pérdida de inyectividad, ni que el primer borde global esté certificado, ni que las cotas de la sección 6 sean una estimación del efecto (solo miden sensibilidad a lo no determinado) ni que sus intervalos tengan una cobertura determinada.

## 10. Registro de integridad (completar al congelar)

Hash de esta enmienda: [ ]. Fecha y hora de congelado: [ ]. Anexo operativo: [ ]. Inventario fechado (manifiesto separado): [ ]. Soporte (expediente): state_025_regen.npz `845c2251…4776`; state_025_regen_j6.npz `0e3fbfd3…6cac`; snapshot de referencia state.npz `6713246b…e19c`; snapshot zip `9970F036…749E`; sondeo_j5_u25.csv `38B5D4BE…1F3B`; sondeo_j6_u25.csv `4522E8C6…EEE2`.
