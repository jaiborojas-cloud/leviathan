"""visitas_piloto.py - corre la visita completa instrumentada de las visitas del piloto, una tras otra, en procesos aparte.

OPERATIVO. NO usa --extra-budget (solo el responsable lo autoriza, caso por caso). OMITE por defecto las visitas con decision
registrada «mantener pausado» (split8_j5, j7, j8) y split8_j9 (se reanuda aparte con --extra-budget, decision registrada).
Reanuda por si solo: una visita con VISITA_COMPLETA.json se omite; con REVISION_PENDIENTE.json se omite y se lista (requiere
revision, anexo 3.3). Escribe visitas_piloto.csv y visitas_piloto.log en --work-root. Ctrl+C conserva lo hecho.
Los resultados son diagnosticos geometricos del piloto operativo: NO asignan Y, NO establecen el veredicto predictivo.

Ejecucion (PowerShell; del orden de 1 minuto por visita sana, mas si hay candidatas con muchos rayos):
  & "D:\\RIPG_DATA\\T2_A\\cribado_borde\\venv_torch\\Scripts\\python.exe" -I "D:\\RIPG_DATA\\T2_A\\expediente\\anexo_implementacion\\visitas_piloto.py"
"""
import argparse, csv, json, subprocess, sys, time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--list", default=r"D:\RIPG_DATA\T2_A\expediente\estados_u25\regeneracion_u25.csv")
ap.add_argument("--work-root", default=r"D:\RIPG_DATA\T2_A\expediente\piloto_visitas")
ap.add_argument("--visita", default=str(Path(__file__).resolve().parent / "visita_completa_instrumentada.py"))
ap.add_argument("--omit", nargs="*", default=["split8_j5_true", "split8_j7_true", "split8_j8_true", "split8_j9_true"])
a = ap.parse_args()
W = Path(a.work_root); W.mkdir(parents=True, exist_ok=True)
log = open(W / "visitas_piloto.log", "a", encoding="utf-8")
def say(*p):
    s = " ".join(str(x) for x in p); print(s, flush=True); log.write(s + "\n"); log.flush()
rows = list(csv.DictReader(open(a.list, encoding="utf-8")))
say(f"== {time.strftime('%Y-%m-%d %H:%M:%S')}  {len(rows)} trayectorias; omitidas por decision: {a.omit}")
summary = []
try:
    for r in rows:
        tid = r["trajectory"]; wd = W / tid
        rec = dict(trajectory=tid, estado="", razon="", clasificacion="", radio="", r_conj="", A_embed="", intentos="", alarma_max="", sin_cubrir="", segundos="")
        if tid in a.omit:
            rec["estado"] = "OMITIDA_POR_DECISION"; summary.append(rec); say(f"{tid}: {rec['estado']}"); continue
        if r["gate"] != "PASS":
            rec["estado"] = "SIN_ESTADO_GATE_FALLO"; summary.append(rec); say(f"{tid}: {rec['estado']}"); continue
        d = None
        for fname in ("VISITA_COMPLETA.json", "REVISION_PENDIENTE.json", "ERROR_EJECUCION.json"):
            if (wd / fname).exists():
                d = json.loads((wd / fname).read_text()); rec["estado"] = d["status"] + " (ya existente)"; break
        if d is None:
            t0 = time.time()
            p = subprocess.run([sys.executable, "-I", a.visita, "--case", tid, "--work", str(wd)], capture_output=True, text=True)
            rec["segundos"] = f"{time.time() - t0:.1f}"
            for fname in ("VISITA_COMPLETA.json", "REVISION_PENDIENTE.json", "ERROR_EJECUCION.json"):
                if (wd / fname).exists():
                    d = json.loads((wd / fname).read_text()); rec["estado"] = d["status"]; break
            if d is None:
                rec["estado"] = "ERROR_DE_PROCESO"; rec["razon"] = (p.stderr or p.stdout)[-300:].replace("\n", " | ")
        if d:
            rv = d.get("resultado_visita") or {}; ins = d.get("instrumentacion", {})
            rec.update(razon=rec["razon"] or (d.get("reason") or ""), clasificacion=rv.get("classification", ""), radio=rv.get("nominal_radius", ""),
                       r_conj=rv.get("r_conj", ""), A_embed=rv.get("A_embed", ""), intentos=ins.get("intentos_total", ""),
                       alarma_max=ins.get("max_alarma", ""), sin_cubrir=len(d.get("sin_cubrir", [])))
        summary.append(rec)
        say(f"{tid}: {rec['estado']}  {rec['clasificacion']}  {rec['razon'][:80]}  intentos={rec['intentos']} alarma={rec['alarma_max']} sin_cubrir={rec['sin_cubrir']} {rec['segundos']} s")
except KeyboardInterrupt:
    say("INTERRUMPIDO con Ctrl+C; lo ya hecho queda en disco.")
finally:
    if summary:
        with open(W / "visitas_piloto.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(summary[0])); w.writeheader(); w.writerows(summary)
    n = lambda pref: sum(s["estado"].startswith(pref) for s in summary)
    say(f"RESUMEN: {n('VISIT_EVALUATED')} evaluadas, {n('PAUSED')} en PAUSED_PENDING_REVIEW, {n('OMITIDA')} omitidas, {n('ERROR')} con error, de {len(summary)}.")
    say("Sin Y y sin veredicto predictivo. Las pausas requieren revision (anexo 3.3); este script no las reanuda.")
    log.close()
