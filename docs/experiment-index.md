# Índice experimental

## Etapas iniciales

La [revisión estática E1–E8](archive/review-before-import/docs/experiment-index.md) conserva población, método y referencias por celda del [notebook](../Perspectivas.ipynb). Sus limitaciones no se resuelven mediante esta organización.

## Fuentes posteriores recuperadas

| Etapa | Alcance documental | Fuente |
|---|---|---|
| E9/E10 | Síntesis y axioma; cierre autónomo E9 pendiente | [Contexto](archive/import-2026-10-17/originals/RIPG_contexto_vigente_axioma.md) |
| E11 | Cierre y paso al campo perspectival | [Cierre](archive/import-2026-10-17/originals/Cierre_E11_RIPG_y_apertura_E12.md) |
| E12 | Campo, conexión, curvatura y holonomía como control | [Cierre](archive/import-2026-10-17/originals/E12E_holonomia_control_derivado_y_cierre_E12.md) |
| E13 | Normalización intrínseca y fallo instrumental que motiva E14 | [Cierre](archive/import-2026-10-17/originals/E13_cierre_y_punto_de_partida_E14.md) |
| E14 | Cierre primario autónomo pendiente | [Faltantes](handoff/missing-sources.md) |
| E15-B6/B7/B8/C1/A2 | Auditorías y cierres, C1-A INCONCLUSIVE | [Índice E15](../experiments/E15/README.md) |
| T1-A/B | Panel histórico y análisis descriptivo a radio común | [Índice T1](../experiments/T1/README.md) |
| T2-A0/A | Diseño prospectivo congelado y seguimiento incompleto | [Índice T2-A](../experiments/T2_A/README.md) |

Consultar los protocolos originales para poblaciones y tolerancias; esta tabla no sustituye sus diseños.

## Fichas de cierre

[Selección mínima por experimento: README, conclusión y evidencia](../experiments/README.md).

## Línea independiente: E16

[E16](../experiments/E16/README.md): cartas, subfamilias, descenso de métricas y
composición escalar. Primera fase analítica EXPECTED_GEOMETRIC_CONTROL;
[conclusión y fallos conservados](../experiments/E16/CONCLUSION.md). No continúa E15/T2.

## E16-B — Red sintética sin entrenamiento

[E16-B](../experiments/E16/B/README.md): identidades y derivadas PASS; validación
independiente del rango INCONCLUSIVE en 81 configuraciones. Estado, scripts y
resultados nuevos separados de T2-A y de los controles analíticos E16.

## E16-D — Réplica instrumental prospectiva

[E16-D](../experiments/E16/D/README.md): pesos, entradas y puntos nuevos sin
entrenamiento; 396/396 decisiones PASS_NUMERICAL y 216/216 negativos detectados.
La suma, producto y cuadrática dieron rango 2 en los 324 casos principales.
No reescribe B/C ni establece una ventaja predictiva.

## E16-E — Distancias y anisotropía

[E16-E](../experiments/E16/E/README.md): 216 comparaciones exploratorias respecto
a la suma. El rango 2 coexiste con cambios de escala y forma; 10 176 controles
numéricos pasan. Distancia entre tensores SPD, no geodésicas entre perspectivas.

## E16-F — Longitudes de caminos

[E16-F](../experiments/E16/F/README.md): 324 longitudes de tres segmentos fijados
bajo suma, producto y cuadrática. 239 PASS_NUMERICAL y 85 INCONCLUSIVE por
integración y/o comprobación global de positividad. No son distancias geodésicas.

## E16-G — Resolución numérica diagnóstica

[E16-G](../experiments/E16/G/README.md): 324/324 longitudes y 216/216 pares
validados con primitiva/cuadratura localizada y cotas Bernstein subdivididas.
Resuelve bajo G los 85 inconclusos F, sin alterar F. No es confirmación
independiente ni certificado intervalar.

