"""analisis_T2A1.py (v1) - analisis confirmatorio UNICO de T2-A1 segun fase0prima/PROTOCOLO_0c_prima_v1_CONGELADO.md.

Entradas (todas verificadas por SHA-256 antes de leer nada; si una no coincide, ABORTA sin calcular):
  --x      predictors_locked.csv de T2-A0 (X sellado; 9458086153e7...0a)
  --fase2  fase2_rho.csv (desenlaces de la fase 2; be47e118...02de)
  --u5     rho_borde_u5.csv (covariable L5; 618c263e...df2d)
  --ng     comparadores_ng_u5.csv (no geometricos del update 5; hash pasado con --ng-sha, publicado antes de abrir X). Opcional:
           si falta, esos secundarios se reportan como NO_CALCULADO.
Modo --sintetico <semilla> [--efecto r]: sustituye X por un X sintetico (no lee --x). Sirve para probar el script antes de abrir X.

Reglas fijadas en este script ANTES de abrir X (complementan la seccion 2 del protocolo, sin cambiarla):
  * Muestra: splits 12-167. Una trayectoria entra si tiene X finito y al menos una visita con rho_borde. Las que no, cuentan
    como faltantes; si los faltantes (X o Y_c) superan el 5 % de 780, el veredicto es INCONCLUSIVE.
  * Empates en X: orden lexicografico (X, init) ascendente. Empates en Y: rangos promedio.
  * Split valido: >= 3 trayectorias, X no todos iguales y Y no todos iguales.
  * Permutaciones: generador numpy default_rng(semilla); splits en orden creciente; para cada split, rng.permuted sobre una
    matriz (B, n_s) con la fila de rangos de Y repetida, eje 1.
  * W_adj: residuos de log Y_c ~ ordenada por split + beta*L5 (MCO intra-split). Freedman-Lane: se permutan los residuos dentro
    del split sin reestimar beta.
  * Secundarios (no deciden): Delta (semilla 220023); G global con bootstrap de splits (220020); Y_b con r*; comparadores
    orientados como en T2-A0 (C_A y Lambda descendente => mayor = mas riesgo; R_eff ascendente => se usa -R_eff), cada uno con
    W propio (semilla 220024+i) y W de X ajustado por L5 + comparador (semilla 220034+i).
"""
import argparse, csv, hashlib, json, math, sys, time
from pathlib import Path
import numpy as np
from scipy.stats import rankdata

SHA = dict(x="9458086153e7bedba05a3234aff0a7e5f4145c4aac595137c4866294f65ee70a",
           fase2="be47e118886627ba61252b7f7dd7793032b42482fd01c44da89efb0cbffb02de",
           u5="618c263e9e3abac651a7e8b51e7a3ec3352b8a3990c00839dfb48307a6b5df2d")
R_STAR = 0.05697156262709151
SPLITS = range(12, 168)
B = 20000
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
fnum = lambda v: float(v) if v not in (None, "", "None", "nan") and math.isfinite(float(v)) else None


def rangos_x(x, init):
    o = np.lexsort((init, x)); r = np.empty(len(x)); r[o] = np.arange(1, len(x) + 1); return r


def preparar(grupos):
    """grupos: lista de (x, init, y) por split. Devuelve lista de (rx_norm, ry_centr, ry_norm) de splits validos."""
    out = []
    for x, init, y in grupos:
        if len(x) < 3 or np.all(x == x[0]) or np.all(y == y[0]):
            continue
        rx = rangos_x(x, init); ry = rankdata(y)
        rx = rx - rx.mean(); ry = ry - ry.mean()
        out.append((rx / np.linalg.norm(rx), ry / np.linalg.norm(ry)))
    return out


def W_y_perm(grupos, semilla, b=B):
    v = preparar(grupos)
    if not v:
        return dict(W=None, p=None, splits_validos=0)
    W = float(np.mean([a @ c for a, c in v]))
    rng = np.random.default_rng(semilla); acc = np.zeros(b)
    for a, c in v:
        acc += rng.permuted(np.tile(c, (b, 1)), axis=1) @ a
    Wp = acc / len(v)
    return dict(W=W, p=float((1 + np.sum(Wp >= W - 1e-12)) / (1 + b)), splits_validos=len(v), W_nulo_q95=float(np.quantile(Wp, 0.95)))


def residuos(y, split, covs):
    """MCO de y ~ ordenada por split + covs (pendientes comunes): centrado intra-split."""
    y = y.copy(); C = np.column_stack(covs).astype(float)
    for s in np.unique(split):
        m = split == s; y[m] -= y[m].mean(); C[m] -= C[m].mean(0)
    beta = np.linalg.lstsq(C, y, rcond=None)[0]
    return y - C @ beta, beta


def por_split(split, x, init, y):
    return [(x[split == s], init[split == s], y[split == s]) for s in sorted(set(split.tolist()))]


def spearman(a, b):
    ra, rb = rankdata(a), rankdata(b); return float(np.corrcoef(ra, rb)[0, 1])


