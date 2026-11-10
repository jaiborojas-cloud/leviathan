# Reauditoría Independiente de Código: PR #150 (Ejecutor A2a de recuperación de resúmenes para Q15, v1.1)

- **Fecha:** 2026-11-10
- **Auditor:** Argon
- **Autor del PR:** Claude
- **PR auditado:** `#150` (`Q15 A2a: segunda recuperación automática de resúmenes (ancla S2, ids derivados, búsqueda por título con identidad estricta)`)
- **Commit reauditado:** `2e41199f9d8de039476a632b3ac6908781b85bde` (`2e41199f`, padre `081021ba7973983ea473e1e375448df3d97a8209`)
- **Archivos en alcance del commit `2e41199f` (SHAs con LF verificados):**
  - `docs/research-notes/Q15/ejecucion/recuperacion_A2a/AUDITORIA_ARGON_PR150_2026-11-10.md` (188 líneas, SHA-256 LF: `c3550af617ea4abf6996d596cb406438aa20e92985b7618e68dab59678791a44`)
  - `docs/research-notes/Q15/ejecucion/recuperacion_A2a/README.md` (121 líneas, SHA-256 LF: `7af4512f1f95375c94decfb92a1d55a8f32c7fbd226807bb1025e9d407561943`)
  - `docs/research-notes/Q15/ejecucion/recuperacion_A2a/recuperar_a2a.py` (`VERSION = "A2a-1.1"`, 567 líneas, SHA-256 LF: `fcd78a0aa13c530bcb84e287e3b92284fcb0bdc04a6026a8009f276f36d837d0`)
  - `docs/research-notes/Q15/ejecucion/recuperacion_A2a/pruebas_recuperar_a2a.py` (288 líneas, 23 pruebas, SHA-256 LF: `17d39dc2d5f4395bb00ff3bb1e765c61b1d67e3321ea0968258c238e958de28e`)
- **Método:** Revisión estática de código y verificación de blobs/hashes en el árbol de Git, sin ejecutar las pruebas ni usar la red para las APIs bibliográficas, conforme a `AGENTS.md`.

---

## 1. Verificación del cierre de hallazgos (`081021ba` -> `2e41199f`)

### 1. [ALTO - A1] Apellidos en alfabetos no latinos, rechazo de candidatos anónimos en búsqueda y consulta de todas las fuentes cuando falta autor de referencia — **CERRADO**
- **Apellidos en cualquier alfabeto (`recuperar_a2a.py`, líneas 85–92):**
  ```python
  def apellido(nombre: str | None) -> str:
      """Último token alfabético del nombre, plegado (sin acentos, minúsculas)."""
      if not nombre:
          return ""
      plegado = _plegar(nombre)
      # Alfabeto latino tras plegar; si no hay, tokens de letras en cualquier alfabeto (A1 de Argon).
      toks = re.findall(r"[a-z]+", plegado) or re.findall(r"[^\W\d_]+", plegado)
      return toks[-1] if toks else ""
  ```
- **Rechazo de candidatos sin primer autor identificable (`recuperar_a2a.py`, líneas 438–442):**
  ```python
  ap_k = apellido((k.get("autores") or [None])[0])
  if (ap_ref and ap_k != ap_ref) or not ap_k:
      motivo.append("primer_autor")
  ```
  Ahora ningún candidato de búsqueda anónimo (`autores: []` o sin letras) puede ser aceptado ni siquiera en el nivel débil `ID_TA`.
- **Consulta de todas las fuentes sin `ap_ref` y detección de conflicto entre fuentes (`recuperar_a2a.py`, líneas 447–461):**
  ```python
  for fn in (q_openalex_busqueda, q_crossref_busqueda, q_s2_match, q_arxiv_busqueda):
      nuevos = correr(fn(c, titulo))
      for k in nuevos:
          juzgar(k)
      busq += nuevos
      if ap_ref and any(k["aceptado"] and k.get("resumen") for k in busq):
          break
  ok = [k for k in busq if k["aceptado"] and k.get("resumen")]
  if ok:
      if not ap_ref and len({apellido((k.get("autores") or [None])[0]) for k in ok}) > 1:
          res["estado_propuesto"] = "CONFLICTO_IDENTIDAD"
  ```
  Con `ap_ref` se detiene en la primera fuente que recupera resumen; sin `ap_ref` consulta las 4 fuentes y si dos candidatos aceptados (dentro de una fuente o entre fuentes distintas) difieren en `apellido`, marca `CONFLICTO_IDENTIDAD`.
- **Pruebas unitarias (`pruebas_recuperar_a2a.py`, líneas 249–268):** Cubierto por `test_a1_apellido_no_latino`, `test_a1_candidato_anonimo_se_rechaza_en_nivel_debil` y `test_a1_conflicto_entre_fuentes_en_nivel_debil`.

### 2. [MEDIO - M1] Respaldo de año en Crossref (`issued`, `published-print`, `published-online`, `posted`, `created`) — **CERRADO**
- **`recuperar_a2a.py` (líneas 252–254):**
  ```python
  "anio": next((anio(fechas.get(k)) for k in ("issued", "published-print", "published-online", "posted", "created")
                if anio(fechas.get(k))), None),
  ```
