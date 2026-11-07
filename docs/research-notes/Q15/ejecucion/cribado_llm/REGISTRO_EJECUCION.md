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

**Siguiente:** cuando el registro diga `FIN seleccion`, `bajar -Mitad seleccion` y `elegir` en la PC.
