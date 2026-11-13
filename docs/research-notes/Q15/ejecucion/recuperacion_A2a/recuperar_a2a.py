#!/usr/bin/env python3
"""Q15, fase A2a: segunda recuperación automática de resúmenes de autor, sin LLM.

Insumos (SHA verificados): INVENTARIO_857.json del plan de pendientes v1 y la salida de A0
(recuperacion_a0.json). Procesa solo los registros que A0 no recuperó.

Por registro, en este orden y deteniéndose al recuperar un resumen:
  1. Ancla S2: el paperId de la URL del snapshot se consulta en Semantic Scholar. El registro
     es el mismo del snapshot, así que su resumen se acepta si el título normalizado coincide.
     De ahí se toman autores, año e identificadores externos (DOI, arXiv) nuevos.
  2. Identificadores derivados del ancla: DOI nuevo en OpenAlex y Crossref; arXiv nuevo en la
     API de arXiv. Se acepta con título normalizado coincidente, como en A0.
  3. Búsqueda por título en OpenAlex, Crossref, S2 (match) y arXiv. Un candidato se acepta solo
     si (a) el título normalizado es idéntico, (b) el año es compatible (±1 con el snapshot) y
     (c) el apellido del primer autor coincide con el del ancla S2, cuando el ancla lo da. Si no
     hay autores de referencia, se acepta con nivel de identidad débil y A1 debe verificarlos;
     si los candidatos aceptados discrepan en el primer autor, queda CONFLICTO_IDENTIDAD.
Nunca decide pertinencia ni fechas: registra las fechas candidatas de las fuentes aceptadas.
Guarda cada respuesta cruda con su SHA-256 y reanuda desde caché. Solo biblioteca estándar.

Cambios de A2a-1.2 (solo acceso; la lógica de identidad y aceptación es la de 1.1):
  - Claves de API opcionales, leídas de variables de entorno: OPENALEX_API_KEY (encabezado
    «Authorization: Bearer») y S2_API_KEY (encabezado «x-api-key»), solo al origen HTTPS exacto
    (esquema, host y puerto 443). Nunca van en la URL. Se validan antes de usarlas; los mensajes de
    error y los cuerpos que las reflejen se guardan redactados, con constancia. EJECUCIONES.jsonl
    registra solo si había clave o no, aparte de IDENTIDAD.json, para no romper la reanudación.
  - --continuar-de: carpeta de salida de A2a-1.1 cuya caché se hereda en solo lectura. Cada
    consulta que falta en la carpeta nueva se copia de la anterior (cuerpos verificados por SHA
    primero y meta.json al final, de forma atómica) antes de decidir si hace falta otra solicitud.
    La carpeta anterior no se modifica; --out no puede ser igual a ella ni estar anidada.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

VERSION = "A2a-1.2"
INVENTARIO_SHA_ESPERADO = "778424329491191e31c6c669e3504ff2a0e2730966c389226d7a1a73315ef14d"
A0_SHA_ESPERADO = "1e05f504b39d44e410e43eddfb2e58ed60fce86a71859840d377f5cb4593c2ce"
USER_AGENT = "Q15-A2a-abstract-recovery/1.0"
PAUSAS = {"openalex": 0.5, "crossref": 1.0, "s2": 1.1, "arxiv": 3.0}
# Versión anterior aceptada como origen de --continuar-de (auditada en el PR #150).
CONTINUA_VERSION = "A2a-1.1"
CONTINUA_SCRIPT_SHA = "fcd78a0aa13c530bcb84e287e3b92284fcb0bdc04a6026a8009f276f36d837d0"
ENV_OPENALEX = "OPENALEX_API_KEY"
ENV_S2 = "S2_API_KEY"
RECUPERADO = "RESUMEN_RECUPERADO"
# Niveles de identidad, de más fuerte a más débil.
ID_ANCLA = "ANCLA_S2"
ID_DERIVADO = "ID_DERIVADO_DEL_ANCLA"
ID_TAA = "BUSQUEDA_TITULO_ANIO_AUTOR"
ID_TA = "BUSQUEDA_TITULO_ANIO_SIN_AUTOR_DE_REFERENCIA"
ATOM = "{http://www.w3.org/2005/Atom}"


# ---------------------------------------------------------------- utilidades

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ahora_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _plegar(t: str) -> str:
    t = unicodedata.normalize("NFKD", t)
    return "".join(c for c in t if not unicodedata.combining(c)).casefold()


def normalizar_titulo(t: str | None) -> str:
    if not t:
        return ""
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"[^0-9a-z]+", "", _plegar(t))


def apellido(nombre: str | None) -> str:
    """Último token alfabético del nombre, plegado (sin acentos, minúsculas)."""
    if not nombre:
        return ""
    plegado = _plegar(nombre)
    # Alfabeto latino tras plegar; si no hay, tokens de letras en cualquier alfabeto (A1 de Argon).
    toks = re.findall(r"[a-z]+", plegado) or re.findall(r"[^\W\d_]+", plegado)
    return toks[-1] if toks else ""


def anio(v) -> int | None:
    if v is None:
        return None
    m = re.match(r"\s*(\d{4})", str(v))
    return int(m.group(1)) if m else None


def texto_busqueda(t: str) -> str:
    t = html.unescape(re.sub(r"<[^>]+>", " ", t or ""))
    return re.sub(r"\s+", " ", re.sub(r"[\W_]+", " ", t)).strip()


def reconstruir_inverted_index(idx: dict | None) -> str | None:
    if not idx:
        return None
    pos = [(int(i), w) for w, lugares in idx.items() for i in lugares]
    if not pos:
        return None
    pos.sort()
    return " ".join(w for _, w in pos)


def limpiar_jats(s: str | None) -> str | None:
    if not s:
        return None
    s = re.sub(r"<jats:title>.*?</jats:title>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", html.unescape(s)).strip()
    return s or None


def escribir_atomico(p: Path, data: bytes) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, p)


def rel(p: Path, base: Path) -> str:
    return p.relative_to(base).as_posix()


S2_ID = re.compile(r"semanticscholar\.org/paper/(?:[^/]*/)?([0-9a-f]{40})", re.I)


def s2_id_de_url(u: str | None) -> str | None:
    m = S2_ID.search(u or "")
    return m.group(1).lower() if m else None


def norm_doi(d: str | None) -> str:
    d = (d or "").strip().lower()
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", d)


# ---------------------------------------------------------------- HTTP con caché (igual que A0 v1.1)

_CLAVES = ("authorization", "x-api-key")
_REDACTADO = "<CLAVE_REDACTADA>"
# Una clave válida es un token imprimible sin espacios ni caracteres de control.
_CLAVE_VALIDA = re.compile(r"[\x21-\x7e]{8,512}")


def _origen(u: str) -> tuple:
    s = urllib.parse.urlsplit(u)
    puerto = s.port or {"https": 443, "http": 80}.get(s.scheme)
    return (s.scheme, s.hostname, puerto)


class _RedireccionSinClaves(urllib.request.HTTPRedirectHandler):
    """Las claves solo siguen una redirección al mismo origen HTTPS (esquema, host y puerto).

    Cualquier otro destino (otro host, otro puerto o bajada a HTTP) recibe la solicitud sin claves.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        nuevo = super().redirect_request(req, fp, code, msg, headers, newurl)
        if nuevo is None:
            return nuevo
        o_nuevo, o_req = _origen(newurl), _origen(req.full_url)
        if o_nuevo[0] != "https" or o_nuevo != o_req:
            for k in list(nuevo.headers):
                if k.lower() in _CLAVES:
                    del nuevo.headers[k]
            for k in list(nuevo.unredirected_hdrs):
                if k.lower() in _CLAVES:
                    del nuevo.unredirected_hdrs[k]
        return nuevo


