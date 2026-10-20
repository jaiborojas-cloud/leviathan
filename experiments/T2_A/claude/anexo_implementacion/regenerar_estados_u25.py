"""regenerar_estados_u25.py - regenera el estado de update 25 de las visitas del piloto, con la puerta del prefijo de A0.

EXPLORATORIO/OPERATIVO. No clasifica ni asigna outcomes. Solo LEE la compacta (no escribe en ella) y escribe en --out.
Para cada trayectoria del piloto (por defecto las 20 de PILOTO_20_visitas_update25.csv):
  1. PUERTA DEL PREFIJO (exigida por A0): reentrena 5 updates desde las semillas del manifiesto (new_session(S, J)) y
     compara los parametros con checkpoint_005.pt: max|dtheta| <= 1e-12. Tambien compara M y f con state_005.npz (informativo).
     Si la puerta FALLA, esa trayectoria queda GATE_FAIL y NO se genera su estado de update 25.
  2. Reentrena 25 updates en una sesion NUEVA (mismo patron que train_u25_j6.py) y guarda state_025_regen_<traj>.npz (M, f) + SHA-256.
  3. Autocomprobacion: para j5 y j6 compara el SHA-256 con las copias ya usadas (845c2251..., 0e3fbfd3...); si difiere, avisa.
Salidas en --out: state_025_regen_<traj>.npz, regeneracion_u25.csv (una fila por trayectoria), regeneracion_u25.log.
Los estados son COPIAS REGENERADAS desde semillas, no los estados de la corrida original; no sustituyen ninguna corrida confirmada.

Ejecucion (PowerShell; del orden de decenas de segundos por trayectoria):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "D:\\RIPG_DATA\\T2_A\\expediente\\anexo_implementacion\\regenerar_estados_u25.py"
"""
import argparse, csv, hashlib, platform, re, sys, time
from pathlib import Path
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--root", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
ap.add_argument("--list", default=r"D:\RIPG_DATA\T2_A\expediente\PILOTO_20_visitas_update25.csv")
ap.add_argument("--out", default=r"D:\RIPG_DATA\T2_A\expediente\estados_u25")
ap.add_argument("--ids", nargs="*", help="trayectorias explicitas (sustituye a --list)")
ap.add_argument("--tol", type=float, default=1e-12)
a = ap.parse_args()
ROOT = Path(a.root); OUT = Path(a.out); OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "sources"))
import torch, core, training  # noqa: E402

REF = {"split8_j5_true": "845c22519a20be8c", "split8_j6_true": "0e3fbfd3dd290b6c"}   # prefijos de SHA-256 ya usados
log = open(OUT / "regeneracion_u25.log", "a", encoding="utf-8")
def say(*p):
    s = " ".join(str(x) for x in p); print(s, flush=True); log.write(s + "\n"); log.flush()

ids = a.ids or [r["trajectory"] for r in csv.DictReader(open(a.list, encoding="utf-8"))]
say(f"== {time.strftime('%Y-%m-%d %H:%M:%S')}  python {platform.python_version()}  numpy {np.__version__}  torch {torch.__version__}  {platform.platform()}")
say(f"trayectorias: {len(ids)}  tol prefijo: {a.tol:g}")

def state_of(m, Xv, yv):
    Rb, Ub, f = core.make_geom_state(m, Xv, yv)
    return core.subset_M(Rb, Ub, [0, 1, 2]).detach().numpy(), f.detach().numpy()

rows = []
for tid in ids:
    mo = re.fullmatch(r"split(\d+)_j(\d+)_true", tid)
    if not mo:
        say(f"{tid}: nombre no reconocido, se omite"); continue
    S, J = int(mo.group(1)), int(mo.group(2)); t0 = time.time()
    row = dict(trajectory=tid, split=S, init=J, gate="", max_dtheta="", max_dM_vs_state005="", max_df_vs_state005="",
               state_file="", sha256="", ref_check="", seconds="")
    try:
        X, y, Xv, yv, m, opt, rng = training.new_session(S, J)
        training.updates(m, opt, rng, X, y, 5)
        ck = torch.load(ROOT / "trajectories" / tid / "checkpoint_005.pt", map_location="cpu", weights_only=False)
        mc = core.WineMLP().double(); mc.load_state_dict(ck["model"] if "model" in ck else ck)
        dth = max(float(torch.max(torch.abs(p.detach() - q.detach()))) for p, q in zip(m.parameters(), mc.parameters()))
        M5, f5 = state_of(m, Xv, yv)
        with np.load(ROOT / "trajectories" / tid / "state_005.npz") as z:
            row["max_dM_vs_state005"] = repr(float(np.max(np.abs(M5 - z["M"]))))
            row["max_df_vs_state005"] = repr(float(np.max(np.abs(f5 - z["f"]))))
        row["max_dtheta"] = repr(dth); row["gate"] = "PASS" if dth <= a.tol else "GATE_FAIL"
        if row["gate"] == "PASS":
            X, y, Xv, yv, m, opt, rng = training.new_session(S, J)
            training.updates(m, opt, rng, X, y, 25)
            M25, f25 = state_of(m, Xv, yv)
            fp = OUT / f"state_025_regen_{tid}.npz"; np.savez(fp, M=M25, f=f25)
            row["state_file"] = fp.name; row["sha256"] = hashlib.sha256(fp.read_bytes()).hexdigest()
            if tid in REF:
                row["ref_check"] = "COINCIDE" if row["sha256"].startswith(REF[tid]) else "DIFIERE_de_la_copia_usada"
    except Exception as e:                      # no se oculta: queda registrado y se sigue con la siguiente
        row["gate"] = f"ERROR: {type(e).__name__}: {e}"
    row["seconds"] = f"{time.time() - t0:.1f}"; rows.append(row)
    say(f"{tid}: gate={row['gate']}  dtheta={row['max_dtheta']}  sha={row['sha256'][:12]}  ref={row['ref_check']}  {row['seconds']} s")

with open(OUT / "regeneracion_u25.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
n_pass = sum(r["gate"] == "PASS" for r in rows)
say(f"RESUMEN: {n_pass} PASS, {len(rows) - n_pass} no PASS de {len(rows)}. CSV: {OUT / 'regeneracion_u25.csv'}")
say("Estados = copias regeneradas; sin clasificacion ni outcomes.")
log.close()
