"""analisis_Q13.py - analisis UNICO de DIN-Q13 (diseno Q13 v1). Reutiliza SIN CAMBIOS cen, D_cv y primaria de C1/analisis_C1_v2.py
(SHA verificado). Ejecutado por Claude una sola vez sobre la tabla publicada por el agente de cohorte.

Entradas: --tabla q13_cohorte.csv + --tabla-sha; --plan q13_plan.json + --plan-sha (n_splits, brazos, dosis, ids_sha256);
--resumen RESUMEN_q13.json (tabla_sha256, plan_sha256).
Universo: IDs q13_{brazo}_s{split:04d}_k{k}, brazo en (A0, LS, WD) salvo los descartados en el plan, split 0..N-1, k 0..4.
Duplicados o ajenos: ABORTA. Faltante: ausente, error, o dominio invalido (rho_caras_10/250 > 0 finitas, X10 finita, c250, q250 y
acc_panel250 finitas). INCONCLUSIVE si en CUALQUIER brazo faltantes > 5 % de 5N o splits con >= 3 validas < 80 % de N, X o L sin
variacion, fallo de ajuste, o plan/resumen no vinculados. El analisis usa en cada brazo los splits con >= 3 validas EN TODOS los
brazos (pareado).
1) COMPUERTA DE MANIPULACION: A0 mediana c250 >= 0.8 y mediana q250 <= 0.05; cada brazo reducido mediana c250 <= 0.70 y
   |mediana acc_panel250 - mediana A0| < 0.05. Si no: INCONCLUSIVE_MANIPULACION.
2) SENAL EN EL CONTROL: primaria C1 en A0 (base cubica de log rho_caras_10, 10 bloques 260010, 5000 perm. 260001); PASS si p<0.05,
   D>0, pendiente>0. Si no: INCONCLUSIVE_SIN_SENAL_CONTROL.
3) POR BRAZO REDUCIDO b: primaria C1 (misma semilla 260001); bootstrap pareado de splits (2000, semilla 760001; los mismos remuestreos
   para todos los brazos; cada copia de un split es un split nuevo; bloques por la regla 260010 sobre las etiquetas nuevas) ->
   IC95 percentil de D_b y de dD_b = D_A0 - D_b. Las copias de un mismo split original caen en el MISMO bloque (bloque del split
   original por la regla 260010), para no filtrar filas identicas entre entrenamiento y prueba.
   CAE: IC95 sup de D_b < 0.006 y IC95 inf de dD_b > 0. SE_MANTIENE: PASS en b y IC95 inf de dD_b <= 0. Si no: INTERMEDIO.
4) VEREDICTO con dos brazos: CAE+CAE NECESARIO_APOYADO; SE_MANTIENE+SE_MANTIENE NO_NECESARIO; CAE+SE_MANTIENE DEPENDE_DEL_MANIPULADOR;
   cualquier INTERMEDIO NO_CONCLUYENTE. Con un solo brazo reducido (el otro descartado antes de entrenar): CAE -> NECESARIO_APOYADO_UN_
   MANIPULADOR; SE_MANTIENE -> NO_NECESARIO_UN_MANIPULADOR; INTERMEDIO -> NO_CONCLUYENTE.
SECUNDARIOS (no deciden): DE intra-split de Y y X por brazo; pendiente estandarizada; D con rho_vert (2000 perm., 770001+i).
"""
import argparse, csv, hashlib, json, math, sys
from pathlib import Path
import numpy as np
H = Path(__file__).resolve().parent
A_SHA = "8711f468d0df110a94c9cfdf6a1d0777f495537546cdce516929f0cb129858d5"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sha(H.parent / "C1" / "analisis_C1_v2.py") != A_SHA: sys.exit("ABORTA: analisis_C1_v2.py no coincide")
sys.path.insert(0, str(H.parent / "C1")); import analisis_C1_v2 as A
BRAZOS = ("A0", "LS", "WD")


def fnum(v):
    try: x = float(v)
    except (TypeError, ValueError): return None
    return x if math.isfinite(x) else None


def universo(n, brazos=BRAZOS): return [f"q13_{b}_s{s:04d}_k{k}" for b in brazos for s in range(n) for k in range(5)]


def bloques(us):
    perm = np.random.default_rng(260010).permutation(np.asarray(us)); return {u: i % 10 for i, u in enumerate(perm)}


def D_punto(sp, X, L, Y, fo=None):
    """Mismo D que A.primaria (grado 3), sin permutaciones. fo explicito solo en el bootstrap."""
    if fo is None: f = bloques(np.unique(sp)); fo = np.array([f[s] for s in sp])
    Yc = A.cen(Y, sp); z = (L - L.mean()) / L.std()
    Bm = np.column_stack([A.cen(z ** g, sp) for g in (1, 2, 3)]); return A.D_cv(Yc, Bm, A.cen(X, sp), fo)


