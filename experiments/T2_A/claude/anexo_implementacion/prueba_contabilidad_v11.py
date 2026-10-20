"""Pruebas de la contabilidad corregida (candidato v1.1) con EDO de juguete (sin geometria, sin torch).
Cada prueba se ejecuta con el codigo VIGENTE del piloto (debe MOSTRAR el defecto) y con el candidato v11 (debe pasar).
Revision externa 2026-10-20: (1) con extra_budget el tope de visita se duplicaba dos veces; (2) el tope de visita solo sumaba integraciones TERMINADAS;
(3) rechazados = intentos - n podia salir negativo con checkpoints historicos. Ejecucion: python -I prueba_contabilidad_v11.py  (~40 s)."""
import sys, tempfile, json, time, zipfile, hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np, cloudpickle
import resumable_dop853_instrumentado as Rold
import resumable_dop853_instrumentado_v11 as Rnew
import visita_completa_instrumentada as Vold
import visita_completa_instrumentada_v11 as Vnew

def slow(w, dt=0.01):
    def f(t, y):
        time.sleep(dt); return np.array([y[1], -w * w * y[0]])
    return f
y0 = np.array([1.0, 0.0]); ARGS = ((0, 1e4), y0, 'DOP853', 2e-10, 2e-12, True)
ok = True
def check(name, cond, info=""):
    global ok; ok &= bool(cond); print(("PASS " if cond else "FAIL ") + name, info)
def last_meta(root, ident=None):
    ms = [json.loads(p.read_text()) for p in sorted(Path(root).rglob('step_*.json'))]
    return ms
def wall_total(root):
    t = 0.0
    for d in Path(root).iterdir():
        if d.is_dir():
            ms = sorted(d.glob('step_*.json'))
            if ms: t += json.loads(ms[-1].read_text())['wall_seconds']
    return t
def run(driver):
    try:
        driver(slow(40.0), *ARGS); return None
    except Rold.IntegrationPaused as e: return e.reason
    except Rnew.IntegrationPaused as e: return e.reason

# 1. presupuesto adicional y tope de visita: el consumo total no debe pasar de 2 x visita_cap (+ tolerancia de un intento)
CAP = 2.0
with tempfile.TemporaryDirectory() as td:
    Vold.ROOTS[:] = [Path(td)]
    r = run(Vold.StageDriver("rays", td, 'toy1', time_cap_s=100.0, extra_budget=True, visit_cap_s=CAP, max_new_steps=10**6))
    w_old = wall_total(td)
with tempfile.TemporaryDirectory() as td:
    Vnew.ROOTS[:] = [Path(td)]
    r2 = run(Vnew.StageDriver("rays", td, 'toy1', time_cap_s=100.0, extra_budget=True, visit_cap_s=CAP, max_new_steps=10**6, roots=Vnew.ROOTS))
    w_new = wall_total(td)
print(f"   (vigente) tiempo usado {w_old:.2f} s con tope efectivo previsto {2*CAP:.1f} s ; (v11) {w_new:.2f} s")
check("1a [vigente] EXCEDE el tope de visita duplicado (defecto reproducido)", w_old > 2 * CAP + 1.0, f"{w_old:.2f}")
check("1b [v11] respeta el tope de visita duplicado una sola vez", r2 == 'PAUSED_TIME_CAP' and w_new <= 2 * CAP + 0.5, f"{w_new:.2f}")

# 2. integraciones PARCIALES cuentan para el tope de visita
def partial_case(V, R):
    with tempfile.TemporaryDirectory() as td:
        V.ROOTS[:] = [Path(td)]
        kw = dict(time_cap_s=100.0, max_new_steps=10**6)
        extra = dict(roots=V.ROOTS) if V is Vnew else {}
        run(V.StageDriver("rays", td, 'A', visit_cap_s=1.0, **kw, **extra))          # A queda PAUSADA (parcial) tras ~1 s
        wa = wall_total(td)
        run(V.StageDriver("jacobi", td, 'B', visit_cap_s=1.5, **kw, **extra))         # B: queda 1.5 - A de visita
        return wa, wall_total(td) - wa
wa, wb = partial_case(Vold, Rold); wa2, wb2 = partial_case(Vnew, Rnew)
print(f"   (vigente) A={wa:.2f} s, B={wb:.2f} s ; (v11) A={wa2:.2f} s, B={wb2:.2f} s ; B permitido = {1.5 - wa2:.2f} s")
check("2a [vigente] ignora la integracion parcial A (B usa ~1.5 s) (defecto reproducido)", wb > 1.2, f"{wb:.2f}")
check("2b [v11] descuenta la parcial A: A+B <= 1.5 s (+ un intento)", wa2 + wb2 <= 1.5 + 0.5 and wb2 < 1.0, f"{wa2 + wb2:.2f}")

# 3. checkpoint historico sin contadores: rechazados no negativos
def strip_counters(root):
    d = next(p for p in Path(root).iterdir() if p.is_dir())
    m = json.loads(sorted(d.glob('step_*.json'))[-1].read_text()); z = d / m['archive']
    with zipfile.ZipFile(z) as a: b = cloudpickle.loads(a.read('integration.pkl'))
    for k in ('attempts', 'alarm_count', 'extra_used', 'counters_from_zero', 'last_reason', 'n_start', 'alarm_log'): b.pop(k, None)
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as a: a.writestr('integration.pkl', cloudpickle.dumps(b))
    m['sha256'] = hashlib.sha256(z.read_bytes()).hexdigest(); (d / f"step_{m['steps']:08d}.json").write_text(json.dumps(m))
    return m['steps']
def legacy_case(R):
    with tempfile.TemporaryDirectory() as td:
        f = slow(40.0, 0.0)
        try: R.Driver(td, 'toy3', max_new_steps=60, attempt_cap=10**6, time_cap_s=1e9)(f, *ARGS)
        except R.IntegrationPaused: pass
        n0 = strip_counters(td)
        try: R.Driver(td, 'toy3', max_new_steps=30, attempt_cap=10**6, time_cap_s=1e9)(f, *ARGS)
        except R.IntegrationPaused: pass
        m = last_meta(td)[-1]
        return n0, m
n0, mo = legacy_case(Rold); n1, mn = legacy_case(Rnew)
print(f"   (vigente) pasos historicos={n0}, aceptados={mo['steps']}, intentos={mo['attempts']}, rechazados={mo['rejected']} ; (v11) rechazados={mn['rejected']}, instrumentado desde el paso {mn.get('instrumented_from_step')}")
check("3a [vigente] rechazados NEGATIVO con historial sin contadores (defecto reproducido)", mo['rejected'] < 0, f"{mo['rejected']}")
check("3b [v11] rechazados >= 0 y registra el paso desde el que se instrumento",
      mn['rejected'] >= 0 and mn.get('instrumented_from_step') == n1 and mn['attempts'] - mn['rejected'] == mn['steps'] - n1, f"{mn['rejected']}")
print("\nRESULTADO:", "PASS (el vigente reproduce los 3 defectos; el candidato v11 los corrige)" if ok else "FAIL")
sys.exit(0 if ok else 1)