_ABRIDOR = urllib.request.build_opener(_RedireccionSinClaves)


def _variantes_secretas(claves: list[str]) -> list[str]:
    """Formas en que una clave puede aparecer en un mensaje: literal, escapada (repr) y sus tramos imprimibles."""
    v = set()
    for k in claves:
        v.add(k)
        v.add(repr(k)[1:-1])
        v.update(t for t in re.split(r"[^\x21-\x7e]+", k) if len(t) >= 6)
    return sorted((x for x in v if x), key=len, reverse=True)


def validar_claves(entorno) -> list[str]:
    """Nombres de variables con una clave inválida. Nunca devuelve ni imprime el valor."""
    return [v for v in (ENV_OPENALEX, ENV_S2) if entorno.get(v) and not _CLAVE_VALIDA.fullmatch(entorno[v])]


class Cliente:
    def __init__(self, out: Path, reintentos: int, timeout: float, fetch=None, dormir=time.sleep,
                 previa: Path | None = None, entorno=None):
        self.out = out
        self.previa = previa
        self._entorno = os.environ if entorno is None else entorno
        self._secretos = _variantes_secretas([self._entorno[v] for v in (ENV_OPENALEX, ENV_S2) if self._entorno.get(v)])
        self.heredadas = 0
        self.reintentos = reintentos
        self.timeout = timeout
        self._fetch = fetch or self._fetch_urllib
        self._dormir = dormir
        self._ultimo: dict[str, float] = {}
        self.solicitudes = 0

    def encabezados(self, url: str) -> dict:
        """Encabezados por origen HTTPS exacto. Las claves salen solo del entorno y no se registran."""
        h = {"User-Agent": USER_AGENT, "Accept": "*/*"}
        esquema, host, puerto = _origen(url)
        if esquema != "https" or puerto != 443:
            return h
        if host == "api.openalex.org" and self._entorno.get(ENV_OPENALEX):
            h["Authorization"] = "Bearer " + self._entorno[ENV_OPENALEX]
        if host == "api.semanticscholar.org" and self._entorno.get(ENV_S2):
            h["x-api-key"] = self._entorno[ENV_S2]
        return h

    def _redactar_texto(self, t: str) -> str:
        for k in self._secretos:
            t = t.replace(k, _REDACTADO)
        return t

    def _redactar_cuerpo(self, body: bytes) -> tuple[bytes, dict | None]:
        """Si la respuesta refleja una clave, se guarda redactada y queda constancia explícita."""
        if not any(k.encode() in body for k in self._secretos):
            return body, None
        red = body
        for k in self._secretos:
            red = red.replace(k.encode(), _REDACTADO.encode())
        return red, {"motivo": "la respuesta contenía una clave de API; se sustituyó por " + _REDACTADO,
                     "bytes_original": len(body)}

    def _fetch_urllib(self, url: str, timeout: float):
        req = urllib.request.Request(url, headers=self.encabezados(url))
        try:
            with _ABRIDOR.open(req, timeout=timeout) as r:
                return r.status, dict(r.headers), r.read(), r.geturl()
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers or {}), e.read() or b"", url

    def _importar_previa(self, d: Path) -> None:
        """Copia una consulta de la carpeta previa: cuerpos verificados primero, meta.json al final.

        meta.json es lo último que se escribe (de forma atómica), así que su presencia indica una
        importación completa. Un corte deja solo cuerpos sin meta, que la siguiente ejecución completa.
        """
        d_prev = self.previa / "raw" / d.name
        m = json.loads((d_prev / "meta.json").read_text(encoding="utf-8"))
        for it in m.get("intentos", []):
            nombre = Path(it["cuerpo"]).name
            data = (d_prev / nombre).read_bytes()
            if sha256_bytes(data) != it["sha256"]:
                raise SystemExit(f"ERROR A2a: cuerpo previo {d.name}/{nombre} no coincide con su SHA")
            destino = d / nombre
            if destino.exists() and destino.read_bytes() != data:
                raise SystemExit(f"ERROR A2a: {d.name}/{nombre} ya existe con otro contenido; revisar a mano")
            escribir_atomico(destino, data)
        m["heredado_de"] = CONTINUA_VERSION
        escribir_atomico(d / "meta.json", json.dumps(m, ensure_ascii=False, indent=1).encode("utf-8"))
        self.heredadas += 1

    def get(self, fuente: str, url: str) -> dict:
        d = self.out / "raw" / sha256_bytes(url.encode())
        meta_p = d / "meta.json"
        if not meta_p.exists() and self.previa is not None and (self.previa / "raw" / d.name / "meta.json").exists():
            self._importar_previa(d)  # la carpeta previa no cambia
        if meta_p.exists():
            meta = json.loads(meta_p.read_text(encoding="utf-8"))
            if meta.get("final"):
                if not (self.out / meta["cuerpo"]).exists():
                    raise SystemExit(f"ERROR A2a: falta el cuerpo de una consulta final en caché ({d.name})")
                meta["cache"] = True
                return meta
        meta_previa = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {}
        previos = meta_previa.get("intentos", [])
        heredado = meta_previa.get("heredado_de")
        en_disco = [int(p.stem.split("_")[1]) for p in d.glob("intento_*.body")] if d.exists() else []
        base_n = max([len(previos)] + en_disco)
        intentos = list(previos)
        meta = None
        for n in range(self.reintentos + 1):
            t0 = self._ultimo.get(fuente)
            if t0 is not None:
                espera = PAUSAS.get(fuente, 1.0) - (time.monotonic() - t0)
                if espera > 0:
                    self._dormir(espera)
            hora = ahora_utc()
            try:
                status, headers, body, url_final = self._fetch(url, self.timeout)
                error = None
            except Exception as ex:  # red, timeout, cabecera inválida
                status, headers, body, url_final = None, {}, b"", url
                error = self._redactar_texto(f"{type(ex).__name__}: {ex}")
            self._ultimo[fuente] = time.monotonic()
            self.solicitudes += 1
            body, redaccion = self._redactar_cuerpo(body)
            url_final = self._redactar_texto(url_final or "")
            cuerpo_p = d / f"intento_{base_n + n + 1:02d}.body"
            escribir_atomico(cuerpo_p, body)
            intento = {"n": base_n + n + 1, "fecha_utc_real": hora, "status": status, "error": error,
                       "url_final": url_final, "cuerpo": rel(cuerpo_p, self.out),
                       "sha256": sha256_bytes(body), "bytes": len(body)}
            if redaccion:
                intento["redaccion"] = redaccion
            intentos.append(intento)
            transitorio = status is None or status == 429 or status >= 500
            meta = {"fuente": fuente, "url": url, "intentos": intentos, "status": status,
                    "cuerpo": intento["cuerpo"], "sha256": intento["sha256"],
                    "final": not transitorio, "cache": False}
            if heredado:
                meta["heredado_de"] = heredado
            escribir_atomico(meta_p, json.dumps(meta, ensure_ascii=False, indent=1).encode("utf-8"))
            if not transitorio or n == self.reintentos:
                break
            ra = (headers or {}).get("Retry-After") or (headers or {}).get("retry-after")
            try:
                espera = min(float(ra), 120.0) if ra else min(2 ** (n + 2), 60)
            except ValueError:
                espera = min(2 ** (n + 2), 60)
            self._dormir(espera)
        return meta

    def json(self, meta: dict):
        return json.loads((self.out / meta["cuerpo"]).read_bytes())

    def bytes(self, meta: dict) -> bytes:
        return (self.out / meta["cuerpo"]).read_bytes()


