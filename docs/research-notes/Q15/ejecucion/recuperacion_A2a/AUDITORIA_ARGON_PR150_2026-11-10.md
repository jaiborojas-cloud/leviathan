# Auditoría Independiente de Código: PR #150 (Ejecutor A2a de recuperación de resúmenes para Q15)

- **Fecha:** 2026-11-10
- **Auditor:** Argon
- **Autor del PR:** Claude
- **PR auditado:** `#150` (`Q15 A2a: segunda recuperación automática de resúmenes (ancla S2, ids derivados, búsqueda por título con identidad estricta)`)
- **Commit auditado:** `081021ba7973983ea473e1e375448df3d97a8209` (`081021ba`, padre `43829f664a13568c8ddbe116b0e4e6d0b745508b`)
- **Archivos en alcance del PR (SHAs con LF verificados):**
  - `.gitattributes` (2 líneas añadidas, blob `dce5bc18a8dc883e6ccad3e531d43954568946c6`)
  - `docs/research-notes/Q15/ejecucion/recuperacion_A2a/README.md` (118 líneas, SHA-256 LF: `4d56c5b9b721076ff052bf4a411cc1db81f65223cbd63369132514722b9a3ca4`)
  - `docs/research-notes/Q15/ejecucion/recuperacion_A2a/recuperar_a2a.py` (546 líneas, SHA-256 LF: `fd1c7193f9826f2b7a0fb0848268000caba8cd2553441017e29ef4627ad5ca89`)
  - `docs/research-notes/Q15/ejecucion/recuperacion_A2a/pruebas_recuperar_a2a.py` (256 líneas, SHA-256 LF: `d1425f15750b74b6199af774fd7ca2b24f60d3bbbae827e1f82614c063283325`)
- **Método:** Revisión estática del código, sin ejecutar pruebas ni red, conforme a `AGENTS.md`.

---

## 1. Revisión de los 5 puntos solicitados

### 1. Identidad: ancla S2, ids derivados y las tres condiciones de la búsqueda — ¿Puede aceptar un resumen de otra obra?
- **Ancla S2 (`recuperar_a2a.py`, líneas 138–143, 297–299, 364 y 380–394):**
  - Extrae el `paperId` hexadecimal de 40 caracteres de `url_snapshot` (`S2_ID`).
  - Consulta `graph/v1/paper/{pid}` y verifica `k["titulo_coincide"] = bool(tnorm) and normalizar_titulo(k.get("titulo")) == tnorm` (línea 364).
  - Si `cands[0].get("titulo_coincide")` es `False` (o si `tnorm` es vacío), el registro S2 **no** se usa como ancla (`ancla = None`), no aporta autores ni IDs derivados, no se marca `aceptado` y deja constancia en `nota_ancla` (líneas 386–387).
- **IDs derivados del ancla (`recuperar_a2a.py`, líneas 396–407):**
  - Solo se consultan si `ancla` fue validada por título (`if ancla:`, línea 396) y el DOI o arXiv es distinto del que ya tenía el snapshot (líneas 400 y 402).
  - Cada candidato derivado exige `k["aceptado"] = k["titulo_coincide"]` (línea 405) antes de poder aceptarse con nivel `ID_DERIVADO_DEL_ANCLA`.
- **Tres condiciones en búsqueda por título (`recuperar_a2a.py`, líneas 413–443):**
  - En `juzgar(k)` (líneas 415–425), un candidato de búsqueda solo recibe `k["aceptado"] = True` si simultáneamente:
    - **(a) Título normalizado idéntico:** `not k["titulo_coincide"]` → rechaza con `"titulo"`.
    - **(b) Año compatible a ±1 del snapshot:** `anio_snap is None or a is None or abs(a - anio_snap) > 1` → rechaza con `"anio"`. Si falta el año en el snapshot o en el candidato, rechaza (comportamiento *fail-closed*). *(Ver Hallazgo Medio M1 sobre el año en Crossref cuando la fecha está en `published-online`/`published-print`/`created`/`posted` pero no en `issued`, y Hallazgo Bajo B1 sobre formatos de `author` en Crossref).*
    - **(c) Primer autor:** si el ancla dio autores (`ap_ref`), compara `apellido((k.get("autores") or [None])[0]) != ap_ref` → rechaza con `"primer_autor"`.
