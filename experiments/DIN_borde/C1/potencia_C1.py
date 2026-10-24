"""potencia_C1.py (v1) - potencia simulada de la primaria B de DIN-C1 con datos de descubrimiento (d6 + d1; splits 12-167).
Modelo: e = residuo de log rho(250) ~ split + log rho(10). X sintetico = r*z(e) + sqrt(1-r^2)*ruido, con r calibrado para un W_adj
esperado objetivo. Cohorte nueva simulada remuestreando splits completos (con reemplazo). Prueba: W_adj unilateral, permutacion
dentro del split de residuos (Freedman-Lane), umbral nulo estimado por simulacion. Uso: python3 -I potencia_C1.py"""
import csv, json, math
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
H = Path(__file__).resolve().parent.parent
rho = {(r["trajectory"], int(r["update"])): float(r["rho"]) for r in csv.DictReader(open(H / "d1" / "d1_estados.csv"))}
d6 = {(r["trajectory"], int(r["update"])): r for r in csv.DictReader(open(H / "d6" / "PROGRESO_d6.csv")) if not r["error"]}
trays = sorted({t for t, k in d6})
sp = np.array([int(t.split("_")[0][5:]) for t in trays]); Y = np.log([rho[(t, 250)] for t in trays]); L10 = np.log([float(d6[(t, 10)]["rho_borde"]) for t in trays])
def cen(v, s):
    v = v.copy()
    for u in np.unique(s): v[s == u] -= v[s == u].mean()
    return v
def resid(y, l, s):
    yc, lc = cen(y, s), cen(l, s); return yc - (lc @ yc) / (lc @ lc) * lc
def Wstat(x, e, s):
    out = []
    for u in np.unique(s):
        m = s == u
        if m.sum() < 3: continue
        rx = rankdata(x[m]); ry = rankdata(e[m]); rx -= rx.mean(); ry -= ry.mean()
        if np.linalg.norm(ry) == 0: continue
        out.append(rx @ ry / np.linalg.norm(rx) / np.linalg.norm(ry))
    return np.mean(out)
rng = np.random.default_rng(250001); usp = np.unique(sp); idx = {u: np.where(sp == u)[0] for u in usp}
res = {}
for S in (100, 156, 200):
    # umbral nulo: W con X independiente (equivale a permutar), 2000 replicas
    nul = []
    for _ in range(2000):
        ch = rng.choice(usp, S); ii = np.concatenate([idx[u] for u in ch]); s2 = np.repeat(np.arange(S), [len(idx[u]) for u in ch])
        e = resid(Y[ii], L10[ii], s2); nul.append(Wstat(rng.standard_normal(len(ii)), e, s2))
    thr = float(np.quantile(nul, 0.95)); res[S] = dict(umbral_W_nulo_95=thr, potencia={})
    for r in (0.12, 0.15, 0.18, 0.22, 0.30):
        hits = []; Ws = []
        for _ in range(1000):
            ch = rng.choice(usp, S); ii = np.concatenate([idx[u] for u in ch]); s2 = np.repeat(np.arange(S), [len(idx[u]) for u in ch])
            e = resid(Y[ii], L10[ii], s2); z = (e - e.mean()) / e.std()
            x = r * z + math.sqrt(1 - r * r) * rng.standard_normal(len(ii)); W = Wstat(x, e, s2); Ws.append(W); hits.append(W > thr)
        res[S]["potencia"][f"r={r}"] = dict(W_medio=float(np.mean(Ws)), potencia=float(np.mean(hits)))
    print(S, json.dumps(res[S]), flush=True)
(Path(__file__).parent / "potencia_C1.json").write_text(json.dumps(res, indent=2))
