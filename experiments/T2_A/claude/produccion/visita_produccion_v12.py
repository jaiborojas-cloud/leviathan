"""visita_produccion_v12.py - EJECUTOR DE PRODUCCION (candidato, no vigente hasta validarse y registrar su hash).
Unico cambio respecto a visita_completa_instrumentada_v11_t4p.py (congelado, SHA-256 b7352b23...ceee): admite --step en
{25, 50, ..., 250}. El modelo del update k se obtiene entrenando k-5 updates desde checkpoint_005.pt (mismo new_session,
updates y save_checkpoint, mismo RNG restaurado). Con k = 25 el camino es identico al del script congelado. La geometria,
la calibracion (v1.0 y recuperacion T4'), los topes T1/T2 y las auditorias no cambian. --solo-entrenamiento escribe el
checkpoint y state.npz y termina (validacion barata). Texto original del script congelado a continuacion.
CANDIDATO v1.1 (no vigente) de visita_completa_instrumentada.py: driver v11 (contabilidad corregida) + T4' (D5): si la calibracion v1.0 (bg.calibrate, cota 0.09)
queda PAUSADA, se recupera con t4prima.calibrate_t4prima (parada por area; misma raiz A=0.02) y la visita continua; el camino sin pausa es identico a v11.
--forzar-t4prima (SOLO validacion): salta bg.calibrate y usa T4' directamente, para comprobar que la visita completa da el mismo resultado por esa via.
visita_completa_instrumentada.py - UNA visita de update 25 completa (entrenar, calibrar, auditar, clasificar) con los topes,
la alarma y la revision obligatoria del ANEXO_OPERATIVO_E1_v1.0_CONGELADO en TODAS las integraciones DOP853 de rayos y de
campos de Jacobi (geometry.solve_ivp y audit.solve_ivp).

Replica followup.one_visit (entrega de solo lectura) sin tocar los fuentes originales: mismo entrenamiento desde
checkpoint_005.pt (20 updates), mismo estado, mismas llamadas bg.calibrate y topological_map.result. Diferencias, y solo estas:
  * en vez del gate de predictores bloqueados (que depende de archivos de la corrida original), verifica que existan y coincidan
    el checkpoint basal y (si se encuentra) su SHA-256 del manifiesto de cohorte;
  * toda integracion pasa por un Driver instrumentado (rays: work/ode_checkpoints/rays; Jacobi: .../jacobi); si una llamada no
    cumple las precondiciones del Driver (p. ej. dense_output False) se ejecuta con scipy sin instrumentar y se REGISTRA en
    'sin_cubrir' del resultado (no se oculta);
  * el tope de VISITA (900 s) suma el tiempo de TODAS las integraciones terminadas de ambos drivers;
  * si hay pausa: escribe REVISION_PENDIENTE.json (PAUSED_PENDING_REVIEW, sin clasificacion ni Y) y termina; el reinicio con
    el mismo --work retoma desde los checkpoints y las tareas ya hechas.
NO clasifica salvo lo que ya hace topological_map.result. NO usa --extra-budget por si solo: solo con la bandera, tras decision
registrada del responsable.

Uso (PowerShell; validacion sobre j6, caso cerrado, carpeta de trabajo nueva):
  & "...\\venv_torch\\Scripts\\python.exe" -I "...\\visita_completa_instrumentada.py" --case split8_j6_true --work "D:\\RIPG_DATA\\T2_A\\expediente\\visita_j6_validacion"
"""
import os
for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_k] = "1"
import argparse, csv, hashlib, json, platform, shutil, sys, time, traceback
from pathlib import Path
import numpy as np, scipy
from scipy.integrate import solve_ivp as scipy_solve_ivp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import resumable_dop853_instrumentado_v11 as R
import t4prima

GEOM_SHA = "b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
ROOTS = []            # raices de checkpoints de ambos drivers (para el tope de visita)
SIN_CUBRIR = []       # llamadas que no cumplen las precondiciones del Driver
LAST = {}             # ultima integracion lanzada (para el registro de pausa)


