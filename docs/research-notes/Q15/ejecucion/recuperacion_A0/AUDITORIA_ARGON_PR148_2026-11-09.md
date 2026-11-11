# Auditoría de Código: PR #148 (Ejecutor A0 de recuperación de resúmenes para Q15)

- **Fecha:** 2026-11-09
- **Auditor:** Argon
- **Autor del PR:** Claude
- **PR auditado:** `#148` (`q15: ejecutor A0 de recuperación de resúmenes por DOI/arXiv`)
- **Commit auditado:** `6a4a72677870bf24b41eaf5c6917361152acca5b` (`6a4a7267`, padre `43829f66`)
- **Archivos en alcance del PR:**
  - `docs/research-notes/Q15/ejecucion/recuperacion_A0/README.md` (72 líneas)
  - `docs/research-notes/Q15/ejecucion/recuperacion_A0/recuperar_a0.py` (370 líneas, SHA-256 con LF: `97d2f0e3bd0ad100eca7784c60ab7571a714fe69705ee833cf711733b1adffa2`)
  - `docs/research-notes/Q15/ejecucion/recuperacion_A0/pruebas_recuperar_a0.py` (199 líneas, SHA-256 con LF: `c3685c3ae924b245960edd21053c332a681a5613248700beb777d8f4e4890904`)
- **Método:** Revisión estática de código, sin ejecutar la suite de pruebas (`pruebas_recuperar_a0.py`), conforme a `AGENTS.md`.

---

## 1. Verificación de los 4 criterios solicitados

### A. ¿Solo acepta resúmenes con título coincidente? — **CUMPLE (con observación menor M1 sobre títulos vacíos)**
- **Normalización (`recuperar_a0.py`, líneas 56–62):** `normalizar_titulo(t)` elimina etiquetas HTML (`re.sub(r"<[^>]+>", " ", t)`), desescapa entidades (`html.unescape`), aplica descomposición Unicode `NFKD` eliminando marcas diacríticas (`unicodedata.combining`), pasa a `casefold()` y conserva únicamente caracteres alfanuméricos `[0-9a-z]`.
- **Comprobación de coincidencia (`recuperar_a0.py`, líneas 260 y 276–281):**
  ```python
  titulo_inv = normalizar_titulo(reg.get("titulo"))
  ...
  coincide = bool(q.get("titulo")) and normalizar_titulo(q.get("titulo")) == titulo_inv
  q["titulo_coincide"] = coincide
  if q.get("resumen"):
      q["resumen_sha256"] = sha256_bytes(q["resumen"].encode("utf-8"))
      (resumenes if coincide else discordantes).append(q["fuente"])
  ```
- **Asignación de estado y exportación (`recuperar_a0.py`, líneas 282–289 y 324):**
  - El estado `RESUMEN_RECUPERADO` se asigna **únicamente** si `resumenes` (`fuentes_con_resumen_coincidente`) no está vacío (líneas 282–283).
  - Si hay resúmenes pero ninguno tiene `coincide == True`, `resumenes` queda vacío, `discordantes` no está vacío y el registro pasa a `CONFLICTO_IDENTIDAD` (líneas 284–285).
  - En `exportar()` (línea 324), la columna `resumen` del CSV toma exclusivamente la primera fuente de `fuentes_con_resumen_coincidente`; si no hay coincidencia, escribe cadena vacía `""`.

### B. ¿No decide pertinencia ni fechas? — **CUMPLE**
- **Sin decisiones de pertinencia (`recuperar_a0.py`, líneas 257–294):** El código solo emite estados operativos de recuperación: `SIN_IDENTIFICADOR` (línea 264), `RESUMEN_RECUPERADO` (línea 283), `CONFLICTO_IDENTIDAD` (línea 285), `ERROR_ACCESO` (línea 287) y `SIN_RESUMEN_EN_FUENTES` (línea 289). No contiene reglas temáticas, palabras clave ni llamadas a modelos para clasificar `INCLUIR_PARA_TEXTO`, `EXCLUIR_FUERA_TEMA` o `CONTEXTO`.
- **Sin adjudicación de fechas (`recuperar_a0.py`, líneas 189, 210, 227, 249 y 325):**
  - OpenAlex guarda `{"publication_date": ...}` (línea 189); Crossref guarda `{"created", "published-online", "published-print", "issued", "posted"}` (línea 210); S2 guarda `{"publicationDate", "year"}` (línea 227); arXiv guarda `{"published_v1": g("published"), "updated": g("updated")}` (línea 249).
  - Ninguna función compara fechas contra el corte temporal ni cambia `estado_propuesto` según la fecha; `exportar()` simplemente serializa el diccionario de fechas por fuente en `fechas_json` (líneas 325 y 328).
  - *(Ver Hallazgo Medio H2 sobre la recolección de `fechas_json` cuando una fuente tiene título discordante).*

