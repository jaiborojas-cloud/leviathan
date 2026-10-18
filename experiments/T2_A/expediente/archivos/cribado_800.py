"""cribado_800.py - barrido EXPLORATORIO del margen basal (update 5) en los 800 estados.

- Solo lee la carpeta compacta; escribe unicamente en OUT.
- Reanudable: si cribado_800.csv ya tiene un estado, lo salta.
- Umbrales elegidos por el analista (no del protocolo): min_eff < 10 y max cond(G) > 100.
- Rejilla r/R = 1.0 ... 40.0, paso 0.5; 128 rayos. La resolucion del cruce es +-0.5R.
- No asigna clasificaciones ni outcomes.

Ejecucion (PowerShell, fuera del agente):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "D:\\RIPG_DATA\\T2_A\\cribado_borde\\margen\\cribado_800.py"
"""
import csv
import hashlib
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

N_RAYS = 128
MULTS = np.arange(1.0, 40.5, 0.5)
EFF_THR, COND_THR = 10.0, 100.0
OUT_CSV = OUT / "cribado_800.csv"
ERR_LOG = OUT / "errores_800.log"
FIELDS = ["id", "R", "eff_crit", "cond_crit", "seconds", "status", "npz_sha256", "json_sha256"]
SELF_CHECK_ID, SELF_CHECK_EXPECTED = "split8_j5_true", (15.5, 23.0)  # barrido ya reproducido


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def metrics(geo, M, f, r, n):
    """min_eff (por rayo, luego minimo) y max cond(G) en el radio absoluto r."""
    sol = geo.rays(r, n)
    P = sol.sol(r).reshape(2, n, 2)[0]            # (n, 2)
    logits = f @ P.T                              # (npanel, n)
    a = np.exp(logits - logits.max(axis=0, keepdims=True))
    a /= a.sum(axis=0, keepdims=True)
    eff = 1.0 / np.sum(a ** 2, axis=0)            # por rayo
    assert np.all(eff >= 1.0 - 1e-9) and np.all(eff <= f.shape[0] + 1e-9), (eff.min(), eff.max())
    max_cond = 0.0
    for i in range(n):
        ai = a[:, i]
        mu = (ai[:, None] * f).sum(axis=0)
        C = ai[:, None] * (f - mu)
        max_cond = max(max_cond, np.linalg.cond(C.T @ M @ C))
    return float(eff.min()), float(max_cond)


def crossings(M, f, R, n=N_RAYS):
    geo = Geometry(M, f)
    first_eff = first_cond = None
    for m in MULTS:
        min_eff, max_cond = metrics(geo, M, f, R * m, n)
        if first_eff is None and min_eff < EFF_THR:
            first_eff = float(m)
        if first_cond is None and max_cond > COND_THR:
            first_cond = float(m)
        if first_eff is not None and first_cond is not None:
            break
    return first_eff, first_cond


def load_state(sid):
    d = ROOT / "trajectories" / sid
    with np.load(d / "state_005.npz") as a:
        M, f = a["M"], a["f"]
    R = json.loads((d / "baseline_result.json").read_text())["nominal_radius"]
    return M, f, R, d


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ids = sorted(p.name for p in (ROOT / "trajectories").iterdir() if p.is_dir())
    print(f"{len(ids)} estados encontrados", flush=True)

    # Autocomprobacion: si no reproduce el resultado ya validado, no se continua.
    M, f, R, _ = load_state(SELF_CHECK_ID)
    got = crossings(M, f, R)
    print(f"autocomprobacion {SELF_CHECK_ID}: {got} (esperado {SELF_CHECK_EXPECTED})", flush=True)
    if got != SELF_CHECK_EXPECTED:
        sys.exit("ABORTA: la autocomprobacion no reproduce el resultado validado.")

    done = set()
    if OUT_CSV.exists():
        with open(OUT_CSV, newline="", encoding="utf-8") as fh:
            done = {row["id"] for row in csv.DictReader(fh)}
    new_file = not OUT_CSV.exists()

    t_start = time.perf_counter()
    with open(OUT_CSV, "a", newline="", encoding="utf-8") as fh, \
            open(ERR_LOG, "a", encoding="utf-8") as err:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        for k, sid in enumerate(ids, 1):
            if sid in done:
                continue
            t0 = time.perf_counter()
            row = dict(id=sid, R="", eff_crit="", cond_crit="", seconds="", status="",
                       npz_sha256="", json_sha256="")
            try:
                M, f, R, d = load_state(sid)
                e, c = crossings(M, f, R)
                row.update(R=repr(R), eff_crit="NA" if e is None else e,
                           cond_crit="NA" if c is None else c,
                           status="OK",
                           npz_sha256=sha256(d / "state_005.npz"),
                           json_sha256=sha256(d / "baseline_result.json"))
            except Exception as ex:  # nada de pass: se registra todo
                row["status"] = f"ERROR:{type(ex).__name__}"
                err.write(f"{sid}\n{traceback.format_exc()}\n")
                err.flush()
            row["seconds"] = f"{time.perf_counter() - t0:.3f}"
            w.writerow(row)
            fh.flush()
            print(f"[{k}/{len(ids)}] {sid} {row['status']} eff={row['eff_crit']} "
                  f"cond={row['cond_crit']} ({row['seconds']}s)", flush=True)

    # Resumen
    with open(OUT_CSV, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    print(f"\nfilas: {len(rows)}  errores: {sum(r['status'] != 'OK' for r in rows)}  "
          f"tiempo de esta sesion: {time.perf_counter() - t_start:.0f}s")
    for col in ("eff_crit", "cond_crit"):
        vals = np.array([float(r[col]) for r in rows if r["status"] == "OK" and r[col] != "NA"])
        na = sum(r[col] == "NA" for r in rows if r["status"] == "OK")
        if len(vals):
            print(f"{col}: min {vals.min()}  mediana {np.median(vals)}  max {vals.max()}  "
                  f"NA(sin cruce<=40R) {na}")


if __name__ == "__main__":
    main()
