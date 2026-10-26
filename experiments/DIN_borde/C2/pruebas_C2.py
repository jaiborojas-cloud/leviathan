"""pruebas_C2.py - regresiones de analisis_C2.py antes de congelar. Fixture: cohorte G3 (PR #86, results/run_v1/trajectories.csv,
copiada en fixtures/) re-etiquetada al esquema C2. NO es dato confirmatorio. Semillas fijas. Uso: python3 -I pruebas_C2.py --out <dir>"""
import argparse, copy, csv, hashlib, json, subprocess, sys
from pathlib import Path
import numpy as np
H = Path(__file__).resolve().parent; sys.path.insert(0, str(H)); import analisis_C2 as C
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
CAMPOS = ["trajectory", "split", "k", "X10", "R250", "c250", "q250", "rho_caras_10", "rho_caras_250", "rho_vert_10", "rho_vert_250", "error"]


def fixture(s):
    out = []
    for r in csv.DictReader(open(H / "fixtures" / "G3_trajectories.csv")):
        if abs(float(r["s"]) - s) > 1e-9: continue
        q = {c: r.get(c, "") for c in CAMPOS}; q.update(trajectory=f"c2_s{int(r['split']):04d}_k{r['k']}", error="" if r["pair_valid"] == "True" else "invalido"); out.append(q)
    return out


def cli(out, nombre, filas, n, plan_mod=None, res_mod=None):
    d = out / nombre; d.mkdir(parents=True, exist_ok=True); t = d / "tabla.csv"
    with open(t, "w", newline="") as f: w = csv.DictWriter(f, fieldnames=CAMPOS, extrasaction="ignore"); w.writeheader(); w.writerows(filas)
    plan = dict(n_splits=n, ids_sha256=hashlib.sha256("\n".join(C.universo(n)).encode()).hexdigest()); plan.update(plan_mod or {})
    (d / "plan.json").write_text(json.dumps(plan)); res = dict(tabla_sha256=sha(t), plan_sha256=sha(d / "plan.json")); res.update(res_mod or {}); (d / "res.json").write_text(json.dumps(res))
    p = subprocess.run([sys.executable, "-I", str(H / "analisis_C2.py"), "--tabla", str(t), "--tabla-sha", sha(t), "--plan", str(d / "plan.json"), "--plan-sha", sha(d / "plan.json"),
                        "--resumen", str(d / "res.json"), "--out", str(d)], capture_output=True, text=True)
    if p.returncode != 0: return dict(veredicto="ABORTA" if "ABORTA" in p.stdout + p.stderr else f"CRASH {p.returncode}", detalle=(p.stderr or p.stdout)[-300:])
    r = json.loads((d / "RESULTADO_C2.json").read_text()); return dict(veredicto=r["veredicto"], motivos=r["motivos_inconclusive"], regimen=r["regimen"], primaria=r["primaria"])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    res = {}; fallos = []
    def esperar(n, o, e):
        ok = o["veredicto"].startswith(e); res[n] = dict(o, esperado=e, ok=ok)
        if not ok: fallos.append(n)
        print(("OK   " if ok else "FALLA"), n, o["veredicto"], "(esperado", e + ")", flush=True)
    base = fixture(0.8); N = 100; g = np.random.default_rng(280101); idx = g.permutation(500)
    esperar("completa_s08", cli(out, "completa", base, N), "PASS")
    esperar("s025_sin_colapso", cli(out, "s025", fixture(0.25), N), "INCONCLUSIVE_REGIMEN")
    esperar("omitidas_26", cli(out, "om26", [r for i, r in enumerate(base) if i not in set(idx[:26])], N), "INCONCLUSIVE")
    e25 = copy.deepcopy(base); [e25[i].update(error="x") for i in idx[:25]]; esperar("errores_25_limite", cli(out, "e25", e25, N), "PASS")
    e26 = copy.deepcopy(base); [e26[i].update(error="x") for i in idx[:26]]; esperar("errores_26", cli(out, "e26", e26, N), "INCONCLUSIVE")
    esperar("splits_omitidos_21", cli(out, "sp21", [r for r in base if int(r["trajectory"][4:8]) not in set(g.permutation(100)[:21].tolist())], N), "INCONCLUSIVE")
    esperar("duplicados", cli(out, "dup", base + base[:3], N), "ABORTA")
    esperar("id_ajeno", cli(out, "ajeno", base + [dict(base[0], trajectory="c2_s9999_k0")], N), "ABORTA")
    rz = copy.deepcopy(base); rz[3]["rho_caras_10"] = "0"; rz[4]["rho_caras_250"] = "-1"; rz[5]["X10"] = "nan"; esperar("dominio_3", cli(out, "dom", rz, N), "PASS")
    lc = copy.deepcopy(base); [r.update(rho_caras_10="0.5") for r in lc]; esperar("L_constante", cli(out, "lc", lc, N), "INCONCLUSIVE")
    xc = copy.deepcopy(base); [r.update(X10="-2") for r in xc]; esperar("X_constante", cli(out, "xc", xc, N), "INCONCLUSIVE")
    rg = copy.deepcopy(base); [r.update(c250="0.5") for r in rg]; esperar("regimen_forzado_fallo", cli(out, "rg", rg, N), "INCONCLUSIVE_REGIMEN")
    esperar("plan_otros_ids", cli(out, "plan", base, N, plan_mod=dict(ids_sha256="0" * 64)), "INCONCLUSIVE")
    esperar("resumen_otra_tabla", cli(out, "resu", base, N, res_mod=dict(tabla_sha256="0" * 64)), "INCONCLUSIVE")
    # controles por el nucleo
    def ctl(n, f, e, sem):
        filas = copy.deepcopy(base); gg = np.random.default_rng(sem); f(filas, gg)
        o = C.analizar(filas, N, True, "", B=999, BW=999, B2=499); esperar("control:" + n, dict(veredicto=o["veredicto"], primaria=o["primaria"]), e)
    import math
    ctl("X_igual_L", lambda F, g: [r.update(X10=repr(math.log(float(r["rho_caras_10"])))) for r in F], "NOT_MET", 290101)
    ctl("X_ruido", lambda F, g: [r.update(X10=repr(float(g.standard_normal()))) for r in F], "NOT_MET", 290102)
    res["fallos"] = fallos; res["analisis_sha256"] = sha(H / "analisis_C2.py"); res["fixture_sha256"] = sha(H / "fixtures" / "G3_trajectories.csv")
    (out / "pruebas_C2.json").write_text(json.dumps(res, indent=2, ensure_ascii=False)); print("FALLOS:", fallos)


if __name__ == "__main__":
    main()
