"""pruebas_rho_borde.py - controles de la fase 0a' para rho_borde.py (no usan X; usan estados de desarrollo y sinteticos).
C1 cambio lineal de carta (f -> f A): rho invariante.  C2 traslacion del panel (f -> f + c): invariante.
C3 escala (M -> c M): rho escala con sqrt(c).  C4 contraste independiente en mpmath (50 digitos) de rho(u) en 4 direcciones.
C5 reproduccion exacta del diagnostico (commit 032a1d7) en los 80 estados de desarrollo.  C6 T* <= rho en los 8 escapes medidos.
Uso: python -I pruebas_rho_borde.py --geometry <dir> --lista ../diagnostico/lista_estados.csv --diag ../diagnostico/resultados/diagnostico.csv --out <dir>
"""
import argparse, csv, json, math, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rho_borde as RB

T_ESC = {("split8_j5_true", "50"): 0.01697, ("split8_j7_true", "50"): 0.01302, ("split8_j9_true", "50"): 0.01617,
         ("split8_j9_true", "150"): 0.00929, ("split8_j9_true", "250"): 0.00729,
         ("split8_j5_true", "25"): 0.07447464619553969, ("split8_j7_true", "25"): 0.07466422956747366, ("split8_j8_true", "25"): 0.08746544626359999}


def rho_u_mp(M, f, th, dps=50):
    import mpmath as mp
    mp.mp.dps = dps; Mm = mp.matrix(M.tolist()); n = len(f); u = (mp.cos(th), mp.sin(th))
    def integ(s):
        z = [s * (u[0] * f[k, 0] + u[1] * f[k, 1]) for k in range(n)]; zm = max(z); e = [mp.exp(x - zm) for x in z]; Z = mp.fsum(e); a = [x / Z for x in e]
        mf = [mp.fsum(a[k] * f[k, c] for k in range(n)) for c in range(2)]
        Ju = mp.matrix([a[k] * ((f[k, 0] - mf[0]) * u[0] + (f[k, 1] - mf[1]) * u[1]) for k in range(n)])
        return mp.sqrt(max((Ju.T * Mm * Ju)[0], 0))
    return mp.quad(integ, [0, 1, 10, 100, mp.inf])


def main():
    ap = argparse.ArgumentParser()
    for x in ("--geometry", "--lista", "--diag", "--out"):
        ap.add_argument(x, required=True)
    a = ap.parse_args(); G = RB._geometria(a.geometry); out = Path(a.out); out.mkdir(parents=True, exist_ok=True); res = {}
    filas = list(csv.DictReader(open(a.lista, encoding="utf-8"))); diag = {(d["trajectory"], d["update"]): d for d in csv.DictReader(open(a.diag, encoding="utf-8"))}
    cargar = lambda p: (lambda z: (np.array(z["M"], float), np.array(z["f"], float)))(np.load(p))
    rng = np.random.default_rng(20261024)
    # C1-C3 en 4 estados de regimenes distintos
    casos = [("split8_j5_true", "50"), ("split9_j10_true", "50"), ("split10_j15_true", "150"), ("split11_j20_true", "250")]
    c13 = []
    for t, k in casos:
        p = next(r["npz"] for r in filas if r["trajectory"] == t and r["update"] == k); M, f = cargar(p)
        r0 = RB.rho_borde(G(M, f))["rho_borde"]
        A = rng.normal(size=(2, 2)) + 2 * np.eye(2)
        r1 = RB.rho_borde(G(M, f @ A))["rho_borde"]; r2 = RB.rho_borde(G(M, f + rng.normal(size=2)))["rho_borde"]; r3 = RB.rho_borde(G(4.0 * M, f))["rho_borde"]
        c13.append(dict(estado=f"{t}/u{k}", rho=r0, C1_rel=abs(r1 - r0) / r0, C2_rel=abs(r2 - r0) / r0, C3_rel=abs(r3 - 2 * r0) / (2 * r0)))
    res["C1_C3"] = c13
    res["C1_ok"] = all(x["C1_rel"] <= 1e-6 for x in c13); res["C2_ok"] = all(x["C2_rel"] <= 1e-8 for x in c13); res["C3_ok"] = all(x["C3_rel"] <= 1e-8 for x in c13)
    # C4 mpmath en 4 direcciones del primer caso (incluida la del minimo)
    t, k = casos[0]; M, f = cargar(next(r["npz"] for r in filas if r["trajectory"] == t and r["update"] == k)); g = G(M, f); rb = RB.rho_borde(g)
    c4 = []
    for th in (rb["theta"], 0.0, 2.0, 4.0):
        v = RB.rho_quad(g, th)[0]; vm = float(rho_u_mp(M, f, th)); c4.append(dict(theta=th, float64=v, mp50=vm, rel=abs(v - vm) / vm))
    res["C4"] = c4; res["C4_ok"] = all(x["rel"] <= 1e-8 for x in c4)
    # C5 reproduccion del diagnostico y C6 cota frente a escapes
    c5 = []; c6 = []
    for r in filas:
        M, f = cargar(r["npz"]); v = RB.rho_borde(G(M, f))["rho_borde"]; d = float(diag[(r["trajectory"], r["update"])]["rho_borde"])
        c5.append(dict(estado=f"{r['trajectory']}/u{r['update']}", rho=v, diag=d, igual=(v == d)))
        if (r["trajectory"], r["update"]) in T_ESC:
            c6.append(dict(estado=f"{r['trajectory']}/u{r['update']}", rho=v, T_star=T_ESC[(r["trajectory"], r["update"])], ok=T_ESC[(r["trajectory"], r["update"])] <= v))
        print(c5[-1], flush=True)
    res["C5_ok"] = all(x["igual"] for x in c5); res["C5_distintos"] = [x for x in c5 if not x["igual"]]
    res["C6"] = c6; res["C6_ok"] = len(c6) == 8 and all(x["ok"] for x in c6)
    res["TODAS"] = all(res[k] for k in ("C1_ok", "C2_ok", "C3_ok", "C4_ok", "C5_ok", "C6_ok"))
    (out / "pruebas_rho_borde.json").write_text(json.dumps(res, indent=2)); print(json.dumps({k: v for k, v in res.items() if k.endswith("ok") or k == "TODAS"}, indent=2))


if __name__ == "__main__":
    main()
