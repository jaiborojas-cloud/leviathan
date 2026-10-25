"""d7_mecanismo.py (v1) - DIN-borde D7 exploratorio (PLAN_D7_mecanismo.md). Solo tablas publicadas d1/d3/d4/d6 (splits 12-167).
Uso (desde experiments/DIN_borde): python3 -I d7_mecanismo.py"""
import csv, json, math, sys
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
H = Path(__file__).resolve().parent
sys.path.insert(0, str(H / "C1")); import analisis_C1_v2 as A
L1m = lambda p: math.log(max(1 - p, 1e-300))
d1 = {(r["trajectory"], int(r["update"])): float(r["rho"]) for r in csv.DictReader(open(H / "d1" / "d1_estados.csv"))}
d3 = {(r["trajectory"], int(r["update"])): r for r in csv.DictReader(open(H / "d3" / "d3_estados.csv"))}
d4 = {(r["trajectory"], int(r["update"])): r for r in csv.DictReader(open(H / "d4" / "d4_estados.csv"))}
d6 = {(r["trajectory"], int(r["update"])): r for r in csv.DictReader(open(H / "d6" / "PROGRESO_d6.csv")) if not r["error"]}
T = A.universo(12, 167)
sp = np.array([int(t.split("_")[0][5:]) for t in T]); X = np.array([L1m(float(d6[(t, 10)]["p_min_val"])) for t in T])
L = np.log([float(d6[(t, 10)]["rho_borde"]) for t in T]); Y = np.log([d1[(t, 250)] for t in T])
R = np.array([L1m(float(d4[(t, 250)]["p_k_star"])) for t in T]); Mal = np.array([int(d4[(t, 250)]["k_star_mal"]) for t in T])
k250 = np.array([int(d3[(t, 250)]["k_star"]) for t in T])
res = dict(n=len(T), splits=len(set(sp.tolist())))
mismo = {}
for u in (5, 10, 20, 30, 40, 50):
    if u == 5: km = [int(d4[(t, 5)]["k_min"]) for t in T]
    elif u == 50: km = [int(d4[(t, 50)]["k_min"]) for t in T]
    else: km = [int(d6[(t, u)]["k_min"]) for t in T]
    mismo[u] = float(np.mean(np.array(km) == k250))
res["frac_kmin_t_igual_kstar_250"] = mismo
Mismo = np.array([int(d6[(t, 10)]["k_min"]) for t in T]) == k250
res["frac_mal_250"] = float(Mal.mean())
def base(Lv, spv, extra=()):
    z = (Lv - Lv.mean()) / Lv.std(); cols = [A.cen(z ** g, spv) for g in (1, 2, 3)] + [A.cen(e, spv) for e in extra]; return np.column_stack(cols)
def Dcv(spv, Xv, Lv, Yv, extra=(), B=2000, semilla=300001):
    us = np.unique(spv); perm = np.random.default_rng(260010).permutation(us); fold = {u: i % 10 for i, u in enumerate(perm)}
    fo = np.array([fold[s] for s in spv]); Yc = A.cen(Yv, spv); Bm = base(Lv, spv, extra); Xc = A.cen(Xv, spv); D = A.D_cv(Yc, Bm, Xc, fo)
    beta = float(np.linalg.lstsq(np.column_stack([Bm, Xc]), Yc, rcond=None)[0][-1]); g = np.random.default_rng(semilla); idx = [np.where(spv == s)[0] for s in us]; nul = np.empty(B)
    for b in range(B):
        Xp = Xv.copy()
        for ii in idx: Xp[ii] = Xv[g.permutation(ii)]
        nul[b] = A.D_cv(Yc, Bm, A.cen(Xp, spv), fo)
    return dict(D=D, p=float((1 + np.sum(nul >= D - 1e-15)) / (1 + B)), pendiente=beta, n=int(len(Xv)))
res["W_X_R"] = A.W_perm(sp, X, R, 300002, 2000); res["W_X_Mal"] = A.W_perm(sp, X, Mal.astype(float), 300003, 2000)
eR = A.cen(R, sp) - base(L, sp) @ np.linalg.lstsq(base(L, sp), A.cen(R, sp), rcond=None)[0]
res["W_X_R_ajustado_L10"] = A.W_perm(sp, X, eR, 300004, 2000)
res["W_R_Y"] = A.W_perm(sp, R, Y, 300005, 2000)
res["D_X"] = Dcv(sp, X, L, Y); res["D_X_dado_R"] = Dcv(sp, X, L, Y, extra=(R,), semilla=300006)
res["D_X_dado_Mal"] = Dcv(sp, X, L, Y, extra=(Mal.astype(float),), semilla=300007)
res["fraccion_mediada_por_R"] = 1 - res["D_X_dado_R"]["D"] / res["D_X"]["D"]
het = {}
for nombre, m in (("Mismo", Mismo), ("No_mismo", ~Mismo), ("Mal", Mal == 1), ("Resuelto", Mal == 0)):
    spm = sp[m]; ok = np.isin(spm, [s for s in np.unique(spm) if (spm == s).sum() >= 3]); idx = np.where(m)[0][ok]
    het[nombre] = Dcv(sp[idx], X[idx], L[idx], Y[idx], semilla=300010 + len(het)) if len(np.unique(sp[idx])) >= 10 else dict(nota="menos de 10 splits", n=int(len(idx)))
res["heterogeneidad_D_X"] = het
out = H / "d7"; out.mkdir(exist_ok=True); (out / "d7_resumen.json").write_text(json.dumps(res, indent=2)); print(json.dumps(res, indent=2))
