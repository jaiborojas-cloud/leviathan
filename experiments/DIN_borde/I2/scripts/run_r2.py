"""Ejecución inmutable I2: controles →302 casos; conserva todos los fallos."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import datetime
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback
import warnings
import numpy as np
import scipy
import mpmath

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rho_borde_v2 import rho_borde_v2, _Instrument, geometry_class
from common_v1 import (ROOT, STAGE, CFG, ARRAYS, RUN, GEOM, V1, cases, clean,
                       write, guard, code_guard, v1_module, array, sha)
from references_v2 import exact_triangle, mp_ray
import common_v1
RUN = STAGE/'results/run_r2'
ARRAYS = Path('/workspace/work/din-i2-r2-arrays')
common_v1.ARRAYS = ARRAYS


def controls():
    f = np.array([[0., 0.], [1., 0.], [0., 1.]])
    M = np.eye(3)
    base = rho_borde_v2(M, f)
    inst = _Instrument(M, f)
    k, edge = 0, inst.edges[-1]
    normal = inst.ray(edge['gaps'], validate=True)
    tail = inst.ray(inst.edges[0]['gaps'], active=edge['support'], validate=True)
    boundary = []
    for t in [1e-2, 1e-4, 1e-6, 1e-8]:
        rr = inst.validated_vertex(k, t)
        boundary.append(dict(t=t, length=rr['length']))
    outside = next(j for j in range(3) if j not in inst.original_indices(edge['support']))
    coord = np.zeros((3, 3)); coord[outside, outside] = 1
    ci = _Instrument(coord, f)
    nojump = ci.ray(ci.edges[0]['gaps'], active=ci.edges[-1]['support'], validate=True)
    constant = rho_borde_v2(np.ones((3, 3))/3, f)
    scaled = rho_borde_v2(4*M, f)
    changed = rho_borde_v2(M, f@np.array([[2., .5], [0., 1.]])+np.array([.25, -.5]))
    rejects = {}
    for name, mm, ff in [('indefinite', np.diag([1., 1., -1.]), f),
                         ('rank1_f', M, np.array([[0., 0.], [1., 0.], [2., 0.]]))]:
        try:
            rho_borde_v2(mm, ff)
            rejects[name] = 'NOT_REJECTED'
        except ValueError as e:
            rejects[name] = str(e)
    checks = dict(triangle_vert=abs(base['rho_vert']-np.sqrt(2/3)) < 2e-5,
                  triangle_faces=abs(base['rho_caras']-np.sqrt(1/6)) < 2e-5,
                  tail_jump=abs(tail['length']-np.sqrt(.5)) < 2e-7,
                  boundary_limit=abs(boundary[-1]['length']-normal['length']-tail['length']) < 2e-5,
                  zero_jump=nojump['length'] < 2e-7,
                  zero_metric=constant['rho_caras'] == 0 and constant['rho_vert'] == 0,
                  homogeneity=abs(scaled['rho_caras']-2*base['rho_caras']) < 2e-7,
                  affine=abs(changed['rho_caras']-base['rho_caras']) < 2e-7 and abs(changed['rho_vert']-base['rho_vert']) < 2e-5,
                  reject_indefinite=rejects['indefinite'] == 'M_NOT_PSD',
                  reject_rank=rejects['rank1_f'] == 'AFFINE_RANK_LESS_THAN_TWO')
    return dict(status='PASS' if all(checks.values()) else 'FAIL', checks=checks, base=base,
                normal=normal, tail=tail, boundary=boundary, nojump=nojump, constant=constant,
                scaled=scaled, affine=changed, rejects=rejects)


def contemporary_v1(c):
    start = time.perf_counter()
    try:
        module = v1_module()
        g = geometry_class()(c['M'], c['f'])
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('always')
            raw = module.rho_borde(g, ndir=1440, orden=800)
        return dict(status='RETURNED', raw=raw, seconds=time.perf_counter()-start,
                    warnings=[dict(category=w.category.__name__, message=str(w.message)) for w in ws])
    except Exception as e:
        return dict(status='FAILED', exception=repr(e), traceback=traceback.format_exc(),
                    seconds=time.perf_counter()-start)


def measure(item):
    number, c = item
    guard()
    start = time.perf_counter()
    name = f'{number:03d}'
    out = dict(number=number, id=c['id'], group=c['group'], input={k: v for k, v in c.items() if k not in ['M', 'f']})
    out['arrays'] = array(name, M=c['M'], f=c['f'])
    for label, options in [('v2', {}), ('sensitivity', dict(grid=17, starts=6, maxiter=64,
                    margin=1e-12, order=24, log_step=2.))]:
        if label == 'sensitivity' and not c['sensitivity']:
            continue
        try:
            out[label] = rho_borde_v2(c['M'], c['f'], **options)
        except Exception as e:
            out[label] = dict(status='FAILED', exception=repr(e), traceback=traceback.format_exc())
    if c['fresh_v1']:
        previous = json.loads((STAGE/'results/run_v1/states'/f'{number:03d}.json').read_text())
        out['fresh_v1'] = previous['fresh_v1']
        out['fresh_v1_reused_from'] = 'run_v1; misma sesión, CPU, workers y BLAS1'
    if c['group'] == 'AG_triangle':
        try:
            out['triangle_reference'] = exact_triangle(c['M'], c['f'])
        except Exception as e:
            out['triangle_reference'] = dict(status='FAILED', exception=repr(e), traceback=traceback.format_exc())
    if c['MP_ray'] and out['v2'].get('rho_caras') is not None:
        try:
            out['MP_reference'] = mp_ray(c['M'], c['f'], out['v2']['rho_caras_winner'])
        except Exception as e:
            out['MP_reference'] = dict(status='FAILED', exception=repr(e), traceback=traceback.format_exc())
    out['wall_seconds'] = time.perf_counter()-start
    write(RUN/'states'/f'{name}.json', out)
    return dict(number=number, id=c['id'], status=out['v2']['status'],
                rho_caras=out['v2'].get('rho_caras'), seconds=out['wall_seconds'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--part', choices=['controls', 'cohort'], required=True)
    args = parser.parse_args()
    code_guard()
    guard()
    if args.part == 'controls':
        RUN.mkdir(parents=True, exist_ok=False)
        (RUN/'states').mkdir()
        ARRAYS.mkdir(parents=True, exist_ok=False)
        write(RUN/'environment.json', dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
               python=sys.version, platform=platform.platform(), numpy=np.__version__, scipy=scipy.__version__,
               mpmath=mpmath.__version__, pid=os.getpid(), workers=CFG['workers'],
               commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
               env={k: os.environ.get(k) for k in ['OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'PYTHONDONTWRITEBYTECODE']}))
        result = controls()
        write(RUN/'controls.json', result)
        print(json.dumps(clean(dict(status=result['status'], checks=result['checks']))), flush=True)
    else:
        if not (RUN/'controls.json').exists():
            raise RuntimeError('Controles primero')
        inputs = cases()
        write(RUN/'cohort_inventory.json', [{k: v for k, v in c.items() if k not in ['M', 'f']} for c in inputs])
        start = time.perf_counter()
        completed = []
        with ProcessPoolExecutor(max_workers=CFG['workers']) as pool:
            jobs = [pool.submit(measure, pair) for pair in enumerate(inputs)]
            for job in as_completed(jobs):
                try:
                    info = job.result()
                except Exception as e:
                    info = dict(status='WORKER_FAILED', exception=repr(e), traceback=traceback.format_exc())
                completed.append(info)
                print(json.dumps(clean(dict(done=len(completed), total=len(inputs), **info))), flush=True)
                if time.perf_counter()-start > CFG['total_budget_seconds']:
                    for pending in jobs:
                        pending.cancel()
                    print('TOTAL_BUDGET_EXHAUSTED; se conservan tareas ya en curso', flush=True)
                    break
        write(RUN/'execution.json', dict(completed=completed, seconds=time.perf_counter()-start,
                 all_count=len(inputs), over_budget=time.perf_counter()-start > CFG['total_budget_seconds']))


if __name__ == '__main__':
    main()