# ---------------------------------------------------------------- parsers de candidatos
# Cada candidato: {fuente, via, titulo, autores, resumen, anio, fechas, ids}

def _cand_openalex(j: dict, via: str) -> dict:
    ids = j.get("ids") or {}
    return {"fuente": "openalex", "via": via, "titulo": j.get("title") or j.get("display_name"),
            "autores": [((a.get("author") or {}).get("display_name")) for a in j.get("authorships") or []],
            "resumen": reconstruir_inverted_index(j.get("abstract_inverted_index")),
            "anio": j.get("publication_year") or anio(j.get("publication_date")),
            "fechas": {"publication_date": j.get("publication_date")},
            "ids": {"doi": norm_doi(ids.get("doi") or j.get("doi")) or None, "openalex": j.get("id")}}


def _cand_crossref(j: dict, via: str) -> dict:
    tit = j.get("title") or []

    def fecha(k):
        parts = ((j.get(k) or {}).get("date-parts") or [[None]])[0]
        return "-".join(str(x) for x in parts if x is not None) or None
    fechas = {k: fecha(k) for k in ("created", "published-online", "published-print", "issued", "posted")}
    return {"fuente": "crossref", "via": via, "titulo": tit[0] if tit else None,
            "autores": [(" ".join(x for x in (a.get("given"), a.get("family")) if x) or a.get("name") or "").strip()
                        for a in j.get("author") or []],
            "resumen": limpiar_jats(j.get("abstract")),
            # Año: issued y, si falta, las demás fechas propias de la obra (M1 de Argon).
            "anio": next((anio(fechas.get(k)) for k in ("issued", "published-print", "published-online", "posted", "created")
                          if anio(fechas.get(k))), None),
            "fechas": fechas, "ids": {"doi": norm_doi(j.get("DOI")) or None}}


