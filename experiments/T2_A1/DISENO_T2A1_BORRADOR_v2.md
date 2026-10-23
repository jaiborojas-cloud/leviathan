# T2-A1 — diseño, BORRADOR v2 (2026-10-23)

**Estado:** borrador v2. Incorpora la revisión adversarial de Nemotron 3 Ultra (2026-10-23; sección 9), aprobada por el responsable el 2026-10-23 a las 08:24. Las decisiones de v1 siguen vigentes (sección 8). **No congelado.** No autoriza ejecutar nada salvo la fase 0a (implementación y pruebas del instrumento D, sin datos de la muestra confirmatoria). Antecedentes: [ANTECEDENTES.md](ANTECEDENTES.md).

## 0. Idea en una frase
Misma pregunta que T2-A0 (¿una señal geométrica temprana anticipa un evento geométrico posterior en el entrenamiento?), con un **desenlace que el instrumento pueda resolver siempre** y con un instrumento **validado en cobertura antes** de tocar la muestra confirmatoria.

## 1. Pregunta, población y muestras
- **Hipótesis primaria:** en trayectorias Wine true, mayor X en el update 5 implica mayor riesgo del evento D (sección 2) en visitas posteriores.
- **Predictor:** el mismo X sellado de T2-A0 (r* = 0.05697156262709151), sin recalcular. Así el predictor queda fijado antes de cualquier desenlace de T2-A1, y X sigue cerrado hasta congelar el instrumento.
- **Muestra de desarrollo:** splits 8–11 (20 trayectorias). Ya abiertos o reservados; ahí se diseña y valida el instrumento libremente.
- **Muestra confirmatoria:** splits 12–167 (780 trayectorias), sin ninguna visita futura abierta.
- Los splits 8–11 **no** entran en la evaluación confirmatoria.

## 2. Desenlace D: «el disco nominal no es construible»
Para cada visita (trayectoria, update k), se integra la exponencial desde P0 = (0,0) con el instrumento heredado (área 0.02, sin reducirla). La visita se clasifica en una de tres categorías:

| clase | definición | evidencia exigida |
|---|---|---|
| **D = 0, disco construible** | se alcanza área 0.02 con borde simple, sin conjugados ni colisiones | auditoría heredada T1-A/C1-A2 completa: INJECTIVE_AT_NOMINAL_RADIUS |
| **D = 1, disco no construible** | antes de llegar a 0.02 ocurre (a) no inyectividad geométrica, (b) conjugado o (c) escape de rayos | (a) o (b) por la auditoría heredada; o una **cota superior certificada** U del área alcanzable con U < 0.02 (1 − m), por la maquinaria T5 generalizada |
| **D = ?, no resuelta** | nada de lo anterior se establece con el presupuesto | se conserva; nunca es 0 |

- **Por qué cambia las pausas.** La mayoría de las pausas del lote 0 fueron por progreso radial bajo: el integrador se arrastra cerca de una métrica degenerada. Con D, ese arrastre no es el final: se activa la cota de área, que puede certificar D = 1 sin terminar la integración. **La fase 0 mide cuántas pausas resuelve realmente.**
- **No es un rescate:** el área sigue siendo 0.02. Se amplía qué cuenta como evento, y se declara que D ≠ Y de T2-A0. D incluye T5; Y no lo incluía.
- **Margen m = 0.025:** D = 1 por cota si U < 0.0195, igual que en T5 v1.
- **Robustez de la vía C (revisión, hallazgo 2).** Los factores de seguridad de T5 v1 (F_K = 4, F_T = 10, F_disc = 10) se validaron solo en tres estados. Si la cota fallara más en estados de curvatura alta, y esos tuvieran X alto, los falsos D = 1 se correlacionarían con X y **sesgarían el resultado a favor de la hipótesis**. Por eso, D = 1 por la vía C exige **U ≤ 0.0195 con los factores de T5 v1 y también con factores dobles** (F_K = 8, F_T = 20, F_disc = 20). Si solo pasa con los primeros, D = ?.

