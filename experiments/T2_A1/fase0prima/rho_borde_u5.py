"""rho_borde_u5.py (v1) - estados del update 5 y rho_borde(u5) de las 800 trayectorias (T2-A1, diseno v3, fase previa a abrir X).

Para cada trayectoria del manifiesto de cohorte: verifica checkpoint_005.pt contra metadata/cohort_manifest.csv (columnas
trajectory y checkpoint_sha256; no lee otras), reconstruye el estado geometrico (M, f) del update 5 SIN entrenar, con las mismas
llamadas que el ejecutor v12 (new_session, load_state_dict, core.make_geom_state, core.subset_M), lo guarda y calcula rho_borde
con rho_borde.py congelado (d8ec69f8...). NO lee baseline/ ni comparators/ (X sigue cerrado). No abre visitas futuras.

Salidas en --out: estados_u5/<tray>.npz, rho_borde_u5.csv (tray, split, init, rho_borde, diagnosticos, sha256 del npz y del
checkpoint), PROGRESO.csv (reanudable) y RESUMEN_u5.json con el SHA-256 de la tabla.

Uso (PowerShell, equipo del responsable):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "<repo>\\experiments\\T2_A1\\fase0prima\\rho_borde_u5.py" `
     --out "D:\\RIPG_DATA\\T2_A1\\rho_u5" --procesos 12
  --seco: verifica hashes y rutas de las 800 sin calcular nada.  --solo <tray> [...]: subconjunto (pruebas; no cuenta).
"""
import os
for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_k] = "1"
import argparse, csv, hashlib, json, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RHO_SHA = "d8ec69f89a75ab947ac05d3764858eb2e8f6dc873b47733645b2e8b5aac0416b"
GEOM_SHA = "b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
_W = {}


def _init(root, mocks):
    src = Path(root) / "sources"
    for p in (str(src / "instrument"), mocks, str(src)):   # mismo orden que el ejecutor v12 (sources queda primero)
        sys.path.insert(0, p)
    sys.path.append(str(HERE))
    import torch
    torch.set_num_threads(1)
    import core, rho_borde
    from training import new_session
    from geometry import Geometry
    _W.update(torch=torch, core=core, rb=rho_borde, new_session=new_session, Geometry=Geometry, root=Path(root))


def una(tray, ck_sha, out):
    torch, core, rb = _W["torch"], _W["core"], _W["rb"]
    S, J = int(tray.split("_")[0][5:]), int(tray.split("_")[1][1:])
    ck = _W["root"] / "trajectories" / tray / "checkpoint_005.pt"
    h = sha(ck)
    if h != ck_sha:
        return dict(trajectory=tray, error="checkpoint_005 no coincide con el manifiesto")
    X, y, Xv, yv, m, opt, rng = _W["new_session"](S, J)
    c = torch.load(ck, weights_only=False)
    assert c["step"] == 5 and c["split"] == S and c["init"] == J
    m.load_state_dict(c["model"])
    Rb, Ub, f = core.make_geom_state(m, Xv, yv); M = core.subset_M(Rb, Ub, [0, 1, 2])
    M, f = M.detach().numpy(), f.detach().numpy()
    p = Path(out) / "estados_u5" / f"{tray}.npz"; np.savez_compressed(p, M=M, f=f)
    t0 = time.perf_counter(); R = rb.rho_borde(_W["Geometry"](np.array(M, float), np.array(f, float)))
    R.update(trajectory=tray, split=S, init=J, npz_sha256=sha(p), checkpoint_sha256=h, segundos=round(time.perf_counter() - t0, 1))
    return R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--root", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
    ap.add_argument("--procesos", type=int, default=12)
    ap.add_argument("--mocks", default=r"D:\RIPG_DATA\T2_A\cribado_borde\margen\mocks", help="mismo valor por defecto que el ejecutor v12")
    ap.add_argument("--seco", action="store_true"); ap.add_argument("--solo", nargs="*", default=None)
    a = ap.parse_args()
    if sha(HERE / "rho_borde.py") != RHO_SHA:
        sys.exit("ABORTA: rho_borde.py no coincide con la version congelada")
    root = Path(a.root)
    if sha(root / "sources" / "geometry.py") != GEOM_SHA:
        sys.exit("ABORTA: sources/geometry.py no coincide con b4d1e0e4...")
    man = [(r["trajectory"], r["checkpoint_sha256"]) for r in csv.DictReader(open(root / "metadata" / "cohort_manifest.csv", encoding="utf-8"))]
    if a.solo:
        man = [x for x in man if x[0] in set(a.solo)]
    faltan = [t for t, _ in man if not (root / "trajectories" / t / "checkpoint_005.pt").exists()]
    rep = dict(trayectorias=len(man), checkpoints_faltantes=faltan, out=a.out, rho_borde_sha256=RHO_SHA, script_sha256=sha(Path(__file__)))
    print(json.dumps(rep, indent=2))
    if faltan:
        sys.exit("ABORTA: faltan checkpoints")
    if a.seco:
        return
    out = Path(a.out); (out / "estados_u5").mkdir(parents=True, exist_ok=True)
    prog = out / "PROGRESO.csv"; hechas = set()
    if prog.exists():
        hechas = {r["trajectory"] for r in csv.DictReader(open(prog, encoding="utf-8")) if not r.get("error")}
    campos = ["trajectory", "split", "init", "rho_borde", "err_quad", "theta", "rho_min_gl", "dif_orden", "dif_dir", "rho_mediana",
              "npz_sha256", "checkpoint_sha256", "segundos", "error"]
    nuevo = not prog.exists(); fh = open(prog, "a", newline="", encoding="utf-8"); w = csv.DictWriter(fh, fieldnames=campos, extrasaction="ignore")
    if nuevo:
        w.writeheader()
    pend = [(t, h) for t, h in man if t not in hechas]
    print(f"pendientes: {len(pend)}", flush=True)
    with ProcessPoolExecutor(max_workers=a.procesos, initializer=_init, initargs=(str(root), a.mocks)) as pool:
        futs = {pool.submit(una, t, h, str(out)): t for t, h in pend}
        for i, fu in enumerate(as_completed(futs), 1):
            try:
                R = fu.result()
            except Exception as e:
                R = dict(trajectory=futs[fu], error=repr(e)[:300])
            w.writerow(R); fh.flush()
            print(f"[{i}/{len(pend)}] {R['trajectory']}: {R.get('rho_borde', R.get('error'))}", flush=True)
    fh.close()
    filas = {r["trajectory"]: r for r in csv.DictReader(open(prog, encoding="utf-8")) if not r.get("error")}
    orden = [t for t, _ in man if t in filas]
    tabla = out / "rho_borde_u5.csv"
    with open(tabla, "w", newline="", encoding="utf-8") as f2:
        w2 = csv.DictWriter(f2, fieldnames=campos, extrasaction="ignore"); w2.writeheader(); w2.writerows(filas[t] for t in orden)
    errores = [r for r in csv.DictReader(open(prog, encoding="utf-8")) if r.get("error") and r["trajectory"] not in filas]
    res = dict(trayectorias=len(man), con_rho=len(orden), errores=len(errores), tabla_sha256=sha(tabla), script_sha256=sha(Path(__file__)),
               rho_borde_sha256=RHO_SHA, fecha=time.strftime("%Y-%m-%dT%H:%M:%S%z"), nota="Predictor basal; sin X; sin visitas futuras.")
    (out / "RESUMEN_u5.json").write_text(json.dumps(res, indent=2)); print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
