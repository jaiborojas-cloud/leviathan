"""analisis_C1.py (BORRADOR v0, no congelado) - analisis UNICO de DIN-C1 segun DISENO_DIN_C1 (seccion 5).
Entradas verificadas por SHA: --tabla c1_cohorte.csv (--tabla-sha) y --compuerta RESUMEN_c1.json de la compuerta (debe PASA=true).
Modos de prueba: --descubrimiento (acepta una tabla de los splits 12-167 en formato de cohorte; no es confirmatorio)
                 --sintetico <semilla> --efecto r (sustituye X por X sintetico).
Primaria B: W_adj = media intra-split de Spearman(X, e), e = residuos de Y ~ split + beta*L10 (MCO intra-split), Freedman-Lane,
20000 permutaciones, semilla 260001, unilateral H1: W_adj > 0. Exito p < 0.05.
X = log(1 - p_min,val(u10)); Y = log rho_borde(u250); L10 = log rho_borde(u10).
Secundaria A: W(log rho_borde(u30), Y), semilla 260002. Descriptivos: W de X sin ajuste (260003); W_adj con ajuste flexible
(Y y L10 en rangos intra-split + polinomio cubico, 260004). INCONCLUSIVE: compuerta no PASA; < 125 splits validos; > 5 % faltantes.
"""
import argparse, csv, hashlib, json, math, sys
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
fnum = lambda v: float(v) if v not in (None, "", "None", "nan") and math.isfinite(float(v)) else None


def W_perm(sp, ini, x, y, semilla, B):
    comps = []
    for s in np.unique(sp):
        m = sp == s
        if m.sum() < 3 or np.all(x[m] == x[m][0]) or np.all(y[m] == y[m][0]): continue
        o = np.lexsort((ini[m], x[m])); rx = np.empty(m.sum()); rx[o] = np.arange(1, m.sum() + 1); ry = rankdata(y[m])
        rx -= rx.mean(); ry -= ry.mean(); comps.append((rx / np.linalg.norm(rx), ry / np.linalg.norm(ry)))
    if not comps: return dict(W=None, p=None, splits_validos=0)
    W = float(np.mean([a @ b for a, b in comps])); g = np.random.default_rng(semilla); acc = np.zeros(B)
    for a, b in comps: acc += g.permuted(np.tile(b, (B, 1)), axis=1) @ a
    Wp = acc / len(comps)
    return dict(W=W, p=float((1 + np.sum(Wp >= W - 1e-12)) / (1 + B)), splits_validos=len(comps), W_nulo_q95=float(np.quantile(Wp, .95)))


def cen(v, sp):
    v = np.asarray(v, float).copy()
    for s in np.unique(sp): v[sp == s] -= v[sp == s].mean()
    return v


