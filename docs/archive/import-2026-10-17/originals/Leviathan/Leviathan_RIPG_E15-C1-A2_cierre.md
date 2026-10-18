# Leviathan / RIPG — cierre E15-C1-A2

Fecha de cierre: 2026-09-28T19:31:34.706591+00:00

## Decisión

**E15-C1-A permanece INCONCLUSIVE.** Esta auditoría es diagnóstica y no reabre C1-A ni autoriza C2. Los resultados originales 78/80 PASS y 38 pares elegibles no se transforman en evidencia confirmatoria del panel completo.

| Estado primario | Clasificación A2 | Radio nominal | Primer conjugado estimado / cota superior numérica de r_inj | A_embed estimada | A_embed/0.02 |
|---|---|---:|---:|---:|---:|
| split 0 / j1_true | GEOMETRIC_NONINJECTIVITY | 0.08852874528 | 0.0759620835 | 0.01542077684 | 0.7710388418 |
| split 0 / j3_true | GEOMETRIC_NONINJECTIVITY | 0.08400036772 | 0.07637387649 | 0.01694300409 | 0.8471502043 |

Las cotas de r_inj son numéricas, no intervalos certificados. No se demuestra r_inj=r_conj ni se descarta un cut locus anterior. A_embed aproxima el límite inicial de la familia embebida conectada al origen; no se usa para reducir el área de C1.

## Integridad y protocolo

Se descomprimió y verificó por SHA-256 el paquete C1: **1925 archivos y 80 checkpoints** íntegros. Se verificó también el manifest B4/B5: **28 archivos y 16 checkpoints** íntegros. Ambos ZIP pasan además CRC. El ZIP B4/B5 tiene SHA-256 `18cf736dca66dea7915a4a10d1827454047fa829d88dc8fb65896143364b7430`. El ZIP C1 tiene SHA-256 `397d0b0d274ffaf72f98b79d8bf3b7c8442cc8916b041a8f5e8cf64a490a7adc`. `final_integrity_audit.json` comprueba otra vez la inmutabilidad de los archivos fuente y de los diez checkpoints usados.

Arquitectura 13→64→32→3, semillas, panel, rho=1e-4, M/f, D_0.02, radios nominales y criterios heredados permanecen iguales. Los j=0 espaciales se toman de B8 mesh-independent. No se reutilizan estimaciones provisionales B4/B5. No se reentrenó ni reemplazó corrida alguna.

La reconstrucción desde checkpoints da un error máximo relativo de M de 1.38e-11 y máximo absoluto de f de 0. Se integraron los M/f guardados, sin sustituirlos por reconstrucciones redondeadas.

La matriz congelada incluye **220 tareas**: 80 bordes DOP853, 60 sistemas geodésica/Jacobi y 80 bordes RK4. DOP853: 2048/4096/8192/16384 rayos, fases 0 y media celda, rtol=2e-10 y atol=2e-12. RK4: 2048 rayos, ambas fases, 64/128/256/512 pasos. Jacobi: 256/512/1024 ángulos, ambas fases. Todos los controles reciben el mismo instrumento.

## Resolución, fase y radio del primer cruce

| Estado | Rayos | Fase (celdas) | Cruces al radio nominal | Último radio simple | Primer radio no simple |
|---|---:|---:|---:|---:|---:|
| j1_true | 2048 | 0 | 1 | 0.07596242521 | 0.07596242521 |
| j1_true | 2048 | 0.5 | 1 | 0.07596248409 | 0.07596248409 |
| j1_true | 4096 | 0 | 1 | 0.07596212856 | 0.07596212856 |
| j1_true | 4096 | 0.5 | 1 | 0.07596224943 | 0.07596224943 |
| j1_true | 8192 | 0 | 1 | 0.07596212735 | 0.07596212735 |
| j1_true | 8192 | 0.5 | 1 | 0.0759621002 | 0.0759621002 |
| j1_true | 16384 | 0 | 1 | 0.07596210327 | 0.07596210328 |
| j1_true | 16384 | 0.5 | 1 | 0.07596210622 | 0.07596210622 |
| j3_true | 2048 | 0 | 1 | 0.07637435419 | 0.07637435419 |
| j3_true | 2048 | 0.5 | 1 | 0.07637404817 | 0.07637404817 |
| j3_true | 4096 | 0 | 1 | 0.07637396843 | 0.07637396843 |
| j3_true | 4096 | 0.5 | 1 | 0.07637393452 | 0.07637393453 |
| j3_true | 8192 | 0 | 1 | 0.07637388918 | 0.07637388918 |
| j3_true | 8192 | 0.5 | 1 | 0.07637390276 | 0.07637390277 |
| j3_true | 16384 | 0 | 1 | 0.07637388015 | 0.07637388015 |
| j3_true | 16384 | 0.5 | 1 | 0.07637388209 | 0.07637388209 |

