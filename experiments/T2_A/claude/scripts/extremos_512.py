"""extremos_512.py - contraste de resolucion angular en los estados de menor margen basal.

EXPLORATORIO. Solo lee la compacta y cribado_800.csv; escribe unicamente en OUT.
- Selecciona, para cada umbral (min_eff < 10 y max cond(G) > 100), los 5 estados con
  menor cruce en cribado_800.csv (empates por id) y anade un control: split8_j5_true.
- Recalcula cada uno con 128, 256 y 512 rayos (rejilla gruesa de 0.5R) y refina cada
  cruce con paso 0.1R dentro del ultimo intervalo grueso.
- Autocomprobacion: el control debe dar (15.5, 23.0) en la rejilla gruesa para todo n;
  si no, aborta.
- No asigna clasificaciones ni outcomes.

Ejecucion (PowerShell, fuera del agente):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "D:\\RIPG_DATA\\T2_A\\cribado_borde\\margen\\extremos_512.py"
"""
import csv
import json
import sys
import time
import traceback
from pathlib import Path

import numpy as np

ROOT = Path(r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
OUT = Path(r"D:\RIPG_DATA\T2_A\cribado_borde\margen")
sys.path.insert(0, str(ROOT / "sources"))
from geometry import Geometry  # noqa: E402

NS = (128, 256, 512)
COARSE, FINE, MAXM = 0.5, 0.1, 40.0
EFF_THR, COND_THR = 10.0, 100.0
K = 5
CONTROL, CONTROL_EXPECTED = "split8_j5_true", (15.5, 23.0)
SRC = OUT / "cribado_800.csv"
OUT_CSV = OUT / "extremos_512.csv"
ERR_LOG = OUT / "errores_extremos_512.log"
FIELDS = ["id", "why", "n", "eff_coarse", "cond_coarse", "eff_fine", "cond_fine",
          "eff_n128_original", "cond_n128_original", "seconds", "status"]


def metrics(geo, M, f, r, n):
    """min_eff (por rayo, luego minimo) y max cond(G) en el radio absoluto r."""
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
    return float(eff.min()), float(max_cond)


def crossings(geo, M, f, R, n):
    coarse = {"eff": None, "cond": None}
    for m in np.arange(1.0, MAXM + COARSE / 2, COARSE):
        min_eff, max_cond = metrics(geo, M, f, R * m, n)
        if coarse["eff"] is None and min_eff < EFF_THR:
            coarse["eff"] = float(m)
        if coarse["cond"] is None and max_cond > COND_THR:
            coarse["cond"] = float(m)
        if None not in coarse.values():
            break
    fine = {}
    for key, thr in (("eff", EFF_THR), ("cond", COND_THR)):
        mc = coarse[key]
        fine[key] = mc
        if mc is None:
            continue
        for m in np.arange(mc - COARSE + FINE, mc - 1e-9, FINE):
            min_eff, max_cond = metrics(geo, M, f, R * m, n)
            hit = (min_eff < thr) if key == "eff" else (max_cond > thr)
            if hit:
                fine[key] = round(float(m), 2)
                break
    return coarse, fine


def load_state(sid):
    d = ROOT / "trajectories" / sid
    with np.load(d / "state_005.npz") as a:
        M, f = a["M"], a["f"]
    R = json.loads((d / "baseline_result.json").read_text())["nominal_radius"]
    return M, f, R


def main():
    with open(SRC, newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh)
                if r["status"] == "OK" and r["eff_crit"] != "NA" and r["cond_crit"] != "NA"]
    orig = {r["id"]: (float(r["eff_crit"]), float(r["cond_crit"])) for r in rows}
    sel = {}
    for col in ("eff_crit", "cond_crit"):
        for r in sorted(rows, key=lambda r: (float(r[col]), r["id"]))[:K]:
            sel.setdefault(r["id"], []).append(col)
    ids = [CONTROL] + [i for i in sel if i != CONTROL]
    print(f"{len(ids)} estados (control + extremos): {ids}", flush=True)

    results = {}
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh, \
            open(ERR_LOG, "w", encoding="utf-8") as err:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for sid in ids:
            why = "control" if sid == CONTROL else "+".join(sel[sid])
            M, f, R = load_state(sid)
            geo = Geometry(M, f)
            for n in NS:
                t0 = time.perf_counter()
                row = dict(id=sid, why=why, n=n, eff_coarse="", cond_coarse="", eff_fine="",
                           cond_fine="", eff_n128_original=orig[sid][0],
                           cond_n128_original=orig[sid][1], seconds="", status="OK")
                try:
                    coarse, fine = crossings(geo, M, f, R, n)
                    results[(sid, n)] = (coarse, fine)
                    row.update(eff_coarse=coarse["eff"], cond_coarse=coarse["cond"],
                               eff_fine=fine["eff"], cond_fine=fine["cond"])
                except Exception as ex:
                    row["status"] = f"ERROR:{type(ex).__name__}"
                    err.write(f"{sid} n={n}\n{traceback.format_exc()}\n")
                    err.flush()
                row["seconds"] = f"{time.perf_counter() - t0:.1f}"
                w.writerow(row)
                fh.flush()
                print(f"{sid} n={n} {row['status']} grueso=({row['eff_coarse']},{row['cond_coarse']}) "
                      f"fino=({row['eff_fine']},{row['cond_fine']}) {row['seconds']}s", flush=True)
            if sid == CONTROL:
                for n in NS:
                    c = results.get((CONTROL, n))
                    if c is None or (c[0]["eff"], c[0]["cond"]) != CONTROL_EXPECTED:
                        sys.exit(f"ABORTA: el control no reproduce {CONTROL_EXPECTED} con n={n}.")
                print("autocomprobacion del control OK\n", flush=True)

    print("\nResumen (cambio de cruce fino respecto a n=128, en unidades de R):")
    print(f"{'id':<22}{'why':<20}{'eff n128/256/512':<24}{'cond n128/256/512':<24}")
    worst_e = worst_c = 0.0
    for sid in ids[1:]:
        try:
            e = [results[(sid, n)][1]["eff"] for n in NS]
            c = [results[(sid, n)][1]["cond"] for n in NS]
        except KeyError:
            print(f"{sid}: faltan resultados (ver errores_extremos_512.log)")
            continue
        worst_e = max(worst_e, max(abs(x - e[0]) for x in e))
        worst_c = max(worst_c, max(abs(x - c[0]) for x in c))
        print(f"{sid:<22}{'+'.join(sel[sid]):<20}{str(e):<24}{str(c):<24}")
    print(f"\nmaximo cambio: eff {worst_e:.2f}R  cond {worst_c:.2f}R")


if __name__ == "__main__":
    main()