def _cand_s2(j: dict, via: str) -> dict:
    ext = j.get("externalIds") or {}
    return {"fuente": "s2", "via": via, "titulo": j.get("title"),
            "autores": [a.get("name") for a in j.get("authors") or []],
            "resumen": j.get("abstract") or None, "anio": j.get("year"),
            "fechas": {"publicationDate": j.get("publicationDate"), "year": j.get("year")},
            "ids": {"doi": norm_doi(ext.get("DOI")) or None, "arxiv": ext.get("ArXiv") or None,
                    "s2": j.get("paperId")}}


def _cands_arxiv(xml: bytes, via: str) -> list[dict]:
    out = []
    root = ET.fromstring(xml)
    for e in root.findall(ATOM + "entry"):
        if e.find(ATOM + "title") is None:
            continue
        g = lambda k: (e.findtext(ATOM + k) or "").strip() or None  # noqa: E731
        aid = re.sub(r"^https?://arxiv\.org/abs/", "", g("id") or "")
        out.append({"fuente": "arxiv", "via": via, "titulo": re.sub(r"\s+", " ", g("title") or ""),
                    "autores": [(a.findtext(ATOM + "name") or "").strip() for a in e.findall(ATOM + "author")],
                    "resumen": re.sub(r"\s+", " ", g("summary") or "") or None, "anio": anio(g("published")),
                    "fechas": {"published_v1": g("published"), "updated": g("updated")},
                    "ids": {"arxiv": re.sub(r"v\d+$", "", aid) or None}})
    return out


