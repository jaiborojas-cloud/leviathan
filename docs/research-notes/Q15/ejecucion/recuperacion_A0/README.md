# Q15, fase A0: recuperación automática de resúmenes (sin LLM)

**Estado:** BORRADOR v1.1. Corrige los hallazgos de la [auditoría de Argon](AUDITORIA_ARGON_PR148_2026-11-09.md) sobre `6a4a7267`: B1, H1, H2, M1 y M2. Necesita reconfirmación antes de correrlo. Lo autorizó el responsable el 2026-11-09, a las 13:54 (hora de México), como modificación operativa del [plan de pendientes v1](https://github.com/jaiborojas-cloud/leviathan/pull/138#issuecomment-6749882361) (`7db5386e…`). No cambia criterios, topes, corte ni el tratamiento de desconocidos.

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
| `recuperar_a0.py` | `d67177372a763fbe31d374a203cda4dcc7096bd7b93d6389494690e0bc304720` |
| `pruebas_recuperar_a0.py` | `82df471fd57e04860743b17cb8ea7d50a6a8bce3668f66b0646de4fe328ca76b` |

Pruebas: 20 de 20, sin red (el socket está bloqueado), en Linux con Python 3.13. Incluyen regresiones de H1 (Ctrl+C durante la espera de un reintento y cuerpo huérfano sin meta), H2 (fechas solo de fuentes con título coincidente), M1 (títulos vacíos tras normalizar) y B1 (`.gitattributes`). Hay que confirmarlas en Windows con el bloque de abajo.

**Fin de línea:** `.gitattributes` declara `recuperacion_A0/** -text`, y el clon usa además `core.autocrlf=false`. Así el SHA en Windows coincide con el calculado con LF.

## Procedimiento (una ventana nueva de PowerShell, un solo bloque)

Antes de correr, extrae `INVENTARIO_857.json` del zip `Q15_PLAN_PENDIENTES_857_v1.zip` a `D:\RIPG_DATA\Q15_A0\insumo\`.

```powershell
$ErrorActionPreference = 'Stop'
$Repo = 'D:\leviathan-q15-a0'
$Rev = '<COMMIT_AUDITADO>'
if (-not (Test-Path $Repo)) {
    git -c core.autocrlf=false clone --no-checkout https://github.com/jaiborojas-cloud/leviathan.git $Repo
    git -C $Repo config core.autocrlf false
    git -C $Repo checkout --detach $Rev
}
if ((git -C $Repo rev-parse HEAD) -ne $Rev) { throw 'El clon no está en el commit auditado: usa otra carpeta $Repo (no borres la anterior) o haz fetch y checkout del commit auditado' }
$Py = 'D:\RIPG_DATA\venv_q15\Scripts\python.exe'
$Dir = Join-Path $Repo 'docs\research-notes\Q15\ejecucion\recuperacion_A0'
$Script = Join-Path $Dir 'recuperar_a0.py'; $Suite = Join-Path $Dir 'pruebas_recuperar_a0.py'
if ((Get-FileHash $Script -Algorithm SHA256).Hash.ToLower() -ne 'd67177372a763fbe31d374a203cda4dcc7096bd7b93d6389494690e0bc304720') { throw 'SHA del script' }
if ((Get-FileHash $Suite -Algorithm SHA256).Hash.ToLower() -ne '82df471fd57e04860743b17cb8ea7d50a6a8bce3668f66b0646de4fe328ca76b') { throw 'SHA de las pruebas' }
& $Py -I $Suite
if ($LASTEXITCODE -ne 0) { throw 'Las pruebas fallaron: copia la salida y repórtala' }
$Inv = 'D:\RIPG_DATA\Q15_A0\insumo\INVENTARIO_857.json'
$Out = 'D:\RIPG_DATA\Q15_A0\salida'
$PSNativeCommandUseErrorActionPreference = $false
& $Py -I $Script --inventario $Inv --out $Out --limite 5
"Prueba con 5 registros, código: $LASTEXITCODE"
```

Si la carpeta `$Repo` ya existe de un intento anterior o de otro commit, el bloque se detiene sin tocarla (M2). Si la prueba con 5 registros sale bien (código 0 o 2, sin errores rojos), corre los 857 sobre **la misma carpeta**. Los 5 primeros se reutilizan desde la caché:

```powershell
& $Py -I $Script --inventario $Inv --out $Out
"Código: $LASTEXITCODE"
```

Entrega `RESUMEN_A0.json`, `recuperacion_a0.csv` y `recuperacion_a0.json`, con sus SHA, para la auditoría y para que se cribe en A1.