Los intervalos anteriores son de bisección de cada borde discretizado; su anchura no representa toda la incertidumbre numérica. La estabilidad entre mallas/fases y el refinamiento del integrador se evalúan por separado.

| Estado | Cambio relativo máximo de la posición del cruce (8192/16384, ambas fases) | Rango de mínimos conjugados (512/1024, ambas fases) | Diferencia relativa A_embed 32/64 anillos | Diferencia relativa A_embed 8192/16384 |
|---|---:|---:|---:|---:|
| j1_true | 4.329081217e-09 | 5.134781489e-16 | 1.590133702e-10 | 4.661535257e-07 |
| j3_true | 6.138758375e-09 | 2.636779683e-16 | 1.237618779e-09 | 5.351850919e-08 |

### Refinamiento RK4

| Estado | Pasos | Fase (celdas) | Cruces | Número de giro |
|---|---:|---:|---:|---:|
| j1_true | 64 | 0 | 2 | 1 |
| j1_true | 64 | 0.5 | 2 | 1 |
| j1_true | 128 | 0 | 1 | 2 |
| j1_true | 128 | 0.5 | 1 | 2 |
| j1_true | 256 | 0 | 1 | 2 |
| j1_true | 256 | 0.5 | 1 | 2 |
| j1_true | 512 | 0 | 1 | 2 |
| j1_true | 512 | 0.5 | 1 | 2 |
| j3_true | 64 | 0 | 2 | 1 |
| j3_true | 64 | 0.5 | 2 | 1 |
| j3_true | 128 | 0 | 1 | 2 |
| j3_true | 128 | 0.5 | 1 | 2 |
| j3_true | 256 | 0 | 1 | 2 |
| j3_true | 256 | 0.5 | 1 | 2 |
| j3_true | 512 | 0 | 1 | 2 |
| j3_true | 512 | 0.5 | 1 | 2 |

El RK4 más grueso puede introducir cruces adicionales: en 64 pasos aparecen dos en cada primario, frente a uno en DOP853. La desaparición de ese cruce adicional bajo refinamiento no elimina el cruce persistente que sustenta el diagnóstico geométrico. No se identifica toda estructura del discretizado grueso como geométrica.

Los pares de segmentos, ángulos, coordenadas y multiplicidades de **cada** borde DOP853/RK4 están en `intersections.csv`; las matrices completas están en `resolution_phase_matrix.csv`. Índices base cero; ángulos en radianes.

## Cruces nominales y topología

### j1_true

A 16384 rayos y fase 0: 1 cruce(s), winding respecto al origen 1, número de giro tangente 2, 2 caras. Área algebraica en coordenadas P=11.2166198; área de la unión en P=11.21575811. Estas áreas no son áreas intrínsecas RIPG.

- Segmentos [9909, 12178]; ángulos (3.80025052, 4.670220208); punto (1.022949494, -2.360091667); transversabilidad 0.9149825975.

Caras (área en P, winding): [(11.214896426084666, 1), (0.0008616878543238329, 2)]. La colisión de dos rayos continuos distintos tiene residual 4.89e-15, separación angular 0.86996981 y convergencia del solver=True.

El primer borde no simple guardado tiene radio 0.0759621032766; sus pares/ángulos/coordenadas están en `states/j1_true/first_collision.json` y el borde en `first_collision_boundary.npz`.

### j3_true

A 16384 rayos y fase 0: 1 cruce(s), winding respecto al origen 1, número de giro tangente 2, 2 caras. Área algebraica en coordenadas P=1.304262837; área de la unión en P=1.30397409. Estas áreas no son áreas intrínsecas RIPG.

