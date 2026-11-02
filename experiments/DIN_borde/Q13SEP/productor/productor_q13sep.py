"""Productor de DIN-Q13-SEP v2 (piloto de separabilidad), según DISENO_DIN_Q13SEP_v2_CONGELADO.md.

Solo mide c, q, tr M, S_panel, S_train, confianzas y precisiones por (entrenamiento,
visita, rol de temperatura). NO calcula X, R, min p_y, ρ, L, Y, D ni ninguna
asociación de señal (config «prohibidas»). La decisión (emparejamientos, dosis,
veredicto) la hace `analisis_q13sep.py`, aparte.

Fases (tarea del pool = un entrenamiento; spawn; un hilo por proceso):
  1. entrenamientos: A0 mide A0_ANCHOR (T=1); LP mide GRID j=-16..16 (T=2^(j/8)).
     Se guardan los pesos originales de cada visita (sin pérdida).
  2. E_MATCH: para cada LP, T* = exp(log S_LP(1) − log S_A0(1)) con S de las filas
     A0_ANCHOR y GRID j0 de la misma unidad y visita; copia fresca, l3/T*, M nueva.
  3. controles oficiales (calibración, s0/k0, u250): tres reconstrucciones sin pérdida
     (error 0) y contraste de rutas T1 con `recipe_v1.metric` (≤ 1e-12).
  4. tabla `q13sep_medidas_v2.csv` (fase completa) y resumen operativo.

Uso (equipo del responsable):
  python -I productor_q13sep.py --fase cal --salida D:\\RIPG_DATA\\DIN_Q13SEP\\cal --prueba-corta
  python -I productor_q13sep.py --fase cal --salida D:\\RIPG_DATA\\DIN_Q13SEP\\cal
  python -I productor_q13sep.py --fase val --salida D:\\RIPG_DATA\\DIN_Q13SEP\\val --dosis <DOSIS_Y_REGLAS_Q13SEP_v2.json> --dosis-sha <sha>
Reanudable y exclusivo: lo escrito no se repite ni se sobrescribe; una tarea interrumpida
se conserva movida a `interrumpidas/` y se repite desde cero.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import copy
import csv
import datetime as dt
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import statistics
import sys
import time
import traceback
import types

import numpy as np

AQUI = Path(__file__).resolve().parent
ROOT = AQUI.parents[3]
CONFIG_REL = 'experiments/DIN_borde/Q13SEP/config_v2_CONGELADO.json'
CONFIG_SHA = 'e8074d509f1e5d22e8463d0d7fc00201eb9d6d35207115e1c4dceb60db1f9bf3'
FORMATO = 'DIN-Q13SEP-productor-v1'
COLUMNAS = ('phase,measure_id,trajectory,condition,lambda,split,k,update,temperature_role,j,T,c,q,tr_M,S_panel,'
            'S_train,conf_media_verdadera_panel,conf_media_maxima_panel,acc_train,acc_panel,estado_medida,error,'
            'no_aprendio_final,checkpoint_original_sha256,checkpoint_T_sha256,M_sha256,f_sha256,dataset_sha256,'
            'batches_sha256,cpu_seconds,wall_seconds,M_seconds,memory_peak_mb').split(',')
J_GRID = list(range(-16, 17))
_MOD = {}
CFG = None


# ------------------------------------------------------------------ utilidades
def sha_archivo(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def limpiar(x):
    if isinstance(x, dict):
        return {str(k): limpiar(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [limpiar(v) for v in x]
    if isinstance(x, np.ndarray):
        return limpiar(x.tolist())
    if isinstance(x, np.generic):
        return limpiar(x.item())
    if isinstance(x, float) and not math.isfinite(x):
        return None
    return x


def json_exclusivo(path, obj):
    texto = json.dumps(limpiar(obj), indent=1, ensure_ascii=False, allow_nan=False, sort_keys=True)
    with open(path, 'x', encoding='utf-8', newline='\n') as fh:
        fh.write(texto+'\n')
    return sha_archivo(path)


def npz_exclusivo(path, **arrays):
    with open(path, 'xb') as fh:
        np.savez(fh, **arrays)          # sin compresión: recarga byte a byte
    return sha_archivo(path)


def memoria_pico_mb():
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes

        class PMC(ctypes.Structure):
            _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD),
                        ('PeakWorkingSetSize', ctypes.c_size_t), ('WorkingSetSize', ctypes.c_size_t),
                        ('QuotaPeakPagedPoolUsage', ctypes.c_size_t), ('QuotaPagedPoolUsage', ctypes.c_size_t),
                        ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t), ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
                        ('PagefileUsage', ctypes.c_size_t), ('PeakPagefileUsage', ctypes.c_size_t)]
        k32 = ctypes.WinDLL('kernel32', use_last_error=True)
        k32.GetCurrentProcess.restype = wintypes.HANDLE
        k32.K32GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
        k32.K32GetProcessMemoryInfo.restype = wintypes.BOOL
        pmc = PMC()
        pmc.cb = ctypes.sizeof(PMC)
        if not k32.K32GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb):
            return None
        return pmc.PeakWorkingSetSize/2**20 if pmc.PeakWorkingSetSize > 0 else None
    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024


def versiones():
    import importlib.metadata as md
    import torch
    return {'torch': torch.__version__, 'numpy': md.version('numpy'), 'scipy': md.version('scipy'),
            'scikit-learn': md.version('scikit-learn')}


# ------------------------------------------------------------------ fuentes congeladas
def cargar_config():
    global CFG
    p = ROOT/CONFIG_REL
    if sha_archivo(p) != CONFIG_SHA:
        raise SystemExit('La configuración congelada no coincide con su SHA publicado')
    CFG = json.loads(p.read_text(encoding='utf-8'))
    if CFG['estado'] != 'CONGELADO':
        raise SystemExit('La configuración no está CONGELADO')
    for k, s in CFG['sources'].items():
        if sha_archivo(ROOT/s['path']) != s['sha256']:
            raise SystemExit('Fuente congelada modificada: '+k)
    return CFG


def modulo(nombre):
    """Carga core, receta y adaptador LP desde sus archivos verificados por SHA."""
    if nombre in _MOD:
        return _MOD[nombre]
    s = CFG['sources'][{'core': 'core', 'recipe': 'recipe', 'lp': 'LP_adapter'}[nombre]]
    p = ROOT/s['path']
    data = p.read_bytes()
    if hashlib.sha256(data).hexdigest() != s['sha256']:
        raise RuntimeError('Fuente modificada: '+nombre)
    if nombre == 'lp':
        sys.modules['recipe_v1'] = modulo('recipe')   # el adaptador importa la receta intacta
    m = types.ModuleType({'core': 'q13sep_core', 'recipe': 'recipe_v1', 'lp': 'recipe_m2'}[nombre])
    m.__file__ = str(p)
    exec(compile(data, str(p), 'exec'), m.__dict__)
    _MOD[nombre] = m
    return m


# ------------------------------------------------------------------ universo
def fase_cfg(fase):
    return CFG['calibracion' if fase == 'cal' else 'validacion']


def condiciones(fase, dosis_val=None):
    """[(condición, brazo, λ)] en el orden congelado."""
    if fase == 'cal':
        return [('A0', 'A0', None)] + [(f'LP0{i+1}', 'LP', lam) for i, lam in enumerate(CFG['calibracion']['LP_grid'])]
    return [('A0', 'A0', None), ('LP', 'LP', dosis_val)]


def tray_id(fase, cond, s, k):
    return f'q13sep_{fase}_{cond}_s{s:04d}_k{k}'


def medida_id(t, u, rol, j=None):
    return f'{t}_u{u:03d}_{rol}' + (f'_j{j:+03d}' if rol == 'GRID' else '')


def universo_filas(fase, dosis_val=None):
    """Lista ordenada (tabla) de dicts con las claves de cada medida planificada."""
    fc = fase_cfg(fase)
    filas = []
    for s in range(fc['n_splits']):
        for k in range(fc['n_inits']):
            for cond, brazo, lam in condiciones(fase, dosis_val):
                t = tray_id(fase, cond, s, k)
                if brazo == 'A0':
                    roles = [('A0_ANCHOR', None)]
                else:
                    roles = [('GRID', j) for j in J_GRID] + [('E_MATCH', None)]
                for rol, j in roles:          # orden de tabla: ... condición → T → visita
                    for u in CFG['receta']['visitas']:
                        filas.append(dict(phase=fase, measure_id=medida_id(t, u, rol, j), trajectory=t, condition=cond,
                                          arm=brazo, lam=lam, split=s, k=k, update=u, role=rol, j=j))
    return filas


def plan(fase, dosis_val=None):
    filas = universo_filas(fase, dosis_val)
    ids = [f['measure_id'] for f in filas]
    if len(set(ids)) != len(ids):
        raise RuntimeError('IDs de medida duplicados')
    esperado = fase_cfg(fase)['n_celdas_de_visita']
    if len(ids) != esperado:
        raise RuntimeError(f'Universo de {len(ids)} medidas, se esperaban {esperado}')
    trays = sorted({(f['split'], f['k'], f['condition']) for f in filas})
    return dict(formato=FORMATO, fase=fase, config_sha256=CONFIG_SHA, n_medidas=len(ids),
                n_entrenamientos=len(trays), ids_sha256=sha_bytes('\n'.join(ids).encode()),
                lambda_validacion=dosis_val)


# ------------------------------------------------------------------ medición
def params_bytes(model):
    return b''.join(p.detach().numpy().tobytes() for p in model.parameters())


def escala(z):
    """S: raíz media cuadrática de los logits centrados entre clases (por ejemplo)."""
    zc = z-z.mean(axis=1, keepdims=True)
    return float(np.sqrt((zc**2).mean()))


def medir(torch, model_orig, T, datos, ref=None):
    """Una medida con copia fresca y cabeza dividida entre T. `ref` = (z_panel_1, z_train_1, accs) del modelo T=1."""
    core = modulo('core')
    c0, w0 = time.process_time(), time.perf_counter()
    m = copy.deepcopy(model_orig)
    with torch.no_grad():
        m.l3.weight.div_(T)
        m.l3.bias.div_(T)
    out = dict(T=T, checkpoint_T_sha256=sha_bytes(params_bytes(m)))
    tm = time.perf_counter()
    Rb, Ub, fp = core.make_geom_state(m, datos['xp'], datos['yp'])
    M = core.subset_M(Rb, Ub, [0, 1, 2]).numpy()
    out['M_seconds'] = time.perf_counter()-tm
    f = fp.numpy()
    with torch.no_grad():
        zp = m(datos['xp']).numpy()
        zt = m(datos['xt']).numpy()
    diag = np.diag(M)
    traza, norma = float(np.trace(M)), float(np.linalg.norm(M))
    errores = []
    if not np.isfinite(M).all() or not traza > 0 or not norma > 0:
        errores.append('M no finita o traza/norma no positiva')
    else:
        out.update(c=float(diag.max()/traza), q=float(np.linalg.norm(M-np.diag(diag))/norma), tr_M=traza)
    sp, st = escala(zp), escala(zt)
    lp = zp-np.logaddexp.reduce(zp, axis=1, keepdims=True)
    pp = np.exp(lp)
    yp = datos['yp_np']
    out.update(S_panel=sp, S_train=st, conf_media_verdadera_panel=float(pp[np.arange(len(yp)), yp].mean()),
               conf_media_maxima_panel=float(pp.max(axis=1).mean()),
               acc_train=float((np.argmax(zt, axis=1) == datos['yt_np']).mean()),
               acc_panel=float((np.argmax(zp, axis=1) == yp).mean()),
               M_sha256=sha_bytes(np.ascontiguousarray(M).tobytes()), f_sha256=sha_bytes(np.ascontiguousarray(f).tobytes()))
    for nombre, v in (('S_panel', sp), ('S_train', st)):
        if not (math.isfinite(v) and v > 0):
            errores.append(nombre+' no positiva')
    if 'c' in out and not (0 < out['c'] <= 1 and 0 <= out['q'] <= 1):
        errores.append('c o q fuera de dominio')
    # controles por medida: z_T = z_1/T, S_T = S_1/T, precisiones idénticas
    if ref is not None:
        zp1, zt1, acc1 = ref
        for nombre, z, z1 in (('z_panel', zp, zp1), ('z_train', zt, zt1)):
            esperado = z1/T
            err = float(np.linalg.norm(z-esperado))/max(1.0, float(np.linalg.norm(esperado)))
            out[f'err_{nombre}'] = err
            if not err <= CFG['controles']['z_T_error_normalizado_max']:
                errores.append(f'control {nombre}_T = {nombre}_1/T falla ({err:.3e})')
        for nombre, v, v1 in (('S_panel', sp, escala(zp1)), ('S_train', st, escala(zt1))):
            err = abs(v-v1/T)/max(1.0, abs(v1/T))
            out[f'err_{nombre}'] = err
            if not err <= CFG['controles']['S_T_error_normalizado_max']:
                errores.append(f'control {nombre}_T = {nombre}_1/T falla ({err:.3e})')
        if (out['acc_train'], out['acc_panel']) != acc1:
            errores.append('control: precisiones distintas entre T')
    out['cpu_seconds'] = time.process_time()-c0
    out['wall_seconds'] = time.perf_counter()-w0
    out['estado_medida'] = 'FALLIDA' if errores else 'MEDIDA'
    out['error'] = ' | '.join(errores)
    return out, M, f


def datos_split(torch, fase, s):
    rec = modulo('recipe')
    seed = fase_cfg(fase)['seed_bases']['split']+s
    Z, y, tr, va = rec.dataset(seed)
    d = dict(xt=torch.tensor(Z[tr]), yt=torch.tensor(y[tr]), xp=torch.tensor(Z[va]), yp=torch.tensor(y[va]),
             yt_np=np.asarray(y[tr]), yp_np=np.asarray(y[va]), Z=Z, y=y, tr=tr, va=va, seed=seed,
             dataset_sha256=sha_bytes(np.ascontiguousarray(Z).tobytes()+np.ascontiguousarray(y).tobytes()))
    return d


def ref_T1(torch, model, datos):
    with torch.no_grad():
        zp = model(datos['xp']).numpy()
        zt = model(datos['xt']).numpy()
    return zp, zt, (float((np.argmax(zt, axis=1) == datos['yt_np']).mean()),
                    float((np.argmax(zp, axis=1) == datos['yp_np']).mean()))


def fila_base(fase, t, cond, lam, s, k, u, rol, j):
    f = {c: '' for c in COLUMNAS}
    f.update(phase=fase, measure_id=medida_id(t, u, rol, j), trajectory=t, condition=cond,
             **{'lambda': '' if lam is None else lam}, split=s, k=k, update=u, temperature_role=rol,
             j='' if j is None else j)
    return f


def entrenar(fase, s, k, cond, brazo, lam, carpeta):
    """Una tarea del pool: un entrenamiento con sus medidas de A0_ANCHOR o GRID."""
    import torch
    rec, lp = modulo('recipe'), modulo('lp')
    fc = fase_cfg(fase)
    t = tray_id(fase, cond, s, k)
    datos = datos_split(torch, fase, s)
    s_init = fc['seed_bases']['init']+5*s+k
    s_lote = fc['seed_bases']['lote']+5*s+k
    model, opt, inicial = rec.initialize(s_init, brazo, lam if lam is not None else 0., torch)
    rng = np.random.default_rng(s_lote)
    lotes = hashlib.sha256()
    filas, visitas, u, fallo = [], {}, 0, None
    t_train = 0.0
    w0 = time.perf_counter()
    for v in CFG['receta']['visitas']:
        roles = [('A0_ANCHOR', None)] if brazo == 'A0' else [('GRID', j) for j in J_GRID]
        if fallo is None:
            try:
                ta = time.perf_counter()
                while u < v:
                    lp.update_m2(model, opt, datos['xt'], datos['yt'], rng, lotes, brazo,
                                 lam if lam is not None else 0., torch)
                    u += 1
                t_train += time.perf_counter()-ta
            except Exception:
                fallo = f'entrenamiento interrumpido en el update {u+1}: '+traceback.format_exc(limit=3)
        if fallo is not None:
            for rol, j in roles:
                f = fila_base(fase, t, cond, lam, s, k, v, rol, j)
                f.update(estado_medida='FALLIDA', error='visita no alcanzada: '+fallo, dataset_sha256=datos['dataset_sha256'])
                filas.append(f)
            visitas[v] = dict(alcanzada=False)
            continue
        ck = sha_bytes(params_bytes(model))
        estado_opt = {f'{n}_{i}': x.detach().numpy() for i, st in enumerate(opt.state.values())
                      for n, x in st.items() if hasattr(x, 'numpy')}
        npz_sha = npz_exclusivo(carpeta/f'u{v:03d}_pesos.npz',
                                **{f'p{i}': p.detach().numpy() for i, p in enumerate(model.parameters())}, **estado_opt)
        visitas[v] = dict(alcanzada=True, checkpoint_sha256=ck, npz_sha256=npz_sha, rng=rng.bit_generator.state,
                          batches_sha256=lotes.hexdigest())
        ref = ref_T1(torch, model, datos)
        Ms = {}
        for rol, j in roles:
            T = 1.0 if j is None else 2.0**(j/8)
            f = fila_base(fase, t, cond, lam, s, k, v, rol, j)
            f.update(checkpoint_original_sha256=ck, dataset_sha256=datos['dataset_sha256'],
                     batches_sha256=lotes.hexdigest(), T=T)
            try:
                o, M, _ = medir(torch, model, T, datos, ref)
                Ms[f['measure_id']] = M
                f.update({c: o[c] for c in COLUMNAS if c in o})
                f['memory_peak_mb'] = memoria_pico_mb()
            except Exception:
                f.update(estado_medida='FALLIDA', error='medición: '+traceback.format_exc(limit=3))
            filas.append(f)
        npz_exclusivo(carpeta/f'u{v:03d}_M.npz', **Ms)
    acc_final = next((f['acc_train'] for f in filas if f['update'] == 250 and f['estado_medida'] == 'MEDIDA'
                      and float(f['T']) == 1.0), None)
    no_ap = 'unknown' if acc_final in (None, '') else ('true' if acc_final < CFG['calidad']['no_aprendio_acc_train_final_menor'] else 'false')
    for f in filas:
        f['no_aprendio_final'] = no_ap
    return dict(trajectory=t, fase=fase, split=s, k=k, condition=cond, arm=brazo, lam=lam, semilla_split=datos['seed'],
                semilla_init=s_init, semilla_lote=s_lote, pesos_iniciales_sha256=inicial, visitas=visitas,
                t_train_sin_medidas=t_train, latencia_total=time.perf_counter()-w0, filas=filas,
                memoria_pico_mb=memoria_pico_mb())


def cargar_modelo(torch, carpeta, v):
    rec = modulo('recipe')
    m = rec.network(torch)
    d = np.load(carpeta/f'u{v:03d}_pesos.npz')
    with torch.no_grad():
        for i, p in enumerate(m.parameters()):
            p.copy_(torch.from_numpy(d[f'p{i}']))
    return m


def e_match(fase, s, k, cond, lam, carpeta_lp, reg_a0, reg_lp):
    """E_MATCH de un LP: T* por visita a partir de las filas ya medidas (sin repetirlas)."""
    import torch
    t = tray_id(fase, cond, s, k)
    datos = datos_split(torch, fase, s)
    filas, Ms = [], {}
    no_ap = reg_lp['filas'][0]['no_aprendio_final'] if reg_lp.get('filas') else 'unknown'
    for v in CFG['receta']['visitas']:
        f = fila_base(fase, t, cond, lam, s, k, v, 'E_MATCH', None)
        f['dataset_sha256'] = datos['dataset_sha256']
        a0 = next((r for r in reg_a0['filas'] if r['update'] == v and r['temperature_role'] == 'A0_ANCHOR'), None)
        g0 = next((r for r in reg_lp['filas'] if r['update'] == v and r['temperature_role'] == 'GRID' and r['j'] == 0), None)
        motivo = None
        if a0 is None or g0 is None or a0['estado_medida'] != 'MEDIDA' or g0['estado_medida'] != 'MEDIDA':
            motivo = 'sin S_A0(1) o S_LP(1) medidas'
        else:
            sa, sl = float(a0['S_panel']), float(g0['S_panel'])
            if not (math.isfinite(sa) and sa > 0 and math.isfinite(sl) and sl > 0):
                motivo = 'escalas no finitas o no positivas'
            else:
                T = math.exp(math.log(sl)-math.log(sa))
                if not (math.isfinite(T) and T > 0):
                    motivo = 'T* no finita o no positiva'
        if motivo:
            f.update(estado_medida='FALLIDA', error='E_MATCH: '+motivo, no_aprendio_final=no_ap)
            filas.append(f)
            continue
        model = cargar_modelo(torch, carpeta_lp, v)
        vis = reg_lp['visitas'][str(v)] if str(v) in reg_lp['visitas'] else reg_lp['visitas'][v]
        f.update(checkpoint_original_sha256=vis['checkpoint_sha256'], batches_sha256=vis['batches_sha256'], T=T,
                 no_aprendio_final=no_ap)
        try:
            if sha_bytes(params_bytes(model)) != vis['checkpoint_sha256']:
                raise RuntimeError('pesos recargados distintos del checkpoint')
            o, M, _ = medir(torch, model, T, datos, ref_T1(torch, model, datos))
            Ms[f['measure_id']] = M
            f.update({c: o[c] for c in COLUMNAS if c in o})
            err = abs(o['S_panel']-sa)/sa
            if not err <= CFG['controles']['E_igualdad_S_error_rel_max']:
                f['estado_medida'] = 'FALLIDA'
                f['error'] = (f['error']+' | ' if f['error'] else '')+f'igualdad de S fuera de tolerancia ({err:.3e})'
            f['memory_peak_mb'] = memoria_pico_mb()
        except Exception:
            f.update(estado_medida='FALLIDA', error='E_MATCH medición: '+traceback.format_exc(limit=3))
        filas.append(f)
    npz_exclusivo(carpeta_lp/'E_MATCH_M.npz', **Ms)
    return dict(trajectory=t, filas=filas)


# ------------------------------------------------------------------ controles oficiales
def controles(out, fase):
    """Tres reconstrucciones sin pérdida (error 0) y contraste de rutas T1 (≤ 1e-12), u250, cal s0/k0."""
    import torch
    rec, core = modulo('recipe'), modulo('core')
    res = []
    for spec in CFG['controles']['reconstrucciones_prefijadas']:
        t = tray_id(fase, spec['condition'], spec['split'], spec['k'])
        carpeta = out/'entrenamientos'/t
        mid = medida_id(t, spec['update'], spec['role'], spec['j'])
        r = dict(spec=spec, measure_id=mid)
        try:
            original = np.load(carpeta/f"u{spec['update']:03d}_M.npz")[mid]
            datos = datos_split(torch, fase, spec['split'])
            model = cargar_modelo(torch, carpeta, spec['update'])
            o, M, f = medir(torch, model, spec['T'], datos, ref_T1(torch, model, datos))
            r['reconstruccion_error_rel_frobenius'] = float(np.linalg.norm(M-original)/np.linalg.norm(original))
            r['f_identica'] = bool(np.array_equal(f, datos['xp'].numpy()[:, :2]))
            r['reconstruccion_ok'] = r['reconstruccion_error_rel_frobenius'] == CFG['controles']['reconstruccion_error_rel'] and r['f_identica']
            if spec['T'] == 1.0:   # contraste de rutas T1 con la ruta mínima de la receta
                c, q, acc, M_rec, f_rec = rec.metric(model, datos['Z'], datos['y'], datos['va'], core, torch)
                r['rutas_T1_error_rel_frobenius'] = float(np.linalg.norm(M-M_rec)/np.linalg.norm(M_rec))
                r['rutas_T1_f_identica'] = bool(np.array_equal(f, f_rec))
                r['rutas_T1_ok'] = r['rutas_T1_error_rel_frobenius'] <= CFG['controles']['T1_error_rel_max'] and r['rutas_T1_f_identica']
        except Exception:
            r['error'] = traceback.format_exc()
            r['reconstruccion_ok'] = False
        res.append(r)
    ok = all(r.get('reconstruccion_ok') and r.get('rutas_T1_ok', True) for r in res)
    return dict(controles=res, controles_ok=ok)


# ------------------------------------------------------------------ pool
def _iniciar():
    import torch
    torch.set_num_threads(1)
    cargar_config()
    modulo('core')       # fija float64 por defecto, como en G3/C2
    modulo('lp')


def _tarea_entrenar(fase, s, k, cond, brazo, lam, raiz):
    t = tray_id(fase, cond, s, k)
    carpeta = Path(raiz)/'entrenamientos'/t
    carpeta.mkdir(parents=True)
    try:
        reg = entrenar(fase, s, k, cond, brazo, lam, carpeta)
    except Exception:
        reg = dict(trajectory=t, error='tarea: '+traceback.format_exc(), filas=[], visitas={})
    json_exclusivo(carpeta/'registro.json', reg)
    return t, sum(f['estado_medida'] == 'MEDIDA' for f in reg['filas']), len(reg['filas'])


def _tarea_ematch(fase, s, k, cond, lam, raiz):
    raiz = Path(raiz)
    t = tray_id(fase, cond, s, k)
    c_lp = raiz/'entrenamientos'/t
    reg_lp = json.loads((c_lp/'registro.json').read_text(encoding='utf-8'))
    reg_a0 = json.loads((raiz/'entrenamientos'/tray_id(fase, 'A0', s, k)/'registro.json').read_text(encoding='utf-8'))
    parcial = c_lp/'E_MATCH_M.npz'
    if parcial.exists():     # E_MATCH interrumpido: se conserva y se repite desde cero
        parcial.rename(c_lp/f"E_MATCH_M_interrumpido_{dt.datetime.now().strftime('%Y%m%dT%H%M%S')}.npz")
    try:
        reg = e_match(fase, s, k, cond, lam, c_lp, reg_a0, reg_lp)
    except Exception:
        reg = dict(trajectory=t, error='tarea E_MATCH: '+traceback.format_exc(), filas=[])
    json_exclusivo(c_lp/'E_MATCH.json', reg)
    return t, sum(f['estado_medida'] == 'MEDIDA' for f in reg['filas'])


def entrenamientos_de(fase, dosis_val, prueba_corta):
    fc = fase_cfg(fase)
    pc = CFG['operacion']['prueba_corta']
    out = []
    for s in range(fc['n_splits']):
        for k in range(fc['n_inits']):
            if prueba_corta and not (s in pc['splits'] and k in pc['k']):
                continue
            for cond, brazo, lam in condiciones(fase, dosis_val):
                out.append((s, k, cond, brazo, lam))
    return out


# ------------------------------------------------------------------ tabla y resumen
def valor_csv(v):
    if v is None:
        return ''
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, float):
        return repr(v) if math.isfinite(v) else ''
    return str(v)


def recolectar(out, fase, dosis_val, solo_presentes):
    filas = {}
    for d in sorted((out/'entrenamientos').glob('*')):
        for nombre in ('registro.json', 'E_MATCH.json'):
            p = d/nombre
            if p.exists():
                for f in json.loads(p.read_text(encoding='utf-8'))['filas']:
                    if f['measure_id'] in filas:
                        raise SystemExit('Medida duplicada: '+f['measure_id'])
                    filas[f['measure_id']] = f
    orden = universo_filas(fase, dosis_val)
    if solo_presentes:
        return [filas[x['measure_id']] for x in orden if x['measure_id'] in filas]
    faltan = [x['measure_id'] for x in orden if x['measure_id'] not in filas]
    if faltan:
        raise SystemExit(f'Faltan {len(faltan)} medidas planificadas; la fase no está completa')
    return [filas[x['measure_id']] for x in orden]


def escribir_tabla(path, filas):
    buf = io.StringIO(newline='')
    w = csv.DictWriter(buf, fieldnames=COLUMNAS, lineterminator='\n')
    w.writeheader()
    for f in filas:
        w.writerow({c: valor_csv(f.get(c)) for c in COLUMNAS})
    with open(path, 'x', encoding='utf-8', newline='') as fh:
        fh.write(buf.getvalue())
    return sha_archivo(path)


def tiempos(out, filas, elapsed, procesos, fase, dosis_val):
    regs = [json.loads(p.read_text(encoding='utf-8')) for p in (out/'entrenamientos').glob('*/registro.json')]
    med = lambda xs: float(statistics.median(xs)) if xs else None
    mx = lambda xs: float(max(xs)) if xs else None
    ms = [float(f['M_seconds']) for f in filas if f.get('M_seconds') not in ('', None)]
    por_rol = {}
    for f in filas:
        if f.get('M_seconds') not in ('', None):
            por_rol.setdefault(f"{f['temperature_role']}_u{f['update']:03d}", []).append(float(f['M_seconds']))
    tt = [r['t_train_sin_medidas'] for r in regs if 't_train_sin_medidas' in r]
    lat = [r['latencia_total'] for r in regs if 'latencia_total' in r]
    mem = [r['memoria_pico_mb'] for r in regs if r.get('memoria_pico_mb')]
    # proyección de las dos fases con las cantidades congeladas
    tot = CFG['totales']
    t_train, t_M = med(tt) or 0., med(ms) or 0.
    io_por_tarea = max(0., (med(lat) or 0.)-t_train-sum(ms)/max(1, len(regs)))
    proy = (tot['n_entrenamientos_max']*(t_train+io_por_tarea)+tot['n_llamadas_M_max']*t_M)/(procesos*.8)/60
    return dict(entrenamientos=len(regs), medidas=len(filas), t_train_mediana=med(tt), t_train_max=mx(tt),
                t_M_mediana=med(ms), t_M_max=mx(ms),
                t_M_por_rol={k: dict(mediana=med(v), max=mx(v), n=len(v)) for k, v in sorted(por_rol.items())},
                latencia_tarea_mediana=med(lat), latencia_tarea_max=mx(lat), memoria_pico_mb_mediana=med(mem),
                memoria_pico_mb_max=mx(mem), elapsed_global_s=elapsed, procesos=procesos,
                proyeccion_dos_fases_min=proy,
                detener_si_supera_min=CFG['operacion']['detener_si_proyeccion_supera_minutos'],
                proyeccion_supera_limite=proy > CFG['operacion']['detener_si_proyeccion_supera_minutos'])


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fase', choices=('cal', 'val'), required=True)
    ap.add_argument('--salida', required=True)
    ap.add_argument('--procesos', type=int, default=12)
    ap.add_argument('--prueba-corta', action='store_true')
    ap.add_argument('--dosis', help='validación: DOSIS_Y_REGLAS_Q13SEP_v2.json publicado')
    ap.add_argument('--dosis-sha', help='validación: SHA publicado de ese archivo')
    ap.add_argument('--permitir-versiones', action='store_true', help='solo desarrollo; queda registrado')
    a = ap.parse_args()
    cargar_config()
    v = versiones()
    if v != CFG['versiones'] and not a.permitir_versiones:
        raise SystemExit(f'Versiones distintas de las fijadas: {v} != {CFG["versiones"]}')
    dosis_val = None
    if a.fase == 'val':
        if not a.dosis or not a.dosis_sha or sha_archivo(a.dosis) != a.dosis_sha:
            raise SystemExit('Validación: falta DOSIS_Y_REGLAS o su SHA no coincide con el publicado')
        dec = json.loads(Path(a.dosis).read_text(encoding='utf-8'))
        if dec.get('decision') != 'DOSIS_APTA' or dec.get('config_sha256') != CONFIG_SHA:
            raise SystemExit('La decisión de calibración no autoriza validación')
        dosis_val = float(dec['lambda'])
        if dosis_val not in CFG['calibracion']['LP_grid']:
            raise SystemExit('λ fuera de la rejilla congelada')
    if a.prueba_corta and a.fase != 'cal':
        raise SystemExit('La prueba corta pertenece a la calibración')
    _iniciar()
    out = Path(a.salida)
    (out/'entrenamientos').mkdir(parents=True, exist_ok=True)
    (out/'interrumpidas').mkdir(exist_ok=True)
    pl = plan(a.fase, dosis_val)
    meta = dict(pl, productor_sha256=sha_archivo(Path(__file__)), versiones=v, permitir_versiones=a.permitir_versiones,
                python=platform.python_version(), plataforma=platform.platform(),
                dosis_sha256=a.dosis_sha if a.fase == 'val' else None)
    pm = out/'meta.json'
    if pm.exists():
        previo = json.loads(pm.read_text(encoding='utf-8'))
        claves = ('formato', 'fase', 'config_sha256', 'ids_sha256', 'productor_sha256', 'versiones', 'dosis_sha256')
        if {k: previo.get(k) for k in claves} != {k: meta.get(k) for k in claves}:
            raise SystemExit('La carpeta de salida es de otra configuración; usa otra carpeta')
    else:
        json_exclusivo(pm, meta)
    for d in (out/'entrenamientos').glob('*'):
        if not (d/'registro.json').exists():
            d.rename(out/'interrumpidas'/f"{d.name}_{dt.datetime.now().strftime('%Y%m%dT%H%M%S')}")
            print('interrumpida conservada y repetida desde cero:', d.name, flush=True)
    t0 = time.perf_counter()
    lista = entrenamientos_de(a.fase, dosis_val, a.prueba_corta)
    pend = [x for x in lista if not (out/'entrenamientos'/tray_id(a.fase, x[2], x[0], x[1])/'registro.json').exists()]
    print(f'Entrenamientos: {len(lista)-len(pend)} ya escritos; {len(pend)} pendientes', flush=True)
    with cf.ProcessPoolExecutor(a.procesos, initializer=_iniciar) as ex:
        futs = [ex.submit(_tarea_entrenar, a.fase, s, k, cond, brazo, lam, str(out)) for s, k, cond, brazo, lam in pend]
        for i, fu in enumerate(cf.as_completed(futs), 1):
            t, ok, n = fu.result()
            print(f'[{i}/{len(futs)}] {t}: {ok}/{n} medidas  {time.perf_counter()-t0:.0f}s', flush=True)
        # E_MATCH: cada LP cuyo A0 de la misma unidad ya terminó
        em = []
        for s, k, cond, brazo, lam in lista:
            c = out/'entrenamientos'/tray_id(a.fase, cond, s, k)
            if brazo == 'LP' and not (c/'E_MATCH.json').exists() and (c/'registro.json').exists() and \
               (out/'entrenamientos'/tray_id(a.fase, 'A0', s, k)/'registro.json').exists():
                em.append((s, k, cond, lam))
        futs = [ex.submit(_tarea_ematch, a.fase, s, k, cond, lam, str(out)) for s, k, cond, lam in em]
        for i, fu in enumerate(cf.as_completed(futs), 1):
            t, ok = fu.result()
            print(f'[E_MATCH {i}/{len(futs)}] {t}: {ok}/2', flush=True)
    elapsed = time.perf_counter()-t0
    if a.fase == 'cal' and not (out/'controles.json').exists() and \
       (out/'entrenamientos'/tray_id('cal', 'LP01', 0, 0)/'registro.json').exists():
        ctl = controles(out, 'cal')
        json_exclusivo(out/'controles.json', ctl)
        print('Controles oficiales:', 'OK' if ctl['controles_ok'] else 'FALLA (corrida INVALIDA)', flush=True)
    filas = recolectar(out, a.fase, dosis_val, solo_presentes=a.prueba_corta)
    tm = tiempos(out, filas, elapsed, a.procesos, a.fase, dosis_val)
    estados = {}
    for f in filas:
        estados[f['estado_medida']] = estados.get(f['estado_medida'], 0)+1
    if a.prueba_corta:
        nombre = f"prueba_corta_tiempos_{dt.datetime.now().strftime('%Y%m%dT%H%M%S')}.json"
        json_exclusivo(out/nombre, dict(tm, estados=estados, nota='Prueba corta: parte del universo de calibración.'))
        print(json.dumps(dict(estados=estados, **{k: tm[k] for k in ('entrenamientos', 'medidas', 't_train_mediana',
              't_M_mediana', 't_M_max', 'latencia_tarea_mediana', 'memoria_pico_mb_max', 'elapsed_global_s',
              'proyeccion_dos_fases_min', 'proyeccion_supera_limite')}), indent=1, ensure_ascii=False))
        return 0
    tabla = out/'q13sep_medidas_v2.csv'
    tsha = escribir_tabla(tabla, filas)
    res = dict(meta, tabla_sha256=tsha, estados=estados, tiempos=tm,
               controles_sha256=sha_archivo(out/'controles.json') if (out/'controles.json').exists() else None,
               nota='Operacional: sin X, ρ ni D. La decisión la calcula analisis_q13sep.py.')
    json_exclusivo(out/'RESUMEN_Q13SEP.json', res)
    print(json.dumps(dict(estados=estados, tabla_sha256=tsha, productor_sha256=meta['productor_sha256'],
                          controles_sha256=res['controles_sha256']), indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
