# Q15 v3: preparación y ejecución en PowerShell

**BORRADOR para auditoría. Ahora solo preparación y pruebas simuladas.** La búsqueda real se hará después de la auditoría y de resolver la incompatibilidad S2 indicada en [README](README.md). No se modifica el protocolo para evitar ese bloqueo.

Código probado: commit `7056e0dd05cb8ed2b280c2c877d5f6cd7b75487c`. El código, los requisitos y la suite vigente están en ese commit; este procedimiento se publica después sin cambiar sus bytes. Una versión futura requiere su propio commit, SHA y carpeta de salida.

## 1. Clon nuevo y entorno pequeño

Python 3.12 o posterior y Git para Windows instalados. El ejemplo usa Python 3.12 y un entorno nuevo, independiente de los entornos de torch. Si ya existe el directorio de clon, elegir otro; no borrarlo ni resetearlo.

```powershell
$ErrorActionPreference = 'Stop'
$Repo = 'D:\leviathan-q15'
$Revision = '7056e0dd05cb8ed2b280c2c877d5f6cd7b75487c'
if (Test-Path $Repo) { throw 'El directorio de clon ya existe: usa uno nuevo.' }

git -c core.autocrlf=false clone --no-checkout --branch docs/q15-protocolo-sistematico-v1 https://github.com/jaiborojas-cloud/leviathan.git $Repo
if ($LASTEXITCODE -ne 0) { throw 'Fallo al clonar' }
git -C $Repo config core.autocrlf false
git -C $Repo checkout --detach $Revision
if ($LASTEXITCODE -ne 0) { throw 'No se pudo fijar el commit publicado' }

py -3.12 -m venv 'D:\RIPG_DATA\venv_q15'
if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el venv; comprueba el Python instalado.' }
$Py = 'D:\RIPG_DATA\venv_q15\Scripts\python.exe'
$Dir = Join-Path $Repo 'docs\research-notes\Q15\ejecutor_pc_v1'
$Script = Join-Path $Dir 'ejecutar_q15_v3.py'
& $Py -m pip install --requirement (Join-Path $Dir 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'Fallo al instalar tzdata' }
```

En Windows, el único paquete es `tzdata==2025.2` para America/Mexico_City. El resto es biblioteca estándar. No instalar bibliotecas científicas para este productor. No habilitar `autocrlf`: los SHA son de los bytes publicados.

## 2. SHA y controles sin internet bibliográfico

```powershell
$Esperado = 'd561cb0bdccdd40fb91e5d0553ac85dbc58adc13e7487c7f1a1c226b2af1ee41'
$Observado = (Get-FileHash -Algorithm SHA256 -LiteralPath $Script).Hash.ToLowerInvariant()
if ($Observado -ne $Esperado) { throw "SHA del productor discordante: $Observado" }

$Suite = Join-Path $Dir 'pruebas_ejecutar_q15_v3_v1_1.py'
$SuiteEsperada = 'f9fd933d0d3f6417874fca7cb855d9951380baa4a6c3eb2629781f9ed2916671'
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $Suite).Hash.ToLowerInvariant() -ne $SuiteEsperada) { throw 'SHA de suite discordante' }

New-Item -ItemType Directory -Force 'D:\RIPG_DATA\Q15_CONTROLES' | Out-Null
$Informe = 'D:\RIPG_DATA\Q15_CONTROLES\pruebas_001.json'
if ((Test-Path $Informe) -or (Test-Path ([IO.Path]::ChangeExtension($Informe, '.log')))) { throw 'Nombre ya usado; conserva el informe y elige otro.' }
& $Py -I $Suite --out $Informe
if ($LASTEXITCODE -ne 0) { throw 'Las pruebas simuladas fallaron: conservar JSON/log y reportar.' }

& $Py -I $Script --fase preparar --out 'D:\RIPG_DATA\Q15_v3_PREPARACION'
if ($LASTEXITCODE -ne 0) { throw 'No pasó la validación de inputs/plan' }
```

