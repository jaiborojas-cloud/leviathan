"""analisis_Q13M2.py v2.1 - analisis UNICO de DIN-Q13-M2 (segundo y tercer manipulador del colapso: LP y WD, A0 compartido, 11 niveles).
Reutiliza SIN CAMBIOS, con SHA verificado: C1/analisis_C1_v2.py (primaria), Q13/analisis_Q13.py (D_punto, bloques) y
Q13DR/analisis_Q13DR.py v3 (valida, pendiente, rango_c, clasificar_extremo, equivalencia, spearman, limpio, Aborta).

Entradas: --tabla/--tabla-sha q13m2_cohorte.csv; --plan/--plan-sha q13m2_plan.json; --resumen RESUMEN_q13m2.json;
--tabla-ls/--tabla-ls-sha: tabla de Q13-DR (ed00364f...), referencia LS para la compatibilidad.
PLAN (estricto; si no ABORTA codigo 3): n_splits entero (no bool) en 1..320 (tope: decision del responsable 09:23, opcion B); niveles = lista EXACTA de 11 objetos
{nivel, brazo, dosis} = A0/0, LP1..LP5 = 1e-4, 3.52e-4, 7.48e-4, 1.85e-3, 7.22e-3, WD1..WD5 = 0.709, 1.56, 2.19, 2.94, 4; ids_sha256.
Universo: q13m2_{nivel}_s{split:04d}_k{k}. Duplicados/ajenos: ABORTA. Dominio de fila: el de Q13DR v3 (valida).
INCONCLUSIVE (global) si en cualquier nivel faltantes > 5 % de 5N o splits con >= 3 validas < 80 % de N; comunes (>= 3 validas en los
11 niveles) < 80 % de N; plan/resumen no vinculados. v2 (auditoria PR #117, F01): X o L sin variacion, o un fallo de la primaria, en un
nivel EXCLUSIVO de m deja INCONCLUSIVE solo a m (el otro se evalua; veredicto conjunto INCONCLUSIVE_PARCIAL); en A0 es global.
Salida (F02): RESULTADO_Q13M2.json se crea en exclusiva; si ya existe: ABORTA (no se sobrescribe).
v2.1 (verificacion PR #118, N01): con varios niveles fallidos de un mismo manipulador se registran todos los motivos.
Por manipulador m en {LP, WD}, niveles (A0, m1..m5):
 1) COMPUERTA: A0 c >= 0.8 y q <= 0.05 (si falla: INCONCLUSIVE_MANIPULACION en ambos); por m: c estrictamente decreciente A0 > m1 > ... > m5,
    rango (c_A0 - c_m5) >= 0.30, |acc_mj - acc_A0| < 0.05 en m1-m3, acc_A0 - acc_mj <= 0.10 en m4-m5 (si falla: INCONCLUSIVE_MANIPULACION en m).
 2) SENAL EN EL CONTROL: primaria C1 en A0 (5000 perm., 260001); si no PASS: INCONCLUSIVE_SIN_SENAL_CONTROL en ambos.
 3) PRIMARIA: beta_m = pendiente MCO de D sobre la mediana de c (filas comunes) en los 6 niveles. Bootstrap pareado de splits comunes
    (2000, semilla 960001; MISMOS remuestreos para LP y WD; copias en el bloque del split original). IC bilateral 97.5 %
    (cuantiles 0.0125 y 0.9875; Bonferroni por dos primarias). MODULA_m si el limite inferior > 0; si no NO_CONCLUYENTE.
    Replica degenerada en un nivel usado por m: m INCONCLUSIVE con todos los fallos registrados (A0 afecta a ambos).
 4) SECUNDARIOS PREDECLARADOS:
    - Compatibilidad con LS: beta_LS recalculado de la tabla Q13-DR con Q13DR v3 (filas comunes, mediana de c); su incertidumbre por
      un bootstrap INDEPENDIENTE de los splits LS (2000, semilla 960002). Por replica b: dbeta_m,b = beta_m,b - beta_LS,b, con la MISMA
      referencia LS en cada replica para LP y WD. IC95 (0.025, 0.975): SIN_DIFERENCIA_DETECTADA si contiene 0 (compatibilidad
      estadistica, no equivalencia); si no DIFIERE.
    - LP frente a WD: IC95 pareado de beta_LP,b - beta_WD,b.
    - Extremo por m (regla Q13-DR con IC95 de D_m5) y equivalencia por m (IC 97.5 % de beta_m en [-0.02, 0.02]; sin potencia prometida).
 VEREDICTO CONJUNTO (etiqueta derivada; solo si ambos tienen veredicto primario): MODULACION_REPRODUCIDA_EN_DOS_VIAS / REPRODUCIDA_SOLO_EN_LP /
 REPRODUCIDA_SOLO_EN_WD / NO_REPRODUCIDA; si un manipulador queda inconcluso: INCONCLUSIVE_PARCIAL (se reportan ambos veredictos).
"""
import argparse, csv, hashlib, json, math, numbers, sys
from pathlib import Path
import numpy as np
H = Path(__file__).resolve().parent
SHAS = {"C1/analisis_C1_v2.py": "8711f468d0df110a94c9cfdf6a1d0777f495537546cdce516929f0cb129858d5",
        "Q13/analisis_Q13.py": "9998a1b2f8f37dd0e803c6a4b024f289a23df71eea17a0b1ed6f7c6d15f3c5b3",
        "Q13DR/analisis_Q13DR.py": "cc5524a781b16ac08ef25b86427f8f36bb43c6425d8cf17753c4ae5a9b534b6a"}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
