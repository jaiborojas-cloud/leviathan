"""Q15: piloto de cribado por título y resumen con modelos abiertos (Ollama).

Subcomandos, en orden:
  preparar   construye la referencia auditada (lotes 01-03), la partición y las entradas sin etiquetas
  probar     revisa el formato de respuesta de cada configuración con una obra inventada; corre en la VM
  etiquetar  etiqueta una entrada con una configuración; reanudable; corre en la VM
  verificar  revisa estructura y respuestas inválidas de una salida
  elegir     compara las configuraciones SOLO en la mitad de selección y aplica la regla fija
  validar    aplica las compuertas a la configuración elegida en la mitad de validación

Parámetros congelados abajo. Ver PREREGISTRO_CRIBADO_LLM.md.
"""
import argparse, csv, hashlib, io, json, random, re, sys, time, unicodedata, urllib.request, zipfile
from collections import Counter, defaultdict
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
MAX_INVALIDAS = 0.02       # fracción máxima de respuestas inválidas, validación
MAX_OMISIONES = 0          # obras INCLUIR de la referencia que el modelo EXCLUYE, validación
PROMPT = Path(__file__).with_name("PROMPT_CRIBADO_LLM.md")
# --------------------------------------------------------


def sha(b):
    return hashlib.sha256(b).hexdigest()


def escribir(p, obj):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def norm_titulo(t):
    t = unicodedata.normalize("NFKC", t or "").lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def leer_zip(ruta, nombre):
    """Devuelve el contenido de un archivo dentro del zip, buscado por nombre base."""
    with zipfile.ZipFile(ruta) as z:
        hits = [n for n in z.namelist() if n.rsplit("/", 1)[-1] == nombre]
        if len(hits) != 1:
            sys.exit(f"{ruta}: se esperaba un solo '{nombre}', hay {len(hits)}")
        return z.read(hits[0])


def csv_zip(ruta, nombre):
    return list(csv.DictReader(io.StringIO(leer_zip(ruta, nombre).decode("utf-8-sig"))))


def resumenes_de_evidencia(ruta, nombre):
    """Recorre la evidencia y junta, por obra, el título y los resúmenes distintos de sus posiciones."""
    datos = json.loads(leer_zip(ruta, nombre).decode("utf-8-sig"))
    por_obra = defaultdict(lambda: {"titulo": "", "resumenes": []})

    def visitar(x):
        if isinstance(x, dict):
            obra = x.get("obra_id") or x.get("work_id")
            rec = x.get("record") if isinstance(x.get("record"), dict) else x
            if obra and isinstance(rec, dict) and ("abstract" in rec or "title" in rec):
                d = por_obra[obra]
                d["titulo"] = d["titulo"] or (rec.get("title") or "")
                a = (rec.get("abstract") or "").strip()
                vistos = {unicodedata.normalize("NFKC", r) for r in d["resumenes"]}
                if len(a) > 20 and unicodedata.normalize("NFKC", a) not in vistos:
                    d["resumenes"].append(a)
            for v in x.values():
                visitar(v)
        elif isinstance(x, list):
            for v in x:
                visitar(v)

    visitar(datos)
    return por_obra


