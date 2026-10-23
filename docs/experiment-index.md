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
