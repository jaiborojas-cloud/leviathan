"""analisis_C1_v1.py (BORRADOR v1, no congelado) - analisis UNICO de DIN-C1, diseno v2 (primaria por incremento predictivo).
Sustituye a analisis_C1.py v0 (que se conserva) tras la revision D2b (PR #74): el residuo lineal + Spearman no identifica
informacion mas alla de L10.

Entradas: --tabla c1_cohorte.csv (SHA con --tabla-sha) y --compuerta RESUMEN_c1.json (PASA=true).
Variables: X = log(1 - p_min,val(u10)) (logsumexp); L = log rho_borde(u10); Y = log rho_borde(u250).
PRIMARIA (incremento predictivo fuera de muestra):
  todo centrado dentro del split (equivale a ordenadas por split). Base: Yc ~ [z, z^2, z^3]c, z = (L - media)/de de la cohorte.
  Completo: base + Xc (pendiente comun). 10 bloques de splits (asignacion: default_rng(260010).permutation de los splits, bloque
  = posicion mod 10). Estadistico D = 1 - SSE_completo/SSE_base, sumando los errores de prediccion de cada bloque con modelos
  ajustados en los otros 9. Nulo: permutar X dentro de cada split (default_rng(260001)), 5000 permutaciones, recalculando D.
  p = (1 + #{D_perm >= D}) / (1 + 5000). PASS si p < 0.05 Y la pendiente de X ajustada en toda la cohorte es > 0.
SECUNDARIOS (no deciden): W_adj lineal-rangos (definicion v0, semilla 260002, afirmacion acotada a ese estimando); W_adj con
ajuste flexible por rangos (260003); W de log rho(30) frente a Y (260004); D con base de 5 terminos (z..z^5) (260005);
auditoria de precision de rho(10) (columna rho_u10_alta) y cota de cuerda.
INCONCLUSIVE: compuerta no PASA; < 80 % de splits con >= 3 trayectorias completas; > 5 % de trayectorias con faltantes.
Empates: rangos promedio; split sin variacion en X o Y se excluye del W y se cuenta.
Modos de prueba: --descubrimiento (splits 12-167); --control <nombre> (controles negativos/positivos sinteticos).
"""
import argparse, csv, hashlib, json, math, sys
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
fnum = lambda v: float(v) if v not in (None, "", "None", "nan") and math.isfinite(float(v)) else None
CONTROLES = ("X_igual_L", "X_cubica_L", "Y_g_L", "X_constante", "L_con_error", "incremento_real", "nulo_ruido")


def cen(v, sp):
    v = np.asarray(v, float).copy()
    for s in np.unique(sp): v[sp == s] -= v[sp == s].mean()
    return v


def base_mat(L, sp, grado):
    z = (L - L.mean()) / L.std(); return np.column_stack([cen(z ** g, sp) for g in range(1, grado + 1)])


def D_cv(Yc, Bm, Xc, fo):
    sb = sf = 0.0; C = np.column_stack([Bm, Xc])
    for k in range(10):
        tr, te = fo != k, fo == k
        bb = np.linalg.lstsq(Bm[tr], Yc[tr], rcond=None)[0]; bf = np.linalg.lstsq(C[tr], Yc[tr], rcond=None)[0]
        sb += float(((Yc[te] - Bm[te] @ bb) ** 2).sum()); sf += float(((Yc[te] - C[te] @ bf) ** 2).sum())
    return 1 - sf / sb


def primaria(sp, X, L, Y, grado, semilla, B):
    us = np.unique(sp); perm = np.random.default_rng(260010).permutation(us); fold = {u: i % 10 for i, u in enumerate(perm)}
    fo = np.array([fold[s] for s in sp]); Yc = cen(Y, sp); Bm = base_mat(L, sp, grado); Xc = cen(X, sp)
    if np.allclose(Xc, 0): return dict(D=None, p=None, pendiente_X=None, nota="X sin variacion dentro de los splits: NO_IDENTIFICABLE")
    D = D_cv(Yc, Bm, Xc, fo); beta = float(np.linalg.lstsq(np.column_stack([Bm, Xc]), Yc, rcond=None)[0][-1])
    g = np.random.default_rng(semilla); idx = [np.where(sp == s)[0] for s in us]; nul = np.empty(B)
    for b in range(B):
        Xp = X.copy()
        for ii in idx: Xp[ii] = X[g.permutation(ii)]
        nul[b] = D_cv(Yc, Bm, cen(Xp, sp), fo)
    return dict(D=D, p=float((1 + np.sum(nul >= D - 1e-15)) / (1 + B)), D_nulo_q95=float(np.quantile(nul, .95)), pendiente_X=beta, grado_base=grado)


