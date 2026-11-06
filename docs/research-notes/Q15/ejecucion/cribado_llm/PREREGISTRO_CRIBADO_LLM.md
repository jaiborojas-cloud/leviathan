# Preregistro: piloto de cribado de Q15 con modelos abiertos

**Estado: CONGELADO, 2026-11-06, hora de México, con las enmiendas 1 a 4 (ver el historial). La enmienda 4 está pendiente de la revisión de Codex; no se ejecuta nada antes.** Aprobado por el responsable. Lo que se cambie desde aquí va como enmienda, antes de usarse. Autor: Claude. Decide: el responsable.

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

- **Prompt:** [`PROMPT_CRIBADO_LLM.md`](PROMPT_CRIBADO_LLM.md), SHA-256 del archivo `0d102764a522b0d09cbfd60fbc0d1fff375a99c40d254b52dafa9592a9d593f0`. El mensaje de sistema es el texto entre las líneas que son exactamente `<<<INICIO>>>` y `<<<FIN>>>` (una de cada una): **8 954 caracteres, SHA-256 `4659f18ddde2d7634ffc2aa4ec0db857c955d1176993f5b5dacb97307cd42727`**. El script se niega a correr si el texto efectivo no tiene ese hash, y cada fila de salida lo registra. Contiene, copiados sin cambios, la sección 1 (preguntas y diccionario) y la sección 6 (elegibilidad) del protocolo, y los dos criterios del responsable. No contiene ejemplos de la referencia.
- **Entrada por obra:** título y todos los resúmenes distintos de sus posiciones elegibles. Un resumen cuenta si tiene al menos un carácter alfanumérico, letra o dígito; el guion bajo no cuenta (por ejemplo, el resumen `","` de W00126 no cuenta). La evidencia debe ser una lista de `{obra_id, record: {title, abstract}}`; otra estructura detiene `preparar`.
- **Opciones:** temperatura 0, semilla 0, contexto de 32 768 tokens y hasta 16 384 tokens de salida, incluido el razonamiento. Cada respuesta registra `done_reason`, para distinguir una respuesta truncada de una mal formada.
- **Salida:** JSON con esquema obligatorio: `decision` (una de las tres), `puntos` (lista de puntos válidos), `razon` (no vacía) y `dudoso` (booleano), sin otras claves. El esquema enviado a Ollama prohíbe claves extra (`additionalProperties: false`), y el script valida todo por su cuenta. Una respuesta que no cumpla, o que venga de un modelo distinto del pedido, queda como **INVALIDA**; nunca se interpreta ni se adivina.
- **Prueba de formato:** antes de etiquetar, `probar` manda a cada configuración una obra inventada (no pertenece a la referencia ni al corpus) y registra en `probar.json` cuáles responden con el esquema. Esta prueba no ve datos de la referencia.
  - Si una configuración falla, se puede corregir **la instalación** (versión de Ollama, descarga del modelo) y repetir `probar`; el prompt, las opciones y las configuraciones no se tocan. Cuenta la última corrida de `probar` antes de `lanzar`.
  - Las configuraciones que no pasen quedan **NO_EVALUADAS**: no se etiquetan ni compiten, y se reportan como tales. Si ninguna pasa, el piloto es NO APTO.
