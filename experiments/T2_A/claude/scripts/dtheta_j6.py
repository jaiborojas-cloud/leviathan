"""dtheta_j6.py - compuerta del prefijo de 5 updates para split8_j6_true (exigida por A0: max|dtheta| <= 1e-12).

EXPLORATORIO. Solo lee la compacta; no escribe nada (solo imprime). No asigna clasificaciones.
Reentrena 5 updates desde las semillas del manifiesto (split 1000+s, init 2000+j, minibatches 4000+10s+j)
y compara los parametros con checkpoint_005.pt de la compacta. Tambien compara M y f con state_005.npz.

Ejecucion (PowerShell):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "D:\\RIPG_DATA\\T2_A\\cribado_borde\\margen\\dtheta_j6.py"
"""
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
sys.path.insert(0, str(ROOT / "sources"))
import core  # noqa: E402
import training  # noqa: E402

SID, S, J = "split8_j6_true", 8, 6
TOL = 1e-12

X, y, Xv, yv, m, opt, rng = training.new_session(S, J)
training.updates(m, opt, rng, X, y, 5)

ck = torch.load(ROOT / "trajectories" / SID / "checkpoint_005.pt", map_location="cpu", weights_only=False)
sd = ck["model"] if "model" in ck else ck
mc = core.WineMLP().double()
mc.load_state_dict(sd)

dth = 0.0
for (name, a), b in zip(m.named_parameters(), mc.parameters()):
    d = float(torch.max(torch.abs(a.detach() - b.detach())))
    dth = max(dth, d)
    print(f"{name:<14} max|dtheta| {d!r}")
print(f"max|dtheta| (global): {dth!r}   umbral A0: {TOL!r}   {'PASS' if dth <= TOL else 'FAIL'}")

Rb, Ub, f_r = core.make_geom_state(m, Xv, yv)
M_r = core.subset_M(Rb, Ub, [0, 1, 2]).detach().numpy()
f_r = f_r.detach().numpy()
with np.load(ROOT / "trajectories" / SID / "state_005.npz") as a:
    print(f"max|DM| vs state_005.npz: {np.max(np.abs(M_r - a['M']))!r}")
    print(f"max|Df| vs state_005.npz: {np.max(np.abs(f_r - a['f']))!r}")