- **¿Puede aceptar un resumen de otra obra? (Ver Hallazgo Alto A1):**
  - Cuando **hay** autor de referencia con apellido ASCII (`ap_ref != ""`), las tres condiciones (`título idéntico` + `año ±1` + `apellido del primer autor`) impiden aceptar una obra ajena salvo homonimia exacta del mismo autor en el mismo año (±1).
  - Sin embargo, existen **dos casos de borde** en la verificación del primer autor (detallados en **Hallazgo Alto A1**):
    1. En el nivel débil (`ap_ref == ""`), si una fuente devuelve varios candidatos aceptados con primer autor distinto (`len({apellido(...) for k in ok}) > 1`), la línea 437 detecta `CONFLICTO_IDENTIDAD`; pero como el bucle de las líneas 428–434 hace `break` en la primera fuente que devuelve al menos un candidato con resumen (p. ej. OpenAlex), **no compara contra el primer autor de las demás fuentes**, y además si un candidato aceptado viene sin lista de autores (`autores: []`), su `apellido(None)` es `""`.
    2. `apellido()` (líneas 85–90) usa `re.findall(r"[a-z]+", _plegar(nombre))`. Si el primer autor del ancla o del candidato está en alfabeto no latino (coreano, chino, japonés, cirílico, etc.), `apellido()` devuelve `""`, desactivando silenciosamente la condición (c) de primer autor (`ap_ref = ""`) o haciendo que dos autores no latinos distintos colisionen en `"" == ""`.

### 2. Que nunca cuente un fallo como "sin resumen" (`ERROR_ACCESO`) y que un 404 de S2 `match` no sea fallo
- **CUMPLE:**
  - En `correr()` (`recuperar_a2a.py`, líneas 360–362):
    ```python
    st = q["status"]
    if st is None or st == 429 or st >= 500 or q.get("error_parseo"):
        fallos.append(q)
    ```
  - En `_cerrar()` (`recuperar_a2a.py`, líneas 452–453):
    ```python
    if res["estado_propuesto"] != RECUPERADO and fallos:
        res["estado_propuesto"] = "ERROR_ACCESO"
    ```
  - Por tanto, si un registro no alcanza `RESUMEN_RECUPERADO` y ocurrió cualquier error de red/timeout (`st is None`), `429`, `5xx` o `error_parseo` en **cualquiera** de las etapas (ancla, IDs derivados o búsqueda), el estado final nunca queda como `SIN_RESUMEN_TRAS_A2A` ni `CONFLICTO_IDENTIDAD`, sino que pasa a `ERROR_ACCESO` y `main()` devuelve código de salida `2` (línea 542).
  - Un `404` (como el que devuelve Semantic Scholar `paper/search/match` cuando no hay coincidencia, o un DOI inexistente) tiene `st == 404`: en `Cliente.get` `transitorio` es `False` (línea 204), se marca `"final": True` en caché y en `correr()` **no** se agrega a `fallos`.

### 3. Caché, reintentos e identidad de salida (correcciones heredadas de A0)
- **CUMPLE en los 5 puntos corregidos en A0 v1.1:**
  - **CRLF / `.gitattributes`:** `.gitattributes` (líneas 12–13) declara `docs/research-notes/Q15/ejecucion/recuperacion_A2a/** -text`, y el bloque de PowerShell en `README.md` (líneas 88–90) clona con `-c core.autocrlf=false`. Los hashes SHA-256 publicados en `README.md` (líneas 65–66 y 99–100) coinciden exactamente con los blobs LF del commit `081021ba`.
  - **Ctrl+C y cuerpos huérfanos en caché (`Cliente.get`, líneas 179–208):** Calcula `en_disco = [int(p.stem.split("_")[1]) for p in d.glob("intento_*.body")] if d.exists() else []` y `base_n = max([len(previos)] + en_disco)`, y escribe atómicamente `meta.json` en cada iteración del bucle antes de dormir en el backoff.
  - **Identidad de salida (`verificar_identidad`, líneas 462–472 y 524):** Persiste y verifica `IDENTIDAD.json` con `version`, `script_sha256`, `inventario_sha256` y `a0_sha256`.
  - **Fechas solo de fuentes aceptadas (`_cerrar`, líneas 454–456):** `acept = [k for k in res["candidatos"] if k.get("aceptado")]` y `res["fechas_candidatas"]` solo incluye candidatos con `k.get("aceptado") == True`.
  - **Títulos vacíos tras normalización (`evaluar_registro`, líneas 364 y 409–412):** `bool(tnorm)` impide coincidencias vacías `"" == ""` en las 3 etapas, y si `not tnorm` en la etapa 3 no ejecuta búsquedas por título. *(Ver Hallazgo Medio M2 para el caso en que `texto_busqueda(titulo)` quede vacío o con comas aunque `tnorm` no sea vacío).*

