"""rho_borde.py (v1, fase 0a' de T2-A1; borrador v3 del diseno). Instrumento del desenlace rho_borde.

rho_borde(M, f) = min_u int_0^inf sqrt(u^T G(s u) u) ds, G = J^T M J de la familia softmax (geometry.py b4d1e0e4..., sin
cambios). Mismo calculo que diagnostico_degeneracion.py (commit 032a1d7), extraido sin cambios numericos:
  1) Gauss-Legendre (orden 800) en s = S0 x/(1-x), S0 = 10, sobre 1440 direcciones uniformes;
  2) minimo refinado con scipy quad (epsrel 1e-10) y busqueda acotada en el angulo (+-1 paso angular, xatol 1e-9);
  3) diagnosticos de estabilidad: orden 400 y 720 direcciones.
Funcion publica: rho_borde(M, f) -> dict. Uso por lotes: python -I rho_borde.py --lista estados.csv --geometry <dir> --out <dir>
"""
import argparse, csv, hashlib, json, math, sys, time
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize_scalar

GEOM_SHA = "b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3"
S0, NDIR, ORDEN = 10.0, 1440, 800
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
_G = {}


def _geometria(gdir):
    if "Geometry" not in _G:
        gdir = Path(gdir)
        if sha(gdir / "geometry.py") != GEOM_SHA:
            sys.exit("ABORTA: geometry.py no coincide")
        sys.path.insert(0, str(gdir)); from geometry import Geometry
        _G["Geometry"] = Geometry
    return _G["Geometry"]


def integrando(g, U, s):
    m, k = len(U), len(s)
    P = (U[:, None, :] * s[None, :, None]).reshape(-1, 2); out = np.empty(len(P)); UU = np.repeat(U, k, axis=0)
    for i in range(0, len(P), 20000):
        J = g.jac(P[i:i + 20000]); Ju = np.einsum("bni,bi->bn", J, UU[i:i + 20000])
        out[i:i + 20000] = np.sqrt(np.maximum(np.einsum("bn,nm,bm->b", Ju, g.M, Ju), 0.0))
    return out.reshape(m, k)


def rho_gl(g, U, orden):
    x, w = np.polynomial.legendre.leggauss(orden); x = (x + 1) / 2; w = w / 2
    return integrando(g, U, S0 * x / (1 - x)) @ (w * S0 / (1 - x) ** 2)


def rho_quad(g, th):
    u = np.array([math.cos(th), math.sin(th)])
    return quad(lambda s: float(integrando(g, u[None], np.array([s]))[0, 0]), 0, np.inf, epsabs=0, epsrel=1e-10, limit=1000)


def rho_borde(g, ndir=NDIR, orden=ORDEN):
    th = np.arange(ndir) * 2 * np.pi / ndir; U = np.stack([np.cos(th), np.sin(th)], 1)
    r = rho_gl(g, U, orden); i = int(np.argmin(r)); d = 2 * np.pi / ndir
    opt = minimize_scalar(lambda t: rho_quad(g, t)[0], bounds=(th[i] - d, th[i] + d), method="bounded", options=dict(xatol=1e-9))
    v, err = rho_quad(g, opt.x)
    th2 = np.arange(ndir // 2) * 2 * np.pi / (ndir // 2); U2 = np.stack([np.cos(th2), np.sin(th2)], 1)
    return dict(rho_borde=float(v), err_quad=float(err), theta=float(opt.x), rho_min_gl=float(r.min()),
                dif_orden=float(abs(rho_gl(g, U, orden // 2).min() - r.min()) / v), dif_dir=float(abs(rho_gl(g, U2, orden).min() - r.min()) / v),
                rho_mediana=float(np.median(r)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lista", required=True); ap.add_argument("--geometry", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(); Geometry = _geometria(a.geometry); out = Path(a.out); out.mkdir(parents=True, exist_ok=True); filas = []
    for row in csv.DictReader(open(a.lista, encoding="utf-8")):
        h = sha(row["npz"])
        if row.get("sha256_esperado") and row["sha256_esperado"] != h:
            sys.exit(f"ABORTA: hash de {row['npz']}")
        with np.load(row["npz"]) as z:
            M, f = np.array(z["M"], float), np.array(z["f"], float)
        t0 = time.perf_counter(); R = rho_borde(Geometry(M, f))
        R.update(trajectory=row["trajectory"], update=row["update"], npz_sha256=h, segundos=round(time.perf_counter() - t0, 1)); filas.append(R)
        print(f"{row['trajectory']} u{row['update']}: {R['rho_borde']:.6g}", flush=True)
    with open(out / "rho_borde.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0])); w.writeheader(); w.writerows(filas)
    (out / "rho_borde.json").write_text(json.dumps(dict(script_sha256=sha(Path(__file__)), geometry_sha256=GEOM_SHA, filas=filas), indent=2))


if __name__ == "__main__":
    main()
