"""analisis_Q13DR.py v3 - analisis UNICO de DIN-Q13-DR (dosis-respuesta con label smoothing, 6 niveles). Reutiliza SIN CAMBIOS cen,
D_cv y primaria de C1/analisis_C1_v2.py (SHA verificado) y D_punto/bloques de Q13/analisis_Q13.py (SHA verificado).
v2 corrige los defectos F01-F04 de la auditoria (PR #104) y aplica las decisiones del responsable de 2026-10-26 20:53.
v3 corrige N01-N05 de la verificacion (PR #105): c constante exacta (ptp == 0), rango = max - min, eps enorme y archivos
ilegibles -> ABORTA, y se conservan TODOS los fallos de bootstrap.

Entradas: --tabla q13dr_cohorte.csv + --tabla-sha; --plan q13dr_plan.json + --plan-sha; --resumen RESUMEN_q13dr.json.
PLAN (validacion estricta, si no ABORTA): n_splits entero (no bool) en 1..400; niveles = lista de 6 dict con nivel entero 0..5 en orden
y eps numerico finito igual EXACTAMENTE a [0, 0.002, 0.005, 0.01, 0.02, 0.05]; ids_sha256 del universo.
Universo: IDs q13dr_L{l}_s{split:04d}_k{k}. Duplicados o ajenos: ABORTA.
DOMINIO de una fila (si no, faltante): sin error; X10, c250, q250, acc_panel250, rho_caras_10, rho_caras_250 finitas;
rho_caras_10, rho_caras_250 > 0; q250 y acc_panel250 en [0,1]; c250 en (0,1]. Comparaciones exactas, sin tolerancias ni redondeo.
INCONCLUSIVE si: en cualquier nivel faltantes > 5 % de 5N o splits con >= 3 validas < 80 % de N; splits COMUNES (>= 3 validas en cada
uno de los 6 niveles) < 80 % de N; X o L sin variacion en algun nivel; fallo de ajuste; plan/resumen no vinculados.
1) COMPUERTA (medianas sobre todas las filas validas de cada nivel; resumen operacional): L0 c250 >= 0.8 y q250 <= 0.05; c250
   estrictamente decreciente L0 > ... > L5; c_L0 - c_L5 >= 0.30; |acc_Ll - acc_L0| < 0.05 en L1-L3; acc_L0 - acc_Ll <= 0.10 en L4-L5.
   Si no: INCONCLUSIVE_MANIPULACION.
2) SENAL EN EL CONTROL: primaria C1 en L0 (base cubica, 10 bloques 260010, 5000 perm. 260001); PASS si p<0.05, D>0, pendiente>0.
   Si no: INCONCLUSIVE_SIN_SENAL_CONTROL.
3) PRIMARIA sobre las FILAS COMUNES (las mismas en el punto y en el bootstrap): beta = pendiente MCO de D_l sobre la mediana de c250_l
   de esas filas. Bootstrap pareado de splits comunes (2000, semilla 860001; copias en el bloque del split original; D_l y c_l
   recalculados). Cada replica se valida (L con variacion en cada nivel, D finito, c no constante, beta finita); si alguna falla:
   INCONCLUSIVE con motivo, indices y error (no se descartan ni redibujan replicas). Punto con c constante: INCONCLUSIVE.
   VEREDICTO PRIMARIO: MODULA si IC95 inf de beta > 0; si no NO_CONCLUYENTE.
4) SECUNDARIOS PREDECLARADOS: equivalencia NO_MODULA si IC95 de beta contenido en [-0.02, 0.02] (|dD lineal| <= 0.02 x rango(c);
   sin potencia prometida; puede coexistir con MODULA); extremo L5: PERSISTE si PASS; DESAPARECE si no PASS e IC95 sup de D_L5 < 0.006;
   si no INDETERMINADO.
DESCRIPTIVOS (no deciden): Spearman(D_l, c_l) con rangos medios (null si D o c constantes); fraccion de varianza intra-split de Y
tras la base por nivel; D con rho_vert por nivel (2000 perm., 870001+l); D por cuartiles de c250 dentro de L0 (499 perm., 880001+q).
"""
import argparse, csv, hashlib, json, math, numbers, sys
from pathlib import Path
import numpy as np
H = Path(__file__).resolve().parent
A_SHA = "8711f468d0df110a94c9cfdf6a1d0777f495537546cdce516929f0cb129858d5"
Q_SHA = "9998a1b2f8f37dd0e803c6a4b024f289a23df71eea17a0b1ed6f7c6d15f3c5b3"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sha(H.parent / "C1" / "analisis_C1_v2.py") != A_SHA: sys.exit("ABORTA: analisis_C1_v2.py no coincide")
if sha(H.parent / "Q13" / "analisis_Q13.py") != Q_SHA: sys.exit("ABORTA: analisis_Q13.py no coincide")
sys.path.insert(0, str(H.parent / "C1")); sys.path.insert(0, str(H.parent / "Q13"))
import analisis_C1_v2 as A
import analisis_Q13 as Q
NIV = 6
EPS = [0, 0.002, 0.005, 0.01, 0.02, 0.05]
N_MAX = 400


