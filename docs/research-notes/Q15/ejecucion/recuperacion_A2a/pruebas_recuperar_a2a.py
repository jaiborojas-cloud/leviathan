#!/usr/bin/env python3
"""Pruebas sin red del ejecutor A2a. Uso: python -I pruebas_recuperar_a2a.py"""
import csv
import hashlib
import json
import socket
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import recuperar_a2a as A  # noqa: E402


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

    def cuenta(self, sub):
        return len([u for u in self.llamadas if sub in u])


PID = "a" * 40
TIT = "Deep Ensembles for Calibrated Uncertainty"
S2_ANCLA_SIN_RES = {"paperId": PID, "title": TIT, "abstract": None, "year": 2017,
                    "authors": [{"name": "Balaji Lakshminarayanan"}, {"name": "Alexander Pritzel"}],
                    "externalIds": {"DOI": "10.5555/nuevo"}}
OA_DOI = {"title": TIT, "publication_year": 2017, "publication_date": "2017-12-04",
          "authorships": [{"author": {"display_name": "Balaji Lakshminarayanan"}}],
          "abstract_inverted_index": {"Ensembles": [0], "help.": [1]}, "ids": {"doi": "https://doi.org/10.5555/nuevo"}}


def oa_busq(*works):
    return {"results": list(works)}


def oa_work(title=TIT, year=2017, autor="Balaji Lakshminarayanan", abstract=True):
    return {"title": title, "publication_year": year, "publication_date": f"{year}-01-01",
            "authorships": [{"author": {"display_name": autor}}],
            "abstract_inverted_index": {"Texto": [0], "del": [1], "autor.": [2]} if abstract else None, "ids": {}}


def inv_reg(rid="W1", titulo=TIT, fecha="2017", url=f"https://www.semanticscholar.org/paper/{PID}", doi="", ax=""):
    return {"registro_id": rid, "titulo": titulo, "estado": "PENDIENTE_ACCESO", "url_snapshot": url,
            "doi_snapshot": doi, "arxiv_snapshot": ax, "fecha_snapshot": fecha}


def a0_reg(rid="W1", estado="SIN_IDENTIFICADOR"):
    return {"registro_id": rid, "estado_propuesto": estado}


def escribir(tmp, nombre, obj):
    p = Path(tmp) / nombre
    p.write_text(json.dumps(obj), encoding="utf-8")
    return p, hashlib.sha256(p.read_bytes()).hexdigest()


class Utilidades(unittest.TestCase):
    def test_s2_id(self):
        self.assertEqual(A.s2_id_de_url(f"https://www.semanticscholar.org/paper/{PID}"), PID)
        self.assertEqual(A.s2_id_de_url(f"https://www.semanticscholar.org/paper/Algun-Titulo/{PID.upper()}"), PID)
        self.assertIsNone(A.s2_id_de_url(""))
        self.assertIsNone(A.s2_id_de_url("https://proceedings.neurips.cc/x"))

    def test_apellido_y_anio(self):
        self.assertEqual(A.apellido("José Núñez"), "nunez")
        self.assertEqual(A.apellido("B. Lakshminarayanan"), "lakshminarayanan")
        self.assertEqual(A.apellido(None), "")
        self.assertEqual(A.anio("2017-06-14"), 2017)
        self.assertIsNone(A.anio("s/f"))

    def test_texto_busqueda(self):
        self.assertEqual(A.texto_busqueda("A: <i>B</i>, C?"), "A B C")