### C. ¿Conserva todos los intentos? — **CUMPLE (con observación H1 ante `Ctrl+C` en mitad de un backoff)**
- **Numeración incremental sin sobrescritura (`recuperar_a0.py`, líneas 124–171):**
  - Para cada URL (`clave = sha256_bytes(url.encode())`), si `meta.json` ya existe y `"final"` es `True`, reutiliza la caché sin hacer red (líneas 128–132).
  - Si `meta.json` existe con `"final": False` (por ejemplo, tras fallos transitorios en una corrida previa), carga los intentos previos (`previos = json.loads(...)["intentos"]`, línea 133) y define `base_n = len(previos)` (línea 134).
  - En el bucle de reintentos (`for n in range(self.reintentos + 1)`), cada respuesta se escribe atómicamente en `d / f"intento_{base_n + n + 1:02d}.body"` (líneas 152–153) y se añade a la lista `intentos` con su `n`, `fecha_utc_real`, `status`, `error`, `url_final`, ruta relativa POSIX `cuerpo`, `sha256` y `bytes` (líneas 154–157).
  - En flujo normal de terminación del bucle, nunca se trunca ni sobrescribe un `intento_NN.body` anterior, ni dentro de una misma ejecución (ante `status is None`, `429` o `>= 500`, línea 158) ni al reanudar el script en una ejecución posterior.

### D. ¿El bloque de PowerShell es correcto? — **TIENE UN BLOQUEANTE EN WINDOWS (`.gitattributes` / CRLF)**

---

## 2. Hallazgos