def cmd_preparar(a):
    out = Path(a.datos); out.mkdir(parents=True, exist_ok=True)
    ref = {}
    # lote 01 (Codex) y lote 03 (Argon): decisiones finales
    for zipf, crib, evid in [(a.lote01, "cribado_lote01.csv", "evidencia_lote01.json"),
                             (a.lote03, "cribado_lote03.csv", "evidencia_lote03.json")]:
        ev = resumenes_de_evidencia(zipf, evid)
        for r in csv_zip(zipf, crib):
            ref[r["obra_id"]] = {"decision": r["decision"], "titulo": r["titulo"], "ev": ev.get(r["obra_id"]), "lote": crib[8:14]}
    # lote 02 (Argon) con las correcciones de O2, que vienen en el paquete del lote 03
    ev2 = resumenes_de_evidencia(a.lote02, "evidencia_lote02.json")
    corr = {r["obra_id"]: r["decision"] for r in csv_zip(a.lote03, "correcciones_lote02.csv")}
    for r in csv_zip(a.lote02, "cribado_lote02.csv"):
        ref[r["obra_id"]] = {"decision": corr.get(r["obra_id"], r["decision"]), "titulo": r["titulo"], "ev": ev2.get(r["obra_id"]), "lote": "lote02"}
    # solo obras con resumen y decisión de las tres clases
    filas, fuera = [], Counter()
    for o, d in sorted(ref.items()):
        ev = d["ev"] or {"titulo": "", "resumenes": []}
        if d["decision"] not in DECISIONES:
            fuera[d["decision"]] += 1; continue
        if not ev["resumenes"]:
            fuera["SIN_RESUMEN"] += 1; continue
        filas.append({"obra_id": o, "titulo": d["titulo"] or ev["titulo"], "resumenes": ev["resumenes"], "ref": d["decision"], "lote": d["lote"]})
    # grupos por título normalizado, para que un duplicado no quede en ambas mitades
    grupos = defaultdict(list)
    for f in filas:
        grupos[norm_titulo(f["titulo"])].append(f)
    # partición estratificada por la decisión de referencia del grupo (la más conservadora)
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
    t = PROMPT.read_text(encoding="utf-8")
    return t.split("<<<INICIO>>>", 1)[1].split("<<<FIN>>>", 1)[0].strip(), sha(PROMPT.read_bytes())


def mensaje_obra(x):
    partes = [f"Título: {x['titulo']}"]
    for i, r in enumerate(x["resumenes"], 1):
        partes.append(f"Resumen {i}: {r}")
    return "\n\n".join(partes)


def llamar(host, cfg, sistema, usuario, simular):
    if simular:
        return {"message": {"content": json.dumps({"decision": "EXCLUIR_FUERA_TEMA", "puntos": [], "razon": "simulado", "dudoso": False})},
                "model": cfg["modelo"], "total_duration": 0}
    cuerpo = {"model": cfg["modelo"], "stream": False, "format": ESQUEMA, "options": OPCIONES,
              "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": usuario}]}
    if cfg["think"] is not None:
        cuerpo["think"] = cfg["think"]
    req = urllib.request.Request(host.rstrip("/") + "/api/chat", data=json.dumps(cuerpo).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=1800) as r:
        return json.loads(r.read())


def interpretar(contenido):
    """Respuesta válida solo si es el JSON del esquema; si no, queda INVALIDA (nunca se adivina)."""
    try:
        j = json.loads(contenido)
        if j.get("decision") in DECISIONES and isinstance(j.get("razon"), str) and j["razon"].strip() and isinstance(j.get("dudoso"), bool):
            return j
    except Exception:
        pass
    return None


def cmd_etiquetar(a):
    cfg = CONFIGS[a.config]
    sistema, sha_prompt = prompt_sistema()
    entrada = [json.loads(l) for l in open(a.entrada, encoding="utf-8") if l.strip()]
    salida = Path(a.datos) / f"salida_{Path(a.entrada).stem.replace('entrada_', '')}_{a.config}.jsonl"
    hechos = set()
    if salida.exists():
        for l in open(salida, encoding="utf-8"):
            try:
                hechos.add(json.loads(l)["obra_id"])
            except Exception:
                pass  # línea truncada por un desalojo: se rehace
    print(f"{a.config} {cfg}: {len(hechos)} de {len(entrada)} ya hechas -> {salida}")
    # si un desalojo dejó la última línea sin terminar, se cierra para no pegarle la siguiente respuesta
    if salida.exists() and salida.stat().st_size and not salida.read_bytes().endswith(b"\n"):
        with open(salida, "ab") as fb:
            fb.write(b"\n")
    with open(salida, "a", encoding="utf-8", newline="\n") as fo:
        for i, x in enumerate(entrada, 1):
            if x["obra_id"] in hechos:
                continue
            t0 = time.time()
            r = llamar(a.host, cfg, sistema, mensaje_obra(x), a.simular)
            contenido = r.get("message", {}).get("content", "")
            j = interpretar(contenido)
            fo.write(json.dumps({
                "obra_id": x["obra_id"], "config": a.config, "modelo": r.get("model", cfg["modelo"]), "think": cfg["think"],
                "decision": j["decision"] if j else "INVALIDA", "dudoso": j["dudoso"] if j else None,
                "puntos": j.get("puntos", []) if j else [], "razon": j["razon"] if j else "",
                "crudo": contenido, "pensamiento": r.get("message", {}).get("thinking", ""),
                "segundos": round(time.time() - t0, 2), "total_duration_ns": r.get("total_duration"), "done_reason": r.get("done_reason"),
                "prompt_sha256": sha_prompt, "opciones": OPCIONES,
            }, ensure_ascii=False) + "\n")
            fo.flush()
            print(f"  {i}/{len(entrada)} {x['obra_id']} {j['decision'] if j else 'INVALIDA'} {time.time()-t0:.1f}s", flush=True)