for rel, h in SHAS.items():
    if sha(H.parent / rel) != h: sys.exit(f"ABORTA: {rel} no coincide")
for d in ("C1", "Q13", "Q13DR"): sys.path.insert(0, str(H.parent / d))
import analisis_C1_v2 as A
import analisis_Q13 as Q
import analisis_Q13DR as DR
Aborta = DR.Aborta
LS_TABLA_SHA = "ed00364f66d4ac0d312cba63d14d5c5da67006956336c16e7e44336457b5240a"
NIVELES = [("A0", "A0", 0)] + [(f"LP{i + 1}", "LP", d) for i, d in enumerate([1e-4, 3.52e-4, 7.48e-4, 1.85e-3, 7.22e-3])] \
    + [(f"WD{i + 1}", "WD", d) for i, d in enumerate([0.709, 1.56, 2.19, 2.94, 4])]
NOMBRES = [n for n, _, _ in NIVELES]
MANIP = {"LP": ["A0"] + [f"LP{i}" for i in range(1, 6)], "WD": ["A0"] + [f"WD{i}" for i in range(1, 6)]}
N_MAX = 320
Q_PRI = (0.0125, 0.9875)
Q_SEC = (0.025, 0.975)


def universo(n): return [f"q13m2_{nv}_s{s:04d}_k{k}" for nv in NOMBRES for s in range(n) for k in range(5)]


def validar_plan(plan):
    if not isinstance(plan, dict): raise Aborta("plan no es un objeto")
    n = plan.get("n_splits")
    if isinstance(n, bool) or not isinstance(n, int) or not (1 <= n <= N_MAX): raise Aborta(f"n_splits invalido: {str(n)[:40]}")
    nv = plan.get("niveles")
    if not isinstance(nv, list) or len(nv) != len(NIVELES): raise Aborta("niveles: se esperan 11")
    for i, (x, (nom, br, ds)) in enumerate(zip(nv, NIVELES)):
        if not isinstance(x, dict) or x.get("nivel") != nom or x.get("brazo") != br: raise Aborta(f"nivel {i}: nombre o brazo invalido")
        e = x.get("dosis")
        if isinstance(e, bool) or not isinstance(e, numbers.Real): raise Aborta(f"nivel {nom}: dosis invalida")
        try: ok = (e == ds) and math.isfinite(float(e))
        except (OverflowError, ValueError, TypeError): ok = False
        if not ok: raise Aborta(f"nivel {nom}: dosis invalida {str(e)[:40]}")
    if not isinstance(plan.get("ids_sha256"), str): raise Aborta("ids_sha256 ausente")
    return n