## 3. Visitas y Y
- **Y = 1** si alguna visita programada tiene D = 1. **Y = 0** solo si todas tienen D = 0. Si no, Y = ? (no es 0).
- **Horizonte: 3 visitas** (updates 50, 150, 250) en lugar de 10. Así se divide entre 3 o más el coste. Las 10 visitas de T2-A0 no aportaron resolución temporal útil (en el lote 0, el estado operacional de una trayectoria —evaluada o pausada— casi no cambió entre updates).
- **Disco:** guardar `ode_checkpoints` solo para visitas D = ?. Las visitas resueltas guardan estados y resúmenes. Objetivo ≤ 50 MB por visita resuelta.

## 4. Análisis primario
- **Estimando primario: W (dentro del split); G (global) es secundario.** Las dos opciones, por L5 (panel):
  - **(G) global**, como T2-A0: precision@top10 % de X sobre las 780 trayectorias, bootstrap de splits completos.
  - **(W) dentro del split:** dentro de cada split, ¿la inicialización con mayor X tiene evento con más frecuencia que el resto? Controla el efecto de panel, porque compara trayectorias del mismo split y el mismo panel.
  - **Compromisos para definir W en 0c, a ciegas (revisión, hallazgo 5):** (a) empates en X se rompen por índice de inicialización, regla fijada antes de abrir X; (b) los splits sin variación en Y (todos 0 o todos 1) no informan y salen del denominador; los que tienen Y = ? se tratan con las cotas por completación; (c) estadístico y prueba exacta por **permutación de Y dentro del split**; (d) **potencia simulada** con la tasa de eventos y de ? medida en 0b y 156 splits de 5 trayectorias. Si la potencia para el efecto de referencia (lift 2) es < 80 %, se reporta antes de abrir X y el responsable decide si sigue. (e) Se reporta siempre el número de splits efectivos.
  - Si W sale y G no, la señal es de trayectoria. Si solo sale G, puede ser de panel.
- **Comparadores geométricos** (C_A, Λ_0.1 %, R_eff), sellados igual que X: secundarios, misma cola. No son independientes de X (L4).
- **Comparadores no geométricos (revisión, hallazgo 8):** pérdida y precisión de validación y norma de los pesos en el update 5. Se calculan desde los `checkpoint_005` de `sources/`, **antes** de abrir cualquier desenlace confirmatorio, y se publican por hash. Secundario: lift de X condicionado a ellos (por ejemplo, dentro de terciles del comparador). Si X no añade nada sobre ellos, se reporta.
- **Desconocidos:** se reportan con cotas por completación binaria (sección 6 de E1, script ya validado) y se fija de antemano una **compuerta de cobertura**: si más del **10 %** de las trayectorias confirmatorias quedan con Y = ?, el veredicto es INCONCLUSIVE. **Ambas escalas (revisión, hallazgo 10):** se reportan siempre la fracción de visitas con D = ? y la de trayectorias con Y = ?. En 0c se fija, con la relación observada en 0b, la compuerta equivalente en visitas para los informes operacionales de la fase 2.
- **Eventos mínimos:** ≥ 40 trayectorias Y = 1 en ≥ 20 splits; si no, INCONCLUSIVE por información insuficiente.
- **Criterio de éxito:** W significativa al 5 % unilateral **y** lift global ≥ 2 con intervalo de bootstrap de splits por encima de 1. La prueba exacta de W (estadístico, permutación, empates) se fija en la congelación 0c.

