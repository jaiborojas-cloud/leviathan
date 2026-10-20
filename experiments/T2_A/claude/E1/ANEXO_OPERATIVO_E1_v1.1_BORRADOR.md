# Anexo operativo de E1 — versión 1.1 (BORRADOR 2, no vigente, no congelado)

**Estado:** borrador 1 del 2026-10-19 ≈23:40; **borrador 2 del 2026-10-20 ≈11:50** (America/Mexico_City), a petición del responsable (se añaden T4 y T5 y se corrige la motivación). **No está en vigor.** El anexo v1.0 congelado (SHA-256 `a7cb20d87f0c96b1962ccc56da15d0df23338c908659f3c469c12d5d93d84085`) rige todo hasta que este borrador se congele con hash y E1 lo cite en una versión nueva.
**Naturaleza:** presupuesto y manejo **operativos**, no evidencia científica. No clasifica por sí mismo, no asigna Y.

## 1. Alcance y motivación (declarados para que no se confundan)
- **Motivo de T1–T2 (presupuesto):** el piloto produjo una visita con evento candidato (`split10_j17_true`, `GEOMETRIC_NONINJECTIVITY`) y los topes de v1.0, calibrados con visitas sanas (j6: 60–145 s por visita, 187–653 intentos), quedan ajustados para el camino de refinamiento: 65 integraciones, 3341 intentos, 563 s de integración sobre un tope de visita de 900 s (63 %), y una integración de 8192 rayos de ≈ 99 s sobre un tope de 120 s (83 %). Una visita candidata con 16384 rayos pausaría por tiempo sin que haya fallo. Evidencia de una sola visita candidata (j17); valores provisionales.
- **Motivo de T4–T5 (escape de rayos):** el diagnóstico de solo lectura del 2026-10-20 (`piloto/diagnostico_escape/`) muestra en `split8_j5`, `j7` y `j8` que un sector de rayos sale de la carta a distancia intrínseca finita (|p| ≈ −C·ln(t*−t), |v| ≈ C/(t*−t)); reproducido en MPFR de 169 bits (no es ruido de precisión). Consecuencias: (a) en j5 y j7 el área del disco medida con la exponencial no llega a 0.02 antes del escape (j5: 0.01847 en t = 0.07402, 0.018714 en 0.07447 según el agente original; j7: 0.01853 en t = 0.07418, escape en 0.07466, ≈ 0.0188 por extrapolación **no medida**); (b) en j8 el disco nominal existe (A = 0.02 en t ≈ 0.0792) y queda antes del escape (t* ≈ 0.08746), pero la cota de búsqueda de la calibración (0.09) queda detrás: ninguna integración hasta 0.09 puede terminar.
- **Qué NO es:** no rescata visitas. El área nominal **A = 0.02 no se reduce ni se redefine** en ningún caso. Este borrador no decide por sí mismo la suerte de j5, j7 y j8 (ver sección 4, decisiones D1–D3); hasta que se congele, siguen `PAUSED_PENDING_REVIEW`.

## 2. Cambios respecto a v1.0
| # | v1.0 | v1.1 propuesto | Regla |
|---|---|---|---|
| T1 | Tope de tiempo por integración, float64: 120 s | **max(120 s, 0.04 s × n_rayos)** (2048 → 120 s; 4096 → 164 s; 8192 → 328 s; 16384 → 655 s) | j17 midió ≈ 0.012–0.014 s/ray; 0.04 s/ray ≈ 3× lo medido. Para ≤ 2048 rayos no cambia |
| T2 | Tope de tiempo por visita: 900 s | **900 s si la visita no entra a la etapa de refinamiento; 3600 s si entra** (la condición `candidate` que ya calcula `topological_map.result`) | j17: 563 s de integración, 895 s de sesión |
| T3 | Reanudación | Sin cambio; el presupuesto adicional duplica los topes vigentes (T1 y T2 incluidos) | — |
| T4 | Cota de búsqueda fija (0.09, ×1.25 si hace falta) | **Detección de escape y cota adaptativa** (2.1) | j8 |
| T5 | Sin estado para «el disco nominal no es construible» | **Estado nuevo explícito** (2.2) | j5, j7 |

