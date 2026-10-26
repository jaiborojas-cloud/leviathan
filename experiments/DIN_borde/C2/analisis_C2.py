"""analisis_C2.py (BORRADOR v0, no congelado) - analisis UNICO de DIN-C2 (diseno C2). Reutiliza SIN CAMBIOS cen, D_cv, primaria y
W_perm de C1/analisis_C1_v2.py (SHA verificado). Ejecutado por Claude una sola vez sobre la tabla publicada por el agente de cohorte.

Entradas (confirmatorio): --tabla c2_cohorte.csv + --tabla-sha; --plan c2_plan.json + --plan-sha (publicado al congelar el tamano:
n_splits, ids_sha256); --resumen RESUMEN_c2.json (tabla_sha256 = tabla, plan_sha256 = plan).
Universo: IDs c2_s{split:04d}_k{k}, split 0..N-1, k 0..4 (N del plan). IDs duplicados o ajenos: ABORTA.
Columnas: trajectory, split, k, X10, R250, c250, q250, rho_caras_10, rho_caras_250, rho_vert_10, rho_vert_250, error.
Faltante: ausente, con error, o dominio invalido (rho > 0 finita, X10 finita). INCONCLUSIVE si faltantes > 5 % de 5N; splits con
>= 3 validas < 80 % de N; X o L sin variacion; SSE_base = 0 o fallo de ajuste.
COMPUERTA DE REGIMEN (antes de la primaria): mediana c250 >= 0.8 y mediana q250 <= 0.05 sobre las trayectorias validas; si no:
INCONCLUSIVE_REGIMEN. Se reporta la fraccion individual con c250 >= 0.8 y q250 <= 0.05 (descriptiva, no filtra).
PRIMARIA: X = X10; L = log rho_caras_10; Y = log rho_caras_250; D de C1 (base cubica, 10 bloques 260010, 5000 permutaciones
260001). PASS si p < 0.05, D > 0 y pendiente > 0; si no NOT_MET.
SECUNDARIOS (no deciden): D_X|R250 (R anadido a la base, 2000 perm., 270011); D con rho_vert (270012); W_adj legado (270013);
D en el subconjunto colapsado individualmente (270014, descriptivo).
"""
import argparse, csv, hashlib, json, math, sys
from pathlib import Path
import numpy as np
H = Path(__file__).resolve().parent
A_SHA = "8711f468d0df110a94c9cfdf6a1d0777f495537546cdce516929f0cb129858d5"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sha(H.parent / "C1" / "analisis_C1_v2.py") != A_SHA: sys.exit("ABORTA: analisis_C1_v2.py no coincide")
sys.path.insert(0, str(H.parent / "C1")); import analisis_C1_v2 as A


def fnum(v):
    try: x = float(v)
    except (TypeError, ValueError): return None
    return x if math.isfinite(x) else None


def universo(n): return [f"c2_s{s:04d}_k{k}" for s in range(n) for k in range(5)]


def D_extra(sp, X, L, Y, extra, semilla, B):
    us = np.unique(sp); perm = np.random.default_rng(260010).permutation(us); fold = {u: i % 10 for i, u in enumerate(perm)}
    fo = np.array([fold[s] for s in sp]); Yc = A.cen(Y, sp); z = (L - L.mean()) / L.std()
    Bm = np.column_stack([A.cen(z ** g, sp) for g in (1, 2, 3)] + [A.cen(e, sp) for e in extra]); Xc = A.cen(X, sp); D = A.D_cv(Yc, Bm, Xc, fo)
    g = np.random.default_rng(semilla); idx = [np.where(sp == s)[0] for s in us]; nul = np.empty(B)
    for b in range(B):
        Xp = X.copy()
        for ii in idx: Xp[ii] = X[g.permutation(ii)]
        nul[b] = A.D_cv(Yc, Bm, A.cen(Xp, sp), fo)
    return dict(D=D, p=float((1 + np.sum(nul >= D - 1e-15)) / (1 + B)))


