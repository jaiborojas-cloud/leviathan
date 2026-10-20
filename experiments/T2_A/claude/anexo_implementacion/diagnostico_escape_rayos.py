"""diagnostico_escape_rayos.py - DIAGNOSTICO SEPARADO, SOLO LECTURA. No clasifica, no asigna Y, no toca checkpoints ni presupuestos.

Pregunta: en los casos pausados (split8_j5/j7/j8) los rayos de la aplicacion exponencial se van a infinito en la carta (|p| -> infinito, |v| -> infinito)
a distancia intrinseca finita (frontera de la familia softmax). Este script mide, para el mismo estado regenerado de update 25:
  (1) el radio t* de escape (extrapolado) y CUALES rayos escapan (indices/angulos, ancho del sector);
  (2) el area geodesica A(t) del disco de radio t (anillos de rayos + cuadratura area7 de geometry.py) en los instantes en que el maximo
      |p| cruza umbrales, para ver si A(t) llega a 0.02 (area nominal) antes del escape. El area NO se reduce para rescatar el caso.
Integra con float64 (geometry.Geometry.jet, DOP853 rtol 2e-10, atol 2e-12), los mismos rayos y angulos que Geometry.rays/MPFR (nt=2048 por
defecto), y se detiene cuando max|p| supera --pstop, dt < --dtmin, t >= --radius o se agotan --max-steps. Es un diagnostico de la ecuacion
del rayo: cerca de la singularidad float64 pierde significado en las ultimas decimas de paso; por eso se compara contra el CSV de MPFR si
existe (--mpfr-csv) y las tablas de area se calculan solo hasta --pstop.

Ejecucion (PowerShell, minutos):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "D:\\RIPG_DATA\\T2_A\\expediente\\anexo_implementacion\\diagnostico_escape_rayos.py" --case split8_j7_true
"""
import os
for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_k] = "1"
import argparse, csv, hashlib, json, sys, time
from pathlib import Path
import numpy as np
from scipy.integrate import DOP853, OdeSolution