def resid(y, covs, sp):
    yc = cen(y, sp); C = np.column_stack([cen(c, sp) for c in covs]); b = np.linalg.lstsq(C, yc, rcond=None)[0]; return yc - C @ b, b


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tabla", required=True); ap.add_argument("--tabla-sha"); ap.add_argument("--compuerta")
    ap.add_argument("--out", required=True); ap.add_argument("--descubrimiento", action="store_true"); ap.add_argument("--sintetico", type=int)
    ap.add_argument("--efecto", type=float, default=0.0); ap.add_argument("--B", type=int, default=20000)
    a = ap.parse_args(); conf = not a.descubrimiento and a.sintetico is None; err = []
    if conf:
        if not a.tabla_sha or sha(a.tabla) != a.tabla_sha: err.append("tabla: SHA no coincide o falta --tabla-sha")
        if a.B != 20000: err.append("B debe ser 20000 en modo confirmatorio")
    if err: print(err); sys.exit("ABORTA")
    gate = json.loads(Path(a.compuerta).read_text()) if a.compuerta else {}
    filas = list(csv.DictReader(open(a.tabla, encoding="utf-8")))
    if conf and any(int(r["split"]) < 168 for r in filas): sys.exit("ABORTA: la tabla confirmatoria contiene splits < 168")
    N = len(filas); ok = [r for r in filas if not r.get("error") and all(fnum(r.get(c)) is not None for c in ("X", "rho_u10", "rho_u250"))]
    sp = np.array([int(r["split"]) for r in ok]); ini = np.array([int(r["init"]) for r in ok])
    X = np.array([float(r["X"]) for r in ok]); Y = np.log([float(r["rho_u250"]) for r in ok]); L10 = np.log([float(r["rho_u10"]) for r in ok])
    if a.sintetico is not None:
        g = np.random.default_rng(a.sintetico); e0, _ = resid(Y, [L10], sp); z = (e0 - e0.mean()) / e0.std()
        X = a.efecto * z + math.sqrt(1 - a.efecto ** 2) * g.standard_normal(len(X))
    e, b = resid(Y, [L10], sp)
    prim = W_perm(sp, ini, X, e, 260001, a.B); prim["beta_L10"] = float(b[0])
    n_splits = len(set(int(r["split"]) for r in filas)); inc = []
    if conf and not gate.get("PASA"): inc.append("compuerta de reproduccion no PASA o falta --compuerta")
    if prim["splits_validos"] < math.ceil(0.8 * n_splits): inc.append(f"splits validos {prim['splits_validos']} < 80 % de {n_splits}")
    if N - len(ok) > 0.05 * N: inc.append(f"faltantes {N - len(ok)} > 5 % de {N}")
    ver = "INCONCLUSIVE" if inc else ("PASS" if prim["p"] < 0.05 else "NOT_MET")
    sec = {}
    m30 = np.array([fnum(r.get("rho_u30")) is not None for r in ok])
    if m30.any():
        L30 = np.log([float(r["rho_u30"]) for r, k in zip(ok, m30) if k]); sec["A_W_logrho30"] = W_perm(sp[m30], ini[m30], L30, Y[m30], 260002, a.B)
    sec["W_X_sin_ajuste"] = W_perm(sp, ini, X, Y, 260003, a.B)
    ry = np.empty(len(Y)); rl = np.empty(len(Y))
    for s in np.unique(sp):
        m = sp == s; ry[m] = rankdata(Y[m]); rl[m] = rankdata(L10[m])
    ef, _ = resid(ry, [rl, rl ** 2, rl ** 3], sp); sec["W_adj_flexible_rangos_cubico"] = W_perm(sp, ini, X, ef, 260004, a.B)
    for c in ("diag_frac_u10", "diag_frac_u250"):
        v = [fnum(r.get(c)) for r in ok]; v = [x for x in v if x is not None]
        if v: sec[f"{c}_mediana"] = float(np.median(v))
    if all(fnum(r.get("k_star_u250")) is not None for r in ok) and all(r.get("k_min_u10") not in (None, "") for r in ok):
        sec["frac_kstar250_igual_kmin10"] = float(np.mean([int(r["k_star_u250"]) == int(r["k_min_u10"]) for r in ok]))
    modo = "CONFIRMATORIO" if conf else ("DESCUBRIMIENTO (no confirmatorio)" if a.descubrimiento else f"SINTETICO s{a.sintetico} r{a.efecto}")
    res = dict(veredicto=ver if conf else f"{ver} [{modo}]", motivos_inconclusive=inc, modo=modo, primaria_B=prim, secundarios=sec, n_tabla=N, n_analizadas=len(ok),
               splits=n_splits, compuerta=gate, permutaciones=a.B, tabla_sha256=sha(a.tabla), script_sha256=sha(Path(__file__)))
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    nombre = "RESULTADO_C1.json" if conf else ("descubrimiento.json" if a.descubrimiento else f"sintetico_s{a.sintetico}_r{a.efecto:g}.json")
    (out / nombre).write_text(json.dumps(res, indent=2, ensure_ascii=False)); print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
