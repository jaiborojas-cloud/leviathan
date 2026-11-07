# Registro de ejecución del piloto de cribado con modelos abiertos

Bitácora de la corrida del [preregistro](PREREGISTRO_CRIBADO_LLM.md), congelado con las enmiendas 1 a 5 y fusionado a `main` en el PR #138. Cada entrada se escribe en el momento, **antes** de ver los resultados de la etapa siguiente.

## 2026-11-07, 11:24 (hora de México): entorno instalado, antes de `probar`

**VM:** `vm-q15-cribado`, grupo `rg-q15-cribado`, región `eastus`, `Standard_NC24ads_A100_v4` spot, tope de 1 USD/h. La creó el responsable el 2026-11-07, después de borrar la del día anterior, que no llegó a usarse. `preparar` instaló los drivers de NVIDIA.

**Ollama:** `ollama version is 0.40.14` en la VM, según `ollama --version`. Es la misma versión del cliente en la PC del responsable. Se instaló con `OLLAMA_VERSION=0.40.14`.

**Modelos**, tal como los reportan `ollama list` y `ollama show` en la VM:

| Modelo | ID | Tamaño | Parámetros | Cuantización | Contexto | Razonamiento (`ollama show`) | Configuración |
|---|---|---|---|---|---|---|---|
| `qwen3.8:27b` | `aaee06c39dcf` | 17 GB | 27.3B | Q4_K_M | 262 144 | niveles `false, low, medium, xhigh`; por defecto `medium` | C1 (`think: false`), C2 (`think: true`) |
| `gemma4:31b` | `17ba34c06c80` | 20 GB | 30.7B | Q4_K_M | 262 144 | niveles `false, true`; por defecto `true` | C3 (sin `think`) |
| `gpt-oss:120b` | `714d86958b6e` | 65 GB | 116.8B | MXFP4 | 131 072 | niveles `low, medium, high`; por defecto `medium` | C4 (`think: "medium"`) |

- El ID de `qwen3.8:27b` coincide con el del experimento E001 de `experimentos-aislados`.
- Los parámetros por defecto de los modelos (temperatura 1 y otros) no se usan: el script envía en cada llamada temperatura 0, semilla 0, contexto de 32 768 y hasta 16 384 tokens de salida. El contexto de 32 768 cabe en los de los tres modelos.

**Precisiones escritas antes de `probar`**, sin cambiar ninguna configuración:
- **C3 razona.** El preregistro define C3 con el razonamiento "por defecto del modelo"; para `gemma4:31b` ese valor es `true`. C3 es, por lo tanto, Gemma con razonamiento.
- **C2 envía `think: true`,** y `qwen3.8:27b` no lista un nivel `true`: sus niveles son `false, low, medium, xhigh`. Si Ollama lo acepta, se entiende como el nivel por defecto del modelo (`medium`). Si lo rechaza, C2 falla en `probar` y queda **NO_EVALUADA**, como dice el preregistro; no se cambia su configuración para rescatarla.

**Código en uso:** `cribado_llm.py` con SHA-256 `0206cd3f296b3d501fcfa1097cf76ec7d9be951581d9bdf8c0fbb501076dac81`. El script de Azure lo verifica antes de subirlo.

**Partición:** el responsable corrió `preparar` en su PC el 2026-11-06 y obtuvo los mismos hashes que [`particion.json`](particion.json): `entrada_seleccion.jsonl` `60fb90cc…a4c2`, `entrada_validacion.jsonl` `cf173c36…8309` y `referencia.jsonl` `1efae470…3d13`.

## 2026-11-07, 11:28: corrección de fines de línea en la PC del responsable

El primer intento de `probar` se detuvo **antes de subir nada**. El script de Azure encontró que `cribado_llm.py` en la PC tenía SHA-256 `3e4b1904…fdfa6` en lugar del congelado `0206cd3f…ac81`. Causa: `core.autocrlf` de Git en Windows convertía el archivo a CRLF al hacer checkout (convertido a CRLF, el archivo congelado da exactamente `3e4b1904…`). Se corrigió con el PR #144, que agrega la carpeta del piloto a `.gitattributes` con `-text`. El responsable volvió a sacar la carpeta, y el control de hashes la aceptó en el segundo intento. El `preparar` del 2026-11-06 no se afecta, porque Python ejecuta igual el código con cualquier fin de línea y sus salidas tuvieron los hashes congelados.

