"""comparar_visita_j6.py - compara el result.json producido por visita_completa_instrumentada.py (j6/update25) con el
registro de la corrida original (entrega de solo lectura). Solo lee. Uso:
  python -I comparar_visita_j6.py <work>\\states\\split8_j6_true\\result.json
Tolerancias: igualdad exacta en campos discretos; relativa 1e-9 en cantidades de Jacobi/metrica; 1e-12 absoluta en el radio
nominal (diferencia plataforma/version conocida 6.5e-15; xtol de brentq 1e-13). Termina con RESULTADO GLOBAL: PASS/FAIL."""
import json, sys
r = json.load(open(sys.argv[1], encoding="utf-8"))
REG = dict(classification="INJECTIVE_AT_NOMINAL_RADIUS", nominal_radius=0.07883553716312919, A_embed=0.020000000000000007,
           max_Dexp_condition=1.156426741290947, min_abs_det_Dexp=0.8832672934858652, min_signed_det_Dexp=0.8832672934858652,
           metric_min_eigenvalue=0.0005568520646096764, max_boundary_resolution=1024, self_intersections=0,
           first_self_intersection=None, r_conj=None, metric_nonpositive=0, metric_nonfinite=0, determinant_sign_change=False,
           cut_locus_probable=False)
ok = True
for k, v in REG.items():
    x = r.get(k)
    if isinstance(v, float):
        tol = 1e-12 if k == "nominal_radius" else 1e-9 * max(abs(v), 1e-300)
        good = x is not None and abs(x - v) <= tol
    else:
        good = x == v
    ok &= good; print(("PASS " if good else "FAIL ") + f"{k}: registrado={v!r} obtenido={x!r}")
print("RESULTADO GLOBAL:", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
