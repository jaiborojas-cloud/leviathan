"""calibracion_incremental.py - CANDIDATO (T4', decision D5; no vigente hasta congelar). Recuperacion de la calibracion del radio nominal SIN cota fija:
integra los rayos con el MISMO solver, tolerancias e instrumentacion (driver v11: topes de intentos/tiempo y alarma de progreso de v1.0) con t_bound=0.09,
pero se detiene en cuanto el area del disco supera 0.02 (se evalua cada --check-every pasos aceptados), y busca la raiz de area(r)=0.02 con brentq
(xtol 1e-13) como bg.calibrate. Como DOP853 no depende de t_bound salvo en el ultimo paso recortado, las interpolantes usadas coinciden con las de v1.0 y el radio nominal
debe coincidir con el de v1.0 (validacion exigida: j6, j9, j17, dif < 1e-12). NUNCA integra mas alla de lo necesario. No reduce el area nominal (0.02).
Si la integracion se pausa (progreso/tiempo/intentos) antes de llegar a 0.02: escribe REVISION_PENDIENTE_incremental.json (area alcanzada, t) y termina; no clasifica.
Uso (PowerShell):
  & "...\\python.exe" -I "...\\calibracion_incremental.py" --state <state.npz> --out <carpeta_nueva> [--compare <nominal.json>]
"""
import os
for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_k] = "1"
import argparse, hashlib, json, sys, time, zipfile
from pathlib import Path
import numpy as np
from scipy.integrate import OdeSolution
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import resumable_dop853_instrumentado_v11 as R

GEOM_SHA = "b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3"
ap = argparse.ArgumentParser()
ap.add_argument("--state", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--sources", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto\sources")
ap.add_argument("--compare", default=None, help="nominal.json de v1.0 para comparar el radio")
ap.add_argument("--check-every", type=int, default=4)
ap.add_argument("--nt", type=int, default=2048)
ap.add_argument("--attempt-cap", type=int, default=250)
ap.add_argument("--time-cap", type=float, default=120.0)
a = ap.parse_args()
if hashlib.sha256((Path(a.sources) / "geometry.py").read_bytes()).hexdigest() != GEOM_SHA:
    sys.exit("ABORTA: geometry.py no coincide con b4d1e0e4...")
sys.path.insert(0, a.sources)
from geometry import Geometry, area7, triangles

out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
with np.load(a.state) as z:
    M, f = z["M"], z["f"]
g = Geometry(M, f); n = a.nt
g0 = g.jet(np.zeros((1, 2)))[0][0]
th = np.arange(n) * 2 * np.pi / n
v0 = np.linalg.solve(np.linalg.cholesky(g0).T, np.array([np.cos(th), np.sin(th)])).T


def rhs(t, y):
    p, v = y.reshape(2, n, 2)
    gam = g.jet(p)[4]
    return np.concatenate([v, -np.einsum('bkij,bi,bj->bk', gam, v, v)]).ravel()


y0 = np.concatenate([np.zeros_like(v0), v0]).ravel()
UPPER = 0.09


def area_of(sol, r):
    return area7(g, triangles(sol(np.linspace(0, r, 33)).T.reshape(33, 2, n, 2)[:, 0]))


class EarlyStop(Exception):
    pass


def load_partial(zpath):
    with zipfile.ZipFile(zpath) as zf:
        import cloudpickle
        b = cloudpickle.loads(zf.read("integration.pkl"))
    return b


def check(zpath, jpath, meta):
    b = load_partial(zpath)
    if len(b["interpolants"]) % a.check_every:      # solo cada check_every pasos aceptados (o al terminar)
        if meta["status"] == "running":
            return
    sol = OdeSolution(b["ts"], b["interpolants"])
    t = float(b["ts"][-1]); A = area_of(sol, t)
    print(f"   CHECK pasos={len(b['interpolants'])} t={t:.7f} area={A:.8f}", flush=True)
    if A >= 0.02:
        raise EarlyStop()


identity = hashlib.sha256(Path(a.state).read_bytes()).hexdigest()
drv = R.Driver(out / "ode_checkpoints", identity, max_new_steps=10**6, every=a.check_every, on_commit=check,
               attempt_cap=a.attempt_cap, time_cap_s=a.time_cap)
t0 = time.perf_counter()
state, sol = "AREA_ALCANZADA", None
try:
    res = drv(rhs, (0.0, UPPER), y0, "DOP853", 2e-10, 2e-12, True)       # termino sin llegar a 0.02 antes de 0.09
    state = "TERMINO_EN_0.09"
except EarlyStop:
    pass
except R.IntegrationPaused as e:
    state = f"PAUSED_PENDING_REVIEW ({getattr(e, 'reason', '?')})"
# estado final desde el ultimo checkpoint
d = next((out / "ode_checkpoints").iterdir())
meta = json.loads(sorted(d.glob("step_*.json"))[-1].read_text())
b = load_partial(d / meta["archive"])
sol = OdeSolution(b["ts"], b["interpolants"]); t_reach = float(b["ts"][-1]); A_reach = area_of(sol, t_reach)
rec = dict(estado=state, t_alcanzado=t_reach, area_en_t_alcanzado=A_reach, pasos=len(b["interpolants"]), intentos=meta.get("attempts"), rechazados=meta.get("rejected"),
           alarma_max=meta.get("alarm_count"), segundos=time.perf_counter() - t0, cap=dict(attempts=a.attempt_cap, time_s=a.time_cap))
if state == "AREA_ALCANZADA" and A_reach >= 0.02:
    r = brentq(lambda x: area_of(sol, x) - 0.02, 0, t_reach, xtol=1e-13)
    A = area_of(sol, r); assert abs(A / 0.02 - 1) <= 1e-6
    rec.update(radius=r, area_degree5=A, area_relative_error=A / 0.02 - 1)
    if a.compare:
        ref = json.loads(Path(a.compare).read_text())["radius"]
        rec.update(radius_v10=ref, dif_abs=abs(r - ref), coincide_1e12=bool(abs(r - ref) < 1e-12))
    (out / "nominal_incremental.json").write_text(json.dumps(rec, indent=2))
else:
    (out / "REVISION_PENDIENTE_incremental.json").write_text(json.dumps(rec, indent=2))
print(json.dumps(rec, indent=2))
