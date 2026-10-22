"""seccion6_sensibilidad.py - analisis exploratorio de sensibilidad por completaciones binarias (T2-A0, E1 seccion 6 enmendada por
E2 v1 congelada, secciones 5 bis y 5 ter; SHA-256 de E2 d5bc75657e2055a093cf5523debb0e283578a1b8a192c924eb14242abc65f955).

EXPLORATORIO. No decide nada: ningun resultado modifica el veredicto confirmatorio de T2-A0 (primary_analysis.py). No asigna Y.
Las completaciones de desenlaces no determinados (ND) son escenarios hipoteticos, no recuperacion de un Y latente.
BLOQUEADO para datos reales hasta cumplir E2 5 ter.3 (pruebas por enumeracion superadas y hashes registrados en manifiesto).

Entrada: CSV con una fila por trayectoria elegible y columnas split, trajectory, X, Y (Y en {1, 0, ND}); opcional causa_ND.
Cola y bootstrap: identicos a primary_analysis.py del prerregistro (SHA-256 817a1783...): cola = X >= sort(X)[-ceil(0.1 N)]
(empates completos); remuestreo de splits completos con np.random.default_rng(220020), bloques en orden np.unique(split),
rng.integers(0, S, S) por replica; percentiles 2.5/97.5 por interpolacion lineal.

Uso:  python -I seccion6_sensibilidad.py --entrada trayectorias.csv --salida resultado_seccion6.json
"""
import argparse, csv, json, math
from fractions import Fraction as F
import numpy as np

TAIL_Q, REPS, SEED = 0.10, 20000, 220020
ETIQUETA_ENVOLVENTE = "envolvente exploratoria de remuestreo de cotas; cobertura nominal no validada"
CRITERIO5 = "NO EVALUADO POR ESTE METODO"


# ---------------- cola (identica a primary_analysis.tail) ----------------
def cola(x):
    x = np.asarray(x, float)
    if len(x) == 0:
        return np.zeros(0, bool)
    if not np.isfinite(x).all():
        raise ValueError("X no finito")
    cutoff = np.sort(x)[-int(np.ceil(TAIL_Q * len(x)))]
    return x >= cutoff


# ---------------- conteos y extremos exactos (E2 5 bis, punto 1) ----------------
def conteos(x, y):
    """y: array de objetos en {1, 0, 'ND'}. Devuelve N, m, a, b, u, v."""
    t = cola(x); y = np.asarray(y, object)
    pos, nd = (y == 1), (y == "ND")
    return dict(N=int(len(y)), m=int(t.sum()), a=int((pos & t).sum()), b=int((pos & ~t).sum()), u=int((nd & t).sum()), v=int((nd & ~t).sum()))


def extremos(c):
    """Extremos exactos (Fraction) sobre todas las completaciones binarias. None = metrica no definida."""
    N, m, a, b, u, v = c["N"], c["m"], c["a"], c["b"], c["u"], c["v"]
    r = dict(precision=None, base=None, diferencia=None, lift=None, lift_restringido=None,
             lift_definido_en_todas=False, completaciones_lift_indefinido=0)
    if N == 0 or m == 0:
        return r
    r["precision"] = (F(a, m), F(a + u, m))
    r["base"] = (F(a + b, N), F(a + b + u + v, N))
    r["diferencia"] = (F(a, m) - F(a + b + v, N), F(a + u, m) - F(a + b + u, N))
    if a + b > 0:
        r["lift"] = (F(N * a, m * (a + b + v)), F(N * (a + u), m * (a + b + u)))
        r["lift_definido_en_todas"] = True
        r["lift_restringido"] = r["lift"]
    else:
        # a + b = 0: la completacion con todos los ND = 0 tiene tasa base 0 (lift indefinido). Extremos restringidos a tasa base > 0.
        r["completaciones_lift_indefinido"] = 1
        if u + v > 0:
            lo = F(0) if v > 0 else F(N, m)        # v>0: algun positivo solo fuera -> lift 0; si no, solo dentro -> N/m
            hi = F(N, m) if u > 0 else F(0)
            r["lift_restringido"] = (lo, hi)
    return r


