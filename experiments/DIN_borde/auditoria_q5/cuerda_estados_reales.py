"""cuerda_estados_reales.py - auditoria descriptiva (AUDITORIA_Q5_estados_reales_2026-10-24.md). Ejecutar desde D:\\RIPG_DATA\\T2_A1.
Comprueba rho_borde >= min_S sqrt(Delta_S^T M Delta_S) sobre vertices y aristas de la envolvente de f, en los 3120 estados de D1."""
import numpy as np, csv, math
from scipy.spatial import ConvexHull
rho = {}
for r in csv.DictReader(open('DIN_borde/d1/d1_estados.csv')): rho[(r['trajectory'], int(r['update']))] = float(r['rho'])
viol = []; ratios = []; n0 = 0
for (t, k), rv in sorted(rho.items()):
    p = f'rho_u5/estados_u5/{t}.npz' if k == 5 else f'fase2/visitas/{t}/u{k}/states/{t}/state.npz'
    z = np.load(p); M = z['M'].astype(float); M = (M + M.T) / 2; f = z['f'].astype(float); n = len(f)
    V = list(ConvexHull(f).vertices); caras = [[v] for v in V] + [[V[i], V[(i + 1) % len(V)]] for i in range(len(V))]
    best = 1e300
    for S in caras:
        d = -np.ones(n) / n; d[S] += 1 / len(S); best = min(best, math.sqrt(max(d @ M @ d, 0)))
    ratios.append(rv / best); n0 += 1
    if rv < best * (1 - 1e-6): viol.append((t, k, rv, best))
ratios = np.array(ratios)
print('estados', n0, 'violaciones rho<cuerda', len(viol)); print(viol[:10])
print('rho/cuerda cuantiles', np.quantile(ratios, [0, .01, .5, .99, 1]))
