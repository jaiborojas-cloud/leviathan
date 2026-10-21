"""leer_ensayo_t4p_j8.py - SOLO LECTURA. Lee la carpeta de trabajo del ensayo de T4' sobre split8_j8_true (D4, anexo E1 v1.1 congelado)
y aplica las compuertas de integridad declaradas ANTES de correr el ensayo (PREPARACION_ensayo_t4p_j8_2026-10-21.md).
No integra, no clasifica, no asigna Y, no modifica nada. Imprime cada compuerta como OK / FALLA / NO_APLICA y una lectura final.

Uso (PowerShell):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "<ruta>\\leer_ensayo_t4p_j8.py" --work "D:\\RIPG_DATA\\T2_A\\expediente\\ensayo_t4p_j8_D4_2026-10-21"
"""
import argparse, json, sys
from pathlib import Path

CASE = "split8_j8_true"
# Pausa original de la calibracion v1.0 (piloto, equipo del responsable, 2026-10-19): REVISION_PENDIENTE_split8_j8_true.json
ORIG_PAUSE_STEP, ORIG_PAUSE_T = 67, 0.07992408179528583
# Traza por paso del diagnostico de escape (contenedor, float64, nt=2048): piloto/diagnostico_escape/escape_split8_j8_true.csv
T56, T60 = 0.07894004938133196, 0.07948321944527635
TOL_PLATAFORMA = 1e-9      # diferencia contenedor/Windows observada en la traza: ~2e-11
N_STATE_CAL = 2048 * 4     # calibracion: 2048 rayos, estado [p, v] de 2 coordenadas


