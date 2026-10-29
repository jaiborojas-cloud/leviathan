# Revisión de la primaria de C1: ¿hace falta una base robusta? (2026-10-29)

**Tipo:** revisión metodológica **EXPLORATORIA**, pedida por el responsable el 2026-10-29 («Revisar si la primaria…») después de F1 de CIFAR. **No cambia ningún veredicto:** C1 PASS, C2 PASS y CIFAR F1 PASS_DESCRIPTIVO siguen como se congelaron. Tampoco define todavía una primaria nueva; eso requiere un diseño congelado y auditado antes de nuevos datos.

## 1. Motivo
En CIFAR F1, una trayectoria que no aprendió (`cifar_f1_s0009_k0`, con precisión de entrenamiento de 0.33) quedó a z = −12.9 en L = log ρ(10). La base cúbica, fuera de muestra, extrapola z³, y esa sola trayectoria aportó el 80 % de la mejora (D = 0.46). Ver [RESULTADO_F1](../CIFAR/F1/resultado/RESULTADO_F1_2026-10-29.md).

## 2. Qué se comparó
Cuatro bases de L. Ninguna usa Y, y todo lo demás es igual a la primaria de C1: centrado dentro del split, 10 bloques (260010) y permutación de X dentro del split (260001), con **2000** permutaciones en vez de 5000.
- **cúbica:** la original de C1, con z de toda la muestra.
- **cúbica recortada:** igual, pero en el bloque de prueba z se recorta al rango de z del entrenamiento, así que no extrapola. Es el cambio mínimo.
- **spline natural:** spline cúbico restringido con 4 nudos en los cuantiles 5, 35, 65 y 95 % de L del entrenamiento, lineal en las colas.
- **cúbica sobre rangos:** z = puntajes normales del rango de L, lo que acota la palanca.

Para cada base se reportan:
- el D y su p;
- la fracción de la mejora (SSE_base − SSE_completo) que aporta la observación más influyente;
- D sin esa observación.

Cohortes: las tablas publicadas de C1 (780), C2 (1000) y CIFAR F1 (500), con los splits que tienen al menos 3 trayectorias.

Scripts: [sensibilidad_bases.py](sensibilidad_bases.py) y [sensibilidad_sin_s0009_k0.py](sensibilidad_sin_s0009_k0.py). Salidas: [sensibilidad_bases.json](sensibilidad_bases.json) y [cifar_sin_s0009_k0.json](cifar_sin_s0009_k0.json). Las rutas de los scripts se hicieron relativas al repositorio después de ejecutarlos, con la lógica idéntica. Se corrieron en el contenedor (numpy 2.5.3, scipy 1.18.1), no con las versiones fijadas.

## 3. Resultados
| cohorte | base | D | p (2000) | peso de la obs. más influyente | D sin ella |
|---|---|---|---|---|---|
| **C1** (\|z_L\| máx 3.0) | cúbica | 0.0256 | 0.0005 | 20 % | 0.0195 |
| | recortada | 0.0258 | 0.0005 | 20 % | 0.0197 |
| | spline natural | 0.0265 | 0.0005 | 20 % | 0.0204 |
| | rangos | 0.0252 | 0.0005 | 21 % | 0.0192 |
| **C2** (\|z_L\| máx 3.5) | cúbica | 0.0295 | 0.0005 | 7 % | 0.0272 |
| | recortada | 0.0296 | 0.0005 | 7 % | 0.0273 |
| | spline natural | 0.0294 | 0.0005 | 7 % | 0.0271 |
| | rangos | 0.0295 | 0.0005 | 7 % | 0.0272 |
| **CIFAR F1** (\|z_L\| máx 12.9) | cúbica | 0.460 | 0.0005 | **80 %** | 0.0039 |
| | recortada | 0.0089 | 0.016 | 30 % | 0.0064 |
| | spline natural | 0.0148 | 0.008 | 47 % | 0.0055 |
| | rangos | 0.0117 | 0.010 | 27 % | 0.0077 |

**CIFAR F1 sin `s0009_k0`** (499 trayectorias):

| base | D | p (2000) | peso de la obs. más influyente |
|---|---|---|---|
| cúbica | 0.0039 | 0.068 | 49 % |
| recortada | 0.0045 | 0.062 | 43 % |
| spline natural | 0.0055 | 0.045 | 42 % |
| rangos | 0.0077 | 0.025 | 31 % |

## 4. Lectura
1. **Wine (C1 y C2) no depende de la base.** Las cuatro dan el mismo D (diferencias ≤ 0.001) y la misma p, y ninguna observación domina: 20 % en C1 y 7 % en C2. Las confirmaciones no son un artefacto de palanca.
2. **En CIFAR la base cúbica es patológica,** porque no protege contra una L extrema. Con cualquiera de las bases robustas D cae a 0.009–0.015.
3. **La señal residual en CIFAR es pequeña y frágil.** Sin la trayectoria que no aprendió, D queda entre 0.004 y 0.008 según la base, con p entre 0.025 y 0.068. Además, una sola observación sigue aportando del 31 al 49 % de la mejora. Es del orden de una cuarta parte del D de Wine y no es robusta. **No hay base aquí para afirmar ni descartar la señal en CIFAR-3.** Además, estas variantes se miraron después de ver F1, así que no pueden servir para adjudicarlo.

## 5. Propuesta para la próxima primaria
Para congelar con el otro agente **antes** de cualquier dato nuevo:
1. **Criterio de entrenamiento fallido, fijado de antemano:** una trayectoria con precisión de entrenamiento final menor que 0.5, que es claramente azar con 3 clases, cuenta como **faltante por motivo «no aprendió»**. Se reporta y entra en el umbral del 5 %. En CIFAR F1 lo cumple solo `s0009_k0`; la siguiente más baja está en 0.77, y en Wine no hay casos. Hay que fijar el umbral sin mirar más datos.
2. **Base sin extrapolación:**
   - **Recomendada: la cúbica recortada.** Es el cambio mínimo: dentro del rango observado es idéntica a la de C1 (Wine da el mismo D) y fuera de él no extrapola.
   - **Alternativa: rangos,** que acota más la palanca. En CIFAR fue la de menor peso de una sola observación.
3. **Compuerta de influencia, también predeclarada:** reportar siempre la fracción de la mejora que aporta la observación más influyente y el D sin ella. Por ejemplo: PASS exige además que D sin la observación más influyente sea > 0, o, si se prefiere solo descriptivo, que lo reporte sin decidir.
4. **Alcance:** solo para diseños nuevos (un F2 de CIFAR, otras familias). C1, C2 y CIFAR F1 conservan sus primarias y sus veredictos.

## 6. Decisión pendiente del responsable
- ¿Se adopta la propuesta del §5 (criterio de entrenamiento fallido, base recortada o de rangos, compuerta de influencia) como primaria para los diseños nuevos?
- Con esa primaria, ¿se hace un F2 de CIFAR? El efecto plausible sería D ≈ 0.005–0.01, así que la potencia exigiría una muestra mucho mayor que 500.
- ¿O se cierra CIFAR-3 como «señal no detectable con robustez en descubrimiento»?
