"""certificar_t5.py - implementacion de PROTOCOLO_certificacion_T5_v1_CONGELADO.md (SHA-256 3d2e4882...). SOLO LECTURA sobre los estados.

Diagnostico adicional de T5 (anexo E1 v1.1, 2.2/D3). No reclasifica, no asigna Y, no toca carpetas del piloto ni A = 0.02.
Por caso (j5, j7 y el control j8) escribe <out>/<caso>/resultado.json, rayos.csv y log; al final <out>/RESUMEN.json con V1/V2 y
el veredicto por caso (T5_CERTIFICADA / T5_NO_CERTIFICADA + razones). Reanuda: un caso con resultado.json completo no se recalcula.

Uso (PowerShell, equipo del responsable):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "<ruta>\\certificar_t5.py" --out "D:\\RIPG_DATA\\T2_A\\expediente\\certificacion_t5_2026-10-21"
Pruebas (no cuentan, seccion 9 del protocolo): --prueba --estado-prueba <npz> --caso-prueba <nombre> [--t0-forzado r]
"""
import os
for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_k, "1")
import argparse, csv, hashlib, json, math, platform, sys, time, traceback
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np, scipy
from scipy.integrate import DOP853, OdeSolution, solve_ivp
from scipy.optimize import brentq

# ---------------- constantes congeladas (protocolo v1) ----------------
PROTOCOLO_SHA = "3d2e488242a8c8dc81c0967a73887cc40ae8290b4e23f388beabb2daa4dafdbd"
GEOM_SHA = "b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3"
AUDIT_SHA_REF = "d357bfccabba809364b14f29662a0d3a836a411f77294058f538a34888386aaf"   # archivo importado; se registra, no aborta
ESTADOS = {  # ../estados_u25/regeneracion_u25.csv
    "split8_j5_true": ("state_025_regen_split8_j5_true.npz", "845c22519a20be8ceef4e35210157d97bd5bc223fc9f05e1769b91d998aa4776"),
    "split8_j7_true": ("state_025_regen_split8_j7_true.npz", "59990ae56e64499d9bc46bfa056a8c91bcbffd9b188e4fc081933fdb413625c2"),
    "split8_j8_true": ("state_025_regen_split8_j8_true.npz", "f70d88b3c300286e31b8ca55860cc99f7d2a38c9e5f0c21242d566703928132b"),
}
CASOS_DECISION, CONTROL = ("split8_j5_true", "split8_j7_true"), "split8_j8_true"
A_MEDIDA_J8 = (0.0861038161, 0.02393521)       # ../diagnostico_escape/salida_float64_split8_j8_true.txt (V2)
NT, RTOL, ATOL, T_BOUND = 2048, 2e-10, 2e-12, 0.09
P_T0, P_T1, P_FACE = 10.0, 40.0, 150.0          # 4.1 (t0), V1/4.4 (t1, arranque de la carta de cara), 4.3 (cambio a carta de cara)
P_MP_LO, P_MP_HI = 8.0, 12.0                    # solapamiento float64/mpmath
NS, NS2 = 513, 1025
F_K, F_T, F_DISC, U_MAX = 4.0, 10.0, 10.0, 0.0195
V3_TOL, DISC_TOL, C3_MIN, KCONV_TOL, OVL_K_TOL, C2_TOL, C5_TOL = 1e-5, 1e-5, 1.0, 1e-3, 1e-6, 1e-12, 1e-6
MP_DPS_K, MP_DPS_BETA = 50, 100
VARIANTES_AREA = [(65, NT), (33, NT // 2), (129, NT)]
MAX_PASOS, MAX_REINICIOS = 5000, 5000      # tope operacional de memoria (~0.5 MB por paso con 2048 rayos); los casos reales usan 110-220 pasos

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def clean(x):
    if isinstance(x, dict):
        return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, np.ndarray)):
        return [clean(v) for v in x]
    if isinstance(x, (float, np.floating)):
        return float(x) if np.isfinite(x) else (None if np.isnan(x) else ("inf" if x > 0 else "-inf"))
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


# ---------------- curvatura en mpmath (carta P, mismas formulas que geometry.jet/eval) ----------------
_MPG = {}


def _mp_init(M, f):
    import mpmath as mp
    mp.mp.dps = MP_DPS_K
    _MPG["mp"] = mp
    _MPG["M"] = [[mp.mpf(x) for x in row] for row in M]
    _MPG["f"] = [[mp.mpf(x) for x in row] for row in f]


