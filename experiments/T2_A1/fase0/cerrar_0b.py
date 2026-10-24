"""cerrar_0b.py (v1) - combinacion y compuerta de la fase 0b (PROTOCOLO_0b_v1_CONGELADO.md, seccion 4). SOLO LECTURA.

Combina:
  * I1 (instrumento_D sobre el lote 0, updates 50/150/250): D_lote0/D_visitas.csv, sin split10_j19 u150/u250;
  * I2 (visitas nuevas): la corrida se interrumpio por decision del responsable (2026-10-23 21:38) con la compuerta ya
    determinada, asi que no escribio D_visitas.csv. Se reconstruye con las MISMAS funciones del instrumento congelado
    (asignar_paso2, certifica, controles), reutilizando solo cota.json ya existentes; un caso del paso 3 sin cota.json queda
    D = ? con la razon "no calculado". No se calcula ninguna cota nueva (los controles ya existen y no se recalculan);
  * I3 (repeticiones D0-1, secundario): D_repeticiones/D_visitas.csv, solo las 4 programadas.
Escribe <fase0b>/cierre_0b/D_primarias.csv, D_repeticiones.csv y RESUMEN_0b.json. No usa X.

Uso: python -I cerrar_0b.py <carpeta fase0b> <ruta de instrumento_D.py> [--sources <sources>] [--estados-control <dir>]
"""
import argparse, csv, hashlib, importlib.util, json, os, sys
from pathlib import Path
from types import SimpleNamespace

