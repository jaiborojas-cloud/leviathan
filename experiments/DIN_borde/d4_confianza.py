"""d4_confianza.py (v1) - DIN-borde D4, exploratorio. Carga checkpoints ya guardados y calcula p(y) en el panel de validacion;
no entrena. Lee d3_estados.csv para k*. Uso (PowerShell, equipo del responsable):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I d4_confianza.py --d3 "D:\\RIPG_DATA\\T2_A1\\DIN_borde\\d3\\d3_estados.csv" --out "D:\\RIPG_DATA\\T2_A1\\DIN_borde\\d4"
"""
import argparse, csv, json, math, sys
from pathlib import Path

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--d3", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--root", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
    ap.add_argument("--t2a1", default=r"D:\RIPG_DATA\T2_A1"); ap.add_argument("--mocks", default=r"D:\RIPG_DATA\T2_A\cribado_borde\margen\mocks")
    a = ap.parse_args(); root = Path(a.root); src = root / "sources"
    for p in (str(src / "instrument"), a.mocks, str(src)):
        sys.path.insert(0, p)
    import numpy as np, torch
    from scipy.stats import spearmanr
    torch.set_num_threads(1)
    from training import new_session
    d3 = list(csv.DictReader(open(a.d3, encoding="utf-8"))); filas = []; ses = {}
    for i, r in enumerate(d3, 1):
        t, k, ks = r["trajectory"], int(r["update"]), int(r["k_star"]); S, J = int(t.split("_")[0][5:]), int(t.split("_")[1][1:])
        ck = root / "trajectories" / t / "checkpoint_005.pt" if k == 5 else Path(a.t2a1) / "fase2" / "visitas" / t / f"u{k}" / "states" / t / "checkpoint.pt"
        if t not in ses:
            ses = {t: new_session(S, J)}
        X, y, Xv, yv, m, opt, rng = ses[t]
        c = torch.load(ck, weights_only=False); m.load_state_dict(c["model"]); m.eval()
        with torch.no_grad():
            pr = torch.softmax(m(Xv), 1); py = pr[torch.arange(len(yv)), yv].numpy(); mal = int((pr.argmax(1) != yv).sum())
        orden = np.argsort(py)
        filas.append(dict(trajectory=t, split=S, update=k, rho=None, k_star=ks, k_min=int(orden[0]), rango_k_star=int(np.where(orden == ks)[0][0]) + 1,
                          p_k_star=float(py[ks]), p_min=float(py.min()), p_mediana=float(np.median(py)), mal_clasificados=mal, k_star_mal=int(pr[ks].argmax() != yv[ks])))
        if i % 300 == 0: print(f"[{i}/{len(d3)}]", flush=True)
    rho = {}
    for r in csv.DictReader(open(Path(a.t2a1) / "DIN_borde" / "d1" / "d1_estados.csv", encoding="utf-8")):
        rho[(r["trajectory"], int(r["update"]))] = float(r["rho"])
    for f in filas: f["rho"] = rho[(f["trajectory"], f["update"])]
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    with open(out / "d4_estados.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0])); w.writeheader(); w.writerows(filas)
    res = {}
    for k in (5, 50, 150, 250):
        F = [f for f in filas if f["update"] == k]; sp = np.array([f["split"] for f in F])
        lr = np.log([f["rho"] for f in F]); a1 = np.log(np.clip([1 - f["p_k_star"] for f in F], 1e-300, None)); a2 = np.log(np.clip([1 - f["p_min"] for f in F], 1e-300, None))
        def cen(v):
            v = np.array(v, float).copy()
            for s in np.unique(sp): v[sp == s] -= v[sp == s].mean()
            return v
        res[k] = dict(frac_kstar_es_kmin=float(np.mean([f["k_star"] == f["k_min"] for f in F])),
                      rango_k_star_cuartiles=[float(np.quantile([f["rango_k_star"] for f in F], q)) for q in (.25, .5, .75, .9)],
                      frac_kstar_mal_clasificado=float(np.mean([f["k_star_mal"] for f in F])), mal_clasificados_mediana=float(np.median([f["mal_clasificados"] for f in F])),
                      p_kstar_mediana=float(np.median([f["p_k_star"] for f in F])), p_mediana_panel=float(np.median([f["p_mediana"] for f in F])),
                      spearman_logrho_log1mp_kstar=float(spearmanr(lr, a1)[0]), spearman_logrho_log1mp_min=float(spearmanr(lr, a2)[0]),
                      spearman_dentro_split_logrho_log1mp_kstar=float(spearmanr(cen(lr), cen(a1))[0]))
    (out / "d4_resumen.json").write_text(json.dumps(res, indent=2)); print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
