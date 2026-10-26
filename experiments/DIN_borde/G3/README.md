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

## Tamaño y análisis congelados

[SAMPLE_FROZEN](SAMPLE_FROZEN.md) selecciona **100 splits×5 inicios por nivel**:
1500 entrenamientos y10500 visitas. Potencias simuladas para D_obj=.026:
.905/.8925/.890; límites inferiores Wilson95%≥.8555. También se simulan
.015/.020 y el nulo,400 réplicas/nivel/efecto con1999 permutaciones.
La potencia es condicional al modelo Gaussiano y soporte piloto, no universal.

Diseño7bce1dc → código potencia3f01bc7 → potencia → tamaño1e88d2b → código
cohorte2048dd4 → controles y datos nuevos. [Diff G2/G3](COHORT_IMPLEMENTATION.md).
La primaria C1 exacta usa base cúbica, centrado intra-split, diez bloques y
1999 permutaciones. PASS_DESCRIPTIVO requiere p<.05,D>0,beta positiva;
colapso operacional exige mediana c250≥.8 y mediana q250≤.05. Se reportan
todos los individuos, sin filtrar colapso para cambiar el resultado.

V_cont media varianzas de los cinco R250 por split; V_bin es secundario.
Sólo tres niveles: la tendencia D–V_cont es descriptiva. D7,rho_vert yW_adj
legado no rescatan NOT_MET ni establecen información condicional general.

## Reproducción por fases

Fuentes core/geometry/I2 r3/C1 intactas porSHA; no se invoca load_split/load_wine.
La guarda bloquea datos ajenos. El piloto en sources/G2/results sólo se
permite al script de potencia, no al de cohorte.

En una copia independiente y entorno limpio, el commit64fcc7d contiene
la planificación y los ejecutores antes de archivar la cohorte. Con sus
paquetes y desde la raíz:

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python experiments/DIN_borde/G3/scripts/run_v1.py --part prepare
python experiments/DIN_borde/G3/scripts/run_v1.py --part cohort
python experiments/DIN_borde/G3/scripts/verify_v1.py --part reconstruct
python experiments/DIN_borde/G3/scripts/analysis_v1.py
python experiments/DIN_borde/G3/scripts/verify_v1.py --part final
python experiments/DIN_borde/G3/scripts/plot_v1.py
python experiments/DIN_borde/G3/scripts/report_v1.py
python experiments/DIN_borde/G3/scripts/archive_v1.py --part pack
```

Para repetir potencia, partir del commit3f01bc7 anterior a sus salidas y
usar scripts/power_v1.py. Ningún ejecutor sobrescribe: no repetir sobre
salidas archivadas. Presupuesto43200s,dos procesos,BLAS/Torch1, y los
presupuestos por estado predeterminados de I2 r3. Sin extensión por outcome.

Matrices/scores/pesos/Adam/RNG/rho completos fuera de Git en
`/workspace/work/din-g3-v1-arrays`; simulaciones en din-g3-power-v1-arrays.
Los10500 metadatos originales se preservan y versionan en shardsJSONL
reversibles conSHA. La cohorte se genera desde semillas, sin datasets externos.
