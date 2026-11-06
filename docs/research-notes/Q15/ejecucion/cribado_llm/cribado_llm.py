"""Q15: piloto de cribado por título y resumen con modelos abiertos (Ollama).

Subcomandos, en orden:
  preparar   construye la referencia auditada (lotes 01-03), la partición y las entradas sin etiquetas
  probar     revisa el formato de respuesta de cada configuración con una obra inventada; corre en la VM
  etiquetar  etiqueta una entrada con una configuración; reanudable; corre en la VM
  verificar  revisa estructura, metadatos e inválidas de una salida
  elegir     compara las configuraciones SOLO en la mitad de selección y aplica la regla fija
  validar    aplica las compuertas a la configuración elegida en la mitad de validación

Parámetros congelados abajo. Ver PREREGISTRO_CRIBADO_LLM.md (enmienda 2).
"""
import argparse, csv, hashlib, io, json, random, re, socket, sys, time, unicodedata, urllib.error, urllib.request, zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ---------------- parámetros congelados ----------------
SEMILLA = 20261105
CONFIGS = {
    "C1": {"modelo": "qwen3.8:27b", "think": False},
    "C2": {"modelo": "qwen3.8:27b", "think": True},
    "C3": {"modelo": "gemma4:31b", "think": None},
    "C4": {"modelo": "gpt-oss:120b", "think": "medium"},
}
OPCIONES = {"temperature": 0, "seed": 0, "num_ctx": 32768, "num_predict": 16384}
DECISIONES = ["INCLUIR_PARA_TEXTO", "CONTEXTO", "EXCLUIR_FUERA_TEMA"]
PROTEGIDAS = {"INCLUIR_PARA_TEXTO", "CONTEXTO"}   # excluir una de estas es una OMISIÓN (enmienda 2, D1)
PUNTOS = ["1", "2", "3a", "3b", "3c", "4a", "4b", "4c"]
ESQUEMA = {
    "type": "object",
    "properties": {
        "decision": {"type": "string", "enum": DECISIONES},
        "puntos": {"type": "array", "items": {"type": "string", "enum": PUNTOS}},
        "razon": {"type": "string"},
        "dudoso": {"type": "boolean"},
    },
    "required": ["decision", "puntos", "razon", "dudoso"],
}
UMBRAL_ACUERDO = 0.85      # acuerdo exacto en 3 clases, validación
MAX_INVALIDAS = 0.02       # fracción máxima de respuestas inválidas (selección y validación)
MAX_OMISIONES = 0          # obras PROTEGIDAS de la referencia que el modelo EXCLUYE, validación
INTENTOS = 3               # intentos en total por obra (no 1 + 3)
AQUI = Path(__file__).resolve().parent
PROMPT = AQUI / "PROMPT_CRIBADO_LLM.md"
PARTICION = AQUI / "particion.json"
SHA_SISTEMA = "4659f18ddde2d7634ffc2aa4ec0db857c955d1176993f5b5dacb97307cd42727"   # SHA-256 del texto efectivo que se envía como mensaje de sistema
# --------------------------------------------------------


def sha(b):
    return hashlib.sha256(b).hexdigest()


def ahora():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def escribir(p, obj):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def escribir_estado(datos, nombre, obj):
    """Escribe el estado vigente y una copia con fecha; un estado anterior nunca pasa por actual."""
    obj = {"utc": ahora(), **obj}
    escribir(Path(datos) / f"{nombre}.json", obj)
    escribir(Path(datos) / f"{nombre}_{obj['utc'].replace(':', '').replace('-', '')}.json", obj)
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def norm_titulo(t):
    t = unicodedata.normalize("NFKC", t or "").lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def tiene_texto(a):
    """Un resumen cuenta si tiene al menos un carácter alfanumérico (descarta "", ",", "-")."""
    return re.search(r"\w", a or "") is not None


