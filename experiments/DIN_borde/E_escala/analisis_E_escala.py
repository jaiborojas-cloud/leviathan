"""analisis_E_escala.py - DIN-E-escala (exploratorio, plan PLAN_E_escala_v1.md). Cruza la escala de logits en u250 (escala_u250.csv de
cada cohorte) con los resultados CONGELADOS de Q13-DR y Q13-M2 (D y c por nivel) y con las tablas de cohorte (para E2).
Uso: python3 -I analisis_E_escala.py --escala-dr <csv> --escala-m2 <csv> --out <dir>
"""
import argparse, csv, hashlib, json, math, sys
from pathlib import Path
import numpy as np
H = Path(__file__).resolve().parent; DB = H.parent
sys.path.insert(0, str(DB / "C1")); import analisis_C1_v2 as A
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rk(v):
    v = np.asarray(v, float); o = np.argsort(v, kind="mergesort"); r = np.empty(len(v)); i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]: j += 1
        r[o[i:j + 1]] = (i + j) / 2 + 1; i = j + 1
    return r


def sp(a, b): return float(np.corrcoef(rk(a), rk(b))[0, 1])


def parcial(y, x, z):
    ry, rx, rz = rk(y), rk(x), rk(z); Z = np.column_stack([np.ones(len(rz)), rz])
    ey = ry - Z @ np.linalg.lstsq(Z, ry, rcond=None)[0]; ex = rx - Z @ np.linalg.lstsq(Z, rx, rcond=None)[0]
    return float(np.corrcoef(ey, ex)[0, 1])


