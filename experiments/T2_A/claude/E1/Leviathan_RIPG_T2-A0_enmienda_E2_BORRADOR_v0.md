# Enmienda E2 al preregistro T2-A0 — BORRADOR v0 (2026-10-21)

**Estado:** borrador, **no congelado, sin dictamen estadístico externo y no aplicable a datos**. Lo redactó la línea claude por encargo del responsable (Jaibo Rojas). Los puntos marcados **[DECISIÓN]** son del responsable; los marcados **[DICTAMEN]**, de la revisión estadística externa.
**Qué cubre:** lo que E1 v9 y el anexo operativo v1.1 dejaron para E2: (a) el tratamiento de T5 en el análisis; (b) la disposición de split8_j5, j7 y j8 en el piloto; (c) la sección 6 de E1, que sigue SIN APROBAR.
**Qué no hace:** no modifica nada confirmatorio de T2-A0: X, r*, cola, Y, compuertas, criterios 1–6, A = 0.02, bootstrap. No reclasifica visitas ni asigna Y.

## 1. Hechos nuevos desde E1 v9

1. **Piloto de 20 visitas (update 25):**
   - 16 `INJECTIVE_AT_NOMINAL_RADIUS`. Incluye j8 por la reevaluación D4: `piloto/ensayo_t4p_j8/RESULTADO_ensayo_t4p_j8_2026-10-21.md`, con la pausa original conservada.
   - 2 `GEOMETRIC_NONINJECTIVITY` (split10_j17, split8_j9).
   - 2 sin clasificar (split8_j5, split8_j7).
   - Ningún Y asignado.
2. **Certificación de T5** (`piloto/certificacion_t5/`, protocolo v1 congelado, script v4, corrida 4 válida):
   - **split8_j5: T5 certificada.** El rayo 1776 sale por la arista 6/13 en r = 0.0744746462 y el área está acotada por U = 0.019426 ≤ 0.0195.
   - **split8_j7: no certificada.** U = 0.019744 > 0.0195.
   - Es una cota numérica con factores de seguridad declarados, **no aritmética de intervalos** (decisión D-T5-1).
   - Hubo **cuatro corridas**, con tres defectos de implementación corregidos tras ver resultados intermedios. Los números de j5 y j7 son idénticos desde la corrida 2.
3. **El escape es una propiedad del split.** El campo f de la familia es `Xpanel[:, :2]` (`core.make_geom_state`): las dos primeras coordenadas de los 27 puntos del panel de validación. Solo depende del split. M depende del modelo.
   - j5, j7 y j8 escapan por la **misma** arista de la envolvente convexa de f (componentes 6/13, transversal 20; det A y β_min idénticos).
   - Lo que varía con la inicialización es el radio: 0.07447, 0.07466 y 0.08747.
   - En split 8, 3 de 5 inicializaciones llegan a esa frontera, j9 tiene un conjugado y j6 está sana. En split 10, 1 de 5 tiene evento (j17).
   - Es descriptivo y viene de los mismos datos; ver la sección 7.

## 2. El problema central que E2 debe decidir [DECISIÓN + DICTAMEN]

Bajo T2-A0 (sección 5: «cualquier auditoría obligatoria faltante o fallida mantiene la compuerta técnica global INCONCLUSIVE»; sección 7, criterio 1), **una sola visita T5** en las 8000 basta para que el veredicto confirmatorio sea INCONCLUSIVE. Una visita T5 no tiene radio nominal y su auditoría no puede completarse.

El piloto muestra 1 visita certificada y 1 sospechosa entre 20, concentradas en un split. Con una tasa 50 veces menor (0.1 %), seguiría habiendo del orden de 8 visitas T5 entre 8000. La frecuencia real no está estimada (sección 1.8 de E1), pero **es previsible que T2-A0 termine INCONCLUSIVE por construcción**.

E1 eligió conscientemente mantener la compuerta (opción C) y rechazó cambiar la pregunta (opción B). E2 no puede deshacer eso retrospectivamente. Las alternativas legítimas son:

- **E2-C (mantener).** No se cambia nada confirmatorio. T2-A0 se reporta primero, previsiblemente INCONCLUSIVE. Las visitas T5 se reportan como incidencia (sección 7 de E1) y la sección 6 da la sensibilidad. Es lo más coherente con lo ya congelado, pero el piloto prospectivo probablemente no producirá un veredicto.
- **E2-A1 (análisis adicional prerregistrado antes de la producción).** Se define **antes de abrir cualquier visita de producción** un análisis T2-A1 separado. En él, T5 es un **desenlace en competencia** declarado. Ejemplo (por fijar con el dictamen):
  - Y′ = 1 si hay `GEOMETRIC_NONINJECTIVITY` en alguna visita;
  - Y′ = 0 si las visitas son `INJECTIVE` o T5 certificada;
  - el resto, no determinado.

  Variantes posibles: estimar la incidencia acumulada con T5 como evento en competencia, o analizar la incidencia de T5 como desenlace propio. T2-A0 se sigue reportando primero y sin cambios.

  **Riesgo:** T2-A1 se diseña después de ver el piloto. Propuesta para separarlo: declarar los **splits 8–11 (los del piloto) como conjunto de descubrimiento, excluidos del confirmatorio de T2-A1**, que usaría los splits 12–167. **[DICTAMEN]** sobre si esta separación basta y sobre la pérdida de potencia (156 de 160 splits).
- **E2-R (rediseño).** Si T5 resulta frecuente, la pregunta «¿predice X la no inyectividad futura?» queda mal planteada en esta familia sin tratar la frontera del dominio. Habría que abrir un preregistro nuevo, no una enmienda.

