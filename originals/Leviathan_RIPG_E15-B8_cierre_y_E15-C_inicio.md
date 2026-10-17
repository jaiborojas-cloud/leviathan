# Leviathan / RIPG — cierre E15-B7/B8 y siguiente paso
**Fecha:** 24 septiembre 2026

## E15-B7 — validación externa del protocolo mesh-independent

### Integridad
- 28/28 archivos del manifest verificados.
- 16/16 checkpoints verificados.
- Semillas, observables, integrador y umbrales preservados.

### Casos auditados
1. split 5 true
2. split 6 random

### Resultados

#### split 5 true
\[
\operatorname{median}(C_A)=36.75316178
\]

Dispersión multifuente:
\[
\boxed{0.001315918\%}
\]

Clasificación:
\[
\boxed{\text{PASS}}
\]

#### split 6 random
\[
\operatorname{median}(C_A)=2.661827025\times10^{-6}
\]

Dispersión multifuente:
\[
\boxed{0.0000004243\%}
\]

Clasificación:
\[
\boxed{\text{PASS}}
\]

En ambos casos:
- convergencia interna en las seis fuentes;
- cinco compuertas de concentración aprobadas;
- sin fallos SPD;
- sin excepciones de integración.

Conclusión:
\[
\boxed{\text{E15-B7 PASS}}
\]

El protocolo mesh-independent no es específico de split 6 true.

---

# E15-B8 — reconstrucción poblacional mesh-independent

### Alcance
- 8 particiones
- j=0
- true/random
- 16 estados
- 6 fuentes por estado
- 96 fuentes totales

Resultado:
\[
\boxed{16/16\text{ estados PASS}}
\]

Mayor dispersión multifuente observada en \(C_A\):
\[
\boxed{0.0020501\%}
\]

frente al límite:
\[
0.5\%.
\]

No se registraron:
- fallos SPD;
- excepciones de integración.

Se documentó y corrigió un fallo de serialización del log sin modificar cálculos, resultados ni criterios.

## Direcciones poblacionales

Las seis direcciones true/random se mantienen en 8/8 particiones:

\[
\boxed{C_A^{true}>C_A^{random}}
\]

\[
\boxed{\Lambda_{1\%}^{true}>\Lambda_{1\%}^{random}}
\]

\[
\boxed{\Lambda_{0.1\%}^{true}>\Lambda_{0.1\%}^{random}}
\]

\[
\boxed{f_{50}^{true}<f_{50}^{random}}
\]

\[
\boxed{f_{90}^{true}<f_{90}^{random}}
\]

\[
\boxed{R_{\rm eff}^{true}<R_{\rm eff}^{random}}
\]

en:
\[
\boxed{8/8\text{ particiones}}
\]

### Precisión de alcance
Estos PASS corresponden al contorno común de:
\[
2048\text{ rayos}
\]

y no equivalen a una auditoría de toda la población a 8192 rayos.

Máximo error relativo de área por centroides:
\[
1.723\times10^{-5}.
\]

Este error se mantiene separado del error de calibración del disco.

---

# Estado científico actualizado

Con B7 y B8, la señal de E15 deja de depender de una malla particular y deja de estar limitada a uno o dos estados.

En el protocolo Wine, el contraste true/random presenta tres ejes robustos:

## 1. Magnitud curvatural
\[
\boxed{C_A^{true}>C_A^{random}}
\]

en 8/8 particiones mesh-independent.

## 2. Organización por profundidad
Resultados previos de B1/B2:
\[
H_\phi^{true}<H_\phi^{random}
\]
y
\[
s_3^{true}<s_3^{random}.
\]

Interpretación descriptiva:
`true` distribuye más la organización geométrica por profundidad; `random` conserva una geometría residual relativamente concentrada en salida.

## 3. Localización espacial
Ahora validado mesh-independent en la reconstrucción poblacional:

\[
\Lambda_{1\%}^{true}>\Lambda_{1\%}^{random}
\]

\[
\Lambda_{0.1\%}^{true}>\Lambda_{0.1\%}^{random}
\]

\[
f_{50}^{true}<f_{50}^{random}
\]

\[
f_{90}^{true}<f_{90}^{random}
\]

\[
R_{\rm eff}^{true}<R_{\rm eff}^{random}.
\]

Interpretación:
la geometría true es no sólo más curva, sino espacialmente más focalizada.

---

# Cierre metodológico de E15-B

E15-B puede considerarse cerrado en su subobjetivo poblacional j=0:

\[
\boxed{\textbf{E15-B PASS para reconstrucción mesh-independent 8 particiones / j=0}}
\]

Esto no equivale todavía a:
- validación en las 40 parejas completas;
- generalización fuera de Wine;
- causalidad;
- ley universal sobre aprendizaje profundo.

---

# Siguiente paso natural

## E15-C — generalización jerárquica y replicación completa

El siguiente paso ya no debe ser otro refinamiento numérico.

La prioridad es comprobar si la señal sobrevive al incorporar las cinco inicializaciones por partición y, después, si replica fuera de Wine.

### E15-C1 — expansión a 40 pares Wine
Reconstruir con el protocolo mesh-independent:

\[
8\text{ splits}\times5\text{ inicializaciones}\times2\text{ regímenes}
=
80\text{ estados}
\]

y contrastar a nivel jerárquico:

- semillas dentro de partición;
- particiones como unidades independientes conservadoras.

Estimandos:
\[
C_A,
\Lambda_{1\%},
\Lambda_{0.1\%},
f_{50},
f_{90},
R_{\rm eff},
H_\phi,
s_3.
\]

Objetivo:
determinar si las seis direcciones espaciales y las señales por profundidad persisten a través de variación de inicialización.

### E15-C2 — contraste conjunto
Separar:
1. magnitud,
2. concentración espacial,
3. distribución por capas.

Evitar colapsarlas en un único score.

### E15-C3 — réplica externa
Sólo si C1 pasa:
repetir el protocolo en una nueva tarea/arquitectura no usada para construir los estimandos.

---

# Interpretación provisional más fuerte compatible con la evidencia

En Wine:

\[
\boxed{
\text{aprendizaje estructurado}
\to
\text{curvatura mayor + organización más profunda + localización espacial más focal}
}
\]

frente a:

\[
\boxed{
\text{memorización aleatoria}
\to
\text{geometría casi plana + residual de salida + energía espacial más difusa}
}
\]

Esto es una regularidad empírica robusta del protocolo actual, no una afirmación causal ni universal.