### [BLOQUEANTE - B1] Falta regla `-text` en `.gitattributes` para `recuperacion_A0`: el bloque de PowerShell abortará en Windows por discrepancia de SHA-256 (`CRLF` vs `LF`)
- **Ubicación:** `.gitattributes` (en el commit `6a4a7267`) y `docs/research-notes/Q15/ejecucion/recuperacion_A0/README.md` (líneas 36–39 y 52–59).
- **Evidencia:**
  - En `README.md` (líneas 58–59), el bloque de PowerShell clona el repositorio en Windows (`git clone --no-checkout ...` + `git -C $Repo checkout --detach $Rev`) y verifica:
    ```powershell
    if ((Get-FileHash $Script -Algorithm SHA256).Hash.ToLower() -ne '97d2f0e3bd0ad100eca7784c60ab7571a714fe69705ee833cf711733b1adffa2') { throw 'SHA del script' }
    if ((Get-FileHash $Suite -Algorithm SHA256).Hash.ToLower() -ne 'c3685c3ae924b245960edd21053c332a681a5613248700beb777d8f4e4890904') { throw 'SHA de las pruebas' }
    ```
  - Esos dos hashes SHA-256 corresponden a los archivos con saltos de línea **LF**. Con **CRLF** (como los convierte Git por defecto en Windows cuando `core.autocrlf=true`), los hashes cambian a:
    - `recuperar_a0.py` (CRLF): `161c0050e296017266d9551bf5be537cc98090589d651f7447a52305f3702aa7`
    - `pruebas_recuperar_a0.py` (CRLF): `d673f3a0f0e4979f4749e7dd7bf62cd144d688b729851be86136d0fca6ce118f`
  - En `.gitattributes` (líneas 1–10 del commit `6a4a7267`) se incluyó `docs/research-notes/Q15/ejecucion/cribado_llm/** -text` (añadido en el PR #144 / commit `da077abb` precisamente por este mismo fallo en Windows), pero **no se añadió `docs/research-notes/Q15/ejecucion/recuperacion_A0/** -text`**.
  - Además, `recuperar_a0.py` (línea 353) guarda `sha256_file(Path(__file__))` dentro de `IDENTIDAD.json`, por lo que el hash del script en disco también queda atado al fin de línea del checkout.
- **Corrección requerida:** Añadir `docs/research-notes/Q15/ejecucion/recuperacion_A0/** -text` en `.gitattributes` (tal como se hizo en `da077abb` para `cribado_llm`).

### [MEDIO - H1] Interrupción con `Ctrl+C` (`KeyboardInterrupt`) durante el backoff de reintento deja `intento_NN.body` en disco sin actualizar `meta.json`
- **Ubicación:** `docs/research-notes/Q15/ejecucion/recuperacion_A0/recuperar_a0.py`, líneas 133–171, y `README.md`, línea 33.
- **Evidencia:**
  - `README.md` (línea 33) indica: *"Se puede cortar con Ctrl+C y reanudar con el mismo comando"*.
  - En `Cliente.get` (línea 148), el bloque `try ... except Exception as ex:` captura subclases de `Exception`, mientras que `KeyboardInterrupt` hereda de `BaseException`.
  - Si una solicitud devuelve un error transitorio (por ejemplo, `429` o `503`), el código escribe `intento_01.body` en disco (línea 153) y luego duerme en `self._dormir(espera)` (línea 169) **antes** de escribir `meta.json` (línea 170, que está fuera del bucle `for`).
  - Si el usuario presiona `Ctrl+C` durante ese `self._dormir(espera)` (o durante el segundo intento), `meta.json` no se habrá escrito (o conservará el `intentos` de una corrida anterior). Al reanudar, `base_n = len(previos)` (línea 134) será `0` y sobrescribirá `intento_01.body`.
- **Recomendación:** Persistir `meta.json` atómicamente dentro de cada iteración del bucle (inmediatamente después de escribir `cuerpo_p` y añadir `intento` a `intentos`), con `"final": not transitorio`. De ese modo, `meta.json` y los archivos `intento_NN.body` están siempre sincronizados aunque el proceso se corte con `Ctrl+C`.

### [MEDIO - H2] `exportar()` incluye en `fechas_json` del CSV las fechas de todas las fuentes que respondieron, incluso aquellas cuyo título no coincidió (`titulo_coincide == False`)
- **Ubicación:** `docs/research-notes/Q15/ejecucion/recuperacion_A0/recuperar_a0.py`, línea 325.
- **Evidencia:**
  - En `exportar()` (líneas 324–325):
    ```python
    fuente = next((q for q in r["fuentes"] if q["fuente"] in r.get("fuentes_con_resumen_coincidente", [])), None)
    fechas = {q["fuente"]: q.get("fechas") for q in r["fuentes"] if q.get("fechas")}
    ```
  - Mientras que `fuente` (para el resumen) exige que el título haya coincidido, `fechas` recolecta `q.get("fechas")` de cualquier fuente en `r["fuentes"]`, sin filtrar por `q.get("titulo_coincide")`.
  - Si un DOI en una de las fuentes apunta a una obra distinta (`titulo_coincide == False`), sus fechas quedan igualmente incluidas en la columna `fechas_json` de `recuperacion_a0.csv`. (En `recuperacion_a0.json` sí está explícito `"titulo_coincide": false` dentro de cada elemento de `"fuentes"`).
- **Recomendación:** Filtrar `fechas` en `exportar()` por `if q.get("fechas") and q.get("titulo_coincide")`, para que `fechas_json` en el CSV solo contenga fechas de fuentes cuya identidad por título coincidió con el inventario.

### [MENOR - M1] `normalizar_titulo` podría evaluar `"" == ""` si el título quedara vacío tras normalizar
- **Ubicación:** `docs/research-notes/Q15/ejecucion/recuperacion_A0/recuperar_a0.py`, líneas 56–62, 260 y 276.
- **Evidencia:**
  - En la línea 276: `coincide = bool(q.get("titulo")) and normalizar_titulo(q.get("titulo")) == titulo_inv`.
  - Si `titulo_inv` fuera `""` (por ejemplo, un título compuesto exclusivamente por caracteres no latinos o símbolos que `re.sub(r"[^0-9a-z]+", "", ...)` vacía) y `q.get("titulo")` también fuera una cadena no vacía de caracteres no latinos/símbolos, ambos normalizarían a `""` y `coincide` daría `True`.
- **Recomendación:** Asegurar que ambos títulos normalizados sean no vacíos:
  ```python
  titulo_f = normalizar_titulo(q.get("titulo"))
  coincide = bool(titulo_inv) and bool(titulo_f) and titulo_f == titulo_inv
  ```

### [MENOR - M2] Reejecución del bloque de PowerShell si la carpeta `$Repo` ya existe de un intento previo
- **Ubicación:** `docs/research-notes/Q15/ejecucion/recuperacion_A0/README.md`, líneas 52–56.
- **Evidencia:**
  ```powershell
  if (-not (Test-Path $Repo)) {
      git clone --no-checkout https://github.com/jaiborojas-cloud/leviathan.git $Repo
      git -C $Repo checkout --detach $Rev
  }
  if ((git -C $Repo rev-parse HEAD) -ne $Rev) { throw 'El clon no está en el commit auditado' }
  ```
  - Si `git clone` fallara a mitad de camino después de crear `$Repo`, o si se actualizara `$Rev` tras un nuevo commit, `Test-Path $Repo` será `True` y abortará en `rev-parse HEAD`. Es un comportamiento seguro (*fail-closed*), pero conviene tener presente que tras actualizar `$Rev` o ante un clon interrumpido habría que borrar `$Repo` o hacer `git -C $Repo fetch origin; git -C $Repo checkout --detach $Rev`.

---

## 3. Veredicto

- **Lógica científica y de protocolo:** Cumple con aceptar resúmenes solo con título coincidente, no decidir pertinencia ni fechas, y preservar todos los intentos crudos con SHA-256.
- **Estado de aprobación:** **Requiere corrección previa a ejecución** de **B1** (`.gitattributes` con `-text` para `docs/research-notes/Q15/ejecucion/recuperacion_A0/**`), recomendando incluir en el mismo commit las mejoras **H1**, **H2** y **M1**.
