"""medicion_mpfr_caso.py - mide intentos, rechazos y tamano de paso de DOP853 con aceleracion MPFR de 169 bits sobre una visita
de update 25 del piloto (por defecto split8_j7_true), como se hizo con j5 y j6. DIAGNOSTICO SEPARADO, solo lectura.

No reanuda ni modifica checkpoints pausados, no consume presupuesto adicional, no clasifica ni asigna Y. Lee el estado regenerado
(estados_u25/state_025_regen_<caso>.npz, cuyo SHA-256 se compara con regeneracion_u25.csv) y escribe SOLO --out/--log.
Integra hasta --radius (0.09 = cota de busqueda de la calibracion). Por paso aceptado registra t, dt, intentos, tiempo y dos
indicadores baratos de blow-up de los rayos: max|p| y max|v| (norma euclidea por rayo). CSV paso a paso; Ctrl+C conserva lo hecho
(el resumen final se escribe igual). Del orden de horas (en j5, 14-29 s por paso aceptado y ~139 pasos hasta r=0.07447).
Se pueden lanzar dos casos a la vez en dos ventanas de PowerShell (un hilo por proceso).

Ejecucion (PowerShell), ejemplo j7:
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "D:\\RIPG_DATA\\T2_A\\expediente\\anexo_implementacion\\medicion_mpfr_caso.py" --case split8_j7_true
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
ap.add_argument("--case", default="split8_j7_true")
ap.add_argument("--states", default=r"D:\RIPG_DATA\T2_A\expediente\estados_u25")
ap.add_argument("--outdir", default=r"D:\RIPG_DATA\T2_A\expediente\diagnostico_mpfr")
ap.add_argument("--nt", type=int, default=2048)
ap.add_argument("--radius", type=float, default=0.09, help="0.09 = cota de busqueda de la calibracion")
ap.add_argument("--time-cap", type=float, default=0.0, help="segundos; 0 = sin tope (se usa Ctrl+C)")
a = ap.parse_args()
OUTD = Path(a.outdir); OUTD.mkdir(parents=True, exist_ok=True)
a.state = str(Path(a.states) / f"state_025_regen_{a.case}.npz")
a.out = str(OUTD / f"mpfr_{a.case}.csv"); a.log = str(OUTD / f"mpfr_{a.case}.log")

GEOM_SHA = "b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3"
FAST_SHA = "b3d4a804dfa02197d235a9b00d0a98759fc8b5608446a7cc552b883478e6f63e"
STATE_SHA = [r["sha256"] for r in csv.DictReader(open(Path(a.states) / "regeneracion_u25.csv", encoding="utf-8")) if r["trajectory"] == a.case][0]
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
say(f"estado: {Path(a.state).name} sha {STATE_SHA[:8]}...  nt={nt}  radio pedido={r!r}  MPFR 169 bits  (Ctrl+C para detener)")

solver = DOP853(rhs, 0.0, y0, r, rtol=2e-10, atol=2e-12)
rows, status, last_att, last_fev, last_wall = [], "COMPLETO", 0, fev["n"], time.perf_counter()
FIELDS = ["step", "t0", "t", "dt", "t_over_R", "attempts", "rejected", "nfev", "wall_s", "max_p", "max_v"]
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
                   nfev=fev["n"] - last_fev, wall_s=now - last_wall,
                   max_p=float(np.max(np.linalg.norm(solver.y.reshape(2, nt, 2)[0], axis=1))), max_v=float(np.max(np.linalg.norm(solver.y.reshape(2, nt, 2)[1], axis=1))))
        rows.append(row); w.writerow(row); fh.flush()
        say(f"PASO {row['step']:>3}  t={row['t']:.7f}  dt={row['dt']:.3e}  intentos={n_att}  max|v|={row['max_v']:.3e}  {row['wall_s']:.1f}s")
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
