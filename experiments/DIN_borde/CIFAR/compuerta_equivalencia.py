"""Compuerta de equivalencia del instrumento generalizado (plan v1 §2).

Requisito: sobre estados de WineMLP (splits 0-2; updates 0, 10, 250 y 2000,
este último cercano al borde), el instrumento generalizado reproduce R, U, M
y ρ (caras y vértices) del core congelado y de rho_borde_v2 con error
relativo <= 1e-12. Controles:
  (a) negativo: la cabeza completa (sin reducir) da un M distinto (rel > 1e-9,
      mil veces por encima de la tolerancia de equivalencia), en Wine y en la CNN;
  (b) invariancia en la CNN de CIFAR-3: sumar un vector común a las filas de la
      cabeza (y un escalar común al sesgo) no cambia las probabilidades ni el M
      reducido (rel <= 1e-12). El M completo tampoco cambia con ese
      desplazamiento (sus gradientes solo dependen de p y h); se reporta, pero
      la diferencia entre ambas parametrizaciones la detecta (a);
  (c) f por PCA es determinista e invariante a un signo global de las imágenes
      del panel salvo la convención de signo.
No usa CIFAR real: el control (b) usa imágenes sintéticas con su forma.
Uso: python compuerta_equivalencia.py --salida compuerta.json
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import instrumento_general as ig  # noqa: E402
import sistema_cifar3 as s3  # noqa: E402

TOL = 1e-12
SPLITS = (0, 1, 2)
SNAPS = (0, 10, 250, 2000)
RHO_SNAPS = (10, 250, 2000)


def rel(a, b):
    if a is None or b is None:
        return float('inf')
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    den = float(np.max(np.abs(b)))
    return float(np.max(np.abs(a-b)))/den if den > 0 else float(np.max(np.abs(a-b)))


def wine(core, torch, rho):
    filas = []
    for s in SPLITS:
        Xtr, ytr, Xva, yva = core.load_split(s)[:4]
        torch.manual_seed(1000+s)
        m = core.WineMLP().double()
        opt = torch.optim.Adam(m.parameters(), lr=core.LR)
        rng = np.random.default_rng(2000+s)
        body = torch.nn.Sequential(m.l1, torch.nn.ReLU(), m.l2, torch.nn.ReLU())
        u = 0
        for meta in SNAPS:
            while u < meta:
                ids = torch.tensor(rng.choice(len(Xtr), size=core.BATCH, replace=False), dtype=torch.long)
                opt.zero_grad()
                torch.nn.functional.cross_entropy(m(Xtr[ids]), ytr[ids]).backward()
                opt.step()
                u += 1
            Rb0, Ub0, f0 = core.make_geom_state(m, Xva, yva)
            Rb1, Ub1 = ig.make_geom_state_general(body, m.l3, Xva, yva)
            fila = dict(split=s, update=u, n_panel=len(Xva),
                        R=[rel(a, b) for a, b in zip(Rb1, Rb0)], U=[rel(a, b) for a, b in zip(Ub1, Ub0)])
            for S in ([0, 1, 2], [2], [0, 1]):
                M0 = core.subset_M(Rb0, Ub0, S).numpy()
                M1 = core.subset_M(Rb1, Ub1, S).numpy()
                fila['M_'+''.join(map(str, S))] = rel(M1, M0)
            M0 = core.subset_M(Rb0, Ub0, [0, 1, 2]).numpy()
            M1 = core.subset_M(Rb1, Ub1, [0, 1, 2]).numpy()
            Rbc, Ubc = ig.make_geom_state_general(body, m.l3, Xva, yva, reducida=False)
            fila['control_cabeza_completa'] = rel(core.subset_M(Rbc, Ubc, [0, 1, 2]).numpy(), M0)
            with torch.no_grad():
                fila['p_min_panel'] = float(torch.softmax(m(Xva), 1).min())
            if u in RHO_SNAPS:
                f = f0.numpy()
                r0, r1 = rho.rho_borde_v2(M0, f), rho.rho_borde_v2(M1, f)
                fila['rho_status'] = [r0.get('status'), r1.get('status')]
                fila['rho_caras'] = rel(r1.get('rho_caras'), r0.get('rho_caras'))
                fila['rho_vert'] = rel(r1.get('rho_vert'), r0.get('rho_vert'))
            filas.append(fila)
    return filas


def invariancia_cnn(torch):
    rng = np.random.default_rng(7)
    x = torch.tensor(rng.normal(size=(27, 3, 32, 32)))
    y = torch.tensor(np.repeat(np.arange(3), 9))
    torch.manual_seed(11)
    m = s3.red(torch)
    n_par = sum(p.numel() for p in m.parameters())
    Mr, c, q = ig.metrica(m.body, m.head, x, y)
    Mf = ig.metrica(m.body, m.head, x, y, reducida=False)[0]
    with torch.no_grad():
        p0 = torch.softmax(m(x), 1)
        a = torch.tensor(rng.normal(size=24))
        m.head.weight += a
        m.head.bias += 0.37
        p1 = torch.softmax(m(x), 1)
    Mr2 = ig.metrica(m.body, m.head, x, y)[0]
    Mf2 = ig.metrica(m.body, m.head, x, y, reducida=False)[0]
    return dict(n_parametros=n_par, c=c, q=q, probabilidades=rel(p1.numpy(), p0.numpy()),
                M_reducida=rel(Mr2, Mr), M_completa_desplazada=rel(Mf2, Mf), reducida_vs_completa=rel(Mf, Mr))


def pca():
    rng = np.random.default_rng(5)
    X = rng.normal(size=(27, 3, 32, 32))
    f1, V1 = ig.perspectivas_pca(X)
    f2, V2 = ig.perspectivas_pca(X.copy())
    f3, V3 = ig.perspectivas_pca(-X)
    return dict(determinista=rel(f2, f1), signo_global=rel(np.abs(f3), np.abs(f1)),
                suma_cargas_no_negativa=bool((V1.sum(1) >= 0).all() and (V3.sum(1) >= 0).all()),
                media=float(np.abs(f1.mean(0)).max()), desv=[float(v) for v in f1.std(0)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--salida', required=True)
    args = ap.parse_args()
    t0 = time.perf_counter()
    core = ig.congelado('core')     # fija float64 por defecto, como en G3/C2
    rho = ig.congelado('rho_v2')
    import torch
    filas = wine(core, torch, rho)
    inv = invariancia_cnn(torch)
    pc = pca()
    peor = max(max(f['R']+f['U']+[f['M_012'], f['M_2'], f['M_01']]+[f.get('rho_caras', 0), f.get('rho_vert', 0)])
               for f in filas)
    checks = {
        'equivalencia_wine_<=1e-12': peor <= TOL,
        'rho_valido_en_ambos': all(f['rho_status'] == ['VALID_NUMERICAL_ESTIMATE']*2 for f in filas if 'rho_status' in f),
        'estado_cercano_al_borde_p_min<1e-3': all(f['p_min_panel'] < 1e-3 for f in filas if f['update'] == 2000),
        'control_negativo_cabeza_completa_>1e-9': min(f['control_cabeza_completa'] for f in filas) > 1e-9,
        'cnn_probabilidades_invariantes': inv['probabilidades'] <= TOL,
        'cnn_M_reducida_invariante': inv['M_reducida'] <= TOL,
        'cnn_reducida_vs_completa_difieren_>1e-9': inv['reducida_vs_completa'] > 1e-9,
        'pca_determinista': pc['determinista'] == 0.0,
        'pca_signo': pc['signo_global'] <= TOL and pc['suma_cargas_no_negativa'],
    }
    import scipy
    import sklearn
    out = dict(compuerta='DIN-CIFAR instrumento generalizado', veredicto='PASA' if all(checks.values()) else 'NO_PASA',
               checks=checks, peor_error_relativo=peor, tolerancia=TOL, wine=filas, cnn=inv, pca=pc,
               fuentes={k: v[1] for k, v in ig.FUENTES.items()},
               versiones=dict(python=platform.python_version(), torch=torch.__version__, numpy=np.__version__,
                              scipy=scipy.__version__, sklearn=sklearn.__version__),
               segundos=time.perf_counter()-t0)
    with open(args.salida, 'x', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(out['veredicto'], f'peor_rel={peor:.3e}', f'{out["segundos"]:.1f}s')
    for k, v in checks.items():
        print(('OK  ' if v else 'FALLA ')+k)
    return 0 if out['veredicto'] == 'PASA' else 1


if __name__ == '__main__':
    sys.exit(main())