OBRA_PRUEBA = {"obra_id": "PRUEBA", "titulo": "A synthetic test record about crop rotation schedules",
               "resumenes": ["This invented abstract describes scheduling crop rotations on small farms with a spreadsheet. It does not involve neural networks, calibration or learning dynamics. It is used only to check the response format."]}


def cmd_probar(a):
    """Manda una obra inventada a cada configuración y revisa que la respuesta cumpla el esquema. No usa datos de la referencia."""
    sistema, sha_prompt = prompt_sistema()
    res = {}
    for c, cfg in CONFIGS.items():
        t0 = time.time()
        r = llamar(a.host, cfg, sistema, mensaje_obra(OBRA_PRUEBA), a.simular)
        contenido = r.get("message", {}).get("content", "")
        j = interpretar(contenido)
        res[c] = {"modelo": r.get("model"), "valida": j is not None, "decision": j["decision"] if j else None,
                  "done_reason": r.get("done_reason"), "segundos": round(time.time() - t0, 1), "crudo": contenido[:300]}
        print(c, res[c]["valida"], res[c]["decision"], res[c]["segundos"], "s", flush=True)
    escribir(Path(a.datos) / "probar.json", {"prompt_sha256": sha_prompt, "resultados": res})
    if not all(v["valida"] for v in res.values()):
        sys.exit("Alguna configuración no devolvió el formato pedido: revisar antes de lanzar.")


def leer_salida(p):
    s = {}
    for l in open(p, encoding="utf-8"):
        try:
            d = json.loads(l); s[d["obra_id"]] = d
        except Exception:
            pass
    return s


