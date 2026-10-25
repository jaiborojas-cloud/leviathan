"""Orquestación independiente: fuentes fijadas, sólo escalares permitidos y sintéticos."""
import ast
import concurrent.futures as cf
import csv
import json
import math
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
import independent_v1 as ref
from support_v1 import ROOT, STAGE, CONFIG, ARRAYS, SOURCES, sha, write, arrays, guard, code_guard, discovery, input_csv

RUN = STAGE/'results/run_v1'
AUTHOR = ['X_igual_L', 'X_cubica_L', 'Y_g_L', 'X_constante', 'L_con_error', 'incremento_real', 'nulo_ruido']
SCENARIOS = ['ruido', 'incremento', 'heterosplit', 'n3', 'n4', 'outlier_L', 'empates_X',
             'escalon', 'log', 'sin', 'entre_splits', 'nulo_condicional']
BASE = None


def synthetic(kind, seed):
    rng = np.random.default_rng(seed)
    n = 3 if kind == 'n3' else (4 if kind == 'n4' else 5)
    sp = np.repeat(np.arange(168, 324), n)
    mu = rng.normal(scale=.7, size=156)
    L = np.repeat(mu, n)+rng.normal(size=len(sp))
    X = rng.normal(size=len(sp))
    err = rng.normal(size=len(sp))
    if kind == 'outlier_L':
        L[0] += 40*L.std()
    Y = .7*L-.2*L**2+.05*L**3+err
    if kind == 'incremento':
        T = rng.normal(size=len(sp))
        Y += T
        X = .3*T+np.sqrt(1-.3**2)*rng.normal(size=len(sp))
    elif kind == 'heterosplit':
        sig = np.repeat(np.exp(np.linspace(-2, 2, 156)), n)
        X *= sig
        Y = .7*L-.2*L**2+.05*L**3+sig*err
    elif kind == 'empates_X':
        X = -rng.binomial(1, .2, len(sp)).astype(float)
    elif kind == 'escalon':
        X = (L > 0).astype(float)
        Y = 2*X+.2*err
    elif kind == 'log':
        X = np.logaddexp(0, L)
        Y = 2*X+.05*err
    elif kind == 'sin':
        X = np.sin(3*L)
        Y = X+.2*err
    elif kind == 'entre_splits':
        X = np.repeat(mu, n)
    elif kind == 'nulo_condicional':
        X = .9*L+.1*rng.normal(size=len(sp))
        Y = .7*L-.2*L**2+.05*L**3+.5*err
    return sp, X, L, Y


def run_subject(case, input_path, B, control=None):
    result_file = RUN/'subject'/(case+'.json')
    cmd = [sys.executable, str(STAGE/'scripts/subject_worker_v1.py'), '--input', input_path,
           '--out', str(result_file), '--B', str(B)]
    if control:
        cmd += ['--control', control]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=300)
    with (RUN/'subject'/(case+'.stdout.txt')).open('x') as f:
        f.write(proc.stdout)
    with (RUN/'subject'/(case+'.stderr.txt')).open('x') as f:
        f.write(proc.stderr)
    if proc.returncode or not result_file.exists():
        return dict(status='PROCESS_ERROR', returncode=proc.returncode)
    return json.loads(result_file.read_text())


def comparison(task):
    name, control, scenario, seed = task
    started = time.perf_counter()
    record = dict(case=name)
    try:
        with np.load(ARRAYS/'discovery.npz', allow_pickle=False) as z:
            ds, dx, dl, dy = [z[k] for k in ['sp', 'X', 'L', 'Y']]
        if scenario:
            sp, X, L, Y = synthetic(scenario, seed)
        else:
            sp, X, L, Y = ds, dx, dl, dy
        raw = arrays('A2_'+name, sp=sp, X=X, L=L, Y=Y)
        B = 5000 if name == 'discovery' else 199
        actual = run_subject(name, raw['path'], B, control)
        if control:
            X, L, Y = ref.author_control(control, sp, X, L, Y)
        independent = ref.primary(sp, X, L, Y, B=B, explicit_null=(B == 199))
        null = independent.pop('null')
        evidence = arrays('A2_ref_'+name, sp=sp, X=X, L=L, Y=Y,
                          null=np.array([]) if null is None else null)
        record.update(subject=actual, independent=independent, input=raw, evidence=evidence, B=B)
        if actual['status'] != 'OK':
            record['status'] = 'SUBJECT_ERROR'
        else:
            s = actual['primary']
            if s['D'] is None or independent['D'] is None:
                passed = s['D'] is None and independent['D'] is None
                record.update(status='PASS' if passed else 'FAIL', defined=False)
            else:
                delta = abs(s['D']-independent['D'])
                db = abs(s['pendiente_X']-independent['beta'])
                peq = s['p'] == independent['p']
                fastpeq = independent['p_fast'] == independent['p']
                fastD = abs(independent['D_fast']-independent['D'])
                # Candidatos observados redundantes en la base pueden tener
                # pendiente no identificable, pero su predicción sí se compara.
                beta_ok = db <= 1e-8*max(1, abs(s['pendiente_X']))
                record.update(D_error=delta, beta_error=db, p_identical=peq,
                              p_fast_identical=fastpeq, D_fast_error=fastD, defined=True,
                              literal_p_differs=s['p'] != independent['p_literal'])
                record['status'] = 'PASS' if delta <= 1e-10 and peq and fastpeq and fastD <= 1e-10 and beta_ok else 'FAIL'
        record['reference_verdict'] = ref.verdict(independent)
    except Exception:
        record.update(status='AUDIT_ERROR', exception=traceback.format_exc())
    record['seconds'] = time.perf_counter()-started
    write(RUN/'comparisons'/(name+'.json'), record)
    return dict(case=name, status=record['status'], seconds=record['seconds'])


