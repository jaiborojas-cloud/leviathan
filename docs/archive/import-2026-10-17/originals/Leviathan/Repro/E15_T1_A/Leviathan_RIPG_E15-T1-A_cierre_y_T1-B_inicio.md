# Leviathan / RIPG — E15-T1-A: cierre y decisión sobre T1-B

**T1-A: mapa observacional completo de 80/80 estados. E15-C1-A permanece INCONCLUSIVE.**

No se reentrenó, sustituyó ni excluyó ningún estado. No se redujo el área C1, ni se usaron supervivientes para confirmación. Los diez estados A2 se reutilizan como evidencia verificada;70 estados reciben screening nuevo. La ausencia de pérdida bajo pruebas finitas no es una demostración global de inyectividad.

## Conteos poblacionales

| Clasificación | true (40) | random (40) |
|---|---:|---:|
| Sin pérdida observada al radio nominal | 38 | 40 |
| No inyectividad geométrica | 2 | 0 |
| Inconcluso | 0 | 0 |
| Anomalía atribuida al discretizado | 0 | 0 |

Prevalencia descriptiva observada: true 2/40 (5.0%); random 0/40 (0.0%). Sin intervalos confirmatorios ni pruebas causales.

## Distribución jerárquica

| Split | true positivos /5 | random positivos /5 |
|---|---:|---:|
| 0 | 2 | 0 |
| 1 | 0 | 0 |
| 2 | 0 | 0 |
| 3 | 0 | 0 |
| 4 | 0 | 0 |
| 5 | 0 | 0 |
| 6 | 0 | 0 |
| 7 | 0 | 0 |

| Inicialización | true positivos /8 | random positivos /8 |
|---|---:|---:|
| 0 | 0 | 0 |
| 1 | 1 | 0 |
| 2 | 0 | 0 |
| 3 | 1 | 0 |
| 4 | 0 | 0 |

Los splits conservan su estructura jerárquica, pero comparten ejemplos Wine: no son ocho datasets independientes. Una diferencia entre inicializaciones dentro de un split no demuestra un efecto fuerte y generalizable de inicialización.

## Radios, área y censura

| Estado positivo | R nominal | Primer conjugado estimado | Cota superior numérica r_inj | A_embed estimada | A_embed/0.02 |
|---|---:|---:|---:|---:|---:|
| split0_j1_true | 0.08852874528 | 0.07596208350 | 0.07596208350 | 0.01542077684 | 0.771038842 |
| split0_j3_true | 0.08400036772 | 0.07637387649 | 0.07637387649 | 0.01694300409 | 0.847150204 |

**true:** 38 áreas censuradas al nivel nominal; 0 no resueltas.

| Variable entre eventos detectados | n | Mínimo | Mediana | Máximo |
|---|---:|---:|---:|---:|
| r_conj_detected | 2 | 0.075962083503 | 0.076167979995 | 0.076373876487 |
| r_inj_numerical_upper | 2 | 0.075962083503 | 0.076167979995 | 0.076373876487 |
| A_embed_event_estimates | 2 | 0.015420776835 | 0.01618189046 | 0.016943004085 |
| A_embed_ratio_event_estimates | 2 | 0.77103884176 | 0.80909452301 | 0.84715020426 |

**random:** 40 áreas censuradas al nivel nominal; 0 no resueltas.

| Variable entre eventos detectados | n | Mínimo | Mediana | Máximo |
|---|---:|---:|---:|---:|
| r_conj_detected | 0 | NA | NA | NA |
| r_inj_numerical_upper | 0 | NA | NA | NA |
| A_embed_event_estimates | 0 | NA | NA | NA |
| A_embed_ratio_event_estimates | 0 | NA | NA | NA |

Las distribuciones de eventos tienen como denominador sólo los eventos detectados; no son estimaciones de la distribución completa de máximos. Las áreas de controles están censuradas observacionalmente al nivel nominal 0.02. No se exploraron radios mayores. No se construyeron cotas inferiores globales de r_inj. Las cotas superiores y A_embed de positivos son numéricas: no se ha demostrado que el primer conjugado coincida con el primer corte, ni descartado un corte anterior.

## Instrumento y compuertas

Se conservan arquitectura13→64→32→3 ReLU/float64; checkpoints y semillas C1; rho=1e-4; M/f exactos; centro(0,0); área nominal0.02; radios nominales C1, tolerancias y geometría heredados. DOP853 rtol2e-10/atol2e-12. La calibración nominal se recupera de artefactos verificados, sin redefinir el dominio.

Protocolo T1-A congelado antes del nuevo screening: bordes512/1024 y Jacobi256/512, ambas fases0 y media celda;128 radios para borde y512 para Jacobi. Candidatos por cruce, cero/cambio de signo, min|det|<0.05, condición>100 o anomalía numérica. Nivel2:2048/4096/8192 y Jacobi1024, ambas fases; RK4 128/256/512 pasos. Nivel3:16384 sólo ante inconsistencias predefinidas. Los datos A2 conservan sus16384; no se impuso esa resolución a los demás.

La condición intrínseca y det Dexp se estiman por Jacobi j/r, retirando la singularidad polar en origen. SPD de G se registra aparte. El radio de primer cruce es una detección muestreada con bisección, no un certificado. La búsqueda del interior usa Jacobi y frentes a múltiples radios; no se equipara borde simple aislado con inyectividad global.

## Relaciones con geometría espacial previa

Se enlazan C_A, Lambda1%, Lambda0.1%, R_eff, f50 y f90 sin imputación. Se entregan correlaciones Pearson/Spearman por régimen y Spearman dentro de split y entre medianas de split, sin p-valores. Para comparabilidad se usa Jacobi512 y ambas fases en todos los estados; esta normalización descriptiva no modifica ninguna clasificación ni compuerta.