## E16-H — Transferencia prospectiva del instrumento

[E16-H](../experiments/E16/H/README.md): pesos, entradas y perspectivas nuevos,
sin selección ni entrenamiento. 324/324 longitudes y 216/216 pares pasan con
el método y tolerancias G intactos. Evidencia de transferencia dentro de la
familia sintética, no de capacidad predictiva ni geodésicas.

## E16-I — Caminos quebrados acotados

[E16-I](../experiments/E16/I/README.md): 27 casos validados; 18/18 caminos
no lineales más cortos que sus rectas, nueve controles de suma sin mejora.
Búsqueda de un punto intermedio acotado, sin certificado de mínimo global.

## E16-J — Refinamiento y estacionariedad discreta

[E16-J](../experiments/E16/J/README.md): 2/4/8 puntos interiores, tres reinicios
y controles de gradiente. Estado global INCONCLUSIVE: 24/27 casos pasan, tres
no. 22 interiores estables discretamente (incluyen nueve controles), dos
limitados por frontera y tres no resueltos; no se certifican geodésicas.

## E16-K — Diagnóstico de gradiente y mallas anidadas

[E16-K](../experiments/E16/K/README.md): dos de los tres casos difíciles J pasan
el protocolo nuevo; uno sigue inconcluso por refinamiento. Los 85 reinicios
validan gradiente y SPD, con acuerdo en 15 resoluciones. K global INCONCLUSIVE;
J conserva sus resultados históricos.

## E16-L — Longitud y forma del caso pendiente

[E16-L](../experiments/E16/L/README.md): mallas anidadas 16/32/64. La longitud
cumple el umbral 0,001, pero la forma y los reinicios M32 no alcanzan el acuerdo
fijado. Global INCONCLUSIVE; 36 reinicios validan gradiente y SPD. Se conserva
figura de caminos y diferencias por nodo, sin certificar geodésicas.

## E16-M — Seguimiento de candidatos y localización

[E16-M](../experiments/E16/M/README.md): dos grupos L32 se siguen por separado
a 64/128 y coinciden numéricamente, pero persisten cambios de forma entre mallas.
El pico cerca del extremo no cumple la concentración de masa fijada. Global
INCONCLUSIVE; v1 conservada y lector de referencia corregido en v2 sin cambiar geometría.

## E16-N — Nodos graduados y Hausdorff

[E16-N](../experiments/E16/N/README.md): nodos concentrados cerca del extremo
reducen la separación de Hausdorff 64→128 de ≈0,00658 a ≈0,00185; aún supera
0,001. Nueve caminos válidos, global INCONCLUSIVE por forma y Hausdorff.
Se conservan las curvas M y se comparan 21 pares sin modificar etapas previas.

## E16-O — Indicador local y refinamiento adaptativo

[E16-O](../experiments/E16/O/README.md): cuatro bisecciones por candidato,
128→132 segmentos. Las ocho transiciones pasan longitud y Hausdorff; la forma
al mismo t y el indicador terminal no pasan. Once caminos y 1428 probes
válidos, global INCONCLUSIVE. Crecen pendientes junto a t≈0,9844; queda abierta
la sensibilidad a la representación como gráficos y a los nodos heredados.

## E16-P — Gráficos y curvas paramétricas

[E16-P](../experiments/E16/P/README.md): variantes con t fijo y t/s libres,
132/264 segmentos. Los candidatos difieren en Hausdorff ≈0,0035 y la fuente
presenta gradiente longitudinal ≈0,0031. Global INCONCLUSIVE: las cuatro
optimizaciones libres cuadráticas agotan 4800 iteraciones. Ocho de doce caminos
pasan el protocolo completo; trece salidas reproducidas exactamente.

## E16-Q — Energía y condicionamiento

