"""pruebas_Q13M2.py v2 - regresiones de analisis_Q13M2.py antes de congelar. Fixture: G3 s=0.8 (C2/fixtures/G3_trajectories.csv) copiada en
11 niveles SINTETICOS; referencia LS = tabla real de Q13-DR (ed00364f...), solo para reproducir beta_LS. Semillas fijas.
Uso: python3 -I pruebas_Q13M2.py --out <dir>"""
import argparse, copy, csv, hashlib, json, math, subprocess, sys
from pathlib import Path
import numpy as np
H = Path(__file__).resolve().parent; sys.path.insert(0, str(H)); import analisis_Q13M2 as M
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
FIX = H.parent / "C2" / "fixtures" / "G3_trajectories.csv"
LS = H.parent / "Q13DR" / "cohorte_q13dr" / "q13dr_cohorte.csv"
CAMPOS = ["trajectory", "nivel", "split", "k", "X10", "R250", "c250", "q250", "rho_caras_10", "rho_caras_250", "rho_vert_10", "rho_vert_250", "acc_panel250", "acc_train250", "error"]
C = dict(A0=.86, LP1=.69, LP2=.61, LP3=.56, LP4=.50, LP5=.40, WD1=.69, WD2=.61, WD3=.56, WD4=.50, WD5=.44)


def base(tiles=1):
    out = []
    for t in range(tiles):
        for r in csv.DictReader(open(FIX)):
            if abs(float(r["s"]) - 0.8) > 1e-9: continue
            q = {c: r.get(c, "") for c in CAMPOS}; q.update(split=str(int(r["split"]) + 100 * t), k=r["k"], acc_panel250="0.93", acc_train250="1.0",
                                                         error="" if r["pair_valid"] == "True" else "invalido"); out.append(q)
    return out


W_DEC = [1, .8, .6, .4, .2, 0]


def cohorte(filas, w=None, c=None, sem=700, mods=None):
    """w: dict nivel -> peso de X real (resto ruido). c: dict nivel -> c250."""
    w = w or {}; c = dict(C, **(c or {})); out = []
    xs = np.array([float(r["X10"]) for r in filas if not r["error"]]); sd = xs.std()
    for i, nv in enumerate(M.NOMBRES):
        g = np.random.default_rng(sem + i); wi = w.get(nv, 1.0)
        for r in filas:
            q = dict(r); q.update(trajectory=f"q13m2_{nv}_s{int(r['split']):04d}_k{r['k']}", nivel=nv, c250=repr(float(c[nv])))
            if wi < 1 and not r["error"]: q["X10"] = repr(float(wi * float(r["X10"]) + math.sqrt(1 - wi * wi) * sd * float(g.standard_normal())))
            q.update((mods or {}).get(nv, {})); out.append(q)
    return out


def dec(m): return {f"{m}{j}": W_DEC[j] for j in range(1, 6)}


def cli(out, nombre, filas, n, plan_mod=None, res_mod=None, ls_sha=None):
    d = out / nombre; d.mkdir(parents=True, exist_ok=True); t = d / "tabla.csv"
    with open(t, "w", newline="") as f: w = csv.DictWriter(f, fieldnames=CAMPOS, extrasaction="ignore"); w.writeheader(); w.writerows(filas)
    plan = dict(n_splits=n, niveles=[dict(nivel=a, brazo=b, dosis=c) for a, b, c in M.NIVELES], ids_sha256=hashlib.sha256("\n".join(M.universo(n)).encode()).hexdigest())
    plan.update(plan_mod or {}); (d / "plan.json").write_text(json.dumps(plan))
    rs = dict(tabla_sha256=sha(t), plan_sha256=sha(d / "plan.json")); rs.update(res_mod or {}); (d / "res.json").write_text(json.dumps(rs))
    p = subprocess.run([sys.executable, "-I", str(H / "analisis_Q13M2.py"), "--tabla", str(t), "--tabla-sha", sha(t), "--plan", str(d / "plan.json"), "--plan-sha", sha(d / "plan.json"),
                        "--resumen", str(d / "res.json"), "--tabla-ls", str(LS), "--tabla-ls-sha", ls_sha or sha(LS), "--out", str(d)], capture_output=True, text=True)
    if p.returncode != 0:
        ab = p.returncode == 3 and p.stderr.startswith("ABORTA:") and "Traceback" not in p.stderr
        return dict(veredicto_conjunto="ABORTA" if ab else f"CRASH rc={p.returncode}", detalle=(p.stderr or p.stdout)[-300:])
    return resumen(json.loads((d / "RESULTADO_Q13M2.json").read_text()))


