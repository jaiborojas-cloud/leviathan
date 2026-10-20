"""calibrar_piloto.py - calibracion del radio nominal (instrumentada) de las visitas del piloto, una tras otra.

EXPLORATORIO/OPERATIVO. No clasifica, no asigna Y, NUNCA usa --extra-budget (eso solo lo autoriza el responsable, caso por caso).
Para cada fila PASS de estados_u25/regeneracion_u25.csv ejecuta sesion_visita_instrumentada.py en un proceso aparte
(aislado: un fallo no detiene el lote) con carpeta de trabajo propia en --work-root/<trajectory>. Reanuda por si sola:
una trayectoria con SESION_COMPLETA.json se omite; una con REVISION_PENDIENTE.json se omite y se lista (requiere revision
segun el anexo 3.3; este script no reanuda pausas). Escribe calibracion_piloto.csv (resumen) y calibracion_piloto.log.
Se puede detener con Ctrl+C: lo ya hecho queda en disco.

Ejecucion (PowerShell; del orden de 30 s por visita sana):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "D:\\RIPG_DATA\\T2_A\\expediente\\anexo_implementacion\\calibrar_piloto.py"
"""
import argparse, csv, json, subprocess, sys, time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--states", default=r"D:\RIPG_DATA\T2_A\expediente\estados_u25")
ap.add_argument("--work-root", default=r"D:\RIPG_DATA\T2_A\expediente\piloto_calibracion")
ap.add_argument("--sesion", default=str(Path(__file__).resolve().parent / "sesion_visita_instrumentada.py"))
a = ap.parse_args()
S, W = Path(a.states), Path(a.work_root); W.mkdir(parents=True, exist_ok=True)
log = open(W / "calibracion_piloto.log", "a", encoding="utf-8")
def say(*p):
    s = " ".join(str(x) for x in p); print(s, flush=True); log.write(s + "\n"); log.flush()

rows = [r for r in csv.DictReader(open(S / "regeneracion_u25.csv", encoding="utf-8"))]
say(f"== {time.strftime('%Y-%m-%d %H:%M:%S')}  {len(rows)} trayectorias en el CSV de regeneracion")
summary = []
try:
    for r in rows:
        tid = r["trajectory"]; wd = W / tid
        rec = dict(trajectory=tid, gate_prefijo=r["gate"], estado="", razon="", intentos="", rechazos="", alarma="", radio="", segundos="")
        if r["gate"] != "PASS":
            rec["estado"] = "SIN_ESTADO_GATE_FALLO"; summary.append(rec); say(f"{tid}: {rec['estado']}"); continue
        for fname in ("SESION_COMPLETA.json", "REVISION_PENDIENTE.json"):
            if (wd / fname).exists():
                d = json.loads((wd / fname).read_text()); rec["estado"] = d["status"] + " (ya existente)"; break
        else:
            d = None
        if d is None:
            t0 = time.time()
            p = subprocess.run([sys.executable, "-I", a.sesion, "--case", tid, "--state", str(S / r["state_file"]), "--work", str(wd)],
                               capture_output=True, text=True)
            rec["segundos"] = f"{time.time() - t0:.1f}"
            for fname in ("SESION_COMPLETA.json", "REVISION_PENDIENTE.json"):
                if (wd / fname).exists():
                    d = json.loads((wd / fname).read_text()); rec["estado"] = d["status"]; break
            if d is None:
                rec["estado"] = "ERROR_DE_PROCESO"; rec["razon"] = (p.stderr or p.stdout)[-300:].replace("\n", " | ")
        if d:
            rec["razon"] = rec["razon"] or (d.get("reason") or "")
            lc = d.get("last_checkpoint", {})
            rec["intentos"], rec["rechazos"], rec["alarma"] = lc.get("attempts", ""), lc.get("rejected", ""), lc.get("alarm_count", "")
            rec["radio"] = d.get("radius", "")
        summary.append(rec)
        say(f"{tid}: {rec['estado']}  {rec['razon']}  intentos={rec['intentos']} rechazos={rec['rechazos']} radio={rec['radio']} {rec['segundos']} s")
except KeyboardInterrupt:
    say("INTERRUMPIDO con Ctrl+C; lo ya hecho queda en disco.")
finally:
    if summary:
        with open(W / "calibracion_piloto.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(summary[0])); w.writeheader(); w.writerows(summary)
    comp = sum(s["estado"].startswith("CALIBRATION_COMPLETE") for s in summary)
    pausa = sum(s["estado"].startswith("PAUSED") for s in summary)
    say(f"RESUMEN: {comp} calibraciones completas, {pausa} en PAUSED_PENDING_REVIEW, {len(summary) - comp - pausa} otras, de {len(summary)} procesadas.")
    say("Sin clasificacion ni outcomes. Las pausas requieren revision (anexo 3.3); este script no las reanuda.")
    log.close()