[E16-Q](../experiments/E16/Q/README.md): distingue energía afín de L²/2 y
comprueba gradientes/Hessianos. El control recto pasa; los ocho candidatos
cuadráticos agotan iteraciones. Energía estacionaria no implica longitud
estacionaria. Global INCONCLUSIVE; v1 parcial y errata conservadas, quince
salidas v2 reproducidas exactamente.

## E16-R — Precondicionamiento conservando longitud

[E16-R](../experiments/E16/R/README.md): escalado diagonal diádico con el mismo
objetivo L y dominio. KKT físico pasa en 4/4 candidatos cuadráticos escalados
frente a 2/4 referencias, pero los ocho agotan 4800 iteraciones. Global
INCONCLUSIVE, con más evaluaciones para scaled. Quince salidas reproducidas;
se distinguen residuo físico, terminación y limitaciones espectrales numéricas.

## E16-S — Parada física auditada

[E16-S](../experiments/E16/S/README.md): PASS_NUMERICAL en doce caminos y
seis refinamientos. Ocho cuadráticos paran tras tres auditorías consecutivas
de KKT físico; cuatro controles terminan naturalmente. 105 auditorías sin
UNVERIFIED. Conserva banderas nativas y el INCONCLUSIVE histórico de R.

## E16-T — Segundo orden y redistribución de nodos

[E16-T](../experiments/E16/T/README.md): doce diagnósticos PASS y 488
comprobaciones. Los cuatro cuadráticos de 264 presentan curvatura negativa
contrastada por MP, casi tangencial; 132 permanece en banda casi nula.
C0 reproduce nulidad tangencial analítica. INCONCLUSIVE sobre mínimos; S intacto.

## E16-U — Descenso finito y cambio de imagen

[E16-U](../experiments/E16/U/README.md): exploratorio, diagnóstico PASS.
360 ensayos prefijados, 350 válidos y diez inviables conservados. Los cuatro
cuadráticos finos tienen cambio par negativo en full_min para los tres pasos;
los descensos a 1e-4/1e-3 cambian la imagen por encima del umbral numérico.
1.487 comprobaciones; S/T y T2-A intactos. No se certifican mínimos.

## E16-V — Transporte y nodos insertados fijos

[E16-V](../experiments/E16/V/README.md): exploratorio, diagnóstico PASS;
360 ensayos, 350 válidos y diez inviables. Subdivisiones a 1/2 y 1/4 conservan
E al transportar la misma curva; fijar nodos cambia a positivo el E de los
cuatro orígenes finos, sin eliminar descenso unilateral. 2.466 comprobaciones.
No calcula espectro refinado ni certifica convergencia. S/T/U y T2-A intactos.

## E16-W — Proyección de primer orden casi nulo

[E16-W](../experiments/E16/W/README.md): doce caminos, 144 ensayos,
140 válidos y cuatro inviables. Las ocho direcciones cuadráticas proyectadas
tienen pendiente casi nula y curvatura positiva, con aumento en ambos sentidos.
1.144 comprobaciones PASS. No calcula el mínimo restringido en g⊥ ni certifica
mínimos; S/T/U/V y T2-A intactos.

## E16-X — Mínimo del Hessiano en g⊥

[E16-X](../experiments/E16/X/README.md): diagnóstico PASS; 627
comprobaciones y 72 ensayos, dos inviables conservados. Cuatro mínimos
restringidos finos negativos, contrastados con MP, con descenso en ambos
sentidos para los tres pasos. No invalida la proyección de W ni certifica
silla exacta o mínimos; etapas anteriores y T2-A intactos.

## E16-Y — Refinamiento y masa consistente

[E16-Y](../experiments/E16/Y/README.md): 24 problemas y 559 comprobaciones
PASS. Ocho refinados cuadráticos con nuevos gradientes importantes y testigos
MP negativos; imagen y longitud conservadas. La masa permite comparar niveles,
pero no se conservó estacionariedad al ampliar variables. No certifica
estabilidad de mínimos ni convergencia; etapas previas y T2-A intactos.