def _k_mp(P):
    mp, M, f = _MPG["mp"], _MPG["M"], _MPG["f"]
    n = len(f); p0, p1 = mp.mpf(P[0]), mp.mpf(P[1])
    s = [f[k][0] * p0 + f[k][1] * p1 for k in range(n)]; smax = max(s)
    e = [mp.exp(x - smax) for x in s]; Z = mp.fsum(e); a = [x / Z for x in e]
    m = [mp.fsum(a[k] * f[k][i] for k in range(n)) for i in range(2)]
    d = [[f[k][i] - m[i] for i in range(2)] for k in range(n)]
    cov = [[mp.fsum(a[k] * d[k][i] * d[k][j] for k in range(n)) for j in range(2)] for i in range(2)]
    J = [[a[k] * d[k][i] for i in range(2)] for k in range(n)]
    H = [[[a[k] * (d[k][i] * d[k][j] - cov[i][j]) for j in range(2)] for i in range(2)] for k in range(n)]
    MJ = [[mp.fsum(M[r][k] * J[k][i] for k in range(n)) for i in range(2)] for r in range(n)]
    g = [[mp.fsum(J[r][i] * MJ[r][j] for r in range(n)) for j in range(2)] for i in range(2)]
    det = g[0][0] * g[1][1] - g[0][1] * g[1][0]
    gi = [[g[1][1] / det, -g[0][1] / det], [-g[1][0] / det, g[0][0] / det]]
    cross = [[[mp.fsum(MJ[r][i] * H[r][j][k] for r in range(n)) for k in range(2)] for j in range(2)] for i in range(2)]
    gam = [[[gi[i][0] * cross[0][j][k] + gi[i][1] * cross[1][j][k] for k in range(2)] for j in range(2)] for i in range(2)]
    nH = [[[H[r][j][k] - (J[r][0] * gam[0][j][k] + J[r][1] * gam[1][j][k]) for k in range(2)] for j in range(2)] for r in range(n)]
    n11 = [nH[r][0][0] for r in range(n)]; n22 = [nH[r][1][1] for r in range(n)]; n12 = [nH[r][0][1] for r in range(n)]
    Mn22 = [mp.fsum(M[r][k] * n22[k] for k in range(n)) for r in range(n)]
    Mn12 = [mp.fsum(M[r][k] * n12[k] for k in range(n)) for r in range(n)]
    K = (mp.fsum(n11[r] * Mn22[r] for r in range(n)) - mp.fsum(n12[r] * Mn12[r] for r in range(n))) / det
    return float(K)


def _k_mp_lote(Ps):
    return [_k_mp(P) for P in Ps]


# ---------------- carta de cara (como FRONTERA_CONFIRMACION, generalizada a la cara (i, j | k)) ----------------
class Cara:
    def __init__(self, M, f, P):
        import mpmath as mp
        w = np.exp(P @ f.T - (P @ f.T).max()); w /= w.sum()
        o = np.argsort(-w); self.j, self.i, self.k = int(o[0]), int(o[1]), int(o[2])
        mp.mp.dps = MP_DPS_BETA
        F = mp.matrix(f.tolist())
        AA = mp.matrix([[F[q, c] - F[self.j, c] for c in range(2)] for q in (self.i, self.k)])
        self.detA = float(mp.det(AA))
        CC = mp.matrix([[F[q, c] - F[self.j, c] for c in range(2)] for q in range(len(f))]) * AA ** -1
        C = np.array(CC.tolist(), dtype=float); C[self.i] = [1, 0]; C[self.j] = [0, 0]; C[self.k] = [0, 1]
        self.A = np.array(AA.tolist(), dtype=float); self.C = C; self.M = M; self.n = len(f)
        self.otros = [q for q in range(self.n) if q not in (self.i, self.j, self.k)]
        self.beta_min = float(min(C[self.otros, 1])) if self.otros else float("inf")
        self.c1 = bool(abs(self.detA) > 0 and self.beta_min > 0)

    def coords(self, P, v):
        a, lb = self.A @ P; b = math.exp(lb)
        return float(a), b, np.array([self.A[0] @ v, b * (self.A[1] @ v)])

    def jet(self, a, b):
        assert b >= 0, b
        n, C = self.n, self.C
        t = np.zeros(n); dt = np.zeros((n, 2)); ht = np.zeros((n, 2, 2))
        t[self.j] = 1.0; t[self.i] = math.exp(a); dt[self.i, 0] = t[self.i]; ht[self.i, 0, 0] = t[self.i]; t[self.k] = b; dt[self.k, 1] = 1.0
        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            for q in self.otros:
                al, be = C[q]; ea = math.exp(al * a)
                b0, b1, b2 = (b ** be, b ** (be - 1), b ** (be - 2)) if b > 0 else ((0.0 if be > 0 else np.inf), (0.0 if be > 1 else (1.0 if be == 1 else np.inf)), (0.0 if be > 2 else (1.0 if be == 2 else np.inf)))
                t[q] = ea * b0; dt[q] = [al * ea * b0, be * ea * b1]
                ht[q] = [[al * al * ea * b0, al * be * ea * b1], [al * be * ea * b1, be * (be - 1) * ea * b2]]
        S = t.sum(); ds = dt.sum(0); hs = ht.sum(0); w = t / S
        J = dt / S - t[:, None] * ds / S ** 2
        H = ht / S - (dt[:, :, None] * ds[None, None, :] + dt[:, None, :] * ds[None, :, None] + t[:, None, None] * hs) / S ** 2 \
            + 2 * t[:, None, None] * ds[None, :, None] * ds[None, None, :] / S ** 3
        G = J.T @ self.M @ J
        return w, J, H, G

    def acc(self, a, b, V):
        w, J, H, G = self.jet(a, b)
        return -np.linalg.solve(G, J.T @ self.M @ np.einsum("nij,i,j->n", H, V, V))

    def K(self, a, b):
        w, J, H, G = self.jet(a, b)
        gam = np.linalg.solve(G, np.einsum("ni,njk->ijk", self.M @ J, H).reshape(2, 4)).reshape(2, 2, 2)
        nH = H - np.einsum("ni,ijk->njk", J, gam)
        return float((nH[:, 0, 0] @ self.M @ nH[:, 1, 1] - nH[:, 0, 1] @ self.M @ nH[:, 0, 1]) / np.linalg.det(G))

    def integrar(self, a, r, b, V, factor=1.0):
        """b como variable independiente desde b hasta 0+ (solo b >= 0). y = (a, r, da/dr, db/dr)."""
        if not V[1] < 0:
            return None, "db/dr >= 0 en el arranque: no se puede parametrizar por b"
        def rhs(bb, y):
            aa = self.acc(y[0], bb, y[2:]); return [y[2] / y[3], 1 / y[3], aa[0] / y[3], aa[1] / y[3]]
        sol = solve_ivp(rhs, (b, 0.0), [a, r, V[0], V[1]], method="DOP853", rtol=RTOL * factor, atol=ATOL * factor, dense_output=True)
        return (sol if sol.success else None), (None if sol.success else sol.message)

    def limite(self, sol):
        import mpmath as mp
        ae, re, vae, vbe = sol.y[:, -1]
        w, J, H, G = self.jet(ae, 0.0); Vb = np.array([vae, vbe]); sp2 = float(Vb @ G @ Vb)
        ev = np.linalg.eigvalsh(G)
        mp.mp.dps = MP_DPS_K   # G en b=0 solo con i, j, k (los demas son 0 por beta>0)
        ea = mp.exp(mp.mpf(ae)); S = 1 + ea
        tt = {self.j: (mp.mpf(1), [0, 0]), self.i: (ea, [ea, 0]), self.k: (mp.mpf(0), [0, 1])}
        Jm = mp.matrix(self.n, 2)
        dS = [ea, mp.mpf(1)]
        for q, (tq, dq) in tt.items():
            for c in range(2):
                Jm[q, c] = mp.mpf(dq[c]) / S - tq * dS[c] / S ** 2
        Mm = mp.matrix(self.M.tolist()); Gm = Jm.T * Mm * Jm
        evm = sorted(float(x) for x in mp.eig(Gm)[0])
        return dict(T_star=float(re), a=float(ae), db_dr=float(vbe), da_dr=float(vae), speed=math.sqrt(sp2) if sp2 > 0 else float("nan"),
                    G_eig=ev.tolist(), G_eig_mp=evm, G_eig_dif=float(abs(ev[0] - evm[0])), w_i=float(w[self.i]), w_j=float(w[self.j]),
                    w_fuera_cara=float(w[self.otros].sum() + w[self.k]), nfev=int(sol.nfev))