## 2026-11-07, 11:45: `probar` (obra inventada; no es dato de la referencia)

`probar.json` con `utc` `2026-11-07T17:31:50Z`, `simulado: false`, `sistema_sha256` `4659f18d…2727` y `script_sha256` `0206cd3f…ac81`, los congelados.

| Config. | Válida | Decisión | Segundos | `done_reason` | Observación |
|---|---|---|---:|---|---|
| C1 `qwen3.8:27b`, `think: false` | sí | EXCLUIR_FUERA_TEMA | 80.6 | stop | Incluye la carga del modelo en la GPU. |
| C2 `qwen3.8:27b`, `think: true` | sí | EXCLUIR_FUERA_TEMA | 3.7 | stop | Ollama aceptó `think: true`. Reutilizó el modelo ya cargado. |
| C3 `gemma4:31b` | sí | EXCLUIR_FUERA_TEMA | 31.5 | stop | Incluye la carga del modelo. |
| C4 `gpt-oss:120b`, `think: "medium"` | **no** | — | 57.2 | stop | Respondió sin error, pero su JSON **omite `puntos`**, que el esquema exige. |

**C4 queda NO_EVALUADA.** No es una falla de instalación: el modelo cargó, respondió y terminó (`done_reason: stop`, `error: null`). Con Ollama 0.40.14, la restricción de formato no se aplicó a la salida de `gpt-oss:120b`. Rescatarla exigiría cambiar su configuración, y el preregistro solo permite corregir la instalación. Por eso no se repite `probar`. C4 no se etiqueta ni compite, y se reporta como no evaluada.

**Configuraciones evaluadas en la selección: C1, C2 y C3.**

## 2026-11-07, 11:48: `lanzar -Mitad seleccion`

- Configuraciones: C1, C2 y C3, tomadas de `probar.json`; C4 no se etiqueta.
- **Presupuesto fijado:** inicio `2026-11-07T17:46:40Z`, límite **`2026-11-08T17:46:40Z`** (24 h). Desde aquí no se lanza nada después del límite, y lo que no termine deja el piloto INCONCLUSIVO.
- Entrada: `entrada_seleccion.jsonl` (79 obras), verificada contra `60fb90cc…a4c2` antes de subirla.

## 2026-11-07, 12:25: fin de la selección

`FIN seleccion codigo=0`: C1, C2 y C3 completaron 79 de 79 obras cada una, en unos 38 minutos. `bajar` verificó los hashes de las 3 salidas contra la VM. El entorno quedó en `nube_info_seleccion.txt`.

## 2026-11-07, 12:26: `elegir` (solo la mitad de selección)

Estado `eleccion.json`: `utc` `2026-11-07T18:26:28Z`, intento `ce57f02e28f84f9abac2ec3165a624f4`, `prueba: false`, sin líneas descartadas. Evaluadas C1, C2 y C3; C4 NO_EVALUADA. Las tres compiten (cero inválidas).

| Config. | Protegidas | Omisiones | Sensibilidad | Acuerdo | Inválidas | Mediana (s) |
|---|---:|---:|---:|---:|---:|---:|
| C1 `qwen3.8:27b`, sin razonamiento | 28 | 16 | 0.429 | 0.785 | 0 | 2.57 |
| C2 `qwen3.8:27b`, con razonamiento | 28 | 15 | 0.464 | 0.759 | 0 | 10.96 |
| **C3 `gemma4:31b`, con razonamiento** | 28 | **4** | **0.857** | **0.835** | 0 | 11.55 |

**Elegida: C3**, por mayor sensibilidad (regla congelada, criterio 1).

