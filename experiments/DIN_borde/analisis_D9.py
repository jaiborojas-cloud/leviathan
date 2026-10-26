"""analisis_D9.py - analisis exploratorio de D9 segun PLAN_D9_generalizacion.md (con errata: 11 candidatos, p<0.05/12).
Entradas: d9_tabla.csv (equipo del responsable, sha e67fe37d...), d6/PROGRESO_d6.csv (c=diag_frac, trM), R1/etapa2/r1_etapa2.csv (rho_caras).
Concreciones fijadas aqui ANTES de calcular (el plan no las especificaba):
  - Y primario = test_loss crudo en u250; secundarios: test_acc u250 y brecha = test_loss - train_loss en u250 (descriptivos, B=499).
  - Base barata del momento t: train_loss, val_loss, val_acc, X(t) de d9_tabla, lineales, centradas en el split.
  - Delta c(10->20) usa la base de t=20; Delta c(20->30) la de t=30 (informacion disponible en ese momento).
  - Signo estable: pendiente del candidato en el modelo completo ajustado por separado en splits pares e impares.
  - Control de integridad: train_loss y val_acc de d9 frente a d6 en u10/20/30 (misma trayectoria reentrenada).
Uso: python3 -I analisis_D9.py --tabla <d9_tabla.csv> --out <dir>
"""
import argparse, csv, hashlib, json, math, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
SHA_TABLA = "e67fe37d8688c3681a75748cf2384ac2ed1326445df535c74a775a585ee76043"


def cen(v, sp):
    v = np.asarray(v, float).copy()
    for s in np.unique(sp): v[sp == s] -= v[sp == s].mean()
    return v


def folds(sp):
    us = np.unique(sp); perm = np.random.default_rng(260010).permutation(us); f = {u: i % 10 for i, u in enumerate(perm)}
    return np.array([f[s] for s in sp])


def sse(Yc, M, fo):
    s = 0.0
    for k in range(10):
        tr, te = fo != k, fo == k
        if M is None or M.shape[1] == 0: s += float((Yc[te] ** 2).sum()); continue
        b = np.linalg.lstsq(M[tr], Yc[tr], rcond=None)[0]; s += float(((Yc[te] - M[te] @ b) ** 2).sum())
    return s


def D(Yc, Bm, Xc, fo):
    C = Xc[:, None] if Bm is None else np.column_stack([Bm, Xc])
    return 1 - sse(Yc, C, fo) / sse(Yc, Bm, fo)