def leer_zip(ruta, nombre):
    with zipfile.ZipFile(ruta) as z:
        hits = [n for n in z.namelist() if n.rsplit("/", 1)[-1] == nombre]
        if len(hits) != 1:
            sys.exit(f"{ruta}: se esperaba un solo '{nombre}', hay {len(hits)}")
        return z.read(hits[0])


def csv_zip(ruta, nombre):
    return list(csv.DictReader(io.StringIO(leer_zip(ruta, nombre).decode("utf-8-sig"))))


def resumenes_de_evidencia(ruta, nombre):
    """Por obra: título y resúmenes distintos. Formato exigido: lista de {obra_id, record: {title, abstract}}."""
    datos = json.loads(leer_zip(ruta, nombre).decode("utf-8-sig"))
    if not isinstance(datos, list) or not all(isinstance(x, dict) and "obra_id" in x and isinstance(x.get("record"), dict) for x in datos):
        sys.exit(f"{ruta}/{nombre}: estructura inesperada; se esperaba una lista de {{obra_id, record}}.")
    por_obra = defaultdict(lambda: {"titulo": "", "resumenes": []})
    for x in datos:
        rec, d = x["record"], por_obra[x["obra_id"]]
        d["titulo"] = d["titulo"] or (rec.get("title") or "")
        a = (rec.get("abstract") or "").strip()
        if tiene_texto(a) and unicodedata.normalize("NFKC", a) not in {unicodedata.normalize("NFKC", r) for r in d["resumenes"]}:
            d["resumenes"].append(a)
    return por_obra


def cmd_preparar(a):
    out = Path(a.datos); out.mkdir(parents=True, exist_ok=True)
    ref = {}
    for zipf, crib, evid, lote in [(a.lote01, "cribado_lote01.csv", "evidencia_lote01.json", "lote01"),
                                   (a.lote03, "cribado_lote03.csv", "evidencia_lote03.json", "lote03")]:
        ev = resumenes_de_evidencia(zipf, evid)
        for r in csv_zip(zipf, crib):
            ref[r["obra_id"]] = {"decision": r["decision"], "titulo": r["titulo"], "ev": ev.get(r["obra_id"]), "lote": lote}
    # lote 02 con las correcciones de O2 (opción B), que vienen en el paquete del lote 03
    ev2 = resumenes_de_evidencia(a.lote02, "evidencia_lote02.json")
    corr = {r["obra_id"]: r["decision"] for r in csv_zip(a.lote03, "correcciones_lote02.csv")}
    for r in csv_zip(a.lote02, "cribado_lote02.csv"):
        ref[r["obra_id"]] = {"decision": corr.get(r["obra_id"], r["decision"]), "titulo": r["titulo"], "ev": ev2.get(r["obra_id"]), "lote": "lote02"}
    filas, fuera = [], Counter()
    for o, d in sorted(ref.items()):
        ev = d["ev"] or {"titulo": "", "resumenes": []}
        if d["decision"] not in DECISIONES:
            fuera[d["decision"]] += 1; continue
        if not ev["resumenes"]:
            fuera["SIN_RESUMEN"] += 1; continue
        filas.append({"obra_id": o, "titulo": d["titulo"] or ev["titulo"], "resumenes": ev["resumenes"], "ref": d["decision"], "lote": d["lote"]})
    grupos = defaultdict(list)
    for f in filas:
        grupos[norm_titulo(f["titulo"])].append(f)
    orden = {"INCLUIR_PARA_TEXTO": 0, "CONTEXTO": 1, "EXCLUIR_FUERA_TEMA": 2}
    estratos = defaultdict(list)
    for k, g in sorted(grupos.items()):
        estratos[min((f["ref"] for f in g), key=orden.get)].append(k)
    rng = random.Random(SEMILLA)
    parte = {}
    for e in sorted(estratos):
        ks = estratos[e][:]; rng.shuffle(ks)
        for i, k in enumerate(ks):
            for f in grupos[k]:
                parte[f["obra_id"]] = "seleccion" if i % 2 == 0 else "validacion"
    with open(out / "referencia.jsonl", "w", encoding="utf-8", newline="\n") as fr:
        for f in filas:
            fr.write(json.dumps({"obra_id": f["obra_id"], "ref": f["ref"], "lote": f["lote"], "mitad": parte[f["obra_id"]]}, ensure_ascii=False) + "\n")
    for m in ("seleccion", "validacion"):
        with open(out / f"entrada_{m}.jsonl", "w", encoding="utf-8", newline="\n") as fe:
            for f in filas:
                if parte[f["obra_id"]] == m:
                    fe.write(json.dumps({"obra_id": f["obra_id"], "titulo": f["titulo"], "resumenes": f["resumenes"]}, ensure_ascii=False) + "\n")
    resumen = {
        "semilla": SEMILLA, "obras": len(filas), "fuera": dict(fuera),
        "por_mitad": {m: dict(Counter(f["ref"] for f in filas if parte[f["obra_id"]] == m)) for m in ("seleccion", "validacion")},
        "grupos_con_mas_de_una_obra": sum(len(g) > 1 for g in grupos.values()),
        "sha256": {p.name: sha(p.read_bytes()) for p in sorted(out.glob("*.jsonl"))},
        "insumos_sha256": {Path(z).name: sha(Path(z).read_bytes()) for z in (a.lote01, a.lote02, a.lote03)},
    }
    escribir(out / "particion.json", resumen)
    print(json.dumps(resumen, indent=2, ensure_ascii=False))


