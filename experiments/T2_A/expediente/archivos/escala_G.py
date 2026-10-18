"""escala_G.py - ¿el margen basal sigue la escala de la metrica en el origen? EXPLORATORIO.

Solo lee la compacta y cribado_800.csv; escribe unicamente escala_G.csv en OUT. No integra
nada (tarda segundos). No asigna clasificaciones ni outcomes.

Para cada estado: G0 = G(P=0) = C^T M C con pesos softmax uniformes (C = (f - fbar)/n_panel),
sus autovalores y la escala s = det(G0)^(1/4). Si G0 ~ s^2 * I, la distancia intrinseca a un
mismo desplazamiento de coordenadas escala con s, asi que el cruce (en unidades de R) deberia
ir como s: log(cruce) ~ a + b*log(s) con pendiente b ~ 1 si la escala domina.

Ejecucion (PowerShell):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "D:\\RIPG_DATA\\T2_A\\cribado_borde\\margen\\escala_G.py"
"""
import collections
import csv
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT = Path(r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
OUT = Path(r"D:\RIPG_DATA\T2_A\cribado_borde\margen")
SRC, OUT_CSV = OUT / "cribado_800.csv", OUT / "escala_G.csv"
CHECK_ID = "split8_j5_true"
CHECK_REPORTED = (0.54109689, 1.50462758)  # autovalores que reporto el agente (sin verificar)


def G0(M, f):
    C = (f - f.mean(axis=0)) / f.shape[0]
    G = C.T @ M @ C
    return 0.5 * (G + G.T)


def between_share(groups, x):
    """fraccion de la varianza de x explicada por el grupo (split)."""
    x = np.asarray(x, float)
    tot = ((x - x.mean()) ** 2).sum()
    within = 0.0
    for g in set(groups):
        xi = x[[i for i, k in enumerate(groups) if k == g]]
        within += ((xi - xi.mean()) ** 2).sum()
    return 1.0 - within / tot


def fit(x, y):
    b, a = np.polyfit(x, y, 1)
    res = y - (a + b * x)
    r2 = 1.0 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return b, r2, res


def main():
    with open(SRC, newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh)
                if r["status"] == "OK" and r["eff_crit"] != "NA" and r["cond_crit"] != "NA"]
    ids, lam, eff, cond = [], [], [], []
    for r in rows:
        with np.load(ROOT / "trajectories" / r["id"] / "state_005.npz") as a:
            M, f = a["M"], a["f"]
        ids.append(r["id"])
        lam.append(np.linalg.eigvalsh(G0(M, f)))
        eff.append(float(r["eff_crit"]))
        cond.append(float(r["cond_crit"]))
    lam, eff, cond = np.array(lam), np.array(eff), np.array(cond)
    if (lam <= 0).any():
        print(f"AVISO: {(lam <= 0).any(axis=1).sum()} estados con autovalores <= 0 en G0; se excluyen")
    keep = (lam > 0).all(axis=1)
    ids = [i for i, k in zip(ids, keep) if k]
    lam, eff, cond = lam[keep], eff[keep], cond[keep]
    s = (lam[:, 0] * lam[:, 1]) ** 0.25
    split = [i.split("_")[0] for i in ids]

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "split", "lam_min", "lam_max", "s", "eff_crit", "cond_crit"])
        for k, i in enumerate(ids):
            w.writerow([i, split[k], lam[k, 0], lam[k, 1], s[k], eff[k], cond[k]])

    if CHECK_ID in ids:
        k = ids.index(CHECK_ID)
        print(f"{CHECK_ID}: autovalores de G0 = {lam[k]}  (reportados por el agente: {CHECK_REPORTED})")
    print(f"estados usados: {len(ids)}")
    print(f"s: min {s.min():.4f}  mediana {np.median(s):.4f}  max {s.max():.4f}")
    print(f"fraccion de varianza de log(s) entre splits: {between_share(split, np.log(s)):.3f}")
    print(f"cociente lam_max/lam_min: mediana {np.median(lam[:, 1] / lam[:, 0]):.2f}")
    xs = {"log s (det^1/4)": np.log(s), "log sqrt(lam_min)": 0.5 * np.log(lam[:, 0]),
          "log sqrt(lam_max)": 0.5 * np.log(lam[:, 1])}
    for name, y in (("eff_crit", eff), ("cond_crit", cond)):
        ly = np.log(y)
        print(f"\n== {name} ==  (entre splits sin ajustar: {between_share(split, ly):.3f})")
        for xn, x in xs.items():
            b, r2, res = fit(x, ly)
            rho = spearmanr(x, y).correlation
            print(f"  {xn:<20} pendiente {b:6.2f}  R2 {r2:5.3f}  Spearman {rho:6.3f}  "
                  f"varianza entre splits del residuo {between_share(split, res):.3f}")


if __name__ == "__main__":
    main()