class StageDriver(R.Driver):
    """v1.1 candidato: el tope de visita lo aplica el Driver (una sola vez, contra TODAS las demas integraciones, terminadas o parciales)."""
    def __init__(self, kind, *a, **kw):
        super().__init__(*a, **kw); self.kind = kind

    def __call__(self, fun, t_span, y0, method, rtol, atol, dense_output):
        ok = (method == "DOP853" and dense_output and t_span[0] == 0 and rtol == 2e-10 and atol == 2e-12)
        if not ok:
            SIN_CUBRIR.append(dict(kind=self.kind, method=method, t_span=list(t_span), rtol=rtol, atol=atol, dense=bool(dense_output)))
            return scipy_solve_ivp(fun, t_span, y0, method=method, rtol=rtol, atol=atol, dense_output=dense_output)
        LAST.update(kind=self.kind, t_end=float(t_span[1]), n_state=int(len(y0)))
        return super().__call__(fun, t_span, y0, method, rtol, atol, dense_output)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--step", type=int, default=25, choices=[25, 50, 75, 100, 125, 150, 175, 200, 225, 250])
    ap.add_argument("--solo-entrenamiento", action="store_true", help="v12: solo checkpoint y state.npz (validacion); no calibra ni audita")
    ap.add_argument("--root", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
    ap.add_argument("--instrument", default=None, help="carpeta con audit.py, topological_map.py (por defecto root/sources/instrument)")
    ap.add_argument("--mocks", default=r"D:\RIPG_DATA\T2_A\cribado_borde\margen\mocks")
    ap.add_argument("--extra-budget", action="store_true", help="SOLO tras decision registrada del responsable")
    ap.add_argument("--time-cap", type=float, default=120.0)
    ap.add_argument("--attempt-cap", type=int, default=250)
    ap.add_argument("--visit-cap", type=float, default=900.0, help="T2: tope de visita hasta que entre a la etapa de refinamiento")
    ap.add_argument("--visit-cap-refinamiento", type=float, default=3600.0, help="T2: tope de visita desde que entra a refinamiento (no baja el tope si --visit-cap es mayor)")
    ap.add_argument("--forzar-t4prima", action="store_true", help="SOLO validacion: calibra con T4' sin intentar bg.calibrate")
    ap.add_argument("--prueba-sin-torch", default=None, help="SOLO pruebas del contenedor: npz de estado; checkpoint ficticio")
    a = ap.parse_args()
    assert a.step % 25 == 0 and 25 <= a.step <= 250, "update programado invalido"
    root = Path(a.root); work = Path(a.work); work.mkdir(parents=True, exist_ok=True)
    src = root / "sources"; ins = Path(a.instrument) if a.instrument else src / "instrument"
    for p in (str(ins), a.mocks, str(src)):      # insert(0): sources queda primero
        sys.path.insert(0, p)
    if sha(src / "geometry.py") != GEOM_SHA:
        sys.exit("ABORTA: geometry.py no coincide con b4d1e0e4...")
    import geometry, baseline_geometry as bg, audit, topological_map
    case = a.case; s_, j_, _ = case.split("_"); S, J = int(s_[5:]), int(j_[1:])
    d = work / "states" / case; d.mkdir(parents=True, exist_ok=True)
    t0, c0 = time.perf_counter(), time.process_time()

    # --- entrenamiento y estado (como one_visit) ---
    if a.prueba_sin_torch:
        if not (d / "state.npz").exists():
            shutil.copyfile(a.prueba_sin_torch, d / "state.npz")
        if not (d / "checkpoint.pt").exists():
            (d / "checkpoint.pt").write_bytes(b"STUB-PRUEBA-SIN-TORCH")
    else:
        import torch, core
        from training import new_session, updates, save_checkpoint
        before = root / "trajectories" / case / "checkpoint_005.pt"
        assert before.exists(), before
        for cand in (root / "records" / "cohort_manifest.csv", root / "cohort_manifest.csv"):
            if cand.exists():
                row = next(r for r in csv.DictReader(open(cand, encoding="utf-8")) if r["trajectory"] == case)
                assert sha(before) == row["checkpoint_sha256"], "checkpoint_005.pt no coincide con el manifiesto de cohorte"
                break
        X, y, Xv, yv, m, opt, rng = new_session(S, J)
        c = torch.load(before, weights_only=False); assert c["step"] == 5 and c["split"] == S and c["init"] == J
        m.load_state_dict(c["model"]); opt.load_state_dict(c["optimizer"])
        rng.bit_generator.state = c["numpy_rng"]; torch.set_rng_state(c["torch_rng"])
        if not (d / "checkpoint.pt").exists():
            updates(m, opt, rng, X, y, a.step - 5); save_checkpoint(d / "checkpoint.pt", m, opt, rng, S, J, a.step)   # v12: k-5 updates desde el update 5
        else:
            c = torch.load(d / "checkpoint.pt", weights_only=False); assert c["step"] == a.step; m.load_state_dict(c["model"])
        if not (d / "state.npz").exists():
            Rb, Ub, f = core.make_geom_state(m, Xv, yv); M = core.subset_M(Rb, Ub, [0, 1, 2])
            np.savez_compressed(d / "state.npz", M=M.detach().numpy(), f=f.detach().numpy())

    if a.solo_entrenamiento:   # v12: validacion barata del entrenamiento
        rec = dict(case=case, step=a.step, checkpoint_sha256=sha(d / "checkpoint.pt"), field_sha256=sha(d / "state.npz"),
                   wall_seconds=time.perf_counter() - t0, environment=dict(python=platform.python_version(), numpy=np.__version__, platform=platform.platform()))
        (work / "ENTRENAMIENTO.json").write_text(json.dumps(rec, indent=2)); print(json.dumps(rec, indent=2)); return

    # --- montaje identico a one_visit ---
    bg.ROOT = work; bg.audit.P = work; bg.topological_map.P = work
    bg.saved(d / "reconstruction.json", dict(passed=True, method="exact checkpoint/core; no surrogate"))
    identity = sha(d / "state.npz")
    for kind in ("rays", "jacobi", "rays_t4p"):
        ROOTS.append(work / "ode_checkpoints" / kind)
        ROOTS[-1].mkdir(parents=True, exist_ok=True)
    kw = dict(max_new_steps=128, every=32, attempt_cap=a.attempt_cap, time_cap_s=a.time_cap, extra_budget=a.extra_budget, visit_cap_s=a.visit_cap, roots=ROOTS)
    rays = StageDriver("rays", ROOTS[0], identity, **kw); jac = StageDriver("jacobi", ROOTS[1], identity, **kw)
    modo_calibracion, pausa_v10 = "V1.0", None
    old_g, old_a = geometry.solve_ivp, audit.solve_ivp
    geometry.solve_ivp, audit.solve_ivp = rays, jac
    # T2 (anexo v1.1): el tope de visita sube a --visit-cap-refinamiento cuando la visita ENTRA a la etapa de refinamiento. 'Entrar' = la primera llamada de
    # topological_map.result a una tarea de refinamiento (boundary n>=2048, jacobi n>=1024, rk4), que solo ocurre si su propia condicion `candidate` es verdadera.
    # No se reimplementa `candidate`: se observa cuando topological_map lo usa.
    REFINE = dict(entrada=None)
    def _entrar(kind, n):
        if REFINE["entrada"] is None:
            REFINE["entrada"] = f"{kind} n={n}"
            for dr in (rays, jac):
                dr.visit_cap_s = max(dr.visit_cap_s, a.visit_cap_refinamiento)
            print(f"T2: la visita entra a refinamiento ({REFINE['entrada']}); tope de visita {rays.visit_cap_s:g} s", flush=True)
    _ob, _oj, _or = topological_map.boundary, topological_map.jacobi, topological_map.rk
    topological_map.boundary = lambda case, n, ph: (_entrar("boundary", n) if n >= 2048 else None, _ob(case, n, ph))[1]
    topological_map.jacobi = lambda case, n, ph: (_entrar("jacobi", n) if n >= 1024 else None, _oj(case, n, ph))[1]
    topological_map.rk = lambda case, steps, ph: (_entrar("rk4", steps), _or(case, steps, ph))[1]
    status, reason, out = "VISIT_EVALUATED", None, {}
    try:
        try:
            if a.forzar_t4prima:
                raise R.IntegrationPaused("calibracion forzada a T4' (validacion)", "FORZADO_VALIDACION")
            nominal = bg.calibrate(case)
        except R.IntegrationPaused as e:                      # recuperacion T4' (D5): la pausa v1.0 se conserva registrada
            pausa_v10 = getattr(e, "reason", "PAUSED_STEP_BUDGET"); modo_calibracion = "T4_PRIME_AREA_STOP"
            print(f"calibracion v1.0 pausada ({pausa_v10}); se recupera con T4' (parada por area)", flush=True)
            kw4 = dict(kw)
            mk = lambda every, cb: R.Driver(ROOTS[2], identity, max_new_steps=10**6, every=every, on_commit=cb, attempt_cap=a.attempt_cap,
                                            time_cap_s=a.time_cap, extra_budget=a.extra_budget, visit_cap_s=a.visit_cap, roots=ROOTS)
            nominal = t4prima.calibrate_t4prima(bg.field(d / "state.npz"), 2048, d, mk, bg.area7, bg.triangles, bg.saved)
        top = topological_map.result(case)
        out = dict(trajectory=case, step=a.step, classification=top["classification"], checkpoint_sha256=sha(d / "checkpoint.pt"),
                   field_sha256=sha(d / "state.npz"), nominal_radius=nominal["radius"], r_conj=top.get("r_conj"), A_embed=top.get("A_embed"),
                   status="VISIT_EVALUATED", calibration_mode=modo_calibracion, calibration_v10_pause=pausa_v10)
        if top.get("errors"):
            out["errors_en_result"] = top["errors"][-600:]
    except R.IntegrationPaused as e:
        status, reason = "PAUSED_PENDING_REVIEW", getattr(e, "reason", "PAUSED_STEP_BUDGET")
    except Exception:
        status, reason = "ERROR_DE_EJECUCION", traceback.format_exc()[-800:]
    finally:
        geometry.solve_ivp, audit.solve_ivp = old_g, old_a
        topological_map.boundary, topological_map.jacobi, topological_map.rk = _ob, _oj, _or
    metas = []
    for rt in ROOTS:
        for p in sorted(Path(rt).rglob("step_*.json")):
            metas.append(json.loads(p.read_text()))
    # ultimo checkpoint de cada integracion
    last_by_dir = {}
    for rt in ROOTS:
        for dd in Path(rt).iterdir():
            ms = sorted(dd.glob("step_*.json"))
            if ms:
                last_by_dir[f"{Path(rt).name}/{dd.name}"] = json.loads(ms[-1].read_text())
    resumen = dict(integraciones=len(last_by_dir), intentos_total=sum(m.get("attempts", 0) for m in last_by_dir.values()),
                   rechazos_total=sum(m.get("rejected", 0) for m in last_by_dir.values()),
                   max_alarma=max([m.get("alarm_count", 0) for m in last_by_dir.values()] or [0]),
                   pausadas=[k for k, m in last_by_dir.items() if m.get("status") != "finished" and not k.startswith("rays_t4p/")],
                   detenidas_por_area_t4p=[k for k in last_by_dir if k.startswith("rays_t4p/")])
    rec = dict(case=case, status=status, reason=reason, extra_budget=a.extra_budget, caps=dict(attempts=a.attempt_cap, time_s=a.time_cap, visit_s=a.visit_cap, visit_s_refinamiento=a.visit_cap_refinamiento, entro_a_refinamiento=REFINE["entrada"]),
               wall_seconds_session=time.perf_counter() - t0, cpu_seconds_session=time.process_time() - c0,
               instrumentacion=resumen, sin_cubrir=SIN_CUBRIR, ultima_integracion_lanzada=LAST,
               environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__, platform=platform.platform(),
                                processor=platform.processor(), cpus=os.cpu_count()),
               resultado_visita=out,
               note="Si el estado es PAUSED_PENDING_REVIEW: pausa operacional, no es FAIL, ni INCONCLUSIVE, ni evidencia topologica. Sin clasificacion ni outcome.")
    name = {"VISIT_EVALUATED": "VISITA_COMPLETA.json", "PAUSED_PENDING_REVIEW": "REVISION_PENDIENTE.json"}.get(status, "ERROR_EJECUCION.json")
    (work / name).write_text(json.dumps(rec, indent=2, default=str))
    print(json.dumps(rec, indent=2, default=str))


if __name__ == "__main__":
    main()
