"""fase2_rho.py (v1) - fase 2 de T2-A1 (diseno v3 y protocolo 0c' congelados): rho_borde en los updates 50, 150 y 250 de las
780 trayectorias confirmatorias (splits 12-167). X sigue CERRADO durante toda la fase (no se lee baseline/ ni comparators/).

Por visita: el ejecutor v12 SIN CAMBIOS (2381fbcc...3347) en modo --solo-entrenamiento escribe checkpoint.pt y state.npz del
update k (k-5 updates desde checkpoint_005, como en T2-A0); luego rho_borde.py congelado (d8ec69f8...) sobre (M, f).
Verifica cada checkpoint_005 contra metadata/cohort_manifest.csv (solo trajectory y checkpoint_sha256). Exige >= 20 GB libres.
Reanudable: PROGRESO_fase2.csv; una visita con fila sin error no se repite. Al final: fase2_rho.csv ordenada, RESUMEN_fase2.json
con SHA-256 y conteos operacionales (visitas, errores, tiempos).

Uso (PowerShell):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "<repo>\\experiments\\T2_A1\\fase2\\fase2_rho.py" `
     --out "D:\\RIPG_DATA\\T2_A1\\fase2" --procesos 12
  --seco: verifica hashes, rutas y cola sin calcular.  --solo <tray> ...: subconjunto (prueba; usar otra --out).
"""
import os
for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_k] = "1"
import argparse, csv, hashlib, json, shutil, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RHO = HERE.parent / "fase0prima" / "rho_borde.py"
RHO_SHA = "d8ec69f89a75ab947ac05d3764858eb2e8f6dc873b47733645b2e8b5aac0416b"
EJECUTOR_SHA = "2381fbcca8ea17472dca69cc6ce2bf6bc7a0a4aa1910d318da5fef7e5fe93347"
GEOM_SHA = "b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3"
UPDATES = (50, 150, 250)
SPLITS = range(12, 168)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
_W = {}


def _init(root):
    src = Path(root) / "sources"
    sys.path.insert(0, str(src)); sys.path.append(str(RHO.parent))
    import rho_borde
    from geometry import Geometry
    _W.update(rb=rho_borde, Geometry=Geometry)


