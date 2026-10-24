"""d5_descubrimiento.py (v1) - DIN-borde D5, descubrimiento exploratorio (PLAN_D5_descubrimiento.md). Carga los checkpoints del
update 50 ya guardados (no entrena) para medidas del conjunto de entrenamiento, y combina con d1/d4/ng. Uso (PowerShell):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I d5_descubrimiento.py --out "D:\\RIPG_DATA\\T2_A1\\DIN_borde\\d5"
"""
import argparse, csv, json, math, sys
from pathlib import Path

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True)
    ap.add_argument("--root", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
    ap.add_argument("--t2a1", default=r"D:\RIPG_DATA\T2_A1"); ap.add_argument("--mocks", default=r"D:\RIPG_DATA\T2_A\cribado_borde\margen\mocks")
    a = ap.parse_args(); root = Path(a.root); T = Path(a.t2a1); src = root / "sources"
    for p in (str(src / "instrument"), a.mocks, str(src)):
        sys.path.insert(0, p)
    import numpy as np, torch
    from scipy.stats import rankdata, spearmanr
    torch.set_num_threads(1)
    from training import new_session
    d1 = {(r["trajectory"], int(r["update"])): float(r["rho"]) for r in csv.DictReader(open(T / "DIN_borde" / "d1" / "d1_estados.csv", encoding="utf-8"))}
    d4 = {(r["trajectory"], int(r["update"])): r for r in csv.DictReader(open(T / "DIN_borde" / "d4" / "d4_estados.csv", encoding="utf-8"))}
    ng = {r["trajectory"]: float(r["val_acc"]) for r in csv.DictReader(open(T / "ng_u5" / "comparadores_ng_u5.csv", encoding="utf-8"))}
    trays = sorted({t for t, _ in d1}, key=lambda t: (int(t.split("_")[0][5:]), int(t.split("_")[1][1:])))
    L = lambda p: math.log(max(1 - p, 1e-300)); filas = []
    for i, t in enumerate(trays, 1):
        S, J = int(t.split("_")[0][5:]), int(t.split("_")[1][1:])
        X, y, Xv, yv, m, opt, rng = new_session(S, J)
        c = torch.load(T / "fase2" / "visitas" / t / "u50" / "states" / t / "checkpoint.pt", weights_only=False); m.load_state_dict(c["model"]); m.eval()
        with torch.no_grad():
            pr = torch.softmax(m(X), 1); py = pr[torch.arange(len(y)), y]
            tr_pmin = float(py.min()); tr_mal = int((pr.argmax(1) != y).sum()); tr_loss = float(-torch.log(py).mean())
        filas.append(dict(trajectory=t, split=S, init=J, Y=math.log(d1[(t, 250)]), P0=math.log(d1[(t, 50)]),
                          a=L(float(d4[(t, 50)]["p_k_star"])), b_pmin=L(tr_pmin), b_mal=tr_mal, b_loss=tr_loss, c=ng[t],
                          d=L(float(d4[(t, 50)]["p_min"])) - L(float(d4[(t, 5)]["p_min"]))))
        if i % 100 == 0: print(f"[{i}/{len(trays)}]", flush=True)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    with open(out / "d5_trayectorias.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0])); w.writeheader(); w.writerows(filas)
    sp = np.array([f["split"] for f in filas]); ini = np.array([f["init"] for f in filas]); Y = np.array([f["Y"] for f in filas]); P0 = np.array([f["P0"] for f in filas])
    def cen(v):
        v = np.array(v, float).copy()
        for s in np.unique(sp): v[sp == s] -= v[sp == s].mean()
        return v
    Yc, Pc = cen(Y), cen(P0); e = Yc - (Pc @ Yc) / (Pc @ Pc) * Pc
    def W(x, yv, mask, semilla, B=5000):
        rs, comps = [], []
        for s in np.unique(sp[mask]):
            k = mask & (sp == s); xs, ys = x[k], yv[k]
            if k.sum() < 3 or np.all(xs == xs[0]) or np.all(ys == ys[0]): continue
            o = np.lexsort((ini[k], xs)); rx = np.empty(k.sum()); rx[o] = np.arange(k.sum()); ry = rankdata(ys)
            rx -= rx.mean(); ry -= ry.mean(); rx /= np.linalg.norm(rx); ry /= np.linalg.norm(ry); rs.append(rx @ ry); comps.append((rx, ry))
        if not rs: return dict(W=None, p_bilateral=None, splits=0)
        Wo = float(np.mean(rs)); g = np.random.default_rng(semilla); acc = np.zeros(B)
        for rx, ry in comps: acc += g.permuted(np.tile(ry, (B, 1)), axis=1) @ rx
        Wp = acc / len(comps); return dict(W=Wo, p_bilateral=float((1 + np.sum(np.abs(Wp) >= abs(Wo) - 1e-12)) / (1 + B)), splits=len(rs))
    todos = np.ones(len(filas), bool); par = sp % 2 == 0; res = dict(n=len(filas), splits=len(np.unique(sp)), beta_Y_P0=float((Pc @ Yc) / (Pc @ Pc)), candidatos={})
    for i, c in enumerate(["P0", "a", "b_pmin", "b_mal", "b_loss", "c", "d"]):
        x = np.array([f[c] for f in filas], float)
        res["candidatos"][c] = dict(W=W(x, Y, todos, 230001 + i), W_adj=W(x, -0 + e, todos, 230011 + i) if c != "P0" else None,
                                    W_adj_pares=W(x, e, par, 230021 + i)["W"] if c != "P0" else None, W_adj_impares=W(x, e, ~par, 230031 + i)["W"] if c != "P0" else None,
                                    W_pares=W(x, Y, par, 230041 + i)["W"], W_impares=W(x, Y, ~par, 230051 + i)["W"], spearman_global=float(spearmanr(x, Y)[0]),
                                    spearman_con_P0_dentro_split=float(spearmanr(cen(x), Pc)[0]))
    (out / "d5_resumen.json").write_text(json.dumps(res, indent=2)); print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
