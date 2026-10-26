# DIN-Q13 v2 — tamaño autorizado y ejecución externa

El responsable confirmó: «Confirmo N=800 (12 000 trayectorias). La cohorte se
ejecutará en el equipo del responsable […] 12 procesos, no en tu entorno».
Se levanta la pausa registrada en potencia_v2/RESULTADO_v1.md. Sus archivos
históricos y verification_v2.json no se reescriben.

Se publica primero q13_plan.json con 800 splits, brazos A0/LS/WD y dosis mínimas
LS=.005/WD=.2, más su SHA. Sólo después se publica el script portable. Semillas
de cohorte: split711000+s, init721000+5s+k, lote731000+5s+k, pareadas entre brazos.
No se entrena ninguna trayectoria de cohorte en el entorno del agente.

La compuerta y la prueba corta de 15 trayectorias se dejan como comandos para
el equipo Windows del responsable. La prueba corta pertenece al universo fijo:
se conserva y se reutiliza al reanudar; no se sustituye si falla.