def prompt_sistema():
    """Texto entre las líneas que son EXACTAMENTE <<<INICIO>>> y <<<FIN>>>; debe haber una de cada una."""
    lineas = PROMPT.read_text(encoding="utf-8").split("\n")
    ini = [i for i, l in enumerate(lineas) if l.strip() == "<<<INICIO>>>"]
    fin = [i for i, l in enumerate(lineas) if l.strip() == "<<<FIN>>>"]
    if len(ini) != 1 or len(fin) != 1 or not ini[0] < fin[0]:
        sys.exit(f"{PROMPT.name}: se esperaba una sola línea <<<INICIO>>> y una sola <<<FIN>>> después; hay {len(ini)} y {len(fin)}.")
    texto = "\n".join(lineas[ini[0] + 1:fin[0]]).strip()
    s = sha(texto.encode("utf-8"))
    if s != SHA_SISTEMA:
        sys.exit(f"El mensaje de sistema efectivo no es el congelado:\n  esperado {SHA_SISTEMA}\n  real     {s}")
    return texto, s


def mensaje_obra(x):
    partes = [f"Título: {x['titulo']}"]
    for i, r in enumerate(x["resumenes"], 1):
        partes.append(f"Resumen {i}: {r}")
    return "\n\n".join(partes)


def es_timeout(e):
    return isinstance(e, (TimeoutError, socket.timeout)) or (isinstance(e, urllib.error.URLError) and isinstance(e.reason, (TimeoutError, socket.timeout)))