S2_CAMPOS = "paperId,title,abstract,authors,year,publicationDate,externalIds"


def consultar(c: Cliente, fuente: str, url: str, parser) -> tuple[dict, list[dict]]:
    """Devuelve (registro_de_consulta, candidatos)."""
    m = c.get(fuente, url)
    q = {"fuente": fuente, "url": url, "status": m["status"], "sha256": m["sha256"], "cuerpo": m["cuerpo"]}
    cands = []
    if m["status"] == 200:
        try:
            cands = parser(c, m)
        except (ValueError, AttributeError, TypeError, ET.ParseError) as ex:
            q["error_parseo"] = f"{type(ex).__name__}: {ex}"
    for k in cands:
        k["consulta_sha256"] = m["sha256"]
        k["url"] = url
    return q, cands


def q_s2_ancla(c, pid):
    url = f"https://api.semanticscholar.org/graph/v1/paper/{pid}?fields={S2_CAMPOS}"
    return consultar(c, "s2", url, lambda c, m: [_cand_s2(c.json(m), "ancla_s2")])


def q_openalex_doi(c, doi):
    url = "https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe="/")
    return consultar(c, "openalex", url, lambda c, m: [_cand_openalex(c.json(m), "doi_derivado")])


def q_crossref_doi(c, doi):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    return consultar(c, "crossref", url, lambda c, m: [_cand_crossref(c.json(m).get("message") or {}, "doi_derivado")])


def q_arxiv_id(c, aid):
    url = "https://export.arxiv.org/api/query?id_list=" + urllib.parse.quote(aid) + "&max_results=1"
    return consultar(c, "arxiv", url, lambda c, m: _cands_arxiv(c.bytes(m), "arxiv_derivado"))


def q_openalex_busqueda(c, t):
    url = ("https://api.openalex.org/works?per-page=10&filter=title.search:"
           + urllib.parse.quote(texto_busqueda(t).replace(",", " ")))
    return consultar(c, "openalex", url,
                     lambda c, m: [_cand_openalex(j, "busqueda") for j in (c.json(m).get("results") or [])])


def q_crossref_busqueda(c, t):
    url = "https://api.crossref.org/works?rows=10&query.bibliographic=" + urllib.parse.quote(texto_busqueda(t))
    return consultar(c, "crossref", url,
                     lambda c, m: [_cand_crossref(j, "busqueda") for j in ((c.json(m).get("message") or {}).get("items") or [])])


RESERVADAS_ARXIV = {"and", "or", "not", "andnot"}


def consulta_arxiv(t: str) -> str:
    """ti:tok1 AND ti:tok2 ... con tokens de más de 2 letras, sin operadores reservados (M2 de Argon).
    Solo amplía la búsqueda: la aceptación sigue exigiendo título normalizado idéntico, año y autor."""
    toks = [w for w in texto_busqueda(t).split() if len(w) > 2 and w.lower() not in RESERVADAS_ARXIV][:12]
    return " AND ".join("ti:" + w for w in toks)


def q_arxiv_busqueda(c, t):
    url = ("https://export.arxiv.org/api/query?max_results=10&search_query="
           + urllib.parse.quote(consulta_arxiv(t)))
    return consultar(c, "arxiv", url, lambda c, m: _cands_arxiv(c.bytes(m), "busqueda"))


def q_s2_match(c, t):
    url = ("https://api.semanticscholar.org/graph/v1/paper/search/match?query="
           + urllib.parse.quote(texto_busqueda(t)) + "&fields=" + S2_CAMPOS)
    return consultar(c, "s2", url, lambda c, m: [_cand_s2(j, "busqueda") for j in (c.json(m).get("data") or [])])


# ---------------------------------------------------------------- lógica por registro