**Recomendación de la línea claude:** E2-A1 con la separación de splits, **solo si** el dictamen la acepta; si no, E2-C. En ambos casos se continúa la recopilación (E1, sección 7).

## 3. Tratamiento de T5 dentro de T2-A0 (sin cambios confirmatorios)

1. Una visita con diagnóstico T5, certificado o no, **no es** `INJECTIVE_AT_NOMINAL_RADIUS` ni `GEOMETRIC_NONINJECTIVITY`. Su disposición confirmatoria es INCONCLUSIVE (E1, sección 4). La trayectoria es Y_ND salvo que otra visita dé Y = 1. La compuerta global sigue INCONCLUSIVE.
2. **Relación con E1 §5.1 (corrección de definiciones, a decidir) [DECISIÓN]:**
   - (a) E1 §5.1(a) exige r₀ < R_nom. En una visita T5, R_nom **no existe** por definición. Propuesta: para T5, el requisito se lee como «A(r₀) < 0.02», que es lo que acota (b).
   - (b) E1 §5.1 exige «aritmética exacta o integración con error acotado; la coincidencia numérica entre precisiones no basta». **La certificación T5 de j5 no cumple ese estándar**: es numérica con factores declarados. Propuesta: **no relajar E1 §5.1 retrospectivamente**. Se registran dos niveles distintos:
     - «salida de dominio certificada (E1 §5.1)», que hoy nadie cumple;
     - «T5 certificado bajo el protocolo T5 v1 (numérico)», que cumple j5.
3. **Visitas de producción futuras.** Si la calibración v1.0 se pausa y T4′ tampoco alcanza A = 0.02, se aplica, como diagnóstico, el protocolo T5 v1 con el script v4 (hashes congelados). No hay versiones nuevas del script sin una enmienda.

   Un fallo del script en un caso nuevo se registra como «T5 no certificado». El script solo está validado en tres estados de un split; su robustez en otros splits es desconocida. **[DECISIÓN]:** si se acepta este uso, o si T5 se deja sin certificar en producción y solo se reporta como sospecha.

## 4. Disposición del piloto [DECISIÓN]

| visita | disposición original | evidencia nueva | propuesta |
|---|---|---|---|
| split8_j8 | PAUSED_PENDING_REVIEW | reevaluación D4: `INJECTIVE_AT_NOMINAL_RADIUS` (T4′, compuertas OK) | se registra como **visita clasificada (reevaluación D4)** junto a la pausa original, que se conserva |
| split8_j5 | PAUSED_PENDING_REVIEW | T5 certificada (protocolo T5 v1, numérico) | INCONCLUSIVE para T2-A0, con diagnóstico «T5 certificado (numérico)» |
| split8_j7 | PAUSED_PENDING_REVIEW | T5 no certificada (U = 0.019744) | INCONCLUSIVE para T2-A0, con diagnóstico «sospecha de salida de dominio, no certificada» |

**Compuerta operacional del piloto** (más de 5 de 20 sin resolver, o 5 de 5 en un split): con la propuesta quedan 2 de 20 sin resolver y 2 de 5 en split 8, así que **no se dispara**.

## 5. Sección 6 de E1 (identificación parcial): sigue SIN APROBAR

No se aplica a datos hasta el dictamen. Preguntas concretas para la revisión externa **[DICTAMEN]**:
1. ¿Es adecuado el intervalo percentil [Q₀.₀₂₅(L*), Q₀.₉₇₅(U*)] o hace falta un método tipo Imbens–Manski para cubrir el parámetro? ¿Bajo qué condiciones con bootstrap de splits completos?
2. Lift no definido cuando una asignación compatible da tasa base cero: ¿qué tratamiento? Hoy el intervalo del lift es «no evaluable».
3. Si n_ND es grande (sección 2), las cotas pueden no ser informativas. ¿Conviene reportarlas igualmente, o fijar antes un umbral de informatividad?
4. ¿Cambia algo que Y_ND esté concentrado por split (correlación intra-split del mecanismo de no determinación)?
5. Para E2-A1: ¿es válido el desenlace en competencia T5 y la separación de splits de descubrimiento? ¿Cuánto cuesta en potencia, frente a la sección 8 del preregistro?
6. ¿Cómo debe ponderarse el historial de cuatro corridas de la certificación T5 (sección 1.2)?

## 6. Integridad y orden de cierre
(1) dictamen externo y cambios derivados; (2) decisiones del responsable en las secciones 2, 3 y 4; (3) SHA-256 de este documento y manifiesto; (4) solo entonces, aplicación. Hasta entonces rigen E1 v9 y el anexo v1.1 tal cual.

## 7. Hipótesis exploratoria registrada (no confirmatoria, fuera de T2-A0)
**H-split:** la llegada de la exponencial a una frontera de la familia antes de A = 0.02 es una propiedad de la geometría del panel de validación del split (envolvente convexa de f = Xpanel[:, :2] y cercanía del punto transversal a la arista), modulada por M (la inicialización).
- Surgió de split 8 (los mismos datos), así que **no puede confirmarse con ellos**.
- Prueba propuesta: un protocolo propio, congelado **antes** de mirar f de otros splits, con un predictor geométrico de f fijado de antemano y una comparación con la incidencia de pausas o T5 en splits nuevos.
- No forma parte de esta enmienda ni puede usarse para seleccionar, excluir o reemplazar trayectorias de T2-A0.

## 8. Qué no se afirma
No se afirma la frecuencia de T5 en la cohorte. Tampoco que T5 sea un evento geométrico intrínseco de la red y no de la carta o la familia de perspectivas, ni que la certificación numérica equivalga a una cota rigurosa. Tampoco que H-split sea cierta, ni que E2-A1 tenga la potencia del diseño original.