## 5. Fases y compuertas
| fase | qué | dónde | compuerta para seguir |
|---|---|---|---|
| **0a. Instrumento D** | implementar D (auditoría heredada más cota T5 generalizada) y controles sintéticos | código | pruebas sintéticas y controles conocidos: j8/u25 (INJECTIVE vía D4) da D = 0; j5/u25 da D = 1 solo si también pasa con factores dobles (si no, D = ?, y se reporta). **Al cerrar 0a, el instrumento D queda congelado** (código, factores, t₀, rayo designado, topes). |
| **0b. Cobertura** | aplicar el instrumento **ya congelado**. Primaria: updates 50, 150 y 250 de los splits 8–11 (60 visitas: 43 del lote 0, más split10_j19 u150 y u250 y las 15 de split 11). Secundaria: las 128 del lote 0 | splits 8–11 | **D = ? en ≤ 5 % de las 60 visitas primarias (≤ 3)**; se reporta también la fracción de trayectorias con Y = ?; tiempo y disco medidos; X sigue cerrado. **0b solo mide: no ajusta el instrumento.** Si falla, el diseño no sigue tal cual: o una versión nueva del instrumento documentada (que repite 0a y 0b) o se abandona |
| **0c. Congelación** | congelar el análisis: definición de W, potencia simulada, comparadores no geométricos, compuertas en ambas escalas y reglas operacionales de la fase 2 (el instrumento ya está congelado desde 0a) | — | revisión adversarial y aprobación del responsable |
| **1. Apertura de X** | X se abre y su tabla, rangos y cola se publican por hash | — | solo después de 0c |
| **2. Confirmatoria** | visitas de los splits 12–167 por lotes, con informes operacionales sin desenlaces | 780 trayectorias | reglas de parada operacionales, como en T2-A0 |
| **3. Análisis** | una única evaluación primaria | — | — |

En 0b se ven desenlaces D de la muestra de desarrollo. Está permitido (es desarrollo) y se declara; como el instrumento ya está congelado, esos desenlaces no pueden afinarlo (revisión, hallazgo 6). Pueden informar solo la potencia simulada y las compuertas de 0c, y eso también se declara. Las 52 visitas evaluadas del lote 0 se reclasifican con D, no con la clasificación de T2-A0.

## 6. Recursos (estimación gruesa, la corrige 0b)
780 × 3 = 2340 visitas. Con 12 procesos y una mediana de 2.5 min, ≈ 8 h; con un 20 % de visitas que lleguen a la cota, quizá 1–2 días. Disco: ≈ 120 GB con 50 MB por visita.

## 7. Qué no se afirma
- D no es Y de T2-A0. Los resultados de T2-A1 no reabren T2-A0.
- El éxito sería predictivo, no causal; con L4, la parte transversal de la señal es esperada por Jacobi.
- Wine y la arquitectura 13→64→32→3 siguen siendo los mismos. La transferencia a otra tarea queda para T2-B.

## 8. Decisiones del responsable (2026-10-22 11:38: «acepto los 5 puntos»)
1. Margen m = 0.025 (U < 0.0195).
2. Horizonte de 3 visitas: updates 50, 150 y 250.
3. Estimando primario W (dentro del split); G secundario.
4. Compuertas de D = ?: ≤ 5 % en desarrollo (0b) y ≤ 10 % de trayectorias en la confirmatoria.
5. ≥ 40 trayectorias con evento en ≥ 20 splits; éxito con W al 5 % unilateral y lift global ≥ 2 con IC de splits > 1.

Siguen abiertos para 0c: la prueba exacta de W, la definición operativa de la cota generalizada (fase 0a) y las reglas operacionales de la fase 2.

## 9. Revisión adversarial (Nemotron 3 Ultra, 2026-10-23)
Tabla de 15 hallazgos, verificada contra los documentos por Claude y aprobada por el responsable el 2026-10-23 a las 08:24.
- **Incorporados:** 2 (factores dobles en la vía C, por riesgo de sesgo correlacionado con X); 5 (compromisos para W y potencia); 8 (comparadores no geométricos); 10 (cobertura en visitas y trayectorias); 6 (instrumento congelado al cerrar 0a; 0b solo mide); 4, parte 1 y 2 (potencia simulada en 0c); 11 y 12 (aclaraciones de conteo y tope).
- **Rechazados:** 1 (la pausa con radio nominal ocurre durante la auditoría; no hay clasificación INJECTIVE); 3 (dar Y = 0 con un 0 y el resto ? rompe la regla «? nunca es 0»); 4, parte 3 (ajustar la compuerta si 0b falla sería mover la portería); 9 (en la carta de cara, b = 0 es la salida del dominio; C3 y C5 exigen transversalidad y longitud finita; que no es aritmética de intervalos ya está declarado).
- 13–15: sin hallazgos (coherencia confirmada). Las filas 2, 7, 9 y 12 del archivo llegaron truncadas por el carácter «|»; la 7 no se pudo leer.

