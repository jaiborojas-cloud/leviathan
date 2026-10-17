# Leviathan / RIPG — cierre documental v1 de split8_j5_true/update25

Fecha: 2026-10-16. Incidente: `T2A-split8_j5_true-update25-domain-v1`.

**Cierre documental completado; problema científico abierto, pendiente/INCONCLUSIVE.** No se asigna clasificación topológica ni outcome. La visita no se cuenta como completa; la trayectoria permanece en la cohorte y conserva su predictor basal sellado. El cierre no constituye una enmienda del prerregistro ni una decisión estadística final del ensayo.

## Reconciliación del estado

Se leyeron las versiones vigentes de progress.md, roadmap, protocol.json, prerregistro, cohort_manifest.csv, task_log.csv, manifest.csv, visits.csv y outcomes.csv. Se verificaron sus bytes disponibles contra manifest.csv; los antecedentes quedan conservados en el paquete documental v1.

- Cohorte: 800 trayectorias Wine true, splits 8–167, cinco inicializaciones por split; update5 basal, visitas 25,50,…,250. Las 800 filas basales son BASELINE_EVALUATED/PASS; el sello conserva 800 elegibles en 160 splits.
- Visitas cerradas: **1/8000**, split8_j6_true/update25, INJECTIVE_AT_NOMINAL_RADIUS. Horizontes completos: **0/800**. Los 800 valores Y siguen vacíos; no son ceros.
- j5/update25: integración float64 histórica en paso512, sin modificación. Replay MPFR separado del PC en paso139, r=0.07447265825972331, PAUSED. Siguiente paso contable140, **no autorizado para continuación ciega hacia .09**.
- j7/update25 y j8/update25 conservan parciales. No se ha abierto ni calculado ninguna visita en esta sesión.
- cohort_manifest.csv conserva campos operativos basales TRAINED_BASELINE_ONLY/NOT_OPENED incluso para las primeras visitas: es una limitación del registro heredado. Para el seguimiento actual mandan visits.csv, outcomes.csv, los índices de parciales y este registro de incidencias. No se reescribe el manifiesto basal sellado para ocultar esa discrepancia.

## Criterios congelados aplicados

Fuentes exactas: protocol.json, SHA256 `7ce3ec683a392ec3de0a5e8a983ea112684912026d427a5cd4f98fb7003d1f95`; Leviathan_RIPG_T2-A0_preregistro.md, SHA256 `36b41002ef0cbd177bee9712181ad45e46cefdf2087b4e918a1e33fa49677f72`.

1. `protocol.json:event.positive`, `event.Y1`, `event.Y0`, `event.unresolved`; prerregistro §5: Y=1 requiere al menos una visita futura con GEOMETRIC_NONINJECTIVITY confirmada por la jerarquía heredada; Y=0 requiere las diez visitas INJECTIVE_AT_NOMINAL_RADIUS. En otro caso Y es desconocido. Un positivo posterior puede resolver Y=1, pero no elimina una auditoría obligatoria faltante o fallida.
2. `eligibility.numerical_failure`, `eligibility.no_event_early_termination`; §5: los fallos futuros no son exclusiones estructurales basales. NUMERICAL_FAILURE e INCONCLUSIVE no son ceros; interrupción sin evento tampoco es negativo. No hay confirmación sobre supervivientes numéricos.
3. `primary_statistics.success[0]` y `primary_statistics.INCONCLUSIVE`; §7: auditorías requeridas incompletas o fallidas bloquean el PASS técnico. Esta incidencia mantiene la compuerta técnica INCONCLUSIVE mientras no se resuelva; no se ejecuta ahora la evaluación primaria.
4. §5: positivo exige evidencia geométrica estable bajo refinamiento y SPD válido, con la jerarquía T1-A/C1-A2; discordancia sigue INCONCLUSIVE. El área nominal sigue A=.02. §10: recuperar estados válidos, conservar parciales e historial, verificar hashes y no sustituir corridas.

## Tres cuestiones distintas

| Cuestión | Evidencia disponible | Estado que se registra |
|---|---|---|
| Dominio de la familia softmax | Certificado algebraico para M,f almacenados: SPD racional, ocho aristas y borde accesible ausente de P finitos. Evidencia numérica fuerte de terminación antes del objetivo. | Existencia/no existencia de D_0.02 todavía no certificada; posible fallo de dominio documentado. |
| Incertidumbre instrumental | Deterioro de la carta original, replay y controles de precisión; faltan cotas globales de integración, cobertura angular continua y área. | Auditoría nominal no resuelta, INCONCLUSIVE documental/técnico. No se promueve el diagnóstico a instrumento de producción. |
| GEOMETRIC_NONINJECTIVITY | No hay en este caso confirmación completa conforme a la jerarquía congelada. | Clasificación topológica desconocida; no positivo ni negativo. |

Una frontera de dominio no implica conjugado, cut locus ni autointersección. La regularidad de una carta límite no autoriza añadir puntos de frontera ni ampliar el espacio softmax.

Mínimo **local** numérico: r≈.07447421006513, índice angular≈1775.39798, entre rayos1775/1776. No es mínimo global certificado. Los controles desde origen difieren ~1e-12; coincidencias locales130/139 de ~1e-14 no son cotas globales. Área diagnóstica muestreada≈.01871467<.02: no A_embed, no radio nominal y no certificado de existencia/no existencia del disco. Parte de ese diagnóstico llega a un radio ligeramente posterior al nuevo candidato local: no debe presentarse como disco completo validado.

