"""sesion_visita_instrumentada.py - calibracion del radio nominal de UNA visita con el driver instrumentado del
ANEXO_OPERATIVO_E1_v1.0_CONGELADO (topes, alarma, presupuesto adicional, registro de revision).

Cubre SOLO las integraciones de rayos de la calibracion (geometry.solve_ivp, como en continue_first_pending_geometry.py).
NO cubre las integraciones de campos de Jacobi de audit.py ni el predictor: siguen con su solve_ivp original.
NO clasifica, NO asigna Y. Si pausa: escribe REVISION_PENDIENTE.json (estado PAUSED_PENDING_REVIEW) y termina.
Tope de VISITA (900 s float64): se aplica sumando el tiempo de pared guardado de las integraciones previas de la visita
y limitando cada integracion al restante; si se agota dispara como PAUSED_TIME_CAP.

Uso (PowerShell; ejemplo de validacion sobre j6, caso cerrado, en una carpeta de trabajo nueva):
  & "...\\venv_torch\\Scripts\\python.exe" -I "...\\sesion_visita_instrumentada.py" --case split8_j6_true ^
      --state "...\\margen\\state_025_regen_j6.npz" --work "D:\\RIPG_DATA\\T2_A\\expediente\\validacion_sesion_j6" [--extra-budget]
"""
import argparse, hashlib, json, os, platform, sys, time
from pathlib import Path
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1"); os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np, scipy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import resumable_dop853_instrumentado as R

VISIT_CAP_S = 900.0
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


class VisitDriver(R.Driver):
    """Driver con tope de tiempo por visita: resta el tiempo ya guardado en las demas integraciones de la visita."""
    def __call__(self, fun, t_span, y0, method, rtol, atol, dense_output):
        spent = 0.0
        for d in self.root.iterdir():
            if d.is_dir():
                metas = sorted(d.glob("step_*.json"))
                if metas:
                    m = json.loads(metas[-1].read_text())
                    if m.get("status") != "finished":
                        continue          # la integracion en curso se mide con su propio contador
                    spent += float(m["wall_seconds"])
        remaining = VISIT_CAP_S * (2 if self.extra_budget else 1) - spent
        self.time_cap_s_eff = min(self.time_cap_s, max(remaining, 0.0))
        saved, self.time_cap_s = self.time_cap_s, self.time_cap_s_eff
        try:
            return super().__call__(fun, t_span, y0, method, rtol, atol, dense_output)
        finally:
            self.time_cap_s = saved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--state", required=True, help="npz con M y f del estado de la visita")
    ap.add_argument("--work", required=True, help="carpeta de trabajo NUEVA (checkpoints, nominal.json, revision)")
    ap.add_argument("--sources", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto\sources")
    ap.add_argument("--mocks", default=r"D:\RIPG_DATA\T2_A\cribado_borde\margen\mocks")
    ap.add_argument("--extra-budget", action="store_true", help="SOLO tras decision registrada del responsable")
    ap.add_argument("--time-cap", type=float, default=120.0)
    ap.add_argument("--attempt-cap", type=int, default=250)
    a = ap.parse_args()
    work = Path(a.work); work.mkdir(parents=True, exist_ok=True)
    for p in (a.sources + r"\instrument", a.mocks, a.sources):   # insert(0): sources queda primero
        sys.path.insert(0, p)
    import geometry, baseline_geometry as bg
    with np.load(a.state) as z:
        M, f = z["M"], z["f"]
    # mismo montaje que margen/run_calibrate.py: geometria sin auditoria, sin escritura de persistencia
    case_dir = work / "states" / a.case; case_dir.mkdir(parents=True, exist_ok=True)
    np.savez(case_dir / "state.npz", M=M, f=f)
    bg.ROOT = work
    bg.field = lambda path: geometry.Geometry(M, f)
    bg.saved = lambda p, d: Path(p).write_text(json.dumps(d, indent=2))
    driver = VisitDriver(work / "ode_checkpoints", sha(case_dir / "state.npz"), max_new_steps=128, every=32,
                         attempt_cap=a.attempt_cap, time_cap_s=a.time_cap, extra_budget=a.extra_budget)
    old = geometry.solve_ivp; geometry.solve_ivp = driver
    t0 = time.perf_counter(); status, reason, result = "CALIBRATION_COMPLETE", None, None
    try:
        result = bg.calibrate(a.case)
    except R.IntegrationPaused as e:
        status, reason = "PAUSED_PENDING_REVIEW", getattr(e, "reason", "PAUSED_STEP_BUDGET")
    finally:
        geometry.solve_ivp = old
    metas = [json.loads(p.read_text()) for p in sorted((work / "ode_checkpoints").rglob("step_*.json"))]
    last = metas[-1] if metas else {}
    rec = dict(case=a.case, status=status, reason=reason, wall_seconds_session=time.perf_counter() - t0,
               extra_budget=a.extra_budget, attempt_cap=a.attempt_cap, time_cap_s=a.time_cap, visit_cap_s=VISIT_CAP_S,
               last_checkpoint=dict(archive=last.get("archive"), sha256=last.get("sha256"), t=last.get("t"),
                                    attempts=last.get("attempts"), rejected=last.get("rejected"),
                                    alarm_count=last.get("alarm_count")),
               environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                                platform=platform.platform(), processor=platform.processor(), cpus=os.cpu_count()),
               note="Si el estado es PAUSED_PENDING_REVIEW: pausa operacional, no es FAIL, ni INCONCLUSIVE, ni evidencia topologica. Sin clasificacion ni outcome.")
    if status != "CALIBRATION_COMPLETE":
        (work / "REVISION_PENDIENTE.json").write_text(json.dumps(rec, indent=2))
    else:
        rec["radius"] = result["radius"]; rec["area_degree5"] = result["area_degree5"]
        (work / "SESION_COMPLETA.json").write_text(json.dumps(rec, indent=2))
    print(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main()
