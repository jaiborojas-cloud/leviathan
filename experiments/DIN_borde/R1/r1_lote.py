"""r1_lote.py - DIN-R1 etapa 1: rho_borde_v2 (r3) sobre estados de la cohorte C1. Reanudable; procesa un tramo [ini, fin).
Uso (VM): python3 r1_lote.py <mnt> <ini> <fin> <salida.csv>"""
import csv, json, sys, time
from pathlib import Path
import numpy as np
H = Path(__file__).resolve().parent; sys.path.insert(0, str(H))
import rho_borde_v2_r3_copia as V
mnt, ini, fin, out = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), Path(sys.argv[4])
gp = mnt / "sources" / "geometry.py"
tab = list(csv.DictReader(open(mnt / "DIN_C1" / "cohorte" / "c1_cohorte.csv")))[ini:fin]
hechos = {(r["trajectory"], r["update"]) for r in csv.DictReader(open(out))} if out.exists() else set()
nuevo = not out.exists(); fh = open(out, "a", newline=""); w = csv.writer(fh)
if nuevo: w.writerow(["trajectory", "update", "rho_v1", "rho_caras", "rho_vert", "ganador", "status", "seg", "error"])
for r in tab:
    for k in ("10", "250"):
        if (r["trajectory"], k) in hechos: continue
        z = np.load(mnt / "DIN_C1" / "cohorte" / "estados" / r["trajectory"] / f"u{k}.npz"); M = z["M"].astype(float); M = (M + M.T) / 2; f = z["f"].astype(float)
        t0 = time.time()
        try:
            o = V.rho_borde_v2(M, f, geometry_path=gp); g = o.get("rho_caras_winner", {}) or {}
            w.writerow([r["trajectory"], k, r[f"rho_u{k}"], o.get("rho_caras"), o.get("rho_vert"), g.get("kind", g.get("type", "")), o["status"], round(time.time() - t0, 3), ""])
        except Exception as e:
            w.writerow([r["trajectory"], k, r[f"rho_u{k}"], "", "", "", "ERROR", round(time.time() - t0, 3), repr(e)[:200]])
        fh.flush()
