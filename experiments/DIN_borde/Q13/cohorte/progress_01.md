# DIN-Q13 — cronología y detención

Base main df75f66 (PR #96 fusionado). Diseño original SHA 81d8ad9e… verificado.
8dce698 registra procedimiento y fuentes; 5c82382 implementa receta/calibración.
Ambos commits fueron publicados en research/din-q13-cohorte antes de iniciar las
mediciones. PR #97 creado en borrador antes de medir. No hubo fallos de código,
enmiendas ni sustituciones de trayectorias.

La calibración prevista terminó: 9 condiciones × 20 splits × 5 = 900. Ninguna
dosis cumple c en [.55,.70]. LS y WD se descartan; se aplica la parada obligatoria
INCONCLUSIVE_MANIPULACION. Publicar los resultados con sus hashes es el último
paso autorizado aplicable. No se ejecuta la potencia ni se produce un plan/cohorte.

No se abrió ningún dato de cohorte C2. No se calcularon X, rho o asociaciones en
calibración; el script de análisis Q13 no se ejecutó. Se leyó únicamente su código
para una eventual simulación que no se hizo. Archivos de otras etapas y todos los
congelados permanecen idénticos. Pesos, M y f se conservan fuera de Git con SHA.