# ---------------- integracion de rayos en la carta P ----------------
def v_inicial(g, n, phase=0.0):
    g0 = g.jet(np.zeros((1, 2)))[0][0]; th = np.arange(n) * 2 * np.pi / n + phase
    return th, np.linalg.solve(np.linalg.cholesky(g0).T, np.array([np.cos(th), np.sin(th)])).T


def rhs_rayos(g, n):
    def rhs(t, y):
        p, v = y.reshape(2, n, 2); gam = g.jet(p)[4]
        return np.concatenate([v, -np.einsum("bkij,bi,bj->bk", gam, v, v)]).ravel()
    return rhs


def maxp(y, n):
    p = np.linalg.norm(y.reshape(2, n, 2)[0], axis=1); return p


class Segmento:
    def __init__(self, ts, interps, idx):
        self.t0, self.t1, self.idx = ts[0], ts[-1], np.asarray(idx); self.sol = OdeSolution(ts, interps)
        self.col = {int(r): c for c, r in enumerate(self.idx)}

    def pos(self, r, ray):
        n = len(self.idx); return self.sol(r).reshape(2, n, 2)[0, self.col[ray]]

    def estado(self, r, ray):
        n = len(self.idx); y = self.sol(r).reshape(2, n, 2); return y[0, self.col[ray]], y[1, self.col[ray]]


def integrar_haz(g, y0, idx, t_start, t_bound, parar, log, etiqueta):
    """DOP853 paso a paso; parar(ts, ys) -> True detiene tras el paso aceptado. Devuelve ts, ys, interps, status."""
    n = len(idx)
    s = DOP853(rhs_rayos(g, n), t_start, y0, t_bound, rtol=RTOL, atol=ATOL)
    ts, ys, its = [t_start], [np.asarray(y0).copy()], []
    while s.status == "running":
        msg = s.step()
        if s.status == "failed":
            log(f"{etiqueta}: DOP853 fallo: {msg}"); return ts, ys, its, "failed"
        its.append(s.dense_output()); ts.append(s.t); ys.append(s.y.copy())
        if len(its) > MAX_PASOS:
            return ts, ys, its, "max_pasos"
        if parar(ts, ys):
            return ts, ys, its, "parado"
    return ts, ys, its, "finished"


def area_en(g, triangles, area7, seg, r, nr, rays):
    n = len(seg.idx); y = seg.sol(np.linspace(0, r, nr)).T.reshape(nr, 2, n, 2)[:, 0]
    return float(area7(g, triangles(y[:, [seg.col[q] for q in rays]])))