class Aborta(Exception):
    pass


def fnum(v):
    try: x = float(v)
    except (TypeError, ValueError): return None
    return x if math.isfinite(x) else None


def universo(n): return [f"q13dr_L{l}_s{s:04d}_k{k}" for l in range(NIV) for s in range(n) for k in range(5)]


def validar_plan(plan):
    if not isinstance(plan, dict): raise Aborta("plan no es un objeto")
    n = plan.get("n_splits")
    if isinstance(n, bool) or not isinstance(n, int) or not (1 <= n <= N_MAX): raise Aborta(f"n_splits invalido: {n!r}")
    nv = plan.get("niveles")
    if not isinstance(nv, list) or len(nv) != NIV: raise Aborta("niveles: se esperan 6")
    for i, x in enumerate(nv):
        if not isinstance(x, dict): raise Aborta(f"nivel {i} no es objeto")
        l, e = x.get("nivel"), x.get("eps")
        if isinstance(l, bool) or not isinstance(l, int) or l != i: raise Aborta(f"nivel {i}: numero invalido {l!r}")
        if isinstance(e, bool) or not isinstance(e, numbers.Real): raise Aborta(f"nivel {i}: eps invalido {e!r}")
        try: ok = (e == EPS[i]) and math.isfinite(float(e))
        except (OverflowError, ValueError, TypeError): ok = False
        if not ok: raise Aborta(f"nivel {i}: eps invalido {str(e)[:40]}")
    if not isinstance(plan.get("ids_sha256"), str): raise Aborta("ids_sha256 ausente")
    return n


def valida(r):
    if r is None or r.get("error"): return False
    v = {c: fnum(r.get(c)) for c in ("X10", "c250", "q250", "acc_panel250", "rho_caras_10", "rho_caras_250")}
    if any(x is None for x in v.values()): return False
    return v["rho_caras_10"] > 0 and v["rho_caras_250"] > 0 and 0 <= v["q250"] <= 1 and 0 <= v["acc_panel250"] <= 1 and 0 < v["c250"] <= 1


def pendiente(D, c):
    c = np.asarray(c, float); D = np.asarray(D, float)
    if not np.all(np.isfinite(D)) or not np.all(np.isfinite(c)): raise FloatingPointError("beta no identificada (valores no finitos)")
    if np.ptp(c) == 0: raise FloatingPointError("beta no identificada (c constante)")
    cc = c - c.mean(); den = float((cc ** 2).sum())
    if not (den > 0): raise FloatingPointError("beta no identificada (c constante)")
    b = float((cc * (D - D.mean())).sum() / den)
    if not math.isfinite(b): raise FloatingPointError("beta no finita")
    return b


def rango_c(cs): return float(max(cs) - min(cs))


def clasificar_beta(ic): return "MODULA" if ic[0] > 0 else "NO_CONCLUYENTE"


def equivalencia(ic): return "NO_MODULA" if (ic[0] >= -0.02 and ic[1] <= 0.02) else "NO_ESTABLECIDA"


def clasificar_extremo(pass5, ic5):
    if pass5: return "PERSISTE"
    if ic5[1] < 0.006: return "DESAPARECE"
    return "INDETERMINADO"


