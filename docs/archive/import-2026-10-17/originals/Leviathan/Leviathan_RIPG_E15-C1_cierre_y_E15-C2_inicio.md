# Leviathan / RIPG — E15-C1: cierre de la ejecución y condición de E15-C2
Fecha UTC: 2026-09-25T01:41:05.443933+00:00

**C1-A: INCONCLUSIVE para magnitud; INCONCLUSIVE para localización. C1-B: INCONCLUSIVE, pendiente. C2 no abierto.**

El panel de 80 estados se procesó: {'PASS': 78, 'FAIL': 0, 'INCONCLUSIVE': 2}. Se reutilizaron 16 resultados j=0 mesh-independent de B8 y se entrenaron/evaluaron 64 estados nuevos. Quedaron 38/40 pares elegibles y 7/8 particiones con las cinco inicializaciones completas. No se sustituyeron semillas ni se repararon dominios para admitir estados.

## Integridad y protocolo

El ZIP original conserva SHA-256 `18cf736dca66dea7915a4a10d1827454047fa829d88dc8fb65896143364b7430`: 28/28 archivos y 16/16 checkpoints íntegros. La reproducción de los 16 entrenamientos j=0 fue exacta en pesos, pasos y accuracy. Los 80 checkpoints están incluidos con sus hashes; j=0 usa los originales. Las dependencias faltantes se restauraron a las versiones B8 antes de obtener resultados nuevos.

Semillas: split=1000+s; init=2000+j; minibatches=4000+10s+j; permutación de etiquetas=3000+10s+j. Arquitectura Wine 13→64→32→3, ReLU, float64, Adam 0.006, batch64, presupuesto máximo 20000; parada al primer control cada 25 pasos con accuracy objetivo≥0.99. Misma inicialización y secuencia de minibatches por par; la longitud realizada puede diferir por el mismo criterio de parada. Panel geométrico de validación y geometría RIPG exactos; rho=1e-4.

Disco completo D0.02, seis fuentes (64×32, 96×48, 128×64; fases 0 y π/nt), borde común 2048, DOP853 rtol2e-10/atol2e-12, calibración degree5 con 32 anillos y Brent xtol1e-13. Delaunay global y comprobación de cobertura. Refinamiento global 80% del error, máximo 18 rondas y 1.2M candidatos según la implementación heredada; dos rondas estables. No jets regionales ni surrogates.

Convergencia interna y mesh-independence se evalúan por separado. Compuerta primaria (max CA−min CA)/mediana CA<0.005; se conservan también las cinco compuertas de concentración de B6/B8. La tolerancia de área calibrada es |A/0.02−1|≤1e-6; el error de suma por centroides se reporta separadamente, exactamente como B8. El protocolo JSON y los hashes de geometría/integrador permanecieron intactos.

## Exclusiones y diagnóstico

- split0, j=1: [{"regime": "true", "status": "INCONCLUSIVE", "gates": null, "exceptions": ["AssertionError()"], "internal": null}]
- split0, j=3: [{"regime": "true", "status": "INCONCLUSIVE", "gates": null, "exceptions": ["AssertionError()"], "internal": null}]
- Diagnóstico split0_init1_true: Self-intersection[1.02295003176527 -2.36009167676653]; radio=0.0885287453; área radial=0.02; triángulos de orientación negativa=948.
- Diagnóstico split0_init3_true: Self-intersection[0.706488943885091 -0.672652418991271]; radio=0.0840003677; área radial=0.02; triángulos de orientación negativa=500.

La suma de cuadratura radial puede alcanzar 0.02 incluso si el mapa exponencial se pliega: no acredita un disco simple cuando el borde se autointerseca. Los diagnósticos guardan rayos, orientaciones, validez a radios fraccionarios y auditoría SPD. No se aplicó buffer, unión de polígonos, reducción del radio ni otra redefinición del dominio. La autointersección por sí sola no distingue error ODE de un locus de corte/conjugación.

Un fallo de un miembro excluye el par completo. La política fijada antes de los resultados exige INCONCLUSIVE para la confirmación del panel de 40 si hay alguna exclusión. Los resultados elegibles siguientes son descriptivos, no una selección confirmatoria de supervivientes.

## Contrastes jerárquicos espaciales

Diferencias firmadas true−random. Cada estado se resume por la mediana de sus seis fuentes. Cada partición completa se resume por la mediana de cinco contrastes. Los valores de particiones incompletas se conservan descriptivamente en results_splits.csv y no entran a la prueba sobre particiones completas.

