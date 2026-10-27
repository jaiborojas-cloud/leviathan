"""analisis_C1_v2.py (BORRADOR v2, no congelado) - analisis UNICO de DIN-C1 (diseno v3). Sustituye a analisis_C1_v1.py (que se
conserva) tras la auditoria independiente D2c (PR #76): D01 universo planificado y unicidad; D02 dominio antes del log; D03
degeneraciones sin crash; compuerta vinculada por SHA del script de cohorte; PASS exige ademas D > 0.

Universo planificado (constante): splits 168..323 x k=0..4, init j = 5 + 5(s-8) + k, ID split{s}_j{j}_true (780 IDs, 156 splits).
En --descubrimiento el universo es splits 12..167 (misma regla). La tabla debe contener SOLO IDs del universo y sin duplicados
(si no: ABORTA, sin resultado). Faltante = ID planificado ausente, con error, o con X/rho no validos (rho > 0 y finita; X finita).
Entradas confirmatorias: --tabla c1_cohorte.csv + --tabla-sha; --resumen-cohorte RESUMEN_c1.json (modo cohorte; su tabla_sha256
debe coincidir con la tabla); --compuerta RESUMEN_c1.json (modo compuerta; PASA is True y script_sha256 igual al de la cohorte).
Variables: X = log(1 - p_min,val(u10)) (logsumexp, columna X); L = log rho_borde(u10); Y = log rho_borde(u250).
PRIMARIA D: todo centrado dentro del split; z = (L - media)/de; base Yc ~ [z, z^2, z^3]c; completo = base + Xc; 10 bloques de
splits (default_rng(260010).permutation de los splits analizados; bloque = posicion mod 10); D = 1 - SSE_completo/SSE_base fuera de
muestra; nulo: X permutada dentro del split (default_rng(260001)), 5000 permutaciones, D recalculado; p = (1 + #{D_perm >= D - 1e-15})
/ (1 + 5000) (holgura 1e-15 solo para empates de punto flotante). PASS si p < 0.05, D > 0 y pendiente de X (ajuste completo) > 0.
Alcance: un PASS dice que X mejora a esa base cubica concreta de L; no prueba informacion condicional nueva sobre toda funcion de L.
INCONCLUSIVE (se evalua ANTES de calcular): compuerta no valida; faltantes > 5 % de 780 (39 permitidos, 40 no); splits con >= 3
trayectorias validas < 80 % de 156; X sin variacion intra-split (atol 1e-8); L sin variacion; SSE_base = 0 o fallo de ajuste.
Secundarios (no deciden; None si no definidos): W_adj lineal-rangos (260002, 20000), W_adj flexible por rangos (260003), A: W de
log rho(30) (260004), D con base de grado 5 (260005, 2000 permutaciones), auditoria rho(10) y cota de cuerda con caras completas.
"""
import argparse, csv, hashlib, json, math, sys
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def fnum(v):
    try: x = float(v)
    except (TypeError, ValueError): return None
    return x if math.isfinite(x) else None


def pos(v):
    x = fnum(v); return x if (x is not None and x > 0) else None


def universo(desde, hasta):
    return [f"split{s}_j{5 + 5 * (s - 8) + k}_true" for s in range(desde, hasta + 1) for k in range(5)]


def cen(v, sp):
    v = np.asarray(v, float).copy()
    for s in np.unique(sp): v[sp == s] -= v[sp == s].mean()
    return v


def D_cv(Yc, Bm, Xc, fo):
    sb = sf = 0.0; C = np.column_stack([Bm, Xc])
    for k in range(10):
        tr, te = fo != k, fo == k
        bb = np.linalg.lstsq(Bm[tr], Yc[tr], rcond=None)[0]; bf = np.linalg.lstsq(C[tr], Yc[tr], rcond=None)[0]
        sb += float(((Yc[te] - Bm[te] @ bb) ** 2).sum()); sf += float(((Yc[te] - C[te] @ bf) ** 2).sum())
    if sb <= 0: raise FloatingPointError("SSE_base = 0")
    return 1 - sf / sb


def primaria(sp, X, L, Y, grado, semilla, B):
    us = np.unique(sp); perm = np.random.default_rng(260010).permutation(us); fold = {u: i % 10 for i, u in enumerate(perm)}
    fo = np.array([fold[s] for s in sp]); Yc = cen(Y, sp); z = (L - L.mean()) / L.std(); Bm = np.column_stack([cen(z ** g, sp) for g in range(1, grado + 1)])
    Xc = cen(X, sp); D = D_cv(Yc, Bm, Xc, fo); beta = float(np.linalg.lstsq(np.column_stack([Bm, Xc]), Yc, rcond=None)[0][-1])
    g = np.random.default_rng(semilla); idx = [np.where(sp == s)[0] for s in us]; nul = np.empty(B)
    for b in range(B):
        Xp = X.copy()
        for ii in idx: Xp[ii] = X[g.permutation(ii)]
        nul[b] = D_cv(Yc, Bm, cen(Xp, sp), fo)
    return dict(D=D, p=float((1 + np.sum(nul >= D - 1e-15)) / (1 + B)), D_nulo_q95=float(np.quantile(nul, .95)), pendiente_X=beta, grado_base=grado, permutaciones=B)


