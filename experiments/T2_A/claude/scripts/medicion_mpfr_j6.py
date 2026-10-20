"""medicion_mpfr_j6.py - mide intentos, rechazos y tamano de paso de DOP853 con aceleracion MPFR de 169 bits
sobre un caso YA CERRADO (split8_j6_true, update 25). Referencia "sana" en MPFR para el anexo operativo de E1.

EXPLORATORIO. Usa FastMPFRAcceleration del instrumento (hash verificado), el mismo problema que el replay de j5
(2048 rayos, DOP853 rtol 2e-10 atol 2e-12, dense_output) y el contador de intentos de medicion_rechazos_v2.py
(cada llamada a scipy.integrate._ivp.rk.rk_step es un intento). Integra hasta el radio nominal registrado de j6.
No asigna clasificaciones ni outcomes. No usa ni modifica el integrador del estudio. Escribe solo OUT_CSV y OUT_LOG.

Se puede DETENER CON CTRL+C en cualquier momento: se escribe un resumen de lo medido hasta ahi (CSV por paso y log
ya estan en disco; el log tambien se escribe desde el propio script, no depende de Tee-Object).
Tiempo esperado: del orden de 5 a 15 minutos (el replay MPFR de j5 tardo 14-29 s por paso aceptado).

Requiere gmpy2 (el venv de torch puede no tenerlo: `... python.exe -m pip install gmpy2`, decision tuya).

Ejecucion (PowerShell):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "D:\\RIPG_DATA\\T2_A\\cribado_borde\\margen\\medicion_mpfr_j6.py"
"""
import os
for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_k] = "1"
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
ap.add_argument("--mpfr-dir", default=r"D:\RIPG_DATA\T2_A\cribado_borde\margen\mpfr_src",
                help="carpeta con fast_mpfr_acceleration.py (copia verificada por hash)")
ap.add_argument("--state", default=r"D:\RIPG_DATA\T2_A\cribado_borde\margen\state_025_regen_j6.npz")
ap.add_argument("--out", default=r"D:\RIPG_DATA\T2_A\cribado_borde\margen\medicion_mpfr_j6.csv")
ap.add_argument("--log", default=r"D:\RIPG_DATA\T2_A\cribado_borde\margen\medicion_mpfr_j6.log")
ap.add_argument("--nt", type=int, default=2048)
ap.add_argument("--radius", type=float, default=0.07883553716312919, help="radio nominal registrado de j6 update25")
ap.add_argument("--time-cap", type=float, default=0.0, help="segundos; 0 = sin tope (se usa Ctrl+C)")
a = ap.parse_args()

GEOM_SHA = "b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3"
FAST_SHA = "b3d4a804dfa02197d235a9b00d0a98759fc8b5608446a7cc552b883478e6f63e"
STATE_SHA = "0e3fbfd3dd290b6cf11f8402664c224f668a2f9f4c4055d7e484ad19d5026cac"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

logfh = open(a.log, "w", encoding="utf-8")


def say(*parts):
    line = " ".join(str(p) for p in parts)
    print(line, flush=True)
    logfh.write(line + "\n"); logfh.flush()


for path, want, name in ((Path(a.sources) / "geometry.py", GEOM_SHA, "geometry.py"),
                         (Path(a.mpfr_dir) / "fast_mpfr_acceleration.py", FAST_SHA, "fast_mpfr_acceleration.py"),
                         (Path(a.state), STATE_SHA, "state_025_regen_j6.npz")):
    if sha(path) != want:
        say(f"ABORTA: {name} no coincide con {want[:8]}...")
        sys.exit(1)
try:
    import gmpy2  # noqa: F401
except ImportError:
    say("ABORTA: falta gmpy2 (pip install gmpy2 en el venv, si lo decides).")
    sys.exit(1)
sys.path.insert(0, a.sources); sys.path.insert(0, a.mpfr_dir)
from geometry import Geometry  # noqa: E402
from fast_mpfr_acceleration import FastMPFRAcceleration  # noqa: E402

with np.load(a.state) as z:
    M, f = z["M"], z["f"]
g = Geometry(M, f)
E = FastMPFRAcceleration(g)
nt, r = a.nt, a.radius

G0 = g.jet(np.zeros((1, 2)))[0][0]
th = np.arange(nt) * 2 * np.pi / nt
v0 = np.linalg.solve(np.linalg.cholesky(G0).T, np.array([np.cos(th), np.sin(th)])).T
y0 = np.concatenate([np.zeros_like(v0), v0]).ravel()

