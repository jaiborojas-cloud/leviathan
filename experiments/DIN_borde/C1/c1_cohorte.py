"""c1_cohorte.py (BORRADOR v2, no congelado). v1: compuerta con tolerancia numerica (DIAG_compuerta_2026-10-24.md).
v2 (diseno C1 v2): X desde logits con logsumexp; cota de cuerda en u10; auditoria de precision de rho(10) con 5760 direcciones
y orden 1600 en 40 trayectorias preseleccionadas por semilla 270001.
v3 (auditoria D2c, PR #76): la tabla final conserva TODAS las trayectorias planificadas (las fallidas con su error); cuerda
con caras completas (todos los puntos de cada arista del casco); el resumen publica IDs planificados, auditados y de compuerta. - DIN-C1: entrena la cohorte nueva y mide X, L10, rho(30) y Y. NO analiza.

Modos:
  --compuerta : reproduce desde cero 5 trayectorias antiguas (split12) y exige (a) parametros del update 5 a <= 1e-12 de
                checkpoint_005.pt de T2-A0 y RNG numpy identico, (b) M del update 50 a <= 1e-10 relativo del de la fase 2.
  (normal)    : splits --desde..--hasta (por defecto 168..323), 5 inicializaciones, regla de semillas de T2-A0 extendida.
Por trayectoria: new_session(s, j) -> updates continuos 0->250; estados (M, f) en 5, 10, 30, 250; en 10: p(y) del panel;
rho_borde congelado en 10, 30, 250. Reanudable (PROGRESO_c1.csv); al final tabla c1_cohorte.csv y RESUMEN_c1.json con SHA.
Uso (PowerShell):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I c1_cohorte.py --out "D:\\RIPG_DATA\\DIN_C1\\compuerta" --compuerta
  & ... -I c1_cohorte.py --out "D:\\RIPG_DATA\\DIN_C1\\cohorte" --procesos 12
"""
import os
for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_k] = "1"
import argparse, csv, hashlib, json, math, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import numpy as np

RHO_SHA = "d8ec69f89a75ab947ac05d3764858eb2e8f6dc873b47733645b2e8b5aac0416b"
GEOM_SHA = "b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3"
GUARDAR = (5, 10, 30, 50, 250)
RHO_EN = (10, 30, 250)
TOL_PARAM = 1e-12   # v1: tolerancia numerica (diag_compuerta: entorno distinto al de T2-A0 da <= 2.5e-15)
TOL_M = 1e-10       # v1: diferencia relativa maxima de M(u50) frente a la fase 2 (observado <= 2e-12)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
_W = {}


def _init(root, mocks, rho_dir):
    src = Path(root) / "sources"
    for p in (str(src / "instrument"), mocks, str(src)):
        sys.path.insert(0, p)
    sys.path.append(rho_dir)
    import torch
    torch.set_num_threads(1)
    import core, rho_borde
    from training import new_session, updates
    from geometry import Geometry
    _W.update(torch=torch, core=core, rb=rho_borde, new_session=new_session, updates=updates, Geometry=Geometry, root=Path(root))


def init_index(s, k):
    return 5 + 5 * (s - 8) + k


def caras_expuestas(f, tol=1e-9):
    """Caras expuestas del casco 2D: vertices y, por cada arista, TODOS los indices sobre ella (no solo sus extremos)."""
    from scipy.spatial import ConvexHull
    V = list(ConvexHull(f).vertices); esc = float(np.ptp(f, 0).max()); caras = [[v] for v in V]
    for i in range(len(V)):
        a, b = f[V[i]], f[V[(i + 1) % len(V)]]; d = b - a; L2 = float(d @ d); nrm = np.array([-d[1], d[0]]) / math.sqrt(L2)
        t = (f - a) @ d / L2; S = [j for j in range(len(f)) if abs(float((f[j] - a) @ nrm)) <= tol * esc and -tol <= t[j] <= 1 + tol]
        caras.append(sorted(S))
    return caras


def cuerda(M, f):
    n = len(f); caras = caras_expuestas(f); best = float("inf")
    for S in caras:
        d = -np.ones(n) / n; d[S] += 1 / len(S); best = min(best, math.sqrt(max(float(d @ M @ d), 0.0)))
    return best, max(len(S) for S in caras)


