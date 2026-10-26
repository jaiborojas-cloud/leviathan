# DIN-D9g-c — conclusión exploratoria

**REDUNDANTE_EXPLORATORIO según la regla congelada. Proponer Q13 al responsable.**
En s=.8, BR supera el control de adecuación y es la base de lectura. El componente
de c30 fuera del diccionario barato no añade predicción: **D=−.004952, p=.653**.
C2 no se usa y permanece reservada; no se ejecuta Q13 ni un confirmatorio aquí.

## Primaria: adecuación y lectura en s=.8

| Modelo | D_base sola | D adicional c30 | p (999 permutaciones) | β residual |
|---|---:|---:|---:|---:|
|B1 lineal, referencia|.075126|.021854|.001|−.040886|
|BR ridge anidado, lectura|.071646|−.004952|.653|−.054354|

D_base(B1)−D_base(BR)=**.003479**, menor que el margen permitido **.005**:
BR es adecuada por la regla prefijada, aunque no predice mejor que B1. La holgura
respecto al límite es .001521. No se cambió el umbral después del resultado.
El ridge mejora claramente sobre B4 no regularizada de D9g-b (D_base≈.011801),
recuperando gran parte de su rendimiento; no se afirma que supere la base lineal.

La lectura no elige el modelo con p más favorable. B1 conserva el incremento
conocido, pero no decide cuando BR satisface la compuerta. B1 reproduce el D
anterior con error≤4.45e-16 en los cuatro conjuntos. Su nueva p usa otra semilla
fijada y999permutaciones, resolución .001; no se exige igualdad con la p anterior.

## Qué candidato se probó y qué significa «redundante»

Antes del diseño, el responsable eligió **residualizar c30 por OLS del diccionario
completo de21términos, sólo en entrenamiento, y añadir ese residuo sin penalizar**.
Esto evita que una función barata ya contenida en la base eluda la penalización
ridge. No es el ajuste de c30 cruda sin penalizar al ridge conjunto.

El D negativo es una lectura predictiva operacional, no una identidad algebraica:
c30 NO es exactamente una función lineal del diccionario. En el ajuste completo,
la norma del residuo conserva≈46.7% de la norma de c30 centrada. No se demuestra
independencia condicional, ausencia exacta de efecto, equivalencia estadística,
causa única ni información nula frente a toda función de las medidas baratas.
La proyección OLS del candidato puede añadir variabilidad y no está regularizada.

## Mitades y regularización

| Mitad, BR | D adicional | β residual | D_base | λ descriptivo completo de mitad |
|---|---:|---:|---:|---:|
|splits pares|−.032183|−.058812|.101800|.562341|
|splits impares|−.031409|−.041257|−.011137|3.162278|

Las pendientes mantienen signo negativo, pero ambas mitades tienen D adicional
negativo. El rendimiento de la base sigue siendo variable entre mitades. Se usó
BR en ambas porque es la clase de lectura del completo; λ y transformaciones
se volvieron a ajustar dentro de cada mitad, sin usar el λ del completo.

λ externo por bloque0..9 en s=.8:
`.562341, .562341, .562341, .316228, 1.778279, 1, .562341, 1, .562341, 1`.
No se eligió un extremo de la rejilla. Objetivo ridge:
`MSE_train + λ ||β_barata||²`, con33λ de1e-4 a1e4. Elección mediante5bloques
internos por splits, dentro de cada uno de los10bloques externos. Media/escala y
polinomios también se ajustaron en cada entrenamiento interno/externo.

## Los otros conjuntos son descriptivos

| Conjunto | D_base B1 | D_base BR | Base de lectura | D de lectura | p de lectura | Lectura descriptiva |
|---|---:|---:|---|---:|---:|---|
|s=.25|.084219|.110844|BR|.004465|.048|NO_CONCLUYENTE|
|s=.5|.107150|.146848|BR|−.012154|.960|REDUNDANTE|
|s=.8, decide|.075126|.071646|BR|−.004952|.653|REDUNDANTE|
|agregado|.083308|.076264|B1|.021345|.001|ROBUSTO por respaldo B1|