### 4. Construcción de URLs de búsqueda (escape, caracteres raros)
- Se revisaron `texto_busqueda` (líneas 100–102) y `q_openalex_busqueda`, `q_crossref_busqueda`, `q_arxiv_busqueda`, `q_s2_match` (líneas 317–339).
- Se identificaron dos detalles técnicos relevantes:
  1. **`q_arxiv_busqueda` (`recuperar_a2a.py`, líneas 330–333):** envuelve todo el título en comillas dobles (`ti:"..."`) sin eliminar stopwords de Lucene (`and`, `or`, `not`, `of`, `in`, `on`, `for`, `to`, `the`, `a`, `with`, `by`, `from`, `at`, `as`) ni limitar longitud; además, en la API clásica de arXiv (`export.arxiv.org/api/query`), las búsquedas de frase exacta entre comillas con muchos tokens o con palabras reservadas (`AND`, `OR`, `NOT`) frecuentemente devuelven 0 resultados aunque el preprint esté en arXiv (ver **Hallazgo Medio M2**).
  2. **`texto_busqueda` (`recuperar_a2a.py`, línea 102):** `re.sub(r"[^\w\s]", " ", t)` conserva el guion bajo `_` (porque `\w` incluye `_`) y conserva caracteres Unicode alfabéticos acentuados/no-ASCII, por lo que `replace(",", " ")` en la línea 319 es redundante, pero un `_` en el título no se reemplaza por espacio (ver **Hallazgo Bajo B2**).

### 5. Que no decida pertinencia ni fechas
- **CUMPLE:**
  - El script solo asigna `RESUMEN_RECUPERADO`, `SIN_RESUMEN_TRAS_A2A`, `CONFLICTO_IDENTIDAD` o `ERROR_ACCESO`. No evalúa relevancia temática ni filtra por ventana temporal de Q15; únicamente usa `abs(a - anio_snap) <= 1` como regla de identidad bibliográfica en la búsqueda por título y guarda todas las fechas de los candidatos aceptados en `fechas_candidatas`.

---

## 2. Hallazgos por severidad

### Bloques / Bloqueantes
- **Ninguno (0 bloqueantes).**

---

### Severidad Alta

#### [ALTO - A1] Condición de primer autor (`apellido`) se vacía con nombres no latinos o candidatos sin campo de autor en el nivel sin ancla (`ID_TA`)
- **Ubicación:** `docs/research-notes/Q15/ejecucion/recuperacion_A2a/recuperar_a2a.py`, líneas 85–90, 413, 422–423 y 437.
- **Descripción y evidencia:**
  1. En `apellido(nombre)` (líneas 85–90):
     ```python
     def apellido(nombre: str | None) -> str:
         if not nombre:
             return ""
         toks = re.findall(r"[a-z]+", _plegar(nombre))
         return toks[-1] if toks else ""
     ```
     Si el primer autor en `autores_ref` (del ancla S2) está escrito en caracteres no latinos (por ejemplo, coreano, chino, japonés o cirílico, que no se descomponen a `[a-z]` con `NFKD`), `apellido(autores_ref[0])` devuelve `""`. Entonces `ap_ref` queda `""` (línea 413) a pesar de que `autores_ref` **sí** tenía autor, y el registro:
     - no verifica la condición (c) en `juzgar(k)` (`if ap_ref and ...`, línea 422);
     - se clasifica al final como `ID_TA` (`BUSQUEDA_TITULO_ANIO_SIN_AUTOR_DE_REFERENCIA`, línea 442) en lugar de exigir coincidencia o declararse conflicto.
  2. Inversamente, en la línea 437 (cuando no hay `ap_ref`):
     ```python
     if not ap_ref and len({apellido((k.get("autores") or [None])[0]) for k in ok}) > 1:
     ```
     Si un candidato aceptado en `ok` trae `autores: []` (lista vacía, posible en Crossref/OpenAlex para registros incompletos), se acepta sin autor en `ID_TA`; y si dos candidatos distintos tienen primeros autores en alfabeto no latino, para ambos `apellido(...)` es `""`, por lo que el conjunto `{""}` tiene longitud 1 y **no** dispara `CONFLICTO_IDENTIDAD`.
