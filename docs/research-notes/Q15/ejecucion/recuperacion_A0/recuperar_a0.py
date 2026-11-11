#!/usr/bin/env python3
"""Q15, fase A0: recuperación determinista de resúmenes de autor y fechas, sin LLM.

Insumo: INVENTARIO_857.json del plan de pendientes v1 (SHA verificado).
Para cada registro con DOI consulta OpenAlex, Crossref y Semantic Scholar por DOI.
Para cada registro con arXiv consulta la API de arXiv por id. Guarda cada respuesta
cruda con su SHA-256, acepta un resumen solo si el título normalizado coincide con el
del inventario y nunca decide pertinencia. Los registros sin identificador quedan
SIN_IDENTIFICADOR para la fase manual A2.

Solo biblioteca estándar. Reanudable: las respuestas se cachean por URL.
"""
from __future__ import annotations

import argparse
import hashlib
import html
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

VERSION = "A0-1.1"
INVENTARIO_SHA_ESPERADO = "778424329491191e31c6c669e3504ff2a0e2730966c389226d7a1a73315ef14d"
USER_AGENT = "Q15-A0-abstract-recovery/1.0"
PAUSAS = {"openalex": 0.5, "crossref": 1.0, "s2": 1.1, "arxiv": 3.0}
ESTADOS_RECUPERADO = "RESUMEN_RECUPERADO"


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


def normalizar_titulo(t: str | None) -> str:
    if not t:
        return ""
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^0-9a-z]+", "", t.casefold())


def reconstruir_inverted_index(idx: dict | None) -> str | None:
    """OpenAlex abstract_inverted_index -> texto (reconstrucción determinista)."""
    if not idx:
        return None
    pos = []
    for palabra, lugares in idx.items():
        for i in lugares:
            pos.append((int(i), palabra))
    if not pos:
        return None
    pos.sort()
    return " ".join(p for _, p in pos)


