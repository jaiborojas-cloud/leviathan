"""Productor de F0 (factibilidad) de DIN-CIFAR, plan v1 §4.

Mide por trayectoria: c y q en cada visita; precisión en entrenamiento, panel
y test en u250; tiempos (entrenamiento, geometría por visita, una llamada a
rho_borde_v2 en u250 que SOLO se cronometra); memoria máxima del proceso.
NO guarda ni reporta X10, log(1-p_min), ρ ni M.

Uso (en el equipo del responsable):
  python f0_factibilidad.py --cifar D:\\RIPG_DATA\\cifar-10-python.tar.gz \\
      --compuerta D:\\RIPG_DATA\\DIN_CIFAR_F0\\compuerta.json \\
      --salida D:\\RIPG_DATA\\DIN_CIFAR_F0\\corrida --procesos 12

Reanudable: las trayectorias ya escritas (incluidas las fallidas) se conservan
y no se repiten. Ninguna falla se reemplaza.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import sys
import time
import traceback

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import instrumento_general as ig  # noqa: E402
import sistema_cifar3 as s3  # noqa: E402

FORMATO = 'DIN-CIFAR-F0-v1'
N_SPLITS, N_INITS = 20, 5
SEMILLA_SPLIT, SEMILLA_INIT, SEMILLA_LOTE = 1_010_000, 1_020_000, 1_030_000
VERSIONES = {'torch': '2.9.1+cpu', 'numpy': '2.3.5', 'scipy': '1.17.0', 'scikit-learn': '1.8.0'}
REPETIDAS = ((0, 0), (1, 3))   # se re-ejecutan para comprobar reproducción exacta
CODIGO = ('instrumento_general.py', 'sistema_cifar3.py', 'f0_factibilidad.py')

def sha_archivo(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def versiones():
    import importlib.metadata as md
    import torch
    v = {'torch': torch.__version__}
    for k in ('numpy', 'scipy', 'scikit-learn'):
        v[k] = md.version(k)
    return v


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
        pmc = PMC()
        pmc.cb = ctypes.sizeof(PMC)
        h = ctypes.windll.kernel32.GetCurrentProcess()
        ctypes.windll.psapi.GetProcessMemoryInfo(h, ctypes.byref(pmc), pmc.cb)
        return pmc.PeakWorkingSetSize/2**20
    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024


def _iniciar_trabajador():
    import torch
    torch.set_num_threads(1)
    ig.congelado('core')          # fija float64 por defecto, como en G3/C2
    ig.congelado('rho_v2')


def trayectoria(d, s, k):
    """Una trayectoria de F0 sobre el split preparado `d`. Devuelve el registro."""
    import torch
    rho = ig.congelado('rho_v2')
    t_cpu0, t0 = time.process_time(), time.perf_counter()
    xt, yt = torch.tensor(d['xtr']), torch.tensor(d['ytr'])
    xp, yp = torch.tensor(d['xpa']), torch.tensor(d['ypa'])
    xe, ye = torch.tensor(d['xte']), torch.tensor(d['yte'])
    f, _ = ig.perspectivas_pca(d['xpa'])
    modelo, opt = s3.iniciar(torch, SEMILLA_INIT+5*s+k)
    inicial = hashlib.sha256(b''.join(p.detach().numpy().tobytes() for p in modelo.parameters())).hexdigest()
    rng = np.random.default_rng(SEMILLA_LOTE+5*s+k)
    reg = dict(split=s, k=k, semilla_split=SEMILLA_SPLIT+s, semilla_init=SEMILLA_INIT+5*s+k,
               semilla_lote=SEMILLA_LOTE+5*s+k, sha_parametros_iniciales=inicial,
               sha_panel=hashlib.sha256(d['ipa'].tobytes()).hexdigest(),
               visitas={}, t_entrenamiento=0.0)
    u = 0
    for v in s3.VISITAS:
        ta = time.perf_counter()
        while u < v:
            s3.paso(torch, modelo, opt, xt, yt, rng)
            u += 1
        reg['t_entrenamiento'] += time.perf_counter()-ta
        tg = time.perf_counter()
        M, c, q = ig.metrica(modelo.body, modelo.head, xp, yp)
        reg['visitas'][f'u{v:03d}'] = dict(c=c, q=q, acc_panel=s3.precision(torch, modelo, xp, yp),
                                           t_geometria=time.perf_counter()-tg)
    reg['acc_train250'] = s3.precision(torch, modelo, xt, yt)
    reg['acc_panel250'] = reg['visitas']['u250']['acc_panel']
    reg['acc_test250'] = s3.precision(torch, modelo, xe, ye)
    tr = time.perf_counter()
    r = rho.rho_borde_v2(M, f)
    reg['t_rho250'] = time.perf_counter()-tr
    reg['rho250_status'] = r.get('status')        # solo el estado; el valor se descarta
    del r
    reg['sha_parametros_finales'] = hashlib.sha256(
        b''.join(p.detach().numpy().tobytes() for p in modelo.parameters())).hexdigest()
    reg['t_total'] = time.perf_counter()-t0
    reg['cpu_total'] = time.process_time()-t_cpu0
    reg['memoria_pico_mb'] = memoria_pico_mb()
    return reg


def _tarea(s, pendientes, d):
    """Las trayectorias pendientes de un split; `d` lo prepara el proceso principal."""
    hechos = []
    for k, destino in pendientes:
        try:
            reg = trayectoria(d, s, k)
            reg['estado'] = 'MEDIDA'
        except Exception:
            reg = dict(split=s, k=k, estado='FALLIDA', error=traceback.format_exc())
        with open(destino, 'x', encoding='utf-8') as fh:
            json.dump(reg, fh, indent=1)
        hechos.append((k, reg['estado']))
    return s, hechos


def resumir(regs):
    ok = [r for r in regs if r['estado'] == 'MEDIDA']
    med = lambda xs: statistics.median(xs) if xs else None
    res = dict(n=len(regs), medidas=len(ok), fallidas=len(regs)-len(ok))
    for v in s3.VISITAS:
        cs = [r['visitas'][f'u{v:03d}']['c'] for r in ok]
        qs = [r['visitas'][f'u{v:03d}']['q'] for r in ok]
        res[f'u{v:03d}'] = dict(c_mediana=med(cs), c_cuantiles=[float(x) for x in np.quantile(cs, [0, .1, .25, .5, .75, .9, 1])] if cs else None,
                                q_mediana=med(qs))
    for k in ('acc_train250', 'acc_panel250', 'acc_test250', 'cpu_total', 't_total', 't_entrenamiento',
              't_rho250', 'memoria_pico_mb'):
        res[k+'_mediana'] = med([r[k] for r in ok])
    res['cpu_total_max'] = max((r['cpu_total'] for r in ok), default=None)
    res['t_geometria_mediana'] = med([vv['t_geometria'] for r in ok for vv in r['visitas'].values()])
    res['rho250_status'] = {st: sum(r['rho250_status'] == st for r in ok) for st in sorted({r['rho250_status'] for r in ok})}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cifar', required=True)
    ap.add_argument('--compuerta', required=True, help='JSON de compuerta_equivalencia.py con veredicto PASA')
    ap.add_argument('--salida', required=True)
    ap.add_argument('--procesos', type=int, default=12)
    ap.add_argument('--permitir-versiones', action='store_true', help='solo desarrollo: queda registrado')
    a = ap.parse_args()

    v = versiones()
    if v != VERSIONES and not a.permitir_versiones:
        raise SystemExit(f'Versiones distintas de las fijadas: {v} != {VERSIONES}')
    comp = json.loads(Path(a.compuerta).read_text(encoding='utf-8'))
    if comp.get('veredicto') != 'PASA' or comp.get('fuentes') != {k: x[1] for k, x in ig.FUENTES.items()}:
        raise SystemExit('La compuerta no PASA o se calculó con otras fuentes')
    ig.congelado('core')
    ig.congelado('rho_v2')
    Xtr, ytr, Xte, yte, md5, sha = s3.cargar_cifar10(a.cifar)
    out = Path(a.salida)
    (out/'trayectorias').mkdir(parents=True, exist_ok=True)
    meta = dict(formato=FORMATO, cifar_md5=md5, cifar_sha256=sha, versiones=v, versiones_fijadas=VERSIONES,
                permitir_versiones=a.permitir_versiones, compuerta_sha256=sha_archivo(a.compuerta),
                codigo={n: sha_archivo(AQUI/n) for n in CODIGO}, fuentes={k: x[1] for k, x in ig.FUENTES.items()},
                python=platform.python_version(), plataforma=platform.platform(), procesos=a.procesos,
                cpu=platform.processor())
    pm = out/'meta.json'
    if pm.exists():
        previo = json.loads(pm.read_text(encoding='utf-8'))
        if {k: previo.get(k) for k in ('formato', 'cifar_sha256', 'codigo', 'fuentes', 'versiones')} != \
           {k: meta[k] for k in ('formato', 'cifar_sha256', 'codigo', 'fuentes', 'versiones')}:
            raise SystemExit('La carpeta de salida es de otra configuración; usa otra carpeta')
    else:
        pm.write_text(json.dumps(meta, indent=1), encoding='utf-8')

    tareas = [(s, k, str(out/'trayectorias'/f's{s:02d}_k{k}.json')) for s in range(N_SPLITS) for k in range(N_INITS)]
    pend = [t for t in tareas if not Path(t[2]).exists()]
    print(f'{len(tareas)-len(pend)} ya escritas; {len(pend)} pendientes', flush=True)
    t0 = time.perf_counter()
    por_split = {}
    for s, k, destino in pend:
        por_split.setdefault(s, []).append((k, destino))
    with cf.ProcessPoolExecutor(a.procesos, initializer=_iniciar_trabajador) as ex:
        futs = [ex.submit(_tarea, s, items, s3.preparar(Xtr, ytr, Xte, yte, SEMILLA_SPLIT+s))
                for s, items in sorted(por_split.items())]
        for fu in cf.as_completed(futs):
            s, hechos = fu.result()
            print(f's{s:02d} ' + ' '.join(f'k{k}:{st}' for k, st in hechos) + f'  {time.perf_counter()-t0:.0f}s',
                  flush=True)

    regs = [json.loads(Path(t[2]).read_text(encoding='utf-8')) for t in tareas]
    # reproducción exacta: se re-ejecutan dos trayectorias en este proceso
    _iniciar_trabajador()
    repro = []
    for s, k in REPETIDAS:
        orig = regs[s*N_INITS+k]
        if orig['estado'] != 'MEDIDA':
            repro.append(dict(split=s, k=k, identica=None, nota='original fallida'))
            continue
        nuevo = trayectoria(s3.preparar(Xtr, ytr, Xte, yte, SEMILLA_SPLIT+s), s, k)
        campos = lambda r: ([r['sha_parametros_iniciales'], r['sha_parametros_finales'], r['acc_test250']] +
                            [(x['c'], x['q'], x['acc_panel']) for x in r['visitas'].values()])
        repro.append(dict(split=s, k=k, identica=campos(nuevo) == campos(orig)))
    res = resumir(regs)
    res['reproduccion'] = repro
    regla = dict(
        acc_panel250_mediana_ge_055=res['acc_panel250_mediana'] is not None and res['acc_panel250_mediana'] >= .55,
        c250_mediana_en_030_097=res['u250']['c_mediana'] is not None and .30 <= res['u250']['c_mediana'] <= .97,
        cpu_por_trayectoria_mediana_le_60s=res['cpu_total_mediana'] is not None and res['cpu_total_mediana'] <= 60,
        compuerta_pasa=True,
        reproduccion_exacta=all(r['identica'] for r in repro))
    res['regla_descriptiva_F1'] = regla
    res['nota'] = 'Descriptivo: el responsable decide si se pasa a F1 (plan v1 §4).'
    with open(out/'resumen_F0.json', 'w', encoding='utf-8') as fh:
        json.dump(res, fh, indent=1)
    with open(out/'tabla_F0.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        cols = ['split', 'k', 'estado'] + [f'{m}_u{v:03d}' for v in s3.VISITAS for m in ('c', 'q', 'acc_panel')] + \
               ['acc_train250', 'acc_test250', 'cpu_total', 't_rho250', 'rho250_status', 'memoria_pico_mb']
        w.writerow(cols)
        for r in regs:
            fila = [r['split'], r['k'], r['estado']]
            if r['estado'] == 'MEDIDA':
                fila += [r['visitas'][f'u{v:03d}'][m] for v in s3.VISITAS for m in ('c', 'q', 'acc_panel')]
                fila += [r['acc_train250'], r['acc_test250'], r['cpu_total'], r['t_rho250'], r['rho250_status'],
                         r['memoria_pico_mb']]
            w.writerow(fila)
    print(json.dumps({k: res[k] for k in ('medidas', 'fallidas', 'acc_panel250_mediana', 'cpu_total_mediana',
                                          'memoria_pico_mb_mediana')}, indent=1))
    print('c250:', res['u250']['c_cuantiles'])
    for k, x in regla.items():
        print(('OK  ' if x else 'NO  ')+k)
    return 0


if __name__ == '__main__':
    sys.exit(main())