En el agregado BR es peor que B1 por .007044>.005, por eso la regla lee B1. Ese
«ROBUSTO» descriptivo no demuestra robustez a una base flexible adecuada y no
rescata la decisión de s=.8. Se mantiene el emparejamiento por split de todos los
niveles, centrando/permutando en (nivel,split). No se trataron300paneles como300splits.

## Pipeline completo y controles

- **999permutaciones**, resolución p=.001, seed340001. En cada repetición se
  recalcularon los33scores internos/argmin de λ, proyección de c permutada, gamma,
  predicciones/SSE y elección B1/BR. Se guardan10.000llamadas externas por conjunto.
  λ depende sólo de medidas baratas/Y train: sus elecciones y la compuerta de
  adecuación fueron idénticas entre permutaciones, como debían ser. No se fijó un
  λ elegido con c observada. Se cachean sólo transformaciones/SVD invariantes a c.
- **Sin caché:** selección observada y primeras2permutaciones de cada bloque en
  control numérico, mismas elecciones; error relativo máximo de scores2.71e-15.
- **Pipeline directo:** todos los1.000D frente al cálculo vectorizado, error máximo
  7.78e-16 y p idéntica, incluido reajuste de λ y base de lectura.
- **Negativos no lineales:** c=q0² y c=q1q2 con Y dependiente de c. D_BR=0 en ambos,
  alias en10/10bloques. El cero resulta del componente fuera del diccionario elegido;
  no es una prueba universal de calibración ni de que ridge crudo sea invariante a duplicados.
- **Positivo grande**, D_oráculo=.20: D_BR=.147151,p=.001, pendiente positiva estable.
- **Positivo pequeño**, D_oráculo=.02: D_BR=.029237,p=.001, pendiente positiva estable;
  detectado en la realización fijada. Es UNA realización: no estima potencia≥.8
  ni garantiza detectar cualquier efecto real de .02. El D_oráculo no es el D_CV finito.
- [verification.json](verification.json): **PASS**,1.500filas,4conjuntos,9arrays
  externos por SHA, fuentes congeladas intactas. No hubo fallos ni enmiendas de implementación.

## Decisión propuesta y límites

Con la regla anticipada, **proponer Q13**, no el confirmatorio de c30 en C2. El
responsable decide y autoriza el siguiente trabajo; no se implementa aquí. Esta
etapa es la última prueba de descubrimiento solicitada sobre estos datos para esta
decisión: no se buscan otra rejilla, diccionario, penalización o semilla después.

«Redundante» significa que no añade mejora de CV a BR bajo el estimando elegido
y el control de adecuación, no que se haya probado el nulo o una causa. El efecto
podría ser pequeño o depender de otra representación; no se explora aquí. La
cercanía de la compuerta de adecuación y la variabilidad de las mitades quedan visibles.
Las identidades de M no implican esta lectura empírica de generalización.

No se regeneró test, reentrenó, reevaluó red/test ni midió geometría. Se importaron
D9g/D9g-b por SHA sin modificar etapas/instrumentos. No se leyeron Wine/Iris/T2/
DIN-C1 ni cohorte/estados/checkpoints/asociaciones C2. La prueba es exploratoria,
sin afirmación confirmatoria, causal o de transferencia. El centrado del desenlace
usa media final del grupo, como D9g: no predictor desplegable sin esa información.

[Diseño](DESIGN_FROZEN.md) · [decisión del candidato](DECISION_CANDIDATO.md) ·
[8 estimaciones](results/run_v1/estimates.csv) · [análisis completo](results/run_v1/analysis.json) ·
[controles](results/run_v1/controls.json) · [teoría](THEORY.md) · [reproducción](REPRODUCCION.md).