def evaluar_registro(c: Cliente, inv: dict, a0: dict) -> dict:
    titulo = inv.get("titulo") or ""
    tnorm = normalizar_titulo(titulo)
    anio_snap = anio(inv.get("fecha_snapshot"))
    pid = s2_id_de_url(inv.get("url_snapshot"))
    res = {"registro_id": inv["registro_id"], "estado_a0": a0["estado_propuesto"], "titulo_inventario": titulo,
           "anio_snapshot": anio_snap, "s2_paper_id": pid, "doi_snapshot": norm_doi(inv.get("doi_snapshot")) or None,
           "arxiv_snapshot": (inv.get("arxiv_snapshot") or "").strip() or None, "consultas": [],
           "candidatos": [], "version": VERSION}
    fallos = []

    def correr(par):
        q, cands = par
        res["consultas"].append(q)
        # Fallo = error reintentable (red, 429, 5xx) o respuesta ilegible. Un 404 es una respuesta final
        # (p. ej. S2 match sin coincidencia) y no cuenta como fallo de acceso.
        st = q["status"]
        if st is None or st == 429 or st >= 500 or q.get("error_parseo"):
            fallos.append(q)
        for k in cands:
            k["titulo_coincide"] = bool(tnorm) and normalizar_titulo(k.get("titulo")) == tnorm
            if k.get("resumen"):
                k["resumen_sha256"] = sha256_bytes(k["resumen"].encode("utf-8"))
        res["candidatos"].extend(cands)
        return cands

    def aceptar(cands, nivel):
        ok = [k for k in cands if k.get("aceptado")]
        con_res = [k for k in ok if k.get("resumen")]
        if con_res:
            res["estado_propuesto"] = RECUPERADO
            res["nivel_identidad"] = nivel
            return True
        return False

    # 1. Ancla S2
    ancla = None
    autores_ref: list[str] = []
    if pid:
        cands = correr(q_s2_ancla(c, pid))
        if not cands:
            res["nota_ancla"] = "Ancla S2 sin registro legible (status o parseo)."
        elif not cands[0].get("titulo_coincide"):
            res["nota_ancla"] = "El título del registro S2 no coincide con el del inventario: no se usa como ancla."
        if cands and cands[0].get("titulo_coincide"):
            ancla = cands[0]
            ancla["aceptado"] = True
            autores_ref = [a for a in ancla.get("autores") or [] if a]
            if aceptar([ancla], ID_ANCLA):
                return _cerrar(res, fallos)
    res["autores_referencia"] = autores_ref
    # 2. Identificadores derivados del ancla
    if ancla:
        doi_n = (ancla["ids"].get("doi") or "")
        ax_n = (ancla["ids"].get("arxiv") or "")
        derivados = []
        if doi_n and doi_n != (res["doi_snapshot"] or ""):
            derivados += correr(q_openalex_doi(c, doi_n)) + correr(q_crossref_doi(c, doi_n))
        if ax_n and ax_n != (res["arxiv_snapshot"] or ""):
            derivados += correr(q_arxiv_id(c, ax_n))
        for k in derivados:
            k["aceptado"] = k["titulo_coincide"]
        if aceptar(derivados, ID_DERIVADO):
            return _cerrar(res, fallos)
    # 3. Búsqueda por título
    if not tnorm:
        res["estado_propuesto"] = "SIN_RESUMEN_TRAS_A2A"
        res["nota"] = "Título vacío tras normalizar: no se busca."
        return _cerrar(res, fallos)
    ap_ref = apellido(autores_ref[0]) if autores_ref else ""

    def juzgar(k):
        motivo = []
        if not k["titulo_coincide"]:
            motivo.append("titulo")
        a = anio(k.get("anio"))
        if anio_snap is None or a is None or abs(a - anio_snap) > 1:
            motivo.append("anio")
        ap_k = apellido((k.get("autores") or [None])[0])
        # Con autor de referencia, el primer autor debe coincidir; sin él, el candidato debe traer un
        # primer autor identificable (no se aceptan registros anónimos en el nivel débil; A1 de Argon).
        if (ap_ref and ap_k != ap_ref) or not ap_k:
            motivo.append("primer_autor")
        k["aceptado"] = not motivo
        k["rechazo"] = motivo

    busq: list[dict] = []
    for fn in (q_openalex_busqueda, q_crossref_busqueda, q_s2_match, q_arxiv_busqueda):
        nuevos = correr(fn(c, titulo))
        for k in nuevos:
            juzgar(k)
        busq += nuevos
        # Con autor de referencia basta el primer aceptado. Sin él se consultan todas las fuentes, para
        # detectar discrepancias de primer autor entre fuentes (A1 de Argon).
        if ap_ref and any(k["aceptado"] and k.get("resumen") for k in busq):
            break
    ok = [k for k in busq if k["aceptado"] and k.get("resumen")]
    if ok:
        if not ap_ref and len({apellido((k.get("autores") or [None])[0]) for k in ok}) > 1:
            res["estado_propuesto"] = "CONFLICTO_IDENTIDAD"
            res["nota"] = "Candidatos con título y año idénticos discrepan en el primer autor y no hay autor de referencia."
            return _cerrar(res, fallos)
        res["estado_propuesto"] = RECUPERADO
        res["nivel_identidad"] = ID_TAA if ap_ref else ID_TA
        return _cerrar(res, fallos)
    res["estado_propuesto"] = "SIN_RESUMEN_TRAS_A2A"
    return _cerrar(res, fallos)