def ultimo_meta(dd):
    ms = sorted(Path(dd).glob("step_*.json"))
    return json.loads(ms[-1].read_text()) if ms else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    w = Path(ap.parse_args().work)
    res = []
    def g(nombre, ok, detalle=""):
        res.append((nombre, ok)); print(f"[{'OK' if ok is True else 'FALLA' if ok is False else 'NO_APLICA'}] {nombre}  {detalle}")

    regs = [p for p in (w / "VISITA_COMPLETA.json", w / "REVISION_PENDIENTE.json", w / "ERROR_EJECUCION.json") if p.exists()]
    if not regs:
        sys.exit("No hay registro final en la carpeta (la corrida no termino o la ruta es otra).")
    rec = json.loads(regs[0].read_text()); rv = rec.get("resultado_visita") or {}
    print(f"registro: {regs[0].name}  status={rec['status']}  reason={str(rec.get('reason'))[:120]}")
    print(f"pared {rec['wall_seconds_session']:.1f} s, CPU {rec['cpu_seconds_session']:.1f} s, entro_a_refinamiento={rec['caps'].get('entro_a_refinamiento')}")
    print(f"entorno: {rec['environment']}")

    g("0 caso = split8_j8_true", rec.get("case") == CASE, str(rec.get("case")))
    # 1. topes = los del anexo v1.1, sin presupuesto adicional
    c = rec["caps"]
    g("1 topes v1.1 sin extra-budget", rec["extra_budget"] is False and c["attempts"] == 250 and c["time_s"] == 120.0
      and c["visit_s"] == 900.0 and c.get("visit_s_refinamiento") == 3600.0, json.dumps(c))
    # 2. nada fuera del driver instrumentado
    g("2 sin_cubrir vacio", rec["sin_cubrir"] == [], f"{len(rec['sin_cubrir'])} llamadas")

    # 3. la calibracion v1.0 dentro de la visita reproduce la pausa original (identidad del estado + mismo camino numerico)
    cal = None
    rays_dir = w / "ode_checkpoints" / "rays"
    for dd in (sorted(rays_dir.iterdir()) if rays_dir.exists() else []):
        m = ultimo_meta(dd)
        if m and m["signature"]["t_span"] == [0.0, 0.09]:
            cal = m
    if cal is None:
        g("3 pausa v1.0 reproduce la original", False, "no se encontro la integracion de calibracion v1.0 (t_span [0, 0.09])")
    else:
        dt = abs(cal["t"] - ORIG_PAUSE_T)
        g("3 pausa v1.0 reproduce la original", cal["steps"] == ORIG_PAUSE_STEP and cal["last_reason"] == "PAUSED_LOW_RADIAL_PROGRESS"
          and cal["alarm_count"] == 8 and dt <= TOL_PLATAFORMA,
          f"paso {cal['steps']} t={cal['t']!r} (original {ORIG_PAUSE_T!r}, dif {dt:.2e}) razon={cal['last_reason']} alarma={cal['alarm_count']}")
        if dt != 0.0:
            print("     nota: dif != 0 en el mismo equipo indicaria otro estado u otra plataforma; revisar antes de leer la geometria")
    g("3b la visita registra la pausa v1.0 y el modo T4'", rv.get("calibration_v10_pause") == "PAUSED_LOW_RADIAL_PROGRESS"
      and rv.get("calibration_mode") == "T4_PRIME_AREA_STOP" if rv else None,
      f"calibration_v10_pause={rv.get('calibration_v10_pause')} calibration_mode={rv.get('calibration_mode')}")

    # 4. T4': parada por area en el paso 60 (primer CHECK con A >= 0.02), radio en (t56, t60]
    nom_p = w / "states" / CASE / "nominal.json"
    if nom_p.exists():
        nom = json.loads(nom_p.read_text())
        r = nom["radius"]
        g("4a T4' se detiene en el paso 60", nom.get("steps") == 60 and abs(nom["t_reached"] - T60) <= TOL_PLATAFORMA,
          f"pasos={nom.get('steps')} t_reached={nom.get('t_reached')!r} area_en_t_reached={nom.get('area_at_t_reached')}")
        g("4b radio nominal en (t56, t60]", T56 - TOL_PLATAFORMA < r <= T60 + TOL_PLATAFORMA, f"radio={r!r}")
        g("4c area del radio = 0.02 (|err rel| <= 1e-6)", abs(nom["area_relative_error"]) <= 1e-6, f"err rel={nom['area_relative_error']:.2e}")
        print(f"     (registro, sin criterio) polygon_valid={nom.get('polygon_valid')} polygon_simple={nom.get('polygon_simple')} "
              f"intentos={nom.get('attempts')} rechazos={nom.get('rejected')} {nom.get('seconds', 0):.1f} s")
    else:
        g("4 nominal.json de T4'", False, "no existe: T4' no termino (ver status y reason)")

    # 5. auditorias
    if rec["status"] == "VISIT_EVALUATED":
        g("5a sin errores en result", "errors_en_result" not in rv, str(rv.get("errors_en_result", ""))[:200])
        g("5b sin pausas fuera de T4'", rec["instrumentacion"]["pausadas"] == [] or
          all(k.startswith("rays/") and ultimo_meta(w / "ode_checkpoints" / k)["signature"]["t_span"] == [0.0, 0.09]
              for k in rec["instrumentacion"]["pausadas"]), f"pausadas={rec['instrumentacion']['pausadas']}")
        rs = w / "states" / CASE / "result.json"
        top = json.loads(rs.read_text()) if rs.exists() else {}
        cl = rv.get("classification")
        print("\nRESULTADO DEL INSTRUMENTO (lectura en PREPARACION, seccion 4; no asigna Y):")
        for k in ("classification", "nominal_radius", "r_conj", "A_embed"):
            print(f"   {k} = {rv.get(k)!r}")
        for k in ("level", "max_boundary_resolution", "first_self_intersection", "minimum_resolution_with_event", "phase_persistence",
                  "determinant_sign_change", "max_Dexp_condition", "min_abs_det_Dexp", "min_signed_det_Dexp", "cut_locus_probable",
                  "metric_min_eigenvalue", "metric_nonpositive", "metric_nonfinite", "notes"):
            if k in top:
                print(f"   {k} = {top[k]!r}")
        if cl == "GEOMETRIC_NONINJECTIVITY" and rv.get("r_conj") is not None:
            g("5c r_conj < radio nominal", rv["r_conj"] < rv["nominal_radius"], "")
        g("5d metrica SPD y finita en las auditorias", top.get("metric_nonpositive", 0) == 0 and top.get("metric_nonfinite", 0) == 0 if top else None, "")
    else:
        ul = rec.get("ultima_integracion_lanzada")
        print(f"\nSin clasificacion. Ultima integracion lanzada: {ul}")
        print("Lectura: pausa operacional / error de ejecucion; j8 sigue PAUSED_PENDING_REVIEW. Ver PREPARACION, seccion 4.")

    fallas = [n for n, ok in res if ok is False]
    print("\nCOMPUERTAS DE INTEGRIDAD:", "TODAS OK" if not fallas else f"FALLAN {fallas} -> no leer la geometria hasta revisar")


if __name__ == "__main__":
    main()
