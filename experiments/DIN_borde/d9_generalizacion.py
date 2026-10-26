"""d9_generalizacion.py (v1) - DIN-borde D9 (PLAN_D9_generalizacion.md). Reentrena 5->50 como D6 (compuerta: params u50 vs fase2 a
<=1e-12) y carga el checkpoint u250 de fase2. Mide perdidas/precisiones de train/val/TEST y X(t). No calcula asociaciones.
Uso (PowerShell): & $PY -I d9_generalizacion.py --out "D:\\RIPG_DATA\\T2_A1\\DIN_borde\\d9" --procesos 12
"""
import os
for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"
import argparse, csv, hashlib, json, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
_W = {}


def _init(root, mocks):
    src = Path(root) / "sources"
    for p in (str(src / "instrument"), mocks, str(src)): sys.path.insert(0, p)
    import torch, core
    torch.set_num_threads(1)
    from training import new_session, updates
    _W.update(torch=torch, core=core, new_session=new_session, updates=updates, root=Path(root))


def medir(m, X, y):
    torch = _W["torch"]
    with torch.no_grad():
        z = m(X); lse = torch.logsumexp(z, 1); lp = z[torch.arange(len(y)), y] - lse
        zm = z.clone(); zm[torch.arange(len(y)), y] = -float("inf"); l1mp = torch.logsumexp(zm, 1) - lse
        return float(-lp.mean()), float((z.argmax(1) == y).double().mean()), float(l1mp.max())


def una(tray, ck_sha, t2a1):
    torch, core = _W["torch"], _W["core"]; S, J = int(tray.split("_")[0][5:]), int(tray.split("_")[1][1:])
    before = _W["root"] / "trajectories" / tray / "checkpoint_005.pt"
    if sha(before) != ck_sha: return [dict(trajectory=tray, update=0, error="checkpoint_005 no coincide")]
    X, y, Xv, yv, m, opt, rng = _W["new_session"](S, J); Xtr, ytr, Xva, yva, Xte, yte, *_ = core.load_split(S)
    c = torch.load(before, weights_only=False); m.load_state_dict(c["model"]); opt.load_state_dict(c["optimizer"]); rng.bit_generator.state = c["numpy_rng"]; torch.set_rng_state(c["torch_rng"])
    filas = []; prev = 5
    def fila(k):
        tl, ta, _ = medir(m, X, y); vl, va, Xk = medir(m, Xv, yv); sl, sa, _ = medir(m, Xte, yte)
        return dict(trajectory=tray, split=S, init=J, update=k, train_loss=tl, train_acc=ta, val_loss=vl, val_acc=va, X=Xk, test_loss=sl, test_acc=sa, error="")
    for k in (10, 20, 30, 50):
        _W["updates"](m, opt, rng, X, y, k - prev); prev = k; R = fila(k)
        if k == 50:
            ref = torch.load(Path(t2a1) / "fase2" / "visitas" / tray / "u50" / "states" / tray / "checkpoint.pt", weights_only=False)["model"]
            R["dif_param_u50"] = max(float((a - ref[n]).abs().max()) for n, a in m.state_dict().items()); R["compuerta_u50"] = int(R["dif_param_u50"] <= 1e-12)
        filas.append(R)
    c250 = torch.load(Path(t2a1) / "fase2" / "visitas" / tray / "u250" / "states" / tray / "checkpoint.pt", weights_only=False)
    assert c250["step"] == 250; m.load_state_dict(c250["model"]); filas.append(fila(250))
    return filas


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--procesos", type=int, default=12)
    ap.add_argument("--root", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
    ap.add_argument("--t2a1", default=r"D:\RIPG_DATA\T2_A1"); ap.add_argument("--mocks", default=r"D:\RIPG_DATA\T2_A\cribado_borde\margen\mocks")
    a = ap.parse_args(); root = Path(a.root)
    man = [(r["trajectory"], r["checkpoint_sha256"]) for r in csv.DictReader(open(root / "metadata" / "cohort_manifest.csv", encoding="utf-8"))]
    man = [x for x in man if 12 <= int(x[0].split("_")[0][5:]) <= 167]
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True); prog = out / "PROGRESO_d9.csv"
    campos = ["trajectory", "split", "init", "update", "train_loss", "train_acc", "val_loss", "val_acc", "X", "test_loss", "test_acc", "dif_param_u50", "compuerta_u50", "error"]
    hechas = set()
    if prog.exists():
        por = {}
        for r in csv.DictReader(open(prog, encoding="utf-8")): por.setdefault(r["trajectory"], []).append(r)
        hechas = {t for t, v in por.items() if len(v) == 5 and not any(x["error"] for x in v)}
    nuevo = not prog.exists(); fh = open(prog, "a", newline="", encoding="utf-8"); w = csv.DictWriter(fh, fieldnames=campos, extrasaction="ignore")
    if nuevo: w.writeheader()
    pend = [x for x in man if x[0] not in hechas]; print(json.dumps(dict(trayectorias=len(man), pendientes=len(pend), script_sha256=sha(Path(__file__)))), flush=True); t0 = time.time()
    with ProcessPoolExecutor(max_workers=a.procesos, initializer=_init, initargs=(str(root), a.mocks)) as pool:
        futs = {pool.submit(una, t, h, a.t2a1): t for t, h in pend}
        for i, fu in enumerate(as_completed(futs), 1):
            try: F = fu.result()
            except Exception as e: F = [dict(trajectory=futs[fu], update=0, error=repr(e)[:300])]
            for r in F: w.writerow(r)
            fh.flush()
            if i % 50 == 0 or F[0].get("error"): print(f"[{i}/{len(pend)}] {futs[fu]} {'ERROR ' + F[0]['error'] if F[0].get('error') else 'ok'} ({(time.time() - t0) / 60:.1f} min)", flush=True)
    fh.close()
    filas = list(csv.DictReader(open(prog, encoding="utf-8"))); comp = [r for r in filas if r["update"] == "50" and not r["error"]]
    tabla = out / "d9_tabla.csv"
    with open(tabla, "w", newline="", encoding="utf-8") as f2:
        w2 = csv.DictWriter(f2, fieldnames=campos, extrasaction="ignore"); w2.writeheader(); w2.writerows(sorted((r for r in filas if not r["error"]), key=lambda r: (r["trajectory"], int(r["update"]))))
    res = dict(trayectorias=len(man), compuerta_pasa=sum(r["compuerta_u50"] == "1" for r in comp), compuerta_falla=sum(r["compuerta_u50"] != "1" for r in comp),
               errores=sum(1 for r in filas if r["error"]), tabla_sha256=sha(tabla), script_sha256=sha(Path(__file__)), nota="Sin asociaciones; el analisis se hace aparte.")
    (out / "RESUMEN_d9.json").write_text(json.dumps(res, indent=2)); print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