def _cerrar(res: dict, fallos: list[dict]) -> dict:
    res["consultas_fallidas"] = [f"{q['fuente']}:{q['status']}" for q in fallos]
    # Si no se recuperó y alguna consulta falló de forma reintentable, el «sin resumen» no es definitivo:
    # queda ERROR_ACCESO (repetir el comando reintenta solo esas consultas; lo demás sale de la caché).
    if res["estado_propuesto"] != RECUPERADO and fallos:
        res["estado_propuesto"] = "ERROR_ACCESO"
    acept = [k for k in res["candidatos"] if k.get("aceptado")]
    res["fuentes_aceptadas"] = sorted({k["fuente"] + ":" + k["via"] for k in acept if k.get("resumen")})
    res["fechas_candidatas"] = [{"fuente": k["fuente"], "via": k["via"], "fechas": k.get("fechas")} for k in acept]
    return res


# ---------------------------------------------------------------- identidad y exportación

def identidad(script_sha: str, inv_sha: str, a0_sha: str, continua: dict | None = None) -> dict:
    ident = {"version": VERSION, "script_sha256": script_sha, "inventario_sha256": inv_sha, "a0_sha256": a0_sha}
    if continua is not None:
        ident["continua_de"] = continua
    return ident


def verificar_previa(previa: Path, inv_sha: str, a0_sha: str) -> dict:
    """La carpeta previa debe ser una salida de A2a-1.1 con los mismos insumos."""
    p = previa / "IDENTIDAD.json"
    if not p.exists():
        raise SystemExit("ERROR A2a: --continuar-de no tiene IDENTIDAD.json")
    raw = p.read_bytes()
    prev = json.loads(raw)
    esperado = {"version": CONTINUA_VERSION, "script_sha256": CONTINUA_SCRIPT_SHA,
                "inventario_sha256": inv_sha, "a0_sha256": a0_sha}
    if prev != esperado:
        raise SystemExit("ERROR A2a: --continuar-de no es una salida de A2a-1.1 con los mismos insumos")
    return {"version": CONTINUA_VERSION, "script_sha256": CONTINUA_SCRIPT_SHA,
            "identidad_sha256": sha256_bytes(raw)}


def verificar_identidad(out: Path, ident: dict) -> None:
    p = out / "IDENTIDAD.json"
    if p.exists():
        if json.loads(p.read_text(encoding="utf-8")) != ident:
            raise SystemExit("ERROR A2a: la salida pertenece a otro script o insumo; usar carpeta nueva")
    else:
        escribir_atomico(p, json.dumps(ident, indent=1).encode("utf-8"))


def exportar(out: Path, resultados: list[dict]) -> dict:
    conteos: dict[str, int] = {}
    niveles: dict[str, int] = {}
    for r in resultados:
        conteos[r["estado_propuesto"]] = conteos.get(r["estado_propuesto"], 0) + 1
        if r.get("nivel_identidad"):
            niveles[r["nivel_identidad"]] = niveles.get(r["nivel_identidad"], 0) + 1
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["registro_id", "estado_a0", "estado_propuesto", "nivel_identidad", "titulo_inventario",
                "fuente_resumen", "titulo_fuente", "autores_fuente", "anio_fuente", "ids_fuente",
                "resumen_sha256", "resumen", "fechas_candidatas_json", "consultas_fallidas"])
    for r in resultados:
        k = next((k for k in r["candidatos"] if k.get("aceptado") and k.get("resumen")), None)
        w.writerow([r["registro_id"], r["estado_a0"], r["estado_propuesto"], r.get("nivel_identidad", ""),
                    r["titulo_inventario"], f"{k['fuente']}:{k['via']}" if k else "", k.get("titulo", "") if k else "",
                    "; ".join(a for a in (k.get("autores") or []) if a) if k else "", k.get("anio", "") if k else "",
                    json.dumps(k.get("ids"), ensure_ascii=False) if k else "", k.get("resumen_sha256", "") if k else "",
                    k.get("resumen", "") if k else "", json.dumps(r.get("fechas_candidatas"), ensure_ascii=False),
                    ";".join(r.get("consultas_fallidas", []))])
    escribir_atomico(out / "recuperacion_a2a.csv", buf.getvalue().encode("utf-8"))
    escribir_atomico(out / "recuperacion_a2a.json", json.dumps(resultados, ensure_ascii=False, indent=1).encode("utf-8"))
    resumen = {"version": VERSION, "fecha_utc": ahora_utc(), "registros": len(resultados),
               "conteos": conteos, "niveles_identidad": niveles}
    escribir_atomico(out / "RESUMEN_A2A.json", json.dumps(resumen, ensure_ascii=False, indent=1).encode("utf-8"))
    return resumen