- **Errores al llamar al modelo:** 3 intentos en total por obra. Si Ollama responde con un error HTTP, con un cuerpo que no es JSON, o tarda más de 30 minutos, la obra queda INVALIDA con el error registrado. Si no hay conexión con Ollama (una falla de infraestructura), el proceso se detiene sin registrar nada y se reanuda con `lanzar`; esa falla no se cuenta contra el modelo.
- **Integridad de las salidas:** cada fila lleva su firma: configuración, modelo pedido, `think`, opciones, hash del mensaje de sistema, hash del script, hash de la entrada, `simulado` y hora UTC. Para reanudar, todas las filas existentes deben tener la firma de la corrida; si no, se detiene. `elegir` y `validar` exigen, con comparación estricta de tipos: la firma oficial (entrada congelada, `simulado: false` y **el hash del script congelado**, el mismo que evalúa); que `referencia.jsonl` tenga el hash congelado; que cada fila sea coherente con su respuesta cruda (la decisión, los puntos, la razón y `dudoso` tabulados deben salir de `crudo`, y `modelo_respuesta` debe ser el modelo pedido; si no, la fila solo puede decir INVALIDA); que no haya obras repetidas ni ajenas a la mitad; que la hora de cada fila sea una fecha UTC real dentro del presupuesto (entre su inicio y su límite); y que `segundos` sea un número finito y no negativo, medido con reloj monotónico. Si algo falla, el resultado es INCONCLUSIVO. Las salidas se leen en bytes; una línea que no decodifica o no es JSON válido (por ejemplo, la cola cortada por un desalojo, o un `NaN`) no se usa, pero queda **registrada** con su número, hash y motivo en `lineas_descartadas` del estado, y su obra se rehace al reanudar. `--prueba` existe solo para las pruebas sintéticas y marca el resultado como no oficial.
- **Estados:** `elegir` y `validar` siempre escriben su estado vigente (`eleccion.json`, `veredicto.json`), también cuando terminan en INCONCLUSIVO por **cualquier** excepción (por ejemplo, un JSON roto), con el motivo. Cada intento deja además una copia con fecha e identificador único, escrita en modo exclusivo, y el estado vigente se reemplaza de forma atómica. Un veredicto anterior nunca queda como vigente.
- **Presupuesto de tiempo:** **24 horas de reloj desde el primer `lanzar`** (decisión del responsable, 2026-11-06). El primer `lanzar` escribe `presupuesto.json`, que debe declarar fechas UTC reales con exactamente 24 h entre inicio y límite; si no, `elegir` y `validar` dan INCONCLUSIVO. El límite viaja a la VM como hora **absoluta** en un `correr.sh` generado: el tiempo restante se calcula en la VM al arrancar, `timeout` corta en el límite y `etiquetar --hasta` (que solo acepta una fecha UTC válida) no empieza obras después de él. Si quedan 60 s o menos, no arranca. `correr.sh` termina con el código de salida del etiquetado, además de registrarlo. Lo que no esté etiquetado al llegar al límite deja el piloto INCONCLUSIVO. Costo máximo aproximado: 24 USD con el tope de 1 USD/h. Además, Azure apaga la VM una vez al día como medida de seguridad; esa hora no es el presupuesto.
- **Entorno:** `Standard_NC24ads_A100_v4` spot (una A100 de 80 GB), con la versión de Ollama de la PC del responsable. Tope de 1 USD/h. Después de `instalar` y antes de `lanzar`, se registran en el PR la versión de Ollama y el ID y la cuantización de cada modelo, tal como los imprimen `ollama list` y `ollama show`.

## Elección (solo en la mitad de selección)
Se etiquetan en la mitad de selección todas las configuraciones que pasaron `probar`. Solo compiten las configuraciones con **2 % o menos** de respuestas inválidas; así, un modelo que falla el formato no puede ganar por "sensibilidad". Si ninguna cumple, el piloto es NO APTO. Entre las que compiten, `elegir` aplica esta regla, en orden:
1. mayor **sensibilidad**: fracción de obras **protegidas** de la referencia (INCLUIR_PARA_TEXTO o CONTEXTO) que el modelo no excluye;
2. mayor **acuerdo exacto** en las tres clases;
3. menos respuestas inválidas;
4. menor mediana de segundos por obra;
5. si aún hay empate, el número de configuración menor (C1 antes que C2, etc.).

## Validación (solo la configuración elegida, en la otra mitad)
Se etiqueta la mitad de validación solo con la configuración elegida. `validar` aplica tres compuertas:

| Compuerta | Pasa si |
|---|---|
| Omisiones | **0** obras protegidas de la referencia (INCLUIR_PARA_TEXTO o CONTEXTO) excluidas por el modelo |
| Acuerdo | acuerdo exacto en tres clases **≥ 0.85** |
| Inválidas | **≤ 2 %** de respuestas inválidas |

- **APTO** si pasan las tres. **NO APTO** si falla alguna. **INCONCLUSIVO** si la corrida no se completa dentro del presupuesto de tiempo o si alguna verificación de integridad falla.
- **CONTEXTO protegida** (decisión del responsable, 2026-11-06, a partir del hallazgo D1 de Codex): excluir una obra CONTEXTO cuenta como omisión igual que excluir una INCLUIR. Sin esto, un modelo podía excluir las 3 CONTEXTO de la validación y salir APTO.
- **Límite de potencia:** hay 27 obras protegidas en la validación (24 INCLUIR y 3 CONTEXTO). Cero omisiones no prueba que la tasa real sea cero; con la regla de tres solo la acota por debajo de aproximadamente 11 % con 95 % de confianza. Con una tasa real de 10 %, la probabilidad de ver cero omisiones en 27 es de 0.9^27 ≈ 0.06. Por eso el uso en producción lleva la auditoría de abajo.
- **Límite de representatividad (D2):** la referencia son los primeros 155 `obra_id` en orden, no una muestra aleatoria de las 2 998 pendientes. Una familia temática que solo aparezca en obras posteriores no queda probada por el piloto. La auditoría de producción es la defensa contra eso.
- Si el resultado es NO APTO o INCONCLUSIVO, no se cambian el prompt, las configuraciones ni los umbrales para repetir el piloto con estos mismos datos. Un intento nuevo necesitaría una enmienda y una referencia nueva.

