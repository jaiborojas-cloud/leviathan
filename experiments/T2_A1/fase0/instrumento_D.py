"""instrumento_D.py (v2: carga de certificar_t5 importable por los procesos hijos en Windows/spawn; v1 fallaba con PicklingError) - implementacion de PROTOCOLO_instrumento_D_v1_CONGELADO.md (T2-A1, fase 0a).

Instrumento nuevo de T2-A1. NO es una v5 de la certificacion T5 de T2-A0: importa SIN CAMBIOS certificar_t5.py v4
(SHA-256 9e0c12a2...0b7d, verificado al importar) y usa su funcion un_caso tal cual. Lo unico que anade el instrumento:
  * paso 2: asignacion de D a partir de la salida del ejecutor v12 (seccion 2 del protocolo);
  * paso 3: la cota de un estado cualquiera (ruta + hash), con tope de pared de 60 min (D0-2) y U2 con factores dobles
    (F_K = 8, F_T = 20, F_disc = 20), calculado con los mismos ingredientes que U, sin integrar nada nuevo (seccion 3);
  * controles por corrida: j5/u25 debe dar T5 certificada con U = 0.019426498826 (1e-9 relativo) y V1; j8/u25 debe quedar
    no certificada con U >= 0.0239 y V1 (V2). Si un control falla, ningun caso del paso 3 de esa corrida cuenta (D = ?).
SOLO LECTURA sobre las visitas y los estados. Escribe solo en --out. No usa X. No reclasifica nada de T2-A0.

Modos
  asignar   (por defecto): recorre visitas de una carpeta de lote, asigna D y corre el paso 3 donde toca.
  --cota-caso: (interno) un caso del paso 3 en un proceso hijo; lo usa el modo asignar para aplicar el tope de pared.

Uso (PowerShell, equipo del responsable; fase 0b):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "<repo>\\experiments\\T2_A1\\fase0\\instrumento_D.py" `
     --lote "D:\\RIPG_DATA\\T2_A\\produccion\\lote_0" --updates 50 150 250 --out "D:\\RIPG_DATA\\T2_A1\\fase0b\\salida_<fecha>"
Pruebas (no cuentan): --prueba (sin controles; admite --t0-forzado/--T-plus-forzado en el modo --cota-caso).
"""
import os
for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_k, "1")
import argparse, csv, hashlib, importlib.util, json, math, platform, signal, subprocess, sys, time, traceback
from pathlib import Path
from types import SimpleNamespace
import numpy as np