def llamar(host, cfg, sistema, usuario, simular):
    if simular:
        return {"message": {"content": json.dumps({"decision": "EXCLUIR_FUERA_TEMA", "puntos": [], "razon": "simulado", "dudoso": False})},
                "model": cfg["modelo"]}
    cuerpo = {"model": cfg["modelo"], "stream": False, "format": ESQUEMA, "options": OPCIONES,
              "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": usuario}]}
    if cfg["think"] is not None:
        cuerpo["think"] = cfg["think"]
    req = urllib.request.Request(host.rstrip("/") + "/api/chat", data=json.dumps(cuerpo).encode(), headers={"Content-Type": "application/json"})
    error, del_modelo = None, False
    for intento in range(INTENTOS):
        try:
            with urllib.request.urlopen(req, timeout=1800) as r:
                cuerpo_r = r.read()
            try:
                return json.loads(cuerpo_r)
            except ValueError as e:  # Ollama respondió, pero no con JSON
                error, del_modelo = f"respuesta no JSON: {e}", True
        except urllib.error.HTTPError as e:  # el servidor respondió con un error (p. ej. 500 del modelo)
            error, del_modelo = f"HTTPError: {e}", True
        except Exception as e:
            if es_timeout(e):  # la respuesta tardó más de 30 minutos
                error, del_modelo = f"timeout: {e}", True
            else:  # sin conexión con Ollama
                error, del_modelo = f"{type(e).__name__}: {e}", False
        print(f"    intento {intento + 1}/{INTENTOS} fallo: {error}", flush=True)
        if intento + 1 < INTENTOS:
            time.sleep(30 * (intento + 1))
    if not del_modelo:
        # una falla de infraestructura no se cuenta contra el modelo: se detiene y se reanuda con 'lanzar'
        sys.exit(f"Sin conexión con Ollama tras {INTENTOS} intentos ({error}). Se detiene; al relanzar sigue donde iba.")
    return {"message": {"content": ""}, "model": cfg["modelo"], "error": error}


def interpretar(contenido):
    """Válida solo si es EXACTAMENTE el objeto del esquema; si no, INVALIDA (nunca se adivina)."""
    try:
        j = json.loads(contenido)
    except Exception:
        return None
    ok = (isinstance(j, dict) and set(j) == {"decision", "puntos", "razon", "dudoso"}
          and j["decision"] in DECISIONES
          and isinstance(j["puntos"], list) and all(isinstance(p, str) and p in PUNTOS for p in j["puntos"])
          and isinstance(j["razon"], str) and j["razon"].strip() != ""
          and isinstance(j["dudoso"], bool))
    return j if ok else None


OBRA_PRUEBA = {"obra_id": "PRUEBA", "titulo": "A synthetic test record about crop rotation schedules",
               "resumenes": ["This invented abstract describes scheduling crop rotations on small farms with a spreadsheet. It does not involve neural networks, calibration or learning dynamics. It is used only to check the response format."]}


def cmd_probar(a):
    """Manda una obra inventada a cada configuración y registra cuáles cumplen el esquema. No usa datos de la referencia."""
    sistema, sha_sis = prompt_sistema()
    res = {}
    for c, cfg in CONFIGS.items():
        t0 = time.time()
        r = llamar(a.host, cfg, sistema, mensaje_obra(OBRA_PRUEBA), a.simular)
        contenido = r.get("message", {}).get("content", "")
        j = interpretar(contenido)
        valida = j is not None and r.get("model") == cfg["modelo"]
        res[c] = {"modelo_pedido": cfg["modelo"], "modelo_respuesta": r.get("model"), "valida": valida, "decision": j["decision"] if j else None,
                  "done_reason": r.get("done_reason"), "error": r.get("error"), "segundos": round(time.time() - t0, 1), "crudo": contenido[:300]}
        print(c, valida, res[c]["decision"], res[c]["segundos"], "s", flush=True)
    validas = [c for c in CONFIGS if res[c]["valida"]]
    escribir(Path(a.datos) / "probar.json", {"utc": ahora(), "simulado": bool(a.simular), "sistema_sha256": sha_sis,
                                            "script_sha256": sha(Path(__file__).read_bytes()), "resultados": res, "validas": validas})
    print("VALIDAS:", " ".join(validas) or "(ninguna)")


def firma(cfg_id, sha_sis, sha_entrada, simulado):
    """Lo que debe coincidir en todas las filas de una salida para poder reanudarla o evaluarla."""
    return {"config": cfg_id, "modelo_pedido": CONFIGS[cfg_id]["modelo"], "think": CONFIGS[cfg_id]["think"], "opciones": OPCIONES,
            "sistema_sha256": sha_sis, "script_sha256": sha(Path(__file__).read_bytes()), "entrada_sha256": sha_entrada, "simulado": simulado}


