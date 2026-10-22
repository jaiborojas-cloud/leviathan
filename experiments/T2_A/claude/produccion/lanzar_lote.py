"""lanzar_lote.py - lanzador de lotes de produccion T2-A (PLAN_PRODUCCION_v1_CONGELADO.md, SHA-256 3c379cee...a03a).

Modos (uno por llamada):
  --seco      prueba en seco: verifica hashes, cohort_manifest.csv (800 filas, splits 8-167 x 5 inits), conteos por lote
              (180 / 1300), raiz y disco. No visita nada.
  --correr    ejecuta las visitas pendientes del lote con N procesos (ejecutor v12). Omite visitas cerradas; reanuda en su mismo
              directorio las interrumpidas (sin archivo de estado); NO reintenta pausadas ni con error. Regla de parada: 20
              ERROR_DE_EJECUCION consecutivos por orden de terminacion. Se detiene si D tiene < 50 GB libres.
  --cerrar    informe operacional (sin clasificaciones, sin Y, sin X) y manifiesto de hashes del lote.
  --archivar  copia a E los ode_checkpoints de las visitas evaluadas (verifica SHA-256 releyendo desde E y solo entonces los borra
              de D) y hace la segunda copia de resultados en E.

Uso (PowerShell):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "D:\\RIPG_DATA\\T2_A\\produccion\\codigo\\lanzar_lote.py" --lote 0 --seco
"""
import argparse, csv, datetime, hashlib, json, os, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, FIRST_COMPLETED, wait
from pathlib import Path

PLAN_SHA = "3c379cee8b4ed238f0d6133b3a598410acb149f9aaa3ff1ceee1fe73fe99a03a"
HASHES = {  # PLAN v1 §1 y MANIFIESTO_ejecutor_v12_2026-10-22.sha256
    "visita_produccion_v12.py": "2381fbcca8ea17472dca69cc6ce2bf6bc7a0a4aa1910d318da5fef7e5fe93347",
    "resumable_dop853_instrumentado_v11.py": "e061617ed0627237b2b9d8bc172d318b66a75fe16ca395d2bbbe645ac004b7cd",
    "t4prima.py": "c58eb54b36eee5c07b2dd62e279fc74ad2c1f6b60eff59799515aa7647c63360",
}
LOTES = {0: (range(8, 12), range(50, 251, 25)), 1: (range(12, 38), range(25, 251, 25)), 2: (range(38, 64), range(25, 251, 25)),
         3: (range(64, 90), range(25, 251, 25)), 4: (range(90, 116), range(25, 251, 25)), 5: (range(116, 142), range(25, 251, 25)),
         6: (range(142, 168), range(25, 251, 25))}
ESPERADO = {0: 180, 1: 1300, 2: 1300, 3: 1300, 4: 1300, 5: 1300, 6: 1300}
ESTADOS = {"VISITA_COMPLETA.json": "VISIT_EVALUATED", "REVISION_PENDIENTE.json": "PAUSED_PENDING_REVIEW", "ERROR_EJECUCION.json": "ERROR_DE_EJECUCION"}
MIN_LIBRE_GB, MAX_ERRORES_SEGUIDOS = 50, 20
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
ahora = lambda: datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def sha_archivo(p, bloque=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(bloque), b""):
            h.update(b)
    return h.hexdigest()


# ---------------- cohorte y cola ----------------
def leer_manifiesto(root):
    for cand in (Path(root) / "records" / "cohort_manifest.csv", Path(root) / "cohort_manifest.csv"):
        if cand.exists():
            filas = list(csv.DictReader(open(cand, encoding="utf-8")))
            return cand, filas
    raise SystemExit("ABORTA: no se encuentra cohort_manifest.csv en la raiz de basales")


def parsear(tray):
    s_, j_, reg = tray.split("_")
    return int(s_[5:]), int(j_[1:]), reg


def cola_lote(filas, lote):
    splits, updates = LOTES[lote]
    trays = sorted({f["trajectory"] for f in filas if parsear(f["trajectory"])[0] in splits}, key=lambda t: parsear(t)[:2])
    return [(t, k) for t in trays for k in updates]


