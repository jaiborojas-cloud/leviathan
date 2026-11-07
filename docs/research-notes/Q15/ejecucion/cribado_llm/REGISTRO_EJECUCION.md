# Registro de ejecución del piloto de cribado con modelos abiertos

Bitácora de la corrida del [preregistro](PREREGISTRO_CRIBADO_LLM.md), congelado con las enmiendas 1 a 5 y fusionado a `main` en el PR #138. Cada entrada se escribe en el momento, **antes** de ver los resultados de la etapa siguiente.

## 2026-11-07, 11:24 (hora de México): entorno instalado, antes de `probar`

**VM:** `vm-q15-cribado`, grupo `rg-q15-cribado`, región `eastus`, `Standard_NC24ads_A100_v4` spot, tope de 1 USD/h. La creó el responsable el 2026-11-07, después de borrar la del día anterior, que no llegó a usarse. `preparar` instaló los drivers de NVIDIA.

**Ollama:** se instaló con `OLLAMA_VERSION=0.40.14`, la misma versión del cliente en la PC del responsable. La salida de `ollama --version` de la VM queda en `nube_info_*.txt` al bajar los resultados.

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

**Siguiente:** `probar`.
