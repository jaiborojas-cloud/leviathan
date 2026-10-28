# DIN-Q13-M2 v2: ejecución en el PC del responsable

**320 splits ×5 inicializaciones ×11 niveles =17.600 trayectorias.** Diseño congelado v2, dosis del plan, salida exclusiva y reanudable. Esta entrega prepara el productor; no se entrenó la cohorte en el entorno del agente ni se ejecutó allí la prueba corta.

| Elemento | Valor fijado |
|---|---|
| Commit de ejecución | `0c00de9362252aa3f51aa2e619b4b36848870ed4` |
| Clon | `D:\leviathan-q13`, `core.autocrlf=false` |
| Python | `D:\RIPG_DATA\venv_q13\Scripts\python.exe` |
| Salida | `D:\RIPG_DATA\DIN_Q13M2_v2` |
| Productor | [scripts/cohorte_v2.py](scripts/cohorte_v2.py) |
| SHA del productor | `87dbc9ee05ad3fdabeb5a0dc21307c81a2a95898159c298dbb8ac4a07c24bbe1` |
| SHA del plan | `4b0aa95f16518fe0854e16540c38494884fbe76201c20df837015548786d90d7` |

El commit de ejecución ya contiene plan, productor, sidecar y requisitos. La documentación y resultados de validación se añaden después para evitar un hash circular. El plan se publicó antes del productor en `b75448d2`.

## 1. Preparar clon e intérprete

PowerShell, una sola vez. Un clon existente debe estar limpio. Los SHA requieren los bytes LF publicados; cambiar autocrlf en un clon antiguo no transforma necesariamente sus archivos. Si falla un SHA, conservar el estado y revisar el checkout, sin normalizar fuentes congeladas automáticamente.

```powershell
$ErrorActionPreference = 'Stop'
$repo = 'D:\leviathan-q13'
$commit = '0c00de9362252aa3f51aa2e619b4b36848870ed4'

if (-not (Test-Path $repo)) {
    git clone --config core.autocrlf=false --branch research/din-q13m2-cohorte https://github.com/jaiborojas-cloud/leviathan.git $repo
    if ($LASTEXITCODE -ne 0) { throw 'Falló el clon' }
}
if (-not (Test-Path (Join-Path $repo '.git'))) { throw 'La carpeta existe y no es el clon esperado' }
git -C $repo config core.autocrlf false
if ($LASTEXITCODE -ne 0) { throw 'No se pudo fijar autocrlf=false' }
$dirty = git -C $repo status --porcelain
if ($LASTEXITCODE -ne 0 -or $dirty) { throw 'Revisar el clon: hay cambios o no se pudo leer su estado' }
git -C $repo fetch origin research/din-q13m2-cohorte
if ($LASTEXITCODE -ne 0) { throw 'Falló fetch' }
git -C $repo -c core.autocrlf=false checkout --detach $commit
if ($LASTEXITCODE -ne 0) { throw 'No se pudo fijar el commit de ejecución' }
$head = git -C $repo rev-parse HEAD
if ($head.Trim() -ne $commit) { throw 'Commit distinto del publicado' }
Set-Location $repo
```

Usar el venv dedicado. Si aún no existe, crearlo con Python3.12; si existe, se reutiliza. Instalación de las [cuatro versiones exactas](requirements_windows_v2.txt), antes de ejecutar el productor:

```powershell
$py = 'D:\RIPG_DATA\venv_q13\Scripts\python.exe'
if (-not (Test-Path $py)) {
    py -3.12 -m venv D:\RIPG_DATA\venv_q13
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear venv_q13 con Python 3.12' }
}
$req = Join-Path $repo 'experiments\DIN_borde\Q13M2\cohorte\requirements_windows_v2.txt'
& $py -m pip install --extra-index-url https://download.pytorch.org/whl/cpu -r $req
if ($LASTEXITCODE -ne 0) { throw 'Revisar instalación de versiones exactas' }
```

La instalación requiere conexión o ruedas locales equivalentes; la ejecución del productor no usa red ni instala paquetes.

## 2. Variables y SHA, también al abrir otra sesión PowerShell

Repetir este bloque en cada ventana nueva. El productor verifica además diseño, analista como archivo, manifiesto, core, geometry, rho r3, receta y soporte. No importa ni ejecuta el analista.

```powershell
$ErrorActionPreference = 'Stop'
$repo = 'D:\leviathan-q13'
$py = 'D:\RIPG_DATA\venv_q13\Scripts\python.exe'
$out = 'D:\RIPG_DATA\DIN_Q13M2_v2'
$commit = '0c00de9362252aa3f51aa2e619b4b36848870ed4'
$script = Join-Path $repo 'experiments\DIN_borde\Q13M2\cohorte\scripts\cohorte_v2.py'
$plan = Join-Path $repo 'experiments\DIN_borde\Q13M2\cohorte\q13m2_plan.json'
$scriptSHA = '87dbc9ee05ad3fdabeb5a0dc21307c81a2a95898159c298dbb8ac4a07c24bbe1'
$planSHA = '4b0aa95f16518fe0854e16540c38494884fbe76201c20df837015548786d90d7'
if (-not (Test-Path $py)) { throw 'Falta el intérprete venv_q13' }
$head = git -C $repo rev-parse HEAD
if ($LASTEXITCODE -ne 0 -or $head.Trim() -ne $commit) { throw 'El clon no está en el commit publicado' }
if ((Get-FileHash -Algorithm SHA256 $script).Hash.ToLowerInvariant() -ne $scriptSHA) { throw 'SHA del productor distinto' }
if ((Get-FileHash -Algorithm SHA256 $plan).Hash.ToLowerInvariant() -ne $planSHA) { throw 'SHA del plan distinto' }
& $py -I -c "import importlib.metadata as m; e=dict(torch='2.9.1+cpu',numpy='2.3.5',scipy='1.17.0'); e['scikit-learn']='1.8.0'; a={k:m.version(k) for k in e}; print(a); assert a==e"
if ($LASTEXITCODE -ne 0) { throw 'Versiones distintas de las fijadas' }
Set-Location $repo
```

