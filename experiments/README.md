# Experimentos cerrados

Selección documental mínima, revisada el 18 de octubre de 2026. Los originales permanecen en el archivo histórico; las fichas los enlazan sin duplicarlos. Cierre de ejecución no significa confirmación científica.

| Etapa | Estado del cierre | Lectura |
|---|---|---|
| E10 | CERRADO_EXPLORATORIO | [README](E10/README.md) · [Conclusión](E10/CONCLUSION.md) |
| E11 | CERRADO_EXPLORATORIO | [README](E11/README.md) · [Conclusión](E11/CONCLUSION.md) |
| E12 | CERRADO_EXPLORATORIO | [README](E12/README.md) · [Conclusión](E12/CONCLUSION.md) |
| E13 | INCONCLUSIVE | [README](E13/README.md) · [Conclusión](E13/CONCLUSION.md) |
| E15/B6 | CIERRE_NUMERICO | [README](E15/B6/README.md) · [Conclusión](E15/B6/CONCLUSION.md) |
| E15/B7 | PASS_NUMERICO | [README](E15/B7/README.md) · [Conclusión](E15/B7/CONCLUSION.md) |
| E15/B8 | PASS_NUMERICO | [README](E15/B8/README.md) · [Conclusión](E15/B8/CONCLUSION.md) |
| E15/C1-A | INCONCLUSIVE | [README](E15/C1-A/README.md) · [Conclusión](E15/C1-A/CONCLUSION.md) |
| E15/C1-A2 | GEOMETRIC_NONINJECTIVITY | [README](E15/C1-A2/README.md) · [Conclusión](E15/C1-A2/CONCLUSION.md) |
| T1/A | MAPA_COMPLETO_DESCRIPTIVO | [README](T1/A/README.md) · [Conclusión](T1/A/CONCLUSION.md) |
| T1/B | EXPECTED_GEOMETRIC_CONTROL | [README](T1/B/README.md) · [Conclusión](T1/B/CONCLUSION.md) |

## Límites de cobertura

E1–E8 permanecen en la [revisión estática histórica](../docs/archive/review-before-import/docs/experiment-index.md) y el notebook. E9 y E14 carecen del cierre primario autónomo recuperado: no se inventan fichas de cierre. E15-B1–B5 se consultan como antecedentes históricos en el archivo; sus estimaciones provisionales no sustituyen B6–B8.

T2-A0 es un [prerregistro](../docs/archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_T2-A0_preregistro.md), no un resultado confirmatorio. [T2-A](T2_A/README.md) continúa abierto; el cierre documental de una incidencia no cierra el seguimiento.

## Integridad

[closed_sources.csv](closed_sources.csv) registra ruta, bytes y SHA-256 de cada fuente seleccionada tal como está en este commit. Es un inventario nuevo y no reemplaza los manifests históricos. Verificación documental: `python tools/verify_closed_sources.py`. No requiere checkpoints ni ejecuta geometría.

## Línea independiente analítica

[E16 — Composicionalidad y coarse-graining perspectival](E16/README.md):
EXPECTED_GEOMETRIC_CONTROL; [conclusión](E16/CONCLUSION.md). Diseño congelado,
código y resultados pequeños propios, sin ejecutar ni modificar T2-A.

[E16-B — Instrumentación en red sintética sin entrenamiento](E16/B/README.md):
identidades PASS, validación independiente del rango INCONCLUSIVE; diseño
congelado, 81 configuraciones conservadas y cero pasos de entrenamiento.

[E16-D — Réplica instrumental en configuraciones nuevas](E16/D/README.md):
396/396 rangos PASS_NUMERICAL, 216/216 negativos detectados y ausencia de cambios
de rango entre composiciones en esta muestra sintética sin entrenamiento.

## E16-E — Distancias y anisotropía relativa

[README](E16/E/README.md) · [conclusión](E16/E/CONCLUSION.md) ·
[evidencia](E16/E/results/run_v1/summary.json). Exploratorio sobre datos D:
216 comparaciones SPD con cambios de forma, sin entrenamiento.

## E16-F — Longitudes de caminos prefijados

[README](E16/F/README.md) · [conclusión](E16/F/CONCLUSION.md) ·
[evidencia](E16/F/results/run_v1/summary.json). Estado global INCONCLUSIVE:
239 longitudes validadas y 85 inconclusas; sin entrenamiento ni geodésicas.

## E16-G — Resolución numérica de las limitaciones F

[README](E16/G/README.md) · [conclusión](E16/G/CONCLUSION.md) ·
[evidencia](E16/G/results/run_v1/summary.json). PASS_NUMERICAL diagnóstico:
324/324 longitudes, incluidos los 85 inconclusos F. Sin cambiar F ni T2-A.

## E16-H — Transferencia prospectiva

[README](E16/H/README.md) · [conclusión](E16/H/CONCLUSION.md) ·
[evidencia](E16/H/results/run_v1/summary.json). PASS_NUMERICAL: 324 longitudes
nuevas y 216 pares, sin selección, entrenamiento ni cambios al método G.

## E16-I — Búsqueda acotada de caminos

[README](E16/I/README.md) · [conclusión](E16/I/CONCLUSION.md) ·
[evidencia](E16/I/results/run_v1/summary.json). 27 casos PASS_NUMERICAL y
18 mejoras no lineales; nueve controles con suma conservan la recta. No se
certifican geodésicas ni mínimos globales.