class Ejecucion(unittest.TestCase):
    def correr(self, invs, a0s, net, extra=(), out=None, tmp=None):
        tmp = tmp or tempfile.mkdtemp()
        inv, si = escribir(tmp, "inv.json", invs)
        a0, sa = escribir(tmp, "a0.json", a0s)
        out = out or Path(tmp) / "out"
        rc = A.main(["--inventario", str(inv), "--a0", str(a0), "--out", str(out),
                     "--sha-inventario", si, "--sha-a0", sa, *extra], fetch=net, dormir=lambda s: None)
        p = out / "recuperacion_a2a.json"
        return rc, out, (json.loads(p.read_text(encoding="utf-8")) if p.exists() else None)

    def test_solo_procesa_no_recuperados_de_a0(self):
        net = FakeNet([("semanticscholar.org/graph/v1/paper/" + PID, ok(dict(S2_ANCLA_SIN_RES, abstract="Resumen.")))])
        _, _, res = self.correr([inv_reg("W1"), inv_reg("W2")], [a0_reg("W1", "RESUMEN_RECUPERADO"), a0_reg("W2")], net)
        self.assertEqual([r["registro_id"] for r in res], ["W2"])

    def test_ancla_s2_con_resumen(self):
        net = FakeNet([("paper/" + PID, ok(dict(S2_ANCLA_SIN_RES, abstract="Resumen del autor.")))])
        rc, out, res = self.correr([inv_reg()], [a0_reg()], net)
        self.assertEqual(rc, 0)
        self.assertEqual(res[0]["estado_propuesto"], "RESUMEN_RECUPERADO")
        self.assertEqual(res[0]["nivel_identidad"], A.ID_ANCLA)
        self.assertEqual(net.cuenta("openalex"), 0)  # se detiene al recuperar

    def test_ancla_da_doi_nuevo(self):
        net = FakeNet([("paper/" + PID, ok(S2_ANCLA_SIN_RES)), ("openalex.org/works/doi:10.5555/nuevo", ok(OA_DOI)),
                       ("crossref.org/works/10.5555", ok({"message": {"title": [TIT]}}))])
        _, _, res = self.correr([inv_reg()], [a0_reg()], net)
        r = res[0]
        self.assertEqual(r["estado_propuesto"], "RESUMEN_RECUPERADO")
        self.assertEqual(r["nivel_identidad"], A.ID_DERIVADO)
        self.assertEqual(r["fuentes_aceptadas"], ["openalex:doi_derivado"])

    def test_doi_derivado_con_titulo_distinto_no_se_acepta(self):
        oa = dict(OA_DOI, title="Otra obra")
        net = FakeNet([("paper/" + PID, ok(S2_ANCLA_SIN_RES)), ("works/doi:", ok(oa)),
                       ("crossref.org/works/10.5555", ok({"message": {"title": ["Otra obra"]}})),
                       ("openalex.org/works?", ok(oa_busq())), ("query.bibliographic", ok({"message": {"items": []}})),
                       ("search/match", ok({}, 404)), ("search_query", ok(b"<feed xmlns='http://www.w3.org/2005/Atom'/>"))])
        _, _, res = self.correr([inv_reg()], [a0_reg()], net)
        self.assertEqual(res[0]["estado_propuesto"], "SIN_RESUMEN_TRAS_A2A")

    def test_busqueda_exige_titulo_anio_y_primer_autor(self):
        works = [oa_work(year=2009),                       # año incompatible
                 oa_work(autor="Otra Persona"),           # primer autor distinto del ancla
                 oa_work(title=TIT + " Revisited")]       # título no idéntico
        net = FakeNet([("paper/" + PID, ok(dict(S2_ANCLA_SIN_RES, externalIds={}))),
                       ("openalex.org/works?", ok(oa_busq(*works))), ("query.bibliographic", ok({"message": {"items": []}})),
                       ("search/match", ok({}, 404)), ("search_query", ok(b"<feed xmlns='http://www.w3.org/2005/Atom'/>"))])
        _, _, res = self.correr([inv_reg()], [a0_reg()], net)
        r = res[0]
        self.assertEqual(r["estado_propuesto"], "SIN_RESUMEN_TRAS_A2A")
        rech = sorted(tuple(k["rechazo"]) for k in r["candidatos"] if k["via"] == "busqueda")
        self.assertEqual(rech, [("anio",), ("primer_autor",), ("titulo",)])

    def test_busqueda_aceptada_con_autor_de_referencia(self):
        net = FakeNet([("paper/" + PID, ok(dict(S2_ANCLA_SIN_RES, externalIds={}))),
                       ("openalex.org/works?", ok(oa_busq(oa_work(year=2018, autor="B. Lakshminarayanan"))))])
        _, _, res = self.correr([inv_reg()], [a0_reg()], net)
        r = res[0]
        self.assertEqual(r["estado_propuesto"], "RESUMEN_RECUPERADO")
        self.assertEqual(r["nivel_identidad"], A.ID_TAA)
        self.assertEqual(net.cuenta("crossref"), 0)  # se detiene tras la primera fuente con aceptado

    def test_sin_ancla_nivel_debil_y_conflicto_de_autores(self):
        url_vacia = ""
        net = FakeNet([("openalex.org/works?", ok(oa_busq(oa_work(autor="Ana Uno"))))])
        _, _, res = self.correr([inv_reg(url=url_vacia)], [a0_reg()], net)
        self.assertEqual(res[0]["nivel_identidad"], A.ID_TA)
        net2 = FakeNet([("openalex.org/works?", ok(oa_busq(oa_work(autor="Ana Uno"), oa_work(autor="Beto Dos"))))])
        _, _, res2 = self.correr([inv_reg(url=url_vacia)], [a0_reg()], net2)
        self.assertEqual(res2[0]["estado_propuesto"], "CONFLICTO_IDENTIDAD")

    def test_ancla_con_titulo_distinto_no_aporta_autores(self):
        net = FakeNet([("paper/" + PID, ok(dict(S2_ANCLA_SIN_RES, title="Otro", abstract="No usar."))),
                       ("openalex.org/works?", ok(oa_busq(oa_work(autor="Cualquiera"))))])
        _, _, res = self.correr([inv_reg()], [a0_reg()], net)
        r = res[0]
        self.assertEqual(r["nivel_identidad"], A.ID_TA)
        self.assertIn("no coincide", r["nota_ancla"])
        acept = [k for k in r["candidatos"] if k.get("aceptado")]
        self.assertTrue(all(k["fuente"] != "s2" or k["via"] != "ancla_s2" for k in acept))

    def test_fallo_parcial_es_error_acceso_y_reintento_usa_cache(self):
        tmp = tempfile.mkdtemp()
        out = Path(tmp) / "out"
        vacio = [("query.bibliographic", ok({"message": {"items": []}})), ("search/match", ok({}, 404)),
                 ("search_query", ok(b"<feed xmlns='http://www.w3.org/2005/Atom'/>"))]
        net1 = FakeNet([("paper/" + PID, ok(dict(S2_ANCLA_SIN_RES, externalIds={}))),
                        ("openalex.org/works?", ok({}, 503))] + vacio)
        rc, _, res = self.correr([inv_reg()], [a0_reg()], net1, extra=("--reintentos", "0"), out=out, tmp=tmp)
        self.assertEqual(res[0]["estado_propuesto"], "ERROR_ACCESO")
        self.assertEqual(rc, 2)
        net2 = FakeNet([("openalex.org/works?", ok(oa_busq(oa_work())))] + vacio)
        rc2, _, res2 = self.correr([inv_reg()], [a0_reg()], net2, extra=("--reintentos", "0"), out=out, tmp=tmp)
        self.assertEqual(res2[0]["estado_propuesto"], "RESUMEN_RECUPERADO")
        self.assertEqual(net2.cuenta("paper/" + PID), 0)  # el ancla final sale de la caché
        self.assertEqual(rc2, 0)

    def test_404_de_match_no_es_fallo(self):
        net = FakeNet([("paper/" + PID, ok(dict(S2_ANCLA_SIN_RES, externalIds={}))),
                       ("openalex.org/works?", ok(oa_busq())), ("query.bibliographic", ok({"message": {"items": []}})),
                       ("search/match", ok({}, 404)), ("search_query", ok(b"<feed xmlns='http://www.w3.org/2005/Atom'/>"))])
        rc, _, res = self.correr([inv_reg()], [a0_reg()], net)
        self.assertEqual(res[0]["estado_propuesto"], "SIN_RESUMEN_TRAS_A2A")
        self.assertEqual(rc, 0)

    def test_arxiv_busqueda(self):
        atom = f"""<?xml version='1.0'?><feed xmlns='http://www.w3.org/2005/Atom'><entry>
<id>http://arxiv.org/abs/1612.01474v3</id><title>Deep Ensembles for
 Calibrated Uncertainty</title><summary> Texto. </summary><published>2016-12-05T00:00:00Z</published>
<author><name>Balaji Lakshminarayanan</name></author></entry></feed>""".encode()
        net = FakeNet([("paper/" + PID, ok(dict(S2_ANCLA_SIN_RES, externalIds={}))),
                       ("openalex.org/works?", ok(oa_busq())), ("query.bibliographic", ok({"message": {"items": []}})),
                       ("search/match", ok({}, 404)), ("search_query", ok(atom))])
        _, out, res = self.correr([inv_reg()], [a0_reg()], net)
        r = res[0]
        self.assertEqual(r["estado_propuesto"], "RESUMEN_RECUPERADO")
        k = next(k for k in r["candidatos"] if k.get("aceptado") and k.get("resumen"))
        self.assertEqual(k["ids"]["arxiv"], "1612.01474")
        fila = next(csv.DictReader((out / "recuperacion_a2a.csv").open(encoding="utf-8")))
        self.assertEqual(fila["fuente_resumen"], "arxiv:busqueda")
        self.assertIn("published_v1", fila["fechas_candidatas_json"])

    def test_shas_e_identidad_de_salida(self):
        tmp = tempfile.mkdtemp()
        inv, si = escribir(tmp, "inv.json", [inv_reg()])
        a0, sa = escribir(tmp, "a0.json", [a0_reg()])
        base = ["--inventario", str(inv), "--a0", str(a0), "--out", str(Path(tmp) / "o")]
        self.assertEqual(A.main(base + ["--sha-inventario", "0" * 64, "--sha-a0", sa], fetch=FakeNet([]), dormir=lambda s: None), 1)
        self.assertEqual(A.main(base + ["--sha-inventario", si, "--sha-a0", "0" * 64], fetch=FakeNet([]), dormir=lambda s: None), 1)
        A.main(base + ["--sha-inventario", si, "--sha-a0", sa], fetch=FakeNet([]), dormir=lambda s: None)
        a0b, sab = escribir(tmp, "a0b.json", [a0_reg(), a0_reg("W1", "SIN_RESUMEN_EN_FUENTES")])
        with self.assertRaises(SystemExit):
            A.main(["--inventario", str(inv), "--a0", str(a0b), "--out", str(Path(tmp) / "o"),
                    "--sha-inventario", si, "--sha-a0", sab], fetch=FakeNet([]), dormir=lambda s: None)

    def test_registro_a0_ausente_del_inventario(self):
        rc, _, _ = self.correr([inv_reg("W1")], [a0_reg("W9")], FakeNet([]))
        self.assertEqual(rc, 1)

    def test_no_decide_pertinencia(self):
        net = FakeNet([("paper/" + PID, ok(dict(S2_ANCLA_SIN_RES, abstract="Resumen.")))])
        _, out, res = self.correr([inv_reg()], [a0_reg()], net)
        txt = json.dumps(res) + (out / "recuperacion_a2a.csv").read_text(encoding="utf-8")
        for palabra in ("INCLUIR", "EXCLUIR", "CONTEXTO", "PERTINENTE"):
            self.assertNotIn(palabra, txt)

    # --- regresiones de la auditoría de Argon sobre 081021ba (A1, M1, M2, B1, B2) ---
    def test_a1_apellido_no_latino(self):
        self.assertTrue(A.apellido("김철수"))  # no vacío (NFKD descompone el hangul en jamo)
        self.assertEqual(A.apellido("Иван Петров"), "петров")
        self.assertNotEqual(A.apellido("김철수"), A.apellido("이영희"))

    def test_a1_candidato_anonimo_se_rechaza_en_nivel_debil(self):
        anon = dict(oa_work(), authorships=[])
        net = FakeNet([("openalex.org/works?", ok(oa_busq(anon)))])
        _, _, res = self.correr([inv_reg(url="")], [a0_reg()], net)
        r = res[0]
        self.assertEqual(r["estado_propuesto"], "SIN_RESUMEN_TRAS_A2A")
        self.assertIn("primer_autor", next(k for k in r["candidatos"] if k["via"] == "busqueda")["rechazo"])

    def test_a1_conflicto_entre_fuentes_en_nivel_debil(self):
        cr = {"message": {"items": [{"title": [TIT], "author": [{"given": "Beto", "family": "Dos"}],
                                     "abstract": "<jats:p>Otro.</jats:p>", "issued": {"date-parts": [[2017]]}}]}}
        net = FakeNet([("openalex.org/works?", ok(oa_busq(oa_work(autor="Ana Uno")))), ("query.bibliographic", ok(cr))])
        _, _, res = self.correr([inv_reg(url="")], [a0_reg()], net)
        self.assertEqual(res[0]["estado_propuesto"], "CONFLICTO_IDENTIDAD")
        self.assertEqual(net.cuenta("query.bibliographic"), 1)  # no se detuvo en la primera fuente

    def test_m1_b1_crossref_anio_de_respaldo_y_nombre(self):
        k = A._cand_crossref({"title": [TIT], "author": [{"name": "Consorcio X"}],
                              "published-online": {"date-parts": [[2018, 3, 1]]}}, "busqueda")
        self.assertEqual(k["anio"], 2018)
        self.assertEqual(k["autores"], ["Consorcio X"])

    def test_m2_b2_consulta_arxiv_y_guion_bajo(self):
        self.assertEqual(A.texto_busqueda("L_2 and NOT"), "L 2 and NOT")
        self.assertEqual(A.consulta_arxiv("Search AND Rescue: on L_2 Or Not"), "ti:Search AND ti:Rescue")

    def test_gitattributes_sin_conversion(self):
        ga = AQUI.parents[4] / ".gitattributes"
        if not ga.exists():
            self.skipTest("fuera del checkout")
        self.assertIn("docs/research-notes/Q15/ejecucion/recuperacion_A2a/** -text", ga.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