HERE = Path(__file__).resolve().parent
PROTOCOLO_D_SHA = "a380e6c3448ed61863075bf855cf36f8c24b336e59a20049d24b5f2b5db81f97"
T5_SCRIPT = HERE.parent.parent / "T2_A" / "claude" / "piloto" / "certificacion_t5" / "certificar_t5.py"
T5_SCRIPT_SHA = "9e0c12a2a3d2fde95bf04cd729e2e7df5a237fc757ca8ee82d40dd7935b90b7d"
GEOM_SHA = "b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3"
U_MAX = 0.0195
F_K2, F_T2, F_DISC2 = 8.0, 20.0, 20.0          # factores dobles (diseno v2, seccion 2)
TOPE_PARED_S = 3600.0                           # D0-2
CONTROLES = {   # estados u25 regenerados (../../T2_A/claude/piloto/estados_u25/regeneracion_u25.csv)
    "split8_j5_true": ("state_025_regen_split8_j5_true.npz", "845c22519a20be8ceef4e35210157d97bd5bc223fc9f05e1769b91d998aa4776"),
    "split8_j8_true": ("state_025_regen_split8_j8_true.npz", "f70d88b3c300286e31b8ca55860cc99f7d2a38c9e5f0c21242d566703928132b"),
}
U_J5_CORRIDA4, U_J5_TOL = 0.019426498826, 1e-9  # RESULTADO_corrida4_v4_2026-10-21.md
A_MEDIDA_J8 = 0.02393521                         # V2 del protocolo T5 v1
TERMINALES = {"VISITA_COMPLETA.json": "VISIT_EVALUATED", "REVISION_PENDIENTE.json": "PAUSED_PENDING_REVIEW", "ERROR_EJECUCION.json": "ERROR_DE_EJECUCION"}

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def cargar_t5():
    h = sha(T5_SCRIPT)
    if h != T5_SCRIPT_SHA:
        sys.exit(f"ABORTA: certificar_t5.py no coincide con v4 ({h[:12]} vs {T5_SCRIPT_SHA[:12]})")
    # v2: el modulo se registra con su nombre y su carpeta va a sys.path, para que los procesos del ProcessPoolExecutor de
    # un_caso puedan importarlo al deserializar _mp_init/_k_mp_lote. En Windows (spawn) v1 fallaba con PicklingError.
    sys.path.insert(0, str(T5_SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("certificar_t5", T5_SCRIPT)
    C = importlib.util.module_from_spec(spec); sys.modules["certificar_t5"] = C; spec.loader.exec_module(C)
    return C


def cargar_geometria(sources):
    src = Path(sources)
    for p in (str(src / "instrument"), str(src)):
        sys.path.insert(0, p)
    gpath = next((p for p in (src / "geometry.py", src / "instrument" / "geometry.py") if p.exists()), None)
    if gpath is None or sha(gpath) != GEOM_SHA:
        sys.exit(f"ABORTA: geometry.py no coincide con {GEOM_SHA[:8]}...")
    import geometry, audit
    return geometry, audit


# ---------------- paso 3: un caso (proceso hijo) ----------------
def u2_desde(R, rayos_csv):
    """U con los factores de T5 v1 (control de lectura) y U2 con factores dobles, a partir de los ingredientes de un_caso."""
    j0, jp0 = [], []
    with open(rayos_csv, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            j0.append(float(row["j_t0"])); jp0.append(float(row["jp_t0"]))
    j0, jp0 = np.array(j0), np.array(jp0); todos = np.arange(len(j0))
    def Lplus(kap, D, rays):   # misma formula que certificar_t5.un_caso (4.5)
        sk = math.sqrt(kap); x = sk * D
        Cc = math.cosh(x) if x < 700 else float("inf"); S = (math.sinh(x) / sk if sk > 0 else D) if x < 700 else float("inf")
        return float((2 * np.pi / len(rays)) * np.sum(np.abs(j0[rays]) * Cc + np.abs(jp0[rays]) * S))
    def cota(fk, ft, fd):
        kap = fk * R["curvatura"]["kappa_hat"]; Tp = R["escape"]["T_star"] + ft * R["escape"]["delta_T"]; D = Tp - R["t0"]["t"]
        L = Lplus(kap, D, todos); Lb = Lplus(kap, D, todos[::2])
        eps = abs(L - Lb) / L if np.isfinite(L) and L > 0 else float("inf")
        return R["area_t0"]["A0"] + fd * R["area_t0"]["delta_disc"] + D * L * (1 + 10 * eps), dict(kappa=kap, T_plus=Tp, Delta=D, L_plus=L, eps_theta=eps)
    U1, _ = cota(4.0, 10.0, 10.0)
    U2, det2 = cota(F_K2, F_T2, F_DISC2)
    return U1, U2, det2


def modo_cota_caso(a):
    C = cargar_t5(); geometry, audit = cargar_geometria(a.sources)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    logf = open(out / "log.txt", "a", encoding="utf-8")
    def log(m):
        line = f"{time.strftime('%H:%M:%S')} {a.cota_caso}: {m}"; print(line, flush=True); logf.write(line + "\n"); logf.flush()
    s_sha = sha(a.estado)
    if a.estado_sha and s_sha != a.estado_sha:
        sys.exit(f"ABORTA: {a.estado} no coincide con el hash esperado")
    with np.load(a.estado) as z:
        M, f = np.array(z["M"], dtype=float), np.array(z["f"], dtype=float)
    g = geometry.Geometry(M, f)
    args = SimpleNamespace(t0_forzado=a.t0_forzado if a.prueba else None, T_plus_forzado=a.T_plus_forzado if a.prueba else None,
                           prueba=a.prueba, procesos=a.procesos)
    t_ini = time.perf_counter()
    try:
        R = C.un_caso(a.cota_caso, g, geometry.triangles, geometry.area7, audit.jacsolve, M, f, out, args, log)
        res = dict(completo=True, veredicto_t5=R.get("veredicto"), U=R.get("cota", {}).get("U"), V1=R.get("V1"))
        if "cota" in R and R.get("escape", {}).get("T_star") is not None:
            U1, U2, det2 = u2_desde(R, out / "rayos.csv")
            res.update(U_releido=U1, U_releido_coincide=bool(abs(U1 - R["cota"]["U"]) <= 1e-12 * max(abs(R["cota"]["U"]), 1e-300)),
                       U2=U2, cota_factores_dobles=det2)
        res["un_caso"] = R
    except Exception:
        res = dict(completo=False, error=traceback.format_exc()[-3000:])
        log(res["error"])
    res.update(estado=str(a.estado), estado_sha256=s_sha, segundos=time.perf_counter() - t_ini,
               t5_script_sha256=T5_SCRIPT_SHA, instrumento_sha256=sha(Path(__file__)), protocolo_D_sha256=PROTOCOLO_D_SHA,
               environment=dict(python=platform.python_version(), numpy=np.__version__, platform=platform.platform()))
    (out / "cota.json").write_text(json.dumps(C.clean(res), indent=2))
    logf.close()


def correr_cota(caso, estado, estado_sha, out, a):
    """Lanza --cota-caso en un proceso hijo con tope de pared. Devuelve el dict de cota.json o None si se agota el tope."""
    out.mkdir(parents=True, exist_ok=True); fj = out / "cota.json"
    if fj.exists() and json.loads(fj.read_text()).get("completo") is not None:
        return json.loads(fj.read_text())
    cmd = [sys.executable, "-I", str(Path(__file__).resolve()), "--cota-caso", caso, "--estado", str(estado), "--out", str(out),
           "--sources", a.sources, "--procesos", str(a.procesos)] + (["--estado-sha", estado_sha] if estado_sha else []) + (["--prueba"] if a.prueba else [])
    kw = dict(creationflags=subprocess.CREATE_NEW_PROCESS_GROUP) if os.name == "nt" else dict(start_new_session=True)
    p = subprocess.Popen(cmd, **kw)
    try:
        p.wait(timeout=a.tope_pared)
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
        else:
            os.killpg(p.pid, signal.SIGKILL)
        p.wait()
        return None
    return json.loads(fj.read_text()) if fj.exists() else dict(completo=False, error=f"el proceso hijo termino con codigo {p.returncode} sin cota.json")


def certifica(c):
    """D = 1 por la via C (seccion 2, paso 3): veredicto T5 de un_caso pendiente solo de V1/V2, V1 del propio caso y U2 <= 0.0195."""
    if not c or not c.get("completo"):
        return False, ["sin resultado completo de la cota"]
    raz = list((c.get("veredicto_t5") or {}).get("razones", []))
    if (c.get("veredicto_t5") or {}).get("estado") != "T5_CERTIFICADA_PENDIENTE_V1_V2":
        raz = raz or ["un_caso no certifica"]
    if not (c.get("V1") or {}).get("ok"):
        raz.append("V1 del propio caso falla o sin t1")
    if c.get("U2") is None or not c["U2"] <= U_MAX:
        raz.append(f"U2 (factores dobles) = {c.get('U2')} > {U_MAX}")
    if c.get("U_releido_coincide") is False:
        raz.append("U releido de rayos.csv no coincide con U de un_caso")
    return (not raz), raz


# ---------------- paso 2: asignacion ----------------
def visitas(lote, updates, trayectorias):
    for td in sorted(Path(lote).glob("split*_j*_*")):
        if not td.is_dir() or (trayectorias and td.name not in trayectorias):
            continue
        for k in updates:
            cands = sorted([d for d in td.glob(f"u{k}*") if d.is_dir() and (d.name == f"u{k}" or d.name.startswith(f"u{k}_r"))],
                           key=lambda d: (0 if d.name == f"u{k}" else int(d.name.split("_r")[1])))
            term = [d for d in cands if any((d / n).exists() for n in TERMINALES)]
            yield td.name, k, (term[-1] if term else (cands[-1] if cands else None))


def asignar_paso2(tray, k, d):
    rec = dict(trajectory=tray, update=k, directorio=str(d) if d else None)
    if d is None:
        return dict(rec, D="?", via=None, razon="NO_INICIADA: sin directorio de visita", paso3=False)
    fn = next((n for n in TERMINALES if (d / n).exists()), None)
    if fn is None:
        return dict(rec, D="?", via=None, razon="visita sin archivo terminal (interrumpida)", paso3=False)
    ej = json.loads((d / fn).read_text()); est = TERMINALES[fn]
    st = d / "states" / tray; nominal = (st / "nominal.json").exists()
    rec.update(estado_ejecutor=est, archivo_ejecutor=fn, archivo_ejecutor_sha256=sha(d / fn), motivo_ejecutor=ej.get("reason"),
               nominal_existe=nominal, state_npz=str(st / "state.npz"), state_sha256=(sha(st / "state.npz") if (st / "state.npz").exists() else None))
    if est == "VISIT_EVALUATED":
        cl = (ej.get("resultado_visita") or {}).get("classification")
        rec["clasificacion_ejecutor"] = cl
        if cl == "INJECTIVE_AT_NOMINAL_RADIUS":
            return dict(rec, D=0, via="A", razon=None, paso3=False)
        if cl == "GEOMETRIC_NONINJECTIVITY":
            return dict(rec, D=1, via="B", razon=None, paso3=False)
        return dict(rec, D="?", via=None, razon=f"evaluada con clasificacion {cl}", paso3=False)
    if est == "PAUSED_PENDING_REVIEW":
        if nominal:
            return dict(rec, D="?", via=None, razon="auditoria interrumpida, sin clasificacion (D0-1)", paso3=False)
        if rec["state_sha256"] is None:
            return dict(rec, D="?", via=None, razon="pausa de calibracion sin state.npz", paso3=False)
        return dict(rec, D=None, via=None, razon=None, paso3=True)
    return dict(rec, D="?", via=None, razon="ERROR_DE_EJECUCION: requiere una repeticion en u<k>_r1 (seccion 2)", paso3=False)


def controles(a, out):
    """Controles de la corrida (seccion 3.3). Devuelve (validos, detalle)."""
    det = {}
    for caso, (fn, h) in CONTROLES.items():
        c = correr_cota(caso, Path(a.estados_control) / fn, h, out / "_controles" / caso, a)
        det[caso] = dict(completo=bool(c and c.get("completo")), U=(c or {}).get("U"), U2=(c or {}).get("U2"),
                         estado_t5=((c or {}).get("veredicto_t5") or {}).get("estado"), V1=((c or {}).get("V1") or {}).get("ok"),
                         tope_agotado=c is None)
    j5, j8 = det["split8_j5_true"], det["split8_j8_true"]
    j5["ok"] = bool(j5["completo"] and j5["estado_t5"] == "T5_CERTIFICADA_PENDIENTE_V1_V2" and j5["V1"]
                    and isinstance(j5["U"], (int, float)) and abs(j5["U"] - U_J5_CORRIDA4) <= U_J5_TOL * U_J5_CORRIDA4)
    u8 = j8["U"]; u8_ok = (u8 == "inf") or (isinstance(u8, (int, float)) and u8 >= A_MEDIDA_J8)
    j8["ok"] = bool(j8["completo"] and j8["V1"] and u8_ok and not str(j8["estado_t5"]).startswith("T5_CERTIFICADA"))
    return bool(j5["ok"] and j8["ok"]), det


def modo_asignar(a):
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    meta = dict(instrumento_sha256=sha(Path(__file__)), protocolo_D_sha256=PROTOCOLO_D_SHA, t5_script_sha256=sha(T5_SCRIPT),
                lote=a.lote, updates=a.updates, prueba=a.prueba, inicio=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                environment=dict(python=platform.python_version(), numpy=np.__version__, platform=platform.platform(), cpus=os.cpu_count()))
    if meta["t5_script_sha256"] != T5_SCRIPT_SHA:
        sys.exit("ABORTA: certificar_t5.py no coincide con v4")
    filas = [asignar_paso2(t, k, d) for t, k, d in visitas(a.lote, a.updates, set(a.trayectorias or []))]
    pend = [r for r in filas if r["paso3"]]
    print(f"{len(filas)} visitas; {len(pend)} van al paso 3", flush=True)
    validos, det = (True, dict(nota="--prueba: sin controles")) if a.prueba else (None, None)
    if pend and not a.prueba:
        validos, det = controles(a, out)
        print(f"controles de la corrida: {'VALIDOS' if validos else 'FALLAN'} {json.dumps(det)}", flush=True)
    for r in pend:
        c = correr_cota(r["trajectory"], r["state_npz"], r["state_sha256"], out / r["trajectory"] / f"u{r['update']}" / "cota", a)
        if c is None:
            r.update(D="?", razon=f"tope de pared del paso 3 ({a.tope_pared:g} s) agotado (D0-2)")
            continue
        r.update(U=c.get("U"), U2=c.get("U2"), segundos_paso3=c.get("segundos"))
        ok, raz = certifica(c)
        if ok and validos:
            r.update(D=1, via="C", razon=None)
        else:
            r.update(D="?", razon="; ".join(raz + ([] if validos else ["controles de la corrida no validos"])) or "no certifica")
    for r in filas:
        r.pop("paso3", None)
        dd = out / r["trajectory"] / f"u{r['update']}"; dd.mkdir(parents=True, exist_ok=True)
        (dd / "D.json").write_text(json.dumps(dict(r, meta=meta), indent=2, default=str))
    campos = ["trajectory", "update", "D", "via", "razon", "estado_ejecutor", "motivo_ejecutor", "nominal_existe", "U", "U2", "segundos_paso3", "state_sha256", "directorio"]
    with open(out / "D_visitas.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos, extrasaction="ignore"); w.writeheader(); w.writerows(filas)
    nv = len(filas); nq = sum(r["D"] == "?" for r in filas)
    por_tray = {}
    for r in filas:
        por_tray.setdefault(r["trajectory"], []).append(r["D"])
    Y = {t: (1 if 1 in ds else (0 if all(x == 0 for x in ds) else "?")) for t, ds in por_tray.items()}
    res = dict(meta=meta, controles_validos=validos, controles=det, visitas=nv,
               por_D={str(v): sum(str(r["D"]) == str(v) for r in filas) for v in (0, 1, "?")},
               por_via={v: sum(r["via"] == v for r in filas) for v in ("A", "B", "C")},
               fraccion_visitas_D_desconocida=(nq / nv if nv else None),
               trayectorias=len(Y), fraccion_trayectorias_Y_desconocida=(sum(v == "?" for v in Y.values()) / len(Y) if Y else None),
               razones_desconocida=sorted({r["razon"] for r in filas if r["D"] == "?"}),
               nota="Fase 0 de T2-A1 (desarrollo). No es Y de T2-A0. Sin X.")
    (out / "RESUMEN_D.json").write_text(json.dumps(res, indent=2, default=str))
    print(json.dumps({k: v for k, v in res.items() if k != "meta"}, indent=2, default=str))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lote", default=None, help="carpeta de lote del ejecutor v12 (modo asignar)")
    ap.add_argument("--updates", nargs="+", type=int, default=[50, 150, 250])
    ap.add_argument("--trayectorias", nargs="*", default=None)
    ap.add_argument("--sources", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto\sources")
    ap.add_argument("--estados-control", default=r"D:\RIPG_DATA\T2_A\expediente\estados_u25")
    ap.add_argument("--procesos", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--tope-pared", type=float, default=TOPE_PARED_S)
    ap.add_argument("--prueba", action="store_true", help="SOLO pruebas: sin controles de corrida")
    ap.add_argument("--cota-caso", default=None, help="(interno) un caso del paso 3")
    ap.add_argument("--estado", default=None); ap.add_argument("--estado-sha", default=None)
    ap.add_argument("--t0-forzado", type=float, default=None, help="SOLO --prueba"); ap.add_argument("--T-plus-forzado", type=float, default=None, help="SOLO --prueba")
    a = ap.parse_args()
    if not a.prueba and (a.t0_forzado or a.T_plus_forzado or a.tope_pared != TOPE_PARED_S):
        sys.exit("--t0-forzado, --T-plus-forzado y --tope-pared distinto de 3600 solo existen con --prueba")
    if a.cota_caso:
        modo_cota_caso(a)
    else:
        if not a.lote:
            sys.exit("falta --lote")
        modo_asignar(a)


if __name__ == "__main__":
    main()