def top10(x, init, ev):
    n = len(x); k = math.ceil(0.1 * n); corte = np.sort(x)[::-1][k - 1]; t = x >= corte
    prec = float(ev[t].mean()); base = float(ev.mean())
    return dict(cola=int(t.sum()), corte_k=k, eventos_cola=int(ev[t].sum()), precision=prec, incidencia=base,
                lift=(prec / base) if base > 0 else None, eventos_total=int(ev.sum()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--x"); ap.add_argument("--fase2", required=True); ap.add_argument("--u5", required=True)
    ap.add_argument("--ng"); ap.add_argument("--ng-sha"); ap.add_argument("--out", required=True)
    ap.add_argument("--sintetico", type=int); ap.add_argument("--efecto", type=float, default=0.0)
    ap.add_argument("--B", type=int, default=B)
    a = ap.parse_args(); b = a.B; err = []
    if a.sintetico is None:
        if not a.x or sha(a.x) != SHA["x"]: err.append("X: hash no coincide o falta --x")
    if sha(a.fase2) != SHA["fase2"]: err.append("fase2_rho.csv: hash no coincide")
    if sha(a.u5) != SHA["u5"]: err.append("rho_borde_u5.csv: hash no coincide")
    if a.ng and (not a.ng_sha or sha(a.ng) != a.ng_sha): err.append("comparadores no geometricos: hash no coincide")
    if b != B and a.sintetico is None: err.append("B distinto de 20000 solo se permite en modo sintetico")
    if err:
        print(json.dumps(err, indent=2)); sys.exit("ABORTA")
    t0 = time.time()
    # desenlaces
    vis = {}
    for r in csv.DictReader(open(a.fase2, encoding="utf-8")):
        v = fnum(r["rho_borde"]) if not r.get("error") else None
        vis.setdefault(r["trajectory"], {})[int(r["update"])] = v
    u5 = {r["trajectory"]: (int(r["split"]), int(r["init"]), fnum(r["rho_borde"])) for r in csv.DictReader(open(a.u5, encoding="utf-8"))}
    trays = sorted([t for t, (s, _, _) in u5.items() if s in SPLITS], key=lambda t: (u5[t][0], u5[t][1]))
    # predictor
    status = {}
    if a.sintetico is None:
        xt = {r["trajectory"]: r for r in csv.DictReader(open(a.x, encoding="utf-8"))}
        faltan_col = [c for c in ("trajectory", "split", "init", "X", "C_A", "Lambda_01pct", "R_eff") if c not in next(iter(xt.values()))]
        if faltan_col:
            sys.exit(f"ABORTA: columnas ausentes en X: {faltan_col}")
        X = {t: fnum(xt[t]["X"]) if t in xt else None for t in trays}
        comp = {c: {t: fnum(xt[t][c]) if t in xt else None for t in trays} for c in ("C_A", "Lambda_01pct", "R_eff")}
        for t in trays:
            k = xt[t].get("predictor_status", "?") if t in xt else "AUSENTE"; status[k] = status.get(k, 0) + 1
            if t in xt and (int(xt[t]["split"]), int(xt[t]["init"])) != u5[t][:2]:
                sys.exit(f"ABORTA: split/init de {t} no coincide entre X y u5")
    else:
        # X sintetico: mezcla de ruido y -residuo verdadero (efecto) para probar potencia y signo; no lee X.
        rng = np.random.default_rng(a.sintetico)
        yc = {t: min(v for v in vis.get(t, {}).values() if v is not None) for t in trays}
        ly = np.log([yc[t] for t in trays]); sp = np.array([u5[t][0] for t in trays]); L5 = np.log([u5[t][2] for t in trays])
        e, _ = residuos(ly, sp, [L5]); e = (e - e.mean()) / e.std()
        z = -a.efecto * e + math.sqrt(max(1 - a.efecto ** 2, 0)) * rng.standard_normal(len(trays))
        X = dict(zip(trays, z.tolist())); comp = {c: {t: float(v) for t, v in zip(trays, rng.standard_normal(len(trays)))} for c in ("C_A", "Lambda_01pct", "R_eff")}
        status = {"SINTETICO": len(trays)}
    ng = {}
    if a.ng:
        nr = {r["trajectory"]: r for r in csv.DictReader(open(a.ng, encoding="utf-8"))}
        for c in ("train_loss", "train_acc", "val_acc", "weight_norm"):
            ng[c] = {t: fnum(nr[t][c]) if t in nr else None for t in trays}
    # muestra
    filas = []; falt = dict(X=0, Y_c=0)
    for t in trays:
        vv = [vis.get(t, {}).get(k) for k in (50, 150, 250)]; ok = [v for v in vv if v is not None]
        if X[t] is None: falt["X"] += 1
        if not ok: falt["Y_c"] += 1
        if X[t] is None or not ok:
            continue
        filas.append(dict(t=t, s=u5[t][0], j=u5[t][1], x=X[t], yc=min(ok), L5=math.log(u5[t][2]), vis_ok=len(ok), yb=int(min(ok) < R_STAR)))
    n_falt = len(trays) - len(filas)
    s = np.array([f["s"] for f in filas]); j = np.array([f["j"] for f in filas]); x = np.array([f["x"] for f in filas])
    ly = np.log([f["yc"] for f in filas]); L5 = np.array([f["L5"] for f in filas]); yb = np.array([f["yb"] for f in filas])
    # primario
    prim = W_y_perm(por_split(s, x, j, -ly), 220021, b)
    e, beta = residuos(ly, s, [L5])
    adj = W_y_perm(por_split(s, x, j, -e), 220022, b); adj["beta_L5"] = float(beta[0])
    inconc = []
    if prim["splits_validos"] < 120: inconc.append(f"splits validos {prim['splits_validos']} < 120")
    if n_falt > 0.05 * len(trays): inconc.append(f"faltantes {n_falt} > 5 % de {len(trays)}")
    if inconc: veredicto = "INCONCLUSIVE"
    elif prim["p"] < 0.05 and adj["p"] < 0.05: veredicto = "PASS"
    else: veredicto = "NOT_MET"
    # secundarios
    sec = {}
    sec["Delta"] = W_y_perm(por_split(s, x, j, -(ly - L5)), 220023, b)
    G = spearman(x, -ly); rng = np.random.default_rng(220020); us = np.unique(s); idx = {u: np.where(s == u)[0] for u in us}; bs = []
    for _ in range(b):
        ii = np.concatenate([idx[u] for u in rng.choice(us, len(us), replace=True)]); bs.append(spearman(x[ii], -ly[ii]))
    sec["G_global"] = dict(spearman=G, IC95=[float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))])
    sec["Y_b"] = top10(x, j, yb); sec["Y_b"]["nota"] = "Y_b=1 demuestra borde < r*; Y_b=0 no demuestra lo contrario"
    orient = dict(C_A=1, Lambda_01pct=1, R_eff=-1); sec["comparadores_geometricos"] = {}
    for i, (c, sg) in enumerate(orient.items()):
        cv = np.array([comp[c][f["t"]] if comp[c][f["t"]] is not None else np.nan for f in filas]) * sg; m = np.isfinite(cv)
        d = dict(faltantes=int((~m).sum()), orientacion="mayor = mas riesgo" if sg > 0 else "se usa -R_eff")
        if m.sum() >= 3:
            d["W_comparador"] = W_y_perm(por_split(s[m], cv[m], j[m], -ly[m]), 220024 + i, b)
            e2, _ = residuos(ly[m], s[m], [L5[m], cv[m]])
            d["W_X_ajustado_L5_y_comparador"] = W_y_perm(por_split(s[m], x[m], j[m], -e2), 220034 + i, b)
            d["spearman_X_comparador"] = spearman(x[m], cv[m])
        sec["comparadores_geometricos"][c] = d
    sec["comparadores_no_geometricos"] = "NO_CALCULADO (sin --ng)" if not ng else {}
    for i, c in enumerate(ng):
        cv = np.array([ng[c][f["t"]] if ng[c][f["t"]] is not None else np.nan for f in filas]); m = np.isfinite(cv)
        d = dict(faltantes=int((~m).sum()), orientacion="sin orientar (descriptivo, bilateral)")
        if m.sum() >= 3:
            d["W_comparador"] = W_y_perm(por_split(s[m], cv[m], j[m], -ly[m]), 220027 + i, b)
            e2, _ = residuos(ly[m], s[m], [L5[m], cv[m]])
            d["W_X_ajustado_L5_y_comparador"] = W_y_perm(por_split(s[m], x[m], j[m], -e2), 220037 + i, b)
            d["spearman_X_comparador"] = spearman(x[m], cv[m])
        sec["comparadores_no_geometricos"][c] = d
    sec["spearman_X_L5_global"] = spearman(x, L5)
    sec["visitas_con_fallo_numerico"] = int(sum(1 for t in trays for k in (50, 150, 250) if vis.get(t, {}).get(k) is None))
    res = dict(veredicto=veredicto, motivos_inconclusive=inconc, modo="SINTETICO semilla %d efecto %g" % (a.sintetico, a.efecto) if a.sintetico is not None else "CONFIRMATORIO",
               primario_W=prim, condicion_W_adj=adj, n_trayectorias=len(trays), n_analizadas=len(filas), faltantes=falt,
               predictor_status=status, secundarios=sec, permutaciones=b,
               hashes=dict(x=None if a.sintetico is not None else SHA["x"], fase2=SHA["fase2"], u5=SHA["u5"], ng=a.ng_sha, script=sha(Path(__file__))),
               segundos=round(time.time() - t0, 1), fecha=time.strftime("%Y-%m-%dT%H:%M:%S%z"))
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    nombre = "RESULTADO_T2A1.json" if a.sintetico is None else f"sintetico_s{a.sintetico}_e{a.efecto:g}.json"
    (out / nombre).write_text(json.dumps(res, indent=2, ensure_ascii=False)); print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
