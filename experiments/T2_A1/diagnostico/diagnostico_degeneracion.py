"""diagnostico_degeneracion.py (v1) - PROTOCOLO_diagnostico_degeneracion_v0.md. Exploratorio, muestra de desarrollo, sin X.

Para cada estado (M, f): panel (envolvente de f), M, metrica y K en el origen, y la cota superior de la distancia al borde
  rho(u) = int_0^inf sqrt(u^T G(s u) u) ds   (longitud metrica de la semirrecta P = s u de la carta),  rho_borde = min_u rho(u).
Primera pasada vectorizada (Gauss-Legendre en s = S0 x/(1-x)) sobre 720 y 1440 direcciones con dos ordenes; refinamiento del
minimo con scipy.integrate.quad (epsrel 1e-10) y busqueda acotada en el angulo. Usa geometry.py b4d1e0e4... sin cambios.

Uso: python -I diagnostico_degeneracion.py --lista estados.csv --geometry <carpeta instrument> --out <dir>
  estados.csv: trajectory,update,npz,sha256_esperado(opcional),regimen
"""
import argparse, csv, hashlib, json, math, sys, time
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize_scalar
from scipy.spatial import ConvexHull

GEOM_SHA = "b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3"
S0 = 10.0
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def integrando(g, U, s):
    """sqrt(u^T G(s u) u) para direcciones U (m,2) y escalares s (k,): devuelve (m,k)."""
    m, k = len(U), len(s)
    P = (U[:, None, :] * s[None, :, None]).reshape(-1, 2)
    out = np.empty(len(P))
    for i in range(0, len(P), 20000):
        Pi = P[i:i + 20000]; J = g.jac(Pi)                       # (b, n, 2)
        Ju = np.einsum("bni,bi->bn", J, np.repeat(U, k, axis=0)[i:i + 20000])
        out[i:i + 20000] = np.sqrt(np.maximum(np.einsum("bn,nm,bm->b", Ju, g.M, Ju), 0.0))
    return out.reshape(m, k)


def rho_gl(g, U, orden):
    x, w = np.polynomial.legendre.leggauss(orden); x = (x + 1) / 2; w = w / 2
    s = S0 * x / (1 - x); ds = S0 / (1 - x) ** 2
    return integrando(g, U, s) @ (w * ds)


def rho_quad(g, th):
    u = np.array([math.cos(th), math.sin(th)])
    f = lambda s: float(integrando(g, u[None], np.array([s]))[0, 0])
    v, err = quad(f, 0, np.inf, epsabs=0, epsrel=1e-10, limit=1000)
    return v, err