- Segmentos [12786, 14900]; ángulos (4.903627413, 5.71409459); punto (0.7064886827, -0.6726524354); transversabilidad 0.996264484.

Caras (área en P, winding): [(1.3036853426528985, 1), (0.0002887471239519946, 2)]. La colisión de dos rayos continuos distintos tiene residual 1.34e-15, separación angular 0.81046725 y convergencia del solver=True.

El primer borde no simple guardado tiene radio 0.0763738801485; sus pares/ángulos/coordenadas están en `states/j3_true/first_collision.json` y el borde en `first_collision_boundary.npz`.


### Localización de la aparición del cruce

| Estado | Pares de segmentos en el primer borde no simple | Coordenadas aproximadas | Ángulos extremos (rad) |
|---|---|---|---|
| j1_true | [[11036, 11039], [11037, 11039]] | (0.901769756, -1.90277435) | (4.23263647, 4.23348113) |
| j3_true | [[13838, 13840]] | (0.65449292, -0.597735534) | (5.30718581, 5.30757356) |

En el umbral de aparición, j=1 produce dos pares de segmentos con puntos separados aproximadamente a escala de redondeo; no se interpretan como dos cruces geométricos resueltos. Las caras diminutas y winding inestables en ese umbral son diagnósticos del discretizado. Al radio nominal existe un cruce transversal bien separado y dos caras estables en cada primario.
## Jacobiano, SPD y singularidades

| Estado | Mínimo det Dexp muestreado | Rayos con det negativo al radio nominal (de 1024) | Máxima condición intrínseca muestreada | Error máximo Jacobi vs diferencias angulares |
|---|---:|---:|---:|---:|
| j1_true | -0.1549093868 | 77 | 38278.00675 | 5.208573292e-06 |
| j3_true | -0.2339757869 | 66 | 13552.52736 | 1.569817351e-06 |

Se integró j″+Kj=0 con curvatura exacta RIPG. Los ceros positivos con cambio de signo persisten y preceden a R; esto aporta evidencia de pérdida de rango de Dexp, además de los cruces. La condición grande por sí sola no se usa como punto conjugado. El determinante intrínseco es j/r, retirando la singularidad polar del origen. Los arrays y matrices Dexp aproximadas están guardados por estado.

En 412,317,908 evaluaciones métricas se registraron 0 autovalores no positivos y 0 no finitos; mínimo autovalor=3.85554e-05, máxima condición de G=101.594. Excepciones numéricas: 0. La degeneración detectada es de Dexp, no una pérdida SPD de G.

## Controles y comparación descriptiva

| Estado | R nominal | r_conj / r_inj | A_embed (estimada o censurada) | A_embed/0.02 | C_A C1 | Lambda_1% C1 | R_eff C1 |
|---|---:|---|---:|---:|---:|---:|---:|
| j0_random | 0.07978852663 | sin evento hasta R / no certificado | ≥ 0.02000003088 | 1.000001544 | 0.0003762492574 | 0.0105171333 | 0.9992799251 |
| j0_true | 0.0838965885 | sin evento hasta R / no certificado | ≥ 0.02000003674 | 1.000001837 | 387.7013717 | 0.3559869501 | 0.04816538253 |
| j1_random | 0.07978851652 | sin evento hasta R / no certificado | ≥ 0.02000003088 | 1.000001544 | 0.0001014445416 | 0.01010654292 | 0.9999698034 |
| j1_true | 0.08852874528 | 0.0759620835 / ≤ estimación | 0.01542077684 | 0.7710388418 | NA | NA | NA |
| j2_random | 0.07978847744 | sin evento hasta R / no certificado | ≥ 0.02000003088 | 1.000001544 | 0.00194775781 | 0.01018609781 | 0.9999079102 |
| j2_true | 0.08147807912 | sin evento hasta R / no certificado | ≥ 0.02000003315 | 1.000001657 | 155.2303536 | 0.262899597 | 0.07354085085 |
| j3_random | 0.07978851389 | sin evento hasta R / no certificado | ≥ 0.02000003088 | 1.000001544 | 0.0002258285631 | 0.01193238817 | 0.9907790989 |
| j3_true | 0.08400036772 | 0.07637387649 / ≤ estimación | 0.01694300409 | 0.8471502043 | NA | NA | NA |
| j4_random | 0.07978841874 | sin evento hasta R / no certificado | ≥ 0.02000003088 | 1.000001544 | 0.004721221566 | 0.01006471406 | 0.9999882182 |
| j4_true | 0.08391166147 | sin evento hasta R / no certificado | ≥ 0.02000002626 | 1.000001313 | 296.7096808 | 0.3232926028 | 0.06233920468 |