def clasificar(D_b, pass_b, IC_D, IC_dD):
    if IC_D[1] < 0.006 and IC_dD[0] > 0: return "CAE"
    if pass_b and IC_dD[0] <= 0: return "SE_MANTIENE"
    return "INTERMEDIO"


def veredicto(cl):
    if len(cl) == 2:
        return {("CAE", "CAE"): "NECESARIO_APOYADO", ("SE_MANTIENE", "SE_MANTIENE"): "NO_NECESARIO",
                ("CAE", "SE_MANTIENE"): "DEPENDE_DEL_MANIPULADOR", ("SE_MANTIENE", "CAE"): "DEPENDE_DEL_MANIPULADOR"}.get(tuple(cl), "NO_CONCLUYENTE")
    return {"CAE": "NECESARIO_APOYADO_UN_MANIPULADOR", "SE_MANTIENE": "NO_NECESARIO_UN_MANIPULADOR"}.get(cl[0], "NO_CONCLUYENTE")


def de_intra(v, sp): return float(np.sqrt(np.mean(A.cen(v, sp) ** 2)))


def analizar(filas, n, brazos, gate_ok, gate_nota, B=5000, NB=2000, B2=2000):
    plan = universo(n, brazos); ids = [r.get("trajectory") for r in filas]
    if len(ids) != len(set(ids)): raise SystemExit("ABORTA: IDs duplicados")
    extra = set(ids) - set(plan)
    if extra: raise SystemExit(f"ABORTA: {len(extra)} IDs fuera del universo")
    por = {r["trajectory"]: r for r in filas}; inc = [] if gate_ok else [gate_nota]
    val = {b: {} for b in brazos}; falt = {b: {} for b in brazos}
    for t in plan:
        b = t.split("_")[1]; s = int(t.split("_")[2][1:]); r = por.get(t)
        if r is None: falt[b][t] = "ausente"; continue
        if r.get("error"): falt[b][t] = "error"; continue
        ok = fnum(r.get("X10")) is not None and all((fnum(r.get(c)) or 0) > 0 for c in ("rho_caras_10", "rho_caras_250")) \
            and all(fnum(r.get(c)) is not None for c in ("c250", "q250", "acc_panel250"))
        if not ok: falt[b][t] = "dominio"; continue
        val[b].setdefault(s, []).append(r)
    for b in brazos:
        if len(falt[b]) > 0.05 * 5 * n: inc.append(f"{b}: faltantes {len(falt[b])} > 5 % de {5 * n}")
        sv = [s for s in range(n) if len(val[b].get(s, [])) >= 3]
        if len(sv) < math.ceil(0.8 * n): inc.append(f"{b}: splits validos {len(sv)} < 80 % de {n}")
    comunes = [s for s in range(n) if all(len(val[b].get(s, [])) >= 3 for b in brazos)]
    arr = {}
    for b in brazos:
        rr = [r for s in comunes for r in val[b][s]]; sp = np.array([int(r["trajectory"].split("_")[2][1:]) for r in rr])
        arr[b] = dict(sp=sp, X=np.array([float(r["X10"]) for r in rr]), L=np.log([float(r["rho_caras_10"]) for r in rr]),
                      Y=np.log([float(r["rho_caras_250"]) for r in rr]), filas=rr)
        if len(sp) and np.allclose(A.cen(arr[b]["X"], sp), 0, atol=1e-8): inc.append(f"{b}: X sin variacion intra-split")
        if len(sp) and np.ptp(arr[b]["L"]) == 0: inc.append(f"{b}: L sin variacion")
    med = lambda b, c: float(np.median([float(r[c]) for s in val[b] for r in val[b][s]])) if val[b] else None
    manip = {b: dict(mediana_c250=med(b, "c250"), mediana_q250=med(b, "q250"), mediana_acc_panel250=med(b, "acc_panel250")) for b in brazos}
    out = dict(brazos=list(brazos), manipulacion=manip, splits_planificados=n, splits_comunes=len(comunes),
               faltantes={b: len(falt[b]) for b in brazos}, motivos_inconclusive=inc, primaria={}, bootstrap={}, clasificacion={}, secundarios={})
    if inc: out["veredicto"] = "INCONCLUSIVE"; return out
    m0 = manip["A0"]; mok = m0["mediana_c250"] >= 0.8 and m0["mediana_q250"] <= 0.05
    for b in brazos[1:]:
        mok = mok and manip[b]["mediana_c250"] <= 0.70 and abs(manip[b]["mediana_acc_panel250"] - m0["mediana_acc_panel250"]) < 0.05
    out["manipulacion_ok"] = bool(mok)
    if not mok: out["veredicto"] = "INCONCLUSIVE_MANIPULACION"; return out
    try:
        for b in brazos:
            a = arr[b]; p = A.primaria(a["sp"], a["X"], a["L"], a["Y"], 3, 260001, B)
            p["pass"] = bool(p["p"] < 0.05 and p["D"] > 0 and p["pendiente_X"] > 0); out["primaria"][b] = p
    except Exception as e:
        out["motivos_inconclusive"].append(f"primaria no definida: {type(e).__name__}"); out["veredicto"] = "INCONCLUSIVE"; return out
    if not out["primaria"]["A0"]["pass"]: out["veredicto"] = "INCONCLUSIVE_SIN_SENAL_CONTROL"; return out
    # bootstrap pareado de splits
    g = np.random.default_rng(760001); cs = np.array(comunes); idx = {b: {s: np.where(arr[b]["sp"] == s)[0] for s in comunes} for b in brazos}
    blq = bloques(cs); Db = {b: np.empty(NB) for b in brazos}
    for i in range(NB):
        draw = g.choice(cs, size=len(cs), replace=True)
        for b in brazos:
            a = arr[b]; ii = np.concatenate([idx[b][s] for s in draw]); sp = np.concatenate([np.full(len(idx[b][s]), j) for j, s in enumerate(draw)])
            fo = np.concatenate([np.full(len(idx[b][s]), blq[s]) for s in draw])
            Db[b][i] = D_punto(sp, a["X"][ii], a["L"][ii], a["Y"][ii], fo)
    q = lambda v: [float(np.quantile(v, .025)), float(np.quantile(v, .975))]
    for b in brazos:
        out["bootstrap"][b] = dict(IC95_D=q(Db[b]))
        if b != "A0":
            dd = Db["A0"] - Db[b]; out["bootstrap"][b]["IC95_dD"] = q(dd); out["bootstrap"][b]["dD_punto"] = out["primaria"]["A0"]["D"] - out["primaria"][b]["D"]
            out["clasificacion"][b] = clasificar(out["primaria"][b]["D"], out["primaria"][b]["pass"], out["bootstrap"][b]["IC95_D"], out["bootstrap"][b]["IC95_dD"])
    out["veredicto"] = veredicto([out["clasificacion"][b] for b in brazos[1:]])
    for i, b in enumerate(brazos):
        a = arr[b]; sec = dict(DE_intra_Y=de_intra(a["Y"], a["sp"]), DE_intra_X=de_intra(a["X"], a["sp"]),
                               pendiente_estandarizada=out["primaria"][b]["pendiente_X"] * de_intra(a["X"], a["sp"]) / de_intra(a["Y"], a["sp"]))
        rv = [(fnum(r.get("rho_vert_10")), fnum(r.get("rho_vert_250"))) for r in a["filas"]]
        if all(x and y and x > 0 and y > 0 for x, y in rv):
            try: sec["D_rho_vert"] = A.primaria(a["sp"], a["X"], np.log([x for x, _ in rv]), np.log([y for _, y in rv]), 3, 770001 + i, B2)
            except Exception as e: sec["D_rho_vert"] = dict(nota=f"no definido: {type(e).__name__}")
        out["secundarios"][b] = sec
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tabla", required=True); ap.add_argument("--tabla-sha", required=True)
    ap.add_argument("--plan", required=True); ap.add_argument("--plan-sha", required=True); ap.add_argument("--resumen", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if sha(a.tabla) != a.tabla_sha: sys.exit("ABORTA: SHA de la tabla")
    if sha(a.plan) != a.plan_sha: sys.exit("ABORTA: SHA del plan")
    plan = json.loads(Path(a.plan).read_text()); rs = json.loads(Path(a.resumen).read_text()); n = int(plan["n_splits"])
    brazos = tuple(plan["brazos"])
    if brazos[0] != "A0" or not (set(brazos) <= set(BRAZOS)) or len(brazos) < 2 or len(set(brazos)) != len(brazos): sys.exit("ABORTA: brazos del plan")
    ids_sha = hashlib.sha256("\n".join(universo(n, brazos)).encode()).hexdigest()
    gate_ok = plan.get("ids_sha256") == ids_sha and rs.get("tabla_sha256") == a.tabla_sha and rs.get("plan_sha256") == a.plan_sha
    res = analizar(list(csv.DictReader(open(a.tabla, encoding="utf-8"))), n, brazos, gate_ok, "plan/resumen no vinculados")
    res.update(modo="CONFIRMATORIO_Q13", dosis=plan.get("dosis"), tabla_sha256=a.tabla_sha, plan_sha256=a.plan_sha, script_sha256=sha(Path(__file__)), analisis_C1_v2_sha256=A_SHA,
               alcance="efecto de manipular el entrenamiento (LS, WD) sobre la senal temprana en la familia gaussiana s=0.8; no necesidad logica ni transferencia")
    o = Path(a.out); o.mkdir(parents=True, exist_ok=True); (o / "RESULTADO_Q13.json").write_text(json.dumps(res, indent=2, ensure_ascii=False)); print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