def rangos(v):
    v = np.asarray(v, float); o = np.argsort(v, kind="mergesort"); r = np.empty(len(v)); i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]: j += 1
        r[o[i:j + 1]] = (i + j) / 2 + 1; i = j + 1
    return r


def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if np.ptp(a) == 0 or np.ptp(b) == 0: return None
    return float(np.corrcoef(rangos(a), rangos(b))[0, 1])


def frac_base(sp, L, Y):
    us = np.unique(sp); f = Q.bloques(us); fo = np.array([f[s] for s in sp]); Yc = A.cen(Y, sp); z = (L - L.mean()) / L.std()
    Bm = np.column_stack([A.cen(z ** g, sp) for g in (1, 2, 3)]); sb = 0.0
    for k in range(10):
        tr, te = fo != k, fo == k; b = np.linalg.lstsq(Bm[tr], Yc[tr], rcond=None)[0]; sb += float(((Yc[te] - Bm[te] @ b) ** 2).sum())
    return sb / float((Yc ** 2).sum())


def limpio(x):
    if isinstance(x, dict): return {k: limpio(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [limpio(v) for v in x]
    if isinstance(x, (float, np.floating)): return float(x) if math.isfinite(float(x)) else None
    if isinstance(x, np.integer): return int(x)
    if isinstance(x, np.bool_): return bool(x)
    return x


def analizar(filas, n, gate_ok, gate_nota, B=5000, NB=2000, B2=2000, BQ=499):
    plan = universo(n); ids = [r.get("trajectory") for r in filas]
    if len(ids) != len(set(ids)): raise Aborta("IDs duplicados")
    extra = set(ids) - set(plan)
    if extra: raise Aborta(f"{len(extra)} IDs fuera del universo")
    por = {r["trajectory"]: r for r in filas}; inc = [] if gate_ok else [gate_nota]
    val = {l: {} for l in range(NIV)}; falt = {l: 0 for l in range(NIV)}
    for t in plan:
        l = int(t.split("_")[1][1:]); s = int(t.split("_")[2][1:]); r = por.get(t)
        if not valida(r): falt[l] += 1; continue
        val[l].setdefault(s, []).append(r)
    for l in range(NIV):
        if falt[l] > 0.05 * 5 * n: inc.append(f"L{l}: faltantes {falt[l]} > 5 % de {5 * n}")
        if sum(1 for s in range(n) if len(val[l].get(s, [])) >= 3) < math.ceil(0.8 * n): inc.append(f"L{l}: splits validos < 80 % de {n}")
    comunes = [s for s in range(n) if all(len(val[l].get(s, [])) >= 3 for l in range(NIV))]
    if len(comunes) < math.ceil(0.8 * n): inc.append(f"splits comunes {len(comunes)} < 80 % de {n}")
    arr = {}
    for l in range(NIV):
        rr = [r for s in comunes for r in val[l][s]]; sp = np.array([int(r["trajectory"].split("_")[2][1:]) for r in rr], dtype=int)
        arr[l] = dict(sp=sp, X=np.array([float(r["X10"]) for r in rr]), L=np.log([float(r["rho_caras_10"]) for r in rr]), Y=np.log([float(r["rho_caras_250"]) for r in rr]),
                      c=np.array([float(r["c250"]) for r in rr]), filas=rr)
        if len(sp) and np.allclose(A.cen(arr[l]["X"], sp), 0, atol=1e-8): inc.append(f"L{l}: X sin variacion intra-split")
        if len(sp) and np.ptp(arr[l]["L"]) == 0: inc.append(f"L{l}: L sin variacion")
    med = lambda l, c: float(np.median([float(r[c]) for s in val[l] for r in val[l][s]])) if val[l] else None
    manip = {f"L{l}": dict(mediana_c250=med(l, "c250"), mediana_q250=med(l, "q250"), mediana_acc_panel250=med(l, "acc_panel250")) for l in range(NIV)}
    out = dict(manipulacion=manip, splits_planificados=n, splits_comunes=len(comunes), faltantes={f"L{l}": falt[l] for l in range(NIV)},
               motivos_inconclusive=inc, primaria={}, bootstrap={}, secundarios={})
    if inc: out["veredicto"] = "INCONCLUSIVE"; return out
    cs_g = [manip[f"L{l}"]["mediana_c250"] for l in range(NIV)]; ac = [manip[f"L{l}"]["mediana_acc_panel250"] for l in range(NIV)]; m0 = manip["L0"]
    mok = m0["mediana_c250"] >= 0.8 and m0["mediana_q250"] <= 0.05 and all(cs_g[i] > cs_g[i + 1] for i in range(NIV - 1)) and cs_g[0] - cs_g[-1] >= 0.30 \
        and all(abs(ac[l] - ac[0]) < 0.05 for l in (1, 2, 3)) and all(ac[0] - ac[l] <= 0.10 for l in (4, 5))
    out["manipulacion_ok"] = bool(mok)
    if not mok: out["veredicto"] = "INCONCLUSIVE_MANIPULACION"; return out
    try:
        for l in range(NIV):
            a = arr[l]; p = A.primaria(a["sp"], a["X"], a["L"], a["Y"], 3, 260001, B); p["pass"] = bool(p["p"] < 0.05 and p["D"] > 0 and p["pendiente_X"] > 0)
            out["primaria"][f"L{l}"] = p
    except Exception as e:
        out["motivos_inconclusive"].append(f"primaria no definida: {type(e).__name__}: {e}"); out["veredicto"] = "INCONCLUSIVE"; return out
    if not out["primaria"]["L0"]["pass"]: out["veredicto"] = "INCONCLUSIVE_SIN_SENAL_CONTROL"; return out
    Ds = [out["primaria"][f"L{l}"]["D"] for l in range(NIV)]; cs = [float(np.median(arr[l]["c"])) for l in range(NIV)]
    try: beta = pendiente(Ds, cs)
    except FloatingPointError as e:
        out["motivos_inconclusive"].append(f"punto: {e}"); out["veredicto"] = "INCONCLUSIVE"; return out
    g = np.random.default_rng(860001); csp = np.array(comunes); blq = Q.bloques(csp)
    idx = {l: {s: np.where(arr[l]["sp"] == s)[0] for s in comunes} for l in range(NIV)}
    Db = np.full((NB, NIV), np.nan); cb = np.full((NB, NIV), np.nan); bb = np.full(NB, np.nan); fallos = []
    for i in range(NB):
        draw = g.choice(csp, size=len(csp), replace=True)
        try:
            for l in range(NIV):
                a = arr[l]; ii = np.concatenate([idx[l][s] for s in draw]); sp = np.concatenate([np.full(len(idx[l][s]), j) for j, s in enumerate(draw)])
                fo = np.concatenate([np.full(len(idx[l][s]), blq[s]) for s in draw])
                if not (np.ptp(a["L"][ii]) > 0): raise FloatingPointError(f"L{l}: L constante en la replica")
                d = Q.D_punto(sp, a["X"][ii], a["L"][ii], a["Y"][ii], fo)
                if not math.isfinite(d): raise FloatingPointError(f"L{l}: D no finito")
                Db[i, l] = d; cb[i, l] = float(np.median(a["c"][ii]))
            bb[i] = pendiente(Db[i], cb[i])
        except Exception as e:
            fallos.append(dict(replica=i, error=f"{type(e).__name__}: {e}"))
    out["bootstrap"] = dict(beta=beta, c_comunes=cs, replicas=NB, replicas_fallidas=len(fallos), fallos=fallos)
    if fallos:
        out["motivos_inconclusive"].append(f"bootstrap degenerado: {len(fallos)} de {NB} replicas (indices {[f['replica'] for f in fallos[:10]]})")
        out["veredicto"] = "INCONCLUSIVE"; return out
    q = lambda v: [float(np.quantile(v, .025)), float(np.quantile(v, .975))]
    ic = q(bb); out["bootstrap"].update(IC95_beta=ic, IC95_D={f"L{l}": q(Db[:, l]) for l in range(NIV)}, rango_c=rango_c(cs), diferencia_c_L0_L5=cs[0] - cs[-1],
                                         margen_dD_equivalencia=0.02 * rango_c(cs))
    out["veredicto"] = clasificar_beta(ic)
    out["equivalencia_secundaria"] = equivalencia(ic)
    out["extremo"] = clasificar_extremo(out["primaria"]["L5"]["pass"], out["bootstrap"]["IC95_D"]["L5"])
    sec = dict(spearman_D_c=spearman(Ds, cs))
    for l in range(NIV):
        a = arr[l]; d = dict(frac_varianza_tras_base=frac_base(a["sp"], a["L"], a["Y"]))
        rv = [(fnum(x.get("rho_vert_10")), fnum(x.get("rho_vert_250"))) for x in a["filas"]]
        if all(u and v and u > 0 and v > 0 for u, v in rv):
            try: d["D_rho_vert"] = A.primaria(a["sp"], a["X"], np.log([u for u, _ in rv]), np.log([v for _, v in rv]), 3, 870001 + l, B2)["D"]
            except Exception as e: d["D_rho_vert"] = f"no definido: {type(e).__name__}"
        sec[f"L{l}"] = d
    a = arr[0]; qs = np.quantile(a["c"], [.25, .5, .75]); cu = np.digitize(a["c"], qs); cuart = {}
    for k in range(4):
        m = cu == k; spm = a["sp"][m]; ok = [s for s in np.unique(spm) if (spm == s).sum() >= 3]; mm = m & np.isin(a["sp"], ok)
        try: cuart[f"Q{k + 1}"] = dict(n=int(mm.sum()), splits=len(ok), D=A.primaria(a["sp"][mm], a["X"][mm], a["L"][mm], a["Y"][mm], 3, 880001 + k, BQ)["D"]) if len(ok) >= 10 else dict(nota="menos de 10 splits")
        except Exception as e: cuart[f"Q{k + 1}"] = dict(nota=f"no definido: {type(e).__name__}")
    sec["D_por_cuartil_c250_en_L0_descriptivo"] = cuart; out["secundarios"] = sec
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tabla", required=True); ap.add_argument("--tabla-sha", required=True)
    ap.add_argument("--plan", required=True); ap.add_argument("--plan-sha", required=True); ap.add_argument("--resumen", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    try:
        try: st, sp_ = sha(a.tabla), sha(a.plan)
        except OSError as e: raise Aborta(f"tabla o plan ilegible: {type(e).__name__}")
        if st != a.tabla_sha: raise Aborta("SHA de la tabla")
        if sp_ != a.plan_sha: raise Aborta("SHA del plan")
        try: plan = json.loads(Path(a.plan).read_text(encoding="utf-8")); rs = json.loads(Path(a.resumen).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e: raise Aborta(f"plan o resumen ilegible: {type(e).__name__}")
        n = validar_plan(plan)
        ids_sha = hashlib.sha256("\n".join(universo(n)).encode()).hexdigest()
        gate_ok = plan.get("ids_sha256") == ids_sha and isinstance(rs, dict) and rs.get("tabla_sha256") == a.tabla_sha and rs.get("plan_sha256") == a.plan_sha
        try:
            with open(a.tabla, encoding="utf-8", newline="") as fh: filas = list(csv.DictReader(fh))
        except (OSError, UnicodeDecodeError, csv.Error) as e: raise Aborta(f"tabla ilegible: {type(e).__name__}")
        res = analizar(filas, n, gate_ok, "plan/resumen no vinculados")
    except Aborta as e:
        print(f"ABORTA: {e}", file=sys.stderr); sys.exit(3)
    res.update(modo="CONFIRMATORIO_Q13DR", niveles=plan["niveles"], tabla_sha256=a.tabla_sha, plan_sha256=a.plan_sha, script_sha256=sha(Path(__file__)),
               alcance="dosis-respuesta (tendencia lineal, no orden de las seis medias) de la senal temprana con label smoothing en la familia gaussiana s=0.8; un manipulador; no separa colapso de efecto propio de LS")
    texto = json.dumps(limpio(res), indent=2, ensure_ascii=False, allow_nan=False)
    o = Path(a.out); o.mkdir(parents=True, exist_ok=True); (o / "RESULTADO_Q13DR.json").write_text(texto); print(texto)


if __name__ == "__main__":
    main()
