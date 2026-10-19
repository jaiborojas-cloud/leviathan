"""sondeo_update25.py - sondeo directo de un state.npz (p. ej. update 25) a radios crecientes. EXPLORATORIO.

Uso (PowerShell):
  & "...\\venv_torch\\Scripts\\python.exe" -I "...\\margen\\sondeo_update25.py" "RUTA\\state.npz" ETIQUETA [--R 0.0797751845662646] [--max 1.0] [--step 0.05] [--n 128]

Integra los rayos (Geometry.rays, igual que en el barrido de los 800 basales) a r = R*m para
m = step, 2*step, ... hasta --max, y registra min_eff (minimo sobre rayos de 1/sum(a^2)) y max cond(G).
Para en cuanto max cond(G) > 1e8 o una integracion tarda mas de 120 s.
Solo lee la compacta (codigo y escala_G2.csv) y el state.npz dado; escribe unicamente
sondeo_<ETIQUETA>.csv en OUT. No asigna clasificaciones ni outcomes.

Compara el primer cruce de min_eff < 10 con la prediccion del modelo log(cruce) = a + b*(1/2)log(rho_min),
ajustado sobre los 800 basales y EXTRAPOLADO aqui (rho_min queda fuera del rango basal).
"""
import csv
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
OUT = Path(r"D:\RIPG_DATA\T2_A\cribado_borde\margen")
sys.path.insert(0, str(ROOT / "sources"))
from geometry import Geometry  # noqa: E402

DEFAULT_R = 0.0797751845662646   # radio nominal basal de split8_j5_true (referencia de unidades)
TIME_CAP, COND_STOP = 120.0, 1e8


def metrics(geo, M, f, r, n):
    sol = geo.rays(r, n)
    P = sol.sol(r).reshape(2, n, 2)[0]
    logits = f @ P.T
    a = np.exp(logits - logits.max(axis=0, keepdims=True))
    a /= a.sum(axis=0, keepdims=True)
    eff = 1.0 / np.sum(a ** 2, axis=0)
    assert np.all(eff >= 1.0 - 1e-9) and np.all(eff <= f.shape[0] + 1e-9), (eff.min(), eff.max())
    max_cond = 0.0
    for i in range(n):
        ai = a[:, i]
        mu = (ai[:, None] * f).sum(axis=0)
        C = ai[:, None] * (f - mu)
        max_cond = max(max_cond, np.linalg.cond(C.T @ M @ C))
    return float(eff.min()), float(max_cond), float(np.abs(P).max())


def rho_min(M, f):
    Fc = f - f.mean(axis=0)
    Q, _ = np.linalg.qr(Fc)
    return float(np.linalg.eigvalsh(Q.T @ M @ Q)[0])


def model_prediction(rho):
    with open(OUT / "escala_G2.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    x = 0.5 * np.log(np.array([float(r["rho_min"]) for r in rows]))
    y = np.log(np.array([float(r["eff_crit"]) for r in rows]))
    b, a0 = np.polyfit(x, y, 1)
    return float(np.exp(a0 + b * 0.5 * np.log(rho)))


def main():
    args = sys.argv[1:]
    opts = {"--R": DEFAULT_R, "--max": 1.0, "--step": 0.05, "--n": 128}
    for k in list(opts):
        if k in args:
            i = args.index(k)
            opts[k] = type(opts[k])(args[i + 1])
            del args[i:i + 2]
    if len(args) < 2:
        sys.exit("Uso: sondeo_update25.py RUTA\\state.npz ETIQUETA [--R x] [--max x] [--step x] [--n x]")
    path, label = Path(args[0]), args[1]
    R, mmax, step, n = opts["--R"], opts["--max"], opts["--step"], opts["--n"]
    with np.load(path) as a:
        M, f = a["M"], a["f"]
    rho = rho_min(M, f)
    pred = model_prediction(rho)
    print(f"{label}: rho_min = {rho:.5g}  -> el modelo (extrapolado) predice cruce de min_eff<10 en {pred:.3f} R "
          f"(R = {R})", flush=True)

    geo = Geometry(M, f)
    out_csv = OUT / f"sondeo_{label}.csv"
    first = {"eff<10": None, "cond>100": None, "cond>1e4": None, "cond>1e6": None}
    last_m = None
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["r_over_R", "r_abs", "min_eff", "max_cond", "max_abs_P", "seconds"])
        for m in np.arange(step, mmax + step / 2, step):
            t0 = time.perf_counter()
            try:
                min_eff, max_cond, pmax = metrics(geo, M, f, R * m, n)
            except Exception as ex:
                print(f"m={m:.3f}R ERROR {type(ex).__name__}: {ex}", flush=True)
                w.writerow([round(m, 4), R * m, "ERROR", str(type(ex).__name__), "", ""])
                break
            dt = time.perf_counter() - t0
            w.writerow([round(m, 4), R * m, min_eff, max_cond, pmax, round(dt, 2)])
            fh.flush()
            last_m = float(m)
            print(f"m={m:.3f}R r={R * m:.5f} min_eff={min_eff:8.3f} max_cond={max_cond:10.4g} max|P|={pmax:9.4g} ({dt:.1f}s)",
                  flush=True)
            for key, hit in (("eff<10", min_eff < 10), ("cond>100", max_cond > 100),
                             ("cond>1e4", max_cond > 1e4), ("cond>1e6", max_cond > 1e6)):
                if first[key] is None and hit:
                    first[key] = round(float(m), 4)
            if max_cond > COND_STOP or dt > TIME_CAP:
                print("parada: cond(G) > 1e8 o integracion lenta", flush=True)
                break
    print(f"\n== {label} ==  hasta m = {last_m} R   (resolucion del cruce: {step} R)")
    for k, v in first.items():
        print(f"  primer cruce {k}: {v}")
    print(f"  prediccion del modelo para min_eff<10: {pred:.3f} R")


if __name__ == "__main__":
    main()