def cmd_etiquetar(a):
    cfg = CONFIGS[a.config]
    sistema, sha_sis = prompt_sistema()
    entrada_bytes = Path(a.entrada).read_bytes()
    entrada = [json.loads(l) for l in entrada_bytes.decode("utf-8").split("\n") if l.strip()]
    fir = firma(a.config, sha_sis, sha(entrada_bytes), bool(a.simular))
    salida = Path(a.datos) / f"salida_{Path(a.entrada).stem.replace('entrada_', '')}_{a.config}.jsonl"
    hechos = set()
    if salida.exists():
        if salida.stat().st_size and not salida.read_bytes().endswith(b"\n"):
            with open(salida, "ab") as fb:
                fb.write(b"\n")  # cierra una línea dejada a medias por un desalojo
        for n, l in enumerate(open(salida, encoding="utf-8"), 1):
            try:
                d = json.loads(l)
            except Exception:
                continue  # línea truncada: esa obra se rehace
            if {k: d.get(k) for k in fir} != fir:
                sys.exit(f"{salida.name}, línea {n}: la fila no corresponde a esta configuración, prompt, script, entrada o modo; no se mezclan corridas.")
            hechos.add(d["obra_id"])
    print(f"{a.config} {cfg}: {len(hechos)} de {len(entrada)} ya hechas -> {salida}")
    with open(salida, "a", encoding="utf-8", newline="\n") as fo:
        for i, x in enumerate(entrada, 1):
            if x["obra_id"] in hechos:
                continue
            t0 = time.time()
            r = llamar(a.host, cfg, sistema, mensaje_obra(x), a.simular)
            contenido = r.get("message", {}).get("content", "")
            j = interpretar(contenido)
            if r.get("model") != cfg["modelo"]:
                j = None  # respondió otro modelo: no cuenta
            fo.write(json.dumps({
                **fir, "obra_id": x["obra_id"], "utc": ahora(), "modelo_respuesta": r.get("model"),
                "decision": j["decision"] if j else "INVALIDA", "dudoso": j["dudoso"] if j else None,
                "puntos": j["puntos"] if j else [], "razon": j["razon"] if j else "",
                "crudo": contenido, "pensamiento": r.get("message", {}).get("thinking", ""),
                "segundos": round(time.time() - t0, 2), "total_duration_ns": r.get("total_duration"),
                "done_reason": r.get("done_reason"), "error": r.get("error"),
            }, ensure_ascii=False) + "\n")
            fo.flush()
            print(f"  {i}/{len(entrada)} {x['obra_id']} {j['decision'] if j else 'INVALIDA'} {time.time()-t0:.1f}s", flush=True)


def mediana(v):
    v = sorted(v); n = len(v)
    return None if n == 0 else (v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2)


class Inconclusivo(Exception):
    pass


def particion_congelada():
    return json.loads(PARTICION.read_text(encoding="utf-8"))


def referencia(datos, mitad, prueba):
    p = Path(datos) / "referencia.jsonl"
    if not p.exists():
        raise Inconclusivo("falta referencia.jsonl")
    if not prueba and sha(p.read_bytes()) != particion_congelada()["sha256"]["referencia.jsonl"]:
        raise Inconclusivo("referencia.jsonl no coincide con la partición congelada")
    return {d["obra_id"]: d["ref"] for d in map(json.loads, open(p, encoding="utf-8")) if d["mitad"] == mitad}


