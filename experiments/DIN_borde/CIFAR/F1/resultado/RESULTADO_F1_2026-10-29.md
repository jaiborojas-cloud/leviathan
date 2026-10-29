# DIN-CIFAR F1 — resultado del descubrimiento (2026-10-29)

**Veredicto oficial (regla congelada): PASS_DESCRIPTIVO.** Lo produjo el analista congelado `analisis_F1_v2.py` (`0c4d03b5…`) con el plan congelado (`4347857e…`). Nada de lo que sigue lo modifica.

**Pero un diagnóstico exploratorio posterior (§4) muestra que el PASS lo produce casi entero una sola trayectoria que no aprendió.** Sin ella, D = 0.004 y p = 0.062. Por eso este PASS **no** se interpreta como evidencia de señal temprana en CIFAR-3, ni como base para dimensionar F2.

## 1. Corrida e integridad
- **Productor:** `productor_F1.py` (`c74add73…`, publicado antes de medir), ejecutado en el equipo del responsable con las versiones fijadas (`permitir_versiones = false`). Tardó 1394 s con 12 procesos, con una mediana de 26.4 s de CPU por trayectoria y 741 MB por proceso.
- **Estados:** **500 de 500 trayectorias y 2000 de 2000 visitas MEDIDA.** Ninguna fallida ni con ρ inválida, y ningún corte por el límite de 120 s.
- **Archivos publicados aquí** (copias de los que entregó el responsable):

| archivo | SHA-256 |
|---|---|
| [cifar_f1_visitas.csv](cifar_f1_visitas.csv) | `34bb7503a953c9c9b9b2a61cdd34a462a2e548144e4c7665eeed309666de4934` |
| [RESUMEN_F1.json](RESUMEN_F1.json) | `74d97184b8d7f09e7b686467c206d183aa98e123f41de70bb079d4034d038336` |
| [RESULTADO_CIFAR_F1.json](RESULTADO_CIFAR_F1.json) | `9473152f3f6157f26c46c6cd1310ff043e2d59817059e46bffc9204cdb40cce9` |

- **Enlaces registrados por el analista:** tabla `34bb7503…`, plan `4347857e…`, productor `c74add73…`, compuerta `2d42fb16…` y dataset `6d958be0…`. Coinciden con los del resumen del productor. No hubo motivos de INCONCLUSIVE y faltaron 0 trayectorias.
- Los arrays, pesos y resultados de ρ completos se quedan en `D:\RIPG_DATA\DIN_CIFAR_F1\corrida\`, fuera de Git.

## 2. Primaria (congelada)
X = X10, L = log ρ_caras(10), Y = log ρ_caras(250), con base cúbica, bloques 260010 y 5000 permutaciones con semilla 260001:

| D | p | percentil 95 del nulo | pendiente de X |
|---|---|---|---|
| **0.460** | **0.0002** (1/5001) | 0.102 | 0.708 |

## 3. Secundarios (predeclarados, sin p)
| secundario | estado | D | pendiente | n / splits |
|---|---|---|---|---|
| ρ_vert | DESCRIPTIVO | 0.050 | 0.44 | 500 / 100 |
| base de grado 5 | DESCRIPTIVO | −0.350 | 0.67 | 500 / 100 |
| X5 | DESCRIPTIVO | 0.037 | 0.49 | 500 / 100 |
| X30 | DESCRIPTIVO | 0.050 | 0.40 | 500 / 100 |
| splits pares | DESCRIPTIVO | −0.006 | 0.26 | 250 / 50 |
| splits impares | DESCRIPTIVO | 0.534 | 1.20 | 250 / 50 |
| estrato bajo de c (mediana < 0.4) | NO_DEFINIDO | — | — | 11 splits |
| estrato intermedio de c | DESCRIPTIVO | 0.004 | 0.86 | 83 splits |
| estrato alto de c (≥ 0.8) | NO_DEFINIDO | — | — | 6 splits |

- **Variación dentro del split** (raíz del cuadrado medio, centrada): X 0.060, L 0.112 e Y 0.419.
- **Relación con c:** solo quedó definido el estrato intermedio, así que F1 **no informa** sobre la relación de la señal con c.

## 4. Diagnóstico de influencia — EXPLORATORIO
Script: [diagnostico_influencia.py](diagnostico_exploratorio/diagnostico_influencia.py). Salida: [diagnostico_influencia.json](diagnostico_exploratorio/diagnostico_influencia.json). Usa las funciones del analista congelado sobre la tabla publicada, después del veredicto, y no lo cambia.

- **Una trayectoria aporta el 80 % de la mejora fuera de muestra, y cinco aportan el 99.9 %.** El bloque 9 tiene un SSE de la base de 1150, frente a 6–12 en los otros nueve. La ganancia total es de 564, y 563 salen de ese bloque.
- **La trayectoria es `cifar_f1_s0009_k0`, y no aprendió:**
  - su precisión de entrenamiento es 0.34 y la del panel 0.33, es decir, azar, en todas las visitas;
  - su c es de 0.04 y su q de 0.96 en u250.
  
  Su log ρ_caras(10) = −0.32, mientras que el resto va de 1.05 a 1.97, así que queda a **z = −12.9** en la estandarización de la base cúbica. Cuando su bloque queda fuera, la base cúbica extrapola z³ ≈ −2160. El error resultante es enorme, y añadir X lo amortigua. **D = 0.46 es un artefacto de palanca de la base cúbica, no una señal de X10.**
- **Sensibilidad sin esa trayectoria** (exploratoria, no es el veredicto): D = 0.0039, p = 0.062, percentil 95 del nulo 0.0048, pendiente 0.65, n = 499. Es coherente con X5, X30, ρ_vert y el estrato intermedio: un efecto típico muy pequeño, que en esta muestra no se distingue del nulo.
- **Quitar un split cada vez** da D entre −0.69 y 0.68. Quitar un split cambia además la asignación de bloques, y con eso también cambia qué bloque se lleva la trayectoria extrema. El D global es inestable.
- **Comparación con Wine:** en C1 el |z| máximo de L es 3.0, y en C2 es 3.5. Sus resultados no tienen esta palanca extrema.

## 5. Lectura
1. **El veredicto congelado se conserva:** F1 = PASS_DESCRIPTIVO. No se reclasifica ni se excluye la trayectoria del resultado oficial.
2. **Como descubrimiento, F1 no muestra señal temprana en CIFAR-3.** Sin la trayectoria degenerada, D ≈ 0.004 con p = 0.06, y los secundarios dan D de 0.04–0.05 sin p.
3. **Hay una lección para el método,** que tampoco es un resultado sobre la señal. La primaria de C1 no protege contra una trayectoria que no entrena: su L extremo domina la base cúbica fuera de muestra. El diseño de F1 prohibió filtrar por precisión, para no seleccionar después de ver los datos, y eso fue correcto para F1. **Cualquier F2 o rediseño debe declarar de antemano** cómo se trata una trayectoria que no aprende (por ejemplo, un criterio de entrenamiento fallido fijado antes de los datos) o qué base resiste la palanca. No hay que decidirlo viendo F1.
4. **No se propone F2 global con D = 0.46.** Si se decide un F2, su efecto objetivo debería ser del orden de D ≈ 0.004–0.05, y la potencia podría exigir una muestra muy grande. Lo decide el responsable con el otro agente.
