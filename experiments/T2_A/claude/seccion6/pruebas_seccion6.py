"""pruebas_seccion6.py - pruebas por enumeracion exhaustiva de seccion6_sensibilidad.py (E2 v1, 5 ter.3, punto 2).

Oraculo: enumera TODAS las completaciones binarias de los ND (2^n_ND vectores; una trayectoria duplicada por el remuestreo
conserva un unico valor en cada completacion), calcula precision, tasa base, diferencia y lift en aritmetica racional y toma
minimos y maximos. Criterio de aprobacion: coincidencia exacta (Fraction) en extremos; <= 1e-12 en cuantiles de la envolvente.

Uso:  python -I pruebas_seccion6.py --primary <ruta a primary_analysis.py del prerregistro>
"""
import argparse, importlib.util, itertools, json, math, random, sys
from fractions import Fraction as F
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import seccion6_sensibilidad as S6

FALLOS = []; CUENTA = {"casos": 0}


def ok(cond, msg):
    CUENTA["casos"] += 1
    if not cond:
        FALLOS.append(msg)


# ---------------- oraculo ----------------
def oraculo(x, y, ident=None):
    """x, y de la muestra (posiblemente con duplicados); ident = identificador de trayectoria original (para empatar copias)."""
    x = np.asarray(x, float); y = list(y); n = len(y)
    ident = list(range(n)) if ident is None else list(ident)
    if n == 0:
        return dict(precision=None, base=None, diferencia=None, lift=None, lift_restringido=None, indef=0, todas=False)
    t = S6.cola(x); m = int(t.sum())
    nds = sorted({ident[i] for i in range(n) if y[i] == "ND"})
    P, B, D, Ld, indef = [], [], [], [], 0
    for bits in itertools.product((0, 1), repeat=len(nds)):
        asg = dict(zip(nds, bits)); yy = [asg[ident[i]] if y[i] == "ND" else y[i] for i in range(n)]
        tp = sum(yy[i] for i in range(n) if t[i]); tot = sum(yy)
        p, bb = F(tp, m), F(tot, n); P.append(p); B.append(bb); D.append(p - bb)
        if tot == 0:
            indef += 1
        else:
            Ld.append(p / bb)
    mm = lambda s: (min(s), max(s)) if s else None
    return dict(precision=mm(P), base=mm(B), diferencia=mm(D), lift=(mm(Ld) if indef == 0 else None),
                lift_restringido=mm(Ld), indef=indef, todas=(indef == 0))


def comparar(x, y, etiqueta, ident=None):
    e = S6.extremos(S6.conteos(x, y)); o = oraculo(x, y, ident)
    for k in ("precision", "base", "diferencia", "lift", "lift_restringido"):
        ok(e[k] == o[k], f"{etiqueta}: {k} script={e[k]} oraculo={o[k]}")
    ok(e["lift_definido_en_todas"] == o["todas"], f"{etiqueta}: lift_definido_en_todas")
    ok(e["completaciones_lift_indefinido"] == o["indef"], f"{etiqueta}: completaciones con lift indefinido {e['completaciones_lift_indefinido']} vs {o['indef']}")