PRIM = (50, 150, 250)
NUEVAS = [("split10_j19_true", k) for k in (150, 250)] + [(f"split11_j{j}_true", k) for j in range(20, 25) for k in PRIM]
REPETICIONES = [("split10_j16_true", 50), ("split10_j18_true", 50), ("split9_j13_true", 50), ("split9_j13_true", 150)]
RAZON_NO_CALC = "paso 3 no calculado: corrida I2 interrumpida por decision del responsable (2026-10-23 21:41 y 2026-10-24 05:35), compuerta ya determinada"
CAMPOS = ["fuente", "trajectory", "update", "D", "via", "razon", "estado_ejecutor", "motivo_ejecutor", "nominal_existe", "U", "U2", "segundos_paso3"]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tam(d):
    return sum(f.stat().st_size for f in Path(d).rglob("*") if f.is_file()) if d and Path(d).exists() else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fase0b"); ap.add_argument("instrumento")
    ap.add_argument("--sources", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto\sources")
    ap.add_argument("--estados-control", default=r"D:\RIPG_DATA\T2_A\expediente\estados_u25")
    a = ap.parse_args()
    B = Path(a.fase0b)
    spec = importlib.util.spec_from_file_location("instrumento_D", a.instrumento)
    I = importlib.util.module_from_spec(spec); spec.loader.exec_module(I)
    filas = []
    # --- I1 ---
    for r in csv.DictReader(open(B / "D_lote0" / "D_visitas.csv", encoding="utf-8")):
        k = int(r["update"])
        if k in PRIM and not (r["trajectory"] == "split10_j19_true" and k in (150, 250)):
            filas.append(dict({c: r.get(c, "") for c in CAMPOS}, fuente="I1_lote0", update=k))
    # --- I2 (reconstruccion con funciones del instrumento) ---
    ns = SimpleNamespace(sources=a.sources, estados_control=a.estados_control, procesos=1, tope_pared=I.TOPE_PARED_S, prueba=False)
    for c in I.CONTROLES:
        if not (B / "D_nuevas" / "_controles" / c / "cota.json").exists():
            sys.exit(f"ABORTA: falta el control {c} de I2; este script no calcula cotas")
    validos2, det2 = I.controles(ns, B / "D_nuevas")
    for t, k in NUEVAS:
        r = I.asignar_paso2(t, k, B / "visitas" / t / f"u{k}")
        paso3 = r.pop("paso3")
        if paso3:
            cj = B / "D_nuevas" / t / f"u{k}" / "cota" / "cota.json"
            c = json.loads(cj.read_text()) if cj.exists() else None
            if c is None:
                r.update(D="?", razon=RAZON_NO_CALC)
            else:
                ok, raz = I.certifica(c)
                r.update(U=c.get("U"), U2=c.get("U2"), segundos_paso3=c.get("segundos"))
                r.update(D=1, via="C", razon=None) if (ok and validos2) else r.update(D="?", razon="; ".join(raz + ([] if validos2 else ["controles de la corrida no validos"])))
        filas.append(dict({c_: r.get(c_, "") for c_ in CAMPOS}, fuente="I2_nuevas_reconstruida"))
    # --- I3 ---
    reps = [dict({c: r.get(c, "") for c in CAMPOS}, fuente="I3_repeticiones") for r in csv.DictReader(open(B / "D_repeticiones" / "D_visitas.csv", encoding="utf-8"))
            if (r["trajectory"], int(r["update"])) in REPETICIONES]
    out = B / "cierre_0b"; out.mkdir(exist_ok=True)
    for nombre, fs in (("D_primarias.csv", filas), ("D_repeticiones.csv", reps)):
        with open(out / nombre, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=CAMPOS); w.writeheader(); w.writerows(fs)
    D = lambda r: str(r["D"])
    nq = sum(D(r) == "?" for r in filas)
    Y = {}
    for r in filas:
        Y.setdefault(r["trajectory"], []).append(D(r))
    Yt = {t: ("1" if "1" in ds else ("0" if all(x == "0" for x in ds) else "?")) for t, ds in Y.items()}
    razones = {}
    for r in filas:
        if D(r) == "?":
            razones[r["razon"]] = razones.get(r["razon"], 0) + 1
    por_split = {}
    for r in filas:
        s = r["trajectory"].split("_")[0]; por_split.setdefault(s, {"0": 0, "1": 0, "?": 0})[D(r)] += 1
    reg = list(csv.DictReader(open(B / "registro_0b.csv", encoding="utf-8")))
    def local(dp):   # el registro guarda rutas de Windows; se reubican bajo <fase0b> si no existen tal cual
        if Path(dp).exists():
            return dp
        parte = dp.replace("\\", "/").split("fase0b/", 1)
        return str(B / parte[1]) if len(parte) == 2 else dp
    disco = {f"{r['trajectory']}/u{r['update']}{'_r1' if r['extra_budget'] == 'True' else ''}": tam(local(r["directorio"])) for r in reg}
    res = dict(visitas_primarias=len(filas), por_D={v: sum(D(r) == v for r in filas) for v in ("0", "1", "?")},
               por_via={v: sum(r["via"] == v for r in filas) for v in ("A", "B", "C")},
               D_desconocida=nq, compuerta="PASA" if nq <= 3 else "FALLA", umbral="D = ? en <= 3 de 60",
               trayectorias=len(Yt), Y={v: sum(x == v for x in Yt.values()) for v in ("0", "1", "?")},
               fraccion_trayectorias_Y_desconocida=sum(x == "?" for x in Yt.values()) / len(Yt),
               por_split=por_split, razones_desconocida=razones,
               I2_controles_validos=validos2, I2_controles=det2,
               repeticiones_D01={f"{r['trajectory']}/u{r['update']}": dict(D=r["D"], razon=r["razon"]) for r in reps},
               segundos_ejecutor_visitas_nuevas={f"{r['trajectory']}/u{r['update']}{'_r1' if r['extra_budget'] == 'True' else ''}": float(r["segundos"]) for r in reg},
               bytes_visitas_nuevas=disco,
               script_sha256=sha(__file__), instrumento_sha256=sha(a.instrumento),
               nota="Fase 0 de T2-A1 (desarrollo). Sin X. I2 reconstruida sin calcular cotas nuevas.")
    (out / "RESUMEN_0b.json").write_text(json.dumps(res, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k not in ("I2_controles", "segundos_ejecutor_visitas_nuevas", "bytes_visitas_nuevas")}, indent=2, default=str))


if __name__ == "__main__":
    main()