fev = {"n": 0}


def rhs(t, y):
    fev["n"] += 1
    return E.bundle_rhs(t, y)


orig = rkmod.rk_step
att = {"calls": 0, "fev_in_attempts": 0}
T0 = time.perf_counter()


class TopeTiempo(Exception):
    pass


def counted(fun, t, y, f_, h, A, B, C, K):
    if a.time_cap and time.perf_counter() - T0 > a.time_cap:
        raise TopeTiempo()
    att["calls"] += 1
    n0 = fev["n"]
    out = orig(fun, t, y, f_, h, A, B, C, K)
    att["fev_in_attempts"] += fev["n"] - n0
    return out


rkmod.rk_step = counted

say("== entorno ==")
say(f"python {platform.python_version()}  numpy {np.__version__}  scipy {scipy.__version__}  gmpy2 {gmpy2.version()}  {platform.platform()}")
say(f"procesador: {platform.processor()}  nucleos logicos: {os.cpu_count()}  (hilos BLAS fijados a 1)")
say("== caso ==")
say(f"estado: state_025_regen_j6.npz sha {STATE_SHA[:8]}...  nt={nt}  radio pedido={r!r}  MPFR 169 bits  (Ctrl+C para detener)")

solver = DOP853(rhs, 0.0, y0, r, rtol=2e-10, atol=2e-12)
rows, status, last_att, last_fev, last_wall = [], "COMPLETO", 0, fev["n"], time.perf_counter()
FIELDS = ["step", "t0", "t", "dt", "t_over_R", "attempts", "rejected", "nfev", "wall_s"]
fh = open(a.out, "w", newline="", encoding="utf-8")
w = csv.DictWriter(fh, fieldnames=FIELDS)
w.writeheader()
try:
    while solver.status == "running":
        t_prev = float(solver.t)
        msg = solver.step()
        if solver.status == "failed":
            status = f"INTEGRADOR_FALLO: {msg}"
            break
        solver.dense_output()
        now = time.perf_counter()
        n_att = att["calls"] - last_att
        row = dict(step=len(rows) + 1, t0=t_prev, t=float(solver.t), dt=float(solver.t) - t_prev,
                   t_over_R=float(solver.t) / r, attempts=n_att, rejected=n_att - 1,
                   nfev=fev["n"] - last_fev, wall_s=now - last_wall)
        rows.append(row); w.writerow(row); fh.flush()
        say(f"PASO {row['step']:>3}  t/R={row['t_over_R']:.5f}  dt={row['dt']:.3e}  intentos={n_att}  {row['wall_s']:.1f}s")
        last_att, last_fev, last_wall = att["calls"], fev["n"], time.perf_counter()
except KeyboardInterrupt:
    status = "INTERRUMPIDO_CON_CTRL_C"
except TopeTiempo:
    status = f"TOPE_DE_TIEMPO_{a.time_cap:g}s"
finally:
    fh.close()

pend_att = att["calls"] - last_att
say("")
say(f"ESTADO DE LA MEDICION: {status}   (no es una clasificacion)")
say("== medicion (DOP853 rtol 2e-10 atol 2e-12, MPFR 169 bits) ==")
say(f"t alcanzado: {float(solver.t)!r} = {float(solver.t) / r:.6f} R   paso propuesto h_abs: {float(solver.h_abs)!r}")
say(f"pasos aceptados: {len(rows)}   intentos totales: {att['calls']}   rechazos en pasos aceptados: {sum(x['rejected'] for x in rows)}   intentos del paso interrumpido: {pend_att}")
if rows:
    say(f"rhs por intento: {att['fev_in_attempts'] / max(att['calls'], 1):.3f}   nfev total: {fev['n']}")
    say(f"tiempo de pared: {time.perf_counter() - T0:.1f} s   mediana por paso: {np.median([x['wall_s'] for x in rows]):.2f} s   maximo: {max(x['wall_s'] for x in rows):.2f} s")
    say(f"rechazos por paso: maximo {max(x['rejected'] for x in rows)}   pasos con algun rechazo: {sum(x['rejected'] > 0 for x in rows)}")
    say(f"paso minimo dt: {min(x['dt'] for x in rows)!r}   ultimo dt: {rows[-1]['dt']!r}")
say(f"CSV: {a.out}")
say(f"LOG: {a.log}")
logfh.close()