def W_perm(sp, x, y, semilla, B):
    comps = []; sin_var = 0
    for s in np.unique(sp):
        m = sp == s
        if m.sum() < 3: continue
        if np.ptp(x[m]) == 0 or np.ptp(y[m]) == 0: sin_var += 1; continue
        rx = rankdata(x[m]); ry = rankdata(y[m]); rx -= rx.mean(); ry -= ry.mean(); comps.append((rx / np.linalg.norm(rx), ry / np.linalg.norm(ry)))
    if not comps: return dict(W=None, p=None, splits_validos=0, splits_sin_variacion=sin_var)
    W = float(np.mean([a @ b for a, b in comps])); g = np.random.default_rng(semilla); acc = np.zeros(B)
    for a, b in comps: acc += g.permuted(np.tile(b, (B, 1)), axis=1) @ a
    Wp = acc / len(comps); return dict(W=W, p=float((1 + np.sum(Wp >= W - 1e-12)) / (1 + B)), splits_validos=len(comps), splits_sin_variacion=sin_var)


def resid(y, covs, sp):
    yc = cen(y, sp); C = np.column_stack([cen(c, sp) for c in covs]); return yc - C @ np.linalg.lstsq(C, yc, rcond=None)[0]


def aplicar_control(nombre, sp, X, L, Y, g, r=0.3):
    zL = (L - L.mean()) / L.std(); Bm = base_mat(L, sp, 3); Yc = cen(Y, sp); e = Yc - Bm @ np.linalg.lstsq(Bm, Yc, rcond=None)[0]   # residuo intra-split
    if nombre == "X_igual_L": return L.copy(), L, Y
    if nombre == "X_cubica_L": return zL ** 3 - 2 * zL, L, Y
    if nombre == "Y_g_L": return L - 2, L, -(zL ** 2) + 0.05 * g.standard_normal(len(L))
    if nombre == "X_constante": return np.zeros(len(L)), L, Y
    if nombre == "L_con_error":          # L observado = latente + error; X mide el latente; Y depende solo del latente
        lat = L.copy(); zl = cen((lat - lat.mean()) / lat.std(), sp); Y2 = Y + 3 * zl * cen(Y, sp).std()
        return lat, lat + 0.5 * lat.std() * g.standard_normal(len(L)), Y2
    if nombre == "incremento_real": z = e / e.std(); return r * z + math.sqrt(1 - r * r) * g.standard_normal(len(L)), L, Y
    if nombre == "nulo_ruido": return g.standard_normal(len(L)), L, Y
    raise SystemExit("control desconocido")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tabla", required=True); ap.add_argument("--tabla-sha"); ap.add_argument("--compuerta")
    ap.add_argument("--out", required=True); ap.add_argument("--descubrimiento", action="store_true"); ap.add_argument("--control", choices=CONTROLES)
    ap.add_argument("--semilla-control", type=int, default=1); ap.add_argument("--r-control", type=float, default=0.3); ap.add_argument("--B", type=int, default=5000); ap.add_argument("--BW", type=int, default=20000)
    a = ap.parse_args(); conf = not a.descubrimiento and a.control is None
    if conf and (not a.tabla_sha or sha(a.tabla) != a.tabla_sha): sys.exit("ABORTA: SHA de la tabla")
    if conf and (a.B != 5000 or a.BW != 20000): sys.exit("ABORTA: permutaciones distintas de las congeladas")
    gate = json.loads(Path(a.compuerta).read_text()) if a.compuerta else {}
    filas = list(csv.DictReader(open(a.tabla, encoding="utf-8")))
    if conf and any(int(r["split"]) < 168 for r in filas): sys.exit("ABORTA: splits < 168 en modo confirmatorio")
    N = len(filas); ok = [r for r in filas if not r.get("error") and all(fnum(r.get(c)) is not None for c in ("X", "rho_u10", "rho_u250"))]
    sp = np.array([int(r["split"]) for r in ok]); X = np.array([float(r["X"]) for r in ok])
    L = np.log([float(r["rho_u10"]) for r in ok]); Y = np.log([float(r["rho_u250"]) for r in ok])
    if a.control: X, L, Y = aplicar_control(a.control, sp, X, L, Y, np.random.default_rng(a.semilla_control), a.r_control)
    cuenta = {s: int((sp == s).sum()) for s in np.unique(sp)}; validos = [s for s, c in cuenta.items() if c >= 3]
    m = np.isin(sp, validos); sp, X, L, Y = sp[m], X[m], L[m], Y[m]; n_splits = len(set(int(r["split"]) for r in filas))
    prim = primaria(sp, X, L, Y, 3, 260001, a.B)
    inc = []
    if conf and not gate.get("PASA"): inc.append("compuerta de reproduccion no PASA o falta --compuerta")
    if len(validos) < math.ceil(0.8 * n_splits): inc.append(f"splits validos {len(validos)} < 80 % de {n_splits}")
    if N - len(ok) > 0.05 * N: inc.append(f"faltantes {N - len(ok)} > 5 % de {N}")
    if prim["D"] is None: ver = "INCONCLUSIVE"; inc.append(prim["nota"])
    else: ver = "INCONCLUSIVE" if inc else ("PASS" if prim["p"] < 0.05 and prim["pendiente_X"] > 0 else "NOT_MET")
    sec = dict(W_adj_lineal_rangos=W_perm(sp, X, resid(Y, [L], sp), 260002, a.BW))
    ry = np.empty(len(Y)); rl = np.empty(len(Y))
    for s in np.unique(sp):
        k = sp == s; ry[k] = rankdata(Y[k]); rl[k] = rankdata(L[k])
    sec["W_adj_flexible_rangos"] = W_perm(sp, X, resid(ry, [rl, rl ** 2, rl ** 3], sp), 260003, a.BW)
    if not a.control:
        ok2 = [r for r in ok if int(r["split"]) in validos]; m30 = np.array([fnum(r.get("rho_u30")) is not None for r in ok2])
        if m30.all(): sec["A_W_logrho30"] = W_perm(sp, np.log([float(r["rho_u30"]) for r in ok2]), Y, 260004, a.BW)
        aud = [(float(r["rho_u10"]), float(r["rho_u10_alta"])) for r in ok2 if fnum(r.get("rho_u10_alta")) is not None]
        if aud: d = np.array([abs(x - y) / y for x, y in aud]); sec["auditoria_rho10"] = dict(n=len(aud), dif_rel_max=float(d.max()), dif_rel_mediana=float(np.median(d)))
        cu = [(float(r["rho_u10"]), float(r["cuerda_u10"])) for r in ok2 if fnum(r.get("cuerda_u10")) is not None]
        if cu: sec["cuerda_u10"] = dict(n=len(cu), violaciones=int(sum(x < y * (1 - 1e-6) for x, y in cu)))
    sec["D_base_grado5"] = primaria(sp, X, L, Y, 5, 260005, min(a.B, 2000))
    modo = "CONFIRMATORIO" if conf else ("DESCUBRIMIENTO" if a.descubrimiento else f"CONTROL {a.control} s{a.semilla_control}")
    res = dict(veredicto=ver if conf else f"{ver} [{modo}]", motivos_inconclusive=inc, modo=modo, primaria=prim, secundarios=sec, n_tabla=N,
               n_analizadas=int(len(sp)), splits=n_splits, splits_validos=len(validos), compuerta=gate, tabla_sha256=sha(a.tabla), script_sha256=sha(Path(__file__)))
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    nombre = "RESULTADO_C1.json" if conf else ("descubrimiento.json" if a.descubrimiento else f"control_{a.control}_s{a.semilla_control}_r{a.r_control:g}.json")
    (out / nombre).write_text(json.dumps(res, indent=2, ensure_ascii=False)); print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
