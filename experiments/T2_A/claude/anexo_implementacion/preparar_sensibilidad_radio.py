"""preparar_sensibilidad_radio.py - PRUEBA DE SENSIBILIDAD (no es una visita del piloto, no asigna Y).
Pregunta: ¿la diferencia entre la visita j17 con T4' (radio ...136) y la de v1.0 (radio ...186), 5e-16, explica por si sola los campos que salen del
criterio de comparar_visita (first_self_intersection, max_Dexp_condition, min_abs_det_Dexp)?
Construye un directorio de trabajo nuevo cuyo nominal.json tiene radio = r_T4' + delta, con la frontera tomada del MISMO objeto denso de la integracion T4'
(checkpoint de parada). Luego se corre la visita normal (sin --forzar-t4prima: bg.calibrate reutiliza nominal.json) y se compara con comparar_visita.py.
No toca el directorio fuente. Uso:
  python -I preparar_sensibilidad_radio.py --src <work T4'> --dst <work nuevo> --case split10_j17_true --delta -5e-16
"""
import argparse, json, shutil, sys, zipfile
from pathlib import Path
import numpy as np
from scipy.integrate import OdeSolution
from shapely.geometry import Polygon
ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True); ap.add_argument("--dst", required=True); ap.add_argument("--case", required=True)
ap.add_argument("--delta", type=float, required=True, help="usar --delta=-5e-16 (con signo negativo, con =)")
ap.add_argument("--mocks", default=r"D:\RIPG_DATA\T2_A\cribado_borde\margen\mocks")
ap.add_argument("--root", default=r"D:\RIPG_DATA\T2_A\data\baselines\Leviathan_T2A_800_basales_compacto")
a = ap.parse_args()
src, dst = Path(a.src) / "states" / a.case, Path(a.dst) / "states" / a.case
assert (src / "nominal.json").exists() and (src / "state.npz").exists() and (src / "checkpoint.pt").exists()
assert not dst.exists(), "el destino ya existe"
for pth in (str(Path(a.root) / "sources" / "instrument"), a.mocks, str(Path(a.root) / "sources")):   # como la visita: los checkpoints referencian audit/core
    sys.path.insert(0, pth)
import geometry as G
nom = json.loads((src / "nominal.json").read_text())
assert nom.get("calibration_mode") == "T4_PRIME_AREA_STOP"
r0 = nom["radius"]; r = r0 + a.delta
# checkpoint de parada de T4': el primer step_*.json cuya cantidad de pasos coincide con 'steps' de nominal.json
ck = None
for dd in sorted((Path(a.src) / "ode_checkpoints" / "rays_t4p").iterdir()):
    for jp in sorted(dd.glob("step_*.json")):
        m = json.loads(jp.read_text())
        if m["steps"] == nom["steps"]:
            ck = dd / m["archive"]
assert ck, "no se encontro el checkpoint de parada de T4'"
import cloudpickle
with zipfile.ZipFile(ck) as zf:
    b = cloudpickle.loads(zf.read("integration.pkl"))
sol = OdeSolution(b["ts"], b["interpolants"]); n = 2048
with np.load(src / "state.npz") as z:
    g = G.Geometry(z["M"], z["f"])
area_of = lambda x: G.area7(g, G.triangles(sol(np.linspace(0, x, 33)).T.reshape(33, 2, n, 2)[:, 0]))
assert abs(area_of(r0) - nom["area_degree5"]) < 1e-15, "no se reproduce el area de nominal.json con el objeto denso"
dst.mkdir(parents=True)
shutil.copyfile(src / "state.npz", dst / "state.npz"); shutil.copyfile(src / "checkpoint.pt", dst / "checkpoint.pt")
border = sol(r).reshape(2, n, 2)[0]; poly = Polygon(border)
np.savez_compressed(dst / "boundary_calibration.npz", P=border, radius=r)
A = area_of(r)
res = dict(nom); res.update(radius=r, area_degree5=A, area_relative_error=A / 0.02 - 1, polygon_valid=poly.is_valid, polygon_simple=poly.exterior.is_simple,
                            calibration_mode="SENSIBILIDAD_RADIO_PERTURBADO", radius_T4prima=r0, delta=a.delta)
(dst / "nominal.json").write_text(json.dumps(res, indent=2))
print(f"radio T4'={r0!r}  radio prueba={r!r}  delta={a.delta:g}  area={A!r}")
