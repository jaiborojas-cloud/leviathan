# T2-A1 — diagnóstico de la degeneración temprana (splits 8 y 11), v0 (2026-10-24)

**Naturaleza:** diagnóstico **exploratorio** sobre la muestra de desarrollo (splits 8–11), que ya está abierta. **No usa X**, no toca la muestra confirmatoria (splits 12–167), no reclasifica nada de T2-A0 ni cambia el instrumento D congelado. Sirve para informar el diseño v3 de T2-A1. Se escribe y se registra con commit **antes** de correr el script.

## 1. Pregunta
En la fase 0b (`../fase0/RESULTADO_0b_2026-10-24.md`) hubo tres regímenes:
- split 9, sano;
- split 10, presupuesto de calibración;
- splits 8 y 11, degeneración temprana: el haz agota 5000 pasos a t ≈ 0.005–0.02 con los rayos ya muy lejos en la carta.

¿**Qué propiedad de la geometría (M, f)** distingue esos regímenes? ¿Se puede medir **sin integrar la exponencial**, de forma barata y siempre computable?

## 2. Hipótesis previas (exploratorias; ninguna es confirmatoria)
- **H-d1 (borde cercano):** la familia softmax tiene «borde en el infinito» de la carta. Si la longitud métrica de una semirrecta de la carta P = s·u (s de 0 a ∞) es finita, es una **cota superior de la distancia de P0 al borde**:

  ρ(u) = ∫₀^∞ √(uᵀ G(s u) u) ds,  ρ_borde = min_u ρ(u).

  Predicción: en splits 8 y 11, ρ_borde es del orden de las escalas donde se atasca el haz (≲ 0.03). En split 9 es mayor que el radio nominal (≈ 0.08). En split 10 es intermedio o grande.
- **H-d2 (panel):** f depende solo del split. Su envolvente convexa (número de vértices, aristas cortas, puntos casi alineados) difiere entre los splits 8/11 y 9/10.
- **H-d3 (métrica en el origen):** la condición de G(P0) y K(P0) difieren por régimen. Se espera que sean menos discriminantes que H-d1, porque la degeneración no es local en P0.

## 3. Estados (todos, sin selección)
- Las 60 visitas primarias de 0b (updates 50, 150 y 250 de los splits 8–11): 43 del lote 0 y 17 de `fase0b/visitas`. Se usa su `state.npz` (M, f) con hash.
- Los 20 estados regenerados del update 25 (splits 8–11, `estados_u25`), con hash de `regeneracion_u25.csv`. Su disposición es la del piloto: 16 INJECTIVE, 2 GNI y j5/j7 sin resolver. Sirven para ver la evolución: split 11 estaba limpio en el update 25 y degenerado desde el 50.
- El régimen de cada visita (sana / presupuesto / degeneración / otros) se toma de `../fase0/resultado_0b/D_primarias.csv`. Así se declara: el diagnóstico **conoce el desenlace D** de estos estados de desarrollo.

## 4. Medidas (script `diagnostico_degeneracion.py`, con `geometry.py` b4d1e0e4… sin cambios)
1. **Panel f:** hash por estado (¿es igual dentro del split?); envolvente convexa (vértices, longitud mínima de arista, ángulo interior mínimo); distancias entre puntos.
2. **M:** autovalores mínimo y máximo, condición.
3. **Origen:** autovalores y condición de G(P0), √det G(P0), K(P0).
4. **ρ(u) para 720 direcciones uniformes de u:**
   - integral en s ∈ [0, ∞) con el cambio de variable s = x/(1 − x) y cuadratura adaptativa (`scipy.integrate.quad`, epsrel 1e-10);
   - control: dos tolerancias y 720 frente a 1440 direcciones;
   - se registran ρ_borde, la dirección u* que lo alcanza y los dos componentes de f que dominan el softmax a lo largo de u* (la arista o el vértice de la envolvente hacia el que va);
   - si la integral no converge (ρ infinito en esa dirección), se registra como tal.
5. **Contraste con lo observado en 0b**, en los estados con paso 3: el t y el |p| máximo con que terminó el haz, y el T* del rayo designado cuando hay escape (split8_j9, j5, j7).

## 5. Lectura (fijada antes de correr)
- **H-d1 se apoya** si ρ_borde separa los regímenes sin solaparse (degeneración < presupuesto ≤ sana) y, donde hubo escape, ρ_borde ≥ T* (es una cota superior). Si ρ_borde < T* en algún caso, hay un error de cálculo o de interpretación: se reporta.
- **H-d2 / H-d3:** descriptivas; se reportan tablas sin umbral.
- Ninguna conclusión se vuelve regla del instrumento D. Si H-d1 se apoya, ρ_borde es **candidato** a desenlace o diagnóstico del diseño v3, con su propia validación (por ejemplo, en E16-AF, donde hay respuesta conocida).

## 6. Qué no se afirma
ρ_borde es la longitud de una curva concreta (una recta de la carta) hasta el borde: es una **cota superior** de la distancia al borde, no la distancia ni un certificado de que la exponencial escape antes de ese radio. No se usa X. Exploratorio.
