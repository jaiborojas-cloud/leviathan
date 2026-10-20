"""diagnostico_split8.py - diagnostico SEPARADO y de SOLO LECTURA de las 4 visitas pausadas de split 8 (j5, j7, j8, j9).

Decision del responsable (2026-10-19 22:23): mantener pausadas y medir el tamano de paso aceptado, como se hizo con j5.
NO reanuda los checkpoints pausados, NO consume presupuesto adicional, NO clasifica ni asigna Y. Lee los estados
regenerados (estados_u25/state_025_regen_<traj>.npz) y la geometria de la compacta; escribe SOLO en --out.
Para cada visita integra los rayos como la calibracion (DOP853 rtol 2e-10 atol 2e-12, 2048 rayos, dense_output) con el
contador de intentos de medicion_rechazos.py (cada llamada a rk_step es un intento) hasta --radius (0.09 = cota de busqueda
de la calibracion) o hasta el tope de tiempo --time-cap por visita. Por paso aceptado registra t, dt, intentos, rechazos y
tiempo, y marca si el paso cumple dt < 1e-4 (el umbral de la alarma). El CSV se escribe paso a paso; Ctrl+C conserva lo hecho.
Resumen por visita: pasos, intentos, t alcanzado, dt minimo/mediano/ultimo, pasos con dt < 1e-4, racha maxima y la mediana de dt
en los ultimos 20 pasos. Control: j6 (calibra sano) con --ids split8_j6_true.

Ejecucion (PowerShell; hasta ~3 min por visita, ~12 min en total):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "D:\\RIPG_DATA\\T2_A\\expediente\\anexo_implementacion\\diagnostico_split8.py"
"""
import os
for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_k] = "1"
import argparse, csv, hashlib, platform, sys, time
from pathlib import Path
import numpy as np, scipy
import scipy.integrate._ivp.rk as rkmod
from scipy.integrate import DOP853

ap = argparse.ArgumentParser()
ap.add_argument("--sources", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto\sources")
ap.add_argument("--states", default=r"D:\RIPG_DATA\T2_A\expediente\estados_u25")
ap.add_argument("--out", default=r"D:\RIPG_DATA\T2_A\expediente\diagnostico_split8")
ap.add_argument("--ids", nargs="*", default=["split8_j5_true", "split8_j7_true", "split8_j8_true", "split8_j9_true"])
ap.add_argument("--radius", type=float, default=0.09)
ap.add_argument("--time-cap", type=float, default=180.0, help="segundos por visita")
ap.add_argument("--alarm-dr", type=float, default=1e-4)
a = ap.parse_args()
GEOM_SHA = "b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sha(Path(a.sources) / "geometry.py") != GEOM_SHA:
    sys.exit("ABORTA: geometry.py no coincide con b4d1e0e4...")
OUT = Path(a.out); OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, a.sources)
from geometry import Geometry  # noqa: E402
log = open(OUT / "diagnostico_split8.log", "a", encoding="utf-8")
def say(*p):
    s = " ".join(str(x) for x in p); print(s, flush=True); log.write(s + "\n"); log.flush()

class Tope(Exception):
    pass

say(f"== {time.strftime('%Y-%m-%d %H:%M:%S')}  python {platform.python_version()} numpy {np.__version__} scipy {scipy.__version__}  {platform.platform()}")
say(f"radio {a.radius}  tope por visita {a.time_cap:g} s  umbral dt {a.alarm_dr:g}  (solo lectura; no reanuda checkpoints)")
summ = []
try:
    for tid in a.ids:
        st = Path(a.states) / f"state_025_regen_{tid}.npz"
        with np.load(st) as z:
            M, f = z["M"], z["f"]
        geo = Geometry(M, f); nt = 2048
        g0 = geo.jet(np.zeros((1, 2)))[0][0]
        th = np.arange(nt) * 2 * np.pi / nt
        v0 = np.linalg.solve(np.linalg.cholesky(g0).T, np.array([np.cos(th), np.sin(th)])).T
        y0 = np.concatenate([np.zeros_like(v0), v0]).ravel()
        def rhs(t, y):
            p, v = y.reshape(2, nt, 2); gam = geo.jet(p)[4]
            return np.concatenate([v, -np.einsum("bkij,bi,bj->bk", gam, v, v)]).ravel()
        orig = rkmod.rk_step; att = {"n": 0}; T0 = time.perf_counter()
        def counted(fun, t, y, f_, h, A, B, C, K):
            if time.perf_counter() - T0 > a.time_cap:
                raise Tope()
            att["n"] += 1
            return orig(fun, t, y, f_, h, A, B, C, K)
        rkmod.rk_step = counted
        solver = DOP853(rhs, 0.0, y0, a.radius, rtol=2e-10, atol=2e-12)
        rows, status, last_att, last_wall = [], "COMPLETO", 0, time.perf_counter()
        fh = open(OUT / f"pasos_{tid}.csv", "w", newline="", encoding="utf-8")
        w = csv.DictWriter(fh, fieldnames=["step", "t", "dt", "attempts", "rejected", "wall_s", "dt_bajo_umbral"]); w.writeheader()
        try:
            while solver.status == "running":
                tp = float(solver.t); msg = solver.step()
                if solver.status == "failed":
                    status = f"INTEGRADOR_FALLO: {msg}"; break
                solver.dense_output(); now = time.perf_counter(); n = att["n"] - last_att
                dt = float(solver.t) - tp
                row = dict(step=len(rows) + 1, t=float(solver.t), dt=dt, attempts=n, rejected=n - 1, wall_s=now - last_wall,
                           dt_bajo_umbral=int(dt < a.alarm_dr)); rows.append(row); w.writerow(row); fh.flush()
                last_att, last_wall = att["n"], time.perf_counter()
        except Tope:
            status = f"TOPE_DE_TIEMPO_{a.time_cap:g}s"
        except KeyboardInterrupt:
            status = "INTERRUMPIDO_CON_CTRL_C"; raise
        finally:
            fh.close(); rkmod.rk_step = orig
            if rows:
                dts = np.array([r["dt"] for r in rows]); low = np.array([r["dt_bajo_umbral"] for r in rows]); run = best = 0
                for b in low:
                    run = run + 1 if b else 0; best = max(best, run)
                rec = dict(trajectory=tid, estado_medicion=status, pasos=len(rows), intentos=att["n"], t_final=rows[-1]["t"],
                           dt_min=float(dts.min()), dt_mediano=float(np.median(dts)), dt_ultimo=float(dts[-1]),
                           dt_mediano_ult20=float(np.median(dts[-20:])), pasos_dt_bajo_umbral=int(low.sum()), racha_max_bajo_umbral=best,
                           segundos=time.perf_counter() - T0)
                summ.append(rec)
                say(f"{tid}: {status}  pasos={rec['pasos']} intentos={rec['intentos']} t={rec['t_final']:.6f}  dt min/mediano/ult20={rec['dt_min']:.2e}/{rec['dt_mediano']:.2e}/{rec['dt_mediano_ult20']:.2e}  bajo umbral={rec['pasos_dt_bajo_umbral']} (racha {rec['racha_max_bajo_umbral']})  {rec['segundos']:.0f} s")
except KeyboardInterrupt:
    say("INTERRUMPIDO con Ctrl+C; lo ya medido queda en disco.")
finally:
    if summ:
        with open(OUT / "diagnostico_split8_resumen.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(summ[0])); w.writeheader(); w.writerows(summ)
    say("Diagnostico de solo lectura: sin clasificacion, sin outcomes, sin reanudar pausas.")
    log.close()