- **Corrección propuesta:**
  - En `apellido()`, usar tokens alfanuméricos Unicode tras quitar puntuación (`re.findall(r"[^\W\d_]+", _plegar(nombre))`) para conservar apellidos en cualquier alfabeto si no son latinos:
    ```python
    def apellido(nombre: str | None) -> str:
        if not nombre:
            return ""
        plegado = _plegar(nombre)
        toks = re.findall(r"[a-z]+", plegado) or re.findall(r"[^\W\d_]+", plegado)
        return toks[-1] if toks else ""
    ```
  - En `juzgar(k)` (o al aceptar en búsqueda por título), exigir que el candidato de búsqueda tenga al menos un autor con apellido no vacío (`ap_cand = apellido((k.get("autores") or [None])[0])`; si `not ap_cand`, rechazar con `"primer_autor"` cuando hay `autores_ref`, o incluso siempre en búsqueda por título para no aceptar registros anónimos en `ID_TA`).

---

### Severidad Media

#### [MEDIO - M1] Crossref (`_cand_crossref`) toma `anio` únicamente de `issued`, ignorando `published-online`, `published-print`, `posted` y `created`
- **Ubicación:** `docs/research-notes/Q15/ejecucion/recuperacion_A2a/recuperar_a2a.py`, líneas 245–249.
- **Descripción y evidencia:**
  ```python
  fechas = {k: fecha(k) for k in ("created", "published-online", "published-print", "issued", "posted")}
  return {"fuente": "crossref", "via": via, "titulo": tit[0] if tit else None,
          "autores": [" ".join(x for x in (a.get("given"), a.get("family")) if x) for a in j.get("author") or []],
          "resumen": limpiar_jats(j.get("abstract")), "anio": anio(fechas.get("issued")),
          "fechas": fechas, "ids": {"doi": norm_doi(j.get("DOI")) or None}}
  ```
  En Crossref, ciertos preprints (`posted-content`) o artículos recién publicados en línea tienen `posted`, `published-online` o `created`, pero `issued` vacío (`None`). En ese caso `k["anio"]` queda `None` y `juzgar(k)` (línea 420) rechaza el candidato por `"anio"` aunque Crossref sí tenga el año en otra clave de `fechas`.
- **Corrección propuesta:**
  Usar fallback ordenado sobre las fechas propias de la publicación en Crossref:
  ```python
  anio_cr = next((anio(fechas.get(k)) for k in ("issued", "published-print", "published-online", "posted", "created") if anio(fechas.get(k))), None)
  ```

#### [MEDIO - M2] Consulta `q_arxiv_busqueda` con frase exacta `ti:"..."` en la API de arXiv falla cuando el título contiene operadores booleanos (`AND`, `OR`, `NOT`) o subtítulos largos
- **Ubicación:** `docs/research-notes/Q15/ejecucion/recuperacion_A2a/recuperar_a2a.py`, líneas 330–333.
- **Descripción y evidencia:**
  ```python
  def q_arxiv_busqueda(c, t):
      url = ("https://export.arxiv.org/api/query?max_results=10&search_query="
             + urllib.parse.quote('ti:"' + texto_busqueda(t) + '"'))
      return consultar(c, "arxiv", url, lambda c, m: _cands_arxiv(c.bytes(m), "busqueda"))
  ```
  El parser de `export.arxiv.org/api/query` interpreta `AND`, `OR`, `NOT` (e incluso en ocasiones palabras vacías o saltos de puntuación que arXiv indexa distinto del snapshot) de forma especial. Además, si `texto_busqueda(t)` elimina guiones o dos puntos (por ejemplo, LaTeX `$\ell_1$` o guiones compuestos), la frase exacta entre comillas `ti:"..."` puede no coincidir en el índice de arXiv aunque el candidato, una vez devuelto, sí pasaría `normalizar_titulo(k["titulo"]) == tnorm`.
