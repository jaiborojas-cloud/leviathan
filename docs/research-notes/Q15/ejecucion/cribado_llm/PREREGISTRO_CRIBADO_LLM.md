# Preregistro: piloto de cribado de Q15 con modelos abiertos

**Estado: CONGELADO, 2026-11-06, hora de México, con la enmienda 1 (ver el historial).** Aprobado por el responsable. Lo que se cambie desde aquí va como enmienda, antes de usarse. Autor: Claude. Decide: el responsable.

## Pregunta
¿Puede un modelo abierto, corriendo en una VM spot de Azure, hacer el cribado por título y resumen de Q15 con la calidad que ya aceptamos en los lotes auditados, sin excluir obras que debían incluirse?

Si la respuesta es sí, el modelo criba las 2 998 obras que siguen en `PENDIENTE_CRIBADO`, bajo las reglas de uso de abajo. Si es no, el cribado espera a Argon (su cuota vuelve el 2026-11-12).

## Referencia
- Son las decisiones finales auditadas de los lotes 01 (Codex), 02 (Argon, con las 6 correcciones de la opción B) y 03 (Argon), en sus paquetes sellados:
  - `Q15_C_LOTE01_D01_SemanticScholar_2026-11-05.zip`, SHA-256 `56a1bb737e583652cce1ba979b2e36045a039eb369f3cf905518641fbe057ad6`;
  - `Q15_C_LOTE02_2026-11-05.zip`, SHA-256 `8c6a9a1e1dd348885a68b262dda7ce303bac5c2a0324439610204229dcf559a8`;
  - `Q15_C_LOTE03_2026-11-05.zip`, SHA-256 `46354f8361951c13c868c422f210ed9ee174d8e2ee7a63f1fd77565ee3ef3cff`.
- Entran solo las obras con resumen y con decisión INCLUIR_PARA_TEXTO, CONTEXTO o EXCLUIR_FUERA_TEMA. W00126 (PENDIENTE_ACCESO) queda fuera. Son **154 obras**.
- CONTEXTO tiene solo 6 obras en total (3 por mitad). El acuerdo en esa clase pesa poco y no se analiza por separado.
- **Limitación declarada:** la referencia la hicieron agentes de IA y la auditó Claude; no es una referencia humana. Mide si el modelo reproduce el criterio aceptado, no si acierta en un sentido absoluto. Además, la mayoría de las decisiones son de Argon, que es de Google: un modelo Gemma podría coincidir por parecido de familia. Esto se tendrá en cuenta al leer los resultados de C3, pero no cambia la regla.

## Partición
- Se agrupan las obras con el mismo título normalizado, para que un duplicado no quede en las dos mitades.
- Cada grupo se asigna a un estrato según la decisión más conservadora de sus miembros (INCLUIR antes que CONTEXTO, y CONTEXTO antes que EXCLUIR).
- Dentro de cada estrato, los grupos se barajan con la semilla `20261105` y se alternan entre la mitad de **selección** y la de **validación**.
- `preparar` escribe la referencia, las dos entradas sin etiquetas y `particion.json` con los conteos y los hashes. A la VM solo viaja la entrada, nunca la referencia.
- **Partición congelada:** [`particion.json`](particion.json), SHA-256 `2598b7dc6a03026d55e0e7b45b4644035132ea50bb857d62920d512052fddc20`. Claude la generó el 2026-11-06 en una carpeta temporal de la PC del responsable, a partir de los tres paquetes sellados. Es determinista: la corrida oficial del responsable debe reproducir los mismos hashes; si no, se detiene todo.

| mitad | INCLUIR_PARA_TEXTO | CONTEXTO | EXCLUIR_FUERA_TEMA | total |
|---|---:|---:|---:|---:|
| selección | 25 | 3 | 51 | 79 |
| validación | 24 | 3 | 48 | 75 |

- Los cuatro grupos de título duplicado quedaron enteros en una sola mitad: TG000 (W00098 y W00135) en validación; TG001, TG002 y TG006 en selección.

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
- **Opciones:** temperatura 0, semilla 0, contexto de 32 768 tokens y hasta 16 384 tokens de salida, incluido el razonamiento. Cada respuesta registra `done_reason`, para distinguir una respuesta truncada de una mal formada.
- **Salida:** JSON con esquema obligatorio: `decision` (una de las tres), `puntos`, `razon` y `dudoso`. Una respuesta que no cumpla el esquema queda como **INVALIDA**; nunca se interpreta ni se adivina.
- **Prueba de formato:** antes de etiquetar, `probar` manda a cada configuración una obra inventada (no pertenece a la referencia ni al corpus) y registra en `probar.json` cuáles responden con el esquema. Esta prueba no ve datos de la referencia.
  - Si una configuración falla, se puede corregir **la instalación** (versión de Ollama, descarga del modelo) y repetir `probar`; el prompt, las opciones y las configuraciones no se tocan. Cuenta la última corrida de `probar` antes de `lanzar`.
  - Las configuraciones que no pasen quedan **NO_EVALUADAS**: no se etiquetan ni compiten, y se reportan como tales. Si ninguna pasa, el piloto es NO APTO.
