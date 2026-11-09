#!/usr/bin/env python3
"""Pruebas sin red del ejecutor A0. Uso: python -I pruebas_recuperar_a0.py"""
import hashlib
import json
import socket
import sys
import tempfile
import unittest
from pathlib import Path, PureWindowsPath

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import recuperar_a0 as A  # noqa: E402


def _sin_red(*a, **k):
    raise AssertionError("las pruebas no deben usar la red")


socket.socket.connect = _sin_red  # bloqueo de red


def ok(obj, status=200):
    body = obj if isinstance(obj, bytes) else json.dumps(obj).encode()
    return status, {}, body, "u"


class FakeNet:
    def __init__(self, rutas):
        self.rutas = rutas  # lista de (subcadena_url, respuesta | lista de respuestas)
        self.llamadas = []

    def __call__(self, url, timeout):
        self.llamadas.append(url)
        for sub, resp in self.rutas:
            if sub in url:
                if isinstance(resp, list):
                    return resp.pop(0) if len(resp) > 1 else resp[0]
                return resp
        return 404, {}, b"{}", url


TIT = "On Calibration of Modern Neural Networks"
OA = {"title": TIT, "authorships": [{"author": {"display_name": "Chuan Guo"}}],
      "abstract_inverted_index": {"Confidence": [0], "calibration": [1], "matters.": [2]}, "publication_date": "2017-06-14"}
CR = {"message": {"title": [TIT], "author": [{"given": "Chuan", "family": "Guo"}],
                  "abstract": "<jats:p>Confidence <jats:italic>calibration</jats:italic> matters.</jats:p>",
                  "created": {"date-parts": [[2017, 6, 14]]}}}
S2 = {"title": TIT, "abstract": None, "authors": [{"name": "Chuan Guo"}], "year": 2017, "publicationDate": "2017-06-14"}


def inventario(tmp, regs):
    p = Path(tmp) / "inv.json"
    p.write_text(json.dumps(regs), encoding="utf-8")
    return p, hashlib.sha256(p.read_bytes()).hexdigest()


def reg(rid="W1", doi="10.1/x", ax="", titulo=TIT, estado="PENDIENTE_ACCESO"):
    return {"registro_id": rid, "doi_snapshot": doi, "arxiv_snapshot": ax, "titulo": titulo, "estado": estado}


class Utilidades(unittest.TestCase):
    def test_inverted_index(self):
        self.assertEqual(A.reconstruir_inverted_index({"b": [1], "a": [0, 2]}), "a b a")
        self.assertIsNone(A.reconstruir_inverted_index(None))
        self.assertIsNone(A.reconstruir_inverted_index({}))

    def test_jats(self):
        self.assertEqual(A.limpiar_jats("<jats:title>Abstract</jats:title><jats:p>A &amp; B</jats:p>"), "A & B")
        self.assertIsNone(A.limpiar_jats("<jats:p> </jats:p>"))

    def test_normalizar_titulo(self):
        self.assertEqual(A.normalizar_titulo("Él <i>Café</i>: A–B!"), A.normalizar_titulo("el cafe a b"))
        self.assertEqual(A.normalizar_titulo(None), "")

    def test_rel_posix_windows(self):
        self.assertEqual(PureWindowsPath(r"raw\abc\intento_01.body").as_posix(), "raw/abc/intento_01.body")