## Decisión de registro y compatibilidad

Se crea `incident_register.csv` como registro administrativo separado, con documento y JSON versionados. Estado de la incidencia: INCONCLUSIVE; estado científico: no resuelto; Y, clasificación topológica, radio nominal y A_embed permanecen nulos en el JSON y vacíos donde corresponde en CSV. `documentary_closed=true` describe únicamente la documentación; `visit_complete=false` describe la ausencia de finalización, no la ausencia de evento.

**visits.csv y outcomes.csv permanecen byte a byte intactos.** El agregador heredado run_followup.py sólo recoge visit_complete.json; `unknown_visits` cuenta clasificaciones desconocidas de esos marcadores, no todos los pendientes. Por eso el cero heredado de j5 en unknown_visits no demuestra ausencia de incertidumbre: hay una incidencia abierta en el registro separado. Fabricar visit_complete.json para este cierre inflaría visitas completas. Se conserva PENDING y Y vacío en outcomes.csv.

El próximo ejecutor debe leer ambos registros: una incidencia abierta bloquea la compuerta técnica aunque el agregador heredado no la cuente. No ejecutar el lanzador genérico sin tratar explícitamente la pausa: volvería a seleccionar j5 por ausencia de marcador. No se modifica código científico ni se falsifica un marcador para saltarlo.

## Recuperación exacta y alcance de hashes

Ver `incident_split8_j5_update25_v1_verification.json` y `incident_split8_j5_update25_v1.json` para hashes completos y rutas. Se verifican 21 entradas materializadas del manifiesto vigente, los seis archivos del sello basal, CRC de cuatro ZIP, 17 hashes del retorno PC, CRC de sus 13 segmentos contiguos91–139 y los 31 hashes internos de los tres diagnósticos. El paquete frontera139 no tenía entrada en el manifiesto raíz vigente: se añade su hash observado, sin afirmar una comparación externa previa inexistente.

- Retorno `/RIPG_RESULTADOS_PC.zip`: `f082f89bd76f94e5bd8060021939008363228aabd0f377d0cd4cfa6eb1ca555b`.
- Base `origin_mpfr_step_000090.zip`: referencia `de0f854646e9da24402b7adf5ce5ad055cea48230008d622bc0097d44244a987`. Para recuperar el replay se necesita esta base y los 13 segmentos del retorno; el índice PC es la autoridad para139. No restaurar el índice90 como si fuera el avance actual.
- Float64 histórico: conservar snapshot512 y ode_resume_index.json por separado; no sustituirlo por MPFR.

No se descargó Windows_CP90 ni se deserializaron estados numéricos. Los bytes de base90 y snapshot512 no se verificaron de nuevo: sus referencias se concilian con índices persistentes. Los 800 ZIP basales tampoco se redescargaron: se conserva la auditoría completa previa y se verifica ahora el sello. Este alcance se declara para no confundir integridad documental con repetición de auditorías científicas.

## Plan concreto de continuación, sin ejecución en esta sesión

El orden operacional heredado recorre primero update25 y dentro de cada update el orden de cohorte (run_followup.py:main y followup_bounded_verified.py:main). **La primera pendiente absoluta sigue siendo split8_j5_true/update25, retenida por esta incidencia. La siguiente tarea ejecutable de cohorte es split8_j7_true/update25**, después j8/update25 y j9/update25. J6 ya está cerrada y no se repite. Esta retención no excluye j5 de la cohorte ni altera su Y.

1. Recuperar el cierre v1, verificar hashes del protocolo/sello y consultar incident_register.csv antes de elegir tareas. Mantener j5 en pausa; no ejecutar paso140.
2. Recuperar `partial_t025_split8_j7_true_checkpoint_snapshot.zip`, verificar su SHA y los hashes de checkpoint.pt/state.npz indicados en el JSON de continuidad. Restaurar modelo, Adam, RNG y campo existentes; no reentrenar. Si hay un avance geométrico persistente adicional, verificarlo y partir del último válido, nunca inventar un paso.
3. Preparar selección explícita de j7/update25 que respete la retención de j5 y omita j6. Mantener A=.02, rayos, semillas, tolerancias, jerarquía y evento originales. Un nuevo fallo se documenta como desconocido, sin rescate retrospectivo.
4. Guardar cada resultado/pausa antes de seguir; cerrar una visita sólo tras las compuertas y paquete verificado. Actualizar los contadores con sus significados existentes y comprobar que no desaparezcan las incidencias abiertas al agregar.
5. Seguir j8 y j9 en el orden heredado; no avanzar por ranking de predictor. No calcular la evaluación primaria mientras falten auditorías obligatorias. El avance descriptivo no resuelve el bloqueo confirmatorio.

La certificación rigurosa del borde y la revisión de dominios históricos son líneas separadas. C1-A sigue INCONCLUSIVE. T1 permanece descubrimiento/control esperado; sus mismos80 estados no validan nuevas hipótesis. Las pruebas locales con copias de los800 basales son exploratorias y no modifican sellos ni prerregistro; nuevas hipótesis requieren diseño prospectivo independiente.
