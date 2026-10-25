"""pruebas_C1_v2.py - regresiones de analisis_C1_v2.py antes de congelar (casos D01-D04 de la auditoria D2c y controles).
Construye la tabla de descubrimiento desde el repo (d1 + d6, splits 12-167; X ~ log(1 - p_min_val) de d6 en u10) y una copia
re-etiquetada al universo confirmatorio (s + 156, init por la regla) SOLO como fixture sintetico. Semillas y orden fijos.
Uso (desde experiments/DIN_borde/C1): python3 -I pruebas_C1_v2.py --out <dir>
"""
import argparse, copy, csv, hashlib, json, math, subprocess, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; DB = HERE.parent
SCRIPT = HERE / "analisis_C1_v2.py"
sys.path.insert(0, str(HERE)); import analisis_C1_v2 as A
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
CAMPOS = ["trajectory", "split", "init", "X", "rho_u10", "rho_u30", "rho_u250", "cuerda_u10", "cara_max_u10", "rho_u10_alta", "auditada", "error"]


def descubrimiento():
    rho = {(r["trajectory"], int(r["update"])): r["rho"] for r in csv.DictReader(open(DB / "d1" / "d1_estados.csv"))}
    d6 = {(r["trajectory"], int(r["update"])): r for r in csv.DictReader(open(DB / "d6" / "PROGRESO_d6.csv")) if not r["error"]}
    out = []
    for t in A.universo(12, 167):
        a = d6[(t, 10)]
        out.append(dict(trajectory=t, split=a["split"], init=a["init"], X=repr(math.log(max(1 - float(a["p_min_val"]), 1e-300))), rho_u10=a["rho_borde"],
                        rho_u30=d6[(t, 30)]["rho_borde"], rho_u250=rho[(t, 250)], cuerda_u10="", cara_max_u10="", rho_u10_alta="", auditada="0", error=""))
    return out


def reetiquetar(filas):
    out = []
    for r in filas:
        s = int(r["split"]) + 156; k = (int(r["init"]) - 5 - 5 * (int(r["split"]) - 8)); j = 5 + 5 * (s - 8) + k
        q = dict(r); q.update(trajectory=f"split{s}_j{j}_true", split=str(s), init=str(j)); out.append(q)
    return out


def escribir(p, filas):
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, extrasaction="ignore"); w.writeheader(); w.writerows(filas)
    return sha(p)


