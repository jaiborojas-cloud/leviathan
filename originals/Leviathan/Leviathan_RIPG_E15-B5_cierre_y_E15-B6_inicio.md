# Leviathan / RIPG — cierre de E15-B5 y punto de partida E15-B6
**Fecha:** 24 septiembre 2026

## Estado de E15-B

### E15-B1 — mecanismo central
Sobre 40 pares Wine:
- \(|K_0|_{\rm true}>|K_0|_{\rm random}\) en 40/40.
- Shapley central:
  - true: shares ~ (0.346, 0.341, 0.317)
  - random: shares ~ (0.232, 0.188, 0.589)
- \(H_\phi^{true}<H_\phi^{random}\) en 39/40 pares y 8/8 particiones.
- \(s_3^{true}<s_3^{random}\) en 37/40 pares y 8/8 particiones.
- Control independiente de Shapley con singletons:
  - \(H_{\rm singleton}^{true}\approx0.335\)
  - \(H_{\rm singleton}^{random}\approx0.612\)
  - misma dirección en 39/40 pares y 8/8 particiones.
- Interacciones \(I_{12},I_{13},I_{23}\) mucho más negativas en true; misma dirección 40/40.
Interpretación: true distribuye la organización geométrica en profundidad; random deja una geometría residual más concentrada en salida.

### E15-B2 — región geodésica común
Se corrigió el juego de Shapley: todos los subconjuntos de un estado se evalúan sobre el mismo disco geodésico \(D_{0.02}\) definido por la métrica completa del estado.
Cribado con j=0 en 8 particiones:
- \(C_A^{true}>C_A^{random}\): 8/8.
- \(H_\phi^{true}<H_\phi^{random}\): 8/8.
- \(s_3^{true}<s_3^{random}\): 8/8.
- interacciones true mucho más negativas: 8/8.
Descriptivo de signos bilateral para 8/8: \(p=0.0078125\). No confirmatorio.

### E15-B3 — auditoría dirigida
Casos críticos split 4 y split 6:
- La dirección en \(H_\phi\) y \(s_3\) sobrevive al refinamiento.
- Split 6 reveló falta de convergencia uniforme de \(C_A\):
  - 128x64: \(C_A\approx1376.84\)
  - 256x128: \(C_A\approx1154.09\)
  - diferencia ~16.2%.
- Diagnóstico: \(K^2 dA\) extremadamente concentrado espacialmente; no pérdida de SPD ni fallo de autodiferenciación.
- En split 6 true, 1% de celdas llegó a contener ~98% de la energía en cuadraturas uniformes.

### E15-B4 — integración adaptativa
Se introdujo refinamiento por error local de cuadratura.
Para split 6 true, partiendo de base 128x64:
\[
1376.84 \to 1382.80 \to 1364.64 \to 1362.93 \to 1362.50
\]
Último cambio:
\[
-0.0319\%
\]
=> convergencia adaptativa interna.

Localización adaptativa split 6 true:
- \(\Lambda_{1\%}\approx0.740\)
- \(\Lambda_{0.1\%}\approx0.216\)
- fracción de celdas para 50% energía ~0.00346
- fracción para 90% ~0.0254
- \(R_{\rm eff}\approx0.0106\)

Split 6 random:
- \(C_A\approx2.66\times10^{-6}\)
- \(\Lambda_{1\%}\approx0.0203\)
- \(\Lambda_{0.1\%}\approx0.00210\)
- frac50 ~0.295
- frac90 ~0.689
- \(R_{\rm eff}\approx0.755\)

Split 4 true:
- \(C_A\approx1.074\)
- \(\Lambda_{1\%}\approx0.157\)
- \(R_{\rm eff}\approx0.158\)

Conclusión B4: true puede presentar concentración espacial fuerte y variable; random auditado es difuso y casi plano.

### E15-B5 — mapa poblacional de concentración
Se evaluaron 8 particiones independientes con j=0.
Estimandos:
- \(C_A\)
- \(\Lambda_{1\%}\)
- \(\Lambda_{0.1\%}\)
- frac50
- frac90
- \(R_{\rm eff}\)

Resultados medianos:

\[
C_A^{true}\approx66.53,\qquad
C_A^{random}\approx3.16\times10^{-4}
\]

\[
\Lambda_{1\%}^{true}\approx0.239,\qquad
\Lambda_{1\%}^{random}\approx0.0200
\]

