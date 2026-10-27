"""pruebas_Q13DR.py v3 - regresiones de analisis_Q13DR.py antes de congelar. Fixture: cohorte G3 s=0.8 (C2/fixtures/G3_trajectories.csv)
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
        if w < 1 and not r["error"]: q["X10"] = repr(float(w * float(r["X10"]) + math.sqrt(max(1 - w * w, 0)) * sd * float(g.standard_normal())))
        q.update(mod); out.append(q)
    return out


def cohorte(filas, ws=(1, 1, 1, 1, 1, 1), cs=None, sem=500, mods=None):
    out = []
    for l in range(6):
        out += nivel(filas, l, None if cs is None else cs[l], ws[l], sem + l, **((mods or {}).get(l, {})))
    return out


def cli(out, nombre, filas, n, plan_mod=None, res_mod=None, plan_raw=None):
    d = out / nombre; d.mkdir(parents=True, exist_ok=True); t = d / "tabla.csv"
    with open(t, "w", newline="") as f: w = csv.DictWriter(f, fieldnames=CAMPOS, extrasaction="ignore"); w.writeheader(); w.writerows(filas)
    plan = dict(n_splits=n, niveles=[dict(nivel=l, eps=e) for l, e in enumerate([0, .002, .005, .01, .02, .05])], ids_sha256=hashlib.sha256("\n".join(R.universo(n)).encode()).hexdigest())
    plan.update(plan_mod or {}); (d / "plan.json").write_text(plan_raw if plan_raw is not None else json.dumps(plan))
    rs = dict(tabla_sha256=sha(t), plan_sha256=sha(d / "plan.json")); rs.update(res_mod or {}); (d / "res.json").write_text(json.dumps(rs))
    p = subprocess.run([sys.executable, "-I", str(H / "analisis_Q13DR.py"), "--tabla", str(t), "--tabla-sha", sha(t), "--plan", str(d / "plan.json"), "--plan-sha", sha(d / "plan.json"),
                        "--resumen", str(d / "res.json"), "--out", str(d)], capture_output=True, text=True)
    if p.returncode != 0:
        aborta = p.returncode == 3 and p.stderr.startswith("ABORTA:") and "Traceback" not in p.stderr
        return dict(veredicto="ABORTA" if aborta else f"CRASH rc={p.returncode}", detalle=(p.stderr or p.stdout)[-300:])
    return resumen(json.loads((d / "RESULTADO_Q13DR.json").read_text()))


def resumen(r): return dict(veredicto=r["veredicto"], equivalencia=r.get("equivalencia_secundaria"), extremo=r.get("extremo"), motivos=r["motivos_inconclusive"],
                            bootstrap=r.get("bootstrap"), D={k: v["D"] for k, v in r.get("primaria", {}).items()}, faltantes=r.get("faltantes"), secundarios=r.get("secundarios"))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    res = {}; fallos = []
    def esperar(n, o, e, eq=None, ext=None, extra_ok=True):
        ok = o["veredicto"] == e and (eq is None or o.get("equivalencia") == eq) and (ext is None or o.get("extremo") == ext) and extra_ok
        res[n] = dict({k: v for k, v in o.items() if k != "secundarios"}, esperado=[e, eq, ext], ok=ok)
        if not ok: fallos.append(n)
        print(("OK   " if ok else "FALLA"), n, o["veredicto"], o.get("equivalencia"), o.get("extremo"), "(esperado", e, eq, ext, ")",
              {k: round(v, 4) for k, v in (o.get("D") or {}).items()}, (o.get("bootstrap") or {}).get("IC95_beta"), (o.get("motivos") or "")[:2] if o.get("motivos") else "", flush=True)
    def run(filas, NN): return resumen(R.analizar(filas, NN, True, "", B=499, NB=300, B2=99, BQ=99))
    def nuc(n, filas, NN, e, eq=None, ext=None): esperar("nucleo:" + n, run(filas, NN), e, eq, ext)
    # reglas puras
    puras = []
    for ic, e in [([0.001, 0.1], "MODULA"), ([-0.01, 0.015], "NO_CONCLUYENTE"), ([0.0, 0.02], "NO_CONCLUYENTE")]: puras.append((R.clasificar_beta(ic), e))
    for ic, e in [([-0.01, 0.015], "NO_MODULA"), ([-0.03, 0.01], "NO_ESTABLECIDA"), ([-0.01, 0.03], "NO_ESTABLECIDA"), ([0.001, 0.01], "NO_MODULA"), ([-0.02, 0.02], "NO_MODULA")]: puras.append((R.equivalencia(ic), e))
    for p5, ic, e in [(True, [0.001, 0.02], "PERSISTE"), (False, [-0.004, 0.005], "DESAPARECE"), (False, [-0.004, 0.009], "INDETERMINADO"), (True, [-0.001, 0.004], "PERSISTE")]: puras.append((R.clasificar_extremo(p5, ic), e))
    puras += [(R.spearman([1] * 6, C), None), (R.spearman([.05, .04, .04, .02, .01, .0], C), float(np.corrcoef([6, 4.5, 4.5, 3, 2, 1], [6, 5, 4, 3, 2, 1])[0, 1]))]
    for cv in (.5, .1, .2, .3, .7, 1.0):   # N01: constantes decimales
        try: R.pendiente([1, 2, 3, 4, 5, 6], [cv] * 6); puras.append((f"sin error c={cv}", "FloatingPointError"))
        except FloatingPointError: puras.append(("FloatingPointError", "FloatingPointError"))
    try: R.pendiente([1, 2, 3, 4, 5, float("nan")], C); puras.append(("sin error nan", "FloatingPointError"))
    except FloatingPointError: puras.append(("FloatingPointError", "FloatingPointError"))
    puras += [(R.rango_c([.3, .35, .4, .45, .5, .6]), .6 - .3), (R.rango_c(C), C[0] - C[-1])]   # N02
    bad = [(o, e) for o, e in puras if not (o == e or (isinstance(o, float) and isinstance(e, float) and abs(o - e) < 1e-12))]
    res["reglas_puras"] = dict(n=len(puras), fallos=[str(x) for x in bad]); fallos += [f"pura:{x}" for x in bad]; print("reglas puras:", len(puras), "fallos", bad, flush=True)
    b1 = base(); b8 = base(8)
    # logica
    nuc("niveles_iguales_N100", cohorte(b1), 100, "NO_CONCLUYENTE", "NO_MODULA", "PERSISTE")
    nuc("N800_modula_y_desaparece", cohorte(b8, ws=(1, .8, .6, .4, .2, 0)), 800, "MODULA", None, "DESAPARECE")
    nuc("N800_modula_y_persiste", cohorte(b8, ws=(1, .9, .8, .7, .6, .5)), 800, "MODULA", None, "PERSISTE")
    nuc("N100_ruido_independiente_sin_precision", cohorte(b1, ws=(1, .9, .9, .9, .9, .9)), 100, "NO_CONCLUYENTE", "NO_ESTABLECIDA")
    # compuertas
    nuc("c_no_monotona", cohorte(b1, cs=[.86, .70, .72, .54, .42, .36]), 100, "INCONCLUSIVE_MANIPULACION")
    nuc("rango_menor_030", cohorte(b1, cs=[.86, .82, .78, .74, .70, .60]), 100, "INCONCLUSIVE_MANIPULACION")
    nuc("L0_sin_colapso", cohorte(b1, cs=[.79, .70, .61, .54, .42, .36]), 100, "INCONCLUSIVE_MANIPULACION")
    nuc("L2_pierde_acc_005", cohorte(b1, mods={2: dict(acc_panel250="0.85")}), 100, "INCONCLUSIVE_MANIPULACION")
    nuc("L2_gana_acc_005", cohorte(b1, mods={2: dict(acc_panel250="1.0")}), 100, "INCONCLUSIVE_MANIPULACION")
    nuc("L5_pierde_acc_009_permitido", cohorte(b1, mods={5: dict(acc_panel250="0.84")}), 100, "NO_CONCLUYENTE", "NO_MODULA")
    nuc("L5_pierde_acc_011", cohorte(b1, mods={5: dict(acc_panel250="0.82")}), 100, "INCONCLUSIVE_MANIPULACION")
    nuc("L4_gana_acc_permitido", cohorte(b1, mods={4: dict(acc_panel250="1.0")}), 100, "NO_CONCLUYENTE", "NO_MODULA")
    nuc("L0_sin_senal", cohorte(b1, ws=(0, 1, 1, 1, 1, 1)), 100, "INCONCLUSIVE_SIN_SENAL_CONTROL")
    # auditoria F01: el punto usa c de las filas comunes
    g = np.random.default_rng(281401); f1 = cohorte(b1)
    for r in f1: r["c250"] = repr(float(C[int(r["nivel"])] - 0.05 + 0.1 * g.random()))
    sp_out = {int(r["split"]) for r in f1 if r["nivel"] == "1" and not r["error"]}; s0 = sorted(sp_out)[0]
    [r.update(error="x") for r in [r for r in f1 if r["nivel"] == "1" and int(r["split"]) == s0 and not r["error"]][:3]]
    o = run(f1, 100); com = [r for r in f1 if r["nivel"] == "0" and valida_test(r) and int(r["split"]) != s0]
    exp = float(np.median([float(r["c250"]) for r in com if all_ok(f1, int(r["split"]))]))
    ok1 = o["bootstrap"] is not None and o["bootstrap"].get("c_comunes") is not None and abs(o["bootstrap"]["c_comunes"][0] - exp) < 1e-15
    esperar("auditoria:F01_punto_usa_c_comunes", o, "NO_CONCLUYENTE", extra_ok=ok1)
    # F02: L constante en replicas
    f2 = cohorte(b1); sdist = sorted({int(r["split"]) for r in f2})[0]
    for r in f2: r["rho_caras_10"] = repr(math.e if int(r["split"]) == sdist else 1.0)
    o = run(f2, 100); bt = o.get("bootstrap") or {}
    esperar("auditoria:F02_N05_L_constante_en_bootstrap", o, "INCONCLUSIVE", extra_ok=any("bootstrap degenerado" in m for m in o["motivos"]) and
            len(bt.get("fallos", [])) == bt.get("replicas_fallidas", -1) > 20)
    # comunes < 80 %
    f3 = cohorte(b1); spl = sorted({int(r["split"]) for r in f3})
    for l in range(6):
        mal = set(spl[8 * l: 8 * l + 8])
        for s in mal: [r.update(error="x") for r in [r for r in f3 if r["nivel"] == str(l) and int(r["split"]) == s and not r["error"]][:3]]
    o = run(f3, 100); esperar("validacion:comunes_menor_80", o, "INCONCLUSIVE", extra_ok=any("comunes" in m for m in o["motivos"]))
    # dominio
    f4 = cohorte(b1); v = [i for i, r in enumerate(f4) if r["nivel"] == "2" and not r["error"]]
    f4[v[0]]["q250"] = "-0.1"; f4[v[1]]["acc_panel250"] = "1.1"; f4[v[2]]["c250"] = "0"; f4[v[3]]["c250"] = "1.2"; f4[v[4]]["c250"] = "1.0"; f4[v[5]]["rho_caras_250"] = "0"
    o = run(f4, 100); base_f = sum(1 for r in f4 if r["nivel"] == "2" and r["error"])
    esperar("validacion:dominio_5_invalidos_1_valido", o, "NO_CONCLUYENTE", extra_ok=o["faltantes"]["L2"] == base_f + 5)
    # validacion por CLI
    full = cohorte(b1); g = np.random.default_rng(281301)
    esperar("cli:completa", cli(out, "completa", full, 100), "NO_CONCLUYENTE", "NO_MODULA", "PERSISTE")
    l3 = [i for i, r in enumerate(full) if r["nivel"] == "3" and not r["error"]]; ya = sum(1 for r in full if r["nivel"] == "3" and r["error"]); sel = g.permutation(l3)
    e25 = copy.deepcopy(full); [e25[i].update(error="x") for i in sel[:25 - ya]]; esperar("cli:L3_25_faltantes_limite", cli(out, "e25", e25, 100), "NO_CONCLUYENTE")
    e26 = copy.deepcopy(full); [e26[i].update(error="x") for i in sel[:26 - ya]]; esperar("cli:L3_26_faltantes", cli(out, "e26", e26, 100), "INCONCLUSIVE")
    esperar("cli:duplicados", cli(out, "dup", full + full[:2], 100), "ABORTA")
    esperar("cli:id_ajeno", cli(out, "ajeno", full + [dict(full[0], trajectory="q13dr_L6_s0000_k0")], 100), "ABORTA")
    esperar("cli:plan_niveles_incompletos", cli(out, "nplan", full, 100, plan_mod=dict(niveles=[dict(nivel=0, eps=0)])), "ABORTA")
    esperar("cli:plan_seis_eps_cero", cli(out, "eps0", full, 100, plan_mod=dict(niveles=[dict(nivel=l, eps=0) for l in range(6)])), "ABORTA")
    esperar("cli:plan_sin_eps", cli(out, "sineps", full, 100, plan_mod=dict(niveles=[dict(nivel=l) for l in range(6)])), "ABORTA")
    esperar("cli:plan_sin_clave_nivel", cli(out, "sinniv", full, 100, plan_mod=dict(niveles=[dict(eps=e) for e in R.EPS])), "ABORTA")
    esperar("cli:plan_n_fraccional", cli(out, "nfrac", full, 100, plan_mod=dict(n_splits=100.5)), "ABORTA")
    esperar("cli:plan_n_cero", cli(out, "n0", full, 100, plan_mod=dict(n_splits=0)), "ABORTA")
    esperar("cli:plan_n_bool", cli(out, "nbool", full, 100, plan_mod=dict(n_splits=True)), "ABORTA")
    esperar("cli:plan_n_sobre_tope", cli(out, "n401", full, 100, plan_mod=dict(n_splits=401)), "ABORTA")
    esperar("cli:plan_ilegible", cli(out, "ilegible", full, 100, plan_raw="{no json"), "ABORTA")
    esperar("cli:plan_eps_entero_enorme_N03", cli(out, "epsbig", full, 100, plan_raw=json.dumps(dict(n_splits=100, ids_sha256="x",
            niveles=[dict(nivel=l, eps=e) for l, e in enumerate(R.EPS)])).replace('"eps": 0.05', '"eps": ' + "1" + "0" * 400)), "ABORTA")
    esperar("cli:plan_ausente_N04", cli_rutas(out, "plan_ausente", full, plan="NO_EXISTE.json"), "ABORTA")
    esperar("cli:plan_directorio_N04", cli_rutas(out, "plan_dir", full, plan="."), "ABORTA")
    esperar("cli:tabla_ausente_N04", cli_rutas(out, "tabla_ausente", full, tabla="NO_EXISTE.csv"), "ABORTA")
    esperar("cli:resumen_ausente_N04", cli_rutas(out, "res_ausente", full, resumen="NO_EXISTE.json"), "ABORTA")
    esperar("cli:plan_otros_ids", cli(out, "plan", full, 100, plan_mod=dict(ids_sha256="0" * 64)), "INCONCLUSIVE")
    esperar("cli:resumen_otra_tabla", cli(out, "resu", full, 100, res_mod=dict(tabla_sha256="0" * 64)), "INCONCLUSIVE")
    xc = copy.deepcopy(full); [r.update(X10="-2") for r in xc if r["nivel"] == "4"]; esperar("cli:L4_X_constante", cli(out, "xc", xc, 100), "INCONCLUSIVE")
    res["fallos"] = fallos; res["analisis_sha256"] = sha(H / "analisis_Q13DR.py"); res["pruebas_sha256"] = sha(Path(__file__)); res["fixture_sha256"] = sha(FIX)
    (out / "pruebas_Q13DR.json").write_text(json.dumps(R.limpio(res), indent=2, ensure_ascii=False, allow_nan=False)); print("FALLOS:", fallos)


def valida_test(r): return R.valida(r)


def cli_rutas(out, nombre, filas, plan=None, tabla=None, resumen=None):
    """N04: rutas ausentes o directorios en lugar de los archivos."""
    d = out / nombre; d.mkdir(parents=True, exist_ok=True); t = d / "tabla.csv"
    with open(t, "w", newline="") as f: w = csv.DictWriter(f, fieldnames=CAMPOS, extrasaction="ignore"); w.writeheader(); w.writerows(filas)
    pl = dict(n_splits=100, niveles=[dict(nivel=l, eps=e) for l, e in enumerate(R.EPS)], ids_sha256=hashlib.sha256("\n".join(R.universo(100)).encode()).hexdigest())
    (d / "plan.json").write_text(json.dumps(pl)); (d / "res.json").write_text(json.dumps(dict(tabla_sha256=sha(t), plan_sha256=sha(d / "plan.json"))))
    P = d / plan if plan else d / "plan.json"; T = d / tabla if tabla else t; Rz = d / resumen if resumen else d / "res.json"
    p = subprocess.run([sys.executable, "-I", str(H / "analisis_Q13DR.py"), "--tabla", str(T), "--tabla-sha", sha(t), "--plan", str(P), "--plan-sha", sha(d / "plan.json"),
                        "--resumen", str(Rz), "--out", str(d)], capture_output=True, text=True)
    aborta = p.returncode == 3 and p.stderr.startswith("ABORTA:") and "Traceback" not in p.stderr
    return dict(veredicto="ABORTA" if aborta else f"rc={p.returncode}", detalle=(p.stderr or p.stdout)[-300:])


def all_ok(filas, s):
    return all(sum(1 for r in filas if r["nivel"] == str(l) and int(r["split"]) == s and R.valida(r)) >= 3 for l in range(6))


if __name__ == "__main__":
    main()