def una(s, k, out, t2a1, compuerta, auditar=False):
    torch, core = _W["torch"], _W["core"]; j = init_index(s, k); tray = f"split{s}_j{j}_true"
    X, y, Xv, yv, m, opt, rng = _W["new_session"](s, j)
    d = Path(out) / "estados" / tray; d.mkdir(parents=True, exist_ok=True); R = dict(trajectory=tray, split=s, init=j, error=""); prev = 0
    for t in GUARDAR:
        _W["updates"](m, opt, rng, X, y, t - prev); prev = t
        if t == 5 and compuerta:
            c = torch.load(_W["root"] / "trajectories" / tray / "checkpoint_005.pt", weights_only=False)
            dmax = max(float((a - c["model"][n]).abs().max()) for n, a in m.state_dict().items())
            R["dif_u5"] = dmax; R["compuerta_u5"] = int(dmax <= TOL_PARAM and c["numpy_rng"] == rng.bit_generator.state)
        if t == 50 and not compuerta:
            continue
        Rb, Ub, f = core.make_geom_state(m, Xv, yv); M = core.subset_M(Rb, Ub, [0, 1, 2]); p = d / f"u{t}.npz"
        np.savez_compressed(p, M=M.detach().numpy(), f=f.detach().numpy()); R[f"sha_u{t}"] = sha(p)
        if t == 50:
            ref = Path(t2a1) / "fase2" / "visitas" / tray / "u50" / "states" / tray / "state.npz"
            Mr = np.load(ref)["M"]; dr = float(np.abs(M.detach().numpy() - Mr).max() / np.abs(Mr).max())
            R["dif_rel_M_u50"] = dr; R["compuerta_u50"] = int(dr <= TOL_M); break
        if t == 10:
            with torch.no_grad():
                z = m(Xv); lse = torch.logsumexp(z, 1); zm = z.clone(); zm[torch.arange(len(yv)), yv] = -float("inf")
                l1mp = (torch.logsumexp(zm, 1) - lse).numpy()          # log(1 - p(y_n)), estable sin saturar
                pv = torch.softmax(z, 1); py = pv[torch.arange(len(yv)), yv].numpy()
            kk = int(np.argmax(l1mp))
            R.update(X=float(l1mp[kk]), k_min_u10=kk, p_min_val_u10=float(py.min()), X_prob=math.log(max(1 - float(py.min()), 1e-300)),
                     val_acc_u10=float((pv.argmax(1) == yv).double().mean()))
        if t in RHO_EN and not compuerta:
            Mn = M.detach().numpy().astype(float); RR = _W["rb"].rho_borde(_W["Geometry"](Mn, f.detach().numpy().astype(float)))
            if t == 10:
                R["cuerda_u10"], R["cara_max_u10"] = cuerda((Mn + Mn.T) / 2, f.detach().numpy().astype(float))
                if auditar:
                    RA = _W["rb"].rho_borde(_W["Geometry"](Mn, f.detach().numpy().astype(float)), ndir=5760, orden=1600); R["rho_u10_alta"] = RA["rho_borde"]
            dg = np.diag(Mn); R.update({f"rho_u{t}": RR["rho_borde"], f"dif_dir_u{t}": RR.get("dif_dir"), f"diag_frac_u{t}": float(dg.max() / np.trace(Mn)), f"k_star_u{t}": int(np.argmax(dg))})
    return R


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--procesos", type=int, default=12)
    ap.add_argument("--desde", type=int, default=168); ap.add_argument("--hasta", type=int, default=323); ap.add_argument("--compuerta", action="store_true")
    ap.add_argument("--root", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
    ap.add_argument("--t2a1", default=r"D:\RIPG_DATA\T2_A1"); ap.add_argument("--mocks", default=r"D:\RIPG_DATA\T2_A\cribado_borde\margen\mocks")
    ap.add_argument("--rho-dir", default=r"D:\RIPG_DATA\T2_A1\codigo\fase0prima")
    a = ap.parse_args(); root = Path(a.root)
    if sha(Path(a.rho_dir) / "rho_borde.py") != RHO_SHA: sys.exit("ABORTA: rho_borde.py no coincide")
    if sha(root / "sources" / "geometry.py") != GEOM_SHA: sys.exit("ABORTA: geometry.py no coincide")
    cola = [(12, k) for k in range(5)] if a.compuerta else [(s, k) for s in range(a.desde, a.hasta + 1) for k in range(5)]
    if not a.compuerta and a.desde < 168: sys.exit("ABORTA: la cohorte confirmatoria empieza en el split 168")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True); prog = out / "PROGRESO_c1.csv"
    campos = ["trajectory", "split", "init", "X", "X_prob", "cuerda_u10", "cara_max_u10", "rho_u10_alta", "auditada", "p_min_val_u10", "k_min_u10", "val_acc_u10", "rho_u10", "rho_u30", "rho_u250", "dif_dir_u10", "dif_dir_u30", "dif_dir_u250",
              "diag_frac_u10", "diag_frac_u30", "diag_frac_u250", "k_star_u10", "k_star_u30", "k_star_u250", "sha_u5", "sha_u10", "sha_u30", "sha_u50", "sha_u250",
              "dif_u5", "dif_rel_M_u50", "compuerta_u5", "compuerta_u50", "error"]
    hechas = set()
    if prog.exists(): hechas = {r["trajectory"] for r in csv.DictReader(open(prog, encoding="utf-8")) if not r["error"]}
    nuevo = not prog.exists(); fh = open(prog, "a", newline="", encoding="utf-8"); w = csv.DictWriter(fh, fieldnames=campos, extrasaction="ignore")
    if nuevo: w.writeheader()
    pend = [(s, k) for s, k in cola if f"split{s}_j{init_index(s, k)}_true" not in hechas]; t0 = time.time()
    aud = set() if a.compuerta else {tuple(x) for x in np.random.default_rng(270001).permutation(np.array(cola))[:40].tolist()}
    print(json.dumps(dict(modo="compuerta" if a.compuerta else "cohorte", trayectorias=len(cola), pendientes=len(pend), script_sha256=sha(Path(__file__)))), flush=True)
    with ProcessPoolExecutor(max_workers=min(a.procesos, max(1, len(pend))), initializer=_init, initargs=(str(root), a.mocks, a.rho_dir)) as pool:
        futs = {pool.submit(una, s, k, str(out), a.t2a1, a.compuerta, (s, k) in aud): (s, k) for s, k in pend}
        for i, fu in enumerate(as_completed(futs), 1):
            try: R = fu.result()
            except Exception as e:
                s, k = futs[fu]; R = dict(trajectory=f"split{s}_j{init_index(s, k)}_true", split=s, init=init_index(s, k), error=repr(e)[:300])
            R["auditada"] = int(futs[fu] in aud); w.writerow(R); fh.flush()
            if i % 25 == 0 or R.get("error") or a.compuerta: print(f"[{i}/{len(pend)}] {R['trajectory']} {'ERROR ' + R['error'] if R.get('error') else 'ok'} ({(time.time() - t0) / 60:.1f} min)", flush=True)
    fh.close()
    ult = {}
    for r in csv.DictReader(open(prog, encoding="utf-8")): ult[r["trajectory"]] = r if (r["trajectory"] not in ult or not r["error"]) else ult[r["trajectory"]]
    planificadas = [f"split{s}_j{init_index(s, k)}_true" for s, k in cola]
    todas = [ult.get(t, dict(trajectory=t, split=int(t.split("_")[0][5:]), init=int(t.split("_")[1][1:]), error="no ejecutada")) for t in planificadas]
    filas = [r for r in todas if not r["error"]]
    res = dict(modo="compuerta" if a.compuerta else "cohorte", trayectorias=len(cola), completas=len(filas), errores=len(todas) - len(filas),
               script_sha256=sha(Path(__file__)), ids_planificados_sha256=hashlib.sha256("\n".join(planificadas).encode()).hexdigest())
    if a.compuerta:
        res.update(compuerta_u5=sum(str(r.get("compuerta_u5")) == "1" for r in filas), compuerta_u50=sum(str(r.get("compuerta_u50")) == "1" for r in filas),
                   PASA=all(str(r.get("compuerta_u5")) == "1" and str(r.get("compuerta_u50")) == "1" for r in filas) and len(filas) == 5,
                   tolerancias=dict(param_u5=TOL_PARAM, M_rel_u50=TOL_M), trayectorias_compuerta=planificadas,
                   detalle=[{k: r.get(k) for k in ("trajectory", "dif_u5", "dif_rel_M_u50", "compuerta_u5", "compuerta_u50")} for r in todas])
    else:
        tabla = out / "c1_cohorte.csv"
        with open(tabla, "w", newline="", encoding="utf-8") as f2:
            w2 = csv.DictWriter(f2, fieldnames=campos, extrasaction="ignore"); w2.writeheader(); w2.writerows(todas)   # orden planificado; incluye fallidas
        res.update(tabla_sha256=sha(tabla), auditadas=sorted(f"split{s}_j{init_index(s, k)}_true" for s, k in aud),
                   nota="Informe operacional: no contiene analisis de X frente a Y. La tabla incluye las trayectorias fallidas con su error.")
    (out / "RESUMEN_c1.json").write_text(json.dumps(res, indent=2)); print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
