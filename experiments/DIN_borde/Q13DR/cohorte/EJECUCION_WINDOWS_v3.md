# DIN-Q13-DR: ejecución Windows por el responsable

**N200,6 niveles,5 inicializaciones:6.000 trayectorias.** Dosis LS:0,.002,.005,.01,.02,.05. La simulación de potencia y sus sensibilidades están [publicadas](potencia/RESULTADO_v1.md). El plan se publicó en fe8dd9c8, antes del productor2452bf47.

No se entrenó la cohorte ni se ejecutó una prueba corta en el entorno del agente. Solo se validaron controles sin entrenamiento e IO. No se ejecuta ningún analista ni se calculan asociaciones en el productor.

## Archivos y versiones

- [Plan](q13dr_plan.json), SHA `e7c99a0188abc84cce6504fb6882b9373775f8aaba8d0eebdf597c752c1fed64`.
- [Productor único](scripts/cohorte_v3.py), SHA `7b855802d0cf1b4bce7a3ede0a465b876284c847aeb1bec4508af7b1228fc9cb`.
- [Versiones exactas](requirements_windows_v3.txt): torch2.9.1+cpu,numpy2.3.5,scipy1.17.0,scikit-learn1.8.0; Python3.12 recomendado, validado con3.12.14.

Se necesita el checkout completo para verificar core, geometry y rho r3 por SHA. La receta y el soporte se incluyen byte por byte dentro del script; no requiere PYTHONPATH, scripts vecinos importados, instalación automática ni red al ejecutar. El texto «v2» de su docstring inicial identifica su productor padre; el vínculo operativo es DIN-Q13DR-v3-portable-1 y el diseño verificado es v3 congelado.

**Conservar bytes LF:** un checkout que transforme a CRLF modifica los SHA y se rechaza. Para un checkout nuevo:

```powershell
git clone --config core.autocrlf=false --branch research/din-q13dr-cohorte https://github.com/jaiborojas-cloud/leviathan.git D:\leviathan-q13dr
Set-Location D:\leviathan-q13dr
```

En un checkout existente, revisar su estado y saltos de línea; no restaurar ni normalizar fuentes congeladas automáticamente. No mezclar salidas Q13DR con Q13 o C2. Los paquetes deben estar instalados antes (se pueden usar ruedas locales); el script aborta si las cuatro versiones no coinciden.

## PowerShell

Usar una carpeta de salida nueva y dedicada fuera del checkout. La ubicación del intérprete no se usa para buscar datos T2:

```powershell
$py = 'D:\RIPG_DATA\T2_A\cribado_borde\venv_torch\Scripts\python.exe'
$script = (Resolve-Path '.\experiments\DIN_borde\Q13DR\cohorte\scripts\cohorte_v3.py').Path
$out = 'D:\RIPG_DATA\DIN_Q13DR_v3'

# 1. Tres reconstrucciones desde pesos SIN entrenar.
& $py -I $script --parte compuerta --procesos 12 --out $out
if ($LASTEXITCODE -ne 0) { throw 'Compuerta fallida: conservar salidas y no entrenar' }

# 2. Prueba corta:30 trayectorias del plan = un split completo,5 k por6 niveles.
& $py -I $script --parte cohorte --limite 30 --procesos 12 --out $out
if ($LASTEXITCODE -ne 0) { throw 'Revisar el fallo y conservar todas las salidas' }
```

Revisar únicamente conteos, errores y tiempos por trayectoria. La prueba corta pertenece al universo fijo y no se sustituye: al continuar se omiten las trayectorias ya escritas, incluidas las fallidas.

```powershell
# 3. Continuar el mismo universo desde los pendientes.
& $py -I $script --parte cohorte --procesos 12 --out $out
if ($LASTEXITCODE -ne 0) { throw 'Conservar el error y reportarlo; no sustituir trayectorias' }

# 4. Publicar tabla con TODOS los IDs planificados y resumen por SHA.
& $py -I $script --parte tabla --out $out
if ($LASTEXITCODE -ne 0) { throw 'No sobrescribir una publicación previa distinta' }

Get-FileHash -Algorithm SHA256 (Join-Path $out 'q13dr_cohorte.csv')
Get-FileHash -Algorithm SHA256 (Join-Path $out 'RESUMEN_q13dr.json')
```

La tabla siempre tiene6.000 filas y las15 columnas del diseño. Las ausentes llevan TRAJECTORY_MISSING; los fallos conservan su error. RESUMEN_q13dr.json contiene exactamente tabla_sha256,plan_sha256,script_sha256. Publicar la tabla impide añadir entrenamiento en esa carpeta. Reexportar lo mismo es idempotente; una tabla distinta nunca se reemplaza.

## Reanudación y archivos

El orden de envío es split→k→nivel, con máximo12 tareas en vuelo. El orden de tabla/hash es nivel→split→k. Semillas pareadas:811000+s,821000+5s+k,831000+5s+k. L0 usa Adam y pérdida normal; L1–L5 usan Adam y el epsilon de cada nivel. La construcción de M y rho no cambia.

El progreso se imprime cada500 trayectorias y al terminar la invocación. Los arrays, checkpoints en5/10/30/250, diagnósticos rho, warnings y estados quedan fuera de Git en la salida. Los claims interrumpidos se convierten en fallos conservados, sin reentrenar ese ID. Los registros truncados se preservan; los hashes alterados detienen la ejecución. Los bloqueos del SO se liberan al morir el proceso, y no se deben borrar claims para forzar un reemplazo.

La carpeta queda vinculada al plan,script y versiones. Cambiar código o paquete requiere una versión documentada, nunca reutilizar salidas como si fueran la misma corrida. Al interrumpir, pueden terminar los workers ya activos; no se encola todo el universo ni se reponen tareas después de un fallo del coordinador.

Entregar al analista la tabla y su resumen, junto al plan publicado. No ejecutar analisis_Q13DR.py ni calcular D,p,correlaciones o X frente a rho/Y sobre esta cohorte desde el papel de productor.
