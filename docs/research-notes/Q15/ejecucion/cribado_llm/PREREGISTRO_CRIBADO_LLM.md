# Preregistro: piloto de cribado de Q15 con modelos abiertos

**Estado: BORRADOR, 2026-11-05, hora de México.** Se congela cuando el responsable lo apruebe y se confirme en git. Nada se etiqueta antes de eso. Autor: Claude. Decide: el responsable.

## Pregunta
¿Puede un modelo abierto, corriendo en una VM spot de Azure, hacer el cribado por título y resumen de Q15 con la calidad que ya aceptamos en los lotes auditados, sin excluir obras que debían incluirse?

Si la respuesta es sí, el modelo criba las 2 998 obras que siguen en `PENDIENTE_CRIBADO`, bajo las reglas de uso de abajo. Si es no, el cribado espera a Argon (su cuota vuelve el 2026-11-12).

## Referencia
- Son las decisiones finales auditadas de los lotes 01 (Codex), 02 (Argon, con las 6 correcciones de la opción B) y 03 (Argon), en sus paquetes sellados:
  - `Q15_C_LOTE01_D01_SemanticScholar_2026-11-05.zip`, SHA-256 `56a1bb737e583652cce1ba979b2e36045a039eb369f3cf905518641fbe057ad6`;
  - `Q15_C_LOTE02_2026-11-05.zip`, SHA-256 `8c6a9a1e1dd348885a68b262dda7ce303bac5c2a0324439610204229dcf559a8`;
  - `Q15_C_LOTE03_2026-11-05.zip`, SHA-256 `46354f8361951c13c868c422f210ed9ee174d8e2ee7a63f1fd77565ee3ef3cff`.
- Entran solo las obras con resumen y con decisión INCLUIR_PARA_TEXTO, CONTEXTO o EXCLUIR_FUERA_TEMA. W00126 (PENDIENTE_ACCESO) queda fuera. Se esperan 154 obras.
- **Limitación declarada:** la referencia la hicieron agentes de IA y la auditó Claude; no es una referencia humana. Mide si el modelo reproduce el criterio aceptado, no si acierta en un sentido absoluto. Además, la mayoría de las decisiones son de Argon, que es de Google: un modelo Gemma podría coincidir por parecido de familia. Esto se tendrá en cuenta al leer los resultados de C3, pero no cambia la regla.

## Partición
- Se agrupan las obras con el mismo título normalizado, para que un duplicado no quede en las dos mitades.
- Cada grupo se asigna a un estrato según la decisión más conservadora de sus miembros (INCLUIR antes que CONTEXTO, y CONTEXTO antes que EXCLUIR).
- Dentro de cada estrato, los grupos se barajan con la semilla `20261105` y se alternan entre la mitad de **selección** y la de **validación**.
- `preparar` escribe la referencia, las dos entradas sin etiquetas y `particion.json` con los conteos y los hashes. **`particion.json` se confirma en git antes de crear la VM.** A la VM solo viaja la entrada, nunca la referencia.

## Configuraciones
Mismo prompt, mismas opciones y misma salida para todas.

| ID | Modelo (etiqueta de Ollama) | Razonamiento |
|---|---|---|
| C1 | `qwen3.8:27b` | no (`think: false`) |
| C2 | `qwen3.8:27b` | sí (`think: true`) |
| C3 | `gemma4:31b` | por defecto del modelo |
| C4 | `gpt-oss:120b` | medio (`think: "medium"`) |

- **Prompt:** [`PROMPT_CRIBADO_LLM.md`](PROMPT_CRIBADO_LLM.md), SHA-256 `0d102764a522b0d09cbfd60fbc0d1fff375a99c40d254b52dafa9592a9d593f0`. Contiene, copiados sin cambios, la sección 1 (preguntas y diccionario) y la sección 6 (elegibilidad) del protocolo, y los dos criterios del responsable. No contiene ejemplos de la referencia.
- **Entrada por obra:** título y todos los resúmenes distintos de sus posiciones elegibles.
- **Opciones:** temperatura 0, semilla 0, contexto de 32 768 tokens y hasta 8 192 tokens de salida.
- **Salida:** JSON con esquema obligatorio: `decision` (una de las tres), `puntos`, `razon` y `dudoso`. Una respuesta que no cumpla el esquema queda como **INVALIDA**; nunca se interpreta ni se adivina.
- **Entorno:** `Standard_NC24ads_A100_v4` spot (una A100 de 80 GB), con la versión de Ollama de la PC del responsable. Tope de 1 USD/h y apagado automático a las 6 h. Después de `instalar` y antes de `lanzar`, se registran en el PR la versión de Ollama y el ID y la cuantización de cada modelo, tal como los imprimen `ollama list` y `ollama show`.