\[
\Lambda_{0.1\%}^{true}\approx0.0446,\qquad
\Lambda_{0.1\%}^{random}\approx0.00213
\]

\[
f_{50}^{true}\approx0.0344,\qquad
f_{50}^{random}\approx0.297
\]

\[
f_{90}^{true}\approx0.1668,\qquad
f_{90}^{random}\approx0.6945
\]

\[
R_{\rm eff}^{true}\approx0.0894,\qquad
R_{\rm eff}^{random}\approx0.7613
\]

Direcciones por partición:
- \(C_A^{true}>C_A^{random}\): 8/8
- \(\Lambda_{1\%}^{true}>\Lambda_{1\%}^{random}\): 8/8
- \(\Lambda_{0.1\%}^{true}>\Lambda_{0.1\%}^{random}\): 8/8
- \(f_{50}^{true}<f_{50}^{random}\): 8/8
- \(f_{90}^{true}<f_{90}^{random}\): 8/8
- \(R_{\rm eff}^{true}<R_{\rm eff}^{random}\): 8/8

Descriptivo de signos bilateral 8/8:
\[
p=0.0078125
\]
No confirmatorio.

## Limitación crítica revelada por B5
Auditoría cruzada split 6 true:

B4, base 128x64:
\[
C_A\approx1362.50,\quad
\Lambda_{1\%}\approx0.740,\quad
R_{\rm eff}\approx0.0106
\]

B5, base 64x32:
\[
C_A\approx1894.40,\quad
\Lambda_{1\%}\approx0.938,\quad
R_{\rm eff}\approx0.00289
\]

Discrepancia en \(C_A\):
\[
\approx39\%.
\]

Por tanto:
\[
\boxed{
\text{convergencia adaptativa interna}
\not\Rightarrow
\text{independencia de la malla inicial}
}
\]

La dirección true/random sigue siendo enorme y consistente, pero los valores absolutos de los estados muy focales no están todavía identificados de forma mesh-independent.

---

# E15-B6 — diseño recomendado

## Título
**E15-B6 — integración adaptativa multifuente / mesh-independent**

## Pregunta
¿Los estimandos \(C_A\), \(\Lambda_q\) y \(R_{\rm eff}\) convergen a valores independientes de la triangulación inicial?

## Objetivo primario
Eliminar dependencia de:
- resolución base,
- fase angular,
- triangulación inicial,
- orientación inicial de rayos.

## Diseño mínimo
Para cada estado extremo (primario: split 6 true; control: split 6 random; réplica: split 5 true):
1. Mantener el mismo disco geodésico completo \(D_{0.02}\).
2. Construir varias mallas iniciales:
   - 64x32, fase 0
   - 64x32, fase \(\pi/64\)
   - 96x48, fase 0
   - 96x48, fase \(\pi/96\)
   - 128x64, fase 0
   - 128x64, fase \(\pi/128\)
3. Aplicar el mismo refinador adaptativo basado en error local.
4. Continuar hasta:
   - cambio adaptativo interno <0.5%
   - y dispersión entre mallas fuente <0.5% para \(C_A\), o hasta demostrar que el estimando no converge bajo este esquema.
5. Para concentración espacial:
   - comparar \(\Lambda_{1\%}\),
   - \(\Lambda_{0.1\%}\),
   - \(f_{50}\),
   - \(f_{90}\),
   - \(R_{\rm eff}\).
6. Reportar mediana, rango y CV entre fuentes.
7. Si las fuentes convergen a clusters distintos, investigar si existe una cresta subresuelta y reemplazar triangulación radial por integración adaptativa 2D basada en subdivisión espacial global.

## Criterio de éxito sugerido
Para cada estimando \(T\):
\[
\frac{\max_m T_m-\min_m T_m}
{\operatorname{median}_m T_m}
<0.005
\]
para \(C_A\), y tolerancia análoga o absoluta predefinida para métricas adimensionales.

## Prioridad científica
No abrir nuevas comparaciones poblacionales hasta resolver mesh-independence de los estados extremos.
La hipótesis poblacional de localización espacial queda fuerte en dirección, pero no cerrada cuantitativamente.

## Interpretación vigente de E15
En Wine, la evidencia actual sugiere:
\[
\text{true}
\to
\text{curvatura alta + distribución profunda + localización espacial}
\]
frente a
\[
\text{random}
\to
\text{geometría casi plana + residual de salida + distribución espacial difusa}.
\]

Esto es descriptivo del protocolo actual, no causal ni universal.
