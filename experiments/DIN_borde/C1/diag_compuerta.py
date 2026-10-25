"""diag_compuerta.py - diagnostico de la compuerta fallida de c1_cohorte.py (2026-10-24). No entrena la cohorte nueva.
Para 5 trayectorias antiguas (split12): compara entrenamiento desde cero en este equipo contra checkpoint_000/005 de T2-A0
(generados en otro entorno) y contra el estado u50 de la fase 2. Reporta diferencias maximas, no solo igualdad.
Uso: & $PY -I diag_compuerta.py --out "D:\\RIPG_DATA\\DIN_C1\\diag_compuerta"
"""
import os
for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"
import argparse, hashlib, json, platform, sys
from pathlib import Path
import numpy as np
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True)
    ap.add_argument("--root", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
    ap.add_argument("--t2a1", default=r"D:\RIPG_DATA\T2_A1"); ap.add_argument("--mocks", default=r"D:\RIPG_DATA\T2_A\cribado_borde\margen\mocks")
    a = ap.parse_args(); root = Path(a.root); src = root / "sources"
    for p in (str(src / "instrument"), a.mocks, str(src)): sys.path.insert(0, p)
    import torch, core, sklearn
    torch.set_num_threads(1)
    from training import new_session, updates
    dif = lambda m, sd: max(float((t - sd[n]).abs().max()) for n, t in m.state_dict().items())
    res = dict(entorno=dict(python=platform.python_version(), torch=torch.__version__, numpy=np.__version__, sklearn=sklearn.__version__, plataforma=platform.platform()), casos=[])
    for k in range(5):
        j = 25 + k; t = f"split12_j{j}_true"; d = root / "trajectories" / t; R = dict(trajectory=t, archivos=sorted(x.name for x in d.iterdir()))
        X, y, Xv, yv, m, opt, rng = new_session(12, j)
        c0p = d / "checkpoint_000.pt"
        if c0p.exists():
            c0 = torch.load(c0p, weights_only=False); R["dif_param_u0"] = dif(m, c0["model"])
            R["numpy_rng_u0_igual"] = c0["numpy_rng"] == rng.bit_generator.state
        c5 = torch.load(d / "checkpoint_005.pt", weights_only=False)
        updates(m, opt, rng, X, y, 5); R["dif_param_u5_desde_cero"] = dif(m, c5["model"]); R["numpy_rng_u5_igual"] = c5["numpy_rng"] == rng.bit_generator.state
        # rama A: desde cero hasta 50; rama B: desde checkpoint_005 (como D6/fase2) hasta 50
        updates(m, opt, rng, X, y, 45); Rb, Ub, f = core.make_geom_state(m, Xv, yv); MA = core.subset_M(Rb, Ub, [0, 1, 2]).detach().numpy()
        X2, y2, Xv2, yv2, m2, o2, g2 = new_session(12, j); m2.load_state_dict(c5["model"]); o2.load_state_dict(c5["optimizer"]); g2.bit_generator.state = c5["numpy_rng"]; torch.set_rng_state(c5["torch_rng"])
        updates(m2, o2, g2, X2, y2, 45); Rb, Ub, f2 = core.make_geom_state(m2, Xv2, yv2); MB = core.subset_M(Rb, Ub, [0, 1, 2]).detach().numpy()
        ref = np.load(Path(a.t2a1) / "fase2" / "visitas" / t / "u50" / "states" / t / "state.npz")["M"]
        R.update(dif_param_u50_A_vs_B=dif(m, m2.state_dict()), dif_rel_M_u50_B_vs_fase2=float(np.abs(MB - ref).max() / np.abs(ref).max()),
                 dif_rel_M_u50_A_vs_fase2=float(np.abs(MA - ref).max() / np.abs(ref).max()))
        res["casos"].append(R); print(json.dumps(R), flush=True)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True); (out / "diag_compuerta.json").write_text(json.dumps(res, indent=2)); print(json.dumps(res["entorno"]))

if __name__ == "__main__":
    main()