def leer_salida_oficial(datos, mitad, c, ref, prueba):
    """Lee una salida y exige que TODAS sus filas tengan la firma oficial esperada y estén dentro del presupuesto de tiempo."""
    p = Path(datos) / f"salida_{mitad}_{c}.jsonl"
    if not p.exists():
        raise Inconclusivo(f"falta {p.name}")
    esperado = {"config": c, "modelo_pedido": CONFIGS[c]["modelo"], "think": CONFIGS[c]["think"], "opciones": OPCIONES, "sistema_sha256": SHA_SISTEMA}
    if not prueba:
        esperado["entrada_sha256"] = particion_congelada()["sha256"][f"entrada_{mitad}.jsonl"]
        esperado["simulado"] = False
    pres = Path(datos) / "presupuesto.json"
    if pres.exists():
        limite = json.loads(pres.read_text(encoding="utf-8-sig"))["limite_utc"]
    elif prueba:
        limite = None
    else:
        raise Inconclusivo("falta presupuesto.json (lo escribe el primer 'lanzar')")
    s, scripts = {}, set()
    for n, l in enumerate(open(p, encoding="utf-8"), 1):
        try:
            d = json.loads(l)
        except Exception:
            continue
        mal = {k: (d.get(k), v) for k, v in esperado.items() if d.get(k) != v}
        if mal:
            raise Inconclusivo(f"{p.name}, línea {n}: metadatos distintos de los oficiales: {mal}")
        if limite and d["utc"] > limite:
            raise Inconclusivo(f"{p.name}, línea {n}: etiquetada después del límite de tiempo {limite}")
        scripts.add(d["script_sha256"])
        s[d["obra_id"]] = d
    if len(scripts) > 1:
        raise Inconclusivo(f"{p.name}: mezcla filas de versiones distintas del script")
    falt = [o for o in ref if o not in s]
    if falt:
        raise Inconclusivo(f"{p.name}: faltan {len(falt)} obras")
    return s


def metricas(ref, sal):
    n = len(ref)
    prot = [o for o, r in ref.items() if r in PROTEGIDAS]
    omis = [o for o in prot if sal[o]["decision"] == "EXCLUIR_FUERA_TEMA"]
    inval = sum(1 for o in ref if sal[o]["decision"] == "INVALIDA")
    return {"n": n, "protegidas_ref": len(prot), "omisiones": len(omis), "omisiones_ids": omis,
            "sensibilidad": 1 - len(omis) / len(prot) if prot else None,
            "acuerdo": sum(1 for o, r in ref.items() if sal[o]["decision"] == r) / n,
            "invalidas": inval, "frac_invalidas": inval / n,
            "mediana_segundos": mediana([sal[o]["segundos"] for o in ref]),
            "matriz": dict(Counter(f"{r}->{sal[o]['decision']}" for o, r in ref.items()))}


def cmd_verificar(a):
    s = []
    for l in open(a.salida, encoding="utf-8"):
        try:
            s.append(json.loads(l))
        except Exception:
            pass
    claves = ["config", "modelo_pedido", "sistema_sha256", "script_sha256", "entrada_sha256", "simulado"]
    print(json.dumps({"lineas_validas": len(s), "decisiones": dict(Counter(d.get("decision") for d in s)),
                      "firmas": dict(Counter(json.dumps({k: d.get(k) for k in claves}, sort_keys=True) for d in s)),
                      "modelos_respuesta": dict(Counter(d.get("modelo_respuesta") for d in s)),
                      "truncadas_por_longitud": sum(d.get("done_reason") == "length" for d in s)}, indent=2, ensure_ascii=False))


def cmd_elegir(a):
    base = {"mitad": "seleccion", "prueba": bool(a.prueba)}
    try:
        ref = referencia(a.datos, "seleccion", a.prueba)
        pp = Path(a.datos) / "probar.json"
        if not pp.exists():
            raise Inconclusivo("falta probar.json")
        pj = json.loads(pp.read_text(encoding="utf-8"))
        if pj["sistema_sha256"] != SHA_SISTEMA or (pj["simulado"] and not a.prueba):
            raise Inconclusivo("probar.json no corresponde al prompt congelado o es simulado")
        evaluadas = pj["validas"]
        res = {c: metricas(ref, leer_salida_oficial(a.datos, "seleccion", c, ref, a.prueba)) for c in evaluadas}
    except Inconclusivo as e:
        escribir_estado(a.datos, "eleccion", {**base, "veredicto": "INCONCLUSIVO", "motivo": str(e), "elegida": None})
        sys.exit(1)
    aptas = [c for c in res if res[c]["frac_invalidas"] <= MAX_INVALIDAS]
    # regla fija: mayor sensibilidad; luego mayor acuerdo; luego menos inválidas; luego menor mediana de tiempo
    orden = sorted(aptas, key=lambda c: (-res[c]["sensibilidad"], -res[c]["acuerdo"], res[c]["invalidas"], res[c]["mediana_segundos"]))
    elegida = orden[0] if orden else None
    escribir_estado(a.datos, "eleccion", {**base, "veredicto": "ELEGIDA" if elegida else "NO_APTO",
                                          "motivo": None if elegida else "ninguna configuración evaluada con inválidas <= MAX_INVALIDAS",
                                          "evaluadas": evaluadas, "no_evaluadas": [c for c in CONFIGS if c not in evaluadas],
                                          "compiten": aptas, "elegida": elegida, "config_elegida": CONFIGS.get(elegida), "metricas": res})


