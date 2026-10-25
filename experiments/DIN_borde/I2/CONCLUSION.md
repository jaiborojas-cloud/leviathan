# DIN-I2 · conclusión exploratoria

La versión pública **r3** distingue `rho_vert` de `rho_caras`, incorpora caras
completas y pasó la validación fijada en302 estados, sin eliminar ninguno.
No se cambia ningún estado anterior. [Resumen ejecutable](results/run_r3/summary.json),
[tabla por estado](results/run_r3/states.csv), [884 comprobaciones](results/run_r3/validation.json).

| Pregunta | Veredicto oficial I2 | Alcance |
|---|---|---|
| I1 teoría | PASS | Partición de direcciones y límite unilateral demostrados;10 controles PASS. |
| I2 corrección | PASS |153 referencias exactas D2,27 fórmulas coordenadas MP,40 triángulos AG,16 rayos G1,24 sensibilidades y4 contrastes MP. |
| I3 compatibilidad literal | PASS |66 casos D2 elegibles; ningún triángulo AG satisface la premisa de que el v1 literal acertó. No es compatibilidad universal. |
| I4 coste | PASS_DESCRIPTIVE |102 pares: mediana v2=.264s, p95=.484s, mediana v1=4.463s; mediana v2/v1=.0607. |
| I5 recomendación | PASS_DESCRIPTIVE |Usar rho_caras para todas las semirrectas; conservar rho_vert como desenlace genérico explícito. Decide el responsable. |

## Demostración y referencias conocidas

La [teoría](THEORY.md) establece, sin asumir continuidad angular,

    inf_todas L = min(inf_conos_abiertos L, min_aristas L(normal)).
    lim_e→0+ L(normal+e·tangente) = L(normal)+L_cola_en_cara.

La normal es estrictamente menor que ese límite cuando la cola tiene longitud
positiva. La cuerda positiva es suficiente; para una cola nula hace falta que
M anule todas sus velocidades. Una cuerda cero por sí sola no basta en una
cara con más de dos posiciones. La ventaja local no asegura ganar frente a
otros conos. Se incluyen todos los índices exactamente colineales, no sólo
los extremos de la arista; duplicados se agrupan con su multiplicidad.

En los27 modos coordenados D2 se recupera
`min(1/n,1/m_k−1/n)`. En mass_face, k=0 o13 pertenece a una cara de26 índices:
`rho_vert≈1/27=.037037037037`, `rho_caras≈1/702=.001424501425`, factor26.
Los57 casos D2 sin mínimo global exacto conocido siguen sin tenerlo certificado:
respetar sus rayos testigo no convierte esas cotas en respuestas exactas.

Los40 triángulos AG tienen tres grupos iguales: se recuperan en MP las cuerdas
analíticas hacia vértices y puntos medios de arista, con `rho_caras=rho_vert/2`.
En todos se cumple `d_borde≤rho_caras`; NO se afirma igualdad con d_borde.
La cota por caminos quebrados de AH tampoco es el objetivo de este instrumento.

## Evidencia por grupo y comparación con v1

| Grupo | Estados | Ganador cara | Mediana rho_caras/rho_vert | Mediana rho_caras/v1 | Mediana v2(s) |
|---|---:|---:|---:|---:|---:|
| D2 gaussian |51|8|1.000000|1.000000|.428|
| D2 interior |51|16|1.000000|.999823|.386|
| D2 near_collinear |51|8|1.000000|.993304|.444|
| D2 mass_face |57|36|.546909|.383602|.157|
| AG triángulos |40|40|.500000|.169029|.101|
| AF sintéticos archivados en AG |40|24|.977798|.977798|.295|
| D2b |8|7|.705729|.705729|.285|
| G1 Iris |4|3|.982028|.982028|.335|

Ratios sobre denominadores positivos; los nulos no se convierten en cocientes.
Empates numéricos pueden etiquetar un ganador cara sin reducción significativa.
La columna v1 mezcla102 mediciones contemporáneas1440/800 explícitamente
etiquetadas y200 resultados históricos archivados. Sus tiempos NO se mezclan:
el benchmark de coste usa sólo los102 pares contemporáneos. En r2/r3 se
reutilizan esos mismos comparadores, medidos en esta sesión con dos procesos,
BLAS1 y la misma cuota CPU. Los tiempos de sensibilidad y MP se separan del
coste del instrumento. Corrida r3 completa:71.57s de pared, en este entorno.