| Estimando | Pares en dirección esperada | Particiones completas en dirección | Mediana de diferencias de partición | p signos bilateral | p Holm | BCa95 | Estado |
|---|---:|---:|---:|---:|---:|---|---|
| C_A | 38/38 | 7/7 | 52.7167637 | 0.015625 | 0.09375 | No calculado: faltan particiones completas | INCONCLUSIVE |
| lambda_1pct | 38/38 | 7/7 | 0.162432494 | 0.015625 | 0.09375 | No calculado: faltan particiones completas | INCONCLUSIVE |
| lambda_01pct | 38/38 | 7/7 | 0.0210930469 | 0.015625 | 0.09375 | No calculado: faltan particiones completas | INCONCLUSIVE |
| frac50 | 38/38 | 7/7 | -0.440300465 | 0.015625 | 0.09375 | No calculado: faltan particiones completas | INCONCLUSIVE |
| frac90 | 38/38 | 7/7 | -0.563454839 | 0.015625 | 0.09375 | No calculado: faltan particiones completas | INCONCLUSIVE |
| R_eff | 38/38 | 7/7 | -0.841707797 | 0.015625 | 0.09375 | No calculado: faltan particiones completas | INCONCLUSIVE |

No se ejecutó un bootstrap sobre supervivientes como sustituto del BCa preespecificado de las ocho particiones. El protocolo conserva mediana, BCa95, 100000 remuestreos y semilla 150150 para un panel completo. Los p anteriores no constituyen una prueba exacta sobre ocho particiones si n<8. Las particiones comparten ejemplos Wine: tampoco son réplicas de datasets independientes.

### Distribución entre inicializaciones

| Estimando | j0 | j1 | j2 | j3 | j4 |
|---|---:|---:|---:|---:|---:|
| C_A | 8/8; mediana 66.4832105 | 7/7; mediana 30.0296307 | 8/8; mediana 34.1241924 | 7/7; mediana 66.4908904 | 8/8; mediana 47.0096438 |
| lambda_1pct | 8/8; mediana 0.275261743 | 7/7; mediana 0.177728918 | 8/8; mediana 0.184935516 | 7/7; mediana 0.140103566 | 8/8; mediana 0.0599400814 |
| lambda_01pct | 8/8; mediana 0.035617976 | 7/7; mediana 0.0210930469 | 8/8; mediana 0.021931687 | 7/7; mediana 0.0160806103 | 8/8; mediana 0.00643734667 |
| frac50 | 8/8; mediana -0.461084965 | 7/7; mediana -0.426785603 | 8/8; mediana -0.445032006 | 7/7; mediana -0.440300465 | 8/8; mediana -0.390162066 |
| frac90 | 8/8; mediana -0.780154541 | 7/7; mediana -0.632552089 | 8/8; mediana -0.641187192 | 7/7; mediana -0.647995154 | 8/8; mediana -0.52855568 |
| R_eff | 8/8; mediana -0.933276895 | 7/7; mediana -0.876603015 | 8/8; mediana -0.860641222 | 7/7; mediana -0.841707797 | 8/8; mediana -0.712609905 |

Cada celda muestra pares en dirección esperada / pares elegibles y mediana del contraste. No afirma replicación de las cinco inicializaciones donde faltan estados.

### Heterogeneidad entre particiones completas

| Estimando | SD | IQR | Rango | IQR / abs(mediana) |
|---|---:|---:|---:|---:|
| C_A | 93.6201633 | 72.4218493 | 265.354257 | 1.37379164 |
| lambda_1pct | 0.154765745 | 0.228297647 | 0.387668366 | 1.40549247 |
| lambda_01pct | 0.0506869433 | 0.0465282188 | 0.138000058 | 2.20585575 |
| frac50 | 0.0684185778 | 0.0775860265 | 0.191657826 | 0.176211548 |
| frac90 | 0.181711721 | 0.298479154 | 0.455721953 | 0.529730394 |
| R_eff | 0.186350061 | 0.24896815 | 0.508960988 | 0.295789288 |

Las tablas conservan SD, IQR y rango de los cinco contrastes dentro de cada split, y las distribuciones por inicialización. Las unidades de CA difieren de las métricas normalizadas: comparar SD brutas entre estimandos sería engañoso. La razón IQR/|mediana| es descriptiva y no una compuerta nueva. El modelo aditivo 8×5 preespecificado no se ajusta a una matriz incompleta; no se imputa el residual para afirmar interacción.

## Respuestas científicas