def main(argv=None, fetch=None, dormir=time.sleep, entorno=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inventario", required=True)
    ap.add_argument("--a0", required=True, help="recuperacion_a0.json de la fase A0")
    ap.add_argument("--out", required=True)
    ap.add_argument("--reintentos", type=int, default=4)
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--limite", type=int, default=0, help="procesar solo los primeros N registros (prueba)")
    ap.add_argument("--sha-inventario", default=INVENTARIO_SHA_ESPERADO)
    ap.add_argument("--sha-a0", default=A0_SHA_ESPERADO)
    ap.add_argument("--continuar-de", default=None,
                    help="carpeta de salida de A2a-1.1 cuya caché se hereda (solo lectura)")
    a = ap.parse_args(argv)
    inv_p, a0_p = Path(a.inventario), Path(a.a0)
    inv_sha, a0_sha = sha256_file(inv_p), sha256_file(a0_p)
    if inv_sha != a.sha_inventario:
        print(f"ERROR A2a: SHA del inventario {inv_sha} != esperado {a.sha_inventario}", file=sys.stderr)
        return 1
    if a0_sha != a.sha_a0:
        print(f"ERROR A2a: SHA de A0 {a0_sha} != esperado {a.sha_a0}", file=sys.stderr)
        return 1
    out = Path(a.out)
    entorno = os.environ if entorno is None else entorno
    malas = validar_claves(entorno)
    if malas:  # solo el nombre de la variable, nunca su valor
        print(f"ERROR A2a: clave inválida en {', '.join(malas)} (espacios, saltos de línea o longitud)",
              file=sys.stderr)
        return 1
    previa = Path(a.continuar_de) if a.continuar_de else None
    continua = None
    if previa is not None:
        rp, ro = previa.resolve(), out.resolve()
        if rp == ro or rp in ro.parents or ro in rp.parents:
            print("ERROR A2a: --out y --continuar-de deben ser carpetas separadas (ni iguales ni anidadas)",
                  file=sys.stderr)
            return 1
        continua = verificar_previa(previa, inv_sha, a0_sha)
    out.mkdir(parents=True, exist_ok=True)
    verificar_identidad(out, identidad(sha256_file(Path(__file__)), inv_sha, a0_sha, continua))
    # Presencia de claves por ejecución: va aparte de la identidad para no romper la reanudación.
    ejec = {"fecha_utc": ahora_utc(), "version": VERSION,
            "claves_api_presentes": {ENV_OPENALEX: bool(entorno.get(ENV_OPENALEX)),
                                     ENV_S2: bool(entorno.get(ENV_S2))}}
    with open(out / "EJECUCIONES.jsonl", "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(ejec, ensure_ascii=False) + "\n")
    inv = {x["registro_id"]: x for x in json.loads(inv_p.read_text(encoding="utf-8"))}
    a0 = json.loads(a0_p.read_text(encoding="utf-8"))
    faltan = [r["registro_id"] for r in a0 if r["registro_id"] not in inv]
    if faltan:
        print(f"ERROR A2a: {len(faltan)} registros de A0 no están en el inventario", file=sys.stderr)
        return 1
    pendientes = [r for r in a0 if r["estado_propuesto"] != RECUPERADO]
    if a.limite:
        pendientes = pendientes[: a.limite]
    c = Cliente(out, a.reintentos, a.timeout, fetch=fetch, dormir=dormir, previa=previa, entorno=entorno)
    resultados = []
    for i, r in enumerate(pendientes, 1):
        resultados.append(evaluar_registro(c, inv[r["registro_id"]], r))
        if i % 25 == 0:
            print(f"A2a: {i}/{len(pendientes)} registros, {c.solicitudes} solicitudes nuevas, "
                  f"{c.heredadas} consultas heredadas", flush=True)
    resumen = exportar(out, resultados)
    print(json.dumps({"conteos": resumen["conteos"], "niveles": resumen["niveles_identidad"]}, ensure_ascii=False))
    return 2 if resumen["conteos"].get("ERROR_ACCESO") else 0


if __name__ == "__main__":
    sys.exit(main())
