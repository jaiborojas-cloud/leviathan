"""Pruebas sintéticas de cribado_llm.py (enmienda 5). No usan datos reales, Azure ni modelos.

Uso:  python -I pruebas_sinteticas.py
Crea todo en una carpeta temporal y levanta un servidor HTTP local que imita /api/chat de Ollama.
Cada prueba corresponde a un hallazgo de las auditorías de Codex (G1-G6, M1-M5, D1; reauditoría R1-R5 y menores; tercera auditoría N1-N4).
"""
import csv, importlib.util, io, json, socket, sys, tempfile, threading, urllib.error, zipfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from types import SimpleNamespace as NS

AQUI = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("c", AQUI / "cribado_llm.py")
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
c.time.sleep = lambda s: None
FALLAS = []


def chequeo(nombre, cond):
    print(("OK   " if cond else "FALLA") + "  " + nombre)
    if not cond:
        FALLAS.append(nombre)


def sale(f, *a):
    try:
        f(*a)
    except SystemExit as e:
        return str(e)
    return None


# ---------- paquetes sintéticos con la estructura de los reales ----------
H = ["registro_id", "obra_id", "version_id", "procedencia_busqueda", "titulo", "autores", "doi", "arxiv", "url", "fecha_publica",
     "fecha_verificada", "etapa", "decision", "razon", "revisor", "fecha_utc", "conflicto", "resolucion"]


def zip_lote(ruta, crib, evid, filas, extra=None):
    with zipfile.ZipFile(ruta, "w") as z:
        s = io.StringIO(); w = csv.DictWriter(s, H); w.writeheader()
        for o, t, d, a in filas:
            w.writerow({**{k: "" for k in H}, "obra_id": o, "registro_id": o, "titulo": t, "decision": d})
        z.writestr(crib, "﻿" + s.getvalue())
        z.writestr(evid, json.dumps([{"obra_id": o, "position_id": f"p:{o}", "record": {"title": t, "abstract": a}} for o, t, d, a in filas]))
        if extra:
            z.writestr(*extra)


T = Path(tempfile.mkdtemp(prefix="q15_pruebas_"))
D = ["INCLUIR_PARA_TEXTO", "CONTEXTO", "EXCLUIR_FUERA_TEMA"]
l1 = [(f"W{i:05d}", f"Titulo {i}", D[i % 3], f"Resumen sintetico de la obra {i}.") for i in range(1, 6)]
l2 = [(f"W{i:05d}", f"Titulo {i}", D[i % 3], f"Resumen sintetico de la obra {i}.") for i in range(10, 60)] + [("W00099", "Sin resumen", "PENDIENTE_ACCESO", ",")]
l3 = [(f"W{i:05d}", f"Titulo {i}", D[i % 3], f"Resumen sintetico de la obra {i}.") for i in range(100, 200)] + [("W00300", "Titulo 150", "INCLUIR_PARA_TEXTO", "Otro resumen de la obra duplicada.")]
s = io.StringIO(); w = csv.DictWriter(s, H + ["decision_lote02_anterior"]); w.writeheader()
w.writerow({**{k: "" for k in H}, "obra_id": "W00011", "decision": "INCLUIR_PARA_TEXTO"})
zip_lote(T / "l1.zip", "cribado_lote01.csv", "evidencia_lote01.json", l1)
zip_lote(T / "l2.zip", "cribado_lote02.csv", "evidencia_lote02.json", l2)
zip_lote(T / "l3.zip", "cribado_lote03.csv", "evidencia_lote03.json", l3, ("correcciones_lote02.csv", "﻿" + s.getvalue()))
DAT = T / "datos"
c.cmd_preparar(NS(lote01=T / "l1.zip", lote02=T / "l2.zip", lote03=T / "l3.zip", datos=DAT))
REF = {d["obra_id"]: d for d in map(json.loads, open(DAT / "referencia.jsonl", encoding="utf-8"))}
c.PARTICION = DAT / "particion.json"   # en las pruebas, la partición "congelada" es la sintética

# ---------- servidor que imita Ollama ----------
MODO = {"tipo": "perfecto"}


