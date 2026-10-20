"""validacion_driver_j6.py - comprueba el driver instrumentado sobre un caso YA CERRADO (split8_j6_true, update 25).

EXPLORATORIO. No clasifica ni asigna outcomes; no modifica ningun archivo de la compacta ni del estudio.
Para cada radio (nominal registrado 0.07883553716312919 y cota de busqueda 0.09) y con el MISMO problema de rayos
que medicion_rechazos.py (DOP853 rtol 2e-10 atol 2e-12, 2048 rayos, dense_output):
  A) integra con solve_ivp (referencia)  B) integra con el Driver instrumentado en una carpeta temporal.
Comprueba: soluciones identicas (t e y); intentos == 21 (radio nominal) y == 24 (0.09) como en las mediciones;
nfev == 2 + 15*aceptados + 12*rechazos con rechazos > 0 (verificacion independiente de la cuenta de rechazos);
la alarma de progreso NO dispara. Termina con RESULTADO GLOBAL: PASS/FAIL. Tiempo: del orden de 30 s.

Ejecucion (PowerShell):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "D:\\RIPG_DATA\\T2_A\\expediente\\anexo_implementacion\\validacion_driver_j6.py"
"""
import os
for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_k] = "1"
import hashlib, json, sys, tempfile, time
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp

HERE = Path(__file__).resolve().parent
SOURCES = Path(r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto\sources")
STATE = Path(r"D:\RIPG_DATA\T2_A\cribado_borde\margen\state_025_regen_j6.npz")
GEOM_SHA = "b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3"
STATE_SHA = "0e3fbfd3dd290b6cf11f8402664c224f668a2f9f4c4055d7e484ad19d5026cac"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sha(SOURCES / "geometry.py") != GEOM_SHA or sha(STATE) != STATE_SHA:
    sys.exit("ABORTA: hash de geometry.py o del estado no coincide")
sys.path.insert(0, str(SOURCES)); sys.path.insert(0, str(HERE))
from geometry import Geometry
import resumable_dop853_instrumentado as R

with np.load(STATE) as z:
    M, f = z["M"], z["f"]
geo = Geometry(M, f); nt = 2048
g = geo.jet(np.zeros((1, 2)))[0][0]
th = np.arange(nt) * 2 * np.pi / nt
v0 = np.linalg.solve(np.linalg.cholesky(g).T, np.array([np.cos(th), np.sin(th)])).T
y0 = np.concatenate([np.zeros_like(v0), v0]).ravel()

def rhs(t, y):
    p, v = y.reshape(2, nt, 2)
    gam = geo.jet(p)[4]
    return np.concatenate([v, -np.einsum("bkij,bi,bj->bk", gam, v, v)]).ravel()

ok = True
def check(name, cond, info=""):
    global ok; ok &= bool(cond); print(("PASS " if cond else "FAIL ") + name, info, flush=True)

for radius, want_att in ((0.07883553716312919, 21), (0.09, 24)):
    t0 = time.perf_counter()
    ref = solve_ivp(rhs, (0, radius), y0, method="DOP853", rtol=2e-10, atol=2e-12, dense_output=True)
    with tempfile.TemporaryDirectory() as td:
        res = R.Driver(td, f"j6_{radius}")(rhs, (0, radius), y0, "DOP853", 2e-10, 2e-12, True)
        meta = [json.loads(p.read_text()) for p in sorted(Path(td).rglob("step_*.json"))][-1]
    acc = len(res.t) - 1; att = meta["attempts"]; rej = att - acc
    check(f"[{radius}] soluciones identicas a solve_ivp", np.array_equal(res.t, ref.t) and np.array_equal(res.y, ref.y))
    check(f"[{radius}] intentos == {want_att}", att == want_att, f"aceptados={acc} intentos={att} rechazos={rej}")
    check(f"[{radius}] nfev == 2 + 15*acc + 12*rej (rechazos>0)", rej > 0 and res.nfev == 2 + 15 * acc + 12 * rej, f"nfev={res.nfev}")
    check(f"[{radius}] alarma de progreso sin disparar", meta["alarm_count"] < 8 and meta["last_reason"] is None, f"alarm_count={meta['alarm_count']}")
    print(f"   tiempo {time.perf_counter() - t0:.1f} s (referencia + driver)", flush=True)
print("RESULTADO GLOBAL:", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
