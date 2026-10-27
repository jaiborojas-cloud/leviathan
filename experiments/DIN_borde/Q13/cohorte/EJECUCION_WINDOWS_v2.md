# DIN-Q13 v2 — ejecución externa autorizada, sin análisis

N=800 confirmado por el responsable: A0/LS/WD, cinco inicializaciones, 12.000
trayectorias. LS=.005; WD=.2. El plan se publicó por SHA en 0135813 **antes**
del generador. Los archivos de calibración y potencia anteriores no se modifican.

## Archivos y entorno

[Generador único](scripts/cohorte_v2.py), [SHA del generador](scripts/cohorte_v2.sha256),
[plan](q13_plan.json), [SHA del plan](q13_plan.sha256) y
[versiones exactas](requirements_windows_v2.txt). Torch es CPU: 2.9.1+cpu;
NumPy2.3.5, SciPy1.17.0 y scikit-learn1.8.0. Validación local con Python3.12.14;
recomendado Python3.12. El script comprueba las cuatro versiones y aborta antes
de entrenar si difieren. La rueda torch+cpu proviene del índice oficial CPU de
PyTorch; los paquetes pueden instalarse previamente desde ruedas locales. No se
instala ni descarga nada desde el script ni se llama a un dataset externo.

Se necesita el checkout completo del repo: core, geometry y rho r3 archivados
se importan sin cambios y se verifican por SHA al arrancar y en cada worker.
No se importa C1/C2/Q13 analista ni se leen sus datos. `python -I` no necesita
PYTHONPATH ni imports de scripts vecinos.

**Conservar bytes LF**, incluso en Windows: SHA distintos por autocrlf detienen
la ejecución. Para un checkout nuevo puede usarse:

```powershell
git clone --config core.autocrlf=false --branch research/din-q13-cohorte-v2 https://github.com/jaiborojas-cloud/leviathan.git D:\leviathan-q13
Set-Location D:\leviathan-q13
```

No normalizar archivos congelados ni sus hashes. En un checkout existente,
comprobar primero su estado y la configuración de saltos de línea; el script no
restaura ni modifica fuentes. Mantener los arrays fuera de Git, en una carpeta
nueva dedicada a esta ejecución. La ruta del venv no se usa para buscar datos T2.

## Comandos PowerShell, desde la raíz del checkout

```powershell
$py = 'D:\RIPG_DATA\T2_A\cribado_borde\venv_torch\Scripts\python.exe'
$script = (Resolve-Path '.\experiments\DIN_borde\Q13\cohorte\scripts\cohorte_v2.py').Path
$out = 'D:\RIPG_DATA\DIN_Q13_v2'

# 1. Tres modelos SIN ENTRENAR, reconstruidos desde sus pesos.
& $py -I $script --parte compuerta --procesos 12 --out $out
if ($LASTEXITCODE -ne 0) { throw 'Compuerta fallida: no entrenar' }

# 2. Prueba corta solicitada: 15 trayectorias NUEVAS, cinco de cada brazo.
& $py -I $script --parte cohorte --limite 15 --procesos 12 --out $out
if ($LASTEXITCODE -ne 0) { throw 'Revisar el fallo y conservar todas las salidas' }
```

La prueba es parte de la cohorte fija, no otro piloto. Las primeras 15 son las
cinco inicializaciones del split0 en A0/LS/WD. Se conservan y no se vuelven a
entrenar al lanzar el resto. **No se ejecutó esta prueba de entrenamiento en el
entorno del agente.** La salida informa tiempo medio de trayectoria y segundos
de pared por trayectoria; el segundo incluye paralelismo y arranque de workers.
Sirve para decidir operacionalmente el lanzamiento, sin calcular asociaciones.

Después de revisar esos tiempos, continuar con la misma carpeta:

```powershell
# 3. Reanudar el universo pendiente; salta registros válidos y fallidos.
& $py -I $script --parte cohorte --procesos 12 --out $out
if ($LASTEXITCODE -ne 0) { throw 'Conservar salida; revisar interrupción antes de reanudar' }

# 4. Sólo al finalizar: publicación, con todas las 12.000 filas planificadas.
& $py -I $script --parte tabla --out $out
if ($LASTEXITCODE -ne 0) { throw 'No sustituir tablas ni registros: reportar el defecto' }
```

La tabla no debe publicarse durante la prueba corta: publicar es terminal y
después se bloquean nuevos entrenamientos en esa carpeta. Incluye ausentes y
fallidas con error, nunca elimina IDs. `RESUMEN_q13.json` contiene tabla_sha256,
plan_sha256 y script_sha256. El proceso imprime sólo conteos/tiempos/hashes,
sin relaciones entre variables ni régimen agregado. No ejecutar el analista.

## Preservación, reanudación y bloqueos

- Multiprocessing usa **spawn** y una hebra BLAS/torch por worker; 12 procesos
  son configurables por CLI. El orden de ejecución es split→k→brazo para el
  pareado; el plan y la tabla usan brazo→split→k como el diseño congelado.
  La revisión r2 mantiene como máximo una tarea enviada por worker. Ante una
  interrupción cancela pendientes y no repone tareas; espera sólo a las ya
  activas, nunca a todo el universo. Véase la enmienda congelada r2.
- Cada trayectoria tiene reclamo, bloqueo del SO, arrays, checkpoints de cuatro
  visitas (5,10,30,250), diagnósticos rho y un JSON final con SHA interno.
- Se salta cualquier JSON ya escrito, incluidos fallos y JSON truncados. Un
  JSON truncado se conserva y se representa como error al publicar la tabla.
  Un reclamo interrumpido sin JSON final se registra como fallo sin reentrenar.
  Si todavía existe un worker vivo que mantiene su bloqueo, se detiene para no
  duplicarlo. Nunca borrar reclamos para volver a entrenar un ID.
- Un bloqueo general evita dos coordinadores o una tabla simultánea con el
  entrenamiento. Los bloqueos los libera el SO al morir el proceso; sus archivos
  permanecen como registro y no necesitan borrarse para reanudar.
- Archivos completos se publican con enlace exclusivo atómico si el FS lo permite;
  fallback exclusivo conserva como fallo cualquier salida incompleta tras un corte.
  Nada se sobreescribe. Tablas/resúmenes idénticos se pueden volver a verificar.
- VINCULO_q13.json ata carpeta, plan, script, instrumento y versiones. Cambiar el
  script o las versiones impide mezclar resultados; un defecto requiere versión y
  enmienda documentadas. No reiniciar en otra carpeta para sustituir fallos.

## Correspondencia con recipe_v1/support_v1

El script incorpora los **bytes íntegros** de ambas fuentes originales y verifica
sus SHA y los archivos archivados. Ejecuta recipe_v1 íntegra sin alterar funciones
de datos, red, inicialización, optimizador, actualización ni métrica. De support_v1
ejecuta los fragmentos originales sha/write/archive/frozen sin cambiar su texto.
El soporte antiguo dependía de Git y rutas de configuración Linux; sus funciones
code_guard/guard no se ejecutan en Windows. El envoltorio nuevo añade verificación
SHA, guarda portable, JSON UTF-8 exclusivo, bloqueos, spawn y reanudación.
No cambia ninguna ecuación científica ni los parámetros del instrumento r3.

La compuerta local se valida sin entrenar y no sustituye la compuerta que deberá
correr en Windows. Las pruebas de tabla/reanudación usan exclusivamente fixtures
sintéticas en una carpeta de validación, no datos de cohorte. Véase el informe de
validación portable que acompaña a la publicación.