En los controles, “≥” es una cota observacional numérica censurada: no se buscó el máximo más allá de su radio nominal ni se certificó ausencia de todo cut locus. No se asigna una cota inferior rigurosa de r_inj por ausencia de cruces muestreados. Los valores espaciales de los primarios son NA porque C1 rechazó el dominio; no se inventa una comparación sobre un dominio reparado. La asociación de eventos con dos estados true es sólo descriptiva y no demuestra causalidad de C_A, Lambda o R_eff.

## Respuestas obligatorias

1. **j=1:** GEOMETRIC_NONINJECTIVITY; evidencia numérica convergente de pérdida geométrica, no explicada por el discretizado ensayado.
2. **j=3:** GEOMETRIC_NONINJECTIVITY; misma conclusión y mismo instrumento.
3. **Resolución/fase:** persisten los cruces en 2048,4096,8192,16384 rayos y ambas fases; se conserva el fenómeno bajo RK4 refinado. Consultar matrices para valores por corrida.
4. **Rango de Dexp:** sí, ceros positivos estables y cambio de signo de j/r antes de R, con contraste independiente por diferencias angulares.
5. **r_inj:** cotas superiores numéricas ≲0.0759620835 y ≲0.07637387649; no igualdad certificada ni cota inferior global nueva.
6. **A_embed:** aproximadamente 0.01542077684 y 0.01694300409; sólo diagnóstico, no sustitución de A=0.02.
7. **Radio nominal:** en ambos casos R supera la cota conjugada numérica y existe colisión continua al radio nominal; la evidencia apoya R≥r_inj.
8. **C1-A:** permanece INCONCLUSIVE bajo el estimando original. No se reduce A, no se excluye split 0 retrospectivamente ni se abre C2.
9. **Nueva etapa:** corresponde abrir un diseño separado sobre radio de inyectividad, cut locus y topología local RIPG. El archivo de diseño acompaña este cierre; esa etapa todavía no se ha ejecutado.

## Incidencias de serialización

Se detectaron tres archivos NPZ incompletos en controles durante la lectura concurrente: j4 true / borde 16384 fase 0; j3 random / Jacobi 1024 fase 1; j2 true / Jacobi 512 fase 1. Se conservaron los bytes incompletos y hashes y se regeneraron sólo esos arrays con idénticos parámetros. Los JSON originales y clasificaciones permanecieron intactos. No fueron fallos SPD ni sustituciones de estados. Ver artifact_recovery/recovery_log.json y artifact_validation.json para comprobación y costes.

## Coste y reproducibilidad

Matriz principal: 220/220 tareas, 947.98 s de pared (15.80 min) y 5426.75 s CPU agregados (1.51 h CPU), seis procesos. Los JSON por tarea conservan costes individuales. Reconstrucción de campos: 0.43 s. Las comprobaciones adicionales tienen tiempos por estado. Recuperar los tres arrays requirió 121.38 s de pared secuenciales y 302.40 s CPU adicionales. El coste del intento interrumpido no persistido no está incluido. El texto de run.log quedó parcial; los 220 JSON por tarea y run_summary.json son el registro completo.

Artefactos: `Leviathan_E15_C1_A2_codigo_resultados.zip`, manifest SHA-256 interno, SHA externo, protocolos heredados y A2, diez checkpoints, campos, radios, scripts, versiones, logs, todos los bordes nominales, primeros cruces, arrays de Jacobi/Dexp, tablas y figuras. `README.md` detalla reproducción y limitaciones. `recovery.json` registra la repetición; no se importaron resultados del intento perdido.

![Diagnóstico](diagnostico.png)