def arreglos(val, comunes, nivel, sid):
    rr = [r for s in comunes for r in val[nivel][s]]; sp = np.array([sid(r) for r in rr], dtype=int)
    return dict(sp=sp, X=np.array([float(r["X10"]) for r in rr]), L=np.log([float(r["rho_caras_10"]) for r in rr]),
                Y=np.log([float(r["rho_caras_250"]) for r in rr]), c=np.array([float(r["c250"]) for r in rr]), filas=rr)


def replica(arr, niveles, idx, draw, blq):
    """D y mediana de c por nivel para un remuestreo; lanza si degenera."""
    D = {}; c = {}
    for nv in niveles:
        a = arr[nv]; ii = np.concatenate([idx[nv][s] for s in draw]); sp = np.concatenate([np.full(len(idx[nv][s]), j) for j, s in enumerate(draw)])
        fo = np.concatenate([np.full(len(idx[nv][s]), blq[s]) for s in draw])
        if not (np.ptp(a["L"][ii]) > 0): raise FloatingPointError(f"{nv}: L constante en la replica")
        d = Q.D_punto(sp, a["X"][ii], a["L"][ii], a["Y"][ii], fo)
        if not math.isfinite(d): raise FloatingPointError(f"{nv}: D no finito")
        D[nv] = d; c[nv] = float(np.median(a["c"][ii]))
    return D, c


def referencia_ls(filas_ls, NB):
    """beta_LS de la tabla Q13-DR (filas comunes, Q13DR v3) y su bootstrap independiente (semilla 960002)."""
    n = 200; val = {l: {} for l in range(6)}
    for t in DR.universo(n):
        l = int(t.split("_")[1][1:]); s = int(t.split("_")[2][1:])
        r = filas_ls.get(t)
        if DR.valida(r): val[l].setdefault(s, []).append(r)
    comunes = [s for s in range(n) if all(len(val[l].get(s, [])) >= 3 for l in range(6))]
    sid = lambda r: int(r["trajectory"].split("_")[2][1:])
    arr = {l: arreglos(val, comunes, l, sid) for l in range(6)}
    D = [Q.D_punto(arr[l]["sp"], arr[l]["X"], arr[l]["L"], arr[l]["Y"]) for l in range(6)]
    beta = DR.pendiente(D, [float(np.median(arr[l]["c"])) for l in range(6)])
    g = np.random.default_rng(960002); cs = np.array(comunes); blq = Q.bloques(cs); idx = {l: {s: np.where(arr[l]["sp"] == s)[0] for s in comunes} for l in range(6)}
    bb = np.full(NB, np.nan); fallos = []
    for i in range(NB):
        draw = g.choice(cs, size=len(cs), replace=True)
        try:
            Dd, cc = replica(arr, range(6), idx, draw, blq); bb[i] = DR.pendiente([Dd[l] for l in range(6)], [cc[l] for l in range(6)])
        except Exception as e: fallos.append(dict(replica=i, error=f"{type(e).__name__}: {e}"))
    return dict(beta=beta, splits_comunes=len(comunes), replicas=bb, fallos=fallos)


def q(v, qs): return [float(np.quantile(v, qs[0])), float(np.quantile(v, qs[1]))]


