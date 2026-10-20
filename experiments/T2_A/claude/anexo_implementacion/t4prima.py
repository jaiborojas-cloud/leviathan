"""t4prima.py - T4' (D5, candidato v1.1): calibracion del radio nominal con parada por area, para usarse como RECUPERACION cuando bg.calibrate (v1.0, cota fija 0.09)
queda pausada. Misma logica que calibracion_incremental.py (validado: dif. de radio < 1.3e-14 en j6, j9, j17, en el contenedor y en el equipo del responsable),
empaquetada como funcion para la visita. No reduce el area nominal (0.02). Escribe nominal.json y boundary_calibration.npz con el mismo formato que bg.calibrate."""
import json, time, zipfile
from pathlib import Path
import numpy as np
from scipy.integrate import OdeSolution
from scipy.optimize import brentq
from shapely.geometry import Polygon


class EarlyStop(Exception):
    pass


class AreaNotReached(RuntimeError):
    pass


def _load(zpath):
    import cloudpickle
    with zipfile.ZipFile(zpath) as zf:
        return cloudpickle.loads(zf.read("integration.pkl"))


def calibrate_t4prima(g, n, d, make_driver, area7, triangles, saved, check_every=4, upper=0.09, log=print):
    """g: geometria (state.npz); d: carpeta del caso (states/<caso>); make_driver(every, on_commit) -> Driver ya configurado (raiz propia, topes, tope de visita).
    Devuelve el dict de nominal.json (tambien lo guarda)."""
    t0, c0 = time.perf_counter(), time.process_time()
    g0 = g.jet(np.zeros((1, 2)))[0][0]
    th = np.arange(n) * 2 * np.pi / n
    v0 = np.linalg.solve(np.linalg.cholesky(g0).T, np.array([np.cos(th), np.sin(th)])).T

    def rhs(t, y):
        p, v = y.reshape(2, n, 2)
        gam = g.jet(p)[4]
        return np.concatenate([v, -np.einsum('bkij,bi,bj->bk', gam, v, v)]).ravel()

    y0 = np.concatenate([np.zeros_like(v0), v0]).ravel()
    area_of = lambda sol, r: area7(g, triangles(sol(np.linspace(0, r, 33)).T.reshape(33, 2, n, 2)[:, 0]))

    def check(zpath, jpath, meta):
        b = _load(zpath)
        if len(b["interpolants"]) % check_every and meta["status"] == "running":
            return
        t = float(b["ts"][-1]); A = area_of(OdeSolution(b["ts"], b["interpolants"]), t)
        log(f"   T4' CHECK pasos={len(b['interpolants'])} t={t:.7f} area={A:.8f}")
        if A >= 0.02:
            raise EarlyStop()

    drv = make_driver(check_every, check)
    finished = False
    try:
        drv(rhs, (0.0, upper), y0, "DOP853", 2e-10, 2e-12, True)
        finished = True
    except EarlyStop:
        pass
    # IntegrationPaused (BaseException) se propaga al llamador: la visita queda PAUSED_PENDING_REVIEW
    root = Path(drv.root)
    meta = None
    for dd in sorted(root.iterdir()):
        ms = sorted(dd.glob("step_*.json"))
        if ms:
            meta = json.loads(ms[-1].read_text()); zp = dd / meta["archive"]
    b = _load(zp); sol = OdeSolution(b["ts"], b["interpolants"]); t_reach = float(b["ts"][-1]); A_reach = area_of(sol, t_reach)
    if A_reach < 0.02:
        raise AreaNotReached(f"T4': la integracion llego a t={t_reach} con area {A_reach} < 0.02 (finished={finished})")
    r = brentq(lambda x: area_of(sol, x) - 0.02, 0, t_reach, xtol=1e-13)
    a = area_of(sol, r); assert abs(a / 0.02 - 1) <= 1e-6
    border = sol(r).reshape(2, n, 2)[0]; poly = Polygon(border)
    np.savez_compressed(d / "boundary_calibration.npz", P=border, radius=r)
    result = dict(radius=r, area_degree5=a, area_relative_error=a / 0.02 - 1, polygon_valid=poly.is_valid, polygon_simple=poly.exterior.is_simple,
                  calibration_mode="T4_PRIME_AREA_STOP", t_reached=t_reach, area_at_t_reached=A_reach, steps=len(b["interpolants"]),
                  attempts=meta.get("attempts"), rejected=meta.get("rejected"), cpu_seconds=time.process_time() - c0, seconds=time.perf_counter() - t0)
    saved(d / "nominal.json", result)
    return result