class Ollama(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        cuerpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        usuario = cuerpo["messages"][1]["content"]
        obra = next((o for o, d in REF.items() if f"de la obra {int(o[1:])}." in usuario or (o == "W00300" and "duplicada" in usuario)), None)
        t = MODO["tipo"]
        if t == "http500":
            self.send_response(500); self.end_headers(); self.wfile.write(b"error del modelo"); return
        if t == "nojson":
            self.send_response(200); self.end_headers(); self.wfile.write(b"<html>no json</html>"); return
        dec = REF[obra]["ref"] if obra else "EXCLUIR_FUERA_TEMA"
        if t == "excluye_contexto" and dec == "CONTEXTO":
            dec = "EXCLUIR_FUERA_TEMA"
        r = {"model": cuerpo["model"], "done_reason": "stop", "total_duration": 1,
             "message": {"content": json.dumps({"decision": dec, "puntos": ["2"], "razon": "sintetica", "dudoso": False})}}
        self.send_response(200); self.end_headers(); self.wfile.write(json.dumps(r).encode())


srv = HTTPServer(("127.0.0.1", 0), Ollama)
threading.Thread(target=srv.serve_forever, daemon=True).start()
HOST = f"http://127.0.0.1:{srv.server_port}"

print("\n== G1: el mensaje de sistema es el prompt completo")
texto, h = c.prompt_sistema()
chequeo("tiene más de 8 000 caracteres", len(texto) > 8000)
chequeo("empieza con las instrucciones", texto.startswith("Eres el lector de cribado"))
chequeo("contiene secciones 1 y 6 y los dos criterios", all(x in texto for x in ["### 1.1 Diccionario", "## 6. Elegibilidad", "aplicaciones primarias", "medidas de dificultad"]))
viejo = c.PROMPT; alt = T / "prompt_alterado.md"
alt.write_text(viejo.read_text(encoding="utf-8").replace("Eres el lector", "Eres un lector"), encoding="utf-8")
c.PROMPT = alt; chequeo("un prompt alterado se rechaza", sale(c.prompt_sistema) is not None); c.PROMPT = viejo

print("\n== G2: validación completa del esquema")
v = '{"decision":"CONTEXTO","puntos":["1"],"razon":"x","dudoso":false}'
chequeo("acepta una respuesta correcta", c.interpretar(v) is not None)
for nombre, malo in [("sin puntos", '{"decision":"CONTEXTO","razon":"x","dudoso":false}'),
                     ("puntos no lista", '{"decision":"CONTEXTO","puntos":"INVALID","razon":"x","dudoso":false}'),
                     ("punto inexistente", '{"decision":"CONTEXTO","puntos":["99"],"razon":"x","dudoso":false}'),
                     ("clave extra", '{"decision":"CONTEXTO","puntos":[],"razon":"x","dudoso":false,"otra":1}'),
                     ("razón vacía", '{"decision":"CONTEXTO","puntos":[],"razon":" ","dudoso":false}'),
                     ("dudoso no booleano", '{"decision":"CONTEXTO","puntos":[],"razon":"x","dudoso":"no"}'),
                     ("decisión fuera de la lista", '{"decision":"PENDIENTE_ACCESO","puntos":[],"razon":"x","dudoso":false}')]:
    chequeo(f"rechaza {nombre}", c.interpretar(malo) is None)

print("\n== M1: clasificación de errores")
MODO["tipo"] = "http500"
r = c.llamar(HOST, c.CONFIGS["C1"], "s", "u", False); chequeo("HTTP 500 -> INVALIDA con error", r.get("error", "").startswith("HTTPError"))
MODO["tipo"] = "nojson"
r = c.llamar(HOST, c.CONFIGS["C1"], "s", "u", False); chequeo("cuerpo no JSON -> INVALIDA con error", r.get("error", "").startswith("respuesta no JSON"))
chequeo("URLError(timeout) cuenta como timeout del modelo", c.es_timeout(urllib.error.URLError(socket.timeout("timed out"))))
chequeo("sin conexión -> se detiene", sale(c.llamar, "http://127.0.0.1:9", c.CONFIGS["C1"], "s", "u", False) is not None)
MODO["tipo"] = "perfecto"

print("\n== M2: extractor de resúmenes")
p = DAT / "particion.json"; part = json.loads(p.read_text(encoding="utf-8"))
chequeo("el resumen ',' no cuenta y su obra queda fuera", "W00099" not in REF and part["fuera"] == {"PENDIENTE_ACCESO": 1})
chequeo("un resumen corto con texto sí cuenta", c.tiene_texto("A short abstract.") and not c.tiene_texto(" , "))
zipf = T / "malo.zip"
with zipfile.ZipFile(zipf, "w") as z:
    z.writestr("evidencia_lote01.json", json.dumps({"obra_id": "W1", "records": [{"abstract": "x"}]}))
chequeo("una estructura inesperada se rechaza", sale(c.resumenes_de_evidencia, zipf, "evidencia_lote01.json") is not None)
chequeo("los duplicados de título quedan en la misma mitad", REF["W00150"]["mitad"] == REF["W00300"]["mitad"])

print("\n== M3: mediana")
chequeo("mediana([1, 100]) = 50.5", c.mediana([1, 100]) == 50.5)
chequeo("mediana([3, 1, 2]) = 2", c.mediana([3, 1, 2]) == 2)

from datetime import datetime, timedelta, timezone
_ini = datetime.now(timezone.utc) - timedelta(hours=1)
F = lambda t: t.strftime("%Y-%m-%dT%H:%M:%SZ")
PRESUPUESTO_VIGENTE = json.dumps({"inicio_utc": F(_ini), "limite_utc": F(_ini + timedelta(hours=24)), "horas": 24})
print("\n== Flujo oficial completo con un modelo que reproduce la referencia")
(DAT / "presupuesto.json").write_text(PRESUPUESTO_VIGENTE, encoding="utf-8")
c.cmd_probar(NS(datos=DAT, host=HOST, simular=False, hasta=None))
for cfg in c.CONFIGS:
    c.cmd_etiquetar(NS(entrada=DAT / "entrada_seleccion.jsonl", config=cfg, datos=DAT, host=HOST, simular=False, hasta=None))
chequeo("elegir termina", sale(c.cmd_elegir, NS(datos=DAT, prueba=False)) is None)
el = json.loads((DAT / "eleccion.json").read_text(encoding="utf-8"))
chequeo("eleccion: ELEGIDA C1 (empate perfecto -> primer criterio que desempata)", el["veredicto"] == "ELEGIDA" and el["elegida"] == "C1")
c.cmd_etiquetar(NS(entrada=DAT / "entrada_validacion.jsonl", config="C1", datos=DAT, host=HOST, simular=False, hasta=None))
sale(c.cmd_validar, NS(datos=DAT, prueba=False))
ve = json.loads((DAT / "veredicto.json").read_text(encoding="utf-8"))
chequeo("veredicto APTO", ve["veredicto"] == "APTO")
chequeo("se guardó una copia con fecha", len(list(DAT.glob("veredicto_*.json"))) >= 1)

print("\n== G3: no se mezclan corridas ni simulaciones")
sv = DAT / "salida_validacion_C1.jsonl"; original = sv.read_bytes()
filas = [json.loads(l) for l in original.decode().splitlines()]
filas[0]["config"] = "C4"
sv.write_text("\n".join(json.dumps(f) for f in filas) + "\n", encoding="utf-8")
chequeo("reanudar con una fila de otra configuración se detiene",
        sale(c.cmd_etiquetar, NS(entrada=DAT / "entrada_validacion.jsonl", config="C1", datos=DAT, host=HOST, simular=False, hasta=None)) is not None)
sale(c.cmd_validar, NS(datos=DAT, prueba=False))
chequeo("validar con una fila ajena da INCONCLUSIVO", json.loads((DAT / "veredicto.json").read_text(encoding="utf-8"))["veredicto"] == "INCONCLUSIVO")
sv.unlink()
c.cmd_etiquetar(NS(entrada=DAT / "entrada_validacion.jsonl", config="C1", datos=DAT, host=HOST, simular=True, hasta=None))
sale(c.cmd_validar, NS(datos=DAT, prueba=False))
chequeo("una salida simulada da INCONCLUSIVO en modo oficial", json.loads((DAT / "veredicto.json").read_text(encoding="utf-8"))["veredicto"] == "INCONCLUSIVO")
sv.write_bytes(original)

print("\n== G4: un intento fallido reemplaza el veredicto anterior")
sale(c.cmd_validar, NS(datos=DAT, prueba=False))
chequeo("antes: APTO", json.loads((DAT / "veredicto.json").read_text(encoding="utf-8"))["veredicto"] == "APTO")
sv.rename(DAT / "aparte.jsonl")
sale(c.cmd_validar, NS(datos=DAT, prueba=False))
ve = json.loads((DAT / "veredicto.json").read_text(encoding="utf-8"))
chequeo("falta la salida: el veredicto vigente pasa a INCONCLUSIVO", ve["veredicto"] == "INCONCLUSIVO" and "falta" in ve["motivo"])
(DAT / "aparte.jsonl").rename(sv)

print("\n== M5: referencia alterada")
rf = DAT / "referencia.jsonl"; ref_orig = rf.read_bytes()
rf.write_bytes(ref_orig.replace(b'"EXCLUIR_FUERA_TEMA"', b'"CONTEXTO"', 1))
sale(c.cmd_validar, NS(datos=DAT, prueba=False))
chequeo("una referencia que no es la congelada da INCONCLUSIVO", json.loads((DAT / "veredicto.json").read_text(encoding="utf-8"))["veredicto"] == "INCONCLUSIVO")
rf.write_bytes(ref_orig)

print("\n== G6: presupuesto de tiempo")
(DAT / "presupuesto.json").write_text('{"inicio_utc":"2000-01-01T00:00:00Z","limite_utc":"2000-01-02T00:00:00Z","horas":24}', encoding="utf-8")
sale(c.cmd_validar, NS(datos=DAT, prueba=False))
chequeo("filas etiquetadas después del límite dan INCONCLUSIVO", json.loads((DAT / "veredicto.json").read_text(encoding="utf-8"))["veredicto"] == "INCONCLUSIVO")
(DAT / "presupuesto.json").unlink()
sale(c.cmd_validar, NS(datos=DAT, prueba=False))
chequeo("sin presupuesto.json, INCONCLUSIVO en modo oficial", json.loads((DAT / "veredicto.json").read_text(encoding="utf-8"))["veredicto"] == "INCONCLUSIVO")
(DAT / "presupuesto.json").write_text(PRESUPUESTO_VIGENTE, encoding="utf-8")

print("\n== D1: excluir CONTEXTO cuenta como omisión")
MODO["tipo"] = "excluye_contexto"; sv.unlink()
c.cmd_etiquetar(NS(entrada=DAT / "entrada_validacion.jsonl", config="C1", datos=DAT, host=HOST, simular=False, hasta=None))
sale(c.cmd_validar, NS(datos=DAT, prueba=False))
ve = json.loads((DAT / "veredicto.json").read_text(encoding="utf-8"))
n_ctx = sum(1 for d in REF.values() if d["mitad"] == "validacion" and d["ref"] == "CONTEXTO")
chequeo(f"{n_ctx} CONTEXTO excluidas -> {n_ctx} omisiones y NO_APTO", ve["metricas"]["omisiones"] == n_ctx > 0 and ve["veredicto"] == "NO_APTO")
MODO["tipo"] = "perfecto"

print("\n== Desalojo: línea cortada a la mitad")
datos = sv.read_bytes(); sv.write_bytes(datos[:-40])
c.cmd_etiquetar(NS(entrada=DAT / "entrada_validacion.jsonl", config="C1", datos=DAT, host=HOST, simular=False, hasta=None))
validas = sum(1 for l in sv.read_text(encoding="utf-8").splitlines() if l.strip().endswith("}"))
chequeo("se rehace la obra cortada sin pegarla a la línea rota", validas == sum(1 for d in REF.values() if d["mitad"] == "validacion"))

print("\n== NO_EVALUADAS: una configuración que no pasa 'probar' no compite")
pj = json.loads((DAT / "probar.json").read_text(encoding="utf-8")); pj["validas"] = ["C2", "C3"]
(DAT / "probar.json").write_text(json.dumps(pj), encoding="utf-8")
sale(c.cmd_elegir, NS(datos=DAT, prueba=False))
el = json.loads((DAT / "eleccion.json").read_text(encoding="utf-8"))
chequeo("C1 y C4 quedan NO_EVALUADAS; elige entre C2 y C3", el["no_evaluadas"] == ["C1", "C4"] and el["elegida"] == "C2")

print("\n== Reauditoría R1: el evaluador exige la versión congelada y coherencia de cada fila")
# estado limpio: las pruebas anteriores dejaron elegida C2 y una línea rota en la salida de validación
pj = json.loads((DAT / "probar.json").read_text(encoding="utf-8")); pj["validas"] = list(c.CONFIGS)
(DAT / "probar.json").write_text(json.dumps(pj), encoding="utf-8")
sale(c.cmd_elegir, NS(datos=DAT, prueba=False))
MODO["tipo"] = "perfecto"; sv.unlink()
c.cmd_etiquetar(NS(entrada=DAT / "entrada_validacion.jsonl", config="C1", datos=DAT, host=HOST, simular=False, hasta=None))
sale(c.cmd_validar, NS(datos=DAT, prueba=False))
chequeo("punto de partida: APTO", json.loads((DAT / "veredicto.json").read_text(encoding="utf-8"))["veredicto"] == "APTO")
original = sv.read_bytes()
def con_fila(cambio):
    filas = [json.loads(l) for l in original.decode().splitlines()]
    cambio(filas[0]); sv.write_text("\n".join(json.dumps(f) for f in filas) + "\n", encoding="utf-8")
    sale(c.cmd_validar, NS(datos=DAT, prueba=False)); sv.write_bytes(original)
    return json.loads((DAT / "veredicto.json").read_text(encoding="utf-8"))["veredicto"]
chequeo("script_sha256 desconocido -> INCONCLUSIVO", con_fila(lambda f: f.update(script_sha256="0" * 64)) == "INCONCLUSIVO")
chequeo("modelo_respuesta distinto -> INCONCLUSIVO", con_fila(lambda f: f.update(modelo_respuesta="otro-modelo")) == "INCONCLUSIVO")
chequeo("crudo que no es JSON con decisión tabulada -> INCONCLUSIVO", con_fila(lambda f: f.update(crudo="no es json")) == "INCONCLUSIVO")
chequeo("decisión tabulada distinta de la cruda -> INCONCLUSIVO", con_fila(lambda f: f.update(decision="CONTEXTO" if f["decision"] != "CONTEXTO" else "INCLUIR_PARA_TEXTO")) == "INCONCLUSIVO")
chequeo("think=0 y simulado=0 (tipos) -> INCONCLUSIVO", con_fila(lambda f: f.update(think=0, simulado=0)) == "INCONCLUSIVO")
chequeo("obra repetida -> INCONCLUSIVO", con_fila(lambda f: None) == "APTO" and (sv.write_bytes(original + original.splitlines(True)[0]) or True)
        and (sale(c.cmd_validar, NS(datos=DAT, prueba=False)) or True) and json.loads((DAT / "veredicto.json").read_text(encoding="utf-8"))["veredicto"] == "INCONCLUSIVO")
sv.write_bytes(original)

print("\n== Reauditoría R2: un archivo de estado roto no deja vigente un APTO viejo")
sale(c.cmd_validar, NS(datos=DAT, prueba=False))
el_orig = (DAT / "eleccion.json").read_bytes(); (DAT / "eleccion.json").write_text("{", encoding="utf-8")
sale(c.cmd_validar, NS(datos=DAT, prueba=False))
ve = json.loads((DAT / "veredicto.json").read_text(encoding="utf-8"))
chequeo("eleccion.json = '{' -> veredicto vigente INCONCLUSIVO con el motivo", ve["veredicto"] == "INCONCLUSIVO" and "JSONDecodeError" in ve["motivo"])
(DAT / "eleccion.json").write_bytes(el_orig)

print("\n== Reauditoría R3: dos intentos en el mismo segundo conservan dos copias")
antes = len(list(DAT.glob("veredicto_*.json"))); reloj = c.ahora; c.ahora = lambda: "2026-11-06T12:00:00Z"
sale(c.cmd_validar, NS(datos=DAT, prueba=False)); sale(c.cmd_validar, NS(datos=DAT, prueba=False)); c.ahora = reloj
chequeo("dos copias nuevas, ninguna sobrescrita", len(list(DAT.glob("veredicto_*.json"))) == antes + 2)

print("\n== Reauditoría R4: corte a mitad de un carácter UTF-8")
sv.write_bytes(original + b'{"razon":"\xc3')
c.cmd_etiquetar(NS(entrada=DAT / "entrada_validacion.jsonl", config="C1", datos=DAT, host=HOST, simular=False, hasta=None))
sale(c.cmd_validar, NS(datos=DAT, prueba=False))
chequeo("se reanuda sin UnicodeDecodeError y el veredicto vuelve a APTO", json.loads((DAT / "veredicto.json").read_text(encoding="utf-8"))["veredicto"] == "APTO")
cortada = original.splitlines(True); sv.write_bytes(b"".join(cortada[:-1]) + cortada[-1][:25] + "é".encode()[:1])
c.cmd_etiquetar(NS(entrada=DAT / "entrada_validacion.jsonl", config="C1", datos=DAT, host=HOST, simular=False, hasta=None))
sale(c.cmd_validar, NS(datos=DAT, prueba=False))
chequeo("la obra cortada a mitad de carácter se rehace y el veredicto es APTO", json.loads((DAT / "veredicto.json").read_text(encoding="utf-8"))["veredicto"] == "APTO")
sv.write_bytes(original)

print("\n== Reauditoría R5: --hasta no empieza obras pasado el límite")
sv.unlink()
msg = sale(c.cmd_etiquetar, NS(entrada=DAT / "entrada_validacion.jsonl", config="C1", datos=DAT, host=HOST, simular=False, hasta="2000-01-01T00:00:00Z"))
chequeo("límite vencido: se detiene sin escribir filas", msg is not None and "límite" in msg and (not sv.exists() or sv.read_bytes() == b""))
sv.write_bytes(original)

print("\n== Menores de la reauditoría")
chequeo("'___' no cuenta como resumen", not c.tiene_texto("___") and c.tiene_texto("ñ"))
chequeo("el esquema enviado prohíbe claves extra", c.ESQUEMA.get("additionalProperties") is False)
pj = json.loads((DAT / "probar.json").read_text(encoding="utf-8")); pj["validas"] = ["C2", "C1"]
(DAT / "probar.json").write_text(json.dumps(pj), encoding="utf-8")
for cfg in ("C1", "C2"):
    f = DAT / f"salida_seleccion_{cfg}.jsonl"
    f.write_text("\n".join(json.dumps({**json.loads(l), "segundos": 1.0}) for l in f.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
sale(c.cmd_elegir, NS(datos=DAT, prueba=False))
chequeo("empate total con validas=[C2, C1] -> elige C1", json.loads((DAT / "eleccion.json").read_text(encoding="utf-8"))["elegida"] == "C1")

print("\n== Tercera auditoría N1: presupuesto y horas como fechas reales")
# la prueba del desempate alteró los tiempos de C1 y C2; aquí se fija C1 como única evaluada
pj = json.loads((DAT / "probar.json").read_text(encoding="utf-8")); pj["validas"] = ["C1"]
(DAT / "probar.json").write_text(json.dumps(pj), encoding="utf-8"); sale(c.cmd_elegir, NS(datos=DAT, prueba=False))
sale(c.cmd_validar, NS(datos=DAT, prueba=False))
chequeo("punto de partida: APTO", json.loads((DAT / "veredicto.json").read_text(encoding="utf-8"))["veredicto"] == "APTO")
def con_presupuesto(txt):
    (DAT / "presupuesto.json").write_text(txt, encoding="utf-8"); sale(c.cmd_validar, NS(datos=DAT, prueba=False))
    (DAT / "presupuesto.json").write_text(PRESUPUESTO_VIGENTE, encoding="utf-8")
    return json.loads((DAT / "veredicto.json").read_text(encoding="utf-8"))["veredicto"]
pv = json.loads(PRESUPUESTO_VIGENTE)
chequeo("limite_utc null -> INCONCLUSIVO", con_presupuesto(json.dumps({**pv, "limite_utc": None})) == "INCONCLUSIVO")
chequeo("límite con fecha imposible -> INCONCLUSIVO", con_presupuesto(json.dumps({**pv, "limite_utc": "2026-00-00T99:99:99Z"})) == "INCONCLUSIVO")
chequeo("presupuesto de 48 h -> INCONCLUSIVO", con_presupuesto(json.dumps({**pv, "horas": 48})) == "INCONCLUSIVO")
chequeo("límite movido 1 h -> INCONCLUSIVO", con_presupuesto(json.dumps({**pv, "limite_utc": F(datetime.strptime(pv["limite_utc"], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=1))})) == "INCONCLUSIVO")
chequeo("fila antes del inicio -> INCONCLUSIVO", con_presupuesto(json.dumps({"inicio_utc": F(_ini + timedelta(hours=2)), "limite_utc": F(_ini + timedelta(hours=26)), "horas": 24})) == "INCONCLUSIVO")
original = sv.read_bytes()
chequeo("hora de fila imposible -> INCONCLUSIVO", con_fila(lambda f: f.update(utc="2026-00-00T99:99:99Z")) == "INCONCLUSIVO")
_ap = c.argparse.ArgumentParser(); _ap.add_argument("--hasta", type=c.arg_fecha)
chequeo("--hasta inválido se rechaza en la línea de comandos", sale(_ap.parse_args, ["--hasta", "not-a-date"]) is not None and _ap.parse_args(["--hasta", "2026-11-07T00:00:00Z"]).hasta == "2026-11-07T00:00:00Z")

print("\n== Tercera auditoría N2: duraciones inválidas")
chequeo("segundos negativos -> INCONCLUSIVO", con_fila(lambda f: f.update(segundos=-1)) == "INCONCLUSIVO")
filas = original.decode().splitlines(); filas[0] = filas[0].replace('"segundos": ', '"segundos": NaN, "x_": ', 1)
sv.write_text("\n".join(filas) + "\n", encoding="utf-8"); sale(c.cmd_validar, NS(datos=DAT, prueba=False)); sv.write_bytes(original)
chequeo("segundos NaN -> la línea no se acepta y el veredicto es INCONCLUSIVO", json.loads((DAT / "veredicto.json").read_text(encoding="utf-8"))["veredicto"] == "INCONCLUSIVO")
pj = json.loads((DAT / "probar.json").read_text(encoding="utf-8")); pj["validas"] = ["C1", "C2"]
(DAT / "probar.json").write_text(json.dumps(pj), encoding="utf-8")
f2 = DAT / "salida_seleccion_C2.jsonl"; o2 = f2.read_bytes()
f2.write_text("\n".join(json.dumps({**json.loads(l), "segundos": -1}) for l in o2.decode().splitlines()) + "\n", encoding="utf-8")
sale(c.cmd_elegir, NS(datos=DAT, prueba=False)); el = json.loads((DAT / "eleccion.json").read_text(encoding="utf-8")); f2.write_bytes(o2)
chequeo("segundos=-1 en C2 ya no gana el desempate: la elección es INCONCLUSIVO", el["veredicto"] == "INCONCLUSIVO")
pj["validas"] = ["C1"]; (DAT / "probar.json").write_text(json.dumps(pj), encoding="utf-8"); sale(c.cmd_elegir, NS(datos=DAT, prueba=False))

print("\n== Tercera auditoría N3: las líneas descartadas se reportan")
sv.write_bytes(b"{garbage}\n" + original); sale(c.cmd_validar, NS(datos=DAT, prueba=False))
ve = json.loads((DAT / "veredicto.json").read_text(encoding="utf-8")); sv.write_bytes(original)
chequeo("una línea basura queda en metricas.lineas_descartadas con número, hash y motivo",
        ve["veredicto"] == "APTO" and len(ve["metricas"]["lineas_descartadas"]) == 1 and ve["metricas"]["lineas_descartadas"][0]["linea"] == 1
        and len(ve["metricas"]["lineas_descartadas"][0]["sha256"]) == 64)
sv.write_bytes(original)

print("\n== Revisión acotada: un INCONCLUSIVO por obras faltantes conserva las líneas descartadas")
sv.write_bytes(b"{garbage}\n" + b"".join(original.splitlines(True)[1:])); sale(c.cmd_validar, NS(datos=DAT, prueba=False))
ve = json.loads((DAT / "veredicto.json").read_text(encoding="utf-8")); sv.write_bytes(original)
d = (ve.get("lineas_descartadas") or {}).get(sv.name, [])
chequeo("INCONCLUSIVO por 1 obra faltante, con la línea basura descartada en el estado",
        ve["veredicto"] == "INCONCLUSIVO" and "faltan 1 obras" in ve["motivo"] and len(d) == 1 and d[0]["linea"] == 1 and len(d[0]["sha256"]) == 64)

print(f"\n{'TODAS LAS PRUEBAS PASAN' if not FALLAS else 'FALLAN: ' + ', '.join(FALLAS)}  (carpeta: {T})")
sys.exit(1 if FALLAS else 0)