def cli(out, nombre, filas, rc_mod=None, gc_mod=None):
    d = out / nombre; d.mkdir(parents=True, exist_ok=True); t = d / "tabla.csv"; h = escribir(t, filas)
    rc = dict(modo="cohorte", tabla_sha256=h, script_sha256="SCRIPT_COHORTE_FIXTURE"); gc = dict(modo="compuerta", PASA=True, script_sha256="SCRIPT_COHORTE_FIXTURE")
    if rc_mod: rc.update(rc_mod)
    if gc_mod: gc.update(gc_mod)
    (d / "rc.json").write_text(json.dumps(rc)); (d / "gc.json").write_text(json.dumps(gc))
    p = subprocess.run([sys.executable, "-I", str(SCRIPT), "--tabla", str(t), "--tabla-sha", h, "--resumen-cohorte", str(d / "rc.json"),
                        "--compuerta", str(d / "gc.json"), "--out", str(d)], capture_output=True, text=True)
    if p.returncode != 0:
        return dict(veredicto="ABORTA" if "ABORTA" in (p.stderr + p.stdout) else f"CRASH rc={p.returncode}", detalle=(p.stderr or p.stdout)[-300:])
    r = json.loads((d / "RESULTADO_C1.json").read_text()); return dict(veredicto=r["veredicto"], motivos=r["motivos_inconclusive"], faltantes=r["faltantes"],
                                                                        D=(r["primaria"] or {}).get("D"), p=(r["primaria"] or {}).get("p"))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--rapido", action="store_true"); a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True); res = {}; fallos = []
    base = descubrimiento(); conf = reetiquetar(base)
    def esperar(nombre, obtenido, esperado):
        ok = obtenido.startswith(esperado); res[nombre] = dict(obtenido=obtenido, esperado=esperado, ok=ok)
        if not ok: fallos.append(nombre)
        print(f"{'OK ' if ok else 'FALLA'} {nombre}: {obtenido} (esperado {esperado})", flush=True)
    # 1) descubrimiento por el nucleo (B=5000) y por CLI en modo descubrimiento
    r = A.analizar(base, A.universo(12, 167), True, "", 5000 if not a.rapido else 499, 2000)
    res["descubrimiento"] = dict(D=r["primaria"]["D"], p=r["primaria"]["p"], pendiente=r["primaria"]["pendiente_X"], veredicto=r["veredicto"])
    print("descubrimiento", res["descubrimiento"], flush=True)
    # 2) casos de cohorte (CLI confirmatorio, B=5000) - D01..D03
    g = np.random.default_rng(280001); idx = g.permutation(780)
    casos = []
    casos.append(("completa", conf, None, None, "PASS"))
    casos.append(("omitidas_47", [r for i, r in enumerate(conf) if i not in set(idx[:47])], None, None, "INCONCLUSIVE"))
    e47 = copy.deepcopy(conf); [e47[i].update(error="fallo sintetico") for i in idx[:47]]; casos.append(("errores_47", e47, None, None, "INCONCLUSIVE"))
    e39 = copy.deepcopy(conf); [e39[i].update(error="fallo sintetico") for i in idx[:39]]; casos.append(("errores_39", e39, None, None, "PASS"))
    e40 = copy.deepcopy(conf); [e40[i].update(error="fallo sintetico") for i in idx[:40]]; casos.append(("errores_40", e40, None, None, "INCONCLUSIVE"))
    sp_om = set(g.permutation(np.arange(168, 324))[:40].tolist()); casos.append(("splits_omitidos_40", [r for r in conf if int(r["split"]) not in sp_om], None, None, "INCONCLUSIVE"))
    casos.append(("duplicados", conf + conf, None, None, "ABORTA"))
    casos.append(("id_ajeno", conf + [dict(conf[0], trajectory="split999_j9999_true", split="999")], None, None, "ABORTA"))
    rz = copy.deepcopy(conf); rz[5]["rho_u10"] = "0"; rz[6]["rho_u250"] = "-1"; rz[7]["X"] = "nan"; casos.append(("dominio_3_invalidos", rz, None, None, "PASS"))
    lc = copy.deepcopy(conf); [r.update(rho_u10="0.5") for r in lc]; casos.append(("L_constante", lc, None, None, "INCONCLUSIVE"))
    yc = copy.deepcopy(conf); [r.update(rho_u250="0.2") for r in yc]; casos.append(("Y_constante", yc, None, None, "INCONCLUSIVE"))
    xc = copy.deepcopy(conf); [r.update(X="-3") for r in xc]; casos.append(("X_constante", xc, None, None, "INCONCLUSIVE"))
    casos.append(("compuerta_otro_script", conf, None, dict(script_sha256="OTRO"), "INCONCLUSIVE"))
    casos.append(("compuerta_PASA_texto", conf, None, dict(PASA="true"), "INCONCLUSIVE"))
    casos.append(("resumen_otra_tabla", conf, dict(tabla_sha256="0" * 64), None, "INCONCLUSIVE"))
    for nombre, filas, rcm, gcm, esp in casos:
        o = cli(out, nombre, filas, rcm, gcm); res.setdefault("cli", {})[nombre] = o; esperar("cli:" + nombre, o["veredicto"], esp)
    # 3) controles por el nucleo (B=400), semillas fijas, orden planificado
    def ctl(nombre, f, esp, semilla):
        gg = np.random.default_rng(semilla)
        r = A.analizar(base, A.universo(12, 167), True, "", 400, 1000, transformar=lambda sp, X, L, Y: f(sp, X, L, Y, gg))
        res.setdefault("controles", {})[nombre] = dict(veredicto=r["veredicto"], D=(r["primaria"] or {}).get("D"), p=(r["primaria"] or {}).get("p"))
        esperar("control:" + nombre, r["veredicto"], esp)
    def e_res(sp, L, Y):
        z = (L - L.mean()) / L.std(); B = np.column_stack([A.cen(z ** k, sp) for k in (1, 2, 3)]); Yc = A.cen(Y, sp); return Yc - B @ np.linalg.lstsq(B, Yc, rcond=None)[0]
    ctl("X_igual_L", lambda sp, X, L, Y, g: (L.copy(), L, Y), "NOT_MET", 290001)
    ctl("X_cubica_L", lambda sp, X, L, Y, g: (((L - L.mean()) / L.std()) ** 3, L, Y), "NOT_MET", 290002)
    ctl("Y_g_L_X_afin", lambda sp, X, L, Y, g: (L - 2, L, -(((L - L.mean()) / L.std()) ** 2) + 0.05 * g.standard_normal(len(L))), "NOT_MET", 290003)
    ctl("X_constante", lambda sp, X, L, Y, g: (np.zeros(len(L)), L, Y), "INCONCLUSIVE", 290004)
    ctl("ruido_nulo", lambda sp, X, L, Y, g: (g.standard_normal(len(L)), L, Y), "NOT_MET", 290005)
    ctl("incremento_real_r03", lambda sp, X, L, Y, g: (0.3 * e_res(sp, L, Y) / e_res(sp, L, Y).std() + math.sqrt(.91) * g.standard_normal(len(L)), L, Y), "PASS", 290006)
    ctl("L_con_error_LIMITACION", lambda sp, X, L, Y, g: (L.copy(), L + 0.5 * L.std() * g.standard_normal(len(L)), Y + 3 * A.cen((L - L.mean()) / L.std(), sp) * A.cen(Y, sp).std()), "PASS", 290007)
    ctl("X_escalon_L_ALCANCE", lambda sp, X, L, Y, g: ((L > np.median(L)).astype(float), L, Y + 2 * A.cen((L > np.median(L)).astype(float), sp)), "PASS", 290008)
    res["fallos"] = fallos; res["script_analisis_sha256"] = sha(SCRIPT); res["pruebas_sha256"] = sha(Path(__file__))
    (out / "pruebas_C1_v2.json").write_text(json.dumps(res, indent=2, ensure_ascii=False)); print("FALLOS:", fallos)


if __name__ == "__main__":
    main()
