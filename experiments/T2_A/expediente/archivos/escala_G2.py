"""escala_G2.py - ¿que determina el margen basal? Contraste de un mecanismo concreto. EXPLORATORIO.

Solo lee la compacta y cribado_800.csv; escribe unicamente escala_G2.csv en OUT. No integra nada.
No asigna clasificaciones ni outcomes.

Argumento (hipotesis del analista, a falsar): los pesos softmax se concentran cuando los logits
f_i . P se separan unas ~L unidades; en la direccion u eso ocurre a un desplazamiento
D(u) ~ L / sigma(u), con sigma(u) la desviacion tipica de f . u. La distancia intrinseca es
~ sqrt(u^T G0 u) * D(u) y, como G0 = (f-fbar)^T M (f-fbar) / n^2, resulta
    r_cruce(u) ~ L * sqrt( (1/n) * w^T M w / ||w||^2 ),   w = (f - fbar) u,
es decir, la raiz del cociente de Rayleigh de M sobre el subespacio generado por las columnas
de (f - fbar). La escala de f se cancela. Predicciones que este script puede refutar:
  1) log(cruce) ~ a + b * (1/2) log rho_min con b ~ 1 y R2 alto;
  2) dado rho_min, los coeficientes de log sigma1 y log sigma2 (solo f) son ~ 0.

Ejecucion (PowerShell):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "D:\\RIPG_DATA\\T2_A\\cribado_borde\\margen\\escala_G2.py"
"""
import csv
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT = Path(r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
OUT = Path(r"D:\RIPG_DATA\T2_A\cribado_borde\margen")
SRC, OUT_CSV = OUT / "cribado_800.csv", OUT / "escala_G2.csv"


def features(M, f):
    n = f.shape[0]
    Fc = f - f.mean(axis=0)
    Q, _ = np.linalg.qr(Fc)                       # base ortonormal de span(f - fbar), (n, 2)
    rho = np.linalg.eigvalsh(Q.T @ M @ Q)         # ascendente
    sv = np.linalg.svd(Fc / np.sqrt(n), compute_uv=False)   # sigma1 >= sigma2
    G0 = (Fc.T @ M @ Fc) / n ** 2
    lam = np.linalg.eigvalsh(0.5 * (G0 + G0.T))
    return rho, sv, np.linalg.norm(Fc, axis=1).max(), lam


def between_share(groups, x):
    x = np.asarray(x, float)
    tot = ((x - x.mean()) ** 2).sum()
    within = 0.0
    for g in set(groups):
        xi = x[[i for i, k in enumerate(groups) if k == g]]
        within += ((xi - xi.mean()) ** 2).sum()
    return 1.0 - within / tot


def ols(X, y):
    X1 = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(X1, y, rcond=None)
    res = y - X1 @ beta
    r2 = 1.0 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return beta, r2, res


def main():
    with open(SRC, newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh)
                if r["status"] == "OK" and r["eff_crit"] != "NA" and r["cond_crit"] != "NA"]
    ids, rho, sv, mx, lam, eff, cond = [], [], [], [], [], [], []
    for r in rows:
        with np.load(ROOT / "trajectories" / r["id"] / "state_005.npz") as a:
            M, f = a["M"], a["f"]
        rr, ss, m, ll = features(M, f)
        ids.append(r["id"]); rho.append(rr); sv.append(ss); mx.append(m); lam.append(ll)
        eff.append(float(r["eff_crit"])); cond.append(float(r["cond_crit"]))
    rho, sv, mx, lam = map(np.array, (rho, sv, mx, lam))
    eff, cond = np.array(eff), np.array(cond)
    ok = (rho > 0).all(axis=1) & (lam > 0).all(axis=1)
    print(f"estados: {len(ids)}  excluidos por autovalores <= 0: {(~ok).sum()}")
    ids = [i for i, k in zip(ids, ok) if k]
    rho, sv, mx, lam, eff, cond = rho[ok], sv[ok], mx[ok], lam[ok], eff[ok], cond[ok]
    split = [i.split("_")[0] for i in ids]
    s = (lam[:, 0] * lam[:, 1]) ** 0.25

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "split", "rho_min", "rho_max", "sigma1", "sigma2", "max_norm_f", "s", "eff_crit", "cond_crit"])
        for k, i in enumerate(ids):
            w.writerow([i, split[k], rho[k, 0], rho[k, 1], sv[k, 0], sv[k, 1], mx[k], s[k], eff[k], cond[k]])

    cands = {
        "1/2 log rho_min (M en span f)": 0.5 * np.log(rho[:, 0]),
        "1/2 log rho_max (M en span f)": 0.5 * np.log(rho[:, 1]),
        "log sigma1 (solo f)": np.log(sv[:, 0]),
        "log sigma2 (solo f)": np.log(sv[:, 1]),
        "log max|f-fbar| (solo f)": np.log(mx),
        "log s (escala de G0)": np.log(s),
    }
    print(f"rho_min: min {rho[:, 0].min():.4g} med {np.median(rho[:, 0]):.4g} max {rho[:, 0].max():.4g}")
    print(f"varianza entre splits: 1/2 log rho_min {between_share(split, cands['1/2 log rho_min (M en span f)']):.3f}"
          f"  log sigma1 {between_share(split, cands['log sigma1 (solo f)']):.3f}")
    for name, y in (("eff_crit", eff), ("cond_crit", cond)):
        ly = np.log(y)
        print(f"\n== {name} ==  (entre splits sin ajustar: {between_share(split, ly):.3f})")
        for cn, x in cands.items():
            beta, r2, res = ols(x[:, None], ly)
            print(f"  {cn:<32} pendiente {beta[1]:6.2f}  R2 {r2:5.3f}  Spearman "
                  f"{spearmanr(x, y).correlation:6.3f}  var. entre splits del residuo {between_share(split, res):.3f}")
        X = np.column_stack([cands["1/2 log rho_min (M en span f)"], cands["log sigma1 (solo f)"],
                             cands["log sigma2 (solo f)"]])
        beta, r2, res = ols(X, ly)
        print(f"  conjunto [1/2 log rho_min, log sigma1, log sigma2]: coef = {np.round(beta[1:], 3)}  R2 {r2:.3f}"
              f"  var. entre splits del residuo {between_share(split, res):.3f}")


if __name__ == "__main__":
    main()