def limpiar_jats(s: str | None) -> str | None:
    """Crossref entrega el resumen en JATS/XML; se quitan etiquetas, sin reescribir texto."""
    if not s:
        return None
    s = re.sub(r"<jats:title>.*?</jats:title>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
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


# ---------------------------------------------------------------- HTTP con caché

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
        clave = sha256_bytes(url.encode())
        d = self.out / "raw" / clave
        meta_p = d / "meta.json"
        if meta_p.exists():
            meta = json.loads(meta_p.read_text(encoding="utf-8"))
            if meta.get("final"):
                meta["cache"] = True
                return meta
        previos = json.loads(meta_p.read_text(encoding="utf-8"))["intentos"] if meta_p.exists() else []
        # Continuar la numeración: nunca sobrescribir intentos anteriores, aunque un corte
        # (Ctrl+C) hubiera dejado un cuerpo escrito sin su meta.
        en_disco = [int(p.stem.split("_")[1]) for p in d.glob("intento_*.body")] if d.exists() else []
        base_n = max([len(previos)] + en_disco)
        intentos = list(previos)
        meta = None
        for n in range(self.reintentos + 1):
            pausa = PAUSAS.get(fuente, 1.0)
            t0 = self._ultimo.get(fuente)
            if t0 is not None:
                espera = pausa - (time.monotonic() - t0)
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
            intento = {"n": base_n + n + 1,"fecha_utc_real": hora, "status": status, "error": error,
                       "url_final": url_final, "cuerpo": rel(cuerpo_p, self.out),
                       "sha256": sha256_bytes(body), "bytes": len(body)}
            intentos.append(intento)
            transitorio = status is None or status == 429 or (status is not None and status >= 500)
            meta = {"fuente": fuente, "url": url, "intentos": intentos, "status": status,
                    "cuerpo": intento["cuerpo"], "sha256": intento["sha256"],
                    "final": not transitorio, "cache": False}
            # meta.json se persiste en cada intento, sincronizado con los cuerpos en disco.
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

    def cuerpo(self, meta: dict) -> bytes:
        return (self.out / meta["cuerpo"]).read_bytes()


# ---------------------------------------------------------------- fuentes

def consultar_openalex(c: Cliente, doi: str) -> dict:
    url = "https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe="/")
    m = c.get("openalex", url)
    r = {"fuente": "openalex", "url": url, "status": m["status"], "sha256": m["sha256"], "cuerpo": m["cuerpo"]}
    if m["status"] == 200:
        try:
            j = json.loads(c.cuerpo(m))
            r["titulo"] = j.get("title") or j.get("display_name")
            r["autores"] = [((a.get("author") or {}).get("display_name")) for a in j.get("authorships") or []]
            r["resumen"] = reconstruir_inverted_index(j.get("abstract_inverted_index"))
            r["fechas"] = {"publication_date": j.get("publication_date")}
        except (ValueError, AttributeError) as ex:
            r["error_parseo"] = str(ex)
    return r


def consultar_crossref(c: Cliente, doi: str) -> dict:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    m = c.get("crossref", url)
    r = {"fuente": "crossref", "url": url, "status": m["status"], "sha256": m["sha256"], "cuerpo": m["cuerpo"]}
    if m["status"] == 200:
        try:
            j = json.loads(c.cuerpo(m)).get("message") or {}
            tit = j.get("title") or []
            r["titulo"] = tit[0] if tit else None
            r["autores"] = [" ".join(x for x in (a.get("given"), a.get("family")) if x) for a in j.get("author") or []]
            r["resumen"] = limpiar_jats(j.get("abstract"))
            def fecha(k):
                v = j.get(k) or {}
                parts = (v.get("date-parts") or [[None]])[0]
                return "-".join(str(x) for x in parts if x is not None) or None
            r["fechas"] = {k: fecha(k) for k in ("created", "published-online", "published-print", "issued", "posted")}
        except (ValueError, AttributeError) as ex:
            r["error_parseo"] = str(ex)
    return r


def consultar_s2(c: Cliente, doi: str) -> dict:
    campos = "title,abstract,authors,year,publicationDate,externalIds"
    url = "https://api.semanticscholar.org/graph/v1/paper/DOI:" + urllib.parse.quote(doi, safe="/") + "?fields=" + campos
    m = c.get("s2", url)
    r = {"fuente": "s2", "url": url, "status": m["status"], "sha256": m["sha256"], "cuerpo": m["cuerpo"]}
    if m["status"] == 200:
        try:
            j = json.loads(c.cuerpo(m))
            r["titulo"] = j.get("title")
            r["autores"] = [a.get("name") for a in j.get("authors") or []]
            r["resumen"] = (j.get("abstract") or None)
            r["fechas"] = {"publicationDate": j.get("publicationDate"), "year": j.get("year")}
        except (ValueError, AttributeError) as ex:
            r["error_parseo"] = str(ex)
    return r


ATOM = "{http://www.w3.org/2005/Atom}"


def consultar_arxiv(c: Cliente, arxiv_id: str) -> dict:
    url = "https://export.arxiv.org/api/query?id_list=" + urllib.parse.quote(arxiv_id) + "&max_results=1"
    m = c.get("arxiv", url)
    r = {"fuente": "arxiv", "url": url, "status": m["status"], "sha256": m["sha256"], "cuerpo": m["cuerpo"]}
    if m["status"] == 200:
        try:
            root = ET.fromstring(c.cuerpo(m))
            e = root.find(ATOM + "entry")
            if e is not None and e.find(ATOM + "title") is not None:
                g = lambda k: (e.findtext(ATOM + k) or "").strip() or None
                r["titulo"] = re.sub(r"\s+", " ", g("title") or "")
                r["autores"] = [(a.findtext(ATOM + "name") or "").strip() for a in e.findall(ATOM + "author")]
                r["resumen"] = re.sub(r"\s+", " ", g("summary") or "") or None
                r["fechas"] = {"published_v1": g("published"), "updated": g("updated")}
        except ET.ParseError as ex:
            r["error_parseo"] = str(ex)
    return r


# ---------------------------------------------------------------- lógica por registro

def evaluar_registro(c: Cliente, reg: dict) -> dict:
    doi = (reg.get("doi_snapshot") or "").strip()
    ax = (reg.get("arxiv_snapshot") or "").strip()
    titulo_inv = normalizar_titulo(reg.get("titulo"))
    res = {"registro_id": reg["registro_id"], "estado_anterior": reg["estado"], "titulo_inventario": reg.get("titulo"),
           "doi": doi or None, "arxiv": ax or None, "fuentes": [], "version": VERSION}
    if not doi and not ax:
        res["estado_propuesto"] = "SIN_IDENTIFICADOR"
        res["nota"] = "Sin DOI ni arXiv en el snapshot: pasa a la fase manual A2."
        return res
    consultas = []
    if doi:
        consultas += [consultar_openalex(c, doi), consultar_crossref(c, doi), consultar_s2(c, doi)]
    if ax:
        consultas.append(consultar_arxiv(c, ax))
    resumenes, discordantes, fallos = [], [], []
    for q in consultas:
        if q.get("status") != 200 or q.get("error_parseo"):
            fallos.append(q["fuente"])
        titulo_f = normalizar_titulo(q.get("titulo"))
        coincide = bool(titulo_inv) and bool(titulo_f) and titulo_f == titulo_inv
        q["titulo_coincide"] = coincide
        if q.get("resumen"):
            q["resumen_sha256"] = sha256_bytes(q["resumen"].encode("utf-8"))
            (resumenes if coincide else discordantes).append(q["fuente"])
        res["fuentes"].append(q)
    if resumenes:
        estado = ESTADOS_RECUPERADO
    elif discordantes:
        estado = "CONFLICTO_IDENTIDAD"
    elif len(fallos) == len(consultas):
        estado = "ERROR_ACCESO"
    else:
        estado = "SIN_RESUMEN_EN_FUENTES"
    res["estado_propuesto"] = estado
    res["fuentes_con_resumen_coincidente"] = resumenes
    res["fuentes_con_resumen_titulo_discordante"] = discordantes
    res["fuentes_fallidas"] = fallos
    return res


# ---------------------------------------------------------------- identidad de salida

def identidad(script_sha: str, inv_sha: str) -> dict:
    return {"version": VERSION, "script_sha256": script_sha, "inventario_sha256": inv_sha}


def verificar_identidad(out: Path, ident: dict) -> None:
    p = out / "IDENTIDAD.json"
    if p.exists():
        prev = json.loads(p.read_text(encoding="utf-8"))
        if prev != ident:
            raise SystemExit("ERROR A0: la salida pertenece a otro script/inventario; usar carpeta nueva")
    else:
        escribir_atomico(p, json.dumps(ident, indent=1).encode("utf-8"))


def exportar(out: Path, resultados: list[dict]) -> dict:
    import csv
    import io
    conteos: dict[str, int] = {}
    for r in resultados:
        conteos[r["estado_propuesto"]] = conteos.get(r["estado_propuesto"], 0) + 1
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["registro_id", "estado_anterior", "estado_propuesto", "doi", "arxiv", "fuente_resumen",
                "resumen_sha256", "resumen", "fechas_json", "fuentes_fallidas", "fuentes_titulo_discordante"])
    for r in resultados:
        fuente = next((q for q in r["fuentes"] if q["fuente"] in r.get("fuentes_con_resumen_coincidente", [])), None)
        fechas = {q["fuente"]: q.get("fechas") for q in r["fuentes"] if q.get("fechas") and q.get("titulo_coincide")}
        w.writerow([r["registro_id"], r["estado_anterior"], r["estado_propuesto"], r["doi"] or "", r["arxiv"] or "",
                    fuente["fuente"] if fuente else "", fuente.get("resumen_sha256", "") if fuente else "",
                    fuente.get("resumen", "") if fuente else "", json.dumps(fechas, ensure_ascii=False),
                    ";".join(r.get("fuentes_fallidas", [])), ";".join(r.get("fuentes_con_resumen_titulo_discordante", []))])
    escribir_atomico(out / "recuperacion_a0.csv", buf.getvalue().encode("utf-8"))
    escribir_atomico(out / "recuperacion_a0.json", json.dumps(resultados, ensure_ascii=False, indent=1).encode("utf-8"))
    resumen = {"version": VERSION, "fecha_utc": ahora_utc(), "registros": len(resultados), "conteos": conteos}
    escribir_atomico(out / "RESUMEN_A0.json", json.dumps(resumen, ensure_ascii=False, indent=1).encode("utf-8"))
    return resumen


