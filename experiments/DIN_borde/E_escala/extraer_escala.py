"""extraer_escala.py - DIN-E-escala: medidas de escala de logits en u250 por trayectoria (solo lectura de u250_state.npz).
No lee X, rho ni D. Escribe una tabla NUEVA (creacion exclusiva) junto a la cohorte.
Uso: python -I extraer_escala.py --cohorte <carpeta de la cohorte, p.ej. D:\\RIPG_DATA\\DIN_Q13M2_v2>
Salida: <cohorte>\\escala_u250.csv con columnas trajectory, S, m, p, n_panel, error
  S = media sobre el panel de la desviacion estandar (ddof=0) de los 3 logits de cada ejemplo
  m = media sobre el panel de z_y - max_{c != y} z_c
  p = media sobre el panel de la probabilidad softmax maxima
"""
import argparse, csv, hashlib, sys
from pathlib import Path
import numpy as np


def medidas(z, y):
    z = np.asarray(z, float); y = np.asarray(y, int)
    S = float(np.mean(z.std(axis=1)))
    otros = z.copy(); otros[np.arange(len(y)), y] = -np.inf
    m = float(np.mean(z[np.arange(len(y)), y] - otros.max(axis=1)))
    e = np.exp(z - z.max(axis=1, keepdims=True)); p = float(np.mean((e / e.sum(axis=1, keepdims=True)).max(axis=1)))
    return S, m, p


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cohorte", required=True); a = ap.parse_args()
    raiz = Path(a.cohorte); arr = raiz / "arrays"; salida = raiz / "escala_u250.csv"
    if not arr.is_dir(): sys.exit(f"ABORTA: no existe {arr}")
    if salida.exists(): sys.exit(f"ABORTA: {salida} ya existe; no se sobrescribe")
    ids = sorted(d.name for d in arr.iterdir() if d.is_dir())
    filas = []; errores = 0
    for i, t in enumerate(ids):
        f = arr / t / "u250_state.npz"
        try:
            with np.load(f, allow_pickle=False) as z:
                S, m, p = medidas(z["logits"], z["labels"]); n = int(z["logits"].shape[0])
            filas.append(dict(trajectory=t, S=repr(S), m=repr(m), p=repr(p), n_panel=n, error=""))
        except Exception as e:
            errores += 1; filas.append(dict(trajectory=t, S="", m="", p="", n_panel="", error=f"{type(e).__name__}: {e}"))
        if (i + 1) % 2000 == 0: print(f"[{i + 1}/{len(ids)}]", flush=True)
    with open(salida, "x", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["trajectory", "S", "m", "p", "n_panel", "error"], lineterminator="\n"); w.writeheader(); w.writerows(filas)
    print(dict(trayectorias=len(ids), errores=errores, salida=str(salida), sha256=hashlib.sha256(salida.read_bytes()).hexdigest(),
               script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))


if __name__ == "__main__":
    main()
