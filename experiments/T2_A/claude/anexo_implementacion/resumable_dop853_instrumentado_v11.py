"""CANDIDATO v1.1 (no vigente; no sustituye al driver usado en el piloto) - correcciones de contabilidad, 2026-10-20:
  (a) el tope de VISITA se aplica aqui, UNA sola vez, contra el tiempo consumido por TODAS las demas integraciones (terminadas o parciales);
      con extra_budget el tope de visita y el de integracion se duplican una vez cada uno y se toma el minimo (antes se duplicaba dos veces);
  (b) rechazados = intentos - (aceptados desde que se instrumento): ya no puede ser negativo al importar checkpoints historicos
      (n_start = pasos aceptados al empezar a contar; el historial anterior queda como DESCONOCIDO, no como cero rechazos).
Driver DOP853 reanudable e INSTRUMENTADO segun el ANEXO_OPERATIVO_E1_v1.0_CONGELADO.

Es una copia modificada de sources/resumable_dop853.py (entrega de solo lectura); el original NO se toca.
Cambios, y solo estos (la aritmetica del solver no cambia: mismos DOP853, rtol, atol, dense_output):
  1. Cuenta INTENTOS de paso (cada llamada a scipy.integrate._ivp.rk.rk_step), aceptados y rechazados.
  2. Tope de intentos por integracion (anexo 3, disparador 1: 250; +250 con presupuesto adicional) y tope de
     tiempo de pared por integracion (disparador 2: 120 s float64; +120 s), ambos evaluados ANTES de cada intento.
  3. Alarma de progreso radial (disparador 3): dr = t_n - t_{n-1} de pasos ACEPTADOS; dispara con dr < 1e-4 durante
     8 pasos aceptados consecutivos; se excluye el paso final recortado; el contador se guarda en el checkpoint.
  4. Todo disparo guarda checkpoint y lanza IntegrationPaused con .reason (PAUSED_LOW_RADIAL_PROGRESS,
     PAUSED_ATTEMPT_CAP, PAUSED_TIME_CAP, o el antiguo tope de pasos aceptados). Estado de la visita: PAUSED_PENDING_REVIEW.
     Una pausa no es FAIL, ni INCONCLUSIVE, ni evidencia topologica.
  5. extra_budget=True (SOLO tras decision registrada del responsable): +128 pasos aceptados, +250 intentos, +120 s,
     sumados a lo acumulado (los contadores NO se reinician); la alarma de progreso se REGISTRA en cada paso sin pausar.
     Se guarda en el checkpoint; no puede usarse dos veces por integracion.
Limitaciones declaradas: (a) el tope de 900 s por VISITA no se aplica aqui (este driver es por integracion): lo
aplica el llamador; (b) un tope disparado a mitad de solver.step() descarta el tamano de paso reducido de ese paso en
curso (el estado aceptado es exacto); al reanudar se repiten los rechazos y se cuentan; (c) checkpoints anteriores
sin contadores se reanudan con contadores en 0 (se registra 'counters_from_zero'); (d) los umbrales valen para
rtol 2e-10 / atol 2e-12 y float64; para MPFR el tiempo debe ser 3600 s (parametro time_cap_s).
"""
from pathlib import Path
import hashlib, json, os, time, zipfile
import numpy as np, cloudpickle
import scipy.integrate._ivp.rk as rkmod
from scipy.integrate import DOP853, OdeSolution
from scipy.integrate._ivp.ivp import OdeResult


class IntegrationPaused(BaseException):
    def __init__(self, msg, reason="PAUSED_STEP_BUDGET"):
        super().__init__(msg)
        self.reason = reason


class _Stop(Exception):
    def __init__(self, reason):
        self.reason = reason


ALARM_DR, ALARM_N = 1e-4, 8