- **Prueba unitaria (`pruebas_recuperar_a2a.py`, líneas 270–274):** Cubierto por `test_m1_b1_crossref_anio_de_respaldo_y_nombre`.

### 3. [MEDIO - M2] Consulta de búsqueda en arXiv por tokens `ti:tok1 AND ti:tok2` sin palabras reservadas — **CERRADO**
- **`recuperar_a2a.py` (líneas 336–349):**
  ```python
  RESERVADAS_ARXIV = {"and", "or", "not", "andnot"}

  def consulta_arxiv(t: str) -> str:
      toks = [w for w in texto_busqueda(t).split() if len(w) > 2 and w.lower() not in RESERVADAS_ARXIV][:12]
      return " AND ".join("ti:" + w for w in toks)
  ```
  Elimina operadores reservados de Lucene y une hasta 12 tokens de más de 2 caracteres con `AND`, manteniendo intacta la exigencia de título normalizado idéntico, año ±1 y primer autor en `juzgar(k)`.
- **Prueba unitaria (`pruebas_recuperar_a2a.py`, líneas 276–278):** Cubierto por `test_m2_b2_consulta_arxiv_y_guion_bajo`.

### 4. [BAJO - B1] Respaldo `a.get("name")` en autores de Crossref — **CERRADO**
- **`recuperar_a2a.py` (líneas 249–250):**
  ```python
  "autores": [(" ".join(x for x in (a.get("given"), a.get("family")) if x) or a.get("name") or "").strip()
              for a in j.get("author") or []],
  ```
- **Prueba unitaria (`pruebas_recuperar_a2a.py`, líneas 270–274):** Cubierto por `test_m1_b1_crossref_anio_de_respaldo_y_nombre`.

### 5. [BAJO - B2] Reemplazo de guion bajo (`_`) en `texto_busqueda` — **CERRADO**
- **`recuperar_a2a.py` (línea 104):**
  ```python
  return re.sub(r"\s+", " ", re.sub(r"[\W_]+", " ", t)).strip()
  ```
- **Prueba unitaria (`pruebas_recuperar_a2a.py`, línea 277):** Cubierto por `test_m2_b2_consulta_arxiv_y_guion_bajo`.

### 6. [BAJO - B3] Orden de fuentes en el docstring — **CERRADO**
- **`recuperar_a2a.py` (línea 13):**
  ```python
  3. Búsqueda por título en OpenAlex, Crossref, S2 (match) y arXiv.
  ```
  Coincide con la línea 447 del código y la línea 26 del `README.md`.

---

## 2. Búsqueda de regresiones y verificación de integridad

- **Versión e identidad:** `VERSION = "A2a-1.1"` (`recuperar_a2a.py`, línea 41).
- **Hashes SHA-256 en `README.md` (líneas 67–68 y 102–103):**
  - `recuperar_a2a.py`: `fcd78a0aa13c530bcb84e287e3b92284fcb0bdc04a6026a8009f276f36d837d0` — **coincide** con el blob LF del commit `2e41199f`.
  - `pruebas_recuperar_a2a.py`: `17d39dc2d5f4395bb00ff3bb1e765c61b1d67e3321ea0968258c238e958de28e` — **coincide** con el blob LF del commit `2e41199f`.
  - `AUDITORIA_ARGON_PR150_2026-11-10.md`: `c3550af617ea4abf6996d596cb406438aa20e92985b7618e68dab59678791a44` — archivado sin modificaciones.
- **Compatibilidad de las pruebas existentes con el cambio en A1:** En `pruebas_recuperar_a2a.py` (líneas 164–181), `test_sin_ancla_nivel_debil_y_conflicto_de_autores` y `test_ancla_con_titulo_distinto_no_aporta_autores` usan `FakeNet`, que para las fuentes no listadas devuelve `404, {}, b"{}", url` (línea 41). Como `404` no es fallo transitorio (`st == 404` no entra en `fallos`), consultar las 4 fuentes cuando `ap_ref == ""` no introduce falsos `ERROR_ACCESO` y mantiene verdes las 23 pruebas.
- **Caso extremo de `consulta_arxiv(t)` vacío:** Si un título solo tuviera palabras de $\le 2$ letras o reservadas, `consulta_arxiv(t)` devolvería `""`, que en arXiv devuelve un feed Atom vacío (`200 OK` con 0 `<entry>`), sin provocar fallo ni excepción.

---

## 3. Veredicto

- **Hallazgos pendientes:** **Ninguno (0 bloqueantes, 0 altos, 0 medios, 0 bajos).**
- **Estado:** **APROBADO** sobre el commit `2e41199f9d8de039476a632b3ac6908781b85bde` (`2e41199f`, v1.1). En el bloque de PowerShell basta con sustituir `<COMMIT_AUDITADO>` por `2e41199f9d8de039476a632b3ac6908781b85bde`.
