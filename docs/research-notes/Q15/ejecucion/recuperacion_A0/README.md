# Q15, fase A0: recuperación automática de resúmenes (sin LLM)

**Estado:** BORRADOR. Pendiente de la auditoría del otro agente antes de correrlo. Lo autorizó el responsable el 2026-11-09, a las 13:54 (hora de México), como modificación operativa del [plan de pendientes v1](https://github.com/jaiborojas-cloud/leviathan/pull/138#issuecomment-6749882361) (`7db5386e…`). No cambia criterios, topes, corte ni el tratamiento de desconocidos.

## Qué hace
- **Insumo:** `INVENTARIO_857.json` del plan v1, con SHA-256 `778424329491191e31c6c669e3504ff2a0e2730966c389226d7a1a73315ef14d`, que se verifica antes de correr.
- **Consultas:**
  - Para los 510 registros con DOI consulta por ese DOI:
    - OpenAlex (`abstract_inverted_index`, reconstruido por posición, sin reescritura);
    - Crossref (`abstract` JATS, solo se quitan etiquetas);
    - Semantic Scholar (`abstract`).
  - Para los 7 con arXiv consulta la API de arXiv: resumen y fecha `published` de la v1.
  - Los 340 registros sin identificador quedan `SIN_IDENTIFICADOR`, para la fase manual A2.
- **Identidad:** un resumen se acepta solo si el **título normalizado** de la fuente coincide con el del inventario. El inventario no trae autores. Si no coincide, queda `CONFLICTO_IDENTIDAD`, con la fuente registrada.
- **No decide pertinencia ni fechas.** Solo propone uno de estos estados:
  - `RESUMEN_RECUPERADO`, que pasa al cribado normal (A1);
  - `SIN_RESUMEN_EN_FUENTES`, `CONFLICTO_IDENTIDAD`, `ERROR_ACCESO` o `SIN_IDENTIFICADOR`, que pasan a A2.

  Las fechas candidatas de cada fuente se registran para F01, sin adjudicarlas.
- **Trazabilidad:** cada respuesta cruda se guarda en `raw/<sha(url)>/intento_NN.body`, con su SHA, la hora UTC real y la URL final. Los reintentos de errores transitorios (429, 5xx, red) continúan la numeración y nunca sobrescriben intentos anteriores. Las respuestas finales se reutilizan desde la caché.
- **Identidad de la salida:** `IDENTIDAD.json` guarda la versión, el SHA del script y el SHA del inventario. Si no coinciden, rechaza la carpeta.
- **Cortesía:** User-Agent genérico (no se envía correo), pausas por fuente (OpenAlex 0.5 s, Crossref 1 s, S2 1.1 s, arXiv 3 s) y respeto de `Retry-After`. Solo usa la biblioteca estándar de Python 3.12.
- **Salidas:**
  - `recuperacion_a0.csv` y `recuperacion_a0.json`, por registro;
  - `RESUMEN_A0.json`, con los conteos.

  Código de salida: 0 si todo terminó, 2 si quedan `ERROR_ACCESO` (reintentable repitiendo el comando) y 1 si hay error de insumo.
- **Duración estimada:** unas 1 540 solicitudes, alrededor de 30–45 min. Se puede cortar con Ctrl+C y reanudar con el mismo comando.
- Los datos quedan **fuera de Git**: los resúmenes son de los editores y servicios citados, y se usan solo para cribar.

| archivo | SHA-256 |
|---|---|
| `recuperar_a0.py` | `97d2f0e3bd0ad100eca7784c60ab7571a714fe69705ee833cf711733b1adffa2` |
| `pruebas_recuperar_a0.py` | `c3685c3ae924b245960edd21053c332a681a5613248700beb777d8f4e4890904` |

Pruebas: 15 de 15, sin red (el socket está bloqueado), en Linux con Python 3.13. Hay que confirmarlas en Windows con el bloque de abajo.

## Procedimiento (una ventana nueva de PowerShell, un solo bloque)

Antes de correr, extrae `INVENTARIO_857.json` del zip `Q15_PLAN_PENDIENTES_857_v1.zip` a `D:\RIPG_DATA\Q15_A0\insumo\`.

```powershell
$ErrorActionPreference = 'Stop'
$Repo = 'D:\leviathan-q15-a0'
$Rev = '<COMMIT_AUDITADO>'
if (-not (Test-Path $Repo)) {
    git clone --no-checkout https://github.com/jaiborojas-cloud/leviathan.git $Repo
    git -C $Repo checkout --detach $Rev
}
if ((git -C $Repo rev-parse HEAD) -ne $Rev) { throw 'El clon no está en el commit auditado' }
$Py = 'D:\RIPG_DATA\venv_q15\Scripts\python.exe'
$Dir = Join-Path $Repo 'docs\research-notes\Q15\ejecucion\recuperacion_A0'
$Script = Join-Path $Dir 'recuperar_a0.py'; $Suite = Join-Path $Dir 'pruebas_recuperar_a0.py'
if ((Get-FileHash $Script -Algorithm SHA256).Hash.ToLower() -ne '97d2f0e3bd0ad100eca7784c60ab7571a714fe69705ee833cf711733b1adffa2') { throw 'SHA del script' }
if ((Get-FileHash $Suite -Algorithm SHA256).Hash.ToLower() -ne 'c3685c3ae924b245960edd21053c332a681a5613248700beb777d8f4e4890904') { throw 'SHA de las pruebas' }
& $Py -I $Suite
if ($LASTEXITCODE -ne 0) { throw 'Las pruebas fallaron: copia la salida y repórtala' }
$Inv = 'D:\RIPG_DATA\Q15_A0\insumo\INVENTARIO_857.json'
$Out = 'D:\RIPG_DATA\Q15_A0\salida'
$PSNativeCommandUseErrorActionPreference = $false
& $Py -I $Script --inventario $Inv --out $Out --limite 5
"Prueba con 5 registros, código: $LASTEXITCODE"
```

Si la prueba con 5 registros sale bien (código 0 o 2, sin errores rojos), corre los 857 sobre **la misma carpeta**. Los 5 primeros se reutilizan desde la caché:

```powershell
& $Py -I $Script --inventario $Inv --out $Out
"Código: $LASTEXITCODE"
```

Entrega `RESUMEN_A0.json`, `recuperacion_a0.csv` y `recuperacion_a0.json`, con sus SHA, para la auditoría y para que se cribe en A1.
