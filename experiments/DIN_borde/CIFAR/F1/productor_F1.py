"""Productor de DIN-CIFAR F1 (descubrimiento), según DISENO_CIFAR_F1_v2_CONGELADO.md.

Produce la tabla larga `cifar_f1_visitas.csv` (ESQUEMA_TABLA_v2: 500 trayectorias
× 4 visitas = 2000 filas) y `RESUMEN_F1.json`, más registros externos por visita
(pesos, M, espectro, logits, f, resultado ρ completo). No analiza: el veredicto lo
calcula `analisis_F1_v2.py` (SHA 0c4d03b5…) con el plan congelado.

Reglas del diseño congelado que implementa:
- universo cifar_f1_s{split:04d}_k{k}, split 0..99, k 0..4; semillas 1.100.000+s,
  1.110.000+5s+k, 1.120.000+5s+k; Adam con lr = 0.003 explícito;
- X(t) = max_n [logsumexp_{c≠y_n} z − logsumexp z]; R(t) igual en k_star = primer
  argmax de diag M; c, q, tr M; precisión y CE de train, panel y test;
- ρ solo en u10 y u250, UNA llamada por estado, con las opciones por defecto de r3
  explícitas y un watchdog externo de 120 s de pared (proceso aparte); sin
  reintentos; aceptación como Q13-M2 (quad_error None = inválido);
- estados MEDIDA / INVALID_RHO / FALLIDA por visita; nada se sustituye.

Uso (equipo del responsable):
  python productor_F1.py --cifar D:\\RIPG_DATA\\cifar-10-python.tar.gz \\
      --compuerta D:\\RIPG_DATA\\DIN_CIFAR_F0\\compuerta.json \\
      --salida D:\\RIPG_DATA\\DIN_CIFAR_F1\\corrida --procesos 12
Reanudable: una trayectoria con registro escrito no se repite. Una carpeta de
trayectoria sin registro (proceso interrumpido) se conserva movida a
`interrumpidas/` y la trayectoria se ejecuta de nuevo desde cero.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import datetime as dt
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
import traceback
import warnings

import numpy as np

AQUI = Path(__file__).resolve().parent
CIFAR = AQUI.parent
ROOT = AQUI.parents[3]
sys.path.insert(0, str(CIFAR))
import instrumento_general as ig  # noqa: E402
import sistema_cifar3 as s3  # noqa: E402

FORMATO = 'DIN-CIFAR-F1-productor-v1'
PLAN_REL = 'experiments/DIN_borde/CIFAR/F1/plan_F1_v2_CONGELADO.json'
PLAN_SHA = '4347857e83fba828fda5910ffc9fd10feff8f4c14d37c27ac40e935b28ef34ae'
VISITAS = (5, 10, 30, 250)
VISITAS_RHO = (10, 250)
N_SPLITS, N_INITS = 100, 5
LR = 0.003
SEMILLAS = (1_100_000, 1_110_000, 1_120_000)
RHO_OPCIONES = dict(grid=9, starts=3, margin=1e-8, order=12, log_step=4., maxiter=40, xatol=1e-9,
                    max_evaluations=4096, seconds=60.)
WATCHDOG = 120.0
GATE_CHECKS = ('equivalencia_wine_<=1e-12', 'rho_valido_en_ambos', 'estado_cercano_al_borde_p_min<1e-3',
               'control_negativo_cabeza_completa_>1e-9', 'cnn_probabilidades_invariantes', 'cnn_M_reducida_invariante',
               'cnn_reducida_vs_completa_difieren_>1e-9', 'pca_determinista', 'pca_signo')
COLUMNAS = ('trajectory,split,k,update,estado,error,X,R,c,q,tr_M,acc_train,acc_panel,acc_test,ce_train,ce_panel,ce_test,'
            'k_star,k_star_wrong,frac_panel_wrong,rho_caras,rho_vert,rho_status,rho_reason,rho_caras_quad_error,'
            'rho_caras_prefix_bound,rho_caras_tail_bound,rho_vert_quad_error,rho_vert_prefix_bound,rho_vert_tail_bound,'
            'rho_evaluations,rho_seconds,model_sha256,f_sha256,split_sha256,diagnostic_sha256').split(',')


# ---------------------------------------------------------------- utilidades
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
        np.savez_compressed(fh, **arrays)
    return sha_archivo(path)


def versiones():
    import importlib.metadata as md
    import torch
    return {'torch': torch.__version__, 'numpy': md.version('numpy'), 'scipy': md.version('scipy'),
            'sklearn': md.version('scikit-learn')}


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


def ids_universo():
    return [f'cifar_f1_s{s:04d}_k{k}' for s in range(N_SPLITS) for k in range(N_INITS)]


# ------------------------------------------------------- ρ con watchdog externo
def _hijo_rho(entrada, salida):
    """Proceso aparte: una sola llamada a rho_borde_v2 con las opciones explícitas."""
    rho = ig.congelado('rho_v2')
    d = np.load(entrada)
    capturadas = []
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        try:
            r = rho.rho_borde_v2(d['M'], d['f'], **RHO_OPCIONES)
        except Exception:
            r = dict(status='EXCEPCION', reason=traceback.format_exc())
        capturadas = [dict(category=x.category.__name__, message=str(x.message)) for x in w]
    r = dict(r, warnings=capturadas)
    texto = json.dumps(limpiar(r), indent=1, ensure_ascii=False, allow_nan=False, sort_keys=True)
    Path(salida).write_text(texto+'\n', encoding='utf-8', newline='\n')
    return 0


def medir_rho(M, f, destino_json):
    """Devuelve (campos para la tabla, info externa). Una llamada; sin reintentos."""
    with tempfile.TemporaryDirectory(prefix='cifar_f1_rho_') as tmp:
        ent, sal = Path(tmp)/'entrada.npz', Path(tmp)/'salida.json'
        np.savez(ent, M=M, f=f)
        t0 = time.perf_counter()
        try:
            proc = subprocess.run([sys.executable, '-I', str(Path(__file__).resolve()), '--rho-hijo', str(ent), str(sal)],
                                  capture_output=True, text=True, timeout=WATCHDOG)
            pared = time.perf_counter()-t0
            if proc.returncode != 0 or not sal.exists():
                return dict(rho_status='ERROR_PROCESO_RHO', rho_reason=(proc.stderr or '')[-2000:],
                            rho_seconds=pared), dict(pared=pared)
            texto = sal.read_text(encoding='utf-8')
        except subprocess.TimeoutExpired:
            pared = time.perf_counter()-t0
            return dict(rho_status='WATCHDOG_120S', rho_reason=f'interrumpida tras {WATCHDOG:.0f} s de pared',
                        rho_seconds=pared), dict(pared=pared)
    with open(destino_json, 'x', encoding='utf-8', newline='\n') as fh:
        fh.write(texto)
    r = json.loads(texto)
    campos = dict(rho_status=r.get('status'), rho_reason=r.get('reason') or '',
                  rho_evaluations=r.get('evaluations'), rho_seconds=r.get('seconds'),
                  diagnostic_sha256=sha_archivo(destino_json))
    for k in ('rho_caras', 'rho_vert'):
        campos[k] = r.get(k)
        w = r.get(k+'_winner') or {}
        for t in ('quad_error', 'prefix_bound', 'tail_bound'):
            campos[f'{k}_{t}'] = w.get(t)
    return campos, dict(pared=pared, implementation_version=r.get('implementation_version'),
                        lengths={k: (r.get(k+'_winner') or {}).get('length') for k in ('rho_caras', 'rho_vert')})


def rho_aceptada(campos, info):
    """Criterio del diseño §4 (idéntico al productor de Q13-M2; None nunca es cero)."""
    motivos = []
    if campos.get('rho_status') != 'VALID_NUMERICAL_ESTIMATE':
        motivos.append('estado ρ: '+str(campos.get('rho_status')))
    if info.get('implementation_version') != 'r3':
        motivos.append('versión ρ distinta de r3')
    num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
    for k in ('rho_caras', 'rho_vert'):
        v = campos.get(k)
        if not (num(v) and v > 0):
            motivos.append(k+' no finita/positiva')
            continue
        t = [campos.get(f'{k}_{x}') for x in ('quad_error', 'prefix_bound', 'tail_bound')]
        if not all(num(x) and x >= 0 for x in t):
            motivos.append(k+': auditoría ausente o inválida')
        elif t[0] > 1e-6*v or t[1]+t[2] > 1e-6*v:
            motivos.append(k+': auditoría excedida')
    if not motivos and campos['rho_caras'] > campos['rho_vert']:
        motivos.append('rho_caras mayor que rho_vert')
    return motivos


# ------------------------------------------------------------- una trayectoria
def _bloque_modelo(torch, modelo, x, y):
    with torch.no_grad():
        z = modelo(x)
        ce = float(torch.nn.functional.cross_entropy(z, y))
        acc = float((z.argmax(1) == y).double().mean())
    return z, ce, acc


def _margen(torch, z, y):
    """logsumexp_{c≠y} z − logsumexp z, por ejemplo (estable, sin restar probabilidades)."""
    mask = torch.nn.functional.one_hot(y, 3).bool()
    otros = torch.logsumexp(z.masked_fill(mask, -math.inf), 1)
    return (otros-torch.logsumexp(z, 1)).numpy()


def visita(torch, modelo, d, t, xs, f, carpeta, u):
    """Mide una visita. Devuelve la fila (dict) y la información externa."""
    fila = {k: '' for k in COLUMNAS}
    fila.update(update=u, rho_status='NO_SOLICITADA' if u not in VISITAS_RHO else '')
    ext = dict(update=u)
    errores = []
    params = [p.detach().numpy() for p in modelo.parameters()]
    fila['model_sha256'] = sha_bytes(b''.join(p.tobytes() for p in params))
    try:
        zt, fila['ce_train'], fila['acc_train'] = _bloque_modelo(torch, modelo, xs['xt'], xs['yt'])
        zp, fila['ce_panel'], fila['acc_panel'] = _bloque_modelo(torch, modelo, xs['xp'], xs['yp'])
        ze, fila['ce_test'], fila['acc_test'] = _bloque_modelo(torch, modelo, xs['xe'], xs['ye'])
        mal = int((zp.argmax(1) != xs['yp']).sum())
        fila['frac_panel_wrong'] = mal/len(xs['yp'])
        marg = _margen(torch, zp, xs['yp'])
        fila['X'] = float(marg.max())
    except Exception:
        errores.append('logits: '+traceback.format_exc(limit=3))
        zp, marg = None, None
    M = None
    try:
        tg = time.perf_counter()
        M, c, q = ig.metrica(modelo.body, modelo.head, xs['xp'], xs['yp'])
        ext['t_geometria'] = time.perf_counter()-tg
        fila['c'], fila['q'], fila['tr_M'] = c, q, float(np.trace(M))
        k_star = int(np.argmax(np.diag(M)))
        fila['k_star'] = k_star
        if marg is not None:
            fila['R'] = float(marg[k_star])
            fila['k_star_wrong'] = int(int(zp[k_star].argmax()) != int(xs['yp'][k_star]))
    except Exception:
        errores.append('geometría: '+traceback.format_exc(limit=3))
    externos = dict(params=np.concatenate([p.reshape(-1) for p in params]))
    if M is not None:
        externos.update(M=M, espectro=np.linalg.eigvalsh(0.5*(M+M.T)))
    if zp is not None:
        externos.update(logits_panel=zp.numpy(), etiquetas_panel=xs['yp'].numpy())
    ext['npz_sha256'] = npz_exclusivo(carpeta/f'u{u:03d}.npz', **externos)
    metricas_ok = not errores
    if u in VISITAS_RHO:
        if M is None:
            fila['rho_status'] = 'NO_MEDIDA'
            fila['rho_reason'] = 'sin M válida'
            rho_motivos = ['sin M']
        else:
            campos, info = medir_rho(M, f, carpeta/f'u{u:03d}_rho.json')
            fila.update({k: ('' if v is None else v) for k, v in campos.items()})
            ext['rho'] = info
            rho_motivos = rho_aceptada(campos, info)
            if rho_motivos and not fila['rho_reason']:
                fila['rho_reason'] = '; '.join(rho_motivos)
        if metricas_ok and not rho_motivos:
            fila['estado'] = 'MEDIDA'
        elif metricas_ok:
            fila['estado'] = 'INVALID_RHO'
            fila['error'] = 'ρ no aceptada: '+'; '.join(rho_motivos)
        else:
            fila['estado'] = 'FALLIDA'
    else:
        fila['estado'] = 'MEDIDA' if metricas_ok else 'FALLIDA'
    if errores:
        fila['error'] = ' | '.join(errores+([fila['error']] if fila['error'] else []))
    return fila, ext


def trayectoria(d, s, k, carpeta):
    import torch
    t = f'cifar_f1_s{s:04d}_k{k}'
    s_init, s_lote = SEMILLAS[1]+5*s+k, SEMILLAS[2]+5*s+k
    t0, c0 = time.perf_counter(), time.process_time()
    xs = dict(xt=torch.tensor(d['xtr']), yt=torch.tensor(d['ytr']), xp=torch.tensor(d['xpa']),
              yp=torch.tensor(d['ypa']), xe=torch.tensor(d['xte']), ye=torch.tensor(d['yte']))
    f = d['f']
    comunes = dict(trajectory=t, split=s, k=k, f_sha256=d['f_sha256'], split_sha256=d['split_sha256'])
    filas, ext = [], dict(trajectory=t, split=s, k=k, semilla_split=SEMILLAS[0]+s, semilla_init=s_init,
                          semilla_lote=s_lote, lr=LR, visitas={})
    modelo, opt = s3.iniciar(torch, s_init, lr=LR)
    rng = np.random.default_rng(s_lote)
    ext['sha_parametros_iniciales'] = sha_bytes(b''.join(p.detach().numpy().tobytes() for p in modelo.parameters()))
    u, fallo = 0, None
    t_entr = 0.0
    for v in VISITAS:
        if fallo is None:
            try:
                ta = time.perf_counter()
                while u < v:
                    s3.paso(torch, modelo, opt, xs['xt'], xs['yt'], rng)
                    u += 1
                t_entr += time.perf_counter()-ta
            except Exception:
                fallo = f'entrenamiento interrumpido en el update {u+1}: '+traceback.format_exc(limit=3)
        if fallo is not None:
            fila = {c: '' for c in COLUMNAS}
            fila.update(comunes, update=v, estado='FALLIDA', error='visita no alcanzada: '+fallo,
                        rho_status='NO_SOLICITADA' if v not in VISITAS_RHO else 'NO_MEDIDA')
            filas.append(fila)
            ext['visitas'][f'u{v:03d}'] = dict(alcanzada=False)
            continue
        ext['visitas'][f'u{v:03d}'] = dict(estado_rng=rng.bit_generator.state)
        try:
            fila, e = visita(torch, modelo, d, t, xs, f, carpeta, v)
        except Exception:
            fila = {c: '' for c in COLUMNAS}
            fila.update(update=v, estado='FALLIDA', error='medición: '+traceback.format_exc(limit=3),
                        rho_status='NO_SOLICITADA' if v not in VISITAS_RHO else 'NO_MEDIDA')
            e = {}
        fila.update(comunes)
        filas.append(fila)
        ext['visitas'][f'u{v:03d}'].update(e)
    ext.update(t_total=time.perf_counter()-t0, cpu_total=time.process_time()-c0, t_entrenamiento=t_entr,
               memoria_pico_mb=memoria_pico_mb())
    return filas, ext


# ------------------------------------------------------------------ procesos
def _iniciar_trabajador():
    import torch
    torch.set_num_threads(1)
    ig.congelado('core')        # fija float64 por defecto, como en G3/C2
    ig.congelado('rho_v2')


def _tarea(s, pendientes, d, raiz):
    hechos = []
    for k in pendientes:
        t = f'cifar_f1_s{s:04d}_k{k}'
        carpeta = Path(raiz)/'trayectorias'/t
        carpeta.mkdir(parents=True)
        try:
            filas, ext = trayectoria(d, s, k, carpeta)
        except Exception:
            err = 'trayectoria: '+traceback.format_exc()
            filas = []
            for v in VISITAS:
                fila = {c: '' for c in COLUMNAS}
                fila.update(trajectory=t, split=s, k=k, update=v, estado='FALLIDA', error=err,
                            rho_status='NO_SOLICITADA' if v not in VISITAS_RHO else 'NO_MEDIDA')
                filas.append(fila)
            ext = dict(trajectory=t, error=err)
        json_exclusivo(carpeta/'registro.json', dict(filas=filas, externo=ext))
        hechos.append((k, [f['estado'] for f in filas]))
    return s, hechos


def preparar_split(Xtr, ytr, Xte, yte, s, raiz):
    d = s3.preparar(Xtr, ytr, Xte, yte, SEMILLAS[0]+s)
    f, V = ig.perspectivas_pca(d['xpa'])
    d['f'] = f
    d['f_sha256'] = sha_bytes(np.ascontiguousarray(f, dtype=np.float64).tobytes())
    d['split_sha256'] = sha_bytes(b''.join(np.ascontiguousarray(d[k], dtype=np.int64).tobytes()
                                           for k in ('itr', 'ipa', 'ite')))
    p = Path(raiz)/'splits'/f's{s:04d}.npz'
    if not p.exists():
        npz_exclusivo(p, itr=d['itr'], ipa=d['ipa'], ite=d['ite'], f=f, cargas=V)
    return d


# ------------------------------------------------------------------ verificación
def verificar(a, v):
    plan_p = ROOT/PLAN_REL
    if sha_archivo(plan_p) != PLAN_SHA:
        raise SystemExit('El plan congelado no coincide con su SHA publicado')
    plan = json.loads(plan_p.read_text(encoding='utf-8'))
    if plan['estado'] != 'CONGELADO':
        raise SystemExit('El plan no está CONGELADO')
    e = plan['entrenamiento']
    if (plan['n_splits'], plan['n_inits'], tuple(plan['visitas'])) != (N_SPLITS, N_INITS, VISITAS) or \
       (plan['seed_bases']['split'], plan['seed_bases']['init'], plan['seed_bases']['lote']) != SEMILLAS or \
       e['lr'] != LR or e['updates'] != s3.UPDATES or e['lote'] != s3.LOTE or tuple(e['clases']) != s3.CLASES or \
       plan['rho']['options'] != RHO_OPCIONES or plan['rho']['outer_timeout_seconds'] != WATCHDOG or \
       tuple(plan['rho']['visitas']) != VISITAS_RHO or plan['dataset_md5'] != s3.MD5_OFICIAL:
        raise SystemExit('El productor no coincide con el plan congelado')
    if hashlib.sha256('\n'.join(ids_universo()).encode()).hexdigest() != plan['ids_sha256']:
        raise SystemExit('Universo de IDs distinto del plan')
    for k, x in plan['fuentes'].items():
        if sha_archivo(ROOT/x['path']) != x['sha256']:
            raise SystemExit('Fuente modificada: '+k)
    if v != plan['versiones'] and not a.permitir_versiones:
        raise SystemExit(f'Versiones distintas de las fijadas: {v} != {plan["versiones"]}')
    g = json.loads(Path(a.compuerta).read_text(encoding='utf-8'))
    ch = g.get('checks')
    if g.get('veredicto') != 'PASA' or not isinstance(ch, dict) or set(ch) != set(GATE_CHECKS) or \
       not all(x is True for x in ch.values()) or not 0 <= g.get('peor_error_relativo', 1) <= 1e-12 or \
       g.get('fuentes') != {'core': plan['fuentes']['core']['sha256'], 'rho_v2': plan['fuentes']['rho']['sha256']}:
        raise SystemExit('La compuerta no PASA o no corresponde a las fuentes del plan')
    if any(g.get('versiones', {}).get(k) != x for k, x in plan['versiones'].items()) and not a.permitir_versiones:
        raise SystemExit('La compuerta se calculó con otras versiones')
    return plan


# ------------------------------------------------------------------ tabla final
def valor_csv(v):
    if v is None:
        return ''
    if isinstance(v, bool):
        return str(int(v))
    if isinstance(v, float):
        return repr(v) if math.isfinite(v) else ''
    return str(v)


def cerrar(out, plan, a, v, meta, t_corrida):
    regs = {}
    for t in ids_universo():
        p = out/'trayectorias'/t/'registro.json'
        regs[t] = json.loads(p.read_text(encoding='utf-8'))
    tabla = out/'cifar_f1_visitas.csv'
    buf = io.StringIO(newline='')
    w = csv.DictWriter(buf, fieldnames=COLUMNAS, lineterminator='\n')
    w.writeheader()
    estados = {str(u): {} for u in VISITAS}
    for t in ids_universo():
        filas = sorted(regs[t]['filas'], key=lambda r: int(r['update']))
        if [int(r['update']) for r in filas] != list(VISITAS):
            raise SystemExit('Registro con visitas incompletas: '+t)
        for r in filas:
            w.writerow({c: valor_csv(r.get(c)) for c in COLUMNAS})
            st = estados[str(r['update'])]
            st[r['estado']] = st.get(r['estado'], 0)+1
    with open(tabla, 'x', encoding='utf-8', newline='') as fh:
        fh.write(buf.getvalue())
    ext = [r['externo'] for r in regs.values()]
    num = [e for e in ext if 'cpu_total' in e]
    mem = [e['memoria_pico_mb'] for e in num if e.get('memoria_pico_mb')]
    med = lambda xs: float(np.median(xs)) if xs else None
    resumen = dict(
        tabla_sha256=sha_archivo(tabla), plan_sha256=PLAN_SHA, productor_sha256=sha_archivo(Path(__file__)),
        compuerta_sha256=sha_archivo(a.compuerta), dataset_sha256=meta['cifar_sha256'],
        fuentes={k: x['sha256'] for k, x in plan['fuentes'].items()}, versiones=v,
        tipo_datos='CIFAR3_DESCUBRIMIENTO', formato=FORMATO, filas=2000, trayectorias=500,
        estados_por_visita=estados, permitir_versiones=a.permitir_versiones,
        cpu_por_trayectoria_mediana=med([e['cpu_total'] for e in num]),
        pared_por_trayectoria_mediana=med([e['t_total'] for e in num]),
        rho_pared_mediana=med([vv['rho']['pared'] for e in num for vv in e['visitas'].values() if 'rho' in vv]),
        memoria_pico_mb_mediana=med(mem), memoria_pico_mb_max=max(mem, default=None),
        memoria_sin_medir=len(num)-len(mem), segundos_ultima_invocacion=t_corrida,
        nota='Operacional: sin asociaciones. El análisis lo hace analisis_F1_v2.py con el plan congelado.')
    json_exclusivo(out/'RESUMEN_F1.json', resumen)
    return resumen


def main():
    if len(sys.argv) == 4 and sys.argv[1] == '--rho-hijo':
        return _hijo_rho(sys.argv[2], sys.argv[3])
    ap = argparse.ArgumentParser()
    ap.add_argument('--cifar', required=True)
    ap.add_argument('--compuerta', required=True)
    ap.add_argument('--salida', required=True)
    ap.add_argument('--procesos', type=int, default=12)
    ap.add_argument('--permitir-versiones', action='store_true', help='solo desarrollo; queda en el resumen')
    a = ap.parse_args()
    v = versiones()
    plan = verificar(a, v)
    ig.congelado('core')
    ig.congelado('rho_v2')
    Xtr, ytr, Xte, yte, md5, sha = s3.cargar_cifar10(a.cifar)
    out = Path(a.salida)
    for sub in ('trayectorias', 'splits', 'interrumpidas'):
        (out/sub).mkdir(parents=True, exist_ok=True)
    if (out/'RESUMEN_F1.json').exists():
        raise SystemExit('La corrida ya está cerrada (RESUMEN_F1.json existe)')
    meta = dict(formato=FORMATO, plan_sha256=PLAN_SHA, productor_sha256=sha_archivo(Path(__file__)), cifar_md5=md5,
                cifar_sha256=sha, versiones=v, permitir_versiones=a.permitir_versiones,
                compuerta_sha256=sha_archivo(a.compuerta), python=platform.python_version(),
                plataforma=platform.platform(), procesos=a.procesos)
    pm = out/'meta.json'
    if pm.exists():
        previo = json.loads(pm.read_text(encoding='utf-8'))
        claves = ('formato', 'plan_sha256', 'productor_sha256', 'cifar_sha256', 'versiones', 'compuerta_sha256')
        if {k: previo.get(k) for k in claves} != {k: meta[k] for k in claves}:
            raise SystemExit('La carpeta de salida es de otra configuración; usa otra carpeta')
    else:
        json_exclusivo(pm, meta)
    # trayectorias interrumpidas: se conservan movidas y se rehacen desde cero
    for t in ids_universo():
        c = out/'trayectorias'/t
        if c.exists() and not (c/'registro.json').exists():
            marca = dt.datetime.now().strftime('%Y%m%dT%H%M%S')
            c.rename(out/'interrumpidas'/f'{t}_{marca}')
            print('interrumpida conservada y repetida desde cero:', t, flush=True)
    pend = {}
    for s in range(N_SPLITS):
        ks = [k for k in range(N_INITS) if not (out/'trayectorias'/f'cifar_f1_s{s:04d}_k{k}'/'registro.json').exists()]
        if ks:
            pend[s] = ks
    print(f'{500-sum(map(len, pend.values()))} ya escritas; {sum(map(len, pend.values()))} pendientes', flush=True)
    t0 = time.perf_counter()
    if pend:
        with cf.ProcessPoolExecutor(a.procesos, initializer=_iniciar_trabajador) as ex:
            futs = [ex.submit(_tarea, s, ks, preparar_split(Xtr, ytr, Xte, yte, s, out), str(out))
                    for s, ks in sorted(pend.items())]
            for i, fu in enumerate(cf.as_completed(futs), 1):
                s, hechos = fu.result()
                txt = ' '.join(f'k{k}:' + '/'.join(e[:3] for e in est) for k, est in hechos)
                print(f'[{i}/{len(futs)}] s{s:04d} {txt}  {time.perf_counter()-t0:.0f}s', flush=True)
    res = cerrar(out, plan, a, v, meta, time.perf_counter()-t0)
    print(json.dumps({k: res[k] for k in ('estados_por_visita', 'cpu_por_trayectoria_mediana', 'rho_pared_mediana',
                                          'memoria_pico_mb_mediana', 'memoria_sin_medir')}, indent=1, ensure_ascii=False))
    print('tabla_sha256 =', res['tabla_sha256'])
    print('productor_sha256 =', res['productor_sha256'])
    print('dataset_sha256 =', res['dataset_sha256'])
    print('compuerta_sha256 =', res['compuerta_sha256'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
