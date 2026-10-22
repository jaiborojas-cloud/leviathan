"""validar_ejecutor_v12.py - validacion del ejecutor de produccion visita_produccion_v12.py ANTES de registrar su hash.
Solo lee los datos existentes; escribe solo en --work (carpeta nueva). No produce visitas de produccion: las pruebas A y B solo
entrenan (sin geometria) y la prueba C repite una visita del update 25 YA evaluada en el piloto.

A. Entrenamiento en el update 25: para cada visita del piloto con carpeta en --piloto, el ejecutor (--solo-entrenamiento) debe
   reproducir BIT A BIT el checkpoint.pt y el state.npz de esa visita (SHA-256 iguales).
B. Encadenamiento: para 3 trayectorias y k = 50, ..., 250, el checkpoint del ejecutor en k (k-5 updates seguidos desde el update 5)
   debe coincidir (parametros y estado de Adam con diferencia maxima <= 1e-12, la tolerancia de replay() del prerregistro; estado del
   RNG identico; se registra la diferencia exacta) con reanudar desde el checkpoint del ejecutor
   en k-25 y entrenar 25 updates mas, que es lo que significa una trayectoria.
C. Visita completa: split8_j6_true en el update 25 con el ejecutor debe dar, con comparar_visita.py, RESULTADO GLOBAL PASS frente
   al result.json de la visita del piloto.

Uso (PowerShell):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "<ruta>\\validar_ejecutor_v12.py" --work "D:\\RIPG_DATA\\T2_A\\expediente\\validacion_ejecutor_v12_2026-10-22"
"""
import argparse, hashlib, json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def correr(args, log):
    log.write("$ " + " ".join(map(str, args)) + "\n"); log.flush()
    p = subprocess.run(args, capture_output=True, text=True)
    log.write(p.stdout[-4000:] + "\n" + p.stderr[-4000:] + "\n"); log.flush()
    return p.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--root", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
    ap.add_argument("--piloto", default=r"D:\RIPG_DATA\T2_A\expediente\piloto_visitas")
    ap.add_argument("--impl", default=str(HERE.parent / "anexo_implementacion"), help="carpeta con resumable_dop853_instrumentado_v11.py, t4prima.py y comparar_visita.py")
    ap.add_argument("--encadenar", nargs="+", default=["split8_j6_true", "split9_j12_true", "split11_j22_true"])
    a = ap.parse_args()
    work = Path(a.work); work.mkdir(parents=True, exist_ok=False)
    py = sys.executable; ejec = HERE / "visita_produccion_v12.py"
    # el ejecutor importa el driver y t4prima de su propia carpeta: se copian los congelados junto a una copia del ejecutor
    run_dir = work / "codigo"; run_dir.mkdir()
    for f in ("resumable_dop853_instrumentado_v11.py", "t4prima.py"):
        (run_dir / f).write_bytes((Path(a.impl) / f).read_bytes())
    (run_dir / ejec.name).write_bytes(ejec.read_bytes()); ejec_run = run_dir / ejec.name
    log = open(work / "log.txt", "w", encoding="utf-8"); res = dict(ejecutor_sha256=sha(ejec), driver_sha256=sha(run_dir / "resumable_dop853_instrumentado_v11.py"),
                                                                    t4prima_sha256=sha(run_dir / "t4prima.py"), A=[], B=[], C=None)
    # ---- A ----
    for vd in sorted(Path(a.piloto).iterdir()):
        case = vd.name; st = vd / "states" / case
        if not (st / "checkpoint.pt").exists() or not (st / "state.npz").exists():
            continue
        w = work / "A" / case
        rc = correr([py, "-I", ejec_run, "--case", case, "--work", w, "--step", "25", "--root", a.root, "--solo-entrenamiento"], log)
        e = json.loads((w / "ENTRENAMIENTO.json").read_text()) if rc == 0 else {}
        ok = rc == 0 and e.get("checkpoint_sha256") == sha(st / "checkpoint.pt") and e.get("field_sha256") == sha(st / "state.npz")
        res["A"].append(dict(caso=case, ok=ok, rc=rc, checkpoint=e.get("checkpoint_sha256"), ref_checkpoint=sha(st / "checkpoint.pt"),
                             field=e.get("field_sha256"), ref_field=sha(st / "state.npz")))
        print(f"A {case}: {'OK' if ok else 'FALLA'}", flush=True)
    # ---- B ----
    sys.path.insert(0, str(Path(a.root) / "sources"))
    import numpy as np, torch, core
    from training import new_session, updates
    for case in a.encadenar:
        s_, j_, _ = case.split("_"); S, J = int(s_[5:]), int(j_[1:])
        ck = {}
        for k in range(25, 251, 25):
            w = work / "B" / case / f"u{k}"
            rc = correr([py, "-I", ejec_run, "--case", case, "--work", w, "--step", str(k), "--root", a.root, "--solo-entrenamiento"], log)
            ck[k] = torch.load(w / "states" / case / "checkpoint.pt", weights_only=False) if rc == 0 else None
        for k in range(50, 251, 25):
            if ck[k] is None or ck[k - 25] is None:
                res["B"].append(dict(caso=case, k=k, ok=False, motivo="falta checkpoint")); continue
            X, y, Xv, yv, m, opt, rng = new_session(S, J); prev = ck[k - 25]
            m.load_state_dict(prev["model"]); opt.load_state_dict(prev["optimizer"]); rng.bit_generator.state = prev["numpy_rng"]; torch.set_rng_state(prev["torch_rng"])
            updates(m, opt, rng, X, y, 25)
            dpar = max(float((m.state_dict()[n] - ck[k]["model"][n]).abs().max()) for n in ck[k]["model"])
            so, sr = opt.state_dict()["state"], ck[k]["optimizer"]["state"]
            dopt = max(float((so[i][t] - sr[i][t]).abs().max()) for i in sr for t in sr[i] if torch.is_tensor(sr[i][t]))
            drng = rng.bit_generator.state == ck[k]["numpy_rng"]
            ok = dpar <= 1e-12 and dopt <= 1e-12 and drng and ck[k]["step"] == k
            res["B"].append(dict(caso=case, k=k, ok=ok, max_dif_parametros=dpar, max_dif_adam=dopt, rng_igual=drng))
            print(f"B {case} k={k}: {'OK' if ok else 'FALLA'} (dpar={dpar}, dadam={dopt}, rng={drng})", flush=True)
    # ---- C ----
    case = "split8_j6_true"; w = work / "C" / case; ref = Path(a.piloto) / case / "states" / case / "result.json"
    t0 = time.perf_counter()
    rc = correr([py, "-I", ejec_run, "--case", case, "--work", w, "--step", "25", "--root", a.root], log)
    obt = w / "states" / case / "result.json"
    rc2 = correr([py, "-I", Path(a.impl) / "comparar_visita.py", obt, ref], log) if obt.exists() else 99
    res["C"] = dict(caso=case, ok=(rc == 0 and rc2 == 0), rc_visita=rc, rc_comparacion=rc2, segundos=time.perf_counter() - t0, referencia=str(ref))
    print(f"C {case}: {'OK' if res['C']['ok'] else 'FALLA'}", flush=True)
    res["veredicto"] = "PASA" if (res["A"] and all(r["ok"] for r in res["A"]) and res["B"] and all(r["ok"] for r in res["B"]) and res["C"]["ok"]) else "FALLA"
    res["resumen"] = dict(A=f"{sum(r['ok'] for r in res['A'])}/{len(res['A'])}", B=f"{sum(r['ok'] for r in res['B'])}/{len(res['B'])}", C=res["C"]["ok"])
    (work / "VALIDACION_EJECUTOR_v12.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(dict(veredicto=res["veredicto"], resumen=res["resumen"], ejecutor_sha256=res["ejecutor_sha256"]), indent=2))
    sys.exit(0 if res["veredicto"] == "PASA" else 1)


if __name__ == "__main__":
    main()