Los dominios C1 inválidos no reciben estimandos espaciales reparados. Cuando los positivos no tienen C_A/concentración válidos, el contraste directo injective/noninjective y la correlación con A_embed o r_conj no son estimables. Las asociaciones con condición o determinante en dominios disponibles describen deformación local; no prueban relación causal con no inyectividad. Ver linked_geometry.csv, correlations.csv, hierarchical_correlations.csv y group_contrasts.json.

## Integridad, costes e incidencias

- ZIP C1: SHA256397d0b0d274ffaf72f98b79d8bf3b7c8442cc8916b041a8f5e8cf64a490a7adc; CRC correcto;1925/1925 entradas de manifest;80/80 checkpoints.
- ZIP A2: SHA25618dbde0b50fe998274c105ef59618420413d7fbae49100628831527f1fa98648; CRC correcto;581/581 entradas de manifest. El SHA externo se registra; no se encontró un sidecar externo independiente en la búsqueda.
- Reconstrucción80/80; máximo error relativo M=1.3842031091770592e-11; f idéntico. Se usan los campos guardados, sin reemplazarlos por reconstrucciones redondeadas.
- Auditoría final:80 archivos ZIP por estado persistidos;780 arrays finales leídos;80 checkpoints verificados; scripts y protocolo con SHA.
- Suma de CPU nueva de procesos por estado: 972.137s; suma de tiempos de pared por estado: 972.365s. No son tiempo total de reloj: hay cuatro procesos y guardado entre lotes. La evidencia A2 reutilizada conserva costes históricos separados en task_log.csv.

Hubo archivos temporales NPZ incompletos detectados por un glob demasiado amplio del postprocesador. Se retienen los informes iniciales y bytes temporales. La corrección excluyó sólo archivos .tmp.npz, leyó los finales ya completos y comprobó que no cambió ningún archivo de tarea: cero reintegraciones y cero sustituciones. No fue una anomalía geométrica ni se etiquetó NUMERICAL_FAILURE científico. postprocess_recovery.json contiene la trazabilidad; run_map.py conserva la versión ejecutada y run_map_postprocess.py la corrección.

## Respuestas obligatorias

1. True: 2/40 GEOMETRIC_NONINJECTIVITY.
2. Random: 0/40.
3. Todos los positivos están en split0:2/5 true;0/5 random. En splits1–7 no se detectaron positivos.
4. Depende de la inicialización en split0 (j1,j3 frente a j0,j2,j4), pero no se establece una dependencia fuerte general.
5. A_embed detectada:0.01542077684 y0.01694300409; mediana0.01618189046. Otros38 true y40 random censurados observacionalmente a0.02.
6. 2 estados positivos no alcanzan la familia nominal embebida de área0.02 bajo la evidencia numérica; no es una afirmación sobre toda región embebida arbitraria.
7. No se puede estimar la asociación directa de no inyectividad con C_A/concentración si faltan esos valores en los positivos. Las correlaciones de diagnósticos continuos disponibles son sólo descriptivas.
8. Casos con cut locus probable sin conjugado detectado: 0. La ausencia de detección no descarta corte previo.
9. Sí: mapa observacional de80/80, sin sustituciones y con persistencia/auditoría. No es prueba global de inyectividad.
10. No abrir T1-B poblacional: sólo se reproducen los dos casos conocidos. Fenómeno poco frecuente en este panel (2/80=2.5%); corresponde una serie geométrica específica, sin extrapolar rareza universal.

## Correlaciones descriptivas de condición intrínseca

Misma resolución: Jacobi512, ambas fases. No son correlaciones del evento binario ni evidencia sobre causalidad.

| Métrica espacial | Spearman true | Spearman random |
|---|---:|---:|
| C_A | 0.9718 (n=38) | 0.9996 (n=40) |
| lambda_1pct | 0.7089 (n=38) | 0.2666 (n=40) |
| lambda_01pct | 0.6864 (n=38) | 0.2666 (n=40) |
| R_eff | -0.7223 (n=38) | -0.2660 (n=40) |
| frac50 | -0.7188 (n=38) | -0.2660 (n=40) |
| frac90 | -0.7186 (n=38) | -0.2636 (n=40) |

En random la condición común varía aproximadamente entre1.0000000029 y1.0000157764: una correlación de rangos alta no implica deformación grande ni proximidad a pérdida de rango. En true, C_A frente a condición da Spearman0.9718 en38 estados con dominio válido; la asociación del evento binario sigue sin ser estimable por falta de C_A en los dos positivos. La dependencia entre inicializaciones del mismo split impide leer estos conteos como réplicas independientes. hierarchical_correlations.csv separa asociaciones dentro de split y medianas entre splits.


## Decisión de continuación

**T1-B poblacional no se abre.** Queda propuesta, sin nueva ejecución, una serie específica de split0 true j1/j3 con sus controles random emparejados y true j0/j2/j4. Estudiar colisiones continuas, minimización independiente de longitudes, curvas conjugadas y cut locus, con nuevo protocolo congelado antes de radios adicionales. El nombre de este documento no implica inicio de T1-B poblacional.

C1-A conserva INCONCLUSIVE. C1 no se rescata reduciendo áreas. C2 permanece cerrado.

## Archivos y reanudación

progress.md, state_results.csv, task_log.csv, manifest.csv, failures.md, protocolo congelado, scripts,80 ZIP por estado, common_sources.zip, enlaces descriptivos, figuras, auditoría final y cierre quedan bajo /Leviathan/Repro/E15_T1_A/. El cierre también se guarda en /Leviathan/. README.md describe la reanudación y la recuperación de cada estado confirmado.

![Diagnósticos descriptivos](population_diagnostics.png)
