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
  3. Búsqueda por título en OpenAlex, Crossref, arXiv y S2 (match). Un candidato se acepta solo
     si (a) el título normalizado es idéntico, (b) el año es compatible (±1 con el snapshot) y
     (c) el apellido del primer autor coincide con el del ancla S2, cuando el ancla lo da. Si no
     hay autores de referencia, se acepta con nivel de identidad débil y A1 debe verificarlos;
     si los candidatos aceptados discrepan en el primer autor, queda CONFLICTO_IDENTIDAD.
Nunca decide pertinencia ni fechas: registra las fechas candidatas de las fuentes aceptadas.
Guarda cada respuesta cruda con su SHA-256 y reanuda desde caché. Solo biblioteca estándar.
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

VERSION = "A2a-1.0"
INVENTARIO_SHA_ESPERADO = "778424329491191e31c6c669e3504ff2a0e2730966c389226d7a1a73315ef14d"
A0_SHA_ESPERADO = "1e05f504b39d44e410e43eddfb2e58ed60fce86a71859840d377f5cb4593c2ce"
USER_AGENT = "Q15-A2a-abstract-recovery/1.0"
PAUSAS = {"openalex": 0.5, "crossref": 1.0, "s2": 1.1, "arxiv": 3.0}
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
    toks = re.findall(r"[a-z]+", _plegar(nombre))
    return toks[-1] if toks else ""


def anio(v) -> int | None:
    if v is None:
        return None
    m = re.match(r"\s*(\d{4})", str(v))
    return int(m.group(1)) if m else None


def texto_busqueda(t: str) -> str:
    t = html.unescape(re.sub(r"<[^>]+>", " ", t or ""))
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", t)).strip()


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

class Cliente:
    def __init__(self, out: Path, reintentos: int, timeout: float, fetch=None, dormir=time.sleep):
        self.out = out
        self.reintentos = reintentos
        self.timeout = timeout
        self._fetch = fetch or self._fetch_urllib
        self._dormir = dormir
        self._ultimo: dict[str, float] = {}
        self.solicitudes = 0

    def _fetch_urllib(self, url: str, timeout: float):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, dict(r.headers), r.read(), r.geturl()
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers or {}), e.read() or b"", url

    def get(self, fuente: str, url: str) -> dict:
        d = self.out / "raw" / sha256_bytes(url.encode())
        meta_p = d / "meta.json"
        if meta_p.exists():
            meta = json.loads(meta_p.read_text(encoding="utf-8"))
            if meta.get("final"):
                meta["cache"] = True
                return meta
        previos = json.loads(meta_p.read_text(encoding="utf-8"))["intentos"] if meta_p.exists() else []
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
            except Exception as ex:  # red, timeout
                status, headers, body, url_final, error = None, {}, b"", url, f"{type(ex).__name__}: {ex}"
            self._ultimo[fuente] = time.monotonic()
            self.solicitudes += 1
            cuerpo_p = d / f"intento_{base_n + n + 1:02d}.body"
            escribir_atomico(cuerpo_p, body)
            intento = {"n": base_n + n + 1, "fecha_utc_real": hora, "status": status, "error": error,
                       "url_final": url_final, "cuerpo": rel(cuerpo_p, self.out),
                       "sha256": sha256_bytes(body), "bytes": len(body)}
            intentos.append(intento)
            transitorio = status is None or status == 429 or status >= 500
            meta = {"fuente": fuente, "url": url, "intentos": intentos, "status": status,
                    "cuerpo": intento["cuerpo"], "sha256": intento["sha256"],
                    "final": not transitorio, "cache": False}
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
            "autores": [" ".join(x for x in (a.get("given"), a.get("family")) if x) for a in j.get("author") or []],
            "resumen": limpiar_jats(j.get("abstract")), "anio": anio(fechas.get("issued")),
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


def q_arxiv_busqueda(c, t):
    url = ("https://export.arxiv.org/api/query?max_results=10&search_query="
           + urllib.parse.quote('ti:"' + texto_busqueda(t) + '"'))
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
        if ap_ref and apellido((k.get("autores") or [None])[0]) != ap_ref:
            motivo.append("primer_autor")
        k["aceptado"] = not motivo
        k["rechazo"] = motivo

    busq: list[dict] = []
    for fn in (q_openalex_busqueda, q_crossref_busqueda, q_s2_match, q_arxiv_busqueda):
        nuevos = correr(fn(c, titulo))
        for k in nuevos:
            juzgar(k)
        busq += nuevos
        if any(k["aceptado"] and k.get("resumen") for k in busq):
            break  # ya hay un candidato aceptado con resumen: no hace falta seguir
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

def identidad(script_sha: str, inv_sha: str, a0_sha: str) -> dict:
    return {"version": VERSION, "script_sha256": script_sha, "inventario_sha256": inv_sha, "a0_sha256": a0_sha}


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


def main(argv=None, fetch=None, dormir=time.sleep) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inventario", required=True)
    ap.add_argument("--a0", required=True, help="recuperacion_a0.json de la fase A0")
    ap.add_argument("--out", required=True)
    ap.add_argument("--reintentos", type=int, default=4)
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--limite", type=int, default=0, help="procesar solo los primeros N registros (prueba)")
    ap.add_argument("--sha-inventario", default=INVENTARIO_SHA_ESPERADO)
    ap.add_argument("--sha-a0", default=A0_SHA_ESPERADO)
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
    out.mkdir(parents=True, exist_ok=True)
    verificar_identidad(out, identidad(sha256_file(Path(__file__)), inv_sha, a0_sha))
    inv = {x["registro_id"]: x for x in json.loads(inv_p.read_text(encoding="utf-8"))}
    a0 = json.loads(a0_p.read_text(encoding="utf-8"))
    faltan = [r["registro_id"] for r in a0 if r["registro_id"] not in inv]
    if faltan:
        print(f"ERROR A2a: {len(faltan)} registros de A0 no están en el inventario", file=sys.stderr)
        return 1
    pendientes = [r for r in a0 if r["estado_propuesto"] != RECUPERADO]
    if a.limite:
        pendientes = pendientes[: a.limite]
    c = Cliente(out, a.reintentos, a.timeout, fetch=fetch, dormir=dormir)
    resultados = []
    for i, r in enumerate(pendientes, 1):
        resultados.append(evaluar_registro(c, inv[r["registro_id"]], r))
        if i % 25 == 0:
            print(f"A2a: {i}/{len(pendientes)} registros, {c.solicitudes} solicitudes nuevas", flush=True)
    resumen = exportar(out, resultados)
    print(json.dumps({"conteos": resumen["conteos"], "niveles": resumen["niveles_identidad"]}, ensure_ascii=False))
    return 2 if resumen["conteos"].get("ERROR_ACCESO") else 0


if __name__ == "__main__":
    sys.exit(main())