def W_perm(sp, x, y, semilla, B):
    comps = []; sin_var = 0
    for s in np.unique(sp):
        m = sp == s
        if m.sum() < 3: continue
        if np.ptp(x[m]) == 0 or np.ptp(y[m]) == 0: sin_var += 1; continue
        rx = rankdata(x[m]); ry = rankdata(y[m]); rx -= rx.mean(); ry -= ry.mean(); comps.append((rx / np.linalg.norm(rx), ry / np.linalg.norm(ry)))
    if not comps: return dict(W=None, p=None, splits_validos=0, splits_sin_variacion=sin_var, nota="no definido")
    W = float(np.mean([a @ b for a, b in comps])); g = np.random.default_rng(semilla); acc = np.zeros(B)
    for a, b in comps: acc += g.permuted(np.tile(b, (B, 1)), axis=1) @ a
    Wp = acc / len(comps); return dict(W=W, p=float((1 + np.sum(Wp >= W - 1e-12)) / (1 + B)), splits_validos=len(comps), splits_sin_variacion=sin_var)


def resid(y, covs, sp):
    yc = cen(y, sp); C = np.column_stack([cen(c, sp) for c in covs]); return yc - C @ np.linalg.lstsq(C, yc, rcond=None)[0]


def seguro(f, *a):
    try: return f(*a)
    except Exception as e: return dict(nota=f"no definido: {type(e).__name__}: {e}"[:200])