# ---------------- un caso ----------------
def un_caso(caso, g, triangles, area7, jacsolve, M, f, out, args, log):
    t_ini = time.perf_counter(); R = dict(caso=caso)
    th, v0 = v_inicial(g, NT); y0 = np.concatenate([np.zeros_like(v0), v0]).ravel(); todos = np.arange(NT)
    # --- 4.1 haz completo hasta el primer paso con max|p| >= 150 (o t_bound) ---
    marca = {}
    def parar(ts, ys):
        mp_ = maxp(ys[-1], NT); m = float(mp_.max())
        if "t0" not in marca and (m >= P_T0 or (args.t0_forzado and ts[-1] >= args.t0_forzado)):
            marca["t0"] = len(ts) - 1
        if "t1" not in marca and m >= P_T1:
            marca["t1"] = len(ts) - 1
        return m >= P_FACE
    ts, ys, its, st = integrar_haz(g, y0, todos, 0.0, T_BOUND, parar, log, "haz")
    seg0 = Segmento(ts, its, todos); R["haz"] = dict(status=st, pasos=len(its), t_final=ts[-1], max_p_final=float(maxp(ys[-1], NT).max()))
    log(f"haz: {st}, {len(its)} pasos, t={ts[-1]!r}, max|p|={R['haz']['max_p_final']:.2f}")
    traza = [(k, ts[k], float(maxp(ys[k], NT).max()), int(maxp(ys[k], NT).argmax())) for k in range(len(ts))]
    with open(out / "traza_haz.csv", "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh); wr.writerow(["paso", "t", "max_p", "argmax"]); wr.writerows(traza)
    if st in ("failed", "max_pasos") and R["haz"]["max_p_final"] < P_FACE:
        R["veredicto"] = dict(estado="T5_NO_CERTIFICADA", razones=[f"el haz termina con '{st}' antes de max|p| = 150"]); return R
    if "t0" not in marca:
        R["veredicto"] = dict(estado="T5_NO_CERTIFICADA", razones=["no se alcanza max|p| >= 10 antes de t_bound: sin escape en la carta P"])
        return R
    k0 = marca["t0"]; t0 = ts[k0]; p_t0 = maxp(ys[k0], NT); d = int(p_t0.argmax())
    R["t0"] = dict(paso=k0, t=t0, max_p=float(p_t0.max()), rayo_designado=d, angulo=float(th[d]))
    k1 = marca.get("t1"); R["t1"] = dict(paso=k1, t=(ts[k1] if k1 is not None else None))
    R["sensibilidad_t0"] = {str(u): next(((k, ts[k]) for k, tt, m, a in traza if m >= u), None) for u in (5.0, 20.0)}
    log(f"t0 = {t0!r} (paso {k0}), rayo designado {d}; t1 = {R['t1']['t']}")

    # --- 4.2 area en t0 (ii) ---
    A0 = area_en(g, triangles, area7, seg0, t0, 33, todos)
    variantes = {f"{nr}x{nn}": area_en(g, triangles, area7, seg0, t0, nr, todos[:: NT // nn]) for nr, nn in VARIANTES_AREA}
    delta_disc = max(abs(x - A0) for x in variantes.values())
    R["area_t0"] = dict(A0=A0, variantes=variantes, delta_disc=delta_disc)
    log(f"A0 = {A0:.10f}, delta_disc = {delta_disc:.3e}")

    # --- 4.3 Jacobi en t0 ---
    sj = jacsolve(g, th, t0)
    z0 = sj.sol(t0).reshape(6, NT); j0, jp0 = z0[4].copy(), z0[5].copy()
    rr = np.linspace(0, t0, NS); jj = sj.sol(rr).reshape(6, NT, NS)[4]
    simpson = np.ones(NS); simpson[1:-1:2] = 4; simpson[2:-1:2] = 2; simpson *= (rr[1] - rr[0]) / 3
    A_J = float((2 * np.pi / NT) * np.sum(np.abs(jj) @ simpson))
    cambios = int(np.sum(np.any(jj[:, 1:] <= 0, axis=1)))
    R["jacobi_t0"] = dict(A_J=A_J, V3_rel=abs(A_J - A0) / A0, rayos_con_j_no_positivo=cambios, j_min=float(j0.min()), j_max=float(j0.max()),
                          jp_min=float(jp0.min()), jp_max=float(jp0.max()))
    log(f"A_J = {A_J:.10f}, V3 rel = {R['jacobi_t0']['V3_rel']:.2e}, rayos con j<=0 en (0,t0]: {cambios}")

    # --- 4.4 escape del rayo designado y T+ (i) ---
    kd = next((k for k in range(len(ts)) if np.linalg.norm(ys[k].reshape(2, NT, 2)[0, d]) >= P_T1), None)
    esc = dict(paso_arranque=kd)
    T_plus = None
    solo = None
    if kd is None:   # el haz se detuvo (otro rayo llego a |p| = 150) antes de que el designado llegue a 40: se sigue solo ese rayo
        y1 = ys[-1].reshape(2, NT, 2)[:, d].ravel()
        t1s, y1s, _, st1 = integrar_haz(g, y1, np.array([d]), ts[-1], T_BOUND, lambda tt, yy: float(np.linalg.norm(yy[-1][:2])) >= P_FACE, log, "designado")
        k1s = next((k for k in range(len(t1s)) if np.linalg.norm(y1s[k][:2]) >= P_T1), None)
        esc["seguimiento_individual"] = dict(status=st1, pasos=len(t1s) - 1, t_final=t1s[-1], paso_arranque=k1s)
        if k1s is not None:
            solo = (t1s[k1s], y1s[k1s][:2], y1s[k1s][2:], y1s[-1][:2])
    else:
        solo = (ts[kd], *ys[kd].reshape(2, NT, 2)[:, d], ys[-1].reshape(2, NT, 2)[0, d])
    if solo is None:
        esc["error"] = "el rayo designado no llega a |p| >= 40"
    else:
        # cara = la arista HACIA LA QUE SE DIRIGE el rayo (4.4.1): se identifica con su ultimo estado disponible, no en |p| = 40
        r_d, P_d, v_d, P_dest = solo; cara = Cara(M, f, P_dest)
        a, b, V = cara.coords(P_d, v_d)
        w, Jf, H, G = cara.jet(a, b); Tm = np.vstack([cara.A[0], b * cara.A[1]])
        c2 = float(np.linalg.norm(Jf @ Tm - g.jac(P_d[None])[0]) / np.linalg.norm(g.jac(P_d[None])[0]))
        esc.update(cara=dict(j=cara.j, i=cara.i, k=cara.k, detA=cara.detA, beta_min=cara.beta_min), C1=cara.c1, C2_rel=c2, r_arranque=r_d, b_arranque=b)
        lims = {}
        for fac in (1.0, 0.01):
            sol, err = cara.integrar(a, r_d, b, V, fac)
            lims[str(fac)] = cara.limite(sol) if sol is not None else dict(error=err)
            if fac == 1.0 and sol is not None and kd is not None:   # solapamiento extra: r de la carta de cara frente al haz cuando el rayo llega a |p| = 150
                kk = next((k for k in range(kd, len(ts)) if np.linalg.norm(ys[k].reshape(2, NT, 2)[0, d]) >= P_FACE), None)
                if kk is not None:
                    _, bb, _ = cara.coords(*ys[kk].reshape(2, NT, 2)[:, d])
                    esc["solape_r_en_150"] = float(sol.sol(bb)[1] - ts[kk])
        esc["limite"] = lims
        if all("T_star" in v for v in lims.values()):
            Ts, Ts2 = lims["1.0"]["T_star"], lims["0.01"]["T_star"]; dT = abs(Ts - Ts2); T_plus = Ts + F_T * dT
            L = lims["1.0"]
            esc.update(T_star=Ts, delta_T=dT, T_plus=T_plus,
                       C3=abs(L["db_dr"]) >= C3_MIN, C4=L["G_eig"][0] > 0 and L["G_eig"][0] > 1e3 * L["G_eig_dif"],
                       C5=bool(np.isfinite(Ts) and abs(L["speed"] - 1) <= C5_TOL), C6=bool(cara.c1 and L["w_fuera_cara"] == 0.0))
            esc["C2"] = c2 <= C2_TOL
    if T_plus is None and args.prueba and args.T_plus_forzado:   # SOLO pruebas sin escape (j6): ejercita muestreo de K y cota
        T_plus = args.T_plus_forzado; esc["T_plus_forzado_prueba"] = T_plus
    R["escape"] = esc
    log(f"escape: {json.dumps(clean({k: esc.get(k) for k in ('T_star', 'delta_T', 'T_plus', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6')}))}")
    if T_plus is None:
        R["veredicto"] = dict(estado="T5_NO_CERTIFICADA", razones=["(i) no se pudo obtener T* del rayo designado"]); return R

    # --- continuacion para muestrear K hasta T+: carta P mientras |p| < 150, luego carta de cara ---
    segs = [seg0]; cara_rayo = {}; problemas = []
    activos = todos.copy(); y_cur = ys[-1]; t_cur = ts[-1]; reinicios = 0
    def entregar(rays, ycur, tcur, act):
        n = len(act); pv = ycur.reshape(2, n, 2)
        for q in rays:
            c = act.tolist().index(q); P, v = pv[0, c], pv[1, c]; cara = Cara(M, f, P); a, b, V = cara.coords(P, v)
            sol, err = cara.integrar(a, tcur, b, V)
            if sol is None:
                problemas.append(f"rayo {q}: {err}"); cara_rayo[int(q)] = dict(r_entrega=tcur, error=err); continue
            cara_rayo[int(q)] = dict(r_entrega=tcur, cara=(cara.j, cara.i, cara.k), C1=cara.c1, beta_min=cara.beta_min, r_salida=float(sol.y[1, -1]), obj=cara, sol=sol)
            if not cara.c1:
                problemas.append(f"rayo {q}: C1 falla en su cara")
    if t_cur < T_plus:
        fuera = [int(q) for q, pp in zip(activos, maxp(y_cur, NT)) if pp >= P_FACE]
        entregar(fuera, y_cur, t_cur, activos)
        keep = np.array([q not in fuera for q in activos]); n = len(activos)
        y_cur = y_cur.reshape(2, n, 2)[:, keep].ravel(); activos = activos[keep]
        while len(activos) and t_cur < T_plus:
            n = len(activos)
            stop_now = lambda tts, yys: bool((maxp(yys[-1], n) >= P_FACE).any())
            tts, yys, iits, st2 = integrar_haz(g, y_cur, activos, t_cur, T_plus, stop_now, log, "continuacion")
            if iits:
                segs.append(Segmento(tts, iits, activos))
            if st2 in ("failed", "max_pasos"):
                problemas.append(f"continuacion: {st2} en t={tts[-1]}"); break
            t_cur, y_cur = tts[-1], yys[-1]
            fuera = [int(q) for q, pp in zip(activos, maxp(y_cur, n)) if pp >= P_FACE]
            if fuera:
                entregar(fuera, y_cur, t_cur, activos)
                keep = np.array([q not in fuera for q in activos])
                y_cur = y_cur.reshape(2, n, 2)[:, keep].ravel(); activos = activos[keep]
            reinicios += 1
            if reinicios > MAX_REINICIOS:
                problemas.append("demasiados reinicios"); break
    else:   # el haz ya paso T+ antes de llegar a |p| = 150 (no deberia ocurrir con escape antes de T+)
        pass
    R["continuacion"] = dict(segmentos=len(segs), reinicios=reinicios, entregados_a_cara=len(cara_rayo), problemas=problemas[:50])
    log(f"continuacion: {len(segs)} segmentos, {len(cara_rayo)} rayos a carta de cara, problemas: {len(problemas)}")

    # --- muestreo de K (4.3) ---
    def fin_rayo(q):
        cr = cara_rayo.get(int(q)); return min(T_plus, cr["r_salida"]) if cr and "r_salida" in cr else T_plus
    def posicion(q, r):
        cr = cara_rayo.get(int(q))
        if cr and "sol" in cr and r > cr["r_entrega"]:
            sol = cr["sol"]; bs = sol.t
            rv = sol.sol(bs)[1]   # r(b), creciente al bajar b
            if r >= rv[-1]:
                return ("cara", cr["obj"], sol.y[0, -1], 0.0)
            bb = brentq(lambda x: sol.sol(x)[1] - r, 0.0, bs[0], xtol=1e-300, rtol=4 * np.finfo(float).eps, maxiter=500)
            return ("cara", cr["obj"], float(sol.sol(bb)[0]), max(bb, 0.0))
        for sg in reversed(segs):
            if int(q) in sg.col and sg.t0 <= r <= sg.t1 + 1e-15:
                return ("P", sg.pos(min(r, sg.t1), int(q)))
        raise RuntimeError(f"sin posicion para rayo {q} en r={r}")

    def muestrear(rays, ra, rb_fun, ns, pool):
        """devuelve max|K| por rayo y conteos por evaluador. Los rayos sin carta de cara comparten la rejilla linspace(ra, rb, ns):
        sus posiciones se evaluan por segmento en lote (mismo resultado que rayo a rayo, mucho mas rapido)."""
        kmax = np.zeros(NT); cnt = dict(float64=0, mpmath=0, cara=0)
        buf = dict(Pf=[], idx_f=[], Pm=[], idx_m=[])
        def vaciar(forzar=False):
            if buf["Pf"] and (forzar or len(buf["Pf"]) >= 20000):
                kf = np.abs(g.eval(np.array(buf["Pf"]))[1]); np.maximum.at(kmax, np.array(buf["idx_f"]), kf)
                cnt["float64"] += len(kf); buf["Pf"].clear(); buf["idx_f"].clear()
            if buf["Pm"] and (forzar or len(buf["Pm"]) >= 64 * 4 * args.procesos):
                lotes = [buf["Pm"][i:i + 64] for i in range(0, len(buf["Pm"]), 64)]
                km = np.abs(np.concatenate([np.array(x) for x in pool.map(_k_mp_lote, lotes)])); np.maximum.at(kmax, np.array(buf["idx_m"]), km)
                cnt["mpmath"] += len(km); buf["Pm"].clear(); buf["idx_m"].clear()
        def clasificar(q, ps):
            if ps[0] == "cara":
                kmax[q] = max(kmax[q], abs(ps[1].K(ps[2], ps[3]))); cnt["cara"] += 1
            elif np.linalg.norm(ps[1]) <= P_T0:
                buf["Pf"].append(np.array(ps[1])); buf["idx_f"].append(q)
            else:
                buf["Pm"].append(np.array(ps[1])); buf["idx_m"].append(q)
            vaciar()
        comunes = [int(q) for q in rays if not (cara_rayo.get(int(q), {}).get("sol") is not None and rb_fun(q) > cara_rayo[int(q)]["r_entrega"])]
        cset = set(comunes)
        if comunes:
            rbs = {rb_fun(q) for q in comunes}
            assert len(rbs) == 1, "rejilla comun con extremos distintos"
            grid = np.linspace(ra, rbs.pop(), ns); hecho = np.zeros((NT, ns), bool)
            for sg in reversed(segs):
                cols = [q for q in comunes if q in sg.col]
                if not cols:
                    continue
                sel = np.where((grid >= sg.t0) & (grid <= sg.t1 + 1e-15))[0]
                for c0 in range(0, len(sel), 64):
                    ss = sel[c0:c0 + 64]
                    Y = sg.sol(np.minimum(grid[ss], sg.t1)).reshape(2, len(sg.idx), 2, len(ss))[0]
                    for q in cols:
                        for m, s_ in enumerate(ss):
                            if not hecho[q, s_]:
                                hecho[q, s_] = True; clasificar(q, ("P", Y[sg.col[q], :, m]))
            falta = int((~hecho[comunes]).sum())
            if falta:
                raise RuntimeError(f"{falta} muestras sin segmento")
        for q in rays:
            if int(q) in cset:
                continue
            for r in np.linspace(ra, rb_fun(q), ns):
                clasificar(int(q), posicion(q, r))
        vaciar(True)
        return kmax, cnt

    with ProcessPoolExecutor(max_workers=args.procesos, initializer=_mp_init, initargs=(M.tolist(), f.tolist())) as pool:
        # solapamiento float64/mpmath en |p| en [8, 12] (sobre el haz en [t0, t_final del haz])
        Pov = []
        for k in range(k0, len(ts)):
            pp = ys[k].reshape(2, NT, 2)[0]; nn = np.linalg.norm(pp, axis=1)
            sel = np.where((nn >= P_MP_LO) & (nn <= P_MP_HI))[0]
            Pov.extend(pp[sel[:: max(1, len(sel) // 8)]])
        Pov = Pov[:400]
        ovl = None
        if Pov:
            k64 = g.eval(np.array(Pov))[1]; kmp = np.array(sum(pool.map(_k_mp_lote, [Pov[i:i + 64] for i in range(0, len(Pov), 64)]), []))
            # "10^-6 relativo" se mide frente a max(|K|, 1): una curvatura de orden 1 es despreciable frente al kappa admisible (~10^5)
            err = np.abs(k64 - kmp) / np.maximum(np.abs(kmp), 1.0)
            ovl = dict(puntos=len(Pov), max_rel=float(err.max()), max_abs=float(np.abs(k64 - kmp).max()), ok=bool(err.max() <= OVL_K_TOL))
        log(f"solape float64/mpmath: {ovl}")
        km513, cnt513 = muestrear(todos, t0, fin_rayo, NS, pool)
        log(f"K 513: max {km513.max():.6e} ({cnt513})")
        km1025, cnt1025 = muestrear(todos, t0, fin_rayo, NS2, pool)
        log(f"K 1025: max {km1025.max():.6e}")
        kv1 = None
        if k1 is not None:
            kv1, _ = muestrear(todos, t0, lambda q: ts[k1], NS, pool)
    kh, kh2 = float(km513.max()), float(km1025.max())
    R["curvatura"] = dict(kappa_hat=kh, kappa_hat_1025=kh2, conv_rel=abs(kh2 - kh) / max(kh, 1.0), conv_ok=bool(abs(kh2 - kh) / max(kh, 1.0) <= KCONV_TOL),   # relativo frente a max(kappa_hat, 1), como el solape
                          rayo_kmax=int(km513.argmax()), conteos_513=cnt513, conteos_1025=cnt1025, solape=ovl)

    # --- 4.5 cota ---
    def Lplus(kap, D, rays):
        sk = math.sqrt(kap); x = sk * D
        C = math.cosh(x) if x < 700 else float("inf"); S = (math.sinh(x) / sk if sk > 0 else D) if x < 700 else float("inf")
        return float((2 * np.pi / len(rays)) * np.sum(np.abs(j0[rays]) * C + np.abs(jp0[rays]) * S)), C, S
    kap = F_K * kh; D = T_plus - t0
    L2048, C, S = Lplus(kap, D, todos); L1024, _, _ = Lplus(kap, D, todos[::2])
    eps = abs(L2048 - L1024) / L2048 if np.isfinite(L2048) and L2048 > 0 else float("inf")
    U = A0 + F_DISC * delta_disc + D * L2048 * (1 + 10 * eps)
    R["cota"] = dict(kappa=kap, Delta=D, cosh=C, sinh_sobre_raiz=S, L_plus=L2048, L_plus_1024=L1024, eps_theta=eps, U=U, U_sobre_002=U / 0.02, U_max=U_MAX)
    log(f"U = {U:.8f} (U/0.02 = {U / 0.02:.4f}); kappa = {kap:.4e}, Delta = {D:.6e}, L+ = {L2048:.6f}")
    # V1: la cota de t0 a t1 debe quedar por encima del area medida en t1
    if k1 is not None and kv1 is not None:
        A1 = area_en(g, triangles, area7, seg0, ts[k1], 33, todos); kap1 = F_K * float(kv1.max()); D1 = ts[k1] - t0
        L1, _, _ = Lplus(kap1, D1, todos); L1b, _, _ = Lplus(kap1, D1, todos[::2]); e1 = abs(L1 - L1b) / L1 if L1 > 0 else 0.0
        U1 = A0 + F_DISC * delta_disc + D1 * L1 * (1 + 10 * e1)
        R["V1"] = dict(t1=ts[k1], A_medida_t1=A1, U_t1=U1, kappa_hat_t0_t1=float(kv1.max()), ok=bool(U1 >= A1))
    else:
        R["V1"] = dict(ok=False, error="sin t1 (|p| >= 40) en el haz")
    log(f"V1: {R['V1']}")

    # --- veredicto del caso (V1/V2 globales en el resumen) ---
    raz = []
    e = R["escape"]
    for c in ("C1", "C2", "C3", "C4", "C5", "C6"):
        if not e.get(c):
            raz.append(f"(i) {c} falla")
    if problemas:
        raz.append(f"continuacion con {len(problemas)} problemas (rayos sin carta valida)")
    if not delta_disc <= DISC_TOL:
        raz.append(f"(ii) delta_disc {delta_disc:.2e} > {DISC_TOL}")
    if not R["jacobi_t0"]["V3_rel"] <= V3_TOL:
        raz.append(f"V3 falla ({R['jacobi_t0']['V3_rel']:.2e})")
    if not (ovl and ovl["ok"]):
        raz.append("V4 solape float64/mpmath falla o sin puntos")
    if not R["curvatura"]["conv_ok"]:
        raz.append("muestreo de K no convergido (513 vs 1025)")
    if not U <= U_MAX:
        raz.append(f"(iii) U = {U:.6f} > {U_MAX}")
    R["veredicto"] = dict(estado="T5_NO_CERTIFICADA" if raz else "T5_CERTIFICADA_PENDIENTE_V1_V2", razones=raz)
    R["segundos"] = time.perf_counter() - t_ini
    # tabla por rayo
    with open(out / "rayos.csv", "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh); wr.writerow(["rayo", "theta", "j_t0", "jp_t0", "kmax_513", "kmax_1025", "r_entrega_cara", "cara_j_i_k", "beta_min", "r_salida"])
        for q in range(NT):
            cr = cara_rayo.get(q, {})
            wr.writerow([q, th[q], j0[q], jp0[q], km513[q], km1025[q], cr.get("r_entrega", ""), cr.get("cara", ""), cr.get("beta_min", ""), cr.get("r_salida", "")])
    return R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--estados", default=r"D:\RIPG_DATA\T2_A\expediente\estados_u25")
    ap.add_argument("--sources", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto\sources")
    ap.add_argument("--casos", nargs="+", default=list(CASOS_DECISION) + [CONTROL])
    ap.add_argument("--procesos", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--prueba", action="store_true", help="SOLO pruebas (no cuentan): sin verificacion de hashes de estado")
    ap.add_argument("--estado-prueba", default=None); ap.add_argument("--caso-prueba", default="prueba")
    ap.add_argument("--t0-forzado", type=float, default=None, help="SOLO pruebas sin escape (j6)")
    ap.add_argument("--T-plus-forzado", type=float, default=None, help="SOLO pruebas sin escape (j6)")
    args = ap.parse_args()
    if not args.prueba and (args.t0_forzado or args.T_plus_forzado):
        sys.exit("--t0-forzado solo existe con --prueba")
    src = Path(args.sources)
    for p in (str(src / "instrument"), str(src)):
        sys.path.insert(0, p)
    gpath = next((p for p in (src / "geometry.py", src / "instrument" / "geometry.py") if p.exists()), None)
    if gpath is None or sha(gpath) != GEOM_SHA:
        sys.exit(f"ABORTA: geometry.py no coincide con {GEOM_SHA[:8]}...")
    import geometry, audit
    from geometry import Geometry, area7, triangles
    audit_sha = sha(audit.__file__)
    out_root = Path(args.out); out_root.mkdir(parents=True, exist_ok=True)
    yo = Path(__file__).resolve()
    meta = dict(script=str(yo), script_sha256=sha(yo), protocolo_sha256=PROTOCOLO_SHA, geometry_sha256=GEOM_SHA, audit_sha256=audit_sha,
                audit_coincide_con_importado=audit_sha == AUDIT_SHA_REF, prueba=args.prueba,
                environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__, platform=platform.platform(), cpus=os.cpu_count()))
    casos = [args.caso_prueba] if args.prueba and args.estado_prueba else args.casos
    resultados = {}
    for caso in casos:
        out = out_root / caso; out.mkdir(exist_ok=True); fres = out / "resultado.json"
        if fres.exists() and json.loads(fres.read_text()).get("completo"):
            resultados[caso] = json.loads(fres.read_text()); print(f"{caso}: ya completo, se reutiliza", flush=True); continue
        logf = open(out / "log.txt", "a", encoding="utf-8")
        def log(m, _f=logf):
            line = f"{time.strftime('%H:%M:%S')} {caso}: {m}"; print(line, flush=True); _f.write(line + "\n"); _f.flush()
        try:
            if args.prueba and args.estado_prueba:
                spath = Path(args.estado_prueba); s_sha = sha(spath)
            else:
                fn, esperado = ESTADOS[caso]; spath = Path(args.estados) / fn; s_sha = sha(spath)
                if s_sha != esperado:
                    sys.exit(f"ABORTA: {fn} no coincide ({s_sha[:12]} vs {esperado[:12]})")
            with np.load(spath) as z:
                M, f = np.array(z["M"], dtype=float), np.array(z["f"], dtype=float)
            g = Geometry(M, f)
            R = un_caso(caso, g, triangles, area7, audit.jacsolve, M, f, out, args, log)
            R.update(meta=meta, estado_archivo=str(spath), estado_sha256=s_sha, completo=True)
        except SystemExit:
            raise
        except Exception:
            R = dict(caso=caso, completo=False, error=traceback.format_exc()[-3000:], meta=meta,
                     veredicto=dict(estado="ERROR_DE_EJECUCION", razones=["ver error"]))
            log(R["error"])
        fres.write_text(json.dumps(clean(R), indent=2)); resultados[caso] = json.loads(fres.read_text()); logf.close()

    # --- resumen con validaciones globales V1/V2 (5) ---
    if not args.prueba:
        v1 = {c: bool(resultados.get(c, {}).get("V1", {}).get("ok")) for c in list(CASOS_DECISION) + [CONTROL]}
        r8 = resultados.get(CONTROL, {})
        v2 = bool(r8.get("completo") and r8.get("cota", {}).get("U") is not None and
                  (r8["cota"]["U"] == "inf" or float(r8["cota"]["U"]) >= A_MEDIDA_J8[1]) and
                  not str(r8.get("veredicto", {}).get("estado", "")).startswith("T5_CERTIFICADA"))
        valido = all(v1.values()) and v2
        fin = {}
        for c in CASOS_DECISION:
            v = resultados.get(c, {}).get("veredicto", {})
            est = v.get("estado")
            if est == "T5_CERTIFICADA_PENDIENTE_V1_V2":
                est = "T5_CERTIFICADA" if valido else "T5_NO_CERTIFICADA"
            fin[c] = dict(estado=est, razones=v.get("razones", []) + ([] if valido or est == "T5_CERTIFICADA" else ["V1/V2 invalidan el procedimiento"]),
                          U=resultados.get(c, {}).get("cota", {}).get("U"))
        RES = dict(meta=meta, V1=v1, V2=v2, procedimiento_valido=valido, casos=fin,
                   nota="Diagnostico de T5. No reclasifica: j5 y j7 siguen PAUSED_PENDING_REVIEW hasta E2. No asigna Y.")
        (out_root / "RESUMEN.json").write_text(json.dumps(clean(RES), indent=2))
        print(json.dumps(clean(RES), indent=2))


if __name__ == "__main__":
    main()
