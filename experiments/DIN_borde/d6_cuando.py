"""d6_cuando.py (v1) - DIN-borde D6 (PLAN_D6_cuando_se_decide.md). Entrena 5->50 de forma continua reproduciendo el bloque del
ejecutor v12, guarda estados en 10,20,30,40,50, compuerta: state.npz(u50) == fase2 (SHA). rho_borde congelado en 10-40.
Uso (PowerShell):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I d6_cuando.py --out "D:\\RIPG_DATA\\T2_A1\\DIN_borde\\d6" --procesos 12
  --solo <tray> ... para prueba (otra --out). Reanudable (PROGRESO_d6.csv).
"""
import os
for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_k] = "1"
import argparse, csv, hashlib, json, math, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RHO_SHA = "d8ec69f89a75ab947ac05d3764858eb2e8f6dc873b47733645b2e8b5aac0416b"
PASOS = (10, 20, 30, 40, 50)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
_W = {}


def _init(root, mocks, rho_dir):
    src = Path(root) / "sources"
    for p in (str(src / "instrument"), mocks, str(src)):
        sys.path.insert(0, p)
    sys.path.append(rho_dir)
    import torch
    torch.set_num_threads(1)
    import core, rho_borde
    from training import new_session, updates
    from geometry import Geometry
    _W.update(torch=torch, core=core, rb=rho_borde, new_session=new_session, updates=updates, Geometry=Geometry, root=Path(root))


def una(tray, ck_sha, out, t2a1):
    torch, core = _W["torch"], _W["core"]; S, J = int(tray.split("_")[0][5:]), int(tray.split("_")[1][1:])
    before = _W["root"] / "trajectories" / tray / "checkpoint_005.pt"
    if sha(before) != ck_sha:
        return [dict(trajectory=tray, update=0, error="checkpoint_005 no coincide")]
    X, y, Xv, yv, m, opt, rng = _W["new_session"](S, J)
    c = torch.load(before, weights_only=False); assert c["step"] == 5 and c["split"] == S and c["init"] == J
    m.load_state_dict(c["model"]); opt.load_state_dict(c["optimizer"]); rng.bit_generator.state = c["numpy_rng"]; torch.set_rng_state(c["torch_rng"])
    d = Path(out) / "estados" / tray; d.mkdir(parents=True, exist_ok=True); filas = []; prev = 5
    for k in PASOS:
        _W["updates"](m, opt, rng, X, y, k - prev); prev = k
        Rb, Ub, f = core.make_geom_state(m, Xv, yv); M = core.subset_M(Rb, Ub, [0, 1, 2])
        p = d / f"u{k}.npz"; np.savez_compressed(p, M=M.detach().numpy(), f=f.detach().numpy())
        R = dict(trajectory=tray, split=S, init=J, update=k, state_sha256=sha(p), error="")
        with torch.no_grad():
            pv = torch.softmax(m(Xv), 1); pyv = pv[torch.arange(len(yv)), yv].numpy()
            pt = torch.softmax(m(X), 1); pyt = pt[torch.arange(len(y)), y]
            R.update(k_min=int(np.argmin(pyv)), p_min_val=float(pyv.min()), mal_val=int((pv.argmax(1) != yv).sum()), val_acc=float((pv.argmax(1) == yv).double().mean()),
                     train_loss=float(-torch.log(pyt).mean()), mal_train=int((pt.argmax(1) != y).sum()))
        Mn = M.detach().numpy().astype(float); dg = np.diag(Mn); R.update(k_star=int(np.argmax(dg)), diag_frac=float(dg.max() / np.trace(Mn)), trM=float(np.trace(Mn)))
        if k == 50:
            ref = Path(t2a1) / "fase2" / "visitas" / tray / "u50" / "states" / tray / "state.npz"
            R["compuerta_u50"] = int(ref.exists() and sha(ref) == R["state_sha256"])
        else:
            t0 = time.perf_counter(); RR = _W["rb"].rho_borde(_W["Geometry"](Mn, f.detach().numpy().astype(float)))
            R.update(rho_borde=RR["rho_borde"], dif_orden=RR.get("dif_orden"), dif_dir=RR.get("dif_dir"), seg_rho=round(time.perf_counter() - t0, 1))
        filas.append(R)
    return filas


