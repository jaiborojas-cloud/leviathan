"""d3_colapso.py (v1) - DIN-borde D3, exploratorio. Lee los estados (M, f) de D1 y d1_estados.csv; no entrena ni integra.
Uso: python3 -I d3_colapso.py --t2a1 <carpeta T2_A1> --d1 <d1_estados.csv> --out <dir>"""
import argparse, csv, json, math
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull
from scipy.stats import spearmanr

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--t2a1", required=True); ap.add_argument("--d1", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(); B = Path(a.t2a1); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    filas = []
    for r in csv.DictReader(open(a.d1, encoding="utf-8")):
        t, k = r["trajectory"], int(r["update"])
        p = B / "rho_u5" / "estados_u5" / f"{t}.npz" if k == 5 else B / "fase2" / "visitas" / t / f"u{k}" / "states" / t / "state.npz"
        with np.load(p) as z:
            M, f = np.array(z["M"], float), np.array(z["f"], float)
        w, V = np.linalg.eigh((M + M.T) / 2); v = V[:, -1]; v2 = v ** 2; ks = int(np.argmax(v2))
        hull = set(ConvexHull(f).vertices.tolist()); d = np.diag(M) / np.trace(M)
        filas.append(dict(trajectory=t, split=int(r["split"]), update=k, log_rho_tilde=float(r["log_rho_tilde"]), lmax_frac=float(r["lmax_frac"]),
                          conc=float(v2[ks]), k_star=ks, pr_v=float(1 / np.sum(v2 ** 2)), diag_max=float(d.max()), k_diag=int(np.argmax(d)),
                          k_en_hull=int(ks in hull), n_hull=len(hull), n=len(f)))
    with open(out / "d3_estados.csv", "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(filas[0])); wr.writeheader(); wr.writerows(filas)
    n = filas[0]["n"]; piso = math.log(1 / n); res = dict(estados=len(filas), n=n, log_piso=piso, por_update={})
    for k in (5, 50, 150, 250):
        F = [x for x in filas if x["update"] == k]; c = np.array([x["conc"] for x in F]); lt = np.array([x["log_rho_tilde"] for x in F])
        lm = np.array([x["lmax_frac"] for x in F]); arriba = lt > piso + 0.05
        res["por_update"][k] = dict(conc_cuartiles=[float(np.quantile(c, q)) for q in (.1, .25, .5, .75, .9)],
                                    pr_v_mediana=float(np.median([x["pr_v"] for x in F])),
                                    frac_conc_mayor_0_9=float((c > 0.9).mean()),
                                    frac_k_en_hull=float(np.mean([x["k_en_hull"] for x in F])), frac_puntos_hull=float(np.mean([x["n_hull"] / n for x in F])),
                                    frac_k_star_igual_k_diag=float(np.mean([x["k_star"] == x["k_diag"] for x in F])),
                                    spearman_logrhotilde_conc=float(spearmanr(lt, c)[0]), spearman_logrhotilde_lmax=float(spearmanr(lt, lm)[0]),
                                    n_arriba_piso=int(arriba.sum()), conc_mediana_arriba=float(np.median(c[arriba])) if arriba.any() else None,
                                    conc_mediana_en_piso=float(np.median(c[~arriba])) if (~arriba).any() else None,
                                    k_star_distintos_por_split_mediana=float(np.median([len({x["k_star"] for x in F if x["split"] == s}) for s in sorted({x["split"] for x in F})])))
    D = {}
    for x in filas: D.setdefault(x["trajectory"], {})[x["update"]] = x["k_star"]
    res["k_star_estable_50_150_250"] = float(np.mean([len({D[t][50], D[t][150], D[t][250]}) == 1 for t in D]))
    res["k_star_u250_igual_u5"] = float(np.mean([D[t][250] == D[t][5] for t in D]))
    (out / "d3_resumen.json").write_text(json.dumps(res, indent=2)); print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
