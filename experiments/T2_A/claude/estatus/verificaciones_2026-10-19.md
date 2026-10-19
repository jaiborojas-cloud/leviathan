# Verificaciones de solo lectura — 2026-10-19

Salida de la terminal del usuario (Windows) o de comandos repetibles; exploratorio, sin outcomes.

- `state.npz` de la otra corrida (`6713246b…e19c`) vs `state_025_regen.npz` (`845c2251…4776`), j5 update 25: `f` idéntico bit a bit; `M` max|diff| = 1.325828336007362e-12.
- `sources/geometry.py` y `sources/instrument/geometry.py` de la compacta: ambos `b4d1e0e4…bdf3`.
- j6, prefijo de 5 updates (`scripts/dtheta_j6.py`, SHA `56ecda89…de00`): max|Δθ| = 7.077671781985373e-16 (umbral A0 1e-12: PASS); max|ΔM| = 2.1103119252074976e-11; max|Δf| = 0.0.
- Compacta: 35 archivos fuera de `compact_manifest.json`; 31 elementos ajenos movidos a `_ajenos_a_la_compacta\` (lista con hashes antes de mover: 480 archivos). Tras mover, 0 fallos en las 23963 entradas del manifiesto ni en los 800 `checkpoint_005.pt` (misma lógica que `verificar.py`, en dos tramos). `verificar.py` formal en Windows: pendiente.
