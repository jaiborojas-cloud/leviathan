"""Pruebas del driver instrumentado con EDO de juguete (sin geometria, sin torch). Ejecucion:
  python -I prueba_driver_instrumentado.py   (desde esta carpeta)  -> imprime PASS/FAIL por prueba."""
import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from scipy.integrate import solve_ivp
import resumable_dop853_instrumentado as R

def osc(w):
    def f(t, y): return np.array([y[1], -w * w * y[0]])
    return f
ok = True
def check(name, cond, info=""):
    global ok; ok &= bool(cond); print(("PASS " if cond else "FAIL ") + name, info)

# 1. equivalencia con solve_ivp y relacion nfev = 2 + 15*aceptados + 12*rechazos
f = osc(3.0); y0 = np.array([1.0, 0.0])
ref = solve_ivp(f, (0, 5), y0, method='DOP853', rtol=2e-10, atol=2e-12, dense_output=True)
with tempfile.TemporaryDirectory() as td:
    r = R.Driver(td, 'toy1')(f, (0, 5), y0, 'DOP853', 2e-10, 2e-12, True)
    meta = [__import__('json').loads(p.read_text()) for p in sorted(Path(td).rglob('step_*.json'))][-1]
    acc = len(r.t) - 1; att = meta['attempts']; rej = att - acc
    check("1a solucion identica a solve_ivp", np.array_equal(r.y, ref.y) and np.array_equal(r.t, ref.t))
    check("1b nfev == 2 + 15*aceptados + 12*rechazos (verificacion independiente del contador)",
          r.nfev == 2 + 15 * acc + 12 * rej, f"nfev={r.nfev} acc={acc} att={att} rej={rej}")

# 2. tope de intentos: pausa, checkpoint exacto, reanudacion con presupuesto adicional sin reiniciar contadores
f = osc(40.0)
with tempfile.TemporaryDirectory() as td:
    try:
        R.Driver(td, 'toy2', max_new_steps=10**6, attempt_cap=20, time_cap_s=1e9)(f, (0, 50), y0, 'DOP853', 2e-10, 2e-12, True); paused = None
    except R.IntegrationPaused as e: paused = e.reason
    m1 = [__import__('json').loads(p.read_text()) for p in sorted(Path(td).rglob('step_*.json'))][-1]
    check("2a pausa por tope de intentos", paused == 'PAUSED_ATTEMPT_CAP' and m1['attempts'] == 20, f"{paused} {m1['attempts']}")
    try:
        R.Driver(td, 'toy2', max_new_steps=10**6, attempt_cap=20, time_cap_s=1e9)(f, (0, 50), y0, 'DOP853', 2e-10, 2e-12, True); p2 = None
    except R.IntegrationPaused as e: p2 = e.reason
    check("2b sin presupuesto adicional vuelve a pausar sin consumir intentos", p2 == 'PAUSED_ATTEMPT_CAP')
    try:
        R.Driver(td, 'toy2', max_new_steps=10**6, attempt_cap=20, time_cap_s=1e9, extra_budget=True)(f, (0, 50), y0, 'DOP853', 2e-10, 2e-12, True); p3 = None
    except R.IntegrationPaused as e: p3 = e.reason
    m3 = [__import__('json').loads(p.read_text()) for p in sorted(Path(td).rglob('step_*.json'))][-1]
    check("2c con presupuesto adicional los contadores continuan (tope 40 acumulado)", p3 == 'PAUSED_ATTEMPT_CAP' and m3['attempts'] == 40 and m3['extra_used'], f"{p3} {m3['attempts']}")
    try:
        R.Driver(td, 'toy2', attempt_cap=20, extra_budget=True)(f, (0, 50), y0, 'DOP853', 2e-10, 2e-12, True); again = False
    except AssertionError: again = True
    except R.IntegrationPaused: again = False
    check("2d el presupuesto adicional no se puede usar dos veces", again)

# 3. alarma de progreso radial (EDO rapida: pasos < 1e-4)
f = osc(1.0e5)
with tempfile.TemporaryDirectory() as td:
    try:
        R.Driver(td, 'toy3', max_new_steps=10**6, attempt_cap=10**6, time_cap_s=1e9)(f, (0, 1), y0, 'DOP853', 2e-10, 2e-12, True); p = None
    except R.IntegrationPaused as e: p = e.reason
    m = [__import__('json').loads(p_.read_text()) for p_ in sorted(Path(td).rglob('step_*.json'))][-1]
    check("3a alarma dispara a los 8 pasos aceptados consecutivos", p == 'PAUSED_LOW_RADIAL_PROGRESS' and m['alarm_count'] == 8 and m['steps'] == 8, f"{p} {m['alarm_count']} {m['steps']}")

# 4. el paso final recortado no cuenta para la alarma
f = osc(3.0)
with tempfile.TemporaryDirectory() as td:
    r = R.Driver(td, 'toy4')(f, (0, 5), y0, 'DOP853', 2e-10, 2e-12, True)
    check("4 visita sana completa sin pausa", r.success)
print("RESULTADO GLOBAL:", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