- **Errores al llamar al modelo:** se reintenta 3 veces. Si Ollama responde con un error, o tarda más de 30 minutos, la obra queda INVALIDA con el error registrado. Si no hay conexión con Ollama (una falla de infraestructura), el proceso se detiene sin registrar nada y se reanuda con `lanzar`; esa falla no se cuenta contra el modelo.
- **Entorno:** `Standard_NC24ads_A100_v4` spot (una A100 de 80 GB), con la versión de Ollama de la PC del responsable. Tope de 1 USD/h y apagado automático a las 6 h. Después de `instalar` y antes de `lanzar`, se registran en el PR la versión de Ollama y el ID y la cuantización de cada modelo, tal como los imprimen `ollama list` y `ollama show`.

## Elección (solo en la mitad de selección)
Se etiquetan en la mitad de selección todas las configuraciones que pasaron `probar`. Solo compiten las configuraciones con **2 % o menos** de respuestas inválidas; así, un modelo que falla el formato no puede ganar por "sensibilidad". Si ninguna cumple, el piloto es NO APTO. Entre las que compiten, `elegir` aplica esta regla, en orden:
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
- Con 24 obras INCLUIR en la validación, cero omisiones no prueba que la tasa real de omisión sea cero. Con la regla de tres, solo la acota por debajo de aproximadamente 12.5 % con 95 % de confianza. Por eso el uso en producción lleva la auditoría de abajo.
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
- [`cribado_llm.py`](cribado_llm.py), SHA-256 `a7d9a718af41966587cdd04944d5b5fa0e751c1eb3a53bf7833c66edd047fb40`, con los subcomandos `preparar`, `probar`, `etiquetar`, `verificar`, `elegir` y `validar`. Se probó de punta a punta con datos sintéticos y `--simular`, incluidos una configuración con todas sus respuestas inválidas, una línea cortada por desalojo, una configuración que no pasa `probar`, un error HTTP del modelo y una caída de Ollama. `preparar` se probó además con los tres paquetes reales, con las dos versiones del script, y reproduce la partición congelada.
- [`cribado_llm_azure.ps1`](cribado_llm_azure.ps1), SHA-256 `38dbb19616089d3af0e0ebe0f77469c21d7bff2d2104f2ceef6cc4001009c30f`, adaptado del E001 de `experimentos-aislados`. Lleva escritos los SHA-256 congelados del script y del prompt, y lee de `particion.json` los de las entradas: **no sube nada a la VM si alguno no coincide**. En selección etiqueta solo las configuraciones de `probar.json`; en validación, solo la de `eleccion.json`, y se niega a correr si no hay elegida. Se revisó su sintaxis con PowerShell 7.4 y se probaron estas rutas con `az`, `ssh` y `scp` simulados; no se ha ejecutado contra Azure.
- Los datos viven en `D:\RIPG_DATA\Q15_CRIBADO_LLM\`, fuera de Git. Al repo solo entran `particion.json`, `eleccion.json`, `veredicto.json` y los hashes.

## Historial
- 2026-11-05: borrador (`a4d6d9c9`).
- 2026-11-06: revisión de Claude antes de congelar (`7f342bcb`). Cambios:
  - las escrituras usan LF, para que los hashes coincidan en Windows y Linux;
  - una línea cortada por un desalojo ya no se pega a la respuesta siguiente;
  - solo compiten en la elección las configuraciones con 2 % o menos de inválidas;
  - el límite de salida sube de 8 192 a 16 384 tokens, y se registra `done_reason`;
  - se agregó la prueba de formato `probar`, con una obra inventada.
- 2026-11-06: congelado por aprobación del responsable (`747f348e`), con la partición generada a partir de los paquetes reales.
- 2026-11-06, **enmienda 1**, segunda revisión de Claude a petición del responsable, **antes de cualquier ejecución** (no se había creado la VM ni etiquetado nada). No cambia el prompt, las configuraciones, las opciones, la partición, la regla de elección ni las compuertas. Cambios:
  - errores al llamar al modelo: un error del modelo queda INVALIDA tras 3 intentos; una caída de Ollama detiene el proceso para reanudarlo, en vez de contarse contra el modelo;
  - una configuración que no pase `probar` queda NO_EVALUADA y no compite, en lugar de detener todo el piloto;
  - el script de Azure verifica los SHA-256 congelados antes de subir nada y toma las configuraciones de `probar.json` y de `eleccion.json`, en vez de una lista escrita a mano;
  - `bajar` copia solo las salidas de la mitad indicada.