def prueba(sp, Y, Bm_raw, X, semilla, B):
    fo = folds(sp); Yc = cen(Y, sp); Bm = None if Bm_raw is None else np.column_stack([cen(c, sp) for c in Bm_raw.T])
    Xc = cen(X, sp); d = D(Yc, Bm, Xc, fo)
    C = Xc[:, None] if Bm is None else np.column_stack([Bm, Xc])
    beta = float(np.linalg.lstsq(C, Yc, rcond=None)[0][-1])
    par = (sp % 2 == 0); sg = [float(np.linalg.lstsq(C[m], Yc[m], rcond=None)[0][-1]) for m in (par, ~par)]
    g = np.random.default_rng(semilla); idx = [np.where(sp == s)[0] for s in np.unique(sp)]; nul = np.empty(B)
    for b in range(B):
        Xp = X.copy()
        for ii in idx: Xp[ii] = X[g.permutation(ii)]
        nul[b] = D(Yc, Bm, cen(Xp, sp), fo)
    return dict(D=d, p=float((1 + np.sum(nul >= d - 1e-15)) / (1 + B)), q95=float(np.quantile(nul, .95)), pendiente=beta,
                pend_pares=sg[0], pend_impares=sg[1], signo_estable=bool(np.sign(sg[0]) == np.sign(sg[1]) == np.sign(beta)), B=B)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tabla", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    h = hashlib.sha256(Path(a.tabla).read_bytes()).hexdigest()
    if h != SHA_TABLA: sys.exit(f"ABORTA: sha de tabla {h} != {SHA_TABLA}")
    t9 = {(r["trajectory"], int(r["update"])): r for r in csv.DictReader(open(a.tabla))}
    d6 = {(r["trajectory"], int(r["update"])): r for r in csv.DictReader(open(HERE / "d6" / "PROGRESO_d6.csv"))}
    r1 = {(r["trajectory"], int(r["update"])): r for r in csv.DictReader(open(HERE / "R1" / "etapa2" / "r1_etapa2.csv"))}
    tr = sorted({k[0] for k in t9}); assert len(tr) == 780
    assert all(not t9[(t, u)]["error"] for t in tr for u in (10, 20, 30, 50, 250))
    assert all(t9[(t, 50)]["compuerta_u50"] == "1" for t in tr)
    sp = np.array([int(t9[(t, 10)]["split"]) for t in tr])
    f = lambda D_, t, u, k: float(D_[(t, u)][k])
    # integridad d9 vs d6
    integ = {}
    for u in (10, 20, 30):
        integ[f"u{u}"] = dict(max_dif_train_loss=max(abs(f(t9, t, u, "train_loss") - f(d6, t, u, "train_loss")) for t in tr),
                              max_dif_val_acc=max(abs(f(t9, t, u, "val_acc") - f(d6, t, u, "val_acc")) for t in tr))
    c = {u: np.array([f(d6, t, u, "diag_frac") for t in tr]) for u in (10, 20, 30)}
    cand = {}
    for u in (10, 20, 30):
        cand[f"c_u{u}"] = (c[u], u)
        cand[f"logtrM_u{u}"] = (np.log([f(d6, t, u, "trM") for t in tr]), u)
        cand[f"logrhocaras_u{u}"] = (np.log([f(r1, t, u, "rho_caras") for t in tr]), u)
    cand["dc_10_20"] = (c[20] - c[10], 20); cand["dc_20_30"] = (c[30] - c[20], 30)
    assert len(cand) == 11 and all(np.all(np.isfinite(v)) for v, _ in cand.values())
    base = {u: np.column_stack([[f(t9, t, u, k) for t in tr] for k in ("train_loss", "val_loss", "val_acc", "X")]) for u in (10, 20, 30)}
    Y = dict(test_loss=np.array([f(t9, t, 250, "test_loss") for t in tr]), test_acc=np.array([f(t9, t, 250, "test_acc") for t in tr]),
             brecha=np.array([f(t9, t, 250, "test_loss") - f(t9, t, 250, "train_loss") for t in tr]))
    res = dict(tabla_sha256=h, script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), integridad_d9_vs_d6=integ,
               umbral=dict(D=0.02, p=0.05 / 12, signo="estable pares/impares"), descriptivos={k: dict(media=float(v.mean()), de=float(v.std())) for k, v in Y.items()})
    # controles: base barata vs nada
    res["control_base_vs_nada"] = {f"u{u}": {k: (lambda fo, Yc, Bm: 1 - sse(Yc, Bm, fo) / sse(Yc, None, fo))(folds(sp), cen(Y[k], sp), np.column_stack([cen(x, sp) for x in base[u].T])) for k in Y} for u in (10, 20, 30)}
    for yk, B in (("test_loss", 2000), ("test_acc", 499), ("brecha", 499)):
        bloque = {}
        for i, (n, (x, u)) in enumerate(cand.items()):
            r = prueba(sp, Y[yk], base[u], x, 320001 + i, B); r["solo"] = prueba(sp, Y[yk], None, x, 330001 + i, 199)["D"]; r["base_t"] = u
            if yk == "test_loss": r["propone"] = bool(r["D"] > 0.02 and r["p"] < 0.05 / 12 and r["signo_estable"])
            bloque[n] = r; print(yk, n, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)
        res[yk] = bloque
    res["candidatos_propuestos"] = [n for n, r in res["test_loss"].items() if r["propone"]]
    res["veredicto"] = "PROPONER_CONFIRMATORIO" if res["candidatos_propuestos"] else "NINGUNO_PASA"
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True); (out / "RESULTADO_D9.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
    print("VEREDICTO", res["veredicto"], res["candidatos_propuestos"]); print("integridad", integ); print("base_vs_nada", res["control_base_vs_nada"])


if __name__ == "__main__":
    main()