def una(tray, k, ejecutor, root, out, mocks):
    d = Path(out) / "visitas" / tray / f"u{k}"; d.mkdir(parents=True, exist_ok=True); t0 = time.perf_counter()
    st = d / "states" / tray / "state.npz"
    if not st.exists():
        cmd = [sys.executable, "-I", ejecutor, "--case", tray, "--step", str(k), "--work", str(d), "--root", root, "--mocks", mocks, "--solo-entrenamiento"]
        with open(d / "stdout.log", "a", encoding="utf-8") as so, open(d / "stderr.log", "a", encoding="utf-8") as se:
            rc = subprocess.call(cmd, stdout=so, stderr=se)
        if rc != 0 or not st.exists():
            return dict(trajectory=tray, update=k, error=f"ejecutor rc={rc}, state.npz {'existe' if st.exists() else 'ausente'}")
    t1 = time.perf_counter()
    with np.load(st) as z:
        M, f = np.array(z["M"], float), np.array(z["f"], float)
    R = _W["rb"].rho_borde(_W["Geometry"](M, f))
    R.update(trajectory=tray, update=k, split=int(tray.split("_")[0][5:]), state_sha256=sha(st),
             checkpoint_k_sha256=sha(d / "states" / tray / "checkpoint.pt"), seg_entrenamiento=round(t1 - t0, 1), seg_rho=round(time.perf_counter() - t1, 1))
    return R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--root", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
    ap.add_argument("--codigo", default=r"D:\RIPG_DATA\T2_A\produccion\codigo")
    ap.add_argument("--mocks", default=r"D:\RIPG_DATA\T2_A\cribado_borde\margen\mocks")
    ap.add_argument("--procesos", type=int, default=12)
    ap.add_argument("--seco", action="store_true"); ap.add_argument("--solo", nargs="*", default=None)
    a = ap.parse_args()
    root = Path(a.root); ej = Path(a.codigo) / "visita_produccion_v12.py"; err = []
    if sha(RHO) != RHO_SHA: err.append("rho_borde.py no coincide")
    if sha(ej) != EJECUTOR_SHA: err.append("ejecutor v12 no coincide")
    if sha(root / "sources" / "geometry.py") != GEOM_SHA: err.append("geometry.py no coincide")
    man = {r["trajectory"]: r["checkpoint_sha256"] for r in csv.DictReader(open(root / "metadata" / "cohort_manifest.csv", encoding="utf-8"))}
    trays = [t for t in man if int(t.split("_")[0][5:]) in SPLITS]
    if a.solo:
        trays = [t for t in trays if t in set(a.solo)]
    for t in trays:
        ck = root / "trajectories" / t / "checkpoint_005.pt"
        if not ck.exists() or sha(ck) != man[t]:
            err.append(f"checkpoint_005 de {t}")
    Path(a.out).mkdir(parents=True, exist_ok=True)
    libre = shutil.disk_usage(a.out).free / 2**30
    if libre < 20: err.append(f"menos de 20 GB libres ({libre:.1f})")
    cola = [(t, k) for t in trays for k in UPDATES]
    rep = dict(trayectorias=len(trays), splits=len({t.split('_')[0] for t in trays}), visitas=len(cola), libre_gb=round(libre, 1), errores=err[:20],
               script_sha256=sha(Path(__file__)), rho_borde_sha256=RHO_SHA, ejecutor_sha256=EJECUTOR_SHA)
    print(json.dumps(rep, indent=2))
    if err:
        sys.exit("ABORTA")
    if a.seco:
        return
    prog = Path(a.out) / "PROGRESO_fase2.csv"; hechas = set()
    if prog.exists():
        hechas = {(r["trajectory"], int(r["update"])) for r in csv.DictReader(open(prog, encoding="utf-8")) if not r.get("error")}
    campos = ["trajectory", "update", "split", "rho_borde", "err_quad", "theta", "rho_min_gl", "dif_orden", "dif_dir", "rho_mediana",
              "state_sha256", "checkpoint_k_sha256", "seg_entrenamiento", "seg_rho", "error"]
    nuevo = not prog.exists(); fh = open(prog, "a", newline="", encoding="utf-8"); w = csv.DictWriter(fh, fieldnames=campos, extrasaction="ignore")
    if nuevo:
        w.writeheader()
    pend = [x for x in cola if x not in hechas]; t_ini = time.time()
    print(f"pendientes: {len(pend)}", flush=True)
    with ProcessPoolExecutor(max_workers=a.procesos, initializer=_init, initargs=(str(root),)) as pool:
        futs = {pool.submit(una, t, k, str(ej), str(root), a.out, a.mocks): (t, k) for t, k in pend}
        for i, fu in enumerate(as_completed(futs), 1):
            try:
                R = fu.result()
            except Exception as e:
                t, k = futs[fu]; R = dict(trajectory=t, update=k, error=repr(e)[:300])
            w.writerow(R); fh.flush()
            if i % 25 == 0 or R.get("error"):
                print(f"[{i}/{len(pend)}] {R['trajectory']} u{R['update']} {'ERROR ' + R['error'] if R.get('error') else 'ok'} ({(time.time() - t_ini) / 60:.1f} min)", flush=True)
    fh.close()
    filas = {(r["trajectory"], int(r["update"])): r for r in csv.DictReader(open(prog, encoding="utf-8")) if not r.get("error")}
    tabla = Path(a.out) / "fase2_rho.csv"
    with open(tabla, "w", newline="", encoding="utf-8") as f2:
        w2 = csv.DictWriter(f2, fieldnames=campos, extrasaction="ignore"); w2.writeheader(); w2.writerows(filas[x] for x in cola if x in filas)
    errores = [r for r in csv.DictReader(open(prog, encoding="utf-8")) if r.get("error") and (r["trajectory"], int(r["update"])) not in filas]
    res = dict(visitas=len(cola), con_rho=len([x for x in cola if x in filas]), errores_sin_resolver=len(errores), tabla_sha256=sha(tabla),
               script_sha256=sha(Path(__file__)), fecha=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
               nota="Fase 2 de T2-A1. Informe operacional: X cerrado; los desenlaces quedan en la tabla y se analizan solo tras abrir X.")
    (Path(a.out) / "RESUMEN_fase2.json").write_text(json.dumps(res, indent=2)); print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
