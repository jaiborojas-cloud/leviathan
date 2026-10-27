"""analisis_Q13DR.py - analisis UNICO de DIN-Q13-DR (dosis-respuesta con label smoothing, 6 niveles). Reutiliza SIN CAMBIOS cen,
D_cv y primaria de C1/analisis_C1_v2.py (SHA verificado) y D_punto/bloques de Q13/analisis_Q13.py (SHA verificado).

Entradas: --tabla q13dr_cohorte.csv + --tabla-sha; --plan q13dr_plan.json + --plan-sha (n_splits, niveles [{nivel, eps}], ids_sha256);
--resumen RESUMEN_q13dr.json (tabla_sha256, plan_sha256).
Universo: IDs q13dr_L{l}_s{split:04d}_k{k}, l = 0..5, split 0..N-1, k 0..4. Duplicados o ajenos: ABORTA.
Faltante: ausente, error o dominio invalido (rho_caras_10/250 > 0 finitas; X10, c250, q250, acc_panel250 finitas). INCONCLUSIVE si en
CUALQUIER nivel faltantes > 5 % de 5N o splits con >= 3 validas < 80 % de N; X o L sin variacion; fallo de ajuste; plan/resumen no
vinculados. Se usan los splits con >= 3 validas EN TODOS los niveles (pareado).
1) COMPUERTA DE MANIPULACION: L0 mediana c250 >= 0.8 y q250 <= 0.05; medianas c250 estrictamente decrecientes L0 > L1 > ... > L5;
   c_L0 - c_L5 >= 0.30; |acc_panel250 mediana - L0| < 0.05 en L1-L3 (L4, L5 se reportan). Si no: INCONCLUSIVE_MANIPULACION.
2) SENAL EN EL CONTROL: primaria C1 en L0 (base cubica, 10 bloques 260010, 5000 perm. 260001); PASS si p<0.05, D>0, pendiente>0.
   Si no: INCONCLUSIVE_SIN_SENAL_CONTROL.
3) PRIMARIA: beta = pendiente MCO de D_l sobre la mediana de c250_l (6 puntos). IC95 percentil por bootstrap pareado de splits
   (2000, semilla 860001; copias de un split en el bloque de su split original; D_l y c_l recalculados por replica).
   MODULA si IC95 inf > 0; NO_MODULA si IC95 contenido en [-0.02, 0.02]; si no NO_CONCLUYENTE.
4) EXTREMO (secundario predeclarado): primaria C1 en L5. PERSISTE si PASS en L5; DESAPARECE si no PASS e IC95 sup de D_L5 < 0.006;
   si no INDETERMINADO.
SECUNDARIOS (no deciden): Spearman(D_l, c_l); fraccion de varianza intra-split de Y que queda tras la base (SSE_base CV / SST) por
nivel; D con rho_vert por nivel (2000 perm., 870001+l); D por cuartiles de c250 dentro de L0 (descriptivo, 499 perm., 880001+q).
"""
import argparse, csv, hashlib, json, math, sys
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


def fnum(v):
    try: x = float(v)
    except (TypeError, ValueError): return None
    return x if math.isfinite(x) else None


def universo(n): return [f"q13dr_L{l}_s{s:04d}_k{k}" for l in range(NIV) for s in range(n) for k in range(5)]


def pendiente(D, c):
    c = np.asarray(c, float); D = np.asarray(D, float); cc = c - c.mean(); return float((cc * (D - D.mean())).sum() / (cc ** 2).sum())


def clasificar_beta(ic):
    if ic[0] > 0: return "MODULA"
    if ic[0] >= -0.02 and ic[1] <= 0.02: return "NO_MODULA"
    return "NO_CONCLUYENTE"


def clasificar_extremo(pass5, ic5):
    if pass5: return "PERSISTE"
    if ic5[1] < 0.006: return "DESAPARECE"
    return "INDETERMINADO"


def frac_base(sp, L, Y):
    us = np.unique(sp); f = Q.bloques(us); fo = np.array([f[s] for s in sp]); Yc = A.cen(Y, sp); z = (L - L.mean()) / L.std()
    Bm = np.column_stack([A.cen(z ** g, sp) for g in (1, 2, 3)]); sb = 0.0
    for k in range(10):
        tr, te = fo != k, fo == k; b = np.linalg.lstsq(Bm[tr], Yc[tr], rcond=None)[0]; sb += float(((Yc[te] - Bm[te] @ b) ** 2).sum())
    return sb / float((Yc ** 2).sum())


