# Resultado de E16-AA

**INCONCLUSIVE para estacionariedad a KKT≤1e-7.** Las ocho curvas cuadráticas
agotan4800 iteraciones, con success=False/status1 conservados, sin alcanzar
el umbral. Los cuatro controles C0 pasan con0 iteraciones. No se amplió el
presupuesto ni se seleccionaron estados anteriores.

La sensibilidad espectral en soluciones cuadráticas que cumplan1e-7 queda
sin resolver. El resultado no contradice Z: su umbral era1e-5. Tampoco prueba
que no existan soluciones más estacionarias o que otro método no las encuentre.

## Todos los puntos devueltos

| Fuente S | Segmentos AA | KKT final | Mínimo masa fijo | Testigo MP negativo | Primer orden |
|---|---:|---:|---:|---|---|
| Q0/reference/132 | 264 | 1.32966e-06 | 7.4610987e-05 | No | INCONCLUSIVE |
| Q0/reference/264 | 528 | 3.02219e-06 | -0.01583671 | Sí | INCONCLUSIVE |
| Q0/scaled/132 | 264 | 2.62303e-06 | 4.7555879e-05 | No | INCONCLUSIVE |
| Q0/scaled/264 | 528 | 3.93737e-06 | -0.010520932 | Sí | INCONCLUSIVE |
| Q1/reference/132 | 264 | 7.84993e-06 | 6.2327597e-05 | No | INCONCLUSIVE |
| Q1/reference/264 | 528 | 5.92893e-06 | -0.0025410222 | Sí | INCONCLUSIVE |
| Q1/scaled/132 | 264 | 2.40177e-06 | 5.55718e-05 | No | INCONCLUSIVE |
| Q1/scaled/264 | 528 | 3.02168e-06 | -0.0087934642 | Sí | INCONCLUSIVE |
| C0/reference/132 | 264 | 2.94245e-36 | -3.1879707e-07 | No | PASS |
| C0/reference/264 | 528 | 1.17698e-35 | -2.5389269e-06 | No | PASS |
| C0/scaled/132 | 264 | 2.94245e-36 | -3.1879707e-07 | No | PASS |
| C0/scaled/264 | 528 | 1.17698e-35 | -2.5389269e-06 | No | PASS |

12/12 diagnósticos espectrales PASS. Cuatro testigos MP negativos corresponden
a las curvas cuadráticas de528 segmentos; los cuatro mínimos de264 segmentos
son positivos numéricamente. Esto describe puntos no elegibles, no desaparición
o persistencia de sillas estacionarias. La clasificación float usa un umbral
relativo distinto del testigo direccional MP; consultar [teoría](THEORY.md).
Los cuatro C0 conservan curvatura MP casi nula, sin testigos negativos, aunque
sus mínimos float sean ligeramente negativos. Sólo esos controles resultan
elegibles (4/12); no sustituyen los casos cuadráticos inconclusos.

## Controles y costes

378 comprobaciones:370 PASS y8 INCONCLUSIVE, exactamente los ocho KKT finales
cuadráticos. Todos los gradientes y diagnósticos restantes pasan.204 monitores:
192 descartes AD SCREENED_NONSTATIONARY y12 auditorías MP iniciales; no hay
monitores UNVERIFIED ni rachas de parada. Los descartes AD no son auditorías MP.
Los gradientes finales se auditan por separado y sus componentes se archivan.
Todos los puntos permanecen interiores y las pruebas bilaterales son factibles;
no hubo aristas nulas ni primitivas inválidas rechazadas.

Primera corrida: 251.705298s, 202.664062MiB; presupuesto1800s/512MiB respetado.

Las ocho longitudes cuadráticas disminuyen; KKT mejora en cuatro casos y
empeora en cuatro. Sus residuos finales van de1.33e-6 a7.85e-6, todos por
encima de1e-7. No hay mejora monótona entre Z y AA. La comparación conserva masa fija por fuente,
sin comparar normalizaciones entre procedencias distintas. C0 reproduce el
mismo punto inicial. No son doce réplicas independientes ni datos nuevos.

Se conservan9480 componentes de gradiente,4764 vértices,9472 autovalores
restringidos y24 auditorías direccionales MP. Ninguna matriz densa ni autovector
se archiva.

## Límites y siguiente pregunta

No hay certificado de mínimo, silla exacta, geodésica ni convergencia.
La continuación cambió inicio, ftol, gtol y criterio; no aísla una causa única.
Antes de interpretar el espectro como estabilidad estacionaria estricta,
procede diseñar un método que trate las direcciones mal condicionadas y
controle explícitamente el residuo físico, bajo un protocolo prospectivo nuevo.
Aumentar retrospectivamente iteraciones o relajar el umbral no resuelve AA.

[Tablas completas](results/run_v1) · [comparación gráfica](figures/tolerance_comparison.svg)

## Reproducción e integridad

PASS_REPRODUCTION: once salidas científicas idénticas byte a byte en una
repetición de255.124747s, dentro del presupuesto. Se reconstruyeron rachas,
KKT, hashes, costes, elegibilidad y espectros; etapas previas/T2-A intactas.
La reproducción verifica integridad; el resultado científico sigue INCONCLUSIVE.
[Registro de verificación](verification.json).
