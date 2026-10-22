# NEM1 — Avance y reanudación

## Estado actual

COMPLETADO (run_v1 y run_v2_wine).
Documentos: README, DESIGN_FROZEN, mathematical_spec, sources, CONCLUSION, requirements, manifest.csv (hashes SHA-256).
Scripts: run.py (soporta --dataset synthetic|wine), verify.py.
Resultados: results/run_v1/ (sintético), results/run_v2_wine/ (dataset Wine de UCI).
Verificación: reproducción byte a byte OK en ambos.

## Resultados

### run_v1 — sintético (modelo lineal 4 features → 3 clases, 15 params, 20 entradas)
- Modos débiles de Fisher (tau=1e-6): 0
- Delta h máximo: 7.79e-02 en epsilon = 0.2
- Tendencia: delta_h crece aproximadamente linealmente con epsilon

### run_v2_wine — dataset Wine de UCI (13 features → 3 clases, 42 params, 178 entradas)
- Modos débiles de Fisher (tau=1e-6): 0
- Delta h máximo: 4.71e-02 en epsilon = 0.2
- Tendencia: delta_h crece aproximadamente linealmente con epsilon
- El autovalor mínimo de Fisher fue mayor que en sintético (menos cercanía al kernel)

## Historial

- 2026-10-21: Diseño congelado, documentos iniciales.
- 2026-10-21: Scripts run.py y verify.py (Python puro).
- 2026-10-21: Primera corrida run_v1 (sintético).
- 2026-10-21: Verificación byte a byte pasada.
- 2026-10-22: Reescritura de run.py con soporte --dataset (synthetic/wine), modelo lineal.
- 2026-10-22: Corrida run_v2_wine con dataset Wine de UCI.
- 2026-10-22: Verificación byte a byte pasada en ambos.
- 2026-10-22: manifest.csv con hashes SHA-256 de 13 archivos propios.
