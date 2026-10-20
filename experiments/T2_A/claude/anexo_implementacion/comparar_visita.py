"""comparar_visita.py - compara dos result.json de una visita (p. ej. el del piloto vs el reproducido con el candidato v11). Solo lee. Uso:
  python -I comparar_visita.py <obtenido\\result.json> <referencia\\result.json>
Campos comparados: clasificacion, radios, areas, conteos y banderas (no tiempos ni rutas). Igualdad exacta en discretos; relativa 1e-9 en
cantidades de Jacobi/metrica/areas; 1e-12 absoluta en radios (diferencia plataforma conocida 6.5e-15; xtol de brentq 1e-13).
Termina con RESULTADO GLOBAL: PASS/FAIL."""
import json, sys
new = json.load(open(sys.argv[1], encoding="utf-8")); ref = json.load(open(sys.argv[2], encoding="utf-8"))
SKIP = {"checkpoint", "checkpoint_sha256", "task_cpu_seconds", "task_seconds_sum", "new_wall_seconds", "new_cpu_seconds", "errors", "notes", "state"}
RADII = {"nominal_radius", "r_inj_upper", "r_inj_lower", "first_self_intersection", "r_conj"}
ok = True
for k, v in ref.items():
    if k in SKIP or isinstance(v, (dict, list)):
        continue
    x = new.get(k)
    if isinstance(v, float) and not isinstance(v, bool):
        tol = 1e-12 if k in RADII else 1e-9 * max(abs(v), 1e-300)
        if k in ("r_conj_min_estimate_range", "area_32_64_relative_difference"):
            tol = 1e-12   # diferencias de ruido numerico: tolerancia absoluta
        good = isinstance(x, (int, float)) and abs(x - v) <= tol
    else:
        good = x == v
    ok &= good; print(("PASS " if good else "FAIL ") + f"{k}: referencia={v!r} obtenido={x!r}")
print("errores (obtenido):", repr(new.get("errors", ""))[:200])
print("RESULTADO GLOBAL:", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