def un_estado(g, M, f):
    R = {}
    # panel y M
    hull = ConvexHull(f); vs = hull.vertices; poly = f[vs]
    edges = np.linalg.norm(np.roll(poly, -1, 0) - poly, axis=1)
    ang = []
    for i in range(len(poly)):
        a, b, c = poly[i - 1], poly[i], poly[(i + 1) % len(poly)]
        v1, v2 = a - b, c - b; ang.append(math.degrees(math.acos(np.clip(v1 @ v2 / np.linalg.norm(v1) / np.linalg.norm(v2), -1, 1))))
    ev = np.linalg.eigvalsh((M + M.T) / 2)
    R.update(f_sha=hashlib.sha256(np.ascontiguousarray(f).tobytes()).hexdigest()[:16], n=len(f), hull_vertices=len(vs),
             hull_edge_min=float(edges.min()), hull_edge_max=float(edges.max()), hull_angle_min=float(min(ang)),
             M_eig_min=float(ev[0]), M_eig_max=float(ev[-1]), M_cond=float(ev[-1] / ev[0]) if ev[0] > 0 else float("inf"))
    # origen
    G0 = g.jet(np.zeros((1, 2)))[0][0]; e0 = np.linalg.eigvalsh(G0); da, K0 = g.eval(np.zeros((1, 2)))
    R.update(G0_eig_min=float(e0[0]), G0_eig_max=float(e0[1]), G0_cond=float(e0[1] / e0[0]), sqrtdetG0=float(da[0]), K0=float(K0[0]))
    # rho(u)
    res = {}
    for nd in (720, 1440):
        th = np.arange(nd) * 2 * np.pi / nd; U = np.stack([np.cos(th), np.sin(th)], 1)
        for orden in (400, 800):
            r = rho_gl(g, U, orden); res[(nd, orden)] = (th, r)
    th, r = res[(1440, 800)]; i = int(np.argmin(r)); dth = 2 * np.pi / 1440
    opt = minimize_scalar(lambda t: rho_quad(g, t)[0], bounds=(th[i] - dth, th[i] + dth), method="bounded", options=dict(xatol=1e-9))
    rq, err = rho_quad(g, opt.x)
    u = np.array([math.cos(opt.x), math.sin(opt.x)])
    # componentes dominantes al 99 % de la longitud
    sgrid = np.linspace(0, 200, 20001); integ = integrando(g, u[None], sgrid)[0]; cum = np.concatenate([[0], np.cumsum((integ[1:] + integ[:-1]) / 2 * np.diff(sgrid))])
    s99 = float(sgrid[np.searchsorted(cum, 0.99 * cum[-1])]); P99 = s99 * u
    w = np.exp(P99 @ f.T - (P99 @ f.T).max()); w /= w.sum(); top = np.argsort(-w)[:3]
    R.update(rho_borde=float(rq), rho_quad_err=float(err), theta_min=float(opt.x),
             rho_min_gl={f"{nd}x{o}": float(v[1].min()) for (nd, o), v in res.items()},
             rho_gl_rel_dif_orden=float(abs(res[(1440, 800)][1].min() - res[(1440, 400)][1].min()) / rq),
             rho_gl_rel_dif_dir=float(abs(res[(1440, 800)][1].min() - res[(720, 800)][1].min()) / rq),
             rho_mediana=float(np.median(r)), rho_max=float(r.max()), s99=s99,
             dominantes=[int(x) for x in top], pesos_dominantes=[float(w[x]) for x in top],
             dominantes_en_hull=[bool(x in set(vs.tolist())) for x in top])
    return R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lista", required=True); ap.add_argument("--geometry", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    gdir = Path(a.geometry)
    if sha(gdir / "geometry.py") != GEOM_SHA:
        sys.exit("ABORTA: geometry.py no coincide")
    sys.path.insert(0, str(gdir)); from geometry import Geometry
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    filas = []
    for row in csv.DictReader(open(a.lista, encoding="utf-8")):
        h = sha(row["npz"])
        if row.get("sha256_esperado") and row["sha256_esperado"] != h:
            sys.exit(f"ABORTA: hash de {row['npz']}")
        with np.load(row["npz"]) as z:
            M, f = np.array(z["M"], float), np.array(z["f"], float)
        t0 = time.perf_counter(); R = un_estado(Geometry(M, f), M, f)
        R.update(trajectory=row["trajectory"], update=row["update"], regimen=row["regimen"], npz_sha256=h, segundos=round(time.perf_counter() - t0, 1))
        filas.append(R); print(f"{row['trajectory']} u{row['update']} {row['regimen']}: rho_borde={R['rho_borde']:.5g} G0_cond={R['G0_cond']:.3g} K0={R['K0']:.3g}", flush=True)
    campos = ["trajectory", "update", "regimen", "rho_borde", "rho_quad_err", "rho_gl_rel_dif_orden", "rho_gl_rel_dif_dir", "rho_mediana", "rho_max",
              "theta_min", "s99", "dominantes", "pesos_dominantes", "dominantes_en_hull", "G0_eig_min", "G0_eig_max", "G0_cond", "sqrtdetG0", "K0",
              "f_sha", "hull_vertices", "hull_edge_min", "hull_edge_max", "hull_angle_min", "M_eig_min", "M_eig_max", "M_cond", "npz_sha256", "segundos"]
    with open(out / "diagnostico.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos, extrasaction="ignore"); w.writeheader(); w.writerows(filas)
    (out / "diagnostico.json").write_text(json.dumps(dict(script_sha256=sha(Path(__file__)), geometry_sha256=GEOM_SHA, estados=filas), indent=2))


if __name__ == "__main__":
    main()
