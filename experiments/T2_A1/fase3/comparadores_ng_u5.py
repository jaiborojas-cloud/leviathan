"""comparadores_ng_u5.py (v1) - comparadores NO geometricos del update 5 (diseno v2/v3 de T2-A1; secundarios, no deciden).

Por trayectoria (las 800 del manifiesto): verifica checkpoint_005.pt contra metadata/cohort_manifest.csv (solo trajectory y
checkpoint_sha256), carga el modelo con las mismas llamadas que rho_borde_u5.py (new_session, load_state_dict) y mide sin entrenar:
  train_loss  entropia cruzada media sobre todo el conjunto de entrenamiento del split
  train_acc   precision en entrenamiento;  val_acc  precision en validacion
  weight_norm norma L2 de todos los parametros
NO lee baseline/ ni comparators/ (X sigue cerrado). Salidas: comparadores_ng_u5.csv y RESUMEN_ng_u5.json con su SHA-256.

Uso (PowerShell):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "<ruta>\\comparadores_ng_u5.py" --out "D:\\RIPG_DATA\\T2_A1\\ng_u5"
"""
import os
for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_k] = "1"
import argparse, csv, hashlib, json, sys, time
from pathlib import Path

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
GEOM_SHA = "b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--root", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
    ap.add_argument("--mocks", default=r"D:\RIPG_DATA\T2_A\cribado_borde\margen\mocks")
    a = ap.parse_args(); root = Path(a.root); src = root / "sources"
    if sha(src / "geometry.py") != GEOM_SHA:
        sys.exit("ABORTA: sources/geometry.py no coincide")
    for p in (str(src / "instrument"), a.mocks, str(src)):
        sys.path.insert(0, p)
    import torch
    torch.set_num_threads(1)
    from training import new_session
    man = [(r["trajectory"], r["checkpoint_sha256"]) for r in csv.DictReader(open(root / "metadata" / "cohort_manifest.csv", encoding="utf-8"))]
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True); filas = []; t0 = time.time()
    for i, (tray, h) in enumerate(man, 1):
        S, J = int(tray.split("_")[0][5:]), int(tray.split("_")[1][1:])
        ck = root / "trajectories" / tray / "checkpoint_005.pt"
        if sha(ck) != h:
            filas.append(dict(trajectory=tray, split=S, init=J, error="checkpoint_005 no coincide")); continue
        X, y, Xv, yv, m, opt, rng = new_session(S, J)
        c = torch.load(ck, weights_only=False)
        assert c["step"] == 5 and c["split"] == S and c["init"] == J
        m.load_state_dict(c["model"]); m.eval()
        with torch.no_grad():
            o = m(X); ov = m(Xv)
            filas.append(dict(trajectory=tray, split=S, init=J,
                              train_loss=float(torch.nn.functional.cross_entropy(o, y)),
                              train_acc=float((o.argmax(1) == y).double().mean()),
                              val_acc=float((ov.argmax(1) == yv).double().mean()),
                              weight_norm=float(torch.sqrt(sum((p.double() ** 2).sum() for p in m.parameters()))),
                              checkpoint_sha256=h, error=""))
        if i % 100 == 0:
            print(f"[{i}/{len(man)}] {time.time() - t0:.0f} s", flush=True)
    tabla = out / "comparadores_ng_u5.csv"
    with open(tabla, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["trajectory", "split", "init", "train_loss", "train_acc", "val_acc", "weight_norm", "checkpoint_sha256", "error"], extrasaction="ignore")
        w.writeheader(); w.writerows(filas)
    res = dict(trayectorias=len(man), errores=sum(1 for r in filas if r.get("error")), tabla_sha256=sha(tabla), script_sha256=sha(Path(__file__)),
               fecha=time.strftime("%Y-%m-%dT%H:%M:%S%z"), nota="Comparadores no geometricos del update 5; sin X; sin visitas futuras.")
    (out / "RESUMEN_ng_u5.json").write_text(json.dumps(res, indent=2)); print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