class Driver:
    def __init__(self, root, identity, max_new_steps=128, every=32, on_commit=None,
                 attempt_cap=250, time_cap_s=120.0, extra_budget=False, visit_cap_s=None, roots=None):
        self.root = Path(root); self.root.mkdir(parents=True, exist_ok=True)
        self.identity = identity; self.limit = max_new_steps; self.every = every; self.on_commit = on_commit
        self.attempt_cap, self.time_cap_s, self.extra_budget = attempt_cap, time_cap_s, extra_budget
        self.visit_cap_s, self.roots = visit_cap_s, roots   # roots: lista de raices de checkpoints de la visita (todas las etapas)

    def __call__(self, fun, t_span, y0, method, rtol, atol, dense_output):
        assert method == 'DOP853' and dense_output and t_span[0] == 0 and rtol == 2e-10 and atol == 2e-12
        signature = dict(identity=self.identity, t_span=list(t_span),
                         y0_sha256=hashlib.sha256(np.asarray(y0).tobytes()).hexdigest(),
                         method=method, rtol=rtol, atol=atol, dense_output=True)
        key = hashlib.sha256(json.dumps(signature, sort_keys=True).encode()).hexdigest()[:20]
        d = self.root / key; d.mkdir(exist_ok=True)
        metas = sorted(d.glob('step_*.json'))
        if metas:
            m = json.loads(metas[-1].read_text()); z = d / m['archive']
            assert hashlib.sha256(z.read_bytes()).hexdigest() == m['sha256']
            with zipfile.ZipFile(z) as a:
                b = cloudpickle.loads(a.read('integration.pkl'))
            assert b['signature'] == signature
            solver = b['solver']; assert np.array_equal(solver.K, solver.K_extended[:solver.n_stages + 1])
            solver.K = solver.K_extended[:solver.n_stages + 1]
        else:
            solver = DOP853(fun, t_span[0], y0, t_span[1], rtol=rtol, atol=atol)
            b = dict(signature=signature, solver=solver, ts=[t_span[0]], ys=[np.asarray(y0).copy()],
                     interpolants=[], cpu_seconds=0., wall_seconds=0.)
        # contadores del anexo (persistentes)
        if 'attempts' not in b:
            b.update(attempts=0, alarm_count=0, extra_used=False, counters_from_zero=bool(metas), last_reason=None,
                 n_start=len(b['interpolants']))
        if self.extra_budget and solver.status == 'running':
            # Una integracion ya TERMINADA que se vuelve a pedir (misma firma) se devuelve tal cual, tambien con el flag.
            assert not b['extra_used'], "presupuesto adicional ya usado en esta integracion"
            b['extra_used'] = True; b['extra_since_attempts'] = b['attempts']
            b['extra_since_steps'] = len(b['interpolants']); b['extra_since_wall'] = b['wall_seconds']
        extra = b['extra_used']
        att_cap = self.attempt_cap * (2 if extra else 1)
        n_start = b.setdefault('n_start', 0)
        # T1 (anexo v1.1): tope por integracion = max(time_cap_s, 0.04 s x n_rays); n_rays = len(y0)/4 (estado [p, v] de 2 coordenadas cada uno).
        # En integraciones con pocos rayos (p. ej. jacobi) no cambia el tope; solo lo sube en integraciones de muchos rayos.
        n_rays = np.asarray(y0).size // 4
        wall_cap = max(self.time_cap_s, 0.04 * n_rays) * (2 if extra else 1)
        if self.visit_cap_s is not None:
            others = 0.0                       # tiempo ya consumido por las DEMAS integraciones de la visita (terminadas o parciales)
            for root in (self.roots or []):
                for dd in Path(root).iterdir():
                    if dd.is_dir() and dd.resolve() != d.resolve():
                        ms = sorted(dd.glob('step_*.json'))
                        if ms:
                            others += float(json.loads(ms[-1].read_text())['wall_seconds'])
            wall_cap = min(wall_cap, max(self.visit_cap_s * (2 if extra else 1) - others, 0.0))
        solver = b['solver']; start_steps = len(b['interpolants']); start = time.perf_counter()
        cpu = time.process_time(); last_saved = start_steps
        alarm_log = b.setdefault('alarm_log', [])

        def wall_total():
            return b['wall_seconds'] + (time.perf_counter() - start)

        def commit():
            nonlocal start, cpu, last_saved
            b['cpu_seconds'] += time.process_time() - cpu; b['wall_seconds'] += time.perf_counter() - start
            n = len(b['interpolants']); name = f'step_{n:08d}.zip'; z = d / name; tmp = z.with_suffix('.tmp')
            with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as a:
                a.writestr('integration.pkl', cloudpickle.dumps(b))
            os.replace(tmp, z)
            m = dict(archive=name, sha256=hashlib.sha256(z.read_bytes()).hexdigest(), steps=n, t=float(solver.t),
                     target=float(solver.t_bound), nfev=solver.nfev, status=solver.status,
                     cpu_seconds=b['cpu_seconds'], wall_seconds=b['wall_seconds'], signature=signature,
                     attempts=b['attempts'], rejected=b['attempts'] - (n - n_start), instrumented_from_step=n_start, alarm_count=b['alarm_count'],
                     extra_used=b['extra_used'], last_reason=b['last_reason'],
                     counters_from_zero=b['counters_from_zero'])
            (d / f'step_{n:08d}.json').write_text(json.dumps(m, indent=2))
            if self.on_commit:
                self.on_commit(z, d / f'step_{n:08d}.json', m)
            print('ODE_CHECKPOINT', n, solver.t, solver.nfev, solver.status, 'intentos', b['attempts'], flush=True)
            last_saved = n; start = time.perf_counter(); cpu = time.process_time()

        orig = rkmod.rk_step

        def counted(fun_, t, y, f_, h, A, B, C, K):
            if b['attempts'] >= att_cap:
                raise _Stop('PAUSED_ATTEMPT_CAP')
            if wall_total() > wall_cap:
                raise _Stop('PAUSED_TIME_CAP')
            b['attempts'] += 1
            return orig(fun_, t, y, f_, h, A, B, C, K)

        rkmod.rk_step = counted
        try:
            while solver.status == 'running':
                t_prev = float(solver.t)
                try:
                    message = solver.step()
                except _Stop as s:
                    b['last_reason'] = s.reason; commit()
                    raise IntegrationPaused(f'{s.reason}: exact accepted state persisted; not a numerical or geometric failure; '
                                            f'attempts={b["attempts"]}', s.reason)
                if solver.status == 'failed':
                    commit(); raise RuntimeError(message)
                interpolant = solver.dense_output()
                b['interpolants'].append(interpolant); b['ts'].append(solver.t); b['ys'].append(solver.y.copy())
                n = len(b['interpolants'])
                # alarma de progreso radial: solo pasos aceptados; se excluye el paso final recortado
                if solver.status == 'running':
                    dr = float(solver.t) - t_prev
                    b['alarm_count'] = b['alarm_count'] + 1 if dr < ALARM_DR else 0
                    if b['alarm_count'] >= ALARM_N:
                        if extra:
                            alarm_log.append((n, float(solver.t), dr, b['alarm_count']))
                        else:
                            b['last_reason'] = 'PAUSED_LOW_RADIAL_PROGRESS'; commit()
                            raise IntegrationPaused(f'PAUSED_LOW_RADIAL_PROGRESS at step {n}, t={solver.t!r}', 'PAUSED_LOW_RADIAL_PROGRESS')
                if n % self.every == 0 or solver.status != 'running' or n - start_steps >= self.limit:
                    commit()
                if solver.status == 'running' and n - start_steps >= self.limit:
                    b['last_reason'] = 'PAUSED_STEP_BUDGET'
                    raise IntegrationPaused('Accepted-step budget reached; exact solver state persisted; not numerical or geometric failure')
        finally:
            rkmod.rk_step = orig
        if solver.status == 'failed':
            raise RuntimeError('Previously persisted integrator failure')
        return OdeResult(t=np.array(b['ts']), y=np.stack(b['ys'], axis=1), sol=OdeSolution(b['ts'], b['interpolants']),
                         t_events=None, y_events=None, nfev=solver.nfev, njev=solver.njev, nlu=solver.nlu, status=0,
                         message='The solver successfully reached the end of the integration interval.', success=True)
