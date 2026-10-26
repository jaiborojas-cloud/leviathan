"""r1_etapa2.py - DIN-R1 etapa 2: rho_borde v2 (r3) en 6240 estados de T2-A1/DIN-borde (splits 12-167). Reanudable.
Uso (PowerShell):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "D:\\RIPG_DATA\\DIN_C1\\R1\\r1_etapa2.py" --procesos 12
"""
import os
for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"
import argparse, csv, hashlib, json, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
V2_SHA = "2ac015a263afb44616de0fceebd3b1d2a36ad0a76cd466adcdcc7e3adb8b8df0"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
_V = {}


def _init(gp):
    sys.path.insert(0, str(HERE)); import rho_borde_v2_r3_copia as V; _V.update(V=V, gp=gp)


def ruta(T, t, k):
    if k == 5: return T / "rho_u5" / "estados_u5" / f"{t}.npz"
    if k in (10, 20, 30, 40): return T / "DIN_borde" / "d6" / "estados" / t / f"u{k}.npz"
    return T / "fase2" / "visitas" / t / f"u{k}" / "states" / t / "state.npz"


def una(T, t, k):
    p = ruta(Path(T), t, k); t0 = time.time()
    try:
        z = np.load(p); M = z["M"].astype(float); M = (M + M.T) / 2; f = z["f"].astype(float)
        o = _V["V"].rho_borde_v2(M, f, geometry_path=_V["gp"]); g = o.get("rho_caras_winner", {}) or {}
        return dict(trajectory=t, update=k, rho_caras=o.get("rho_caras"), rho_vert=o.get("rho_vert"), ganador=g.get("kind", ""), status=o["status"],
                    trM=float(np.trace(M)), state_sha256=sha(p), seg=round(time.time() - t0, 3), error="")
    except Exception as e:
        return dict(trajectory=t, update=k, status="ERROR", seg=round(time.time() - t0, 3), error=repr(e)[:200])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--t2a1", default=r"D:\RIPG_DATA\T2_A1"); ap.add_argument("--procesos", type=int, default=12)
    ap.add_argument("--root", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto"); ap.add_argument("--out", default=str(HERE / "etapa2"))
    a = ap.parse_args(); T = Path(a.t2a1); gp = Path(a.root) / "sources" / "geometry.py"
    if sha(HERE / "rho_borde_v2_r3_copia.py") != V2_SHA: sys.exit("ABORTA: rho_borde_v2 no coincide")
    trays = sorted({r["trajectory"] for r in csv.DictReader(open(T / "fase2" / "fase2_rho.csv", encoding="utf-8"))})
    cola = [(t, k) for t in trays for k in (5, 10, 20, 30, 40, 50, 150, 250)]
    falt = [str(ruta(T, t, k)) for t, k in cola if not ruta(T, t, k).exists()]
    print(json.dumps(dict(trayectorias=len(trays), estados=len(cola), faltan=len(falt), ejemplo_falta=falt[:3], script_sha256=sha(Path(__file__)))), flush=True)
    if falt: sys.exit("ABORTA: faltan estados")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True); prog = out / "PROGRESO_r1e2.csv"
    campos = ["trajectory", "update", "rho_caras", "rho_vert", "ganador", "status", "trM", "state_sha256", "seg", "error"]
    hechos = {(r["trajectory"], int(r["update"])) for r in csv.DictReader(open(prog, encoding="utf-8")) if r["status"] != "ERROR"} if prog.exists() else set()
    nuevo = not prog.exists(); fh = open(prog, "a", newline="", encoding="utf-8"); w = csv.DictWriter(fh, fieldnames=campos, extrasaction="ignore")
    if nuevo: w.writeheader()
    pend = [x for x in cola if x not in hechos]; t0 = time.time(); print(f"pendientes: {len(pend)}", flush=True)
    with ProcessPoolExecutor(max_workers=a.procesos, initializer=_init, initargs=(str(gp),)) as pool:
        futs = [pool.submit(una, str(T), t, k) for t, k in pend]
        for i, fu in enumerate(as_completed(futs), 1):
            R = fu.result(); w.writerow(R); fh.flush()
            if i % 250 == 0 or R["status"] == "ERROR": print(f"[{i}/{len(pend)}] {R['trajectory']} u{R['update']} {R['status']} ({(time.time() - t0) / 60:.1f} min)", flush=True)
    fh.close()
    filas = {(r["trajectory"], int(r["update"])): r for r in csv.DictReader(open(prog, encoding="utf-8"))}
    tabla = out / "r1_etapa2.csv"
    with open(tabla, "w", newline="", encoding="utf-8") as f2:
        w2 = csv.DictWriter(f2, fieldnames=campos, extrasaction="ignore"); w2.writeheader(); w2.writerows(filas[x] for x in cola if x in filas)
    st = {}
    for r in filas.values(): st[r["status"]] = st.get(r["status"], 0) + 1
    res = dict(estados=len(cola), status=st, tabla_sha256=sha(tabla), script_sha256=sha(Path(__file__)), rho_v2_sha256=V2_SHA)
    (out / "RESUMEN_r1e2.json").write_text(json.dumps(res, indent=2)); print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