def analizar(filas, n, gate_ok, gate_nota, B=5000, BW=20000, B2=2000):
    plan = universo(n); ids = [r.get("trajectory") for r in filas]
    if len(ids) != len(set(ids)): raise SystemExit("ABORTA: IDs duplicados")
    extra = set(ids) - set(plan)
    if extra: raise SystemExit(f"ABORTA: {len(extra)} IDs fuera del universo")
    por = {r["trajectory"]: r for r in filas}; val = []; falt = {}
    for t in plan:
        r = por.get(t)
        if r is None: falt[t] = "ausente"; continue
        if r.get("error"): falt[t] = "error"; continue
        ok = fnum(r.get("X10")) is not None and all((fnum(r.get(c)) or 0) > 0 for c in ("rho_caras_10", "rho_caras_250"))
        if not ok: falt[t] = "dominio"; continue
        val.append(r)
    sp = np.array([int(r["trajectory"][4:8]) for r in val]); cuenta = {s: int((sp == s).sum()) for s in range(n)}
    sv = [s for s in range(n) if cuenta[s] >= 3]; keep = [r for r in val if cuenta[int(r["trajectory"][4:8])] >= 3]
    sp = np.array([int(r["trajectory"][4:8]) for r in keep])
    X = np.array([float(r["X10"]) for r in keep]); L = np.log([float(r["rho_caras_10"]) for r in keep]); Y = np.log([float(r["rho_caras_250"]) for r in keep])
    c = np.array([fnum(r.get("c250")) if fnum(r.get("c250")) is not None else np.nan for r in val]); q = np.array([fnum(r.get("q250")) if fnum(r.get("q250")) is not None else np.nan for r in val])
    reg = dict(mediana_c250=float(np.nanmedian(c)) if len(c) else None, mediana_q250=float(np.nanmedian(q)) if len(q) else None,
               frac_individual_colapsada=float(np.nanmean((c >= 0.8) & (q <= 0.05))) if len(c) else None, c_faltantes=int(np.isnan(c).sum()) if len(c) else None)
    inc = []
    if not gate_ok: inc.append(gate_nota)
    if len(falt) > 0.05 * 5 * n: inc.append(f"faltantes {len(falt)} > 5 % de {5 * n}")
    if len(sv) < math.ceil(0.8 * n): inc.append(f"splits validos {len(sv)} < 80 % de {n}")
    if len(sp) and np.allclose(A.cen(X, sp), 0, atol=1e-8): inc.append("X sin variacion intra-split")
    if len(sp) and np.ptp(L) == 0: inc.append("L sin variacion")
    regimen_ok = reg["mediana_c250"] is not None and reg["mediana_c250"] >= 0.8 and reg["mediana_q250"] <= 0.05
    prim = None
    if inc: ver = "INCONCLUSIVE"
    elif not regimen_ok: ver = "INCONCLUSIVE_REGIMEN"
    else:
        try: prim = A.primaria(sp, X, L, Y, 3, 260001, B); ver = "PASS" if (prim["p"] < 0.05 and prim["D"] > 0 and prim["pendiente_X"] > 0) else "NOT_MET"
        except Exception as e: inc.append(f"primaria no definida: {type(e).__name__}"); ver = "INCONCLUSIVE"
    sec = {}
    if len(sp) >= 3 and not inc:
        def seguro(f):
            try: return f()
            except Exception as e: return dict(nota=f"no definido: {type(e).__name__}")
        R = np.array([fnum(r.get("R250")) for r in keep], dtype=object)
        if all(v is not None for v in R): sec["D_X_dado_R250"] = seguro(lambda: D_extra(sp, X, L, Y, [np.array(R, float)], 270011, B2))
        rv = [(fnum(r.get("rho_vert_10")), fnum(r.get("rho_vert_250"))) for r in keep]
        if all(a and b and a > 0 and b > 0 for a, b in rv):
            sec["D_rho_vert"] = seguro(lambda: A.primaria(sp, X, np.log([a for a, _ in rv]), np.log([b for _, b in rv]), 3, 270012, B2))
        sec["W_adj_legado"] = seguro(lambda: A.W_perm(sp, X, A.resid(Y, [L], sp), 270013, BW))
        cm = np.array([(fnum(r.get("c250")) or 0) >= 0.8 and (fnum(r.get("q250")) if fnum(r.get("q250")) is not None else 1) <= 0.05 for r in keep])
        ss = [s for s in np.unique(sp[cm]) if (sp[cm] == s).sum() >= 3]; mm = cm & np.isin(sp, ss)
        sec["D_subconjunto_colapsado_descriptivo"] = seguro(lambda: dict(n=int(mm.sum()), splits=len(ss), **A.primaria(sp[mm], X[mm], L[mm], Y[mm], 3, 270014, B2))) if len(ss) >= 10 else dict(nota="menos de 10 splits")
    falt_m = {k: sum(1 for v in falt.values() if v == k) for k in ("ausente", "error", "dominio")}
    return dict(veredicto=ver, motivos_inconclusive=inc, regimen=reg, regimen_ok=regimen_ok, primaria=prim, secundarios=sec,
                planificadas=5 * n, validas=len(val), faltantes=len(falt), faltantes_por_motivo=falt_m, splits_planificados=n, splits_validos=len(sv),
                alcance="replica confirmatoria independiente en la familia gaussiana explorada por G3 (s=0.8); base cubica; predictivo, no causal; no establece necesidad del colapso ni transferencia a datos reales")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tabla", required=True); ap.add_argument("--tabla-sha", required=True)
    ap.add_argument("--plan", required=True); ap.add_argument("--plan-sha", required=True); ap.add_argument("--resumen", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if sha(a.tabla) != a.tabla_sha: sys.exit("ABORTA: SHA de la tabla")
    if sha(a.plan) != a.plan_sha: sys.exit("ABORTA: SHA del plan")
    plan = json.loads(Path(a.plan).read_text()); rs = json.loads(Path(a.resumen).read_text()); n = int(plan["n_splits"])
    ids_sha = hashlib.sha256("\n".join(universo(n)).encode()).hexdigest()
    gate_ok = plan.get("ids_sha256") == ids_sha and rs.get("tabla_sha256") == a.tabla_sha and rs.get("plan_sha256") == a.plan_sha
    res = analizar(list(csv.DictReader(open(a.tabla, encoding="utf-8"))), n, gate_ok, "plan/resumen no vinculados: ids_sha256, tabla_sha256 o plan_sha256 no coinciden")
    res.update(modo="CONFIRMATORIO", tabla_sha256=a.tabla_sha, plan_sha256=a.plan_sha, script_sha256=sha(Path(__file__)), analisis_C1_v2_sha256=A_SHA)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True); (out / "RESULTADO_C2.json").write_text(json.dumps(res, indent=2, ensure_ascii=False)); print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
