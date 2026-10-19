# Enmienda E1 al preregistro T2-A0 — BORRADOR v2 (no vigente, no congelado)

**Estado:** borrador para revisión del responsable del protocolo; sin efecto hasta que se congele con hash. Sustituye al borrador v1.
**Advertencia de procedimiento:** el análisis complementario de la sección 6 se define **después** de observar un caso (split8_j5_true, update 25, paso 139). El preregistro prohíbe corregir el contrato retrospectivamente tras resultados; por eso esta enmienda no modifica nada confirmatorio y se registra como desviación documentada.
Los puntos **[DECIDIR]** son del responsable del protocolo.

## 1. Hechos que motivan la enmienda

1. split8_j5_true, régimen true, update 25 (integración MPFR; el paso aceptado 139 no es un update). Radio integrado r₁₃₉ = 0.07447265825972331. El radio nominal de esa visita no está determinado.
2. En los rayos 1775 y 1776 las coordenadas P divergen (velocidad en coordenadas de 7.3×10⁴ a 2.89×10⁷ entre los pasos 94 y 139) con rapidez intrínseca ≈ 1 (vᵀGv = 0.99999999766); la condición de G alcanza 3.32×10¹¹ y 2.50×10¹¹. Las aceleraciones coinciden con referencias de 80 y 120 dígitos en 14 rayos.
3. Datos compatibles con una frontera de la familia softmax a distancia intrínseca finita (solo permanecen los componentes 6 y 13), fuera del dominio original. Radio de llegada local mínimo ≈ 0.07447421007, entre los rayos 1775 y 1776. Certificación global: **INCONCLUSIVE**.
4. Área diagnóstica del prefijo ≈ 0.0187 (< 0.02), **no** certificada como A_embed. No se ha demostrado punto conjugado ni pérdida de inyectividad.
5. Reproducción exploratoria en doble precisión, desde las semillas del manifiesto tras pasar la compuerta del update 5 (state_025_regen.npz; R_ref = 0.0797751845662646, radio nominal basal): max cond(G) = 95.8 a 0.80·R_ref, 256 a 0.85·R_ref y 1.05×10⁵ a 0.90·R_ref; la integración se atasca a 0.95·R_ref. split8_j6_true update 25 no muestra señales de borde hasta 0.95·R_ref. Evidencia exploratoria, no certificación.
6. La integración heredada (`rays`) no impone límite de pasos ni de tiempo: ante esta frontera se arrastra con pasos cada vez menores en vez de lanzar excepción.

## 2. Decisión del responsable del protocolo

Se elige la opción **C** para el resultado confirmatorio de T2-A0 y la opción **A corregida** como análisis complementario. No se adopta la opción B porque cambia la pregunta científica.

> Se conserva el análisis confirmatorio y la compuerta técnica de T2-A0. Las visitas no resueltas mantienen su disposición INCONCLUSIVE conforme al contrato original. La eventual certificación de una salida del dominio se registra como diagnóstico adicional, sin convertirla en evento ni en resultado negativo.
> Se incorpora un análisis complementario de identificación parcial, definido después de observar split8_j5_true/update25. Este análisis evalúa la sensibilidad a los desenlaces no determinados mediante cotas sobre todas las asignaciones compatibles. Sus resultados no sustituyen el veredicto de T2-A0 ni permiten declarar PASS_PROSPECTIVE_PILOT cuando la regla original lo impide.
> Esto no obliga a detener la recopilación de datos: se pueden completar las visitas previstas y reportar los hallazgos, aunque la compuerta original impida un veredicto confirmatorio concluyente.

## 3. Lo que NO cambia

Predictor X y r* = 0.05697156262709151; predictores y comparadores sellados; cola 10 %; elegibilidad basal; definición de Y; criterios íntegros T1-A/C1-A2; jerarquía de refinamiento; calibración heredada del radio nominal A = 0.02, **sin reducirlo para rescatar un caso**; horizonte 250 y visitas 25, 50, …, 250; bootstrap de splits completos (20000, semilla 220020); criterios 1–6 de PASS_PROSPECTIVE_PILOT y compuerta técnica global; clasificaciones de visitas ya cerradas. split8_j5_true update 25 **permanece INCONCLUSIVE** y no cuenta como Y = 0.

## 4. Sentido de «fallo técnico» en el contrato

«Fallo técnico» significa que **no se pudo completar la auditoría exigida por el contrato**. No afirma que la causa sea un defecto numérico: la causa puede ser geométrica, pero requiere certificación. Hasta tenerla, la visita permanece INCONCLUSIVE y mantiene la compuerta técnica global.

## 5. Diagnóstico adicional: salida del dominio certificada (no clasifica)

Cuando exista evidencia certificada, se anota sobre la visita INCONCLUSIVE un diagnóstico «salida del dominio nominal», sin convertirlo en evento (no es Y = 1), sin convertirlo en negativo (no es Y = 0) y sin levantar la compuerta. Requiere ambas:
- (a) cota superior certificada r₀ del radio de llegada de al menos un rayo a la frontera de la familia, con r₀ < R_nom (aritmética exacta o integración con error acotado; la coincidencia numérica entre precisiones no basta);
- (b) cota superior certificada del **área inmersa** barrida hasta r₀ (integral del elemento de área sobre el disco de radio r₀, que acota por arriba el área embebida) con valor < 0.02.

