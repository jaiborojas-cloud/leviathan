# DIN-CIFAR F1 — ejecución del productor (Windows, PowerShell)

Requisitos:
- **Fusionados el PR #127** (diseño congelado) **y el PR del productor.**
- El clon `D:\leviathan-q13` con `core.autocrlf=false`.
- El venv `D:\RIPG_DATA\venv_q13` con las versiones fijadas en el plan.
- El CIFAR oficial y la compuerta oficial de F0, que se reutilizan.

```powershell
cd D:\leviathan-q13
git checkout main
git pull
New-Item -ItemType Directory -Force D:\RIPG_DATA\DIN_CIFAR_F1 | Out-Null
D:\RIPG_DATA\venv_q13\Scripts\python.exe experiments\DIN_borde\CIFAR\F1\productor_F1.py --cifar D:\RIPG_DATA\cifar-10-python.tar.gz --compuerta D:\RIPG_DATA\DIN_CIFAR_F0\compuerta.json --salida D:\RIPG_DATA\DIN_CIFAR_F1\corrida --procesos 12
```

**Antes de entrenar,** el productor verifica:
- el plan congelado por su SHA (`4347857e…`), su estado CONGELADO y que coincidan universo, semillas, lr, opciones de ρ, watchdog y MD5 del dataset;
- los SHA de todas las fuentes del plan (core, geometry, rho, C1, instrumento, sistema y compuerta);
- las versiones;
- la compuerta oficial (9 checks, PASA, error ≤ 1e-12, fuentes y versiones).

Si algo no coincide, se detiene sin entrenar.

**Duración estimada:** unos 30–40 minutos con 12 procesos. Por trayectoria son unos 36 s de entrenamiento y geometría (como en F0b), más 2 llamadas a ρ en proceso aparte. La memoria ronda los 9 GB.

**Reanudable:** si se corta, se repite el mismo comando. Las trayectorias con registro se conservan. Una trayectoria a medias se mueve a `interrumpidas\` (no se borra) y se rehace desde cero.

**Salida** (en `D:\RIPG_DATA\DIN_CIFAR_F1\corrida\`):
- `cifar_f1_visitas.csv`: 2000 filas, según el esquema v2;
- `RESUMEN_F1.json`;
- `trayectorias\<id>\`: registro, pesos, M, espectro, logits y resultado ρ completo por visita;
- `splits\`: índices, f y cargas PCA.

En total, unos 550 MB, fuera de Git.

**Qué devolver:** lo que imprime la consola al final. Incluye los estados por visita y los SHA de la tabla, el productor, el dataset y la compuerta. Con esos SHA se arma el comando exacto del analista congelado (`analisis_F1_v2.py`, con el plan congelado y `--plan-sha 4347857e83fba828fda5910ffc9fd10feff8f4c14d37c27ac40e935b28ef34ae`).