## E16-J — Refinamiento de caminos

[README](E16/J/README.md) · [conclusión](E16/J/CONCLUSION.md) ·
[evidencia](E16/J/results/run_v1/summary.json). Global INCONCLUSIVE: 24 casos
validados y tres inconclusos; 81 resoluciones, sin geodésicas certificadas.

## E16-K — Resolución diagnóstica parcial de J

[README](E16/K/README.md) · [conclusión](E16/K/CONCLUSION.md) ·
[evidencia](E16/K/results/run_v1/summary.json). Global INCONCLUSIVE: dos casos
difíciles resueltos, dos controles válidos y un caso de refinamiento pendiente.

## E16-L — Refinamiento del camino completo

[README](E16/L/README.md) · [conclusión](E16/L/CONCLUSION.md) ·
[evidencia](E16/L/results/run_v1/summary.json). Longitud validada por refinamiento,
forma sin acuerdo; global INCONCLUSIVE. Incluye figura y 36 reinicios conservados.

## E16-M — Seguimiento de candidatos

[README](E16/M/README.md) · [conclusión](E16/M/CONCLUSION.md) ·
[evidencia v2](E16/M/results/run_v2/summary.json). Global INCONCLUSIVE por forma;
Q0/Q1 coinciden en 64/128, sin concentración de cambio establecida en la cola fijada.

### E16-N — Nodos graduados y Hausdorff

[E16-N](E16/N/README.md): nueve optimizaciones válidas y 21 comparaciones.
La separación 64→128 baja con nodos graduados pero aún supera 0,001, incluso
usando Hausdorff entre curvas. Global INCONCLUSIVE; M y T2-A intactos.

### E16-O — Refinamiento guiado por indicador local

[E16-O](E16/O/README.md): once caminos y 1428 probes válidos. Cuatro rondas
llevan cada candidato de 128 a 132 segmentos; longitud y Hausdorff pasan,
forma e indicador terminal no. Global INCONCLUSIVE, con crecimiento de
pendientes cerca de t≈0,9844. Etapas previas y T2-A intactos.

### E16-P — Contraste de representación

[E16-P](E16/P/README.md): t fijo frente a t/s libres con los mismos extremos y
dominio. Ocho de doce caminos pasan el protocolo completo; los cuatro libres
cuadráticos agotan iteraciones. Global INCONCLUSIVE, con diferencia geométrica
entre candidatos y trece salidas reproducidas. O y T2-A intactos.

### E16-Q — Energía, parametrización y condicionamiento

[E16-Q](E16/Q/README.md): cuatro caminos del control pasan; ocho cuadráticos
alcanzan el límite de iteraciones. Gradientes y Hessianos verificados, sin
confundir energía afín con longitud. Global INCONCLUSIVE; quince salidas v2
reproducidas, v1 parcial conservada con errata. P y T2-A intactos.

### E16-R — Escalado diagonal del mismo objetivo

[E16-R](E16/R/README.md): ambos métodos minimizan L en el mismo dominio.
El escalado cumple KKT físico en 4/4 cuadráticos frente a 2/4 referencias,
pero todos agotan iteraciones. Global INCONCLUSIVE; cuatro caminos C0 pasan.
Quince salidas reproducidas; costes y espectros documentados. Q y T2-A intactos.

### E16-S — Parada por KKT físico con auditorías MP

[E16-S](E16/S/README.md): doce caminos y seis refinamientos PASS_NUMERICAL.
Ocho paradas por tres auditorías consecutivas; cuatro controles nativos.
105 auditorías, ninguna sin verificar; costes completos y banderas conservadas.
R/Q y T2-A intactos; no demuestra mínimo global ni convergencia continua.

### E16-T — Hessianos físicos y modos casi nulos

[E16-T](E16/T/README.md): validación diagnóstica PASS en doce caminos;
488 comprobaciones y contrastes MP. Cuatro cuadráticos finos con curvatura
negativa casi tangencial, control C0 analítico. INCONCLUSIVE sobre mínimos.
No cambia S ni T2-A/T2_A1; espectros escalares sin matrices densas.

### E16-U — Descenso y geometría con pasos prefijados

[E16-U](E16/U/README.md): 360 ensayos, 350 válidos, diez inviables;
1.487 comprobaciones PASS. Cuatro cuadráticos finos con cambio par negativo
en full_min y descenso unilateral para los tres pasos. Cambios geométricos
resueltos y no resueltos conservados; S/T y T2-A intactos. Estudio exploratorio.

### E16-V — Subdivisión y transporte de direcciones

[E16-V](E16/V/README.md): doce orígenes, cinco familias y 360 ensayos;
350 válidos, diez inviables y 2.466 comprobaciones PASS. Transporte conserva
los cambios de U; nodos insertados fijos cambian el signo par en los finos.
Exploratorio, sin nuevo espectro refinado ni mínimos certificados. T2-A intacto.

### E16-W — Dirección perpendicular al gradiente

[E16-W](E16/W/README.md): diagnóstico PASS, 144 ensayos y 1.144
comprobaciones. Ocho proyecciones cuadráticas casi de primer orden nulo con
curvatura positiva; C0 usa regla de gradiente pequeño. Cuatro inviables
conservados. No prueba positividad de g⊥; S/T/U/V y T2-A intactos.
