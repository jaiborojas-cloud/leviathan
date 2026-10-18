# Leviathan / RIPG — estado tras E15-B6 y siguiente paso
**Fecha:** 24 septiembre 2026

## Estado de E15-B6

### Objetivo
Resolver la dependencia de la malla inicial detectada en E15-B4/B5 para estados con curvatura espacialmente muy focalizada.

### Caso primario auditado
`Wine / split 6 / init j=0 / true`

Checkpoint:
`wine_split6_j0_true.pt`

### Integridad del paquete reproducible
Se verificó nuevamente el paquete de reproducción E15-B4/B5:

- 28/28 archivos del manifest: SHA-256 y tamaño correctos.
- 16/16 checkpoints: SHA-256 correcto.
- El checkpoint usado para la auditoría fue `wine_split6_j0_true.pt`.

### Resultado multifuente
Se compararon seis fuentes independientes de malla sobre el mismo disco geodésico de área 0.02.

Cada fuente fue refinada hasta 2048 rayos.

Dispersión entre las seis fuentes:

\[
\boxed{0.001025\%}
\]

Esto satisface ampliamente el umbral de independencia de malla propuesto:

\[
<0.5\%.
\]

Conclusión:

\[
\boxed{\text{mesh-independence demostrada para split 6 true a 2048 rayos}}
\]

### Auditoría final de alta resolución
Se realizó una auditoría adicional a 8192 rayos sobre una fuente representativa.

Resultado:

\[
\boxed{C_A = 1052.60819}
\]

Precisión de alcance:

- la independencia multifuente fue demostrada a 2048 rayos;
- la estimación a 8192 rayos corresponde a una fuente representativa;
- no se ejecutaron las seis fuentes completas a 8192 rayos.

Por tanto deben mantenerse separadas las dos afirmaciones:

\[
\boxed{\text{mesh-independence @ 2048 rayos}}
\]

y

\[
\boxed{\text{estimación final de alta resolución }C_A=1052.60819\text{ en una fuente representativa}}
\]

### Relación con B4/B5
Resultados históricos previos para split 6 true:

- B4, base 128x64 adaptativa: \(C_A\approx1362.50\)
- B5, base 64x32 adaptativa: \(C_A\approx1894.40\)

Estos valores no deben promediarse ni tratarse como incertidumbre estadística.

Interpretación actual:

\[
\boxed{\text{eran estimaciones contaminadas por aliasing/subresolución}}
\]

de crestas curvaturales muy estrechas.

E15-B6 demuestra que la estructura focal existe, pero requiere integración multifuente y refinamiento mucho más profundo para obtener un valor cuantitativo estable.

### Resultado metodológico
E15-B6 establece una nueva regla para RIPG:

\[
\boxed{\text{convergencia adaptativa interna}\neq\text{independencia de malla}}
\]

Para campos con colas espaciales pesadas deben verificarse ambos criterios.

### Estado formal
\[
\boxed{\textbf{E15-B6 / split 6 true: PASS}}
\]

con la anotación:

- `6-source mesh-independent @ 2048`
- `8192-ray final estimate from one representative source`

---

# Estado científico acumulado de E15-B

## 1. Magnitud curvatural
\[
C_A^{true}\gg C_A^{random}
\]

en los análisis regionales disponibles.

## 2. Distribución por profundidad
\[
H_\phi^{true}<H_\phi^{random}
\]

y

\[
s_3^{true}<s_3^{random}.
\]

Interpretación: `true` distribuye la organización geométrica más profundamente; `random` deja una geometría residual relativamente concentrada en la salida.

## 3. Localización espacial
En el mapa poblacional preliminar:

\[
\Lambda_{1\%}^{true}>\Lambda_{1\%}^{random}
\]

\[
\Lambda_{0.1\%}^{true}>\Lambda_{0.1\%}^{random}
\]

\[
R_{\rm eff}^{true}<R_{\rm eff}^{random}
\]

en 8/8 particiones j=0.

Estas direcciones son fuertes, pero los valores absolutos de los estados extremos deben actualizarse con el protocolo mesh-independent de B6.

---

# Siguiente paso natural

## E15-B7 — validación externa del protocolo mesh-independent

Antes de corregir todo el panel poblacional, el siguiente paso debe comprobar que B6 no es una solución específica del split 6 true.

### Casos mínimos

1. **split 5 true**
   - segundo estado claramente focal;
   - prueba que el esquema multifuente generaliza a otro campo true.

2. **split 6 random**
   - control casi plano;
   - verifica que el mismo instrumento no introduce artificialmente concentración ni inestabilidad.

### Protocolo
Aplicar exactamente el protocolo de E15-B6:

- mismo disco geodésico \(D_{0.02}\);
- seis fuentes independientes;
- comparación multifuente a 2048 rayos;
- misma regla de refinamiento;
- misma definición de \(C_A\), \(\Lambda_{1\%}\), \(\Lambda_{0.1\%}\), \(f_{50}\), \(f_{90}\), \(R_{\rm eff}\);
- sin cambiar umbrales tras observar resultados.

### Compuerta de éxito
Para cada caso:

\[
\frac{\max_m T_m-\min_m T_m}{\operatorname{median}_m T_m}<0.005
\]

para \(C_A\).

### Si E15-B7 pasa
El paso posterior será:

## E15-B8 — reconstrucción poblacional mesh-independent

Recalcular las 8 particiones j=0 con el protocolo validado y sustituir los valores provisionales de B5 por estimandos mesh-independent.

Objetivo:

- mantener o refutar las direcciones 8/8;
- obtener valores cuantitativos finales de:
  - \(C_A\)
  - \(\Lambda_{1\%}\)
  - \(\Lambda_{0.1\%}\)
  - \(f_{50}\)
  - \(f_{90}\)
  - \(R_{\rm eff}\)

Sólo después tendría sentido decidir si escalar a los 40 pares completos.

---

# Interpretación provisional de E15

La formulación descriptiva más fuerte actualmente compatible con la evidencia es:

\[
\boxed{\text{aprendizaje estructurado}\rightarrow\text{curvatura intensa + distribución profunda + localización espacial}}
\]

frente a:

\[
\boxed{\text{memorización aleatoria}\rightarrow\text{geometría casi plana + residual de salida + distribución espacial difusa}}
\]

Esto sigue siendo descriptivo del protocolo Wine; no es una afirmación causal ni universal.