## 3. Compuerta y prueba corta

La salida debe ser nueva y dedicada a esta versión, o una reanudación del mismo vínculo. Ejecutar la compuerta en Windows, conservando sus propios arrays; la validación Linux publicada no sustituye esta compuerta.

```powershell
& $py -I $script --parte compuerta --procesos 12 --out $out
if ($LASTEXITCODE -ne 0) { throw 'Compuerta fallida: conservar salidas y reportar' }
$gate = Get-Content -Raw (Join-Path $out 'COMPUERTA_q13m2.json') | ConvertFrom-Json
if ($gate.PASA -ne $true -or $gate.script_sha256 -ne $scriptSHA -or $gate.plan_sha256 -ne $planSHA) {
    throw 'Compuerta no válida para este plan/productor'
}

& $py -I $script --parte cohorte --limite 33 --procesos 12 --out $out
if ($LASTEXITCODE -ne 0) { throw 'Conservar el fallo de la prueba y reportarlo' }
```

Los33 IDs son las tres primeras combinaciones split/k, cada una con11 niveles; forman parte de las17.600. Revisar únicamente conteos, errores y tiempos que imprime la sesión, incluidos `media_segundos_trayectoria` y `segundos_pared_por_trayectoria`. No borrar ni reemplazar fallidas. La duración total se estima a partir de este PC, no del entorno del agente.

## 4. Tres sesiones de cohorte

`--limite` cuenta **nuevos IDs pendientes de esa invocación**, no un total acumulado. Cada invocación omite registros ya escritos, incluidos fallidos. Se conserva la misma carpeta y el mismo script. Se pueden ejecutar las sesiones en momentos separados, una sola activa a la vez.

```powershell
# Sesión 1: hasta 5.900 pendientes adicionales a la prueba.
& $py -I $script --parte cohorte --limite 5900 --procesos 12 --out $out
if ($LASTEXITCODE -ne 0) { throw 'Conservar salidas y reportar la interrupción; no sustituir IDs' }
```

```powershell
# Sesión 2: otros 5.900 pendientes. En ventana nueva, repetir antes variables/SHA.
& $py -I $script --parte cohorte --limite 5900 --procesos 12 --out $out
if ($LASTEXITCODE -ne 0) { throw 'Conservar salidas y reportar la interrupción; no sustituir IDs' }
```

```powershell
# Sesión 3: se ejecutan solo los restantes, normalmente 5.767 tras 33+5.900+5.900.
& $py -I $script --parte cohorte --limite 5900 --procesos 12 --out $out
if ($LASTEXITCODE -ne 0) { throw 'Conservar salidas y reportar la interrupción; no sustituir IDs' }
```

Progreso cada500 y al finalizar; metadatos por sesión con conteos, errores, tiempos y versiones. Un claim interrumpido se registra como fallo sin reentrenar su ID. Si una invocación se interrumpe, conservar todo; el vínculo y los registros permiten continuar los pendientes sin cambiar el universo. No borrar claims, arrays ni registros para forzar repetición.

## 5. Tabla y resumen

Tras completar las invocaciones, comprobar que el recuento operacional cubre el universo. La exportación incluye también cualquier ID ausente como `TRAJECTORY_MISSING`, de modo que nunca omite filas ni inventa datos. Exportar cierra esa carpeta a más entrenamiento.

```powershell
& $py -I $script --parte tabla --out $out
if ($LASTEXITCODE -ne 0) { throw 'No reemplazar una tabla o resumen previos distintos' }
$csv = Join-Path $out 'q13m2_cohorte.csv'
$summary = Join-Path $out 'RESUMEN_q13m2.json'
$r = Get-Content -Raw $summary | ConvertFrom-Json
if ($r.tabla_sha256 -ne (Get-FileHash -Algorithm SHA256 $csv).Hash.ToLowerInvariant()) { throw 'SHA de tabla no coincide' }
if ($r.plan_sha256 -ne $planSHA -or $r.script_sha256 -ne $scriptSHA) { throw 'Resumen de otro plan/productor' }
Get-FileHash -Algorithm SHA256 $csv
Get-FileHash -Algorithm SHA256 $plan
Get-FileHash -Algorithm SHA256 $summary
```

Entregar al analista la tabla, resumen y plan. CSV:17.600 filas,15 columnas exactas del diseño; resumen: `tabla_sha256`, `plan_sha256`, `script_sha256`. Se conservan fallos, checkpoints, diagnósticos rho y warnings fuera de Git. Reexportar exactamente lo mismo es idempotente; datos distintos no se sobreescriben.

Desde el papel de cohorte no calcular D, p, correlaciones ni asociaciones de X con rho/Y, ni ejecutar `analisis_Q13M2.py`. La generación no declara el régimen ni un resultado del confirmatorio.