La suite vigente debe dar 66/66. Los `run_01`–`run_03` del repo son históricos con sus respectivos SHA; no son la suite vigente contra el script actual. `preparar` valida los cinco insumos por SHA, genera las 294 entradas y construye las URL; no conecta con bases. Un resultado correcto aquí no valida servicios vivos ni resuelve la compatibilidad de S2.

## 3. Red: comandos previstos para después de la auditoría

**No ejecutar esta sección todavía.** La aprobación del protocolo científico no es aprobación de este productor en borrador. Antes de la recuperación completa hace falta decidir la enmienda S2; el código actual dejará esas 55 búsquedas pendientes.

Los comandos siguientes describen la mecánica del productor auditado. Si la auditoría o enmienda cambia el archivo, actualizar el commit/SHA esperado y usar otra salida. No reutilizar la carpeta de la versión anterior como si su código fuera igual.

```powershell
$Out = 'D:\RIPG_DATA\Q15_v3'
# S2_API_KEY es opcional: configurarla como variable de entorno si ya se dispone de ella.
# No pasar la clave en la línea de comandos ni incorporarla a archivos del repo.

# Evitar que PowerShell 7 interprete el código 2 de pendientes como fallo fatal.
$PSNativeCommandUseErrorActionPreference = $false
& $Py -I $Script --fase todo --out $Out --pausa-s2 1.1 --reintentos 5 --timeout 45
$Codigo = $LASTEXITCODE
if ($Codigo -eq 1) { throw 'Error de uso/integridad/sistema. Conservar la salida y reportar.' }
if ($Codigo -eq 2) { Write-Host 'Hay pendientes: revisar runs y raw. Esto NO cierra Q15.' }
```

También se pueden ejecutar `--fase consultas`, `--fase catalogos` y `--fase citas` sobre la misma carpeta, con el mismo código/insumos. `--fase todo` volverá a usar lo terminado y producirá una nueva versión de resumen. Para una prueba operacional autorizada de una base se puede añadir `--bases arXiv` o una lista separada por comas; las restantes quedan explícitamente sin ejecutar.

## 4. Reanudación y fallos

Si se interrumpe, ejecutar **exactamente el mismo comando** y salida; los cuerpos y trabajos terminados se reutilizan por SHA. El bloqueo de proceso se libera al cerrar el programa; no borrar archivos de caché ni el marcador de identidad. No iniciar dos productores sobre el mismo destino.

Después de corregir acceso/obtener una clave de API, y solo si procede reintentar los fallos conservados:

```powershell
& $Py -I $Script --fase todo --out $Out --reintentar-fallos
$Codigo = $LASTEXITCODE
if ($Codigo -eq 1) { throw 'Error fatal: conservar evidencias.' }
if ($Codigo -eq 2) { Write-Host 'Persisten pendientes, revisar sin reemplazarlos.' }
```

Ese flag crea nuevos intentos/versiones; nunca elimina el fallo anterior ni soluciona la incompatibilidad S2. Un cambio de código o insumos no se reanuda sobre la misma identidad: requiere salida nueva. No hay un tiempo real medido para este productor; recuperar los catálogos y resúmenes con pausas puede tomar muchas horas. El progreso y la caché permiten interrumpirlo.

## 5. Entrega de resultados al revisor

Conservar la carpeta completa fuera de Git. Entregar `IDENTIDAD.json`, el último `runs/run_*.json` y sus CSV, los snapshots de S0, y la evidencia cruda/metadatos de errores o discrepancias. No publicar automáticamente artículos/resúmenes completos ni credenciales. Los conteos desconocidos siguen vacíos/null, no cero.

Los estados de recuperación no son decisiones de inclusión, lectura completa ni novedad. No ejecutar analistas DIN ni experimentos como parte de esta tarea.
