"""visita_rho.py - contrasta un state.npz (p. ej. split8_j5_true en update 25) con los basales. EXPLORATORIO.

Uso (PowerShell):
  & "...\\venv_torch\\Scripts\\python.exe" -I "...\\margen\\visita_rho.py" "RUTA\\state.npz" [SHA256_ESPERADO] [--basal ID]
  --basal ID: estado basal con el que comparar (por defecto split8_j5_true).

Solo lee la compacta y escala_G2.csv; no integra nada; no escribe archivos; no asigna outcomes.
Calcula, para el state.npz dado: autovalores de G(P0), rho_min y rho_max (cociente de Rayleigh de M
sobre el subespacio generado por f - fbar) y sigma1, sigma2 de f. Los compara con el basal
split8_j5_true (update 5) y con los 800 basales, y evalua la hipotesis del analista:
log(cruce de min_eff<10, en unidades de R) ~ a + b * (1/2) log rho_min  (ajuste sobre los 800 basales).
La prediccion SOLO es utilizable si rho_min cae dentro del rango basal; fuera de el, es extrapolacion.
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
OUT = Path(r"D:\RIPG_DATA\T2_A\cribado_borde\margen")
DEFAULT_BASAL = "split8_j5_true"
R_139 = 0.07447265825972331     # radio integrado en el paso aceptado 139 de split8_j5_true update 25 (referencia, no verificado)


def features(M, f):
    n = f.shape[0]
    Fc = f - f.mean(axis=0)
    Q, _ = np.linalg.qr(Fc)
    rho = np.linalg.eigvalsh(Q.T @ M @ Q)
    sv = np.linalg.svd(Fc / np.sqrt(n), compute_uv=False)
    G0 = (Fc.T @ M @ Fc) / n ** 2
    lam = np.linalg.eigvalsh(0.5 * (G0 + G0.T))
    return rho, sv, lam


def main():
    args = sys.argv[1:]
    basal_id = DEFAULT_BASAL
    if "--basal" in args:
        i = args.index("--basal")
        basal_id = args[i + 1]
        del args[i:i + 2]
    if not args:
        sys.exit("Uso: visita_rho.py RUTA\\state.npz [SHA256_ESPERADO] [--basal ID]")
    p = Path(args[0])
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    print(f"archivo: {p}\nSHA-256: {digest}\nbasal de comparacion: {basal_id}")
    if len(args) > 1:
        print("hash esperado:", "COINCIDE" if digest.lower() == args[1].strip().lower() else "NO COINCIDE")
    with np.load(p) as a:
        M, f = a["M"], a["f"]
    with np.load(ROOT / "trajectories" / basal_id / "state_005.npz") as a:
        M5, f5 = a["M"], a["f"]
    r_ref = json.loads((ROOT / "trajectories" / basal_id / "baseline_result.json").read_text())["nominal_radius"]
    print(f"M {M.shape}, f {f.shape}; max|f - f_basal| = {np.abs(f - f5).max():.3e}  "
          f"(0 si es el mismo panel); max|M| = {np.abs(M).max():.4g} (basal {np.abs(M5).max():.4g})")

    rho, sv, lam = features(M, f)
    rho5, sv5, lam5 = features(M5, f5)
    print(f"\nautovalores de G0:  este {lam}   basal {lam5}")
    print(f"rho_min: este {rho[0]:.5g}   basal {rho5[0]:.5g}   cociente este/basal {rho[0] / rho5[0]:.4g}")
    print(f"rho_max: este {rho[1]:.5g}   basal {rho5[1]:.5g}")
    print(f"sigma1, sigma2 de f: {sv}  (basal {sv5})")
    if (rho <= 0).any():
        sys.exit("AVISO: autovalores <= 0; no se puede continuar con el ajuste.")

    with open(OUT / "escala_G2.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    rmin = np.array([float(r["rho_min"]) for r in rows])
    eff = np.array([float(r["eff_crit"]) for r in rows])
    x = 0.5 * np.log(rmin)
    b, a0 = np.polyfit(x, np.log(eff), 1)
    pct = (rmin < rho[0]).mean() * 100
    print(f"\nrho_min en los 800 basales: min {rmin.min():.4g}  mediana {np.median(rmin):.4g}  max {rmin.max():.4g}")
    print(f"este valor queda en el percentil {pct:.1f} de los basales"
          f"{'  (FUERA del rango basal: extrapolacion)' if not (rmin.min() <= rho[0] <= rmin.max()) else ''}")
    pred = float(np.exp(a0 + b * 0.5 * np.log(rho[0])))
    base5 = float(np.exp(a0 + b * 0.5 * np.log(rho5[0])))
    print(f"ajuste sobre los 800: log(cruce_eff) = {a0:.3f} + {b:.3f} * 1/2 log rho_min")
    print(f"cruce predicho (min_eff<10) en unidades de R:  este {pred:.3f}   basal(ajuste) {base5:.3f}   "
          f"basal(medido) 15.05-15.5")

    if basal_id != DEFAULT_BASAL:
        print("\n(sin referencia de borde para este estado; compara rho_min con el de split8_j5_true update 25)")
        return
    t = R_139 / r_ref
    print(f"\nreferencia: r_139 / R_basal = {t:.4f}  (el radio nominal de update 25 NO esta determinado)")
    print("El borde (softmax a dos componentes) llega despues de min_eff<10; por tanto, para que el mecanismo "
          "sea consistente con la visita, el cruce predicho deberia ser <~ r_139/R.")
    need = (t / 15.3) ** (2.0 / b)
    print(f"caida de rho_min necesaria (basal -> visita) para que el cruce baje de ~15.3R a {t:.2f}R: "
          f"factor {need:.3g}  (observado: {rho[0] / rho5[0]:.3g})")


if __name__ == "__main__":
    main()