def main(argv=None, fetch=None, dormir=time.sleep) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inventario", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--reintentos", type=int, default=4)
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--limite", type=int, default=0, help="procesar solo los primeros N registros (prueba)")
    ap.add_argument("--sha-inventario", default=INVENTARIO_SHA_ESPERADO)
    a = ap.parse_args(argv)
    inv = Path(a.inventario)
    inv_sha = sha256_file(inv)
    if inv_sha != a.sha_inventario:
        print(f"ERROR A0: SHA del inventario {inv_sha} != esperado {a.sha_inventario}", file=sys.stderr)
        return 1
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    verificar_identidad(out, identidad(sha256_file(Path(__file__)), inv_sha))
    registros = json.loads(inv.read_text(encoding="utf-8"))
    if a.limite:
        registros = registros[: a.limite]
    c = Cliente(out, a.reintentos, a.timeout, fetch=fetch, dormir=dormir)
    resultados = []
    for i, reg in enumerate(registros, 1):
        resultados.append(evaluar_registro(c, reg))
        if i % 25 == 0:
            print(f"A0: {i}/{len(registros)} registros, {c.solicitudes} solicitudes nuevas", flush=True)
    resumen = exportar(out, resultados)
    print(json.dumps(resumen["conteos"], ensure_ascii=False))
    pend = sum(v for k, v in resumen["conteos"].items() if k == "ERROR_ACCESO")
    return 2 if pend else 0


if __name__ == "__main__":
    sys.exit(main())
