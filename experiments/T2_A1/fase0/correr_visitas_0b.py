"""correr_visitas_0b.py (v1) - visitas nuevas de la fase 0b de T2-A1 con el ejecutor v12 SIN CAMBIOS.

Cola fija (PROTOCOLO_0b_BORRADOR_v0.md, seccion 2):
  * nuevas: split10_j19_true u150, u250; split11_j20..j24_true u50, u150, u250  (17)  -> <out>/visitas/<tray>/u<k>
  * repeticiones D0-1 con --extra-budget de las 4 pausas en auditoria del lote 0  (4)  -> <out>/repeticiones/<tray>/u<k>_r1
Verifica el hash del ejecutor (2381fbcc...3347) y de cada checkpoint_005 contra metadata/cohort_manifest.csv (columnas
trajectory y checkpoint_sha256; no lee nada de baseline/ ni comparators/). Antes de cada visita exige >= 50 GB libres en D.
No escribe en las carpetas del lote 0 de T2-A0. Reanuda: una visita con archivo terminal no se repite.

Uso (PowerShell):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "<repo>\\experiments\\T2_A1\\fase0\\correr_visitas_0b.py" `
     --out "D:\\RIPG_DATA\\T2_A1\\fase0b" --procesos 8
  --seco: verifica hashes, espacio y la cola, y termina sin visitar.
"""
import argparse, csv, hashlib, json, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

EJECUTOR_SHA = "2381fbcca8ea17472dca69cc6ce2bf6bc7a0a4aa1910d318da5fef7e5fe93347"
NUEVAS = [("split10_j19_true", k) for k in (150, 250)] + [(f"split11_j{j}_true", k) for j in range(20, 25) for k in (50, 150, 250)]
REPETICIONES = [("split10_j16_true", 50), ("split10_j18_true", 50), ("split9_j13_true", 50), ("split9_j13_true", 150)]
TERMINALES = ("VISITA_COMPLETA.json", "REVISION_PENDIENTE.json", "ERROR_EJECUCION.json")
MIN_LIBRE_GB = 50.0

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
ahora = lambda: time.strftime("%Y-%m-%dT%H:%M:%S%z")


def cola(out):
    return ([(t, k, Path(out) / "visitas" / t / f"u{k}", False) for t, k in NUEVAS] +
            [(t, k, Path(out) / "repeticiones" / t / f"u{k}_r1", True) for t, k in REPETICIONES])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--procesos", type=int, default=8)
    ap.add_argument("--codigo", default=r"D:\RIPG_DATA\T2_A\produccion\codigo")
    ap.add_argument("--root", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
    ap.add_argument("--seco", action="store_true")
    a = ap.parse_args()
    ej = Path(a.codigo) / "visita_produccion_v12.py"
    if sha(ej) != EJECUTOR_SHA:
        sys.exit(f"ABORTA: el ejecutor no coincide con v12 ({sha(ej)[:12]})")
    man = {r["trajectory"]: r["checkpoint_sha256"] for r in csv.DictReader(open(Path(a.root) / "metadata" / "cohort_manifest.csv", encoding="utf-8"))}
    q = cola(a.out); errores = []
    for t in sorted({t for t, *_ in q}):
        ck = Path(a.root) / "trajectories" / t / "checkpoint_005.pt"
        if not ck.exists() or sha(ck) != man.get(t):
            errores.append(f"checkpoint_005 de {t} ausente o con hash distinto al manifiesto")
    libre = shutil.disk_usage(a.out if Path(a.out).exists() else Path(a.out).anchor).free / 2**30
    rep = dict(fecha=ahora(), ejecutor_sha256=EJECUTOR_SHA, script_sha256=sha(Path(__file__)), visitas=len(q), libre_D_gb=round(libre, 1), errores=errores,
               cola=[dict(trajectory=t, update=k, directorio=str(d), extra_budget=x) for t, k, d, x in q])
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    if errores:
        sys.exit("ABORTA: " + "; ".join(errores))
    if a.seco:
        Path(a.out).mkdir(parents=True, exist_ok=True)
        (Path(a.out) / f"PRUEBA_SECO_0b_{time.strftime('%Y%m%d_%H%M%S')}.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False)); return
    reg = Path(a.out) / "registro_0b.csv"; Path(a.out).mkdir(parents=True, exist_ok=True)
    nuevo = not reg.exists()
    fh = open(reg, "a", newline="", encoding="utf-8"); w = csv.writer(fh)
    if nuevo:
        w.writerow(["trajectory", "update", "directorio", "extra_budget", "estado", "rc", "segundos", "fin"])

    def una(item):
        t, k, d, x = item
        if any((d / f).exists() for f in TERMINALES):
            return None
        if shutil.disk_usage(d.anchor).free / 2**30 < MIN_LIBRE_GB:
            return (t, k, str(d), x, "NO_INICIADA_SIN_DISCO", None, 0, ahora())
        d.mkdir(parents=True, exist_ok=True); t0 = time.time()
        cmd = [sys.executable, "-I", str(ej), "--case", t, "--step", str(k), "--work", str(d), "--root", a.root] + (["--extra-budget"] if x else [])
        with open(d / "lanzador_stdout.log", "a", encoding="utf-8") as so, open(d / "lanzador_stderr.log", "a", encoding="utf-8") as se:
            so.write(f"== {ahora()} {' '.join(cmd)}\n"); so.flush(); rc = subprocess.call(cmd, stdout=so, stderr=se)
        est = next((f for f in TERMINALES if (d / f).exists()), "SIN_ARCHIVO_TERMINAL")
        return (t, k, str(d), x, est, rc, round(time.time() - t0, 1), ahora())

    with ThreadPoolExecutor(max_workers=a.procesos) as pool:
        for fut in as_completed([pool.submit(una, it) for it in q]):
            r = fut.result()
            if r:
                w.writerow(r); fh.flush(); print(f"{r[0]} u{r[1]}{' (extra)' if r[3] else ''}: {r[4]} ({r[6]} s)", flush=True)
    fh.close(); print("FIN", flush=True)


if __name__ == "__main__":
    main()
