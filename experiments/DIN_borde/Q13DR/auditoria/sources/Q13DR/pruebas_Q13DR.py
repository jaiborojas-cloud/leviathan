"""pruebas_Q13DR.py - regresiones de analisis_Q13DR.py antes de congelar. Fixture: cohorte G3 s=0.8 (C2/fixtures/G3_trajectories.csv)
copiada en 6 niveles SINTETICOS (c250 y X manipulados). NO es dato confirmatorio. Semillas fijas. Uso: python3 -I pruebas_Q13DR.py --out <dir>"""
import argparse, copy, csv, hashlib, json, math, subprocess, sys
from pathlib import Path
import numpy as np
H = Path(__file__).resolve().parent; sys.path.insert(0, str(H)); import analisis_Q13DR as R
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
FIX = H.parent / "C2" / "fixtures" / "G3_trajectories.csv"
CAMPOS = ["trajectory", "nivel", "split", "k", "X10", "R250", "c250", "q250", "rho_caras_10", "rho_caras_250", "rho_vert_10", "rho_vert_250", "acc_panel250", "acc_train250", "error"]
C = [0.86, 0.70, 0.61, 0.54, 0.42, 0.36]


def base(tiles=1):
    out = []
    for t in range(tiles):
        for r in csv.DictReader(open(FIX)):
            if abs(float(r["s"]) - 0.8) > 1e-9: continue
            q = {c: r.get(c, "") for c in CAMPOS}; q.update(split=str(int(r["split"]) + 100 * t), k=r["k"], acc_panel250="0.93", acc_train250="1.0",
                                                         error="" if r["pair_valid"] == "True" else "invalido"); out.append(q)
    return out


def nivel(filas, l, c=None, w=1.0, sem=0, **mod):
    """w: peso de X real; (1-w) de ruido con la misma DE intra-split aprox. w=0 -> X sin senal."""
    g = np.random.default_rng(sem); out = []
    xs = np.array([float(r["X10"]) for r in filas if not r["error"]]); sd = xs.std()
    for r in filas:
        q = dict(r); q.update(trajectory=f"q13dr_L{l}_s{int(r['split']):04d}_k{r['k']}", nivel=str(l), c250=repr(C[l] if c is None else c))
        if w < 1 and not r["error"]: q["X10"] = repr(w * float(r["X10"]) + math.sqrt(max(1 - w * w, 0)) * sd * float(g.standard_normal()))
        q.update(mod); out.append(q)
    return out


def cohorte(filas, ws=(1, 1, 1, 1, 1, 1), cs=None, sem=500, mods=None):
    out = []
    for l in range(6):
        out += nivel(filas, l, None if cs is None else cs[l], ws[l], sem + l, **((mods or {}).get(l, {})))
    return out


def cli(out, nombre, filas, n, plan_mod=None, res_mod=None):
    d = out / nombre; d.mkdir(parents=True, exist_ok=True); t = d / "tabla.csv"
    with open(t, "w", newline="") as f: w = csv.DictWriter(f, fieldnames=CAMPOS, extrasaction="ignore"); w.writeheader(); w.writerows(filas)
    plan = dict(n_splits=n, niveles=[dict(nivel=l, eps=e) for l, e in enumerate([0, .002, .005, .01, .02, .05])], ids_sha256=hashlib.sha256("\n".join(R.universo(n)).encode()).hexdigest())
    plan.update(plan_mod or {}); (d / "plan.json").write_text(json.dumps(plan))
    rs = dict(tabla_sha256=sha(t), plan_sha256=sha(d / "plan.json")); rs.update(res_mod or {}); (d / "res.json").write_text(json.dumps(rs))
    p = subprocess.run([sys.executable, "-I", str(H / "analisis_Q13DR.py"), "--tabla", str(t), "--tabla-sha", sha(t), "--plan", str(d / "plan.json"), "--plan-sha", sha(d / "plan.json"),
                        "--resumen", str(d / "res.json"), "--out", str(d)], capture_output=True, text=True)
    if p.returncode != 0: return dict(veredicto="ABORTA" if "ABORTA" in p.stdout + p.stderr else f"CRASH {p.returncode}", detalle=(p.stderr or p.stdout)[-300:])
    return resumen(json.loads((d / "RESULTADO_Q13DR.json").read_text()))