def verificar_cohorte(filas):
    errores = []
    trays = [f["trajectory"] for f in filas]
    if len(trays) != 800 or len(set(trays)) != 800:
        errores.append(f"cohort_manifest: {len(trays)} filas ({len(set(trays))} distintas), se esperaban 800")
    por_split = {}
    for t in trays:
        s, j, reg = parsear(t)
        if reg != "true":
            errores.append(f"regimen inesperado en {t}")
        por_split.setdefault(s, set()).add(j)
    if sorted(por_split) != list(range(8, 168)):
        errores.append(f"splits {min(por_split)}..{max(por_split)} ({len(por_split)}), se esperaban 8..167")
    for s, js in por_split.items():
        if js != set(range(5 * (s - 7), 5 * (s - 7) + 5)):
            errores.append(f"split {s}: inits {sorted(js)}, se esperaban {list(range(5 * (s - 7), 5 * (s - 7) + 5))}")
    return errores


# ---------------- estado de una visita (regla autoritativa del plan §3) ----------------
def dirs_visita(raiz, lote, tray, k):
    base = Path(raiz) / f"lote_{lote}" / tray
    ds = [base / f"u{k}"] + sorted(base.glob(f"u{k}_r*"), key=lambda p: int(p.name.split("_r")[1]))
    return [d for d in ds if d.exists()]


def estado_dir(d):
    for f, e in ESTADOS.items():
        if (d / f).exists():
            return e, d / f
    return ("INTERRUMPIDA" if d.exists() else "NO_INICIADA"), None


def estado_visita(raiz, lote, tray, k):
    """autoritativa = la de numero mas alto con VISITA_COMPLETA; si ninguna, la ultima existente."""
    ds = dirs_visita(raiz, lote, tray, k)
    completas = [d for d in ds if (d / "VISITA_COMPLETA.json").exists()]
    if completas:
        return "VISIT_EVALUATED", completas[-1], ds
    if ds:
        e, _ = estado_dir(ds[-1]); return e, ds[-1], ds
    return "NO_INICIADA", Path(raiz) / f"lote_{lote}" / tray / f"u{k}", ds


def libre_gb(p):
    return shutil.disk_usage(p).free / 1e9


# ---------------- modos ----------------
def preparar_codigo(a):
    """copia ejecutor y dependencias congeladas a <raiz>/codigo, verificando hashes en origen y destino."""
    cod = Path(a.raiz) / "codigo"; cod.mkdir(parents=True, exist_ok=True); errores = []
    for f, h in HASHES.items():
        src = Path(a.origen_ejecutor if f == "visita_produccion_v12.py" else a.origen_impl) / f
        if not src.exists():
            errores.append(f"no existe {src}"); continue
        if not a.prueba and sha(src) != h:
            errores.append(f"hash de {src} no coincide con el registrado"); continue
        if not (cod / f).exists() or sha(cod / f) != sha(src):
            shutil.copyfile(src, cod / f)
        if not a.prueba and sha(cod / f) != h:
            errores.append(f"hash de {cod / f} no coincide tras copiar")
    return cod, errores