- Omisiones de C3: W00001, W00024, W00119 y W00377. En su matriz, 3 obras INCLUIR y 1 CONTEXTO pasaron a EXCLUIR, y 9 obras EXCLUIR pasaron a INCLUIR (4) o a CONTEXTO (5).
- C1 y C2 excluyeron más de la mitad de las obras protegidas (13 y 12 INCLUIR, y las 3 CONTEXTO).

**C4 queda NO_EVALUADA de forma definitiva.** El responsable había planteado reintentar gpt-oss, pero `elegir` ya se ejecutó; agregarla ahora sería elegir con los resultados a la vista.

**Expectativa escrita antes de validar:** con 4 omisiones de 28 en la selección, la probabilidad de 0 omisiones entre las 27 protegidas de la validación, con una tasa parecida, es de alrededor de 1 a 2 %. Se espera NO APTO. La validación se corre de todos modos, como pide el preregistro.

## 2026-11-07, 12:40 a 12:57: validación

`lanzar -Mitad validacion` solo con C3, tomada de `eleccion.json`, dentro del mismo presupuesto. `FIN validacion codigo=0`: 75 de 75 obras en unos 15 minutos.

## 2026-11-07, 12:58: `validar`, veredicto oficial

Estado `veredicto.json`: `utc` `2026-11-07T18:57:56Z`, intento `36c992b68017478ab45f56987eea30af`, `prueba: false`, sin líneas descartadas.

| Compuerta | Resultado | Umbral | Estado |
|---|---|---|---|
| Omisiones | **3** de 27 protegidas (W00026, W00057, W00080) | 0 | **FALLA** |
| Acuerdo | 0.853 | ≥ 0.85 | PASA |
| Inválidas | 0 de 75 | ≤ 2 % | PASA |

Matriz (referencia → C3): EXCLUIR→EXCLUIR 40, EXCLUIR→INCLUIR 7, EXCLUIR→CONTEXTO 1, INCLUIR→INCLUIR 23, INCLUIR→EXCLUIR 1, CONTEXTO→CONTEXTO 1, CONTEXTO→EXCLUIR 2. Sensibilidad 0.889; mediana de 11.71 s por obra.

### **Veredicto: NO APTO.**

Conforme al preregistro:
- el cribado de las 2 998 obras pendientes **no** se hace con un modelo abierto: vuelve a Argon (cuota a partir del 2026-11-12);
- no se repite el piloto con estos datos cambiando el prompt, las configuraciones, las opciones ni los umbrales; un intento nuevo requiere una enmienda y una referencia nueva;
- ninguna decisión del modelo entra al corpus de Q15. Las salidas quedan archivadas en `D:\RIPG_DATA\Q15_CRIBADO_LLM`, fuera de Git.

## Observaciones exploratorias (no forman parte del veredicto)

- De las 3 omisiones, 1 es una obra INCLUIR (W00026, 1 de 24) y 2 son CONTEXTO (W00057 y W00080, 2 de 3): aplicaciones de evaluación incremental que el criterio del responsable puso en CONTEXTO. Sin la protección de CONTEXTO (decisión D1), la omisión de W00026 bastaba para fallar; el NO APTO no depende de esa decisión.
- C3 tiende a incluir de más (8 obras EXCLUIR pasaron a INCLUIR o CONTEXTO), el error menos costoso para el protocolo. Los dos Qwen, en cambio, excluyeron más de la mitad de las protegidas en la selección.
- gpt-oss (C4) no respetó el formato estructurado con Ollama 0.40.14.
- Si en el futuro se quisiera usar un modelo como apoyo, por ejemplo para ordenar la cola de Argon o como segundo lector, sería un diseño nuevo, con su propio preregistro y una referencia distinta de estas 154 obras.

## Cierre

- Gasto de cómputo: una VM spot A100 durante unas 2 h el 2026-11-07 (instalación, `probar`, selección y validación), con un tope de 1 USD/h; la del 2026-11-06 se borró sin usarse.
- La VM se borra con `-Fase borrar` después de `bajar -Mitad validacion`.
- Todos los puntos de Q15 siguen **PENDIENTE, sin adjudicar**.