def analizar(filas, n, gate_ok, gate_nota, ls=None, B=5000, NB=2000):
    plan = universo(n); ids = [r.get("trajectory") for r in filas]
    if len(ids) != len(set(ids)): raise Aborta("IDs duplicados")
    extra = set(ids) - set(plan)
    if extra: raise Aborta(f"{len(extra)} IDs fuera del universo")
    por = {r["trajectory"]: r for r in filas}; inc = [] if gate_ok else [gate_nota]
    val = {nv: {} for nv in NOMBRES}; falt = {nv: 0 for nv in NOMBRES}
    for t in plan:
        nv = t.split("_")[1]; s = int(t.split("_")[2][1:]); r = por.get(t)
        if not DR.valida(r): falt[nv] += 1; continue
        val[nv].setdefault(s, []).append(r)
    for nv in NOMBRES:
        if falt[nv] > 0.05 * 5 * n: inc.append(f"{nv}: faltantes {falt[nv]} > 5 % de {5 * n}")
        if sum(1 for s in range(n) if len(val[nv].get(s, [])) >= 3) < math.ceil(0.8 * n): inc.append(f"{nv}: splits validos < 80 % de {n}")
    comunes = [s for s in range(n) if all(len(val[nv].get(s, [])) >= 3 for nv in NOMBRES)]
    if len(comunes) < math.ceil(0.8 * n): inc.append(f"splits comunes {len(comunes)} < 80 % de {n}")
    sid = lambda r: int(r["trajectory"].split("_")[2][1:])
    arr = {nv: arreglos(val, comunes, nv, sid) for nv in NOMBRES}
    malo = {}
    for nv in NOMBRES:
        a = arr[nv]
        if len(a["sp"]) and np.allclose(A.cen(a["X"], a["sp"]), 0, atol=1e-8): malo.setdefault(nv, []).append("X sin variacion intra-split")
        if len(a["sp"]) and np.ptp(a["L"]) == 0: malo.setdefault(nv, []).append("L sin variacion")
    if "A0" in malo: inc += [f"A0: {x}" for x in malo["A0"]]
    med = lambda nv, c: float(np.median([float(r[c]) for s in val[nv] for r in val[nv][s]])) if val[nv] else None
    manip = {nv: dict(mediana_c250=med(nv, "c250"), mediana_q250=med(nv, "q250"), mediana_acc_panel250=med(nv, "acc_panel250")) for nv in NOMBRES}
    out = dict(manipulacion=manip, splits_planificados=n, splits_comunes=len(comunes), faltantes=falt, motivos_inconclusive=inc,
               primaria={}, por_manipulador={}, secundarios={})
    if inc: out["veredicto_conjunto"] = "INCONCLUSIVE"; return out
    m0 = manip["A0"]; estado = {}
    if not (m0["mediana_c250"] >= 0.8 and m0["mediana_q250"] <= 0.05):
        out["veredicto_conjunto"] = "INCONCLUSIVE_MANIPULACION"; out["motivos_inconclusive"].append("A0 sin colapso operacional"); return out
    for m, nvs in MANIP.items():
        cs = [manip[nv]["mediana_c250"] for nv in nvs]; ac = [manip[nv]["mediana_acc_panel250"] for nv in nvs]
        ok = all(cs[i] > cs[i + 1] for i in range(5)) and cs[0] - cs[-1] >= 0.30 and all(abs(ac[j] - ac[0]) < 0.05 for j in (1, 2, 3)) and all(ac[0] - ac[j] <= 0.10 for j in (4, 5))
        estado[m] = None if ok else "INCONCLUSIVE_MANIPULACION"
    for m in MANIP:
        for nv in MANIP[m][1:]:
            if nv in malo and estado[m] in (None, "INCONCLUSIVE"):   # N01: se registran todos los motivos
                estado[m] = "INCONCLUSIVE"; out["motivos_inconclusive"].append(f"{m}: {nv}: {', '.join(malo[nv])}")
    activos = [m for m in MANIP if estado[m] is None]
    usar = sorted({nv for m in activos for nv in MANIP[m]}, key=NOMBRES.index) or ["A0"]
    for nv in usar:
        try:
            a = arr[nv]; p = A.primaria(a["sp"], a["X"], a["L"], a["Y"], 3, 260001, B); p["pass"] = bool(p["p"] < 0.05 and p["D"] > 0 and p["pendiente_X"] > 0)
            out["primaria"][nv] = p
        except Exception as e:
            msg = f"{nv}: primaria no definida: {type(e).__name__}: {e}"
            if nv == "A0":
                out["motivos_inconclusive"].append(msg); out["veredicto_conjunto"] = "INCONCLUSIVE"; return out
            for m in MANIP:
                if nv in MANIP[m] and estado[m] in (None, "INCONCLUSIVE"): estado[m] = "INCONCLUSIVE"; out["motivos_inconclusive"].append(f"{m}: {msg}")   # N01
    activos = [m for m in activos if estado[m] is None]
    if not out["primaria"]["A0"]["pass"]:
        out["veredicto_conjunto"] = "INCONCLUSIVE_SIN_SENAL_CONTROL"; out["por_manipulador"] = {m: dict(veredicto="INCONCLUSIVE_SIN_SENAL_CONTROL") for m in MANIP}; return out
    beta = {}
    for m in activos:
        try: beta[m] = DR.pendiente([out["primaria"][nv]["D"] for nv in MANIP[m]], [float(np.median(arr[nv]["c"])) for nv in MANIP[m]])
        except FloatingPointError as e: estado[m] = "INCONCLUSIVE"; out["motivos_inconclusive"].append(f"{m} punto: {e}")
    activos = [m for m in activos if estado[m] is None]
    g = np.random.default_rng(960001); cs_ = np.array(comunes); blq = Q.bloques(cs_)
    idx = {nv: {s: np.where(arr[nv]["sp"] == s)[0] for s in comunes} for nv in usar}
    bb = {m: np.full(NB, np.nan) for m in activos}; Db = {nv: np.full(NB, np.nan) for nv in usar}; fallos = {m: [] for m in activos}
    for i in range(NB):
        draw = g.choice(cs_, size=len(cs_), replace=True)
        for m in activos:
            try:
                Dd, cc = replica(arr, MANIP[m], idx, draw, blq)
                for nv in MANIP[m]: Db[nv][i] = Dd[nv]
                bb[m][i] = DR.pendiente([Dd[nv] for nv in MANIP[m]], [cc[nv] for nv in MANIP[m]])
            except Exception as e: fallos[m].append(dict(replica=i, error=f"{type(e).__name__}: {e}"))
    for m in MANIP:
        r = dict(veredicto=estado[m]) if estado[m] else {}
        if estado[m] is None:
            cs = [float(np.median(arr[nv]["c"])) for nv in MANIP[m]]
            r.update(beta=beta[m], c_comunes=cs, rango_c=DR.rango_c(cs), replicas_fallidas=len(fallos[m]), fallos=fallos[m])
            if fallos[m]:
                r["veredicto"] = "INCONCLUSIVE"; out["motivos_inconclusive"].append(f"{m}: bootstrap degenerado ({len(fallos[m])} de {NB})")
            else:
                ic = q(bb[m], Q_PRI); r.update(IC975_beta=ic, veredicto="MODULA" if ic[0] > 0 else "NO_CONCLUYENTE", equivalencia_secundaria=DR.equivalencia(ic),
                                                 margen_dD_equivalencia=0.02 * DR.rango_c(cs))
                m5 = MANIP[m][-1]; r["extremo"] = DR.clasificar_extremo(out["primaria"][m5]["pass"], q(Db[m5], Q_SEC))
                r["IC95_D"] = {nv: q(Db[nv], Q_SEC) for nv in MANIP[m]}
                r["spearman_D_c"] = DR.spearman([out["primaria"][nv]["D"] for nv in MANIP[m]], cs)
        out["por_manipulador"][m] = r
    ok = [m for m in MANIP if out["por_manipulador"][m].get("veredicto") in ("MODULA", "NO_CONCLUYENTE")]
    # secundarios
    if ls is not None and ls.get("error"):
        out["secundarios"]["compatibilidad_LS"] = dict(nota=f"referencia LS no definida: {ls['error']}")
    elif ls is not None:
        lsb = ls["replicas"]; sec = dict(beta_LS=ls["beta"], IC95_beta_LS=None, replicas_LS_fallidas=len(ls["fallos"]), fallos_LS=ls["fallos"])
        if not ls["fallos"]:
            sec["IC95_beta_LS"] = q(lsb, Q_SEC)
            for m in ok: sec[f"compatibilidad_{m}"] = compatibilidad(bb[m], lsb, beta[m], ls["beta"])
        out["secundarios"]["compatibilidad_LS"] = sec
    if len(ok) == 2:
        d = bb["LP"] - bb["WD"]; out["secundarios"]["LP_menos_WD"] = dict(dbeta=beta["LP"] - beta["WD"], IC95=q(d, Q_SEC))
    out["veredicto_conjunto"] = conjunto({m: out["por_manipulador"][m].get("veredicto") for m in MANIP})
    return out