def analizar(filas, n, gate_ok, gate_nota, B=5000, NB=2000, B2=2000, BQ=499):
    plan = universo(n); ids = [r.get("trajectory") for r in filas]
    if len(ids) != len(set(ids)): raise SystemExit("ABORTA: IDs duplicados")
    extra = set(ids) - set(plan)
    if extra: raise SystemExit(f"ABORTA: {len(extra)} IDs fuera del universo")
    por = {r["trajectory"]: r for r in filas}; inc = [] if gate_ok else [gate_nota]
    val = {l: {} for l in range(NIV)}; falt = {l: 0 for l in range(NIV)}
    for t in plan:
        l = int(t.split("_")[1][1:]); s = int(t.split("_")[2][1:]); r = por.get(t)
        ok = r is not None and not r.get("error") and fnum(r.get("X10")) is not None \
            and all((fnum(r.get(c)) or 0) > 0 for c in ("rho_caras_10", "rho_caras_250")) and all(fnum(r.get(c)) is not None for c in ("c250", "q250", "acc_panel250"))
        if not ok: falt[l] += 1; continue
        val[l].setdefault(s, []).append(r)
    for l in range(NIV):
        if falt[l] > 0.05 * 5 * n: inc.append(f"L{l}: faltantes {falt[l]} > 5 % de {5 * n}")
        if sum(1 for s in range(n) if len(val[l].get(s, [])) >= 3) < math.ceil(0.8 * n): inc.append(f"L{l}: splits validos < 80 % de {n}")
    comunes = [s for s in range(n) if all(len(val[l].get(s, [])) >= 3 for l in range(NIV))]
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
    cs = [manip[f"L{l}"]["mediana_c250"] for l in range(NIV)]; m0 = manip["L0"]
    mok = m0["mediana_c250"] >= 0.8 and m0["mediana_q250"] <= 0.05 and all(cs[i] > cs[i + 1] for i in range(NIV - 1)) and cs[0] - cs[-1] >= 0.30 \
        and all(abs(manip[f"L{l}"]["mediana_acc_panel250"] - m0["mediana_acc_panel250"]) < 0.05 for l in (1, 2, 3))
    out["manipulacion_ok"] = bool(mok)
    if not mok: out["veredicto"] = "INCONCLUSIVE_MANIPULACION"; return out
    try:
        for l in range(NIV):
            a = arr[l]; p = A.primaria(a["sp"], a["X"], a["L"], a["Y"], 3, 260001, B); p["pass"] = bool(p["p"] < 0.05 and p["D"] > 0 and p["pendiente_X"] > 0)
            out["primaria"][f"L{l}"] = p
    except Exception as e:
        out["motivos_inconclusive"].append(f"primaria no definida: {type(e).__name__}"); out["veredicto"] = "INCONCLUSIVE"; return out
    if not out["primaria"]["L0"]["pass"]: out["veredicto"] = "INCONCLUSIVE_SIN_SENAL_CONTROL"; return out
    Ds = [out["primaria"][f"L{l}"]["D"] for l in range(NIV)]; beta = pendiente(Ds, cs)
    g = np.random.default_rng(860001); csp = np.array(comunes); blq = Q.bloques(csp)
    idx = {l: {s: np.where(arr[l]["sp"] == s)[0] for s in comunes} for l in range(NIV)}
    Db = np.empty((NB, NIV)); cb = np.empty((NB, NIV))
    for i in range(NB):
        draw = g.choice(csp, size=len(csp), replace=True)
        for l in range(NIV):
            a = arr[l]; ii = np.concatenate([idx[l][s] for s in draw]); sp = np.concatenate([np.full(len(idx[l][s]), j) for j, s in enumerate(draw)])
            fo = np.concatenate([np.full(len(idx[l][s]), blq[s]) for s in draw])
            Db[i, l] = Q.D_punto(sp, a["X"][ii], a["L"][ii], a["Y"][ii], fo); cb[i, l] = float(np.median(a["c"][ii]))
    bb = np.array([pendiente(Db[i], cb[i]) for i in range(NB)]); q = lambda v: [float(np.quantile(v, .025)), float(np.quantile(v, .975))]
    out["bootstrap"] = dict(beta=beta, IC95_beta=q(bb), IC95_D={f"L{l}": q(Db[:, l]) for l in range(NIV)})
    out["veredicto"] = clasificar_beta(out["bootstrap"]["IC95_beta"])
    out["extremo"] = clasificar_extremo(out["primaria"]["L5"]["pass"], out["bootstrap"]["IC95_D"]["L5"])
    # secundarios
    r = np.argsort(np.argsort(Ds)); rc = np.argsort(np.argsort(cs)); sec = dict(spearman_D_c=float(np.corrcoef(r, rc)[0, 1]))
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
    if sha(a.tabla) != a.tabla_sha: sys.exit("ABORTA: SHA de la tabla")
    if sha(a.plan) != a.plan_sha: sys.exit("ABORTA: SHA del plan")
    plan = json.loads(Path(a.plan).read_text()); rs = json.loads(Path(a.resumen).read_text()); n = int(plan["n_splits"])
    if [x["nivel"] for x in plan.get("niveles", [])] != list(range(NIV)): sys.exit("ABORTA: niveles del plan")
    ids_sha = hashlib.sha256("\n".join(universo(n)).encode()).hexdigest()
    gate_ok = plan.get("ids_sha256") == ids_sha and rs.get("tabla_sha256") == a.tabla_sha and rs.get("plan_sha256") == a.plan_sha
    res = analizar(list(csv.DictReader(open(a.tabla, encoding="utf-8"))), n, gate_ok, "plan/resumen no vinculados")
    res.update(modo="CONFIRMATORIO_Q13DR", niveles=plan["niveles"], tabla_sha256=a.tabla_sha, plan_sha256=a.plan_sha, script_sha256=sha(Path(__file__)),
               alcance="dosis-respuesta de la senal temprana con label smoothing en la familia gaussiana s=0.8; un manipulador; no separa colapso de efecto propio de LS")
    o = Path(a.out); o.mkdir(parents=True, exist_ok=True); (o / "RESULTADO_Q13DR.json").write_text(json.dumps(res, indent=2, ensure_ascii=False)); print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
