"""d1_escala_forma.py (v1) - DIN-borde D1, exploratorio. Lee estados (M, f) ya guardados y tablas de rho; no entrena ni integra.
Uso: python3 -I d1_escala_forma.py --t2a1 <carpeta D:\\RIPG_DATA\\T2_A1> --ng <comparadores_ng_u5.csv> --out <dir>"""
import argparse, csv, hashlib, json, math
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--t2a1", required=True); ap.add_argument("--ng", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(); B = Path(a.t2a1); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    rho = {}
    for r in csv.DictReader(open(B / "rho_u5" / "rho_borde_u5.csv", encoding="utf-8")):
        if 12 <= int(r["split"]) <= 167: rho[(r["trajectory"], 5)] = float(r["rho_borde"])
    for r in csv.DictReader(open(B / "fase2" / "fase2_rho.csv", encoding="utf-8")):
        rho[(r["trajectory"], int(r["update"]))] = float(r["rho_borde"])
    filas = []
    for (t, k), rv in sorted(rho.items()):
        p = B / "rho_u5" / "estados_u5" / f"{t}.npz" if k == 5 else B / "fase2" / "visitas" / t / f"u{k}" / "states" / t / "state.npz"
        with np.load(p) as z:
            M, f = np.array(z["M"], float), np.array(z["f"], float)
        ev = np.clip(np.linalg.eigvalsh((M + M.T) / 2), 0, None); tr = float(np.trace(M))
        filas.append(dict(trajectory=t, split=int(t.split("_")[0][5:]), update=k, rho=rv, trM=tr, half_log_trM=0.5 * math.log(tr),
                          log_rho_tilde=math.log(rv) - 0.5 * math.log(tr), lmax_frac=float(ev[-1] / ev.sum()),
                          rango_efectivo=float(ev.sum() ** 2 / (ev ** 2).sum()), f_sha=hashlib.sha256(np.ascontiguousarray(f).tobytes()).hexdigest()[:16]))
    campos = list(filas[0]); 
    with open(out / "d1_estados.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos); w.writeheader(); w.writerows(filas)
    D = {(r["trajectory"], r["update"]): r for r in filas}; trays = sorted({r["trajectory"] for r in filas})
    res = dict(estados=len(filas), f_constante_por_trayectoria=all(len({D[(t, k)]["f_sha"] for k in (5, 50, 150, 250)}) == 1 for t in trays))
    res["por_update"] = {k: {c: [float(np.quantile([D[(t, k)][c] for t in trays], q)) for q in (.25, .5, .75)]
                             for c in ("rho", "half_log_trM", "log_rho_tilde", "lmax_frac", "rango_efectivo")} for k in (5, 50, 150, 250)}
    ng = {r["trajectory"]: float(r["val_acc"]) for r in csv.DictReader(open(a.ng, encoding="utf-8"))}
    sp = np.array([D[(t, 5)]["split"] for t in trays])
    def cen(v):
        v = v.copy()
        for s in np.unique(sp): v[sp == s] -= v[sp == s].mean()
        return v
    res["reparto"] = {}
    for k in (50, 150, 250):
        dr = np.array([math.log(D[(t, k)]["rho"]) - math.log(D[(t, 5)]["rho"]) for t in trays])
        ds = np.array([D[(t, k)]["half_log_trM"] - D[(t, 5)]["half_log_trM"] for t in trays])
        dfm = dr - ds; R = {}
        for nombre, (x, y, z) in dict(total=(dr, ds, dfm), dentro_split=(cen(dr), cen(ds), cen(dfm))).items():
            v = x.var(); R[nombre] = dict(var_dlogrho=float(v), frac_escala=float(y.var() / v), frac_forma=float(z.var() / v), frac_2cov=float(2 * np.cov(y, z, bias=True)[0, 1] / v),
                                          mediana_dlogrho=float(np.median(x)), mediana_escala=float(np.median(y)), mediana_forma=float(np.median(z)))
        va = np.array([ng[t] for t in trays])
        R["val_acc_spearman_dentro_split"] = dict(con_dlogrho=float(spearmanr(cen(va), cen(dr))[0]), con_escala=float(spearmanr(cen(va), cen(ds))[0]), con_forma=float(spearmanr(cen(va), cen(dfm))[0]))
        res["reparto"][f"u5_a_u{k}"] = R
    (out / "d1_resumen.json").write_text(json.dumps(res, indent=2)); print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