def conjunto(v):
    """Etiqueta derivada. Solo se usan las cuatro etiquetas cuando ambos manipuladores tienen veredicto primario."""
    if all(x in ("MODULA", "NO_CONCLUYENTE") for x in v.values()):
        return {("MODULA", "MODULA"): "MODULACION_REPRODUCIDA_EN_DOS_VIAS", ("MODULA", "NO_CONCLUYENTE"): "REPRODUCIDA_SOLO_EN_LP",
                ("NO_CONCLUYENTE", "MODULA"): "REPRODUCIDA_SOLO_EN_WD", ("NO_CONCLUYENTE", "NO_CONCLUYENTE"): "NO_REPRODUCIDA"}[(v["LP"], v["WD"])]
    return "INCONCLUSIVE_PARCIAL"


def compatibilidad(bm_b, bls_b, beta_m, beta_ls):
    bm_b, bls_b = np.asarray(bm_b), np.asarray(bls_b)
    if bm_b.shape != bls_b.shape: raise ValueError("replicas M2 y LS de distinto tamano")
    ic = q(bm_b - bls_b, Q_SEC)
    return dict(dbeta=beta_m - beta_ls, IC95_dbeta=ic, lectura="SIN_DIFERENCIA_DETECTADA" if ic[0] <= 0 <= ic[1] else "DIFIERE")


