"""pruebas_Q13.py - regresiones de analisis_Q13.py antes de congelar. Fixture: cohorte G3 s=0.8 (C2/fixtures/G3_trajectories.csv)
re-etiquetada como brazo A0; los brazos reducidos son copias manipuladas SINTETICAMENTE. NO es dato confirmatorio. Semillas fijas.
Uso: python3 -I pruebas_Q13.py --out <dir>"""
import argparse, copy, csv, hashlib, json, math, subprocess, sys
from pathlib import Path
import numpy as np
H = Path(__file__).resolve().parent; sys.path.insert(0, str(H)); import analisis_Q13 as Q
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
FIX = H.parent / "C2" / "fixtures" / "G3_trajectories.csv"
CAMPOS = ["trajectory", "brazo", "split", "k", "X10", "R250", "c250", "q250", "rho_caras_10", "rho_caras_250", "rho_vert_10", "rho_vert_250", "acc_panel250", "acc_train250", "error"]
N = 100


def brazo(b, s=0.8, tiles=1, **mod):
    """tiles > 1: copia los 100 splits como splits nuevos (s + 100 t); solo para tener N grande en pruebas de logica."""
    out = []
    for t in range(tiles):
        for r in csv.DictReader(open(FIX)):
            if abs(float(r["s"]) - s) > 1e-9: continue
            q = {c: r.get(c, "") for c in CAMPOS}; sp = int(r["split"]) + 100 * t
            q.update(trajectory=f"q13_{b}_s{sp:04d}_k{r['k']}", brazo=b, split=str(sp), acc_panel250="0.93", acc_train250="1.0", error="" if r["pair_valid"] == "True" else "invalido")
            q.update(mod); out.append(q)
    return out


def x_es_L(filas): [r.update(X10=repr(math.log(float(r["rho_caras_10"])))) for r in filas if r["rho_caras_10"] not in ("", None) and float(r["rho_caras_10"]) > 0]; return filas
def x_ruido(filas, sem): g = np.random.default_rng(sem); [r.update(X10=repr(float(g.standard_normal()))) for r in filas]; return filas


def cli(out, nombre, filas, brazos=Q.BRAZOS, plan_mod=None, res_mod=None):
    d = out / nombre; d.mkdir(parents=True, exist_ok=True); t = d / "tabla.csv"
    with open(t, "w", newline="") as f: w = csv.DictWriter(f, fieldnames=CAMPOS, extrasaction="ignore"); w.writeheader(); w.writerows(filas)
    plan = dict(n_splits=N, brazos=list(brazos), dosis=dict(LS=0.0, WD=0.0), ids_sha256=hashlib.sha256("\n".join(Q.universo(N, brazos)).encode()).hexdigest()); plan.update(plan_mod or {})
    (d / "plan.json").write_text(json.dumps(plan)); rs = dict(tabla_sha256=sha(t), plan_sha256=sha(d / "plan.json")); rs.update(res_mod or {}); (d / "res.json").write_text(json.dumps(rs))
    p = subprocess.run([sys.executable, "-I", str(H / "analisis_Q13.py"), "--tabla", str(t), "--tabla-sha", sha(t), "--plan", str(d / "plan.json"), "--plan-sha", sha(d / "plan.json"),
                        "--resumen", str(d / "res.json"), "--out", str(d)], capture_output=True, text=True)
    if p.returncode != 0: return dict(veredicto="ABORTA" if "ABORTA" in p.stdout + p.stderr else f"CRASH {p.returncode}", detalle=(p.stderr or p.stdout)[-300:])
    r = json.loads((d / "RESULTADO_Q13.json").read_text()); return resumen(r)