1. **¿Sobreviven las seis señales a las cinco inicializaciones?** No puede confirmarse para el panel solicitado. Las direcciones observadas y sus conteos se muestran arriba, pero existen pares excluidos.
2. **¿Se mantienen en las 8 particiones?** No está establecido bajo las cinco inicializaciones: sólo las particiones completas admiten el agregado preespecificado. El resultado B8 j=0 sigue vigente dentro de su alcance.
3. **¿Qué estimandos son más heterogéneos?** En las siete particiones completas, la dispersión relativa IQR/|mediana| es mayor para Lambda0.1% (2.206), seguida por Lambda1% (1.405) y CA (1.374); menor para f50 (0.176), Reff (0.296) y f90 (0.530). Es una comparación descriptiva condicionada a elegibilidad, no una clasificación confirmatoria.
4. **¿Localización independiente de CA?** Las cinco métricas normalizadas son invariantes ante un factor multiplicativo uniforme de K. Eso separa sus definiciones de la magnitud, pero no demuestra independencia estadística o causal. analysis.json incluye correlaciones de rangos descriptivas dentro de régimen y entre contrastes de partición, sin tratar 40 pares como 40 réplicas independientes.
5. **¿Sobreviven H_phi y s3?** No evaluado en el panel completo. C1-B queda pendiente/INCONCLUSIVE; no se reutilizan las conclusiones históricas de profundidad como resultados C1.
6. **¿Interacción split×inicialización?** No hay una prueba identificable de interacción separada del error sin replicación dentro de celdas, y el panel adicionalmente es incompleto. La heterogeneidad observada no basta para esa afirmación.
7. **Clasificación por familias:** magnitud INCONCLUSIVE; localización INCONCLUSIVE; profundidad INCONCLUSIVE (no ejecutada). No es un FAIL científico de las direcciones: la confirmación está bloqueada por las compuertas numéricas.

## C1-B y condición de continuación

C1 se divide en C1-A espacial (ejecución cerrada, conclusión inconclusa) y C1-B profundidad (pendiente). Los dominios inválidos impiden completar bajo el protocolo congelado los siete campos sobre el mismo dominio de todos los 80 estados. Además, seis coaliciones adicionales por estado multiplican sustancialmente el coste: no se sustituye la definición por singleton, punto central o dominio propio de cada coalición. Las matrices de coaliciones de los estados nuevos quedan guardadas para continuación, sin atribuciones inferidas a partir de ellas.

**E15-C2 no se abre.** La continuación es diagnosticar y resolver la extensión del constructor de disco geodésico fuera de su dominio simple, en una etapa explícita y con cualquier protocolo nuevo congelado antes de reevaluar. No cambiar silenciosamente D0.02 ni las compuertas C1; conservar estas clasificaciones. Después, completar C1-A bajo un protocolo autorizado y C1-B (siete subconjuntos sobre dominio común), y sólo entonces reconsiderar C2. No se abrió tarea/arquitectura externa.

## Auditoría y coste

- Fuentes terminadas con métricas: 468/480. Estados sin fuentes válidas quedan expresamente registrados; no se inventan sus estimandos.
- Máxima dispersión CA entre estados con seis fuentes: 2.05009214e-05 como fracción (0.00205009214%).
- Máximo |error relativo de área calibrada| registrado: 4.77395901e-13. Máximo |error relativo por centroides|: 0.000242384609.
- Tiempo de ejecución C1 nueva: 718.689783s de pared; suma CPU geométrica de los 64 estados: 4136.03956s. Entrenamiento y replay: 4.53381372s. Seis procesos, un hilo por proceso. B8 reutilizado no cuenta como coste nuevo.
- Diagnóstico adicional de dominios: suma de tiempos de casos 88.2504086s. Tiempos y RSS por estado y fuente incluidos; el RSS de un worker puede reflejar máximos de estados anteriores.
- Auditoría final: 0 observaciones no-SPD, 0 no finitas y 0 excepciones de evaluación métrica. Autovalor mínimo observado 7.05047e-8; condición máxima 20153.72. Las dos excepciones de dominio permanecen registradas por separado.
- El máximo error de área por centroides corresponde a split6 / j1 / true / fuente64×32 fase0; supera el máximo observado en B8. No se usa la precisión de calibración como estimación de precisión de la cuadratura adaptativa.

## Artefactos y reanudación

Paquete: `/Leviathan/Repro/Leviathan_E15_C1_codigo_resultados.zip`. Incluye código, protocolo congelado, 80 checkpoints, manifest SHA-256, resultados por fuente/estado/par/split, exclusiones, entrenamiento, logs, dominios y diagnósticos. Las tablas CSV también se guardan por separado. El README da los comandos de reproducción.

Este estado se guarda como `/Leviathan/Leviathan_RIPG_E15-C1_cierre_y_E15-C2_inicio.md`; el nombre de destino solicitado no significa que C2 haya comenzado. Los valores provisionales B4/B5 quedan sólo como insumos históricos del ZIP original, fuera del análisis. La referencia B6 de 1052.60819 a 8192 rayos nunca se mezcla con el panel común 2048.