def cmd_validar(a):
    base = {"mitad": "validacion", "prueba": bool(a.prueba),
            "umbrales": {"omisiones_max": MAX_OMISIONES, "acuerdo_min": UMBRAL_ACUERDO, "invalidas_max": MAX_INVALIDAS}}
    try:
        ej = Path(a.datos) / "eleccion.json"
        if not ej.exists():
            raise Inconclusivo("falta eleccion.json")
        el = json.loads(ej.read_text(encoding="utf-8"))
        if el.get("veredicto") != "ELEGIDA" or bool(el.get("prueba")) != bool(a.prueba):
            raise Inconclusivo(f"eleccion.json no tiene una configuración elegida válida (veredicto {el.get('veredicto')})")
        c = el["elegida"]
        ref = referencia(a.datos, "validacion", a.prueba)
        m = metricas(ref, leer_salida_oficial(a.datos, "validacion", c, ref, a.prueba))
    except Inconclusivo as e:
        escribir_estado(a.datos, "veredicto", {**base, "veredicto": "INCONCLUSIVO", "motivo": str(e)})
        sys.exit(1)
    comp = {"omisiones": "PASA" if m["omisiones"] <= MAX_OMISIONES else "FALLA",
            "acuerdo": "PASA" if m["acuerdo"] >= UMBRAL_ACUERDO else "FALLA",
            "invalidas": "PASA" if m["frac_invalidas"] <= MAX_INVALIDAS else "FALLA"}
    escribir_estado(a.datos, "veredicto", {**base, "config": c, "modelo": CONFIGS[c], "metricas": m, "compuertas": comp,
                                           "veredicto": "APTO" if all(v == "PASA" for v in comp.values()) else "NO_APTO"})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("preparar"); p.add_argument("--lote01", required=True); p.add_argument("--lote02", required=True); p.add_argument("--lote03", required=True); p.add_argument("--datos", required=True)
    p = sp.add_parser("probar"); p.add_argument("--datos", required=True); p.add_argument("--host", default="http://127.0.0.1:11434"); p.add_argument("--simular", action="store_true")
    p = sp.add_parser("etiquetar"); p.add_argument("--entrada", required=True); p.add_argument("--config", required=True, choices=CONFIGS); p.add_argument("--datos", required=True); p.add_argument("--host", default="http://127.0.0.1:11434"); p.add_argument("--simular", action="store_true")
    p = sp.add_parser("verificar"); p.add_argument("--salida", required=True)
    for n in ("elegir", "validar"):
        p = sp.add_parser(n); p.add_argument("--datos", required=True)
        p.add_argument("--prueba", action="store_true", help="solo para pruebas sintéticas: acepta datos simulados y sin presupuesto; el resultado se marca prueba=true y no es oficial")
    a = ap.parse_args()
    {"preparar": cmd_preparar, "probar": cmd_probar, "etiquetar": cmd_etiquetar, "verificar": cmd_verificar, "elegir": cmd_elegir, "validar": cmd_validar}[a.cmd](a)


if __name__ == "__main__":
    main()