def modo_seco(a):
    cod, err = preparar_codigo(a)
    cand, filas = leer_manifiesto(a.root); err += verificar_cohorte(filas)
    conteos = {n: len(cola_lote(filas, n)) for n in LOTES}
    for n, c in conteos.items():
        if c != ESPERADO[n]:
            err.append(f"lote {n}: {c} visitas, se esperaban {ESPERADO[n]}")
    if 25 in [k for _, k in cola_lote(filas, 0)]:
        err.append("el lote 0 no debe incluir el update 25")
    cola = cola_lote(filas, a.lote)
    est = {}
    for t, k in cola:
        e, _, _ = estado_visita(a.raiz, a.lote, t, k); est[e] = est.get(e, 0) + 1
    rep = dict(modo="seco", fecha=ahora(), lote=a.lote, plan_sha256=PLAN_SHA, codigo=str(cod),
               hashes={f: sha(cod / f) for f in HASHES if (cod / f).exists()}, cohort_manifest=str(cand), cohort_manifest_sha256=sha(cand),
               conteos_por_lote=conteos, primeras=cola[:3], ultimas=cola[-3:], estados_actuales=est,
               libre_D_gb=round(libre_gb(a.raiz), 1), libre_E_gb=(round(libre_gb(a.destino_e), 1) if Path(a.destino_e).exists() else None),
               errores=err, veredicto="PASA" if not err else "FALLA")
    out = Path(a.raiz) / f"lote_{a.lote}"; out.mkdir(parents=True, exist_ok=True)
    (out / f"PRUEBA_SECO_lote{a.lote}_{time.strftime('%Y%m%d_%H%M%S')}.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(rep, indent=2, ensure_ascii=False)); return 0 if not err else 1


def escribir_inventario(a, filas):
    out = Path(a.raiz) / f"lote_{a.lote}"; out.mkdir(parents=True, exist_ok=True)
    p = out / f"inventario_lote{a.lote}_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["trajectory", "update", "estado_operacional", "directorio_autoritativo", "repeticiones", "fecha_corte"])
        for t, k in cola_lote(filas, a.lote):
            e, d, ds = estado_visita(a.raiz, a.lote, t, k); w.writerow([t, k, e, str(d), len(ds), ahora()])
    (p.with_suffix(".csv.sha256")).write_text(f"{sha(p)}  {p.name}\n"); return p


def correr_visita(a, cod, tray, k, d):
    d.mkdir(parents=True, exist_ok=True); t0 = time.time(); pico = None
    cmd = [sys.executable, "-I", str(cod / "visita_produccion_v12.py"), "--case", tray, "--step", str(k), "--work", str(d), "--root", a.root]
    with open(d / "lanzador_stdout.log", "a", encoding="utf-8") as so, open(d / "lanzador_stderr.log", "a", encoding="utf-8") as se:
        so.write(f"== {ahora()} {' '.join(cmd)}\n"); so.flush()
        p = subprocess.Popen(cmd, stdout=so, stderr=se)
        try:
            import psutil
            pp = psutil.Process(p.pid)
            while p.poll() is None:
                try:
                    pico = max(pico or 0, pp.memory_info().rss)
                except Exception:
                    pass
                time.sleep(2)
        except ImportError:
            pass
        rc = p.wait()
    e, _ = estado_dir(d)
    return dict(trajectory=tray, update=k, directorio=str(d), estado=e, rc=rc, segundos=round(time.time() - t0, 1),
                pico_memoria_mb=(round(pico / 2**20) if pico else None), fin=ahora())


def modo_correr(a):
    cod, err = preparar_codigo(a)
    if err:
        print("\n".join(err)); return 1
    _, filas = leer_manifiesto(a.root); cola = cola_lote(filas, a.lote)
    inv = escribir_inventario(a, filas); print(f"inventario: {inv}")
    pend = []
    for t, k in cola:
        e, d, _ = estado_visita(a.raiz, a.lote, t, k)
        if e in ("NO_INICIADA", "INTERRUMPIDA"):
            pend.append((t, k, d))           # interrumpida: se reanuda en su mismo directorio (checkpoints del driver)
    print(f"lote {a.lote}: {len(cola)} visitas, {len(pend)} pendientes, {a.procesos} procesos")
    reg = Path(a.raiz) / f"lote_{a.lote}" / "registro_lote.csv"; nuevo = not reg.exists()
    fh = open(reg, "a", newline="", encoding="utf-8"); w = csv.DictWriter(fh, fieldnames=["orden_terminacion", "trajectory", "update", "directorio", "estado", "rc", "segundos", "pico_memoria_mb", "fin"])
    if nuevo:
        w.writeheader()
    orden = sum(1 for _ in open(reg, encoding="utf-8")) - 1 if not nuevo else 0
    seguidos, motivo = 0, None; it = iter(pend); vivos = {}
    with ThreadPoolExecutor(max_workers=a.procesos) as ex:
        def lanzar():
            nonlocal motivo
            if motivo:
                return False
            if libre_gb(a.raiz) < MIN_LIBRE_GB:
                motivo = f"menos de {MIN_LIBRE_GB} GB libres en D"; return False
            try:
                t, k, d = next(it)
            except StopIteration:
                return False
            vivos[ex.submit(correr_visita, a, cod, t, k, d)] = (t, k); return True
        for _ in range(a.procesos):
            if not lanzar():
                break
        while vivos:
            hechos, _ = wait(list(vivos), return_when=FIRST_COMPLETED)
            for f in hechos:
                vivos.pop(f); r = f.result(); orden += 1; r["orden_terminacion"] = orden; w.writerow(r); fh.flush()
                print(f"[{orden}] {r['trajectory']} u{r['update']}: {r['estado']} ({r['segundos']} s)", flush=True)
                seguidos = seguidos + 1 if r["estado"] == "ERROR_DE_EJECUCION" else 0
                if seguidos >= MAX_ERRORES_SEGUIDOS and not motivo:
                    motivo = f"{MAX_ERRORES_SEGUIDOS} ERROR_DE_EJECUCION consecutivos (orden de terminacion)"
                lanzar()
    fh.close()
    print(f"FIN: {'DETENIDO: ' + motivo if motivo else 'cola agotada'}"); return 2 if motivo else 0


def modo_cerrar(a):
    _, filas = leer_manifiesto(a.root); cola = cola_lote(filas, a.lote); out = Path(a.raiz) / f"lote_{a.lote}"
    cnt, tiempos, man = {}, [], []
    for t, k in cola:
        e, d, ds = estado_visita(a.raiz, a.lote, t, k); cnt[e] = cnt.get(e, 0) + 1
        for dd in ds:
            for f in ("VISITA_COMPLETA.json", "REVISION_PENDIENTE.json", "ERROR_EJECUCION.json"):
                if (dd / f).exists():
                    man.append((sha(dd / f), str((dd / f).relative_to(a.raiz)), "AUTORITATIVA" if dd == d else "repeticion"))
            for f in ("result.json", "nominal.json"):
                p = dd / "states" / t / f
                if p.exists():
                    man.append((sha(p), str(p.relative_to(a.raiz)), "AUTORITATIVA" if dd == d else "repeticion"))
        if e == "VISIT_EVALUATED":
            try:
                tiempos.append(json.loads((d / "VISITA_COMPLETA.json").read_text())["wall_seconds_session"])
            except Exception:
                pass
    n = len(cola); malos = cnt.get("PAUSED_PENDING_REVIEW", 0) + cnt.get("ERROR_DE_EJECUCION", 0)
    tiempos.sort()
    inf = dict(lote=a.lote, fecha=ahora(), plan_sha256=PLAN_SHA, visitas=n, por_estado=cnt,
               fraccion_pausadas_o_error=round(malos / n, 4) if n else None,
               regla_revision=("REVISAR ANTES DEL SIGUIENTE LOTE" if n and malos / n > 0.10 else "no se activa"),
               segundos_visita_evaluada=dict(n=len(tiempos), mediana=(tiempos[len(tiempos) // 2] if tiempos else None), max=(tiempos[-1] if tiempos else None)),
               libre_D_gb=round(libre_gb(a.raiz), 1), libre_E_gb=(round(libre_gb(a.destino_e), 1) if Path(a.destino_e).exists() else None),
               nota=("Informe operacional: sin clasificaciones, sin Y, sin X. Una visita que dispara T5 aparece como PAUSED_PENDING_REVIEW. "
                     "Un ERROR_DE_EJECUCION puede deberse a un checkpoint parcial (escritura no atomica); se repite en u<k>_r<n>."))
    (out / f"INFORME_OPERACIONAL_lote{a.lote}.json").write_text(json.dumps(inf, indent=2, ensure_ascii=False), encoding="utf-8")
    mp = out / f"MANIFIESTO_lote{a.lote}.sha256"
    mp.write_text("".join(f"{h}  {r}  ({tipo})\n" for h, r, tipo in sorted(man, key=lambda x: x[1])), encoding="utf-8")
    print(json.dumps(inf, indent=2, ensure_ascii=False)); print(f"manifiesto: {mp} ({len(man)} archivos); sha256 {sha(mp)}"); return 0


def modo_archivar(a):
    _, filas = leer_manifiesto(a.root); cola = cola_lote(filas, a.lote)
    eck = Path(a.destino_e) / "checkpoints_produccion" / f"lote_{a.lote}"; eres = Path(a.destino_e) / "resultados_produccion" / f"lote_{a.lote}"
    movidos = verif = borrados = copiados = 0; problemas = []
    for t, k in cola:
        e, d, ds = estado_visita(a.raiz, a.lote, t, k)
        for dd in ds:   # segunda copia de resultados (todo salvo ode_checkpoints), tambien de pausadas y con error
            for p in dd.rglob("*"):
                if p.is_file() and "ode_checkpoints" not in p.parts:
                    dst = eres / p.relative_to(Path(a.raiz) / f"lote_{a.lote}")
                    if not dst.exists() or sha_archivo(dst) != sha_archivo(p):
                        dst.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(p, dst); copiados += 1
        if e != "VISIT_EVALUATED":
            continue   # pausadas, con error o interrumpidas conservan sus checkpoints en D
        for dd in ds:
            oc = dd / "ode_checkpoints"
            if not oc.exists():
                continue
            ok_todo = True
            for p in [q for q in oc.rglob("*") if q.is_file()]:
                dst = eck / p.relative_to(Path(a.raiz) / f"lote_{a.lote}")
                dst.parent.mkdir(parents=True, exist_ok=True); h = sha_archivo(p)
                if not dst.exists() or sha_archivo(dst) != h:
                    shutil.copyfile(p, dst); movidos += 1
                if sha_archivo(dst) == h:      # relectura desde E
                    verif += 1
                else:
                    ok_todo = False; problemas.append(f"hash distinto tras copiar {p}")
            if ok_todo:
                shutil.rmtree(oc); borrados += 1
    rep = dict(lote=a.lote, fecha=ahora(), archivos_checkpoint_copiados=movidos, verificados_releyendo_E=verif,
               carpetas_ode_borradas_de_D=borrados, archivos_resultado_copiados=copiados, problemas=problemas[:50],
               libre_D_gb=round(libre_gb(a.raiz), 1), libre_E_gb=round(libre_gb(a.destino_e), 1))
    (Path(a.raiz) / f"lote_{a.lote}" / f"ARCHIVO_E_lote{a.lote}_{time.strftime('%Y%m%d_%H%M%S')}.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2)); return 0 if not problemas else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lote", type=int, required=True, choices=sorted(LOTES))
    m = ap.add_mutually_exclusive_group(required=True)
    for x in ("--seco", "--correr", "--cerrar", "--archivar"):
        m.add_argument(x, action="store_true")
    ap.add_argument("--procesos", type=int, default=8)
    ap.add_argument("--raiz", default=r"D:\RIPG_DATA\T2_A\produccion")
    ap.add_argument("--root", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
    ap.add_argument("--origen-ejecutor", default=r"D:\RIPG_DATA\T2_A\expediente\produccion")
    ap.add_argument("--origen-impl", default=r"D:\RIPG_DATA\T2_A\expediente\anexo_implementacion")
    ap.add_argument("--destino-e", default=r"E:\RIPG\T2_A")
    ap.add_argument("--prueba", action="store_true", help="SOLO pruebas del lanzador: no exige los hashes registrados")
    ap.add_argument("--min-libre-gb-prueba", type=float, default=None, help="SOLO con --prueba")
    a = ap.parse_args()
    global MIN_LIBRE_GB
    if a.min_libre_gb_prueba is not None:
        if not a.prueba:
            sys.exit("--min-libre-gb-prueba solo con --prueba")
        MIN_LIBRE_GB = a.min_libre_gb_prueba
    if a.procesos < 1 or a.procesos > 20:
        sys.exit("procesos fuera de 1..20 (plan §4)")
    Path(a.raiz).mkdir(parents=True, exist_ok=True)
    sys.exit({"seco": modo_seco, "correr": modo_correr, "cerrar": modo_cerrar, "archivar": modo_archivar}[
        next(x for x in ("seco", "correr", "cerrar", "archivar") if getattr(a, x))](a))


if __name__ == "__main__":
    main()
