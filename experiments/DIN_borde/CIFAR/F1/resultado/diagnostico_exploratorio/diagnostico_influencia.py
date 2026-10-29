"""DIN-CIFAR F1 — diagnóstico de influencia, EXPLORATORIO y posterior al veredicto.

No cambia el veredicto congelado de F1 (PASS_DESCRIPTIVO), no excluye trayectorias
del resultado oficial y no define ninguna regla nueva. Usa las funciones del analista
congelado (`analisis_F1_v2.py`, que a su vez usa la primaria de C1 por SHA) sobre la
tabla publicada. Uso:  python diagnostico_influencia.py ../cifar_f1_visitas.csv salida.json
"""
import csv
import json
from pathlib import Path
import sys

import numpy as np

F1 = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(F1))
import analisis_F1_v2 as A  # noqa: E402

TABLA_SHA = '34bb7503a953c9c9b9b2a61cdd34a462a2e548144e4c7665eeed309666de4934'


def oos(C, sp, X, L, Y, grado=3):
    """Errores fuera de muestra de base y completo, con los bloques de C1 (260010)."""
    fold = {s: i % 10 for i, s in enumerate(np.random.default_rng(260010).permutation(np.unique(sp)))}
    fo = np.array([fold[s] for s in sp])
    z = (L-L.mean())/L.std()
    B = np.column_stack([C.cen(z**g, sp) for g in range(1, grado+1)])
    xc, yc = C.cen(X, sp), C.cen(Y, sp)
    F = np.column_stack([B, xc])
    eb, ef = np.empty(len(Y)), np.empty(len(Y))
    for k in range(10):
        tr, te = fo != k, fo == k
        eb[te] = yc[te]-B[te]@np.linalg.lstsq(B[tr], yc[tr], rcond=None)[0]
        ef[te] = yc[te]-F[te]@np.linalg.lstsq(F[tr], yc[tr], rcond=None)[0]
    return eb, ef, fo, z


def main(tabla, salida):
    if A.sha(tabla) != TABLA_SHA:
        raise SystemExit('La tabla no es la publicada')
    rows = list(csv.DictReader(open(tabla, encoding='utf-8', newline='')))
    m = {(r['trajectory'], int(r['update'])): r for r in rows}
    ids = A.universe()
    C = A.reference()
    a = A.arrays(ids, m)
    eb, ef, fo, z = oos(C, a['sp'], a['X'], a['L'], a['Y'])
    g = eb**2-ef**2
    o = np.argsort(-g)
    cum = np.cumsum(g[o])/g.sum()
    out = dict(
        nota='EXPLORATORIO, posterior al veredicto congelado; no lo modifica.',
        D_punto=A.point(a)['D'],
        SSE_base_total=float((eb**2).sum()), ganancia_total=float(g.sum()),
        SSE_base_por_bloque=[float((eb[fo == k]**2).sum()) for k in range(10)],
        ganancia_por_bloque=[float(g[fo == k].sum()) for k in range(10)],
        fraccion_ganancia_top=dict(zip(('1', '3', '5', '10'), [float(cum[k-1]) for k in (1, 3, 5, 10)])),
        top10=[dict(trajectory=ids[i], ganancia=float(g[i]), z_L=float(z[i]), X10=float(a['X'][i]),
                    L=float(a['L'][i]), Y=float(a['Y'][i])) for i in o[:10]],
        L_cuantiles=dict(zip(('min', 'p1', 'p5', 'p50', 'p95', 'p99', 'max'),
                             np.quantile(a['L'], [0, .01, .05, .5, .95, .99, 1]).tolist())),
        z_L_max_abs=float(np.abs(z).max()))
    t = 'cifar_f1_s0009_k0'
    out['trayectoria_extrema'] = {f'u{u:03d}': {k: m[t, u][k] for k in ('c', 'q', 'acc_train', 'acc_panel', 'X',
                                                                         'rho_caras', 'rho_vert', 'model_sha256')}
                                  for u in (5, 10, 30, 250)}
    sub = [x for x in ids if x != t]
    use, _ = A.subset_ids(sub)
    b = A.arrays(use, m)
    out['sin_' + t] = dict(C.primaria(b['sp'], b['X'], b['L'], b['Y'], 3, 260001, 5000), n=len(use),
                           nota='sensibilidad exploratoria: no es el veredicto')
    loso = sorted((A.point(A.arrays([x for x in ids if int(x.split('_')[2][1:]) != s], m))['D'], s) for s in range(100))
    out['D_sin_un_split'] = dict(min=loso[:3], max=loso[-3:],
                                 nota='quitar un split cambia también la asignación de bloques')
    Path(salida).write_text(json.dumps(out, indent=1, ensure_ascii=False)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: out[k] for k in ('D_punto', 'fraccion_ganancia_top', 'z_L_max_abs')}, indent=1))
    print('sin', t, out['sin_'+t])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