def _signo(par, umbral=F(0)):
    if par is None:
        return "NO EVALUABLE"
    lo, hi = par
    if lo > umbral:
        return "POR ENCIMA BAJO TODAS"
    if hi < umbral:
        return "POR DEBAJO BAJO TODAS"
    return "NO DETERMINADO POR LAS COTAS"


# ---------------- criterios 3, 4, 6 (E2 5 bis, punto 8) ----------------
def criterio3(split, y):
    y = np.asarray(y, object); split = np.asarray(split)
    ev = int((y == 1).sum()); sp = int(len(np.unique(split[y == 1])))
    return dict(eventos_confirmados=ev, splits_con_evento=sp, cumple=bool(ev >= 30 and sp >= 10),
                nota="solo positivos confirmados; las completaciones pueden anadir positivos, no quitarlos")


def criterio4(ext):
    if not ext["lift_definido_en_todas"]:
        return dict(estado="NO EVALUABLE", motivo="lift no definido en alguna completacion (tasa base 0) o cola/cohorte vacia")
    lo, hi = ext["lift"]
    est = "CUMPLE BAJO TODAS" if lo >= 3 else ("NO CUMPLE BAJO NINGUNA" if hi < 3 else "NO DETERMINADO POR LAS COTAS")
    return dict(estado=est, lift_min=float(lo), lift_max=float(hi))


def criterio6(split, x, y):
    split = np.asarray(split); x = np.asarray(x, float); y = np.asarray(y, object); por = []
    for s in np.unique(split):
        k = split != s; e = extremos(conteos(x[k], y[k])); d = e["diferencia"]
        por.append(dict(split=str(s), diferencia_min=float(d[0]) if d else None, diferencia_max=float(d[1]) if d else None))
    mins = [p["diferencia_min"] for p in por]
    if not por or any(m is None for m in mins):
        est = "NO EVALUABLE"
    else:
        est = "CUMPLE BAJO TODAS" if min(mins) > 0 else "NO CUMPLE BAJO TODAS (existencia de una completacion que cumpla: no evaluada)"
    return dict(estado=est, por_split=por)


# ---------------- bootstrap de splits completos ----------------
def indices_bootstrap(split, reps=REPS, seed=SEED):
    """Mismos sorteos que primary_analysis.evaluate: bloques en orden np.unique(split), rng.integers(0, S, S) por replica."""
    split = np.asarray(split); groups = np.unique(split); blocks = [np.flatnonzero(split == s) for s in groups]
    rng = np.random.default_rng(seed)
    for _ in range(reps):
        yield np.concatenate([blocks[i] for i in rng.integers(0, len(blocks), len(blocks))])


def envolvente(split, x, y, reps=REPS, seed=SEED):
    x = np.asarray(x, float); y = np.asarray(y, object)
    L = {k: [] for k in ("precision", "base", "diferencia", "lift_restringido")}; U = {k: [] for k in L}
    no_def = {k: 0 for k in L}; rep_lift_indef = 0; rep_cola_15 = 0
    for ix in indices_bootstrap(split, reps, seed):
        c = conteos(x[ix], y[ix]); e = extremos(c)
        rep_cola_15 += c["m"] > 0.15 * c["N"]
        if not e["lift_definido_en_todas"]:
            rep_lift_indef += 1
        for k in L:
            if e[k] is None:
                no_def[k] += 1
            else:
                L[k].append(float(e[k][0])); U[k].append(float(e[k][1]))
    out = {}
    for k in L:
        if no_def[k] or not L[k]:
            out[k] = dict(estado="NO EVALUABLE", replicas_no_definidas=no_def[k])
        else:
            out[k] = dict(inferior=float(np.quantile(L[k], 0.025, method="linear")), superior=float(np.quantile(U[k], 0.975, method="linear")),
                          replicas_no_definidas=0)
    if rep_lift_indef:
        out["lift"] = dict(estado="NO EVALUABLE", replicas_con_lift_indefinido_en_alguna_completacion=rep_lift_indef)
    else:
        out["lift"] = dict(out["lift_restringido"])   # sin indefinidos, restringido == global
    out["lift_restringido"]["nota"] = "restringido a completaciones con tasa base > 0 (declarado; no son extremos sobre todas las completaciones)"
    return dict(etiqueta=ETIQUETA_ENVOLVENTE, replicas=reps, semilla=seed, replicas_con_cola_mayor_15pct=int(rep_cola_15), metricas=out)