## Uso si sale APTO
- El modelo criba las 2 998 obras pendientes en lotes de 500, con la configuración elegida y el mismo prompt.
- La entrada de producción se construye desde `D:\RIPG_DATA\Q15_v31_1_ENTREGA_B.zip` con las mismas reglas que la del piloto. El extractor se escribe y se verifica, contra la estructura del zip y contra los resúmenes de los lotes 02 y 03, antes de etiquetar producción.
- **Reglas de producción:**
  - INCLUIR_PARA_TEXTO y CONTEXTO quedan con esa decisión.
  - EXCLUIR_FUERA_TEMA con `dudoso: false` queda excluida.
  - EXCLUIR_FUERA_TEMA con `dudoso: true`, e INVALIDA, pasan a una cola de revisión para Argon.
  - Las obras sin resumen siguen la regla del protocolo: PENDIENTE_ACCESO, sin pasar por el modelo.
- **Auditoría** (endurecida por decisión del responsable, 2026-11-06, a partir del hallazgo D3 de Codex): en cada lote de 500, Claude lee todas las inclusiones de frontera y una **muestra al azar de 100 exclusiones**, con semilla fija. El marco es la lista de exclusiones del lote ordenada por `obra_id`, y la muestra se toma con `random.Random(20261106 + número de lote).sample`; si el lote tiene 100 exclusiones o menos, se revisan todas (censo). **Una sola** exclusión de una obra que debía quedar protegida suspende el uso del modelo, y lo que falte vuelve a la cola de Argon. Con una tasa real de 5 % de exclusiones erróneas, la probabilidad de no detectarlo en un lote es de 0.95^100 ≈ 0.006.
- El revisor se registra como "modelo abierto `<etiqueta>` (ID `<id>`), lector IA único, sin cribado doble". Ninguna decisión del modelo se presenta como lectura humana ni de Argon.

## Lo que no hace este piloto
- No adjudica novedad ni cambia ningún estado de Q15.
- No reabre las 410 exclusiones de B ni la adenda: siguen pendientes para la consolidación final.