**I3 tiene un alcance condicionado.** Los66 casos D2 gaussian/interior con
referencia exacta y v1 archivado correcto pasan la tolerancia literal.
En los40 AF sintéticos `rho_vert/v1∈[1.00000000002,1.00004472]`, compatible
numéricamente, pero no prueba que ninguno sea un mínimo global conocido.
En los40 triángulos el v1 d8ec69f8 contemporáneo NO acertó: `rho_caras/v1`
va de.09149 a.24522. El rho archivado en AG procedía de un escáner propio
que incorporaba aristas; no se lo presenta como salida del v1 literal.
Por teoría, comparar ese valor correcto de cara con rho_vert daría factor2;
por eso sería erróneo prometer compatibilidad entre objetos diferentes.

En el testigo Iris **P60_s02_k0_u010**, v1 contemporáneo=3.260982450355,
rho_vert=2.249355970490 y **rho_caras=1.950687531203**, cara completa[6,16].
Es menor que el rayo axial(-1,0) conocido=2.192027830216 y que el nativo
histórico720/400=3.226441740959. Ganar a ese testigo es validación de una
cota, no prueba de óptimo global. La dirección racional exacta y todas las
otras caras están en [estado301](results/run_r3/states/301.json).

## Versiones, fallos y verificación

El diseño0927faa precedió al código a105dbe. Se conservan las tres corridas:

- [r1](results/run_v1/summary.json): I2 FAIL, seis comprobaciones fallidas por
  cúspides no resueltas en gaussian/near_collinear random_rank1. Diez controles
  PASS. Fallo adicional de impresión NumPy documentado en su salida.
- [r2](results/run_r2/summary.json): I2/I3/I4 INCONCLUSIVE por seis excepciones
  de brackets inconsistentes por redondeo; los demás contrastes sin fallos.
- [r3](results/run_r3/summary.json):302/302 numéricos,884/884 comprobaciones PASS,
  24 sensibilidades y4 referencias MP80. Diferencia MP32/64 máxima7.73e-18.

Las enmiendas [serialización](AMENDMENT_v2_FROZEN.md),
[cúspides](AMENDMENT_r2_FROZEN.md) y [brackets](AMENDMENT_r3_FROZEN.md)
se congelaron antes de corregir. r1 y r2 del instrumento se preservan bit a bit.
No se relajó ninguna tolerancia ni se seleccionaron supervivientes.

[verification.json](verification.json) verifica1693 caras completas mediante
sus direcciones racionales, los906 archivos de estado de las tres corridas,
SHA de arrays, fuentes intactas y alcance exclusivo I2. Nueve brackets de
redondeo quedan registrados en rayos finales r3; cero avisos quad en esos rayos.
No se leyó Wine, datos T2 ni DIN-C1; sólo sus dos instrumentos fuente permitidos.
No se abrió el informe C1 de PR81: las cifras citadas por el usuario no se
toman como evidencia auditada aquí. geometry b4d1e0e4 y v1 d8ec69f8 intactos;
no se importó core ni se entrenó ninguna red.

## Límites y preguntas abiertas

Son estimaciones flotantes exploratorias, sin intervalos ni certificado de
mínimo global por cono. Los restos al infinito son explícitos, pero su evaluación,
quad y la corrección PSD son numéricos. Las raíces se detectan por cambios de
signo y no tienen certificado de exhaustividad. Los arrays fuente y propios
quedan fuera de Git con SHA; sin ellos no se garantiza reproducción autónoma.

La membresía exacta usa los racionales binarios representados por f; el umbral
1e-10 sólo alerta de casi caras y no las fusiona. Un modelo que interprete
esos casi empates como exactos define otro desenlace y requiere otro protocolo.
No se afirma transferencia a Wine/T2/C1 ni se recomienda cambiar retrospectivamente
estudios en curso. Queda abierta una auditoría independiente con aislamiento
certificado de raíces/óptimos y un estudio futuro que declare qué desenlace usa.