def resumen(r):
    pm = r.get("por_manipulador", {})
    return dict(veredicto_conjunto=r["veredicto_conjunto"], LP=pm.get("LP", {}).get("veredicto"), WD=pm.get("WD", {}).get("veredicto"),
                IC_LP=pm.get("LP", {}).get("IC975_beta"), IC_WD=pm.get("WD", {}).get("IC975_beta"), motivos=r.get("motivos_inconclusive"),
                compat=r.get("secundarios", {}).get("compatibilidad_LS"), lp_wd=r.get("secundarios", {}).get("LP_menos_WD"))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    res = {}; fallos = []
    def esperar(n, o, e, lp=None, wd=None, extra=True):
        ok = o["veredicto_conjunto"] == e and (lp is None or o.get("LP") == lp) and (wd is None or o.get("WD") == wd) and extra
        res[n] = dict({k: v for k, v in o.items() if k != "compat"}, esperado=[e, lp, wd], ok=ok)
        if not ok: fallos.append(n)
        print(("OK   " if ok else "FALLA"), n, o["veredicto_conjunto"], o.get("LP"), o.get("WD"), "(esperado", e, lp, wd, ")", o.get("IC_LP"), o.get("IC_WD"), (o.get("motivos") or [])[:2], flush=True)
    # reglas puras
    puras = []
    v = np.linspace(-1, 1, 801); puras.append((M.q(v, M.Q_PRI), [float(np.quantile(v, .0125)), float(np.quantile(v, .9875))]))
    for vv, e in [((("MODULA", "MODULA")), "MODULACION_REPRODUCIDA_EN_DOS_VIAS"), (("MODULA", "NO_CONCLUYENTE"), "REPRODUCIDA_SOLO_EN_LP"),
                  (("NO_CONCLUYENTE", "MODULA"), "REPRODUCIDA_SOLO_EN_WD"), (("NO_CONCLUYENTE", "NO_CONCLUYENTE"), "NO_REPRODUCIDA"),
                  (("MODULA", "INCONCLUSIVE_MANIPULACION"), "INCONCLUSIVE_PARCIAL"), (("INCONCLUSIVE", "NO_CONCLUYENTE"), "INCONCLUSIVE_PARCIAL")]:
        puras.append((M.conjunto(dict(LP=vv[0], WD=vv[1])), e))
    g = np.random.default_rng(1); a1 = g.normal(.08, .02, 2000); a2 = g.normal(.08, .02, 2000); a3 = g.normal(-.05, .02, 2000)
    puras.append((M.compatibilidad(a1, a2, .08, .08)["lectura"], "SIN_DIFERENCIA_DETECTADA")); puras.append((M.compatibilidad(a3, a2, -.05, .08)["lectura"], "DIFIERE"))
    try: M.compatibilidad(a1[:10], a2, .08, .08); puras.append(("sin error", "ValueError"))
    except ValueError: puras.append(("ValueError", "ValueError"))
    plan_ok = dict(n_splits=200, niveles=[dict(nivel=a, brazo=b, dosis=c) for a, b, c in M.NIVELES], ids_sha256="x")
    for mod, e in [({}, "OK"), (dict(n_splits=321), "Aborta"), (dict(n_splits=320), "OK"), (dict(n_splits=True), "Aborta"), (dict(niveles=plan_ok["niveles"][:10]), "Aborta"),
                   (dict(niveles=[dict(x, dosis=(x["dosis"] * 2 if x["nivel"] == "WD3" else x["dosis"])) for x in plan_ok["niveles"]]), "Aborta"),
                   (dict(niveles=[dict(x, brazo=("LS" if x["nivel"] == "LP1" else x["brazo"])) for x in plan_ok["niveles"]]), "Aborta"),
                   (dict(niveles=[dict(x, dosis=(10 ** 400 if x["nivel"] == "LP5" else x["dosis"])) for x in plan_ok["niveles"]]), "Aborta")]:
        try: M.validar_plan(dict(plan_ok, **mod)); o = "OK"
        except M.Aborta: o = "Aborta"
        puras.append((o, e))
    bad = [(o, e) for o, e in puras if o != e]; res["reglas_puras"] = dict(n=len(puras), fallos=[str(x) for x in bad]); fallos += [f"pura:{x}" for x in bad]
    print("reglas puras:", len(puras), "fallos", bad, flush=True)
    # referencia LS reproduce Q13-DR
    fls = {r["trajectory"]: r for r in csv.DictReader(open(LS))}; ls = M.referencia_ls(fls, 300)
    okb = abs(ls["beta"] - 0.07692466151365258) <= 1e-12 and not ls["fallos"]; res["beta_LS_reproduce_Q13DR"] = dict(beta=ls["beta"], ok=okb); print("beta_LS", repr(ls["beta"]), okb, flush=True)
    if not okb: fallos.append("beta_LS")   # F04: tolerancia 1e-12
    def run(filas, NN): return resumen(M.analizar(filas, NN, True, "", ls=ls, B=499, NB=300))
    b1 = base(); b8 = base(8)
    # logica
    o = run(cohorte(b1), 100); esperar("niveles_iguales_N100", o, "NO_REPRODUCIDA", "NO_CONCLUYENTE", "NO_CONCLUYENTE",
                                      extra=o["compat"]["compatibilidad_LP"]["lectura"] == "DIFIERE")
    o = run(cohorte(b8, w={**dec("LP"), **dec("WD")}), 800); esperar("N800_ambos_modulan", o, "MODULACION_REPRODUCIDA_EN_DOS_VIAS", "MODULA", "MODULA",
                                                                  extra=o["lp_wd"] is not None)
    esperar("N800_solo_LP", run(cohorte(b8, w=dec("LP")), 800), "REPRODUCIDA_SOLO_EN_LP", "MODULA", "NO_CONCLUYENTE")
    esperar("N800_solo_WD", run(cohorte(b8, w=dec("WD")), 800), "REPRODUCIDA_SOLO_EN_WD", "NO_CONCLUYENTE", "MODULA")
    # compuertas
    esperar("A0_sin_colapso", run(cohorte(b1, c=dict(A0=.79)), 100), "INCONCLUSIVE_MANIPULACION")
    esperar("WD_no_monotono_LP_modula", run(cohorte(b8, w=dec("LP"), c=dict(WD3=.62)), 800), "INCONCLUSIVE_PARCIAL", "MODULA", "INCONCLUSIVE_MANIPULACION")
    esperar("LP_rango_menor_030", run(cohorte(b1, c=dict(LP1=.80, LP2=.75, LP3=.70, LP4=.65, LP5=.60)), 100), "INCONCLUSIVE_PARCIAL", "INCONCLUSIVE_MANIPULACION", "NO_CONCLUYENTE")
    esperar("WD2_pierde_acc", run(cohorte(b1, mods=dict(WD2=dict(acc_panel250="0.86"))), 100), "INCONCLUSIVE_PARCIAL", "NO_CONCLUYENTE", "INCONCLUSIVE_MANIPULACION")
    esperar("LP5_pierde_011", run(cohorte(b1, mods=dict(LP5=dict(acc_panel250="0.82"))), 100), "INCONCLUSIVE_PARCIAL", "INCONCLUSIVE_MANIPULACION", "NO_CONCLUYENTE")
    esperar("A0_sin_senal", run(cohorte(b1, w=dict(A0=0)), 100), "INCONCLUSIVE_SIN_SENAL_CONTROL", "INCONCLUSIVE_SIN_SENAL_CONTROL", "INCONCLUSIVE_SIN_SENAL_CONTROL")
    # degeneracion en un nivel de WD -> WD INCONCLUSIVE, LP sigue
    f = cohorte(b1); s0 = sorted({int(r["split"]) for r in f})[0]
    for r in f:
        if r["nivel"] == "WD4": r["rho_caras_10"] = repr(math.e if int(r["split"]) == s0 else 1.0)
    o = run(f, 100); esperar("WD4_L_degenerado", o, "INCONCLUSIVE_PARCIAL", "NO_CONCLUYENTE", "INCONCLUSIVE", extra=any("WD: bootstrap degenerado" in m for m in o["motivos"]))
    # auditoria F01: fallo o degeneracion en un nivel exclusivo no borra al otro manipulador; en A0 es global
    def mod_nivel(nv, campo, valor):
        f = cohorte(b8, w=dec("LP") if nv.startswith("WD") else dec("WD"))
        for r in f:
            if r["nivel"] == nv: r[campo] = valor
        return f
    esperar("F01_WD3_Y_constante", run(mod_nivel("WD3", "rho_caras_250", "1.0"), 800), "INCONCLUSIVE_PARCIAL", "MODULA", "INCONCLUSIVE")
    esperar("F01_LP3_Y_constante", run(mod_nivel("LP3", "rho_caras_250", "1.0"), 800), "INCONCLUSIVE_PARCIAL", "INCONCLUSIVE", "MODULA")
    esperar("F01_WD3_X_constante", run(mod_nivel("WD3", "X10", "-2"), 800), "INCONCLUSIVE_PARCIAL", "MODULA", "INCONCLUSIVE")
    esperar("F01_WD3_L_constante", run(mod_nivel("WD3", "rho_caras_10", "0.5"), 800), "INCONCLUSIVE_PARCIAL", "MODULA", "INCONCLUSIVE")
    esperar("F01_A0_X_constante_global", run(mod_nivel("A0", "X10", "-2"), 800), "INCONCLUSIVE")
    # comunes < 80 %
    f = cohorte(b1); spl = sorted({int(r["split"]) for r in f})
    for i, nv in enumerate(M.NOMBRES):
        for s in spl[5 * i: 5 * i + 3]: [r.update(error="x") for r in [r for r in f if r["nivel"] == nv and int(r["split"]) == s and not r["error"]][:3]]
    o = run(f, 100); esperar("comunes_menor_80", o, "INCONCLUSIVE", extra=any("comunes" in m for m in o["motivos"]))
    # CLI
    full = cohorte(b1)
    esperar("cli:completa", cli(out, "completa", full, 100), "NO_REPRODUCIDA", "NO_CONCLUYENTE", "NO_CONCLUYENTE")
    esperar("cli:duplicados", cli(out, "dup", full + full[:2], 100), "ABORTA")
    esperar("cli:id_ajeno", cli(out, "ajeno", full + [dict(full[0], trajectory="q13m2_LS1_s0000_k0")], 100), "ABORTA")
    esperar("cli:dosis_distinta", cli(out, "dosis", full, 100, plan_mod=dict(niveles=[dict(nivel=a, brazo=b, dosis=(c * 1.01 if a == "LP2" else c)) for a, b, c in M.NIVELES])), "ABORTA")
    esperar("cli:n_sobre_tope", cli(out, "n321", full, 100, plan_mod=dict(n_splits=321)), "ABORTA")
    esperar("cli:tabla_LS_otro_sha", cli(out, "lssha", full, 100, ls_sha="0" * 64), "ABORTA")
    d = out / "colision"; d.mkdir(parents=True, exist_ok=True); (d / "RESULTADO_Q13M2.json").write_text("MARCADOR")
    o = cli(out, "colision", full, 100); esperar("cli:F02_salida_existente_no_se_sobrescribe", o, "ABORTA", extra=(d / "RESULTADO_Q13M2.json").read_text() == "MARCADOR")
    esperar("cli:resumen_otra_tabla", cli(out, "resu", full, 100, res_mod=dict(tabla_sha256="0" * 64)), "INCONCLUSIVE")
    res["fallos"] = fallos; res["analisis_sha256"] = sha(H / "analisis_Q13M2.py"); res["pruebas_sha256"] = sha(Path(__file__)); res["fixture_sha256"] = sha(FIX); res["ls_sha256"] = sha(LS)
    (out / "pruebas_Q13M2.json").write_text(json.dumps(M.DR.limpio(res), indent=2, ensure_ascii=False, allow_nan=False)); print("FALLOS:", fallos)


if __name__ == "__main__":
    main()
