"""potencia_0c_prima.py (v3: signo del efecto corregido; v2: rangos vectorizados; v1 se detuvo por lentitud sin producir resultados) - potencia de la regla conjunta de 0c' (W y W_adj al 5 % unilateral), SIN X (X sintetico).

Modelo por split (156 splits x 5 trayectorias): L5 ~ estandarizado; log Y_c = b*L5 + u (u ~ N(0,1));
X = c*L5 + a*u + ruido, con a fijado para que la correlacion de Pearson intra-split entre X y u sea rho_X.
W = media de Spearman(X, -log Y_c) por split; W_adj = igual sobre los residuos de log Y_c ~ split + L5 (pendiente comun).
Umbral de cada prueba: cuantil 95 % de su distribucion nula por permutacion dentro del split (simulada).
Signo: en la simulacion «mayor X -> menor Y_c», asi que se usa -u. Semilla fija. Salida JSON.
"""
import json, sys
import numpy as np
from scipy.stats import rankdata

S, N, REPS, NPERM = 156, 5, 2000, 4000
rng = np.random.default_rng(220023)


def spearman_rows(A, B):   # v2: rangos vectorizados (datos continuos, sin empates); v1 era demasiado lenta
    ra = A.argsort(-1).argsort(-1).astype(float); rb = B.argsort(-1).argsort(-1).astype(float)
    ra -= ra.mean(-1, keepdims=True); rb -= rb.mean(-1, keepdims=True)
    return (ra * rb).sum(-1) / np.sqrt((ra ** 2).sum(-1) * (rb ** 2).sum(-1))


def residuos(Y, L):
    Yc = Y - Y.mean(1, keepdims=True); Lc = L - L.mean(1, keepdims=True)
    beta = (Yc * Lc).sum() / (Lc ** 2).sum()
    return Yc - beta * Lc


def W(X, Y):
    return spearman_rows(X, -Y).mean()


# nula: con X independiente de Y, W es la media de Spearman de 156 permutaciones independientes de 5
null = np.array([spearman_rows(rng.random((S, N)), rng.random((S, N))).mean() for _ in range(NPERM)])
crit = float(np.quantile(null, 0.95))
res = dict(splits=S, por_split=N, reps=REPS, umbral_W_5pct=crit, escenarios=[])
for c in (0.0, 0.5):
    for b in (0.0, 0.5):
        for rho in (0.05, 0.10, 0.15, 0.20, 0.30):
            ok = okW = okA = 0
            for _ in range(REPS):
                L = rng.normal(size=(S, N)); u = rng.normal(size=(S, N)); Y = b * L + u
                a = rho / np.sqrt(1 - rho ** 2)
                X = c * L - a * u + rng.normal(size=(S, N))   # v3: signo corregido (mayor X -> menor log Y_c); v2 usaba +u y simulaba el efecto contrario
                w = W(X, Y) > crit; wa = W(X, residuos(Y, L)) > crit
                okW += w; okA += wa; ok += (w and wa)
            res["escenarios"].append(dict(corr_X_L5=c, efecto_L5_en_Y=b, rho_X_residuo=rho, potencia_W=okW / REPS, potencia_W_adj=okA / REPS, potencia_conjunta=ok / REPS))
            print(res["escenarios"][-1], flush=True)
json.dump(res, open(sys.argv[1] if len(sys.argv) > 1 else "potencia_0c_prima.json", "w"), indent=2)
