"""medicion_rechazos_v2.py - mide intentos y rechazos de DOP853 con TOPE DE TIEMPO DENTRO DEL PASO y escritura parcial.

v2: pensado para split8_j5_true update 25 (estado regenerado, float64), donde la integracion se atasca cerca de 0.9-0.95 R_ref.
Si se alcanza el tope de tiempo (o el integrador falla) se escribe lo medido hasta ahi y se marca el estado; NO es una clasificacion.
Continua: v1 (`medicion_rechazos.py`, j6) queda intacto.

Descripcion original de v1:

EXPLORATORIO. No usa ni modifica el integrador del estudio: replica la llamada de Geometry.rays
(DOP853, rtol 2e-10, atol 2e-12, dense_output) con un contador alrededor de scipy.integrate._ivp.rk.rk_step.
Cada llamada a rk_step es UN INTENTO de paso; intentos - pasos aceptados = rechazos. Es una medicion, no una inferencia desde nfev.
No asigna clasificaciones ni outcomes. Solo lee la compacta y el estado regenerado; escribe unicamente OUT_CSV.

Autocomprobaciones (aborta si fallan): SHA-256 de geometry.py y del estado; el parche se activa (intentos >= pasos);
el radio final es el pedido; los pasos aceptados coinciden con los de solver.step().

Ejecucion (PowerShell; tope por defecto 180 s):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "D:\\RIPG_DATA\\T2_A\\cribado_borde\\margen\\medicion_rechazos_v2.py" 2>&1 | Tee-Object -FilePath "D:\\RIPG_DATA\\T2_A\\cribado_borde\\margen\\medicion_rechazos_j5.log"
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
ap.add_argument("--state", default=r"D:\RIPG_DATA\T2_A\cribado_borde\margen\state_025_regen.npz")
ap.add_argument("--out", default=r"D:\RIPG_DATA\T2_A\cribado_borde\margen\medicion_rechazos_j5.csv")
ap.add_argument("--state-sha", default="845c22519a20be8ceef4e35210157d97bd5bc223fc9f05e1769b91d998aa4776")
ap.add_argument("--nt", type=int, default=2048, help="numero de rayos (la visita usa 2048 en el replay MPFR)")
ap.add_argument("--radius", type=float, default=0.0797751845662646, help="R_ref = radio nominal basal de j5 (NO el nominal de update25, que no esta determinado)")
ap.add_argument("--time-cap", type=float, default=180.0)
a = ap.parse_args()

GEOM_SHA = "b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3"
STATE_SHA = a.state_sha
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sha(Path(a.sources) / "geometry.py") != GEOM_SHA:
    sys.exit("ABORTA: geometry.py no coincide con b4d1e0e4...")
if sha(a.state) != STATE_SHA:
    sys.exit("ABORTA: el estado no coincide con --state-sha")
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
T0 = time.perf_counter()


class TopeTiempo(Exception):
    pass


def counted(fun, t, y, f_, h, A, B, C, K):
    if time.perf_counter() - T0 > a.time_cap:      # el tope se aplica por INTENTO, tambien dentro de un paso
        raise TopeTiempo()
    att["calls"] += 1
    n0 = fev["n"]
    out = orig(fun, t, y, f_, h, A, B, C, K)
    att["fev_in_attempts"] += fev["n"] - n0
    return out


rkmod.rk_step = counted

solver = DOP853(rhs, 0.0, y0, r, rtol=2e-10, atol=2e-12)
rows, status, last_att, last_fev, last_wall = [], "COMPLETO", 0, fev["n"], time.perf_counter()
FIELDS = ["step", "t0", "t", "dt", "t_over_R", "attempts", "rejected", "nfev", "wall_s"]
fh = open(a.out, "w", newline="", encoding="utf-8")
w = csv.DictWriter(fh, fieldnames=FIELDS)
w.writeheader()
while solver.status == "running":
    t_prev = float(solver.t)
    try:
        msg = solver.step()
        if solver.status == "failed":
            status = f"INTEGRADOR_FALLO: {msg}"
            break
        solver.dense_output()  # solve_ivp lo llama en cada paso con dense_output=True
    except TopeTiempo:
        status = f"TOPE_DE_TIEMPO_{a.time_cap:g}s"
        break
    now = time.perf_counter()
    n_att = att["calls"] - last_att
    row = dict(step=len(rows) + 1, t0=t_prev, t=float(solver.t), dt=float(solver.t) - t_prev,
               t_over_R=float(solver.t) / r, attempts=n_att, rejected=n_att - 1,
               nfev=fev["n"] - last_fev, wall_s=now - last_wall)
    rows.append(row); w.writerow(row); fh.flush()
    last_att, last_fev, last_wall = att["calls"], fev["n"], time.perf_counter()
fh.close()

# intentos del paso interrumpido (no aceptado)
pend_att = att["calls"] - last_att
accepted_att = sum(x["attempts"] for x in rows)
assert att["calls"] == accepted_att + pend_att
if status == "COMPLETO":
    assert solver.status == "finished" and abs(float(solver.t) - r) < 1e-12, (solver.status, solver.t)
if rows:
    assert att["calls"] >= len(rows), "el parche de rk_step no se activo"

print("== entorno ==")
print(f"python {platform.python_version()}  numpy {np.__version__}  scipy {scipy.__version__}  {platform.platform()}")
print(f"procesador: {platform.processor()}  nucleos logicos: {os.cpu_count()}  (hilos BLAS fijados a 1)")
print("== caso ==")
print(f"estado: {Path(a.state).name}  sha {STATE_SHA[:8]}...  nt={nt}  radio pedido={r!r}  tope={a.time_cap:g}s")
print(f"ESTADO DE LA MEDICION: {status}   (no es una clasificacion)")
print("== medicion (DOP853 rtol 2e-10 atol 2e-12) ==")
print(f"t alcanzado: {float(solver.t)!r}  = {float(solver.t) / r:.6f} R   paso propuesto h_abs: {float(solver.h_abs)!r}")
print(f"pasos aceptados: {len(rows)}   intentos totales: {att['calls']}   rechazos en pasos aceptados: {sum(x['rejected'] for x in rows)}   intentos del paso interrumpido: {pend_att}")
if rows:
    print(f"evaluaciones de rhs por intento: {att['fev_in_attempts'] / max(att['calls'] - 0, 1):.3f}   nfev total: {fev['n']}")
    print(f"tiempo de pared: {time.perf_counter() - T0:.2f} s   mediana por paso: {np.median([x['wall_s'] for x in rows]):.4f} s   maximo: {max(x['wall_s'] for x in rows):.4f} s")
    print(f"rechazos por paso: maximo {max(x['rejected'] for x in rows)}   pasos con algun rechazo: {sum(x['rejected'] > 0 for x in rows)}")
    print(f"paso minimo dt: {min(x['dt'] for x in rows)!r}   ultimo dt: {rows[-1]['dt']!r}")
    print("ultimos 12 pasos (t/R, dt, intentos, tiempo):")
    for x in rows[-12:]:
        print(f"  {x['step']:>4}  {x['t_over_R']:.5f}  dt={x['dt']:.3e}  intentos={x['attempts']}  {x['wall_s']:.3f}s")
print(f"CSV: {a.out}")