class Ejecucion(unittest.TestCase):
    def correr(self, regs, net, extra=()):
        tmp = tempfile.mkdtemp()
        inv, sha = inventario(tmp, regs)
        out = Path(tmp) / "out"
        rc = A.main(["--inventario", str(inv), "--out", str(out), "--sha-inventario", sha, *extra],
                    fetch=net, dormir=lambda s: None)
        res = json.loads((out / "recuperacion_a0.json").read_text(encoding="utf-8")) if (out / "recuperacion_a0.json").exists() else None
        return rc, out, res, inv, sha

    def test_recupera_con_titulo_coincidente(self):
        net = FakeNet([("openalex", ok(OA)), ("crossref", ok(CR)), ("semanticscholar", ok(S2))])
        rc, out, res, *_ = self.correr([reg()], net)
        self.assertEqual(rc, 0)
        r = res[0]
        self.assertEqual(r["estado_propuesto"], "RESUMEN_RECUPERADO")
        self.assertEqual(set(r["fuentes_con_resumen_coincidente"]), {"openalex", "crossref"})
        oa = next(q for q in r["fuentes"] if q["fuente"] == "openalex")
        self.assertEqual(oa["resumen"], "Confidence calibration matters.")
        cr = next(q for q in r["fuentes"] if q["fuente"] == "crossref")
        self.assertEqual(cr["resumen"], "Confidence calibration matters.")
        self.assertEqual(cr["fechas"]["created"], "2017-6-14")
        csv = (out / "recuperacion_a0.csv").read_text(encoding="utf-8")
        self.assertIn("RESUMEN_RECUPERADO", csv)

    def test_titulo_discordante_es_conflicto(self):
        oa = dict(OA, title="Otro artículo distinto")
        net = FakeNet([("openalex", ok(oa)), ("crossref", ok({"message": {"title": ["Otro"]}})), ("semanticscholar", ok({}, 404))])
        rc, out, res, *_ = self.correr([reg()], net)
        self.assertEqual(res[0]["estado_propuesto"], "CONFLICTO_IDENTIDAD")
        self.assertEqual(res[0]["fuentes_con_resumen_titulo_discordante"], ["openalex"])

    def test_sin_resumen(self):
        oa = dict(OA, abstract_inverted_index=None)
        cr = {"message": {"title": [TIT]}}
        net = FakeNet([("openalex", ok(oa)), ("crossref", ok(cr)), ("semanticscholar", ok(S2))])
        _, _, res, *_ = self.correr([reg()], net)
        self.assertEqual(res[0]["estado_propuesto"], "SIN_RESUMEN_EN_FUENTES")

    def test_sin_identificador_no_consulta(self):
        net = FakeNet([])
        _, _, res, *_ = self.correr([reg(doi="", ax="")], net)
        self.assertEqual(res[0]["estado_propuesto"], "SIN_IDENTIFICADOR")
        self.assertEqual(net.llamadas, [])

    def test_429_reintenta_y_conserva_intentos(self):
        net = FakeNet([("openalex", [(429, {"Retry-After": "1"}, b"x", "u"), ok(OA)]),
                       ("crossref", ok(CR)), ("semanticscholar", ok(S2))])
        rc, out, res, *_ = self.correr([reg()], net)
        oa_calls = [u for u in net.llamadas if "openalex" in u]
        self.assertEqual(len(oa_calls), 2)
        metas = [json.loads(p.read_text(encoding="utf-8")) for p in (out / "raw").glob("*/meta.json")]
        m = next(m for m in metas if m["fuente"] == "openalex")
        self.assertEqual([i["status"] for i in m["intentos"]], [429, 200])
        self.assertTrue(all("\\" not in i["cuerpo"] for i in m["intentos"]))

    def test_todo_falla_error_acceso_codigo_2(self):
        net = FakeNet([("openalex", ok({}, 503)), ("crossref", ok({}, 503)), ("semanticscholar", ok({}, 503))])
        rc, out, res, *_ = self.correr([reg()], net, extra=("--reintentos", "1"))
        self.assertEqual(res[0]["estado_propuesto"], "ERROR_ACCESO")
        self.assertEqual(rc, 2)

    def test_cache_no_repite_y_reintento_no_sobrescribe(self):
        tmp = tempfile.mkdtemp()
        inv, sha = inventario(tmp, [reg()])
        out = Path(tmp) / "out"
        net1 = FakeNet([("openalex", ok({}, 503)), ("crossref", ok(CR)), ("semanticscholar", ok(S2))])
        A.main(["--inventario", str(inv), "--out", str(out), "--sha-inventario", sha, "--reintentos", "0"], fetch=net1, dormir=lambda s: None)
        net2 = FakeNet([("openalex", ok(OA)), ("crossref", ok(CR)), ("semanticscholar", ok(S2))])
        A.main(["--inventario", str(inv), "--out", str(out), "--sha-inventario", sha, "--reintentos", "0"], fetch=net2, dormir=lambda s: None)
        self.assertEqual([u for u in net2.llamadas if "crossref" in u], [])  # final en caché
        self.assertEqual(len([u for u in net2.llamadas if "openalex" in u]), 1)  # transitorio se reintenta
        m = next(json.loads(p.read_text(encoding="utf-8")) for p in (out / "raw").glob("*/meta.json")
                 if json.loads(p.read_text(encoding="utf-8"))["fuente"] == "openalex")
        self.assertEqual([i["n"] for i in m["intentos"]], [1, 2])
        self.assertEqual([i["status"] for i in m["intentos"]], [503, 200])

    def test_sha_inventario_incorrecto(self):
        tmp = tempfile.mkdtemp()
        inv, _ = inventario(tmp, [reg()])
        rc = A.main(["--inventario", str(inv), "--out", str(Path(tmp) / "o"), "--sha-inventario", "0" * 64],
                    fetch=FakeNet([]), dormir=lambda s: None)
        self.assertEqual(rc, 1)

    def test_identidad_de_salida(self):
        tmp = tempfile.mkdtemp()
        inv1, sha1 = inventario(tmp, [reg()])
        out = Path(tmp) / "out"
        net = FakeNet([("openalex", ok(OA)), ("crossref", ok(CR)), ("semanticscholar", ok(S2))])
        A.main(["--inventario", str(inv1), "--out", str(out), "--sha-inventario", sha1], fetch=net, dormir=lambda s: None)
        inv2 = Path(tmp) / "inv2.json"
        inv2.write_text(json.dumps([reg(rid="W2")]), encoding="utf-8")
        sha2 = hashlib.sha256(inv2.read_bytes()).hexdigest()
        with self.assertRaises(SystemExit):
            A.main(["--inventario", str(inv2), "--out", str(out), "--sha-inventario", sha2], fetch=net, dormir=lambda s: None)

    def test_arxiv_fechas(self):
        atom = b"""<?xml version='1.0'?><feed xmlns='http://www.w3.org/2005/Atom'><entry>
<title>On Calibration of
 Modern Neural Networks</title><summary> Confidence matters. </summary>
<published>2017-06-14T00:00:00Z</published><updated>2017-08-03T00:00:00Z</updated>
<author><name>Chuan Guo</name></author></entry></feed>"""
        net = FakeNet([("arxiv.org", ok(atom))])
        _, _, res, *_ = self.correr([reg(doi="", ax="1706.04599", estado="PENDIENTE_FECHA")], net)
        r = res[0]
        self.assertEqual(r["estado_propuesto"], "RESUMEN_RECUPERADO")
        q = r["fuentes"][0]
        self.assertEqual(q["fechas"]["published_v1"], "2017-06-14T00:00:00Z")
        self.assertEqual(q["resumen"], "Confidence matters.")

    def test_no_decide_pertinencia(self):
        net = FakeNet([("openalex", ok(OA)), ("crossref", ok(CR)), ("semanticscholar", ok(S2))])
        _, _, res, *_ = self.correr([reg()], net)
        txt = json.dumps(res)
        for palabra in ("INCLUIR", "EXCLUIR", "CONTEXTO", "PERTINENTE"):
            self.assertNotIn(palabra, txt)


if __name__ == "__main__":
    unittest.main(verbosity=2)