- **Corrección propuesta:**
  Opcionalmente (si se desea mejorar la sensibilidad de la cuarta fuente de búsqueda sin relajar en absoluto `juzgar(k)`, que sigue exigiendo `normalizar_titulo` idéntico, año ±1 y primer autor), construir la consulta de arXiv con los tokens significativos (>2 letras, excluyendo `and`, `or`, `not` case-insensitive) unidos por `AND` en `ti:`, o mantener `ti:"..."` filtrando/escapando las palabras reservadas `AND`/`OR`/`NOT`.

---

### Severidad Baja

#### [BAJO - B1] `_cand_crossref` ignora `a.get("name")` cuando un autor en Crossref viene sin `given`/`family`
- **Ubicación:** `docs/research-notes/Q15/ejecucion/recuperacion_A2a/recuperar_a2a.py`, línea 247.
- **Descripción y evidencia:**
  ```python
  "autores": [" ".join(x for x in (a.get("given"), a.get("family")) if x) for a in j.get("author") or []],
  ```
  Cuando Crossref registra un autor con campo `"name"` (en vez de `"given"` y `"family"`), `" ".join(...)` produce `""`.
- **Corrección propuesta:**
  ```python
  "autores": [(" ".join(x for x in (a.get("given"), a.get("family")) if x) or a.get("name") or "").strip() for a in j.get("author") or []],
  ```

#### [BAJO - B2] `texto_busqueda` conserva guiones bajos (`_`) porque `\w` incluye `_`
- **Ubicación:** `docs/research-notes/Q15/ejecucion/recuperacion_A2a/recuperar_a2a.py`, líneas 100–102.
- **Descripción y evidencia:**
  ```python
  def texto_busqueda(t: str) -> str:
      t = html.unescape(re.sub(r"<[^>]+>", " ", t or ""))
      return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", t)).strip()
  ```
  Si un título tiene restos de LaTeX como `L_2` o `x_i`, `re.sub(r"[^\w\s]", " ", t)` conserva `L_2` con guion bajo.
- **Corrección propuesta:**
  Usar `re.sub(r"[\W_]+", " ", t)` en lugar de `re.sub(r"[^\w\s]", " ", t)`.

#### [BAJO - B3] Docstring inicial enumera el orden de búsqueda por título como `OpenAlex, Crossref, arXiv y S2 (match)`, mientras que el código y el `README.md` ejecutan `OpenAlex, Crossref, S2 (match) y arXiv`
- **Ubicación:** `docs/research-notes/Q15/ejecucion/recuperacion_A2a/recuperar_a2a.py`, líneas 13 vs 428 (`README.md` línea 26 coincide con la línea 428 del código).
- **Descripción:** Discrepancia cosmética en el docstring del módulo (línea 13 dice `OpenAlex, Crossref, arXiv y S2 (match)` y la línea 428 ejecuta `(q_openalex_busqueda, q_crossref_busqueda, q_s2_match, q_arxiv_busqueda)`). El orden real del código es mejor porque la pausa de S2 es 1.1 s frente a 3.0 s de arXiv.
- **Corrección propuesta:** Alinear la línea 13 del docstring con `OpenAlex, Crossref, S2 (match) y arXiv`.

---

## 3. Veredicto

- **Seguridad metodológica y trazabilidad:** El script **no tiene hallazgos bloqueantes**. Respeta todas las correcciones de A0 v1.1 (`.gitattributes` con `-text`, persistencia atómica de `meta.json` en cada intento resistente a `Ctrl+C`, no sobrescritura de cuerpos huérfanos, `IDENTIDAD.json`, `fechas_candidatas` solo de candidatos aceptados y protección contra títulos vacíos), nunca convierte un fallo transitorio o de parseo en «sin resumen» (`ERROR_ACCESO` con salida `2`), trata el `404` de S2 `match` como respuesta final sin fallo, y no decide pertinencia ni fechas.
- **Recomendación:**
  - Se recomienda corregir antes de la corrida completa al menos **A1** (apellidos no latinos y exigencia de apellido no vacío en candidato de búsqueda) y **M1** (fallback de año en Crossref), junto con los ajustes menores **B1–B3** si se edita el archivo (actualizando los SHA-256 en `README.md`).
  - Si el responsable decide correr `081021ba` tal cual porque la verificación de autores de los registros con nivel `BUSQUEDA_TITULO_ANIO_SIN_AUTOR_DE_REFERENCIA` ya está prevista obligatoriamente en A1 contra R4 (`README.md`, línea 31), el commit `081021ba7973983ea473e1e375448df3d97a8209` es **operativamente seguro en Windows**.
