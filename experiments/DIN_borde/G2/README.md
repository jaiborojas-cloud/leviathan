# DIN-G2 · resolución variable del ejemplo difícil

Exploratorio. Seis mezclas gaussianas de tres clases,20 splits×5 inicios
por nivel,600 entrenamientos y4200 visitas previstas. Sin Wine, Iris,
datos T2 ni DIN-C1. No cambia instrumentos ni etapas previas.

- [Diseño congelado](DESIGN_FROZEN.md), [configuración](config.json).
- [Fuentes/SHA](freeze_manifest.csv), [registro de lectura](progress.md).

Primario: rho_caras de I2 r3; secundario rho_vert. Se pregunta si D de C1
es mayor donde la clasificación final del dominante varía entre inicios
del mismo split. No implica causalidad ni transferencia.