def main():
    ap = argparse.ArgumentParser()
    for x in ("tabla", "tabla-sha", "plan", "plan-sha", "resumen", "tabla-ls", "tabla-ls-sha", "out"): ap.add_argument("--" + x, required=True)
    a = ap.parse_args()
    try:
        try: st, sp_, sl = sha(a.tabla), sha(a.plan), sha(a.tabla_ls)
        except OSError as e: raise Aborta(f"entrada ilegible: {type(e).__name__}")
        if st != a.tabla_sha: raise Aborta("SHA de la tabla")
        if sp_ != a.plan_sha: raise Aborta("SHA del plan")
        if sl != a.tabla_ls_sha or sl != LS_TABLA_SHA: raise Aborta("SHA de la tabla LS")
        try: plan = json.loads(Path(a.plan).read_text(encoding="utf-8")); rs = json.loads(Path(a.resumen).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e: raise Aborta(f"plan o resumen ilegible: {type(e).__name__}")
        n = validar_plan(plan)
        gate_ok = plan.get("ids_sha256") == hashlib.sha256("\n".join(universo(n)).encode()).hexdigest() and isinstance(rs, dict) \
            and rs.get("tabla_sha256") == a.tabla_sha and rs.get("plan_sha256") == a.plan_sha
        try:
            with open(a.tabla, encoding="utf-8", newline="") as fh: filas = list(csv.DictReader(fh))
            with open(a.tabla_ls, encoding="utf-8", newline="") as fh: fls = {r["trajectory"]: r for r in csv.DictReader(fh)}
        except (OSError, UnicodeDecodeError, csv.Error, KeyError) as e: raise Aborta(f"tabla ilegible: {type(e).__name__}")
        o = Path(a.out)
        if (o / "RESULTADO_Q13M2.json").exists(): raise Aborta("la salida ya existe; no se sobrescribe")
        try: ls = referencia_ls(fls, 2000)
        except Exception as e: ls = dict(error=f"{type(e).__name__}: {e}")
        res = analizar(filas, n, gate_ok, "plan/resumen no vinculados", ls=ls)
    except Aborta as e:
        print(f"ABORTA: {e}", file=sys.stderr); sys.exit(3)
    res.update(modo="CONFIRMATORIO_Q13M2", niveles=plan["niveles"], tabla_sha256=a.tabla_sha, plan_sha256=a.plan_sha, tabla_ls_sha256=sl, script_sha256=sha(Path(__file__)),
               alcance="modulacion de la senal temprana por el colapso con dos intervenciones de entrenamiento adicionales (LP, WD) en la familia gaussiana s=0.8; no identifica al colapso como causa")
    texto = json.dumps(DR.limpio(res), indent=2, ensure_ascii=False, allow_nan=False)
    o.mkdir(parents=True, exist_ok=True)
    try:
        with open(o / "RESULTADO_Q13M2.json", "x", encoding="utf-8") as fh: fh.write(texto)
    except FileExistsError:
        print("ABORTA: la salida ya existe; no se sobrescribe", file=sys.stderr); sys.exit(3)
    print(texto)


if __name__ == "__main__":
    main()