def cli_case(name):
    started = time.perf_counter()
    record = dict(case=name)
    try:
        rng = np.random.default_rng(260300)
        sp = np.repeat(np.arange(168, 324), 5)
        L = rng.normal(size=len(sp))
        X = -2+.2*rng.normal(size=len(sp))
        Y = .5*L+3*X+.01*rng.normal(size=len(sp))
        errors = np.full(len(sp), '', dtype='U12')
        gate = dict(PASA=True, synthetic=True)
        keep = np.ones(len(sp), bool)
        rho_override = None
        expected = 'PASS'
        if name == 'gate_false':
            gate['PASA'] = False
            expected = 'INCONCLUSIVE'
        elif name == 'gate_absent':
            expected = 'INCONCLUSIVE'
        elif name == 'missing47_omitted':
            keep[np.arange(47)*5] = False
            expected = 'INCONCLUSIVE'
        elif name == 'missing47_explicit':
            errors[np.arange(47)*5] = 'SYNTH_ERROR'
            expected = 'INCONCLUSIVE'
        elif name == 'splits40_omitted':
            keep[sp < 208] = False
            expected = 'INCONCLUSIVE'
        elif name in ['missing39_explicit', 'missing40_explicit']:
            count = 39 if '39' in name else 40
            errors[np.arange(count)*5] = 'SYNTH_ERROR'
            expected = 'PASS' if count == 39 else 'INCONCLUSIVE'
        elif name == 'X_constant':
            X[:] = -2
            expected = 'INCONCLUSIVE'
        elif name == 'X_between_splits':
            X = np.repeat(rng.normal(size=156), 5)
            expected = 'INCONCLUSIVE'
        elif name == 'L_constant':
            L[:] = 0
            expected = 'CONTROLLED_UNDEFINED'
        elif name == 'Y_constant':
            Y[:] = 0
            expected = 'CONTROLLED_UNDEFINED'
        elif name == 'rho_zero':
            rho_override = 0
            expected = 'CONTROLLED_INVALID_INPUT'
        elif name == 'rho_negative':
            rho_override = -1
            expected = 'CONTROLLED_INVALID_INPUT'
        elif name == 'empty':
            keep[:] = False
            expected = 'INCONCLUSIVE'
        elif name == 'all_n2':
            keep[np.arange(len(sp)) % 5 >= 2] = False
            expected = 'INCONCLUSIVE'
        elif name == 'duplicates':
            # Duplicación de las mismas filas/IDs, no nuevas trayectorias.
            sp, X, L, Y, errors = [np.repeat(a, 2) for a in [sp, X, L, Y, errors]]
            keep = np.ones(len(sp), bool)
            expected = 'CONTROLLED_DUPLICATE_INPUT'
        sp, X, L, Y, errors = [a[keep] for a in [sp, X, L, Y, errors]]
        folder = RUN/'cli'/name
        folder.mkdir()
        table = ARRAYS/('cli_'+name+'.csv')
        input_csv(table, sp, X, L, Y, errors=errors, rho_override=rho_override)
        if name == 'duplicates':
            # Restaurar los identificadores duplicados exactamente como sus filas.
            rr = list(csv.DictReader(table.open()))
            for i in range(0, len(rr), 2):
                rr[i+1] = rr[i].copy()
            dupe = ARRAYS/('cli_'+name+'_ids.csv')
            with dupe.open('x') as file:
                w = csv.DictWriter(file, fieldnames=rr[0].keys(), lineterminator='\n')
                w.writeheader()
                w.writerows(rr)
            table = dupe
        gatefile = folder/'synthetic_gate.json'
        write(gatefile, gate)
        cmd = [sys.executable, str(STAGE/'scripts/cli_worker_v1.py'), '--tabla', str(table),
               '--tabla-sha', sha(table), '--out', str(folder/'output')]
        if name != 'gate_absent':
            cmd += ['--compuerta', str(gatefile)]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=300)
        with (folder/'stdout.txt').open('x') as file:
            file.write(proc.stdout)
        with (folder/'stderr.txt').open('x') as file:
            file.write(proc.stderr)
        resultpath = folder/'output/RESULTADO_C1.json'
        output = json.loads(resultpath.read_text()) if resultpath.exists() else None
        record.update(returncode=proc.returncode, expected=expected, output=output,
                      input=dict(path=str(table), sha256=sha(table), rows=len(sp)),
                      status='RECORDED', planned_splits=156, planned_trajectories=780)
        if expected.startswith('CONTROLLED'):
            record['contract_pass'] = proc.returncode == 0 and output is not None and output['veredicto'] == 'INCONCLUSIVE'
        else:
            record['contract_pass'] = proc.returncode == 0 and output is not None and output['veredicto'] == expected
    except Exception:
        record.update(status='AUDIT_ERROR', exception=traceback.format_exc())
    record['seconds'] = time.perf_counter()-started
    write(RUN/'cli'/(name+'.json'), record)
    return dict(case=name, status=record['status'], contract_pass=record.get('contract_pass'), seconds=record['seconds'])


