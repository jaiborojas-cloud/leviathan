"""Pruebas sintéticas de cribado_llm.py (enmienda 2). No usan datos reales, Azure ni modelos.

Uso:  python -I pruebas_sinteticas.py
Crea todo en una carpeta temporal y levanta un servidor HTTP local que imita /api/chat de Ollama.
Cada prueba corresponde a un hallazgo de la auditoría de Codex (G1-G6, M1-M5, D1).
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

print("\n== Flujo oficial completo con un modelo que reproduce la referencia")
(DAT / "presupuesto.json").write_text('{"inicio_utc":"2000-01-01T00:00:00Z","limite_utc":"2999-01-01T00:00:00Z","horas":24}', encoding="utf-8")
c.cmd_probar(NS(datos=DAT, host=HOST, simular=False))
for cfg in c.CONFIGS:
    c.cmd_etiquetar(NS(entrada=DAT / "entrada_seleccion.jsonl", config=cfg, datos=DAT, host=HOST, simular=False))
chequeo("elegir termina", sale(c.cmd_elegir, NS(datos=DAT, prueba=False)) is None)
el = json.loads((DAT / "eleccion.json").read_text(encoding="utf-8"))
chequeo("eleccion: ELEGIDA C1 (empate perfecto -> primer criterio que desempata)", el["veredicto"] == "ELEGIDA" and el["elegida"] == "C1")
c.cmd_etiquetar(NS(entrada=DAT / "entrada_validacion.jsonl", config="C1", datos=DAT, host=HOST, simular=False))
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
        sale(c.cmd_etiquetar, NS(entrada=DAT / "entrada_validacion.jsonl", config="C1", datos=DAT, host=HOST, simular=False)) is not None)
sale(c.cmd_validar, NS(datos=DAT, prueba=False))
chequeo("validar con una fila ajena da INCONCLUSIVO", json.loads((DAT / "veredicto.json").read_text(encoding="utf-8"))["veredicto"] == "INCONCLUSIVO")
sv.unlink()
c.cmd_etiquetar(NS(entrada=DAT / "entrada_validacion.jsonl", config="C1", datos=DAT, host=HOST, simular=True))
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
(DAT / "presupuesto.json").write_text('{"inicio_utc":"2000-01-01T00:00:00Z","limite_utc":"2999-01-01T00:00:00Z","horas":24}', encoding="utf-8")

print("\n== D1: excluir CONTEXTO cuenta como omisión")
MODO["tipo"] = "excluye_contexto"; sv.unlink()
c.cmd_etiquetar(NS(entrada=DAT / "entrada_validacion.jsonl", config="C1", datos=DAT, host=HOST, simular=False))
sale(c.cmd_validar, NS(datos=DAT, prueba=False))
ve = json.loads((DAT / "veredicto.json").read_text(encoding="utf-8"))
n_ctx = sum(1 for d in REF.values() if d["mitad"] == "validacion" and d["ref"] == "CONTEXTO")
chequeo(f"{n_ctx} CONTEXTO excluidas -> {n_ctx} omisiones y NO_APTO", ve["metricas"]["omisiones"] == n_ctx > 0 and ve["veredicto"] == "NO_APTO")
MODO["tipo"] = "perfecto"

print("\n== Desalojo: línea cortada a la mitad")
datos = sv.read_bytes(); sv.write_bytes(datos[:-40])
c.cmd_etiquetar(NS(entrada=DAT / "entrada_validacion.jsonl", config="C1", datos=DAT, host=HOST, simular=False))
validas = sum(1 for l in sv.read_text(encoding="utf-8").splitlines() if l.strip().endswith("}"))
chequeo("se rehace la obra cortada sin pegarla a la línea rota", validas == sum(1 for d in REF.values() if d["mitad"] == "validacion"))

print("\n== NO_EVALUADAS: una configuración que no pasa 'probar' no compite")
pj = json.loads((DAT / "probar.json").read_text(encoding="utf-8")); pj["validas"] = ["C2", "C3"]
(DAT / "probar.json").write_text(json.dumps(pj), encoding="utf-8")
sale(c.cmd_elegir, NS(datos=DAT, prueba=False))
el = json.loads((DAT / "eleccion.json").read_text(encoding="utf-8"))
chequeo("C1 y C4 quedan NO_EVALUADAS; elige entre C2 y C3", el["no_evaluadas"] == ["C1", "C4"] and el["elegida"] == "C2")

print(f"\n{'TODAS LAS PRUEBAS PASAN' if not FALLAS else 'FALLAN: ' + ', '.join(FALLAS)}  (carpeta: {T})")
sys.exit(1 if FALLAS else 0)