def analizar(out, t2a1, filas):
    from scipy.stats import rankdata
    T = Path(t2a1); D = {}
    for r in filas: D[(r["trajectory"], int(r["update"]))] = r
    rho = {(r["trajectory"], int(r["update"])): float(r["rho"]) for r in csv.DictReader(open(T / "DIN_borde" / "d1" / "d1_estados.csv", encoding="utf-8"))}
    d4 = {(r["trajectory"], int(r["update"])): r for r in csv.DictReader(open(T / "DIN_borde" / "d4" / "d4_estados.csv", encoding="utf-8"))}
    d3 = {(r["trajectory"], int(r["update"])): r for r in csv.DictReader(open(T / "DIN_borde" / "d3" / "d3_estados.csv", encoding="utf-8"))}
    ng = {r["trajectory"]: r for r in csv.DictReader(open(T / "ng_u5" / "comparadores_ng_u5.csv", encoding="utf-8"))}
    ok = sorted({t for (t, k), r in D.items() if k == 50 and str(r.get("compuerta_u50")) == "1"})
    ok = [t for t in ok if all((t, k) in D and not D[(t, k)].get("error") for k in PASOS)]
    sp = np.array([int(t.split("_")[0][5:]) for t in ok]); ini = np.array([int(t.split("_")[1][1:]) for t in ok]); Y = np.log([rho[(t, 250)] for t in ok])
    def cen(v):
        v = np.array(v, float).copy()
        for s in np.unique(sp): v[sp == s] -= v[sp == s].mean()
        return v
    def W(x, yv, mask, semilla, B=5000):
        comps = []
        for s in np.unique(sp[mask]):
            k = mask & (sp == s); xs, ys = x[k], yv[k]
            if k.sum() < 3 or np.all(xs == xs[0]) or np.all(ys == ys[0]): continue
            o = np.lexsort((ini[k], xs)); rx = np.empty(k.sum()); rx[o] = np.arange(k.sum()); ry = rankdata(ys)
            rx -= rx.mean(); ry -= ry.mean(); comps.append((rx / np.linalg.norm(rx), ry / np.linalg.norm(ry)))
        if not comps: return dict(W=None, p_bilateral=None, splits=0)
        Wo = float(np.mean([a @ b for a, b in comps])); g = np.random.default_rng(semilla); acc = np.zeros(B)
        for a, b in comps: acc += g.permuted(np.tile(b, (B, 1)), axis=1) @ a
        Wp = acc / len(comps); return dict(W=Wo, p_bilateral=float((1 + np.sum(np.abs(Wp) >= abs(Wo) - 1e-12)) / (1 + B)), splits=len(comps))
    L = lambda p: math.log(max(1 - p, 1e-300)); todos = np.ones(len(ok), bool); par = sp % 2 == 0; res = dict(trayectorias_validas=len(ok), curva={}); sem = 240001
    for t in (5, 10, 20, 30, 40, 50):
        lr = np.log([rho[(x, t)] if t in (5, 50) else float(D[(x, t)]["rho_borde"]) for x in ok])
        lp = np.array([L(float(d4[(x, t)]["p_min"])) if t in (5, 50) else L(float(D[(x, t)]["p_min_val"])) for x in ok])
        va = np.array([float(ng[x]["val_acc"]) if t == 5 else float(D[(x, t)]["val_acc"]) if t != 50 else float(D[(x, 50)]["val_acc"]) for x in ok])
        ks = np.array([int(d3[(x, t)]["k_star"]) if t in (5, 50) else int(D[(x, t)]["k_star"]) for x in ok]); k250 = np.array([int(d3[(x, 250)]["k_star"]) for x in ok])
        df = np.array([float(d3[(x, t)]["diag_max"]) if t in (5, 50) else float(D[(x, t)]["diag_frac"]) for x in ok])
        e = cen(Y) - (cen(lr) @ cen(Y)) / (cen(lr) @ cen(lr)) * cen(lr)
        C = dict(W_logrho=W(lr, Y, todos, sem), W_logrho_pares=W(lr, Y, par, sem + 1)["W"], W_logrho_impares=W(lr, Y, ~par, sem + 2)["W"],
                 W_log1mpmin=W(lp, Y, todos, sem + 3), W_valacc=W(va, Y, todos, sem + 4), W_adj_log1mpmin_sobre_logrho_t=W(lp, e, todos, sem + 5) if t < 50 else None,
                 frac_kstar_igual_250=float(np.mean(ks == k250)), diag_frac_mediana=float(np.median(df)), rho_mediana=float(np.median(np.exp(lr))))
        if t not in (5, 50):
            C["mal_train_mediana"] = float(np.median([int(D[(x, t)]["mal_train"]) for x in ok]))
        res["curva"][t] = C; sem += 10
    return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--procesos", type=int, default=12)
    ap.add_argument("--root", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
    ap.add_argument("--t2a1", default=r"D:\RIPG_DATA\T2_A1"); ap.add_argument("--mocks", default=r"D:\RIPG_DATA\T2_A\cribado_borde\margen\mocks")
    ap.add_argument("--rho-dir", default=r"D:\RIPG_DATA\T2_A1\codigo\fase0prima"); ap.add_argument("--solo", nargs="*")
    a = ap.parse_args(); root = Path(a.root)
    if sha(Path(a.rho_dir) / "rho_borde.py") != RHO_SHA: sys.exit("ABORTA: rho_borde.py no coincide")
    man = [(r["trajectory"], r["checkpoint_sha256"]) for r in csv.DictReader(open(root / "metadata" / "cohort_manifest.csv", encoding="utf-8"))]
    man = [x for x in man if 12 <= int(x[0].split("_")[0][5:]) <= 167]
    if a.solo: man = [x for x in man if x[0] in set(a.solo)]
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True); prog = out / "PROGRESO_d6.csv"
    campos = ["trajectory", "split", "init", "update", "state_sha256", "k_min", "p_min_val", "mal_val", "val_acc", "train_loss", "mal_train", "k_star", "diag_frac", "trM",
              "rho_borde", "dif_orden", "dif_dir", "seg_rho", "compuerta_u50", "error"]
    hechas = set()
    if prog.exists():
        rr = list(csv.DictReader(open(prog, encoding="utf-8"))); por = {}
        for r in rr: por.setdefault(r["trajectory"], []).append(r)
        hechas = {t for t, v in por.items() if len(v) == len(PASOS) and not any(x["error"] for x in v)}
    nuevo = not prog.exists(); fh = open(prog, "a", newline="", encoding="utf-8"); w = csv.DictWriter(fh, fieldnames=campos, extrasaction="ignore")
    if nuevo: w.writeheader()
    pend = [x for x in man if x[0] not in hechas]; print(json.dumps(dict(trayectorias=len(man), pendientes=len(pend), script_sha256=sha(Path(__file__)))), flush=True); t0 = time.time()
    with ProcessPoolExecutor(max_workers=a.procesos, initializer=_init, initargs=(str(root), a.mocks, a.rho_dir)) as pool:
        futs = {pool.submit(una, t, h, str(out), a.t2a1): t for t, h in pend}
        for i, fu in enumerate(as_completed(futs), 1):
            try: F = fu.result()
            except Exception as e: F = [dict(trajectory=futs[fu], update=0, error=repr(e)[:300])]
            for r in F: w.writerow(r)
            fh.flush()
            if i % 25 == 0 or any(r.get("error") for r in F): print(f"[{i}/{len(pend)}] {futs[fu]} {'ERROR ' + F[0]['error'] if F[0].get('error') else 'ok'} ({(time.time() - t0) / 60:.1f} min)", flush=True)
    fh.close()
    filas = [r for r in csv.DictReader(open(prog, encoding="utf-8")) if not r.get("error")]
    comp = [r for r in filas if r["update"] == "50"]
    res = dict(trayectorias=len(man), compuerta_u50_pasa=sum(1 for r in comp if r["compuerta_u50"] == "1"), compuerta_u50_falla=sum(1 for r in comp if r["compuerta_u50"] != "1"),
               errores=sum(1 for r in csv.DictReader(open(prog, encoding="utf-8")) if r.get("error")), progreso_sha256=sha(prog), script_sha256=sha(Path(__file__)))
    if not a.solo:
        res["analisis"] = analizar(out, a.t2a1, filas)
    (out / "RESUMEN_d6.json").write_text(json.dumps(res, indent=2)); print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
