# Q15, fase A2a: segunda recuperación automática de resúmenes (sin LLM)

**Estado:** BORRADOR v1.1. Corrige los hallazgos de la [auditoría de Argon](AUDITORIA_ARGON_PR150_2026-11-10.md) sobre `081021ba` (0 bloqueantes; A1, M1, M2, B1–B3). Necesita reconfirmación antes de correrlo.

**Autorización:** el responsable la dio el 2026-11-10 a las 08:28 (hora de México). Es una modificación operativa del [plan de pendientes v1](https://github.com/jaiborojas-cloud/leviathan/pull/138#issuecomment-6749882361): la fase A2, que el plan definía como manual, se divide en una parte automática (A2a, este script) y una manual (A2b) para lo que A2a no resuelva. No cambia criterios, topes, corte ni el tratamiento de lo desconocido. **No decide pertinencia ni fechas.**

## Insumos

Los dos insumos se verifican por SHA antes de correr:

| Insumo | SHA-256 |
|---|---|
| `INVENTARIO_857.json` del plan v1 | `778424329491191e31c6c669e3504ff2a0e2730966c389226d7a1a73315ef14d` |
| `recuperacion_a0.json`, salida de A0 v1.1 (`IDENTIDAD.json` de A0: script `d6717737…`) | `1e05f504b39d44e410e43eddfb2e58ed60fce86a71859840d377f5cb4593c2ce` |

Se procesan solo los **595** registros que A0 no recuperó: 340 `SIN_IDENTIFICADOR`, 234 `SIN_RESUMEN_EN_FUENTES` y 21 `CONFLICTO_IDENTIDAD`. De ellos, 562 traen en el snapshot la URL de su registro en Semantic Scholar.

Las pendientes de los lotes H y las exclusiones por título sin resumen **no** están en este inventario. Si se quieren pasar por A2a, se necesita un inventario aparte con el mismo esquema, registrado con su SHA.

## Procedimiento por registro

Se detiene en cuanto recupera un resumen aceptado.

1. **Ancla S2.** Toma el `paperId` de la URL del snapshot y consulta `graph/v1/paper/{id}`. Es el mismo registro del snapshot, así que su resumen se acepta si el título normalizado coincide (nivel `ANCLA_S2`). De ahí salen los **autores de referencia**, el año y los identificadores externos (DOI, arXiv). Si el título del registro S2 no coincide, ese registro no se usa como ancla y queda anotado.
2. **Identificadores derivados del ancla.** Si el ancla trae un DOI o un arXiv que el snapshot no tenía, consulta OpenAlex y Crossref (por DOI) o arXiv (por id). Acepta con título normalizado coincidente, como A0 (nivel `ID_DERIVADO_DEL_ANCLA`).
3. **Búsqueda por título**, en este orden: OpenAlex (`title.search`), Crossref (`query.bibliographic`), S2 (`search/match`) y arXiv (`ti:` por token). Un candidato se acepta solo si cumple las tres condiciones:
   - **(a)** su título normalizado es **idéntico** al del inventario;
   - **(b)** su **año** es compatible, a ±1 del snapshot, que admite la diferencia entre preprint y publicación;
   - **(c)** el **apellido del primer autor** coincide con el del ancla, cuando el ancla da autores.

   Un candidato sin primer autor identificable se rechaza siempre. Los apellidos se comparan tras plegar acentos y, si el nombre no está en alfabeto latino, con sus letras en ese alfabeto. Con autor de referencia, la búsqueda se detiene en la primera fuente que da un aceptado; sin él, se consultan **todas** las fuentes para detectar discrepancias de primer autor entre ellas. En Crossref el año se toma de `issued` y, si falta, de las demás fechas de la obra. En arXiv la consulta une con `AND` los tokens del título de más de 2 letras, sin operadores reservados; eso solo amplía la búsqueda, no la aceptación.

   Cada candidato rechazado guarda su motivo (`titulo`, `anio`, `primer_autor`). Con autor de referencia, el nivel es `BUSQUEDA_TITULO_ANIO_AUTOR`. Sin él, el nivel es `BUSQUEDA_TITULO_ANIO_SIN_AUTOR_DE_REFERENCIA` (**identidad débil: A1 debe verificar autores contra R4 antes de cribar**). Si en ese caso los candidatos aceptados discrepan en el primer autor, el registro queda `CONFLICTO_IDENTIDAD`.

### Estados posibles

- `RESUMEN_RECUPERADO`, con su `nivel_identidad`: pasa al cribado normal (A1).
- `SIN_RESUMEN_TRAS_A2A`: pasa a la fase manual A2b.
- `CONFLICTO_IDENTIDAD`: pasa a A2b.
- `ERROR_ACCESO`: alguna consulta falló de forma reintentable (red, 429, 5xx) o no se pudo leer. Se reintenta repitiendo el comando, y **nunca cuenta como «sin resumen»**. Un 404 es una respuesta final (por ejemplo, S2 `match` sin coincidencia) y no se trata como fallo.

## Trazabilidad

Es la misma de A0 v1.1, con las correcciones de la [auditoría de Argon](https://github.com/jaiborojas-cloud/leviathan/pull/148):
- Cada respuesta cruda se guarda en `raw/<sha(url)>/intento_NN.body`, con su SHA, la hora UTC real y la URL final.
- `meta.json` se persiste en cada intento, y los reintentos continúan la numeración sin sobrescribir.
- `IDENTIDAD.json` guarda la versión, el SHA del script, el del inventario y el de A0. Si no coinciden, la carpeta se rechaza.
- Cada candidato guarda el SHA de la consulta que lo produjo.
- Las fechas candidatas solo vienen de fuentes aceptadas.

**Cortesía:** se envía un User-Agent genérico, sin correo. Hay pausas por fuente (OpenAlex 0.5 s, Crossref 1 s, S2 1.1 s, arXiv 3 s) y se respeta `Retry-After`. Usa solo la biblioteca estándar de Python 3.12.

## Salidas

| Archivo | Contenido |
|---|---|
| `recuperacion_a2a.json` | Detalle por registro: consultas, candidatos y motivos de rechazo. |
| `recuperacion_a2a.csv` | Una fila por registro, con la fuente, el título, los autores, el año, los ids, el resumen y su SHA, y las fechas candidatas. |
| `RESUMEN_A2A.json` | Conteos por estado y por nivel de identidad. |

Código de salida: 0 si todo terminó, 2 si quedan registros `ERROR_ACCESO` y 1 si hay un error de insumo.

**Duración estimada:** entre 2 000 y 3 000 solicitudes, alrededor de 1 a 1.5 h. Se puede cortar con Ctrl+C y reanudar con el mismo comando. Los datos quedan **fuera de Git**.

| Archivo | SHA-256 |
|---|---|
| `recuperar_a2a.py` | `fcd78a0aa13c530bcb84e287e3b92284fcb0bdc04a6026a8009f276f36d837d0` |
| `pruebas_recuperar_a2a.py` | `17d39dc2d5f4395bb00ff3bb1e765c61b1d67e3321ea0968258c238e958de28e` |

**Pruebas:** pasan 23 de 23, sin red (el socket está bloqueado), en Linux con Python 3.13. Cubren:
- el ancla, los identificadores derivados y cada condición de aceptación;
- el nivel débil y el conflicto de autores;
- el ancla con título discordante;
- un fallo parcial que queda `ERROR_ACCESO` y un reintento desde la caché;
- un 404 de `match` que no cuenta como fallo;
- la búsqueda en arXiv;
- los SHA, la identidad de salida y el registro ausente;
- que no decide pertinencia;
- `.gitattributes`;
- las regresiones de la auditoría: apellidos no latinos, candidato anónimo rechazado, conflicto entre fuentes en el nivel débil, año de respaldo y nombre de autor en Crossref, consulta de arXiv y guion bajo.

Falta confirmarlas en Windows.

## Procedimiento (una ventana nueva de PowerShell, un solo bloque)

```powershell
$ErrorActionPreference = 'Stop'
$Repo = 'D:\leviathan-q15-a2a'
$Rev = '<COMMIT_AUDITADO>'
if (-not (Test-Path $Repo)) {
    git -c core.autocrlf=false clone --no-checkout https://github.com/jaiborojas-cloud/leviathan.git $Repo
    git -C $Repo config core.autocrlf false
    git -C $Repo checkout --detach $Rev
}
if ((git -C $Repo rev-parse HEAD) -ne $Rev) { throw 'Clon en otro commit: usa otra carpeta $Repo' }
$Py = 'D:\RIPG_DATA\venv_q15\Scripts\python.exe'
$Dir = Join-Path $Repo 'docs\research-notes\Q15\ejecucion\recuperacion_A2a'
$Script = Join-Path $Dir 'recuperar_a2a.py'
$Suite = Join-Path $Dir 'pruebas_recuperar_a2a.py'
$H1 = (Get-FileHash $Script -Algorithm SHA256).Hash.ToLower()
$H2 = (Get-FileHash $Suite -Algorithm SHA256).Hash.ToLower()
if ($H1 -ne 'fcd78a0aa13c530bcb84e287e3b92284fcb0bdc04a6026a8009f276f36d837d0') { throw 'SHA script' }
if ($H2 -ne '17d39dc2d5f4395bb00ff3bb1e765c61b1d67e3321ea0968258c238e958de28e') { throw 'SHA pruebas' }
& $Py -I $Suite
if ($LASTEXITCODE -ne 0) { throw 'Pruebas fallaron: copia la salida' }
$Inv = 'D:\RIPG_DATA\Q15_A0\insumo\INVENTARIO_857.json'
$A0 = 'D:\RIPG_DATA\Q15_A0\salida\recuperacion_a0.json'
$Out = 'D:\RIPG_DATA\Q15_A2a\salida'
$PSNativeCommandUseErrorActionPreference = $false
& $Py -I $Script --inventario $Inv --a0 $A0 --out $Out --limite 5
"Prueba con 5 registros, código: $LASTEXITCODE"
```

Si la prueba con 5 registros sale bien (código 0 o 2, sin errores rojos), corre los 595 sobre **la misma carpeta**:

```powershell
& $Py -I $Script --inventario $Inv --a0 $A0 --out $Out
"Código: $LASTEXITCODE"
```

Si el código es 2, repite el mismo comando: solo se reintentan las consultas que fallaron. Al final se entregan `RESUMEN_A2A.json`, `recuperacion_a2a.csv` y `recuperacion_a2a.json`, con sus SHA, para la auditoría y para el cribado A1.
