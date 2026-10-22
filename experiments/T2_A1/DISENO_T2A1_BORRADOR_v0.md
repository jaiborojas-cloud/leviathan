# T2-A1 — diseño, BORRADOR v0 (2026-10-22)

**Estado:** borrador para discusión. **No autoriza ejecutar nada.** Los puntos **[DECISIÓN]** los resuelve el responsable; después se pasa por revisión adversarial y se congela por fases (fase 0 primero). Antecedentes: [ANTECEDENTES.md](ANTECEDENTES.md).

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
- **[DECISIÓN]** margen m de la cota (en T5 v1 se usó 0.0195 = 0.02 × 0.975).

## 3. Visitas y Y
- **Y = 1** si alguna visita programada tiene D = 1. **Y = 0** solo si todas tienen D = 0. Si no, Y = ? (no es 0).
- **[DECISIÓN] Horizonte:** propongo **3 visitas** (updates 50, 150, 250) en lugar de 10. Así se divide entre 3 o más el coste. Las 10 visitas de T2-A0 no aportaron resolución temporal útil (en el lote 0, el estado operacional de una trayectoria —evaluada o pausada— casi no cambió entre updates).
- **Disco:** guardar `ode_checkpoints` solo para visitas D = ?. Las visitas resueltas guardan estados y resúmenes. Objetivo ≤ 50 MB por visita resuelta.

## 4. Análisis primario
- **[DECISIÓN] Estimando primario.** Dos opciones, por L5 (panel):
  - **(G) global**, como T2-A0: precision@top10 % de X sobre las 780 trayectorias, bootstrap de splits completos.
  - **(W) dentro del split:** dentro de cada split, ¿la inicialización con mayor X tiene evento con más frecuencia que el resto? Controla el efecto de panel, porque compara trayectorias del mismo split y el mismo panel. Por ejemplo: proporción de splits «discordantes» donde el top-X tiene Y = 1 y algún otro Y = 0, frente a los concordantes inversos; prueba de signos o permutación dentro del split.
  - Propuesta: **W primaria y G secundaria**. Si W sale y G no, la señal es de trayectoria. Si solo sale G, puede ser de panel.
- **Comparadores** (C_A, Λ_0.1 %, R_eff), sellados igual que X: secundarios, misma cola.
- **Desconocidos:** se reportan con cotas por completación binaria (sección 6 de E1, script ya validado) y se fija de antemano una **compuerta de cobertura**: si más del **[DECISIÓN] 10 %** de las trayectorias confirmatorias quedan con Y = ?, el veredicto es INCONCLUSIVE.
- **[DECISIÓN] Eventos mínimos:** por ejemplo, ≥ 40 trayectorias Y = 1 en ≥ 20 splits; si no, INCONCLUSIVE por información insuficiente.
- **Criterio de éxito [DECISIÓN]:** por ejemplo, W significativa al 5 % unilateral y lift global ≥ 2 con intervalo de bootstrap de splits por encima de 1.

## 5. Fases y compuertas
| fase | qué | dónde | compuerta para seguir |
|---|---|---|---|
| **0a. Instrumento D** | implementar D (auditoría heredada más cota T5 generalizada) y controles sintéticos | código | pruebas sintéticas y controles conocidos: j8/u25 (INJECTIVE vía D4) da D = 0; j5/u25 (T5 certificado) da D = 1 |
| **0b. Cobertura** | aplicar D a las visitas de desarrollo: las 128 del lote 0 (estados ya en D) y split 11 en 50/150/250 | splits 8–11 | **D = ? en ≤ 5 % [DECISIÓN] de las visitas**; tiempo y disco por visita medidos; X sigue cerrado |
| **0c. Congelación** | congelar el instrumento, la cola de visitas, el análisis y los umbrales (sección 4) | — | revisión adversarial (otro modelo) y aprobación del responsable |
| **1. Apertura de X** | X se abre y su tabla, rangos y cola se publican por hash | — | solo después de 0c |
| **2. Confirmatoria** | visitas de los splits 12–167 por lotes, con informes operacionales sin desenlaces | 780 trayectorias | reglas de parada operacionales, como en T2-A0 |
| **3. Análisis** | una única evaluación primaria | — | — |

En 0b se ven desenlaces D de la muestra de desarrollo. Está permitido (es desarrollo) y se declara. Las 52 visitas evaluadas del lote 0 se reclasifican con D, no con la clasificación de T2-A0.

## 6. Recursos (estimación gruesa, la corrige 0b)
780 × 3 = 2340 visitas. Con 12 procesos y una mediana de 2.5 min, ≈ 8 h; con un 20 % de visitas que lleguen a la cota, quizá 1–2 días. Disco: ≈ 120 GB con 50 MB por visita.

## 7. Qué no se afirma
- D no es Y de T2-A0. Los resultados de T2-A1 no reabren T2-A0.
- El éxito sería predictivo, no causal; con L4, la parte transversal de la señal es esperada por Jacobi.
- Wine y la arquitectura 13→64→32→3 siguen siendo los mismos. La transferencia a otra tarea queda para T2-B.

## 8. Decisiones pendientes (resumen)
1. Margen m de la cota (sección 2).
2. Horizonte: ¿3 visitas (50/150/250) o 10?
3. Estimando primario: ¿W (dentro del split), G (global) o ambos co-primarios?
4. Compuerta de cobertura confirmatoria (10 %) y de desarrollo (5 %).
5. Mínimo de eventos y criterio de éxito.
