"""medicion_rechazos.py - mide intentos y rechazos de DOP853 sobre un caso YA CERRADO (split8_j6_true, update 25).

EXPLORATORIO. No usa ni modifica el integrador del estudio: replica la llamada de Geometry.rays
(DOP853, rtol 2e-10, atol 2e-12, dense_output) con un contador alrededor de scipy.integrate._ivp.rk.rk_step.
Cada llamada a rk_step es UN INTENTO de paso; intentos - pasos aceptados = rechazos. Es una medicion, no una inferencia desde nfev.
No asigna clasificaciones ni outcomes. Solo lee la compacta y el estado regenerado; escribe unicamente OUT_CSV.

Autocomprobaciones (aborta si fallan): SHA-256 de geometry.py y del estado; el parche se activa (intentos >= pasos);
el radio final es el pedido; los pasos aceptados coinciden con los de solver.step().

Ejecucion (PowerShell, tarda del orden de 1 minuto con 2048 rayos; no mas de unos minutos):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "D:\\RIPG_DATA\\T2_A\\cribado_borde\\margen\\medicion_rechazos.py" 2>&1 | Tee-Object -FilePath "D:\\RIPG_DATA\\T2_A\\cribado_borde\\margen\\medicion_rechazos.log"
"""
import os
for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_k] = "1"          # igual que el instrumento original
import argparse
import csv
import hashlib
import platform
import sys
import time
from pathlib import Path

import numpy as np
import scipy
import scipy.integrate._ivp.rk as rkmod
from scipy.integrate import DOP853

ap = argparse.ArgumentParser()
ap.add_argument("--sources", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto\sources")
ap.add_argument("--state", default=r"D:\RIPG_DATA\T2_A\cribado_borde\margen\state_025_regen_j6.npz")
ap.add_argument("--out", default=r"D:\RIPG_DATA\T2_A\cribado_borde\margen\medicion_rechazos_j6.csv")
ap.add_argument("--nt", type=int, default=2048, help="numero de rayos (la visita usa 2048 en el replay MPFR)")
ap.add_argument("--radius", type=float, default=0.07883553716312919, help="radio nominal registrado de j6 update25")
ap.add_argument("--time-cap", type=float, default=600.0)
a = ap.parse_args()

GEOM_SHA = "b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3"
STATE_SHA = "0e3fbfd3dd290b6cf11f8402664c224f668a2f9f4c4055d7e484ad19d5026cac"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sha(Path(a.sources) / "geometry.py") != GEOM_SHA:
    sys.exit("ABORTA: geometry.py no coincide con b4d1e0e4...")
if sha(a.state) != STATE_SHA:
    sys.exit("ABORTA: el estado no coincide con 0e3fbfd3... (state_025_regen_j6.npz)")
sys.path.insert(0, a.sources)
from geometry import Geometry  # noqa: E402

with np.load(a.state) as z:
    M, f = z["M"], z["f"]
geo = Geometry(M, f)
nt, r = a.nt, a.radius

# --- mismo problema que Geometry.rays (L.33-56 de geometry.py) ---
g = geo.jet(np.zeros((1, 2)))[0][0]
th = np.arange(nt) * 2 * np.pi / nt
v0 = np.linalg.solve(np.linalg.cholesky(g).T, np.array([np.cos(th), np.sin(th)])).T
y0 = np.concatenate([np.zeros_like(v0), v0]).ravel()

fev = {"n": 0}


def rhs(t, y):
    fev["n"] += 1
    p, v = y.reshape(2, nt, 2)
    gam = geo.jet(p)[4]
    return np.concatenate([v, -np.einsum("bkij,bi,bj->bk", gam, v, v)]).ravel()


# --- contador de intentos alrededor de rk_step ---
orig = rkmod.rk_step
att = {"calls": 0, "fev_in_attempts": 0}


def counted(fun, t, y, f_, h, A, B, C, K):
    att["calls"] += 1
    n0 = fev["n"]
    out = orig(fun, t, y, f_, h, A, B, C, K)
    att["fev_in_attempts"] += fev["n"] - n0
    return out


rkmod.rk_step = counted

solver = DOP853(rhs, 0.0, y0, r, rtol=2e-10, atol=2e-12)
rows, t_start = [], time.perf_counter()
last_att, last_fev, last_wall = 0, fev["n"], t_start
while solver.status == "running":
    t_prev, h_prev = float(solver.t), None
    msg = solver.step()
    now = time.perf_counter()
    if solver.status == "failed":
        sys.exit(f"INTEGRADOR FALLO: {msg}")
    solver.dense_output()  # solve_ivp lo llama en cada paso con dense_output=True
    n_att = att["calls"] - last_att
    rows.append(dict(step=len(rows) + 1, t0=t_prev, t=float(solver.t), dt=float(solver.t) - t_prev,
                     attempts=n_att, rejected=n_att - 1, nfev=fev["n"] - last_fev,
                     wall_s=now - last_wall))
    last_att, last_fev, last_wall = att["calls"], fev["n"], time.perf_counter()
    if time.perf_counter() - t_start > a.time_cap:
        sys.exit(f"TOPE DE TIEMPO {a.time_cap}s alcanzado en t={solver.t}; resultados parciales NO se escriben.")

# --- autocomprobaciones ---
assert att["calls"] >= len(rows) > 0, "el parche de rk_step no se activo"
assert abs(float(solver.t) - r) < 1e-12, (solver.t, r)
assert solver.status == "finished", solver.status
rejected_total = att["calls"] - len(rows)
assert rejected_total == sum(x["rejected"] for x in rows)

with open(a.out, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)

tot_wall = sum(x["wall_s"] for x in rows)
print("== entorno ==")
print(f"python {platform.python_version()}  numpy {np.__version__}  scipy {scipy.__version__}  {platform.platform()}")
print(f"procesador: {platform.processor()}  nucleos logicos: {os.cpu_count()}  (hilos BLAS fijados a 1)")
print("== caso ==")
print(f"estado: state_025_regen_j6.npz  sha {STATE_SHA[:8]}...  nt={nt}  radio pedido={r!r}")
print("== medicion (DOP853 rtol 2e-10 atol 2e-12) ==")
print(f"pasos aceptados: {len(rows)}   intentos (rk_step): {att['calls']}   rechazos: {rejected_total}")
print(f"evaluaciones de rhs por intento: {att['fev_in_attempts'] / att['calls']:.3f}")
print(f"nfev total (rhs, incluye dense_output): {fev['n']}   por paso aceptado: {fev['n'] / len(rows):.3f}")
print(f"tiempo de pared: {tot_wall:.2f} s   mediana por paso: {np.median([x['wall_s'] for x in rows]):.4f} s   maximo: {max(x['wall_s'] for x in rows):.4f} s")
print(f"rechazos por paso: maximo {max(x['rejected'] for x in rows)}   pasos con algun rechazo: {sum(x['rejected'] > 0 for x in rows)}")
print(f"paso minimo dt: {min(x['dt'] for x in rows)!r}   ultimo dt: {rows[-1]['dt']!r}")
print(f"CSV: {a.out}")
