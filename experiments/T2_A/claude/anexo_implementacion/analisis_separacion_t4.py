"""analisis_separacion_t4.py - SOLO LECTURA. Mide, con las trazas existentes, cuanto se separan los casos con escape (j5, j7, j8) de los demas en la
aceleracion de max|v| (F10 = max|v|_n / max|v|_{n-10}) dentro del regimen de |p| alto. No mira X ni resultados; no fija umbrales (ver el informe).
  python -I analisis_separacion_t4.py <trazas_rays.csv> <escape_j5.csv> <mpfr_j7.csv> <mpfr_j8.csv>"""
import csv, sys
import numpy as np
def ser(rows, kv='max_v', kp='max_p'):
    return np.array([float(x['t']) for x in rows]), np.array([float(x[kp]) for x in rows]), np.array([float(x[kv]) for x in rows])
R = list(csv.DictReader(open(sys.argv[1])))
j9 = ser([r for r in R if r['caso'] == 'split8_j9_true' and r['fuente'] == 'calibracion'])
others = {}
for r in R:
    if r['caso'] not in ('split8_j5_true', 'split8_j7_true', 'split8_j8_true'):
        others.setdefault((r['fuente'], r['caso'], r['clave']), []).append(r)
pos = {'j5': ser(list(csv.DictReader(open(sys.argv[2])))), 'j7': ser(list(csv.DictReader(open(sys.argv[3])))), 'j8': ser(list(csv.DictReader(open(sys.argv[4]))))}
print(f"integraciones de rayos en los demas casos: {len(others)}; max|p| global fuera de j9 (calibracion a 0.09): "
      f"{max(float(r['max_p']) for k, v in others.items() if not (k[1] == 'split8_j9_true' and k[0] == 'calibracion') for r in v):.2f}; "
      f"max|p| de j9 calibracion: {j9[1].max():.2f}")
w = 10
for P0 in (10, 20, 40):
    for n, s in [('j9', j9), ('j5', pos['j5']), ('j7', pos['j7']), ('j8', pos['j8'])]:
        t, p, v = s; F = np.full(len(v), np.nan); F[w:] = v[w:] / v[:-w]
        idx = np.where(p >= P0)[0]; idx = idx[idx >= w]
        print(f"{n} |p|>={P0:3d}: pasos={len(idx):3d}  F10 max={np.nanmax(F[idx]):.3f}  F10 en el primer paso={F[idx[0]]:.3f}")
    print()