## Elección (solo en la mitad de selección)
Se etiquetan las 4 configuraciones en la mitad de selección. `elegir` aplica esta regla, en orden:
1. mayor **sensibilidad**: fracción de obras INCLUIR de la referencia que el modelo no excluye (INCLUIR, CONTEXTO o INVALIDA cuentan como no excluidas);
2. mayor **acuerdo exacto** en las tres clases;
3. menos respuestas inválidas;
4. menor mediana de segundos por obra.

## Validación (solo la configuración elegida, en la otra mitad)
Se etiqueta la mitad de validación solo con la configuración elegida. `validar` aplica tres compuertas:

| Compuerta | Pasa si |
|---|---|
| Omisiones | **0** obras INCLUIR de la referencia excluidas por el modelo |
| Acuerdo | acuerdo exacto en tres clases **≥ 0.85** |
| Inválidas | **≤ 2 %** de respuestas inválidas |

- **APTO** si pasan las tres. **NO APTO** si falla alguna. **INCONCLUSIVO** si la corrida no se completa (por ejemplo, por desalojos que agoten el tope de horas).
- Con unas 25 obras INCLUIR en la validación, cero omisiones no prueba que la tasa real de omisión sea cero. Con la regla de tres, solo la acota por debajo de aproximadamente 12 % con 95 % de confianza. Por eso el uso en producción lleva la auditoría de abajo.
- Si el resultado es NO APTO o INCONCLUSIVO, no se cambian el prompt, las configuraciones ni los umbrales para repetir el piloto con estos mismos datos. Un intento nuevo necesitaría una enmienda y una referencia nueva.

## Uso si sale APTO
- El modelo criba las 2 998 obras pendientes en lotes de 500, con la configuración elegida y el mismo prompt.
- La entrada de producción se construye desde `D:\RIPG_DATA\Q15_v31_1_ENTREGA_B.zip` con las mismas reglas que la del piloto. El extractor se escribe y se verifica, contra la estructura del zip y contra los resúmenes de los lotes 02 y 03, antes de etiquetar producción.
- **Reglas de producción:**
  - INCLUIR_PARA_TEXTO y CONTEXTO quedan con esa decisión.
  - EXCLUIR_FUERA_TEMA con `dudoso: false` queda excluida.
  - EXCLUIR_FUERA_TEMA con `dudoso: true`, e INVALIDA, pasan a una cola de revisión para Argon.
  - Las obras sin resumen siguen la regla del protocolo: PENDIENTE_ACCESO, sin pasar por el modelo.
- **Auditoría:** en cada lote de 500, Claude lee todas las inclusiones de frontera y una muestra al azar de 50 exclusiones, con semilla fija. Si en la muestra aparecen **2 o más** exclusiones de obras que debían incluirse, se suspende el uso del modelo y lo que falte vuelve a la cola de Argon.
- El revisor se registra como "modelo abierto `<etiqueta>` (ID `<id>`), lector IA único, sin cribado doble". Ninguna decisión del modelo se presenta como lectura humana ni de Argon.

## Lo que no hace este piloto
- No adjudica novedad ni cambia ningún estado de Q15.
- No reabre las 410 exclusiones de B ni la adenda: siguen pendientes para la consolidación final.

## Archivos y comandos
- [`cribado_llm.py`](cribado_llm.py), SHA-256 `df67608a50973edaac1b1d0ab5e32a2047cd888f19360cc02bb0c72afd07da31`, con los subcomandos `preparar`, `etiquetar`, `verificar`, `elegir` y `validar`. Se probó con datos sintéticos y `--simular`.
- [`cribado_llm_azure.ps1`](cribado_llm_azure.ps1), SHA-256 `b84f7d4a28d8e22cb1d8df1b513039c9984bb12d0529368588233eabafce8225`, adaptado del E001 de `experimentos-aislados`.
- Los datos viven en `D:\RIPG_DATA\Q15_CRIBADO_LLM\`, fuera de Git. Al repo solo entran `particion.json`, `eleccion.json`, `veredicto.json` y los hashes.

## Historial
- 2026-11-05: borrador.