**Regla operativa de parada (no clasifica) [DECIDIR umbrales]:** para evitar integraciones indefinidas, una visita se detiene y se registra como auditoría incompleta si ocurre alguno de: condición de G > [1e8] en algún rayo antes de R_nom; tamaño de paso < [ε] durante [N] pasos consecutivos; tiempo de pared por radio > [T]. Documenta la causa de la disposición INCONCLUSIVE; no la cambia.

## 6. Análisis complementario de identificación parcial (exploratorio-descriptivo)

**6.1 Desenlace no determinado (Y_ND).** Trayectoria sin Y = 1 confirmado y con al menos una visita no clasificada INJECTIVE_AT_NOMINAL_RADIUS (INCONCLUSIVE por cualquier causa, NUMERICAL_FAILURE, faltante o interrumpida). Un positivo confirmado resuelve Y = 1 aunque otra visita sea desconocida (contrato original).

**6.2 Asignaciones compatibles.** Todo vector en {0,1}^{n_ND} para las trayectorias Y_ND. La cola (10 % superior de X, empates completos) depende solo de X y no cambia con la asignación.

**6.3 Cotas.** Precisión en cola, tasa base, lift y diferencia (precisión − tasa base) son monótonas en cada Y_ND, de signo opuesto según esté dentro o fuera de la cola. Sus extremos se alcanzan en las asignaciones **adversas por posición**, no en «todos a 0» y «todos a 1»:
- cota inferior: Y_ND dentro de la cola → 0; Y_ND fuera de la cola → 1;
- cota superior: Y_ND dentro de la cola → 1; Y_ND fuera de la cola → 0.

*Ejemplo ilustrativo (números inventados):* N = 800, cola = 80, positivos confirmados 12 dentro y 28 fuera, Y_ND = 10 dentro y 100 fuera. «Todos a 0»: lift 3.00; «todos a 1»: lift 1.47. Asignación adversa inferior: lift 0.86; superior: 4.40. El rango compatible [0.86, 4.40] es más ancho que el de los dos escenarios [1.47, 3.00].

**6.4 Intervalos [DECIDIR el procedimiento].** Bootstrap de splits completos (20000, semilla 220020), re-aplicando la regla de cola en cada remuestreo, con empates. En cada remuestreo se calculan ambas cotas. El intervalo del conjunto identificado es [percentil 2.5 de la cota inferior, percentil 97.5 de la cota superior]. Cobertura aproximada y conservadora, no exacta. Alternativas a considerar con asesoría estadística: intervalos de tipo Imbens–Manski.

**6.5 Resultados descriptivos.** Se reportan: n_ND por update y por split, por causa; fracción de la cola con Y_ND; cotas de precisión, tasa base, lift y diferencia con sus intervalos; retirada de cada split bajo la cota inferior; criterio de ≥ 30 eventos en ≥ 10 splits evaluado solo con Y = 1 confirmado. Se informa si cada criterio 3–6 se cumple **bajo todas** las asignaciones compatibles. Ninguna de estas cifras sustituye el veredicto de T2-A0 ni permite declarar PASS_PROSPECTIVE_PILOT cuando la regla original lo impide.

## 7. Continuidad

No se detiene la recopilación: se completan las visitas previstas y se reportan los hallazgos, aunque la compuerta original impida un veredicto confirmatorio concluyente.

## 8. Aplicación y registro

- No se usa para elegir, excluir ni reemplazar trayectorias, ni para modificar X, comparadores, umbrales, cola o Y.
- El mecanismo exploratorio de la escala de la métrica (cociente de Rayleigh ρ_min) **no forma parte** de la enmienda.
- Los análisis exploratorios sobre estados de update 25 de split8_j5_true y split8_j6_true son copias regeneradas desde semillas y no sustituyen ninguna corrida confirmada. Verificación del prefijo de 5 updates exigida por A0 (parámetros ≤ 1e−12): reportada para j5 (max|Δθ| = 6.9×10⁻¹⁶); **pendiente para j6** (solo se reportó max|ΔM| = 2.1×10⁻¹¹).

## 9. Qué no se afirma

No se afirma que la salida del dominio sea un evento geométrico intrínseco, ni que ocurrirá con frecuencia, ni que prediga o evite la pérdida de inyectividad, ni que el primer borde global esté certificado. Las cotas de la sección 6 no son una estimación del efecto, solo la sensibilidad a lo no determinado.

## 10. Registro de integridad (completar al congelar)

Hash de esta enmienda: [ ]. Fecha y hora de congelado: [ ]. Soporte (expediente): state_025_regen.npz `845c2251…4776`; state_025_regen_j6.npz `0e3fbfd3…6cac`; snapshot de referencia state.npz `6713246b…e19c`; snapshot zip `9970F036…749E`; sondeo_j5_u25.csv `38B5D4BE…1F3B`; sondeo_j6_u25.csv `4522E8C6…EEE2`.
