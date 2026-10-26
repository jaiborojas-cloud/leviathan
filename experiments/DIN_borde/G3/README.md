# DIN-G3 · potencia y señal temprana en régimen de colapso

Exploratorio. Tres mezclas gaussianas nuevas (s=.25,.5,.8), mismos instrumentos
y protocolo G2, semillas nuevas. El tamaño≥100 splits×5 por nivel se elige
antes de entrenar mediante simulación C1 exacta con el piloto G2.

- [Diseño congelado y regla de tamaño](DESIGN_FROZEN.md).
- [Configuración del diseño](config_design.json), [fuentes/SHA](freeze_manifest.csv).
- [Origen del piloto/código G2](sources/G2_manifest.json), [registro](progress.md).

La selección de niveles es posterior a G2. Ni datos ni estados G2 se incorporan
a la cohorte nueva. No usa Wine, Iris, datos T2 ni cohorte C1. No cambia sus
estados. rho_caras primario, rho_vert secundario; V_cont es la variancia
intra-split de la confianza continua final, no sólo la clasificación binaria.