def monte_carlo(task):
    scenario, rep = task
    started = time.perf_counter()
    index = ['N0', 'N1', 'N2', 'P010', 'P015'].index(scenario)
    rng = np.random.default_rng(np.random.SeedSequence([260400, index, rep]))
    try:
        global BASE
        if BASE is None:
            with np.load(ARRAYS/'discovery.npz', allow_pickle=False) as z:
                BASE = {key: z[key].copy() for key in ['sp', 'X', 'L', 'Y']}
        groups = np.unique(BASE['sp'])
        chosen = rng.choice(groups, size=156, replace=True)
        indices = np.concatenate([np.flatnonzero(BASE['sp'] == s) for s in chosen])
        L, Y = BASE['L'][indices], BASE['Y'][indices]
        sp = np.repeat(np.arange(168, 324), 5)
        if len(L) != 780:
            raise RuntimeError('Bootstrap con split incompleto')
        z = (L-L.mean())/L.std()
        if scenario == 'N0':
            X = rng.normal(size=len(L))
        elif scenario == 'N1':
            X = .9*z+.1*rng.normal(size=len(L))
            Y = .7*z-.2*z**2+.05*z**3+rng.normal(size=len(L))
        elif scenario == 'N2':
            sig = np.repeat(np.exp(np.linspace(-2, 2, 156)), 5)
            X = sig*rng.normal(size=len(L))
            Y = .7*z-.2*z**2+.05*z**3+sig*rng.normal(size=len(L))
        else:
            r = .1 if scenario == 'P010' else .15
            bb = ref.covariates(L, sp)
            yc = ref.centered(Y, sp)
            e = yc-bb@ref.pinverse(bb)@yc
            X = r*e/e.std()+np.sqrt(1-r*r)*rng.normal(size=len(L))
        result = ref.primary(sp, X, L, Y, B=199)
        null = result.pop('null')
        r_actual = None
        if scenario.startswith('P'):
            r_actual = float(np.corrcoef(X, e)[0, 1])
        sensitivity = None
        if rep < 5 and scenario in ['N0', 'P010', 'P015']:
            more = ref.primary(sp, X, L, Y, B=5000)
            null5000 = more.pop('null')
            sensitivity = dict(**more, verdict=ref.verdict(more))
        else:
            null5000 = np.array([])
        meta = arrays(f'MC_{scenario}_{rep:03}', sp=sp, X=X, L=L, Y=Y,
                      bootstrap=chosen, null=null, null5000=null5000)
        return dict(scenario=scenario, replicate=rep, status='OK', result=result,
                    verdict=ref.verdict(result), realised_r=r_actual, sensitivity=sensitivity,
                    array=meta, seconds=time.perf_counter()-started)
    except Exception:
        return dict(scenario=scenario, replicate=rep, status='AUDIT_ERROR',
                    exception=traceback.format_exc(), seconds=time.perf_counter()-started)