def analizar(filas, plan, gate_ok, gate_nota, B, BW, transformar=None):
    """Nucleo sin E/S. filas: dicts de la tabla. plan: lista de IDs planificados. Devuelve el dict de resultado."""
    ids = [r.get("trajectory") for r in filas]
    if len(ids) != len(set(ids)): raise SystemExit("ABORTA: IDs duplicados en la tabla")
    extra = set(ids) - set(plan)
    if extra: raise SystemExit(f"ABORTA: {len(extra)} IDs fuera del universo planificado (p.ej. {sorted(extra)[:3]})")
    por = {r["trajectory"]: r for r in filas}; N = len(plan); validas = []; motivos_falta = {}
    for t in plan:
        r = por.get(t)
        if r is None: motivos_falta[t] = "ausente"; continue
        if r.get("error"): motivos_falta[t] = "error"; continue
        if fnum(r.get("X")) is None or pos(r.get("rho_u10")) is None or pos(r.get("rho_u250")) is None: motivos_falta[t] = "dominio"; continue
        validas.append(r)
    sp = np.array([int(t.split("_")[0][5:]) for t in (r["trajectory"] for r in validas)], int)
    X = np.array([float(r["X"]) for r in validas]); L = np.log([float(r["rho_u10"]) for r in validas]) if validas else np.array([])
    Y = np.log([float(r["rho_u250"]) for r in validas]) if validas else np.array([])
    if transformar is not None and len(validas): X, L, Y = transformar(sp, X, L, Y)
    splits_plan = sorted({int(t.split("_")[0][5:]) for t in plan}); cuenta = {s: int((sp == s).sum()) for s in splits_plan}
    sv = [s for s in splits_plan if cuenta[s] >= 3]; m = np.isin(sp, sv); sp, X, L, Y = sp[m], X[m], L[m], Y[m]
    nfal = len(motivos_falta); inc = []
    if not gate_ok: inc.append(gate_nota)
    if nfal > 0.05 * N: inc.append(f"faltantes {nfal} > 5 % de {N}")
    if len(sv) < math.ceil(0.8 * len(splits_plan)): inc.append(f"splits validos {len(sv)} < 80 % de {len(splits_plan)}")
    if len(sp) and np.allclose(cen(X, sp), 0, atol=1e-8): inc.append("X sin variacion intra-split: NO_IDENTIFICABLE")
    if len(sp) and np.ptp(L) == 0: inc.append("L sin variacion")
    prim = None
    if not inc:
        prim = seguro(primaria, sp, X, L, Y, 3, 260001, B)
        if "D" not in prim: inc.append(prim["nota"])
    ver = "INCONCLUSIVE" if inc else ("PASS" if (prim["p"] < 0.05 and prim["D"] > 0 and prim["pendiente_X"] > 0) else "NOT_MET")
    sec = {}
    if len(sp) >= 3:
        sec["W_adj_lineal_rangos"] = seguro(lambda: W_perm(sp, X, resid(Y, [L], sp), 260002, BW))
        def flex():
            ry = np.empty(len(Y)); rl = np.empty(len(Y))
            for s in np.unique(sp):
                k = sp == s; ry[k] = rankdata(Y[k]); rl[k] = rankdata(L[k])
            return W_perm(sp, X, resid(ry, [rl, rl ** 2, rl ** 3], sp), 260003, BW)
        sec["W_adj_flexible_rangos"] = seguro(flex)
        vk = [r for r in validas if int(r["trajectory"].split("_")[0][5:]) in sv]
        r30 = [pos(r.get("rho_u30")) for r in vk]
        sec["A_W_logrho30"] = seguro(lambda: W_perm(sp, np.log(r30), Y, 260004, BW)) if (transformar is None and all(v is not None for v in r30)) else dict(nota="no definido")
        sec["D_base_grado5"] = seguro(primaria, sp, X, L, Y, 5, 260005, min(B, 2000))
        aud = [(pos(r.get("rho_u10")), pos(r.get("rho_u10_alta"))) for r in validas if str(r.get("auditada")) == "1"]
        aud_ok = [(x, y) for x, y in aud if x and y]
        sec["auditoria_rho10"] = dict(auditadas=len(aud), con_valor=len(aud_ok), dif_rel_max=float(max(abs(x - y) / y for x, y in aud_ok)) if aud_ok else None)
        cu = [(pos(r.get("rho_u10")), fnum(r.get("cuerda_u10"))) for r in validas if fnum(r.get("cuerda_u10")) is not None]
        sec["cuerda_u10"] = dict(n=len(cu), violaciones=int(sum(x < y * (1 - 1e-6) for x, y in cu if x)),
                                 cara_max=max((int(float(r["cara_max_u10"])) for r in validas if fnum(r.get("cara_max_u10")) is not None), default=None))
    falt = {k: sum(1 for v in motivos_falta.values() if v == k) for k in ("ausente", "error", "dominio")}
    return dict(veredicto=ver, motivos_inconclusive=inc, primaria=prim, secundarios=sec, planificadas=N, validas=len(validas), faltantes=nfal,
                faltantes_por_motivo=falt, splits_planificados=len(splits_plan), splits_validos=len(sv),
                alcance="PASS = X mejora fuera de muestra a una base cubica de log rho(10); no informacion nueva sobre toda funcion de L; predictivo, no causal")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tabla", required=True); ap.add_argument("--tabla-sha"); ap.add_argument("--resumen-cohorte"); ap.add_argument("--compuerta")
    ap.add_argument("--out", required=True); ap.add_argument("--descubrimiento", action="store_true"); ap.add_argument("--B", type=int, default=5000); ap.add_argument("--BW", type=int, default=20000)
    a = ap.parse_args(); conf = not a.descubrimiento
    filas = list(csv.DictReader(open(a.tabla, encoding="utf-8")))
    if conf:
        if not a.tabla_sha or sha(a.tabla) != a.tabla_sha: sys.exit("ABORTA: SHA de la tabla")
        if a.B != 5000 or a.BW != 20000: sys.exit("ABORTA: permutaciones distintas de las congeladas")
        plan = universo(168, 323); rc = json.loads(Path(a.resumen_cohorte).read_text()) if a.resumen_cohorte else {}
        gc = json.loads(Path(a.compuerta).read_text()) if a.compuerta else {}
        gate_ok = (rc.get("modo") == "cohorte" and rc.get("tabla_sha256") == a.tabla_sha and gc.get("modo") == "compuerta" and gc.get("PASA") is True
                   and gc.get("script_sha256") == rc.get("script_sha256"))
        gate_nota = "compuerta/resumen no validos: se exige resumen de cohorte con tabla_sha256 = tabla, compuerta PASA true y mismo script_sha256"
    else:
        plan = universo(12, 167); gate_ok, gate_nota = True, ""; rc = gc = {}
    res = analizar(filas, plan, gate_ok, gate_nota, a.B, a.BW)
    res.update(modo="CONFIRMATORIO" if conf else "DESCUBRIMIENTO (no confirmatorio)", tabla_sha256=sha(a.tabla), script_sha256=sha(Path(__file__)),
               cohorte_script_sha256=rc.get("script_sha256"), compuerta=gc)
    if not conf: res["veredicto"] = f"{res['veredicto']} [DESCUBRIMIENTO]"
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / ("RESULTADO_C1.json" if conf else "descubrimiento.json")).write_text(json.dumps(res, indent=2, ensure_ascii=False)); print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