## E16-Z — Reestacionarización física de mallas refinadas

[E16-Z](../experiments/E16/Z/README.md): 12/12 primer orden PASS,
12/12 diagnóstico espectral PASS, 12/12 comparaciones elegibles.
Masa fija de Y, monitor filtrado AD/MP y todos los estados conservados.
8 testigos MP negativos; no certifica mínimos. T2-A intacto.

## E16-AA — Continuación a estacionariedad más estricta

[E16-AA](../experiments/E16/AA/README.md): resultado global INCONCLUSIVE.
Ocho curvas cuadráticas agotan4800 iteraciones sin KKT≤1e-7; cuatro C0 pasan.
12/12 diagnósticos espectrales PASS y cuatro testigos MP negativos en puntos
no elegibles.370 comprobaciones PASS y ocho KKT finales INCONCLUSIVE.
No resuelve estabilidad estacionaria estricta ni certifica mínimos. T2-A intacto.

## E16-AB — Región de confianza para estacionariedad estricta

[E16-AB](../experiments/E16/AB/README.md): cinco de ocho curvas cuadráticas
alcanzan KKT≤1e-7; tres agotan60 evaluaciones y siguen INCONCLUSIVE.
Cuatro C0 INITIAL_CONTROL,9/12 comparaciones elegibles y12/12 espectros PASS.
Cuatro testigos MP negativos elegibles en las mallas528; no certifica sillas
exactas o mínimos.756 comprobaciones PASS y tres KKT inconclusos. T2-A intacto.

## E16-AC — Índice de Morse por campos de Jacobi

[E16-AC](../experiments/E16/AC/README.md): INCONCLUSIVE; v2 VALID_EXPLORATORY, v1 INVALID preservada.
12 índices continuos 0 estables y 8/8 controles PASS; faltan bloques normales
y tangencialidad de Z/AB, por lo que no se establece H2 por regla.
[Conclusión oficial](../experiments/E16/AC/CONCLUSION.md).

## E16-AD — Bloques discretos y carta normal

[E16-AD](../experiments/E16/AD/README.md): INCONCLUSIVE. Suma, producto y cuadrática tienen K≡0 en región
regular SPD; bloques normales positivos y cociente sin negativas admisibles.
12/12 controles PASS; los tres LIBRE cuadráticos no cumplen la ruta de
estacionariedad. H2 respaldada en sustancia, no establecida por regla.
[Conclusión oficial](../experiments/E16/AD/CONCLUSION.md).

## E16-AE — Conjugados en la familia no plana tipo E12

[E16-AE](../experiments/E16/AE/README.md): Q1/Q2/Q3 INCONCLUSIVE, corrida VALID_EXPLORATORY.
K∈[−6.6438350978,+0.0465519012] en la malla, mayormente negativa;
todos los rayos censurados, sin conjugados ni cruces observados antes de censura.
r_deg y A(r_deg) UNKNOWN; no se validó el salto de índice ni el locus de corte.
[Conclusión oficial](../experiments/E16/AE/CONCLUSION.md).

## E16-AF — Degeneración del disco en estados sintéticos de la familia T2

[E16-AF](../experiments/E16/AF/README.md): Q1 PASS, Q2 INCONCLUSIVE, Q3 PASS exploratorio, Q4 FAIL.
40 estados nuevos: cinco eventos conjugado+colisión operacional y 35 censurados;
20/20 controles PASS. El rayo prefijado no permite validar Morse. Desconocidos
de área/radio 0/40→0/40: no se reprodujo la patología motivadora ni hubo escapes
en la rejilla. Sin transferencia a datos T2.
[Conclusión oficial](../experiments/E16/AF/CONCLUSION.md).

[Síntesis S–AD](../experiments/E16/SINTESIS_S_AD.md) ·
[Síntesis AC–AF y preguntas abiertas](../experiments/E16/SINTESIS_AC_AF.md).