def resumen(r): return dict(veredicto=r["veredicto"], extremo=r.get("extremo"), motivos=r["motivos_inconclusive"], bootstrap=r.get("bootstrap"),
                            D={k: v["D"] for k, v in r.get("primaria", {}).items()})


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    res = {}; fallos = []
    def esperar(n, o, e, ext=None):
        ok = o["veredicto"] == e and (ext is None or o.get("extremo") == ext); res[n] = dict(o, esperado=e, esperado_extremo=ext, ok=ok)
        if not ok: fallos.append(n)
        print(("OK   " if ok else "FALLA"), n, o["veredicto"], o.get("extremo"), "(esperado", e, ext, ")", {k: round(v, 4) for k, v in o.get("D", {}).items()},
              (o.get("bootstrap") or {}).get("IC95_beta"), flush=True)
    def nuc(n, filas, NN, e, ext=None): esperar("nucleo:" + n, resumen(R.analizar(filas, NN, True, "", B=499, NB=300, B2=99, BQ=99)), e, ext)
    # reglas puras
    for ic, e in [([0.001, 0.1], "MODULA"), ([-0.01, 0.015], "NO_MODULA"), ([-0.03, 0.01], "NO_CONCLUYENTE"), ([-0.01, 0.03], "NO_CONCLUYENTE"), ([0.0, 0.02], "NO_MODULA")]:
        o = R.clasificar_beta(ic); res.setdefault("reglas_beta", []).append(dict(ic=ic, o=o, e=e))
        if o != e: fallos.append(f"beta{ic}")
    for p5, ic, e in [(True, [0.001, 0.02], "PERSISTE"), (False, [-0.004, 0.005], "DESAPARECE"), (False, [-0.004, 0.009], "INDETERMINADO"), (True, [-0.001, 0.004], "PERSISTE")]:
        o = R.clasificar_extremo(p5, ic); res.setdefault("reglas_extremo", []).append(dict(p5=p5, ic=ic, o=o, e=e))
        if o != e: fallos.append(f"extremo{p5}{ic}")
    print("reglas puras:", "OK" if not [f for f in fallos if f.startswith(("beta", "extremo"))] else "FALLA", flush=True)
    b1 = base(); b8 = base(8)
    # logica
    nuc("niveles_iguales_N100", cohorte(b1), 100, "NO_MODULA", "PERSISTE")
    nuc("N800_modula_y_desaparece", cohorte(b8, ws=(1, .8, .6, .4, .2, 0)), 800, "MODULA", "DESAPARECE")
    nuc("N800_modula_y_persiste", cohorte(b8, ws=(1, .9, .8, .7, .6, .5)), 800, "MODULA", "PERSISTE")
    nuc("N100_ruido_independiente_sin_precision", cohorte(b1, ws=(1, .9, .9, .9, .9, .9)), 100, "NO_CONCLUYENTE")
    nuc("c_no_monotona", cohorte(b1, cs=[.86, .70, .72, .54, .42, .36]), 100, "INCONCLUSIVE_MANIPULACION")
    nuc("rango_menor_030", cohorte(b1, cs=[.86, .82, .78, .74, .70, .60]), 100, "INCONCLUSIVE_MANIPULACION")
    nuc("L0_sin_colapso", cohorte(b1, cs=[.79, .70, .61, .54, .42, .36]), 100, "INCONCLUSIVE_MANIPULACION")
    nuc("L2_pierde_acc", cohorte(b1, mods={2: dict(acc_panel250="0.85")}), 100, "INCONCLUSIVE_MANIPULACION")
    nuc("L5_pierde_acc_permitido", cohorte(b1, mods={5: dict(acc_panel250="0.89")}), 100, "NO_MODULA", "PERSISTE")
    nuc("L0_sin_senal", cohorte(b1, ws=(0, 1, 1, 1, 1, 1)), 100, "INCONCLUSIVE_SIN_SENAL_CONTROL")
    # validacion por CLI (B y NB completos en el caso base)
    full = cohorte(b1); g = np.random.default_rng(281301)
    esperar("cli:completa", cli(out, "completa", full, 100), "NO_MODULA", "PERSISTE")
    l3 = [i for i, r in enumerate(full) if r["nivel"] == "3" and not r["error"]]; ya = sum(1 for r in full if r["nivel"] == "3" and r["error"]); sel = g.permutation(l3)
    e25 = copy.deepcopy(full); [e25[i].update(error="x") for i in sel[:25 - ya]]; esperar("cli:L3_25_faltantes_limite", cli(out, "e25", e25, 100), "NO_MODULA", "PERSISTE")
    e26 = copy.deepcopy(full); [e26[i].update(error="x") for i in sel[:26 - ya]]; esperar("cli:L3_26_faltantes", cli(out, "e26", e26, 100), "INCONCLUSIVE")
    esperar("cli:duplicados", cli(out, "dup", full + full[:2], 100), "ABORTA")
    esperar("cli:id_ajeno", cli(out, "ajeno", full + [dict(full[0], trajectory="q13dr_L6_s0000_k0")], 100), "ABORTA")
    esperar("cli:niveles_mal_plan", cli(out, "nplan", full, 100, plan_mod=dict(niveles=[dict(nivel=0, eps=0)])), "ABORTA")
    esperar("cli:plan_otros_ids", cli(out, "plan", full, 100, plan_mod=dict(ids_sha256="0" * 64)), "INCONCLUSIVE")
    esperar("cli:resumen_otra_tabla", cli(out, "resu", full, 100, res_mod=dict(tabla_sha256="0" * 64)), "INCONCLUSIVE")
    xc = copy.deepcopy(full); [r.update(X10="-2") for r in xc if r["nivel"] == "4"]; esperar("cli:L4_X_constante", cli(out, "xc", xc, 100), "INCONCLUSIVE")
    res["fallos"] = fallos; res["analisis_sha256"] = sha(H / "analisis_Q13DR.py"); res["pruebas_sha256"] = sha(Path(__file__)); res["fixture_sha256"] = sha(FIX)
    (out / "pruebas_Q13DR.json").write_text(json.dumps(res, indent=2, ensure_ascii=False)); print("FALLOS:", fallos)


if __name__ == "__main__":
    main()