# ---------------- analisis completo ----------------
def analizar(split, x, y, causa=None, reps=REPS, seed=SEED):
    split = np.asarray(split); x = np.asarray(x, float); y = np.asarray(y, object)
    if not (len(split) == len(x) == len(y)):
        raise ValueError("longitudes distintas")
    if not all(v in (0, 1, "ND") for v in y):
        raise ValueError("Y fuera de {1, 0, ND}")
    c = conteos(x, y); e = extremos(c); t = cola(x)
    fr = lambda p: None if p is None else [float(p[0]), float(p[1])]
    nd_split = {str(s): int(((split == s) & (y == "ND")).sum()) for s in np.unique(split)}
    res = dict(
        nombre="analisis exploratorio de sensibilidad por completaciones binarias",
        advertencia=("Exploratorio. No modifica el veredicto confirmatorio de T2-A0. Las completaciones son escenarios hipoteticos. "
                     "La envolvente no es un intervalo de confianza del 95 %."),
        conteos=c, cola_mayor_15pct=bool(c["m"] > 0.15 * c["N"]) if c["N"] else None,
        fraccion_cola_ND=(c["u"] / c["m"]) if c["m"] else None,
        nd_por_split=nd_split,
        extremos=dict(precision=fr(e["precision"]), base=fr(e["base"]), diferencia=fr(e["diferencia"]), lift=fr(e["lift"]),
                      lift_restringido=fr(e["lift_restringido"]), lift_definido_en_todas=e["lift_definido_en_todas"],
                      completaciones_con_lift_indefinido=e["completaciones_lift_indefinido"]),
        signo_diferencia=_signo(e["diferencia"]), lift_frente_a_3=(_signo(e["lift"], F(3)) if e["lift_definido_en_todas"] else "NO EVALUABLE"),
        criterio3=criterio3(split, y), criterio4=criterio4(e), criterio5=CRITERIO5, criterio6=criterio6(split, x, y),
        envolvente=envolvente(split, x, y, reps, seed))
    if causa is not None:
        causa = np.asarray(causa, object)
        res["nd_por_causa"] = {str(k): int(((y == "ND") & (causa == k)).sum()) for k in sorted(set(causa[y == "ND"]))}
    return res


def leer_csv(path):
    split, x, y, causa = [], [], [], []
    with open(path, newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh); tiene_causa = "causa_ND" in (rd.fieldnames or [])
        for r in rd:
            split.append(r["split"]); x.append(float(r["X"]))
            yy = r["Y"].strip(); y.append("ND" if yy.upper() == "ND" else int(yy))
            causa.append(r.get("causa_ND", ""))
    return split, x, y, (causa if tiene_causa else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", required=True); ap.add_argument("--salida", required=True)
    a = ap.parse_args()
    split, x, y, causa = leer_csv(a.entrada)
    res = analizar(split, x, y, causa)
    with open(a.salida, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False)
    print(json.dumps({k: res[k] for k in ("conteos", "extremos", "signo_diferencia", "lift_frente_a_3", "criterio5")}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