def resumen(r): return dict(veredicto=r["veredicto"], motivos=r["motivos_inconclusive"], clasificacion=r.get("clasificacion"), bootstrap=r.get("bootstrap"),
                            D={b: v["D"] for b, v in r.get("primaria", {}).items()}, manipulacion=r.get("manipulacion"))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    res = {}; fallos = []
    def esperar(n, o, e):
        ok = o["veredicto"] == e; res[n] = dict(o, esperado=e, ok=ok)
        if not ok: fallos.append(n)
        print(("OK   " if ok else "FALLA"), n, o["veredicto"], "(esperado", e + ")", o.get("clasificacion"), o.get("D"), flush=True)
    def nucleo(n, filas, e, brazos=Q.BRAZOS, NN=N): esperar("nucleo:" + n, resumen(Q.analizar(filas, NN, brazos, True, "", B=999, NB=500, B2=199)), e)
    # 0b) reglas puras
    tabla = [((0.0, False, [-0.003, 0.004], [0.002, 0.03]), "CAE"), ((0.0, False, [-0.003, 0.0061], [0.002, 0.03]), "INTERMEDIO"),
             ((0.0, False, [-0.003, 0.004], [0.0, 0.03]), "INTERMEDIO"), ((0.02, True, [0.01, 0.03], [-0.01, 0.01]), "SE_MANTIENE"),
             ((0.02, True, [0.01, 0.03], [0.001, 0.01]), "INTERMEDIO"), ((0.02, False, [0.0, 0.03], [-0.01, 0.01]), "INTERMEDIO")]
    for args, e in tabla:
        o = Q.clasificar(*args); okk = o == e; res.setdefault("reglas_clasificar", []).append(dict(args=args, obtenido=o, esperado=e, ok=okk))
        if not okk: fallos.append(f"clasificar{args}")
    for cl, e in [(["CAE", "CAE"], "NECESARIO_APOYADO"), (["SE_MANTIENE"] * 2, "NO_NECESARIO"), (["CAE", "SE_MANTIENE"], "DEPENDE_DEL_MANIPULADOR"),
                  (["SE_MANTIENE", "CAE"], "DEPENDE_DEL_MANIPULADOR"), (["CAE", "INTERMEDIO"], "NO_CONCLUYENTE"), (["CAE"], "NECESARIO_APOYADO_UN_MANIPULADOR"),
                  (["SE_MANTIENE"], "NO_NECESARIO_UN_MANIPULADOR"), (["INTERMEDIO"], "NO_CONCLUYENTE")]:
        o = Q.veredicto(cl); okk = o == e; res.setdefault("reglas_veredicto", []).append(dict(cl=cl, obtenido=o, esperado=e, ok=okk))
        if not okk: fallos.append(f"veredicto{cl}")
    print("reglas puras:", "OK" if not [f for f in fallos if f.startswith(("clasificar", "veredicto"))] else "FALLA", flush=True)
    A0 = brazo("A0")
    # 0) D_punto == D de primaria
    a = [r for r in A0 if not r["error"]]; sp = np.array([int(r["split"]) for r in a]); X = np.array([float(r["X10"]) for r in a])
    L = np.log([float(r["rho_caras_10"]) for r in a]); Y = np.log([float(r["rho_caras_250"]) for r in a])
    d1 = Q.D_punto(sp, X, L, Y); d2 = Q.A.primaria(sp, X, L, Y, 3, 260001, 9)["D"]; ok = abs(d1 - d2) < 1e-14
    res["D_punto_igual_primaria"] = dict(D_punto=d1, D_primaria=d2, ok=ok); print("OK  " if ok else "FALLA", "D_punto", d1, d2)
    if not ok: fallos.append("D_punto")
    # 1) logica de veredictos (nucleo)
    nucleo("brazos_iguales", A0 + brazo("LS", c250="0.6") + brazo("WD", c250="0.6"), "NO_NECESARIO")
    # con N=100 la regla NO debe declarar CAE (sin precision suficiente): INTERMEDIO -> NO_CONCLUYENTE
    nucleo("N100_senal_cae_sin_precision", A0 + x_es_L(brazo("LS", c250="0.6")) + x_es_L(brazo("WD", c250="0.6")), "NO_CONCLUYENTE")
    nucleo("N100_ruido_sin_precision", A0 + x_ruido(brazo("LS", c250="0.6"), 300101) + x_ruido(brazo("WD", c250="0.6"), 300102), "NO_CONCLUYENTE")
    # con N=800 (splits copiados; solo logica)
    T = 8; A0T = brazo("A0", tiles=T)
    nucleo("N800_senal_cae_en_ambos", A0T + x_es_L(brazo("LS", tiles=T, c250="0.6")) + x_es_L(brazo("WD", tiles=T, c250="0.6")), "NECESARIO_APOYADO", NN=100 * T)
    nucleo("N800_cae_solo_LS", A0T + x_es_L(brazo("LS", tiles=T, c250="0.6")) + brazo("WD", tiles=T, c250="0.6"), "DEPENDE_DEL_MANIPULADOR", NN=100 * T)
    nucleo("N800_ruido_en_ambos", A0T + x_ruido(brazo("LS", tiles=T, c250="0.6"), 300101) + x_ruido(brazo("WD", tiles=T, c250="0.6"), 300102), "NECESARIO_APOYADO", NN=100 * T)
    nucleo("A0_sin_colapso", brazo("A0", c250="0.6") + brazo("LS", c250="0.6") + brazo("WD", c250="0.6"), "INCONCLUSIVE_MANIPULACION")
    nucleo("LS_no_baja_c", A0 + brazo("LS", c250="0.75") + brazo("WD", c250="0.6"), "INCONCLUSIVE_MANIPULACION")
    nucleo("WD_rompe_acc", A0 + brazo("LS", c250="0.6") + brazo("WD", c250="0.6", acc_panel250="0.85"), "INCONCLUSIVE_MANIPULACION")
    nucleo("A0_sin_senal", x_ruido(brazo("A0"), 300103) + brazo("LS", c250="0.6") + brazo("WD", c250="0.6"), "INCONCLUSIVE_SIN_SENAL_CONTROL")
    nucleo("N800_un_brazo_cae", A0T + x_es_L(brazo("LS", tiles=T, c250="0.6")), "NECESARIO_APOYADO_UN_MANIPULADOR", brazos=("A0", "LS"), NN=100 * T)
    nucleo("un_brazo_mantiene", A0 + brazo("LS", c250="0.6"), "NO_NECESARIO_UN_MANIPULADOR", brazos=("A0", "LS"))
    # 2) validacion por CLI (B y NB completos en el caso base)
    base = A0 + brazo("LS", c250="0.6") + brazo("WD", c250="0.6"); g = np.random.default_rng(280201)
    esperar("cli:completa", cli(out, "completa", base), "NO_NECESARIO")
    wd = [i for i, r in enumerate(base) if r["brazo"] == "WD" and not r["error"]]; sel = g.permutation(wd)
    e25 = copy.deepcopy(base); [e25[i].update(error="x") for i in sel[:25 - sum(1 for r in base if r["brazo"] == "WD" and r["error"])]]
    esperar("cli:WD_25_faltantes_limite", cli(out, "e25", e25), "NO_NECESARIO")
    e26 = copy.deepcopy(base); [e26[i].update(error="x") for i in sel[:26 - sum(1 for r in base if r["brazo"] == "WD" and r["error"])]]
    esperar("cli:WD_26_faltantes", cli(out, "e26", e26), "INCONCLUSIVE")
    sp21 = set(g.permutation(100)[:21].tolist()); esperar("cli:LS_21_splits_omitidos", cli(out, "sp21", [r for r in base if not (r["brazo"] == "LS" and int(r["split"]) in sp21)]), "INCONCLUSIVE")
    esperar("cli:duplicados", cli(out, "dup", base + base[:2]), "ABORTA")
    esperar("cli:id_ajeno", cli(out, "ajeno", base + [dict(base[0], trajectory="q13_ZZ_s0000_k0")]), "ABORTA")
    esperar("cli:brazos_mal_plan", cli(out, "bplan", base, brazos=("LS", "A0", "WD")), "ABORTA")
    dm = copy.deepcopy(base); dm[3]["rho_caras_10"] = "0"; dm[600]["c250"] = "nan"; dm[1200]["acc_panel250"] = ""; esperar("cli:dominio_3", cli(out, "dom", dm), "NO_NECESARIO")
    xc = copy.deepcopy(base); [r.update(X10="-2") for r in xc if r["brazo"] == "LS"]; esperar("cli:LS_X_constante", cli(out, "xc", xc), "INCONCLUSIVE")
    esperar("cli:plan_otros_ids", cli(out, "plan", base, plan_mod=dict(ids_sha256="0" * 64)), "INCONCLUSIVE")
    esperar("cli:resumen_otra_tabla", cli(out, "resu", base, res_mod=dict(tabla_sha256="0" * 64)), "INCONCLUSIVE")
    # 3) descriptivo (sin expectativa): niveles G3 sin colapso como brazos reducidos
    o = resumen(Q.analizar(A0 + [dict(r, trajectory=r["trajectory"].replace("_A0_", "_LS_"), brazo="LS") for r in brazo("A0", 0.5)]
                           + [dict(r, trajectory=r["trajectory"].replace("_A0_", "_WD_"), brazo="WD") for r in brazo("A0", 0.25)], N, Q.BRAZOS, True, "", B=999, NB=500, B2=199))
    res["descriptivo_G3_niveles_como_brazos"] = o; print("descriptivo G3:", o["veredicto"], o["clasificacion"], o["D"], o["bootstrap"])
    res["fallos"] = fallos; res["analisis_sha256"] = sha(H / "analisis_Q13.py"); res["pruebas_sha256"] = sha(Path(__file__)); res["fixture_sha256"] = sha(FIX)
    (out / "pruebas_Q13.json").write_text(json.dumps(res, indent=2, ensure_ascii=False)); print("FALLOS:", fallos)


if __name__ == "__main__":
    main()