ap = argparse.ArgumentParser()
ap.add_argument("--sources", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto\sources")
ap.add_argument("--states", default=r"D:\RIPG_DATA\T2_A\expediente\estados_u25")
ap.add_argument("--outdir", default=r"D:\RIPG_DATA\T2_A\expediente\diagnostico_escape")
ap.add_argument("--mpfr-csv", default=None, help="CSV de medicion_mpfr_caso.py para comparar (opcional; por defecto diagnostico_mpfr/mpfr_<caso>.csv si existe)")
ap.add_argument("--case", required=True)
ap.add_argument("--nt", type=int, default=2048)
ap.add_argument("--radius", type=float, default=0.09)
ap.add_argument("--pstop", type=float, default=60.0, help="se detiene cuando max|p| supera este valor")
ap.add_argument("--dtmin", type=float, default=1e-9)
ap.add_argument("--max-steps", type=int, default=20000)
ap.add_argument("--nr", type=int, default=96, help="anillos radiales para el area")
a = ap.parse_args()
GEOM_SHA = "b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sha(Path(a.sources) / "geometry.py") != GEOM_SHA:
    sys.exit("ABORTA: geometry.py no coincide con b4d1e0e4...")
state = Path(a.states) / f"state_025_regen_{a.case}.npz"
want = [r["sha256"] for r in csv.DictReader(open(Path(a.states) / "regeneracion_u25.csv", encoding="utf-8")) if r["trajectory"] == a.case][0]
if sha(state) != want:
    sys.exit("ABORTA: el estado no coincide con regeneracion_u25.csv")
sys.path.insert(0, a.sources)
import geometry as G

OUT = Path(a.outdir); OUT.mkdir(parents=True, exist_ok=True)
lines = []
def say(*p):
    s = " ".join(str(x) for x in p); print(s, flush=True); lines.append(s)

with np.load(state) as z:
    M, f = z["M"], z["f"]
g = G.Geometry(M, f); nt = a.nt
g0 = g.jet(np.zeros((1, 2)))[0][0]
th = np.arange(nt) * 2 * np.pi / nt
v0 = np.linalg.solve(np.linalg.cholesky(g0).T, np.array([np.cos(th), np.sin(th)])).T
def rhs(t, y):
    p, v = y.reshape(2, nt, 2)
    gam = g.jet(p)[4]
    return np.concatenate([v, -np.einsum('bkij,bi,bj->bk', gam, v, v)]).ravel()
y0 = np.concatenate([np.zeros_like(v0), v0]).ravel()
solver = DOP853(rhs, 0.0, y0, a.radius, rtol=2e-10, atol=2e-12)
ts, interps, hist = [0.0], [], []
thr = [2.0, 5.0, 10.0, 20.0, 40.0, a.pstop]; crossed = {}
T0 = time.perf_counter(); why = "RADIO_ALCANZADO"
while solver.status == "running" and len(interps) < a.max_steps:
    t_prev = float(solver.t)
    msg = solver.step()
    if solver.status == "failed":
        why = f"INTEGRADOR_FALLO: {msg}"; break
    interps.append(solver.dense_output()); ts.append(float(solver.t))
    P = solver.y.reshape(2, nt, 2)
    np_ = np.linalg.norm(P[0], axis=1); nv = np.linalg.norm(P[1], axis=1)
    hist.append((len(interps), float(solver.t), float(solver.t) - t_prev, float(np_.max()), float(nv.max()), int(np_.argmax())))
    for q in thr:
        if q not in crossed and np_.max() >= q:
            crossed[q] = len(interps)
    if np_.max() >= a.pstop:
        why = "PSTOP"; break
    if hist[-1][2] < a.dtmin:
        why = "DTMIN"; break
if solver.status == "finished":
    why = "RADIO_ALCANZADO"
n_steps = len(interps); sol = OdeSolution(ts, interps) if interps else None
say(f"caso {a.case}  nt={nt}  paro: {why}  pasos={n_steps}  t_final={ts[-1]!r}  tiempo={time.perf_counter() - T0:.1f}s")
P = solver.y.reshape(2, nt, 2); pn = np.linalg.norm(P[0], axis=1); vn = np.linalg.norm(P[1], axis=1)

# (1) escape: extrapolacion del radio t* con polo simple |v| ~ C/(t*-t) en los ultimos pasos
tail = hist[-12:]
# estimacion limpia: 1/|v| lineal en t  =>  t* = t - (1/|v|)/(d(1/|v|)/dt)
tstar = []
for (n1, t1, dt1, p1, v1, i1), (n2, t2, dt2, p2, v2, i2) in zip(tail[:-1], tail[1:]):
    s = (1 / v2 - 1 / v1) / (t2 - t1) if t2 > t1 else 0
    if s < 0:
        tstar.append(t2 - (1 / v2) / s)
tstar = np.array(tstar)
say(f"t* extrapolado (polo simple, ultimos pasos): mediana {np.median(tstar) if len(tstar) else float('nan')!r}  rango [{tstar.min() if len(tstar) else float('nan')!r}, {tstar.max() if len(tstar) else float('nan')!r}]  (solo orientativo)")
top = np.argsort(-pn)[:12]
say("rayos con mayor |p| al final: indice (angulo rad, |p|):", ", ".join(f"{i} ({th[i]:.4f}, {pn[i]:.1f})" for i in top))
for q in (3.0, 10.0, 30.0):
    idx = np.where(pn > q)[0]
    if len(idx):
        say(f"rayos con |p|>{q:g}: {len(idx)} de {nt}; indices {idx.min()}..{idx.max()}  (contiguos: {bool(np.all(np.diff(idx) == 1))})")
    else:
        say(f"rayos con |p|>{q:g}: 0 de {nt}")
say("max|p| de los rayos fuera del grupo principal (mediana |p| de todos): ", float(np.median(pn)))

# (2) area geodesica del disco de radio t en los instantes de cruce de umbrales
def area_disk(t, nt_sub=1, nr=a.nr):
    rr = np.linspace(0.0, t, nr + 1)
    pts = np.stack([sol(r)[: 2 * nt].reshape(nt, 2) for r in rr[1:]])
    rings = np.concatenate([np.zeros((1, nt, 2)), pts])[:, ::nt_sub]
    return G.area7(g, G.triangles(rings))
rows = []
if sol is not None:
    say("\n  umbral|p|    paso        t          A(t) nt   A(t) nt/2   A(t) nr/2")
    for q in thr:
        if q in crossed:
            k = crossed[q]; t = ts[k]
            A1 = area_disk(t); A2 = area_disk(t, 2); A3 = area_disk(t, 1, a.nr // 2)
            rows.append(dict(umbral=q, paso=k, t=t, A=A1, A_nt_medio=A2, A_nr_medio=A3))
            say(f"  {q:7.1f} {k:8d} {t:.10f}  {A1:.8f}  {A2:.8f}  {A3:.8f}")
    # radio en que A = 0.02 (si se alcanza antes del escape)
    tt = np.linspace(ts[1], ts[-1], 400)
    AA = np.array([area_disk(t, 4, 32) for t in tt])
    hit = np.where(AA >= 0.02)[0]
    say(f"\nA(t) con rejilla gruesa (nt/4, nr=32): maximo {AA.max():.6f} en t={tt[AA.argmax()]:.8f}; "
        + (f"alcanza 0.02 en t~{tt[hit[0]]:.8f}" if len(hit) else "NO alcanza 0.02 antes del paro"))
say("\nNota: no es una clasificacion; el estado de la visita sigue siendo PAUSED_PENDING_REVIEW.")

# comparacion con MPFR
mcsv = Path(a.mpfr_csv) if a.mpfr_csv else Path(a.states).parent / "diagnostico_mpfr" / f"mpfr_{a.case}.csv"
if mcsv.exists():
    mr = list(csv.DictReader(open(mcsv, encoding="utf-8")))
    say(f"\ncomparacion con MPFR ({mcsv.name}, {len(mr)} pasos): t en que max|p| cruza cada umbral")
    for q in thr:
        tm = next((float(r["t"]) for r in mr if float(r["max_p"]) >= q), None)
        tf = ts[crossed[q]] if q in crossed else None
        say(f"  |p|>={q:5.1f}  MPFR t={tm!r}  float64 t={tf!r}" + (f"  diff={tf - tm:.3e}" if tm and tf else ""))
with open(OUT / f"escape_{a.case}.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["step", "t", "dt", "max_p", "max_v", "argmax_p_index"]); w.writerows(hist)
(OUT / f"escape_{a.case}.log").write_text("\n".join(lines), encoding="utf-8")