def chord_test():
    # Ejecutar sólo el nodo función puro cuerda, no imports/main de cohorte.
    source = SOURCES/'c1_cohorte.py'
    tree = ast.parse(source.read_text())
    node = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == 'cuerda')
    scope = dict(np=np, math=math)
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), scope)
    f = np.column_stack([np.r_[np.linspace(-1, 1, 26), 0.], np.r_[np.zeros(26), 1.]])
    M = 1e-12*np.eye(27)
    M[0, 0] += 1
    returned = scope['cuerda'](M, f)
    delta = np.full(27, -1/27)
    delta[:26] += 1/26
    chord_all_face = float(np.sqrt(delta@M@delta))
    # Todos los26 pesos de la cara evolucionan juntos; a_27 decrece monótono.
    # La imagen a(su) es un segmento, así que su longitud ES la cuerda.
    info = arrays('chord_face26', f=f, M=M, delta=delta)
    write(RUN/'chord_face26.json', dict(source_lines=[46, 53], returned=returned,
                                       actual_ray_length=chord_all_face,
                                       ratio=returned/chord_all_face,
                                       exceeds_concrete_ray=returned > chord_all_face,
                                       array=info))


def main():
    code_guard()
    guard()
    RUN.mkdir(parents=True, exist_ok=False)
    ARRAYS.mkdir(parents=True, exist_ok=False)
    for sub in ['subject', 'comparisons', 'cli']:
        (RUN/sub).mkdir()
    started = time.perf_counter()
    write(RUN/'environment.json', dict(python=sys.version, platform=platform.platform(),
                                       numpy=np.__version__, scipy=scipy.__version__,
                                       code_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                                       configuration=CONFIG))
    data = discovery()
    meta = arrays('discovery', **{key: data[key] for key in ['sp', 'X', 'L', 'Y']})
    with (RUN/'discovery_table.csv').open('x') as file:
        writer = csv.DictWriter(file, fieldnames=data['rows'][0].keys(), lineterminator='\n')
        writer.writeheader()
        writer.writerows(data['rows'])
    write(RUN/'discovery_provenance.json', dict(rows=len(data['sp']), splits=len(np.unique(data['sp'])),
                                              source_rows=data['source_rows'], problems=data['problems'], array=meta,
                                              empirical_use='EXPLORATORY_SPENT_DATA_ONLY'))
    tasks = [('discovery', None, None, None)]
    tasks += [('author_'+name, name, None, None) for name in AUTHOR]
    tasks += [(f'{kind}_{seed}', None, kind, seed) for seed in CONFIG['synthetic_seeds'] for kind in SCENARIOS]
    comparisons = []
    with cf.ProcessPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(comparison, task) for task in tasks]
        for future in cf.as_completed(futures):
            r = future.result()
            comparisons.append(r)
            print('A2', len(comparisons), '/', len(tasks), r, flush=True)
    chord_test()
    names = ['complete', 'gate_false', 'gate_absent', 'missing47_omitted', 'missing47_explicit',
             'splits40_omitted', 'missing39_explicit', 'missing40_explicit', 'X_constant',
             'X_between_splits', 'L_constant', 'Y_constant', 'rho_zero', 'rho_negative',
             'empty', 'all_n2', 'duplicates']
    cli = []
    with cf.ProcessPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(cli_case, name) for name in names]
        for future in cf.as_completed(futures):
            r = future.result()
            cli.append(r)
            print('A3 CLI', len(cli), '/', len(names), r, flush=True)
    mc_results = []
    with (RUN/'monte_carlo.jsonl').open('x') as log:
        with cf.ProcessPoolExecutor(max_workers=2) as pool:
            jobs = [(scenario, rep) for scenario in ['N0', 'N1', 'N2', 'P010', 'P015'] for rep in range(400)]
            futures = [pool.submit(monte_carlo, job) for job in jobs]
            for future in cf.as_completed(futures):
                r = future.result()
                mc_results.append(r)
                from support_v1 import plain
                log.write(json.dumps(plain(r), allow_nan=False)+'\n')
                log.flush()
                if len(mc_results) % 50 == 0:
                    print('A4', len(mc_results), '/2000', flush=True)
    write(RUN/'resources.json', dict(seconds=time.perf_counter()-started, workers=2,
                                    comparisons=comparisons, cli=cli, monte_carlo=len(mc_results)))


if __name__ == '__main__':
    main()
