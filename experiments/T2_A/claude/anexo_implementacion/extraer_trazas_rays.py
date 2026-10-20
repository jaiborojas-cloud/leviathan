"""extraer_trazas_rays.py - SOLO LECTURA. Extrae, de los checkpoints ya existentes de las integraciones de RAYOS del piloto, la traza por paso aceptado
(t, dt, max|p|, max|v| sobre todos los rayos) para fijar con datos los umbrales del detector de escape (T4). No integra nada, no modifica
checkpoints, no mira X, no clasifica. Escribe un CSV nuevo y un resumen.
Fuentes: piloto_visitas/<caso>/ode_checkpoints/rays/<clave>/  (visitas completas)  y  piloto_calibracion/<caso>/ode_checkpoints/<clave>/  (calibracion).
Por integracion usa el ULTIMO checkpoint (verifica su SHA-256 contra el json). Ejecucion (PowerShell, minutos; omite integraciones de mas de --max-rays):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "D:\\RIPG_DATA\\T2_A\\expediente\\anexo_implementacion\\extraer_trazas_rays.py"
"""
import argparse, csv, hashlib, io, json, pickle, sys, zipfile
from pathlib import Path
import numpy as np
import cloudpickle  # noqa: F401  (los pickles de los checkpoints usan sus reconstructores)

class _Dummy:
    def __init__(self, *a, **k): pass
    def __call__(self, *a, **k): return _Dummy()
    def __setstate__(self, st): pass


class Loader(pickle.Unpickler):
    """Solo se necesitan las listas ts/ys: las referencias a modulos del instrumento (audit, geometry...) que no se importan aqui se sustituyen por un marcador."""
    def find_class(self, module, name):
        try:
            return super().find_class(module, name)
        except (ImportError, AttributeError):
            return _Dummy


ap = argparse.ArgumentParser()
ap.add_argument("--expediente", default=r"D:\RIPG_DATA\T2_A\expediente")
ap.add_argument("--out", default=None)
ap.add_argument("--max-rays", type=int, default=16384)
ap.add_argument("--cases", default="", help="lista separada por comas para limitar (vacio = todos)")
a = ap.parse_args()
E = Path(a.expediente); out = Path(a.out) if a.out else E / "diagnostico_t4" / "trazas_rays.csv"
out.parent.mkdir(parents=True, exist_ok=True)
want = set(x for x in a.cases.split(",") if x)
dirs = []
for case in sorted((E / "piloto_visitas").glob("split*_true")):
    r = case / "ode_checkpoints" / "rays"
    if r.is_dir(): dirs += [("visita", case.name, d) for d in sorted(r.iterdir()) if d.is_dir()]
for case in sorted((E / "piloto_calibracion").glob("split*_true")):
    r = case / "ode_checkpoints"
    if r.is_dir(): dirs += [("calibracion", case.name, d) for d in sorted(r.iterdir()) if d.is_dir() and d.name not in ("rays", "jacobi")]
FIELDS = ["fuente", "caso", "clave", "n_rayos", "estado_checkpoint", "intentos", "paso", "t", "dt", "max_p", "max_v"]
n_int = 0
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader()
    for src, case, d in dirs:
        if want and case not in want: continue
        ms = sorted(d.glob("step_*.json"))
        if not ms: continue
        m = json.loads(ms[-1].read_text()); z = d / m["archive"]
        if hashlib.sha256(z.read_bytes()).hexdigest() != m["sha256"]:
            print("SHA no coincide, se omite:", z); continue
        with zipfile.ZipFile(z) as zf: b = Loader(io.BytesIO(zf.read("integration.pkl"))).load()
        ys = b["ys"]; ts = b["ts"]; ny = len(ys[0])
        if ny % 4: print("estado no es (2,nt,2), se omite:", d); continue
        nt = ny // 4
        if nt > a.max_rays or nt < 16: print(f"omite {case}/{d.name} nt={nt}"); continue
        for i in range(1, len(ts)):
            P = np.asarray(ys[i]).reshape(2, nt, 2)
            w.writerow(dict(fuente=src, caso=case, clave=d.name, n_rayos=nt, estado_checkpoint=m["status"], intentos=m.get("attempts"), paso=i,
                            t=float(ts[i]), dt=float(ts[i]) - float(ts[i - 1]), max_p=float(np.linalg.norm(P[0], axis=1).max()), max_v=float(np.linalg.norm(P[1], axis=1).max())))
        n_int += 1
        print(f"{src:11s} {case:18s} {d.name} nt={nt:6d} pasos={len(ts) - 1:4d} estado={m['status']}", flush=True)
print("integraciones:", n_int, "->", out)