def caso_aleatorio(rng, n, n_nd, ties):
    x = [rng.randint(0, 3) if ties else rng.random() for _ in range(n)]
    y = [rng.choice([0, 1]) for _ in range(n)]
    for i in rng.sample(range(n), n_nd):
        y[i] = "ND"
    return x, y


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--primary", required=True); a = ap.parse_args()
    spec = importlib.util.spec_from_file_location("primary_analysis", a.primary); PA = importlib.util.module_from_spec(spec); spec.loader.exec_module(PA)
    rng = random.Random(20261021)

    # 1. cola identica a la del prerregistro, con y sin empates
    for i in range(300):
        n = rng.randint(1, 60); x = [rng.randint(0, 4) if i % 2 else rng.random() for _ in range(n)]
        ok(np.array_equal(S6.cola(x), PA.tail(x)), f"cola distinta de primary_analysis.tail (caso {i})")

    # 2. aleatorios: desconocidos dentro, fuera o ambos; con y sin empates de X en el borde
    for i in range(600):
        n = rng.randint(1, 14); x, y = caso_aleatorio(rng, n, rng.randint(0, min(n, 10)), ties=(i % 2 == 0))
        comparar(x, y, f"aleatorio {i}")

    # 3. casos dirigidos
    dirigidos = {
        "ND solo dentro": ([9, 8, 1, 1, 1, 1, 1, 1, 1, 1], ["ND", 1, 0, 1, 0, 0, 1, 0, 0, 0]),
        "ND solo fuera": ([9, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, "ND", "ND", 0, 0, 1, 0, 0, 0, "ND"]),
        "ND ambos lados": ([9, 8, 1, 1, 1, 1, 1, 1, 1, 1], ["ND", "ND", "ND", 0, 1, 0, 0, "ND", 0, 0]),
        "tasa base 0 posible (a+b=0, ND dentro y fuera)": ([9, 1, 1, 1, 1], ["ND", 0, "ND", 0, 0]),
        "tasa base 0 posible (a+b=0, ND solo dentro)": ([9, 1, 1, 1, 1], ["ND", 0, 0, 0, 0]),
        "tasa base 0 posible (a+b=0, ND solo fuera)": ([9, 1, 1, 1, 1], [0, "ND", 0, 0, 0]),
        "tasa base 0 obligatoria (sin ND, sin positivos)": ([9, 1, 1, 1], [0, 0, 0, 0]),
        "empate en el borde de la cola": ([5, 5, 5, 1, 1, 1, 1, 1, 1, 1, 1, 1], ["ND", 0, 1, 0, 0, 0, "ND", 1, 0, 0, 0, 0]),
        "todas las X iguales": ([2] * 8, ["ND", 0, 1, 0, "ND", 0, 0, 1]),
        "una sola trayectoria ND": ([3.0], ["ND"]),
    }
    for k, (x, y) in dirigidos.items():
        comparar(x, y, k)
    ok(S6.cola([5, 5, 5, 1, 1, 1, 1, 1, 1, 1, 1, 1]).sum() == 3, "empate en el borde: la cola debe incluir los 3 empatados")

    # 4. cohorte / cola vacia: nada definido y sin excepcion
    e = S6.extremos(S6.conteos([], []))
    ok(all(e[k] is None for k in ("precision", "base", "diferencia", "lift", "lift_restringido")), "cohorte vacia: todo debe ser None")
    ok(S6.criterio4(e)["estado"] == "NO EVALUABLE", "cohorte vacia: criterio 4 NO EVALUABLE")

    # 5. bloques con multiplicidad: una replica fija (un split 3 veces, otro ausente) frente al oraculo con copias empatadas
    split = ["s1"] * 3 + ["s2"] * 3 + ["s3"] * 3 + ["s4"] * 2
    x = [9, 2, 1, 8, 3, 1, 7, 2, 2, 6, 1]; y = ["ND", 0, 1, 1, "ND", 0, 0, "ND", 0, 1, "ND"]
    blocks = {s: [i for i, z in enumerate(split) if z == s] for s in sorted(set(split))}
    for rep in (["s1", "s1", "s1", "s3"], ["s2", "s4", "s4", "s4"], ["s3", "s3", "s1", "s2"]):
        ix = [i for s in rep for i in blocks[s]]
        comparar([x[i] for i in ix], [y[i] for i in ix], f"replica {rep}", ident=ix)
    #    y las replicas que produce el script coinciden con los sorteos de primary_analysis (mismo rng, mismos bloques)
    sp = np.asarray(split); groups = np.unique(sp); bl = [np.flatnonzero(sp == s) for s in groups]; r2 = np.random.default_rng(S6.SEED)
    for k, ix in enumerate(S6.indices_bootstrap(split, reps=50)):
        ref = np.concatenate([bl[i] for i in r2.integers(0, len(bl), len(bl))])
        ok(np.array_equal(ix, ref), f"replica bootstrap {k} distinta del sorteo de primary_analysis")

    # 6. envolvente: oraculo por replica + cuantil lineal; y sin ND debe igualar el IC95 de primary_analysis.evaluate
    rs = np.random.default_rng(7); n_s = 6
    split = np.repeat([f"s{i}" for i in range(n_s)], 4); x = rs.integers(0, 6, len(split)).astype(float)
    y = [int(v) for v in rs.integers(0, 2, len(split))]
    for i in (1, 5, 9, 14, 22):
        y[i] = "ND"
    reps = 300; env = S6.envolvente(split, x, y, reps=reps)
    Lo = {k: [] for k in ("precision", "base", "diferencia")}; Up = {k: [] for k in Lo}
    for ix in S6.indices_bootstrap(split, reps=reps):
        o = oraculo(x[ix], [y[i] for i in ix], ident=list(ix))
        for k in Lo:
            Lo[k].append(float(o[k][0])); Up[k].append(float(o[k][1]))
    for k in Lo:
        q0, q1 = np.quantile(Lo[k], .025, method="linear"), np.quantile(Up[k], .975, method="linear")
        g = env["metricas"][k]
        ok(abs(g["inferior"] - q0) <= 1e-12 and abs(g["superior"] - q1) <= 1e-12, f"envolvente {k}: {g} vs ({q0}, {q1})")
    ok(env["etiqueta"] == S6.ETIQUETA_ENVOLVENTE, "etiqueta de la envolvente")
    #    sin ND: la envolvente colapsa al IC percentil del analisis primario (mismo bootstrap). Datos que pasan sus compuertas.
    rs = np.random.default_rng(11); S = 130; split2 = np.repeat(np.arange(S), 5); x2 = rs.random(len(split2))
    y2 = (rs.random(len(split2)) < 0.03 + 0.25 * (x2 > 0.9)).astype(int)
    pa = PA.evaluate(split2, x2, y2, reps=200)
    ok("CI95_precision" in pa, f"datos de control no pasan las compuertas de primary_analysis: {pa.get('reason')}")
    if "CI95_precision" in pa:
        env2 = S6.envolvente(split2, x2, list(y2), reps=200)["metricas"]
        for k, kk in (("precision", "CI95_precision"), ("base", "CI95_base"), ("diferencia", "CI95_delta")):
            ok(abs(env2[k]["inferior"] - pa[kk][0]) <= 1e-12 and abs(env2[k]["superior"] - pa[kk][1]) <= 1e-12,
               f"sin ND, envolvente {k} {env2[k]} distinta del IC de primary_analysis {pa[kk]}")
        p6 = S6.criterio6(split2, x2, list(y2))
        ok(abs(min(d["diferencia_min"] for d in p6["por_split"]) - pa["min_leave_split_out_delta"]) <= 1e-12, "criterio 6 sin ND distinto de primary_analysis")
    #    lift indefinido en alguna replica -> NO EVALUABLE y contado, sin eliminar replicas
    split3 = ["a"] * 3 + ["b"] * 3; x3 = [5, 1, 1, 4, 1, 1]; y3 = ["ND", 0, 0, 1, 0, 0]
    env3 = S6.envolvente(split3, x3, y3, reps=200)["metricas"]
    ok(env3["lift"]["estado"] == "NO EVALUABLE" and env3["lift"]["replicas_con_lift_indefinido_en_alguna_completacion"] > 0,
       "lift indefinido en replicas: debe ser NO EVALUABLE y contarse")

    # 7. criterio 6 (retirada de cada split, cola recalculada) frente al oraculo
    for i in range(80):
        nsp = rng.randint(2, 4); split = [f"s{j % nsp}" for j in range(rng.randint(nsp, 10))]
        x, y = caso_aleatorio(rng, len(split), rng.randint(0, min(len(split), 7)), ties=(i % 2 == 0))
        c6 = S6.criterio6(split, x, y)
        for d in c6["por_split"]:
            k = [j for j, s in enumerate(split) if s != d["split"]]
            o = oraculo([x[j] for j in k], [y[j] for j in k])
            exp = None if o["diferencia"] is None else float(o["diferencia"][0])
            ok(d["diferencia_min"] == exp, f"criterio 6 caso {i} split {d['split']}: {d['diferencia_min']} vs {exp}")

    # 8. criterio 4 y criterio 5
    for i in range(200):
        n = rng.randint(1, 12); x, y = caso_aleatorio(rng, n, rng.randint(0, min(n, 8)), ties=True)
        o = oraculo(x, y); c4 = S6.criterio4(S6.extremos(S6.conteos(x, y)))
        if not o["todas"]:
            exp = "NO EVALUABLE"
        else:
            lo, hi = o["lift"]; exp = "CUMPLE BAJO TODAS" if lo >= 3 else ("NO CUMPLE BAJO NINGUNA" if hi < 3 else "NO DETERMINADO POR LAS COTAS")
        ok(c4["estado"] == exp, f"criterio 4 caso {i}: {c4['estado']} vs {exp}")
    res = S6.analizar(["a", "a", "b", "b"], [3, 1, 2, 1], ["ND", 0, 1, 0], reps=20)
    ok(res["criterio5"] == "NO EVALUADO POR ESTE METODO", "criterio 5 debe declararse NO EVALUADO POR ESTE METODO")

    print(json.dumps(dict(comprobaciones=CUENTA["casos"], fallos=len(FALLOS), detalle=FALLOS[:20],
                          veredicto="PASA" if not FALLOS else "FALLA"), indent=2, ensure_ascii=False))
    sys.exit(0 if not FALLOS else 1)


if __name__ == "__main__":
    main()