### 2.1 T4 — detección de escape y cota adaptativa
- **Qué detecta (y qué no):** el escape se identifica por **crecimiento no acotado de max|p|** en la carta con colapso geométrico de dt, **no por dt solo**. Motivo: la alarma de progreso (dt < 10⁻⁴ durante 8 pasos) es sensible pero no específica: en j9 disparó (47 pasos) y la integración terminó con |p| acotado; en j17 no disparó. Un colapso de dt con |p| acotado (cercanía a un punto conjugado) **no** es escape y se trata con las reglas de v1.0.
- **Indicadores medidos en los tres positivos** (dt ×0.8–0.85 y |v| ×1.25 por paso; max|p| +≈ 11 por paso con dt → 0; 1/|v| lineal en t): se toman como definición de trabajo. **Los umbrales numéricos (ventana de pasos, tolerancia del ajuste de 1/|v|, valor de |p| para cortar) NO se fijan aquí:** se determinarán con j5, j7 y j8 como positivos y con j6, j9, j17 y las 14 visitas restantes del piloto como negativos, sin mirar X ni resultados, y se hashearán antes de usarse. Requisito de validación: el detector no debe dispararse en ninguna visita ya evaluada; si se dispara en una, T4 no se congela.
- **Acción:** al detectar escape en una integración de rayos con cota B, se estima t* (ajuste de polo simple, orientativo) y se sustituye B por un radio B' < t* alcanzado por la propia integración (el último checkpoint con |p| bajo el corte). Se calcula el área del disco hasta B':
  - si A(B') ≥ 0.02 → la calibración continúa en [0, B'] con el procedimiento de v1.0 (el radio nominal es el mismo que daría una cota mayor, porque A es creciente en t);
  - si A(B') < 0.02 → no se concluye nada por extrapolación sola: pasa a T5.
- **Salvaguardas:** la sustitución de B no modifica A = 0.02, rayos, tolerancias ni el solver; se registra en el resultado (`cota_original`, `cota_adaptativa`, `t_star_estimado`, indicadores). Requiere el checkpoint de paso/tiempo de v1.0 (no consume presupuesto adicional).

### 2.2 T5 — estado nuevo
- **Nombre propuesto:** `NOMINAL_DISK_NOT_CONSTRUCTIBLE_RAY_ESCAPE` (alternativas del responsable: `BOUNDARY_AREA_BELOW_THRESHOLD`, `SUBCRITICAL_DOMAIN_AREA`; lo importante es que sea un estado explícito y registrado, no una omisión).
- **Definición:** una o más geodésicas de la exponencial dejan de existir en la carta (escape confirmado) a un radio t*_min en el que el área del disco construido con la exponencial es **menor que 0.02**; por tanto el radio nominal no puede definirse con el mismo procedimiento. **No** es `INJECTIVE_AT_NOMINAL_RADIUS`, **no** es `GEOMETRIC_NONINJECTIVITY`, **no** es `INCONCLUSIVE`/`NUMERICAL_FAILURE` ni cero, y **no** asigna Y.
- **Certificación (requisitos; el valor numérico de la cota se fija con el responsable y la opinión estadística):** (i) escape confirmado por dos vías independientes (float64 y MPFR, coincidencia de los instantes de cruce de |p|); (ii) área medida A(B') con convergencia entre rejillas (nt, nt/2, nr/2); (iii) una **cota superior verificable** del área en t*, no una extrapolación, y con margen respecto a 0.02. Con la información de hoy, j7 (≈ 0.0188 frente a 0.02, margen ≈ 6 %) **no** cumple (iii): no está certificado. j5 tiene medidas de dos fuentes pero tampoco una cota superior.
- **Advertencia de alcance:** que el disco construido con la exponencial no alcance 0.02 antes del escape no implica que la bola geodésica de ese radio tenga área < 0.02 (otros rayos continúan). T5 se define sobre el procedimiento de E1 (exponencial con todos los rayos), no sobre la bola métrica.
- **Tratamiento en el análisis:** **no está decidido.** Es un tercer resultado no binario con riesgo de sesgo de selección (2 de 20 en el piloto, concentrados en un split). Su tratamiento en el análisis (reporte aparte, sensibilidad, partial identification de la sección 6 de E1 v8, que sigue SIN APROBAR) se fija en la enmienda E2 con opinión estadística externa, no aquí.

Sin cambio: tope de intentos, alarma de progreso, presupuesto adicional, revisión (3.3), compuerta del piloto, tolerancias DOP853, A = 0.02.

## 3. Limitaciones
- T1–T2 son una regla de margen sobre una visita candidata; otra candidata podría necesitar más. La memoria/E-S de checkpoints con 16384 rayos no está medida. Aplica a float64; en MPFR el tope por integración sigue siendo 3600 s.
- T4–T5: tres positivos, todos del split 8 y con el escape por un sector similar (≈ 5.45–5.6 rad en el ángulo normalizado de cada estado); no hay base para generalizar. El diagnóstico se hizo en el contenedor (float64) y falta repetirlo en el equipo del responsable.
- Requiere cambios en `visita_completa_instrumentada.py` y en el flujo de calibración; se implementarán y validarán **después** de congelar, repitiendo j6 (15/15 PASS) y j17 (sin cambios), más un ensayo de T4 sobre j8.

## 4. Decisiones pendientes del responsable (antes de congelar)
- **D1.** Aprobar o ajustar T1 y T2.
- **D2.** Aprobar la estructura de T4 (indicador por |p| y no por dt solo) y que sus umbrales se fijen con datos y se hasheen antes de usarse.
- **D3.** Aprobar T5 (nombre y definición), reconociendo que la certificación de j5 y j7 como ese estado exige una cota verificable del área que hoy no existe.
- **D4.** Retroactividad: si, una vez congelado, se permite reabrir j8 con T4 (es el único caso donde A = 0.02 queda antes del escape), o si el piloto se cierra con j5, j7 y j8 como están. Mi recomendación es decidirlo **antes** de mirar nada más y registrarlo, para que no dependa del resultado.

## 5. Para congelar
SHA-256 del anexo final → nueva versión de E1 que lo cite → SHA-256 → manifiesto y commit de congelación (orden de sellado de v1.0).
