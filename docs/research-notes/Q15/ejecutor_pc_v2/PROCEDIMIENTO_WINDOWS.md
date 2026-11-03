# Q15 v3.1 — comandos PowerShell

Ejecutar **1 → 2 → 3**, en este orden. Usar un clon y una salida nuevos; conservar cualquier salida anterior. El responsable ya autorizó la enmienda S2. Estos comandos no ejecutan experimentos DIN.

## 1. Fijar los bytes publicados

```powershell
$ErrorActionPreference = 'Stop'
$Repo = 'D:\leviathan-q15-v31'
$Revision = '5259d942d4f54c3d28f917f6e4a41ed9bd890a42'
if (Test-Path $Repo) { throw 'El clon ya existe: elige otro directorio, no lo borres.' }
git -c core.autocrlf=false clone --no-checkout --branch docs/q15-protocolo-sistematico-v1 https://github.com/jaiborojas-cloud/leviathan.git $Repo
if ($LASTEXITCODE -ne 0) { throw 'Fallo al clonar' }
git -C $Repo config core.autocrlf false
git -C $Repo checkout --detach $Revision
if ($LASTEXITCODE -ne 0) { throw 'No se pudo fijar el commit' }

$Venv = 'D:\RIPG_DATA\venv_q15'
if (-not (Test-Path $Venv)) {
    py -3.12 -m venv $Venv
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el entorno Python 3.12' }
}
$Py = Join-Path $Venv 'Scripts\python.exe'
$Dir = Join-Path $Repo 'docs\research-notes\Q15\ejecutor_pc_v2'
$Script = Join-Path $Dir 'ejecutar_q15_v3.py'
$Suite = Join-Path $Dir 'pruebas_ejecutar_q15_v3_1.py'
& $Py -I -m pip install --requirement (Join-Path $Dir 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'No se pudo instalar tzdata fijado' }
```

Python 3.12 o posterior. El único requisito externo es `tzdata==2025.2` en Windows. No usar `autocrlf=true`: cambia los SHA. El commit fijado contiene el ejecutor, requisitos, suite y enmienda; esta documentación se publica después sin cambiar esos bytes.

## 2. Pruebas y preparación sin consultas bibliográficas

```powershell
$ScriptSHA = '9d986a770956c49edd1174d9bb2b50bc65dbfe5c4958c7e753083d5ceb2df8a4'
$SuiteSHA = 'eadbb41fae694e8c30077037320bfc46a239768d1861cf4b0d30a2839174aadc'
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $Script).Hash.ToLowerInvariant() -ne $ScriptSHA) { throw 'SHA del ejecutor discordante' }
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $Suite).Hash.ToLowerInvariant() -ne $SuiteSHA) { throw 'SHA de la suite discordante' }

$Controles = 'D:\RIPG_DATA\Q15_v31_CONTROLES'
New-Item -ItemType Directory -Force $Controles | Out-Null
$Informe = Join-Path $Controles 'pruebas_001.json'
if ((Test-Path $Informe) -or (Test-Path ([IO.Path]::ChangeExtension($Informe, '.log')))) { throw 'Informe ya existente: conserva y elige otro nombre.' }
& $Py -I $Suite --out $Informe
if ($LASTEXITCODE -ne 0) { throw 'Las pruebas fallaron: conservar JSON y log, y reportar.' }

& $Py -I $Script --fase preparar --out 'D:\RIPG_DATA\Q15_v31_PREPARACION'
if ($LASTEXITCODE -ne 0) { throw 'Falló la integridad de insumos/plan' }
```

Se esperan **91 pruebas PASS**. La suite sustituye el transporte y bloquea sockets: no consulta bases reales. `preparar` valida los insumos por SHA y construye las 294 unidades/URL sin peticiones HTTP. Ese resultado no demuestra que los servicios vivos sean accesibles.

## 3. Recuperación con internet del PC

Solo después de pasar el paso 2. La salida es nueva y ajena al clon, independiente de la preparación y de cualquier Q15 v3/v1 anterior.

```powershell
$Out = 'D:\RIPG_DATA\Q15_v31_RED'
# S2_API_KEY es opcional si ya se dispone de ella: usar la variable de entorno,
# nunca pegar la clave en comandos, capturas, informes o archivos del repo.
$PSNativeCommandUseErrorActionPreference = $false
& $Py -I $Script --fase todo --out $Out --pausa-s2 1.1 --reintentos 5 --timeout 45
$Codigo = $LASTEXITCODE
if ($Codigo -eq 1) { throw 'Error fatal de uso/integridad/sistema: conservar la salida y reportar.' }
if ($Codigo -eq 2) { Write-Host 'Quedan pendientes de acceso/esquema/cobertura: revisar el último run; Q15 no está cerrada.' }
```

Puede tomar muchas horas recuperar catálogos y resúmenes con las pausas; no hay tiempo real medido. El ejecutor imprime progreso por catálogo/volumen/consulta y cada 50 solicitudes. Para una primera conexión acotada se puede usar `--fase consultas --bases SemanticScholar` con el mismo `$Out`; las bases/fases restantes quedan explícitamente sin ejecutar. Después `--fase todo` las integra utilizando la misma caché y produce otro informe exclusivo.

## 4. Reanudar y entregar

Tras una interrupción, repetir **el mismo comando, versión y salida**; se validan y reutilizan los trabajos terminados y sus dependencias. No borrar caché ni identidad, ni ejecutar dos procesos sobre la misma salida. Para reintentar fallos de acceso o contenido ya conservados:

```powershell
& $Py -I $Script --fase todo --out $Out --pausa-s2 1.1 --reintentos 5 --timeout 45 --reintentar-fallos
$Codigo = $LASTEXITCODE
if ($Codigo -eq 1) { throw 'Error fatal: conservar evidencias y reportar.' }
if ($Codigo -eq 2) { Write-Host 'Persisten pendientes; no confundirlos con cero resultados.' }
```

El reintento crea versiones nuevas, no reemplaza cuerpos ni resultados. Una discrepancia de SHA es un fallo de integridad: no borrarla para forzar un reintento. Si cambia el ejecutor o cualquier insumo, se requiere otra carpeta de salida.

Conservar toda la salida fuera de Git. Entregar `IDENTIDAD.json`, el último `runs/run_*.json` y sus CSV, snapshots S0 y evidencia cruda/metadatos de los pendientes. Los JSON conservan las posiciones no seleccionadas, el total **estimado** de bulk, tokens, incidencias y enlaces de evidencia. Los CSV son índices de consulta, no sustitutos de los JSON completos ni decisiones de pertinencia. Google Scholar queda omitida opcional; no hay automatización de CAPTCHA. No publicar automáticamente respuestas completas, artículos ni credenciales.