def metricas(ref, sal):
    n = len(ref); inc = [o for o, r in ref.items() if r == "INCLUIR_PARA_TEXTO"]
    falt = [o for o in ref if o not in sal]
    omis = [o for o in inc if o in sal and sal[o]["decision"] == "EXCLUIR_FUERA_TEMA"]
    acu = sum(1 for o, r in ref.items() if o in sal and sal[o]["decision"] == r)
    inval = sum(1 for o in ref if o in sal and sal[o]["decision"] == "INVALIDA")
    segs = sorted(sal[o]["segundos"] for o in ref if o in sal)
    return {"n": n, "faltantes": len(falt), "incluidas_ref": len(inc), "omisiones": len(omis), "omisiones_ids": omis,
            "sensibilidad": 1 - len(omis) / len(inc) if inc else None, "acuerdo": acu / n if n else None,
            "invalidas": inval, "frac_invalidas": inval / n if n else None,
            "mediana_segundos": segs[len(segs) // 2] if segs else None,
            "matriz": dict(Counter(f"{r}->{sal[o]['decision']}" for o, r in ref.items() if o in sal))}


def referencia(datos, mitad):
    return {d["obra_id"]: d["ref"] for d in map(json.loads, open(Path(datos) / "referencia.jsonl", encoding="utf-8")) if d["mitad"] == mitad}


def cmd_verificar(a):
    s = leer_salida(a.salida)
    print(json.dumps({"lineas_validas": len(s), "decisiones": dict(Counter(d["decision"] for d in s.values())),
                      "modelos": dict(Counter(d["modelo"] for d in s.values())),
                      "prompt_sha256": sorted({d["prompt_sha256"] for d in s.values()})}, indent=2, ensure_ascii=False))


def cmd_elegir(a):
    ref = referencia(a.datos, "seleccion")
    res = {}
    for c in CONFIGS:
        p = Path(a.datos) / f"salida_seleccion_{c}.jsonl"
        if not p.exists():
            sys.exit(f"Falta {p.name}: la regla exige las cuatro configuraciones completas.")
        m = metricas(ref, leer_salida(p))
        if m["faltantes"]:
            sys.exit(f"{c}: faltan {m['faltantes']} obras.")
        res[c] = m
    # solo compiten las configuraciones con a lo sumo MAX_INVALIDAS de respuestas inválidas
    aptas = [c for c in res if res[c]["frac_invalidas"] <= MAX_INVALIDAS]
    # regla fija: mayor sensibilidad; luego mayor acuerdo; luego menos inválidas; luego menor mediana de tiempo
    orden = sorted(aptas, key=lambda c: (-res[c]["sensibilidad"], -res[c]["acuerdo"], res[c]["invalidas"], res[c]["mediana_segundos"]))
    elegida = orden[0] if orden else None
    out = {"mitad": "seleccion", "metricas": res, "compiten": aptas, "elegida": elegida,
           "config_elegida": CONFIGS[elegida] if elegida else None,
           "veredicto": None if elegida else "NO_APTO (ninguna configuracion con inválidas <= MAX_INVALIDAS)"}
    escribir(Path(a.datos) / "eleccion.json", out)
    print(json.dumps(out, indent=2, ensure_ascii=False))


def cmd_validar(a):
    el = json.loads((Path(a.datos) / "eleccion.json").read_text(encoding="utf-8"))["elegida"]
    if not el:
        sys.exit("No hay configuración elegida: el piloto es NO_APTO desde la selección.")
    p = Path(a.datos) / f"salida_validacion_{el}.jsonl"
    if not p.exists():
        sys.exit(f"Falta {p.name}.")
    ref = referencia(a.datos, "validacion")
    m = metricas(ref, leer_salida(p))
    if m["faltantes"]:
        veredicto, comp = "INCONCLUSIVO", {"completa": "FALLA"}
    else:
        comp = {"omisiones": "PASA" if m["omisiones"] <= MAX_OMISIONES else "FALLA",
                "acuerdo": "PASA" if m["acuerdo"] >= UMBRAL_ACUERDO else "FALLA",
                "invalidas": "PASA" if m["frac_invalidas"] <= MAX_INVALIDAS else "FALLA"}
        veredicto = "APTO" if all(v == "PASA" for v in comp.values()) else "NO_APTO"
    out = {"mitad": "validacion", "config": el, "modelo": CONFIGS[el], "metricas": m, "compuertas": comp, "veredicto": veredicto,
           "umbrales": {"omisiones_max": MAX_OMISIONES, "acuerdo_min": UMBRAL_ACUERDO, "invalidas_max": MAX_INVALIDAS}}
    escribir(Path(a.datos) / "veredicto.json", out)
    print(json.dumps(out, indent=2, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("preparar"); p.add_argument("--lote01", required=True); p.add_argument("--lote02", required=True); p.add_argument("--lote03", required=True); p.add_argument("--datos", required=True)
    p = sp.add_parser("etiquetar"); p.add_argument("--entrada", required=True); p.add_argument("--config", required=True, choices=CONFIGS); p.add_argument("--datos", required=True); p.add_argument("--host", default="http://127.0.0.1:11434"); p.add_argument("--simular", action="store_true")
    p = sp.add_parser("probar"); p.add_argument("--datos", required=True); p.add_argument("--host", default="http://127.0.0.1:11434"); p.add_argument("--simular", action="store_true")
    p = sp.add_parser("verificar"); p.add_argument("--salida", required=True)
    p = sp.add_parser("elegir"); p.add_argument("--datos", required=True)
    p = sp.add_parser("validar"); p.add_argument("--datos", required=True)
    a = ap.parse_args()
    {"preparar": cmd_preparar, "etiquetar": cmd_etiquetar, "probar": cmd_probar, "verificar": cmd_verificar, "elegir": cmd_elegir, "validar": cmd_validar}[a.cmd](a)


if __name__ == "__main__":
    main()