def leer_escala(p):
    return {r["trajectory"]: r for r in csv.DictReader(open(p)) if not r["error"]}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--escala-dr", required=True); ap.add_argument("--escala-m2", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    edr, em2 = leer_escala(a.escala_dr), leer_escala(a.escala_m2)
    rdr = json.load(open(DB / "Q13DR" / "resultado" / "RESULTADO_Q13DR.json")); rm2 = json.load(open(DB / "Q13M2" / "resultado" / "RESULTADO_Q13M2.json"))
    # ---- E1: por nivel
    niveles = []
    for i in range(6):
        nv = f"L{i}"; ids = [t for t in edr if t.split("_")[1] == nv]
        niveles.append(dict(nivel=f"DR_{nv}", familia="A0" if i == 0 else "LS", D=rdr["primaria"][nv]["D"], c=rdr["bootstrap"]["c_comunes"][i],
                            S=float(np.median([float(edr[t]["S"]) for t in ids])), m=float(np.median([float(edr[t]["m"]) for t in ids])),
                            p=float(np.median([float(edr[t]["p"]) for t in ids])), n=len(ids)))
    for man in ("LP", "WD"):
        nvs = ["A0"] + [f"{man}{j}" for j in range(1, 6)]
        for j, nv in enumerate(nvs):
            if man == "WD" and nv == "A0": continue
            ids = [t for t in em2 if t.split("_")[1] == nv]
            niveles.append(dict(nivel=f"M2_{nv}", familia="A0" if nv == "A0" else man, D=rm2["primaria"][nv]["D"], c=rm2["por_manipulador"][man]["c_comunes"][j],
                                S=float(np.median([float(em2[t]["S"]) for t in ids])), m=float(np.median([float(em2[t]["m"]) for t in ids])),
                                p=float(np.median([float(em2[t]["p"]) for t in ids])), n=len(ids)))
    D = np.array([x["D"] for x in niveles]); c = np.array([x["c"] for x in niveles]); S = np.array([x["S"] for x in niveles])
    m = np.array([x["m"] for x in niveles]); p = np.array([x["p"] for x in niveles])
    z = lambda v: (v - v.mean()) / v.std()
    Xm = np.column_stack([np.ones(len(D)), z(c), z(S)]); coef = np.linalg.lstsq(Xm, D, rcond=None)[0]
    e1 = dict(n_niveles=len(D), spearman_D_c=sp(D, c), spearman_D_S=sp(D, S), spearman_c_S=sp(c, S), spearman_D_m=sp(D, m), spearman_D_p=sp(D, p),
              parcial_D_c_dado_S=parcial(D, c, S), parcial_D_S_dado_c=parcial(D, S, c), mco_estandarizado=dict(c=float(coef[1]), S=float(coef[2])),
              niveles=niveles)
    # ---- E2: dentro de los controles sin manipular, D por cuartiles de c y de S
    def cohorte(path, pref):
        return {r["trajectory"]: r for r in csv.DictReader(open(path)) if r["trajectory"].split("_")[1] == pref and not r["error"]}
    e2 = {}
    for nombre, tabla, esc, pref in (("DR_L0", DB / "Q13DR" / "cohorte_q13dr" / "q13dr_cohorte.csv", edr, "L0"),
                                     ("M2_A0", DB / "Q13M2" / "cohorte_q13m2" / "q13m2_cohorte.csv", em2, "A0")):
        filas = cohorte(tabla, pref); ids = [t for t in filas if t in esc]
        spl = np.array([int(t.split("_")[2][1:]) for t in ids]); X = np.array([float(filas[t]["X10"]) for t in ids])
        L = np.log([float(filas[t]["rho_caras_10"]) for t in ids]); Y = np.log([float(filas[t]["rho_caras_250"]) for t in ids])
        cv = np.array([float(filas[t]["c250"]) for t in ids]); Sv = np.array([float(esc[t]["S"]) for t in ids])
        res = dict(n=len(ids), spearman_c_S_trayectorias=sp(cv, Sv))
        for var, v in (("c", cv), ("S", Sv)):
            qs = np.quantile(v, [.25, .5, .75]); cu = np.digitize(v, qs); out = {}
            for k in range(4):
                msk = cu == k; ok = [s for s in np.unique(spl[msk]) if (spl[msk] == s).sum() >= 3]; mm = msk & np.isin(spl, ok)
                out[f"Q{k + 1}"] = dict(n=int(mm.sum()), splits=len(ok), D=A.primaria(spl[mm], X[mm], L[mm], Y[mm], 3, 880101 + k, 499)["D"] if len(ok) >= 10 else None)
            out["gradiente_Q4_menos_Q1"] = (out["Q4"]["D"] - out["Q1"]["D"]) if out["Q4"]["D"] is not None and out["Q1"]["D"] is not None else None
            res[f"por_cuartil_{var}"] = out
        e2[nombre] = res
    # ---- lectura (regla del plan)
    dif = e1["parcial_D_c_dado_S"] - e1["parcial_D_S_dado_c"]
    g = [(e2[k]["por_cuartil_c"]["gradiente_Q4_menos_Q1"], e2[k]["por_cuartil_S"]["gradiente_Q4_menos_Q1"]) for k in e2]
    e2_c = all(gc is not None and gs is not None and abs(gc) > abs(gs) for gc, gs in g); e2_S = all(gc is not None and gs is not None and abs(gs) > abs(gc) for gc, gs in g)
    lectura = "C_SIGUE_MEJOR_A_D" if (dif >= 0.2 and e2_c) else ("S_SIGUE_MEJOR_A_D" if (dif <= -0.2 and e2_S) else "NO_SE_SEPARAN_CON_ESTOS_DATOS")
    res = dict(E1=e1, E2=e2, diferencia_parciales=dif, E2_gradiente_c_mayor_en_ambos=e2_c, E2_gradiente_S_mayor_en_ambos=e2_S, lectura=lectura,
               escala_dr_sha256=sha(a.escala_dr), escala_m2_sha256=sha(a.escala_m2), script_sha256=sha(Path(__file__)))
    o = Path(a.out); o.mkdir(parents=True, exist_ok=True)
    with open(o / "RESULTADO_E_escala.json", "x") as fh: fh.write(json.dumps(res, indent=2, ensure_ascii=False))
    print(json.dumps({k: v for k, v in res.items() if k not in ("E1", "E2")}, indent=2)); print(json.dumps({k: v for k, v in e1.items() if k != "niveles"}, indent=2))
    for x in niveles: print(x["nivel"], x["familia"], round(x["c"], 3), round(x["S"], 3), round(x["m"], 3), round(x["p"], 4), round(x["D"], 4))
    print(json.dumps(e2, indent=1))


if __name__ == "__main__":
    main()