## Archivos y comandos
- [`cribado_llm.py`](cribado_llm.py), SHA-256 `d9288eaba8fcc94aa34cb07eb489cbf804cec0dc0ca4a0445720405bf8d29475`, con los subcomandos `preparar`, `probar`, `etiquetar`, `verificar`, `elegir` y `validar`. `preparar` se probó con los tres paquetes reales y reproduce la partición congelada; en la PC del responsable el mensaje de sistema efectivo mide 8 954 caracteres.
- [`pruebas_sinteticas.py`](pruebas_sinteticas.py), SHA-256 `66ac98f8140c79b1e5b3233902d84563eccd3d628c14156ba1d49144d9be0342`: 64 pruebas, una o más por hallazgo de las tres auditorías de Codex, con un servidor local que imita a Ollama. Se corre con `python -I pruebas_sinteticas.py`; todas pasan.
- [`cribado_llm_azure.ps1`](cribado_llm_azure.ps1), SHA-256 `5944fe0ae99279aec8b84a0e7d39ac56c29ad53978812788106b6eebb264531a`, adaptado del E001 de `experimentos-aislados`. Todo comando nativo (`az`, `ssh`, `scp`) pasa por una función que se detiene si el código de salida no es cero. `lanzar` se niega a correr si ya hay una sesión en la VM, y `bajar` compara los hashes de lo descargado con los de la VM. Lleva escritos los SHA-256 congelados del script y del prompt, y lee de `particion.json` los de las entradas: **no sube nada a la VM si alguno no coincide**. En selección etiqueta solo las configuraciones de `probar.json`; en validación, solo la de `eleccion.json`, y se niega a correr si no hay elegida. Se revisó su sintaxis con PowerShell 7.4 y se probaron con `az`, `ssh` y `scp` simulados las rutas de `probar`, `lanzar` (selección, validación, sin elección, NO APTO, sesión activa, presupuesto agotado, script alterado), `bajar` (hashes correctos y archivo corrompido) y fallas de `az`. Además, el `correr.sh` que genera `lanzar` se ejecutó con bash, `timeout` y `pipefail` reales y un `python3` falso: termina a tiempo con `codigo=0`, corta exactamente en el límite con `codigo=124`, no arranca con el límite vencido (`SIN_TIEMPO`) y, con una configuración que falla con 7, registra `codigo=7`, no corre la siguiente y **termina con 7**. Esto lo ejecutó Claude; el entorno de Codex no permitió ejecutar bash, así que no es una verificación independiente. No se ha ejecutado contra Azure.
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
- 2026-11-06, **enmienda 2**, respuesta a la [auditoría independiente de Codex](auditoria_codex_baa6f061/AUDITORIA_INDEPENDIENTE_CRIBADO_LLM_baa6f061.md) sobre `baa6f061`, **antes de cualquier ejecución**. El detalle, hallazgo por hallazgo, está en [RESPUESTA_AUDITORIA_CODEX.md](RESPUESTA_AUDITORIA_CODEX.md). No cambia el prompt, las configuraciones, las opciones ni la partición. Cambia, por decisión del responsable:
  - CONTEXTO pasa a ser protegida en la sensibilidad y en la compuerta de omisiones (D1);
  - el presupuesto de tiempo es de 24 h de reloj desde el primer `lanzar` (G6);
  - la auditoría de producción usa 100 exclusiones por lote y suspende con un solo error (D3).
  Además corrige la extracción del prompt (G1: el modelo habría recibido 5 caracteres), la validación del esquema (G2), la mezcla de corridas y simulaciones (G3), los estados vigentes (G4), las fallas de comandos nativos (G5) y M1 a M5.
- 2026-11-06, **enmienda 3**, respuesta a la [reauditoría de Codex](auditoria_codex_d580da24/REAUDITORIA_CODEX_d580da24.md) sobre `d580da24`, **antes de cualquier ejecución**. Detalle en [RESPUESTA_AUDITORIA_CODEX.md](RESPUESTA_AUDITORIA_CODEX.md). No cambia el prompt, las configuraciones, las opciones, la partición, la regla de elección, las compuertas ni las decisiones del responsable. Corrige:
  - R1: el evaluador exige el script congelado y la coherencia de cada fila con su respuesta cruda y su modelo;
  - R2: cualquier excepción, no solo las previstas, deja un estado INCONCLUSIVO vigente;
  - R3: el historial usa nombres únicos y escritura exclusiva, y el estado vigente se reemplaza de forma atómica;
  - R4: las salidas se leen en bytes, de modo que un corte a mitad de un carácter UTF-8 ya no bloquea la reanudación;
  - R5: el límite de tiempo viaja como hora absoluta y se aplica en la VM y dentro del proceso;
  - menores: desempate final explícito por número de configuración; "alfanumérico" sin guion bajo; esquema enviado con `additionalProperties: false`; comparación estricta de tipos; `pipefail` en la instalación de Ollama; marco, semilla y censo de la auditoría de producción.
- 2026-11-06, **enmienda 4**, respuesta a la [tercera auditoría de Codex](auditoria_codex_aaa6a255/TERCERA_AUDITORIA_CODEX_aaa6a255.md) sobre `aaa6a255`, **antes de cualquier ejecución**. Codex dio por resueltos R1 a R4 y los seis menores, y R5 en el código. Detalle en [RESPUESTA_AUDITORIA_CODEX.md](RESPUESTA_AUDITORIA_CODEX.md). No cambia el prompt, las configuraciones, las opciones, la partición, la regla de elección, las compuertas ni las decisiones del responsable. Corrige:
  - N1: el presupuesto y las horas de fila se validan como fechas UTC reales; el presupuesto debe declarar exactamente 24 h; una fila fuera de la ventana da INCONCLUSIVO; `--hasta` rechaza fechas inválidas;
  - N2: `segundos` debe ser finito y no negativo, y se mide con reloj monotónico;
  - N3: las líneas descartadas se reportan con número, hash y motivo;
  - N4: `correr.sh` termina con el código del etiquetado;
  - menor: el comentario de `escribir_estado` ya no promete más de lo verificado (no hay `fsync`).
