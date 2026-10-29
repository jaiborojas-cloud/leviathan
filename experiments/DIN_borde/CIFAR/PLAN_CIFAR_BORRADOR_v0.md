# DIN-CIFAR — transferencia de la señal temprana a imágenes reales · plan BORRADOR v0 (2026-10-28)

**Estado:** borrador. Nada está implementado, descargado ni entrenado. Lo pidió el responsable a las 21:12 («comencemos CIFAR»).

## 1. Pregunta
¿La señal temprana de DIN aparece fuera de las dos familias pequeñas donde se confirmó (MLP en Wine y en mezclas gaussianas), en **imágenes reales** con una **red convolucional**?

La señal temprana es: la confianza en el ejemplo del panel más difícil en el update 10, X10, mejora fuera de muestra la predicción de la distancia final al borde, log ρ_borde(250), sobre una base cúbica de log ρ_borde(10).

**Pregunta secundaria:** ¿se repite allí la relación con la concentración de M (Q13-DR y Q13-M2)?

## 2. Restricciones de diseño
- **Instrumento:** M = R(F + γI)⁻¹Rᵀ se calcula en el espacio del panel con la identidad de Woodbury (`subset_M`). El costo es lineal en el número de parámetros P, así que **escala** a una CNN pequeña.
- **Lo que hay que generalizar** de `make_geom_state` (que hoy está escrito para las 3 capas de WineMLP):
  1. las capas: cualquier conjunto de parámetros, con la parametrización reducida de la última capa (clase 3 como referencia);
  2. el número de clases. **Propuesta:** mantener **3 clases**, para que la geometría y ρ_borde no cambien;
  3. las 2 features de perspectiva f, que en Wine y en G3 eran coordenadas de entrada. **Propuesta:** las **2 primeras componentes principales** de las imágenes del panel, estandarizadas y fijadas por split antes de entrenar.
- **Compuerta de equivalencia del instrumento generalizado:** antes de usarlo, sobre estados de Wine, debe reproducir los M y ρ de `core` congelado (tolerancia 1e-12 relativa) y pasar los controles de I2.

## 3. Sistema propuesto («CIFAR-3»)
- **Datos:** 3 clases de CIFAR-10. **Opción por defecto:** gato, perro y ciervo, que son difíciles y se confunden entre sí, para que haya ejemplos inciertos. La alternativa fácil sería avión, automóvil y barco.
- **Split:**
  - entrenamiento: 300 imágenes por clase, muestreadas del conjunto de entrenamiento de CIFAR con la semilla del split;
  - panel: 9 por clase (n = 27, como en Wine y G3);
  - test: 9 por clase, para un posible D9.
- **Red:** una CNN pequeña, del orden de 2 bloques conv–ReLU–pool y 2 capas densas, con unos 20–50 mil parámetros, en float64 como el resto. Una ResNet-8 queda como alternativa si la CNN no alcanza el régimen.
- **Entrenamiento:** Adam, lote 64 y 250 updates, como en Wine y G3. Las visitas son 5, 10, 30 y 250.
- **Cómputo:** en el equipo del responsable, con las versiones fijadas y un productor reanudable como el de Q13-M2.

## 4. Fases (el mismo orden que funcionó en DIN)
- **F0, factibilidad.** Sin medir X ni D.
  - instrumento generalizado y su compuerta de equivalencia;
  - tiempo por trayectoria;
  - régimen: medianas de c250, q250 y precisión en un piloto chico (20 splits × 5).

  **Decide si se sigue:** que el régimen sea útil, con c250 lejos de los extremos y precisión razonable, y que el costo sea manejable.
- **F1, descubrimiento** (exploratorio, como D1–D6 y G3): unos 100 splits × 5. Primaria descriptiva de C1 y, si hay señal, su relación con c.
- **F2, confirmatorio** (como C1 y C2): splits nuevos, diseño, análisis y pruebas congelados, auditoría del otro agente y N según la potencia calculada con F1.

## 5. Riesgos
- **Puede que no haya señal en CIFAR-3.** Iris (G1) ya mostró una ausencia. Un NOT_MET bien medido también es un resultado.
- **Las perspectivas f por PCA** son una elección nueva; la señal podría depender de ella. Se declara y no se cambia después de ver datos.
- **Tiempo:** depende del tamaño de la red. F0 lo mide antes de comprometer cohortes grandes.

## 6. Decisiones pendientes del responsable
1. **Clases:** las difíciles (gato, perro, ciervo) o las fáciles (avión, automóvil, barco).
2. **Red:** una CNN pequeña de unos 30 mil parámetros (recomendada) o una ResNet-8.
3. **Perspectivas f:** las 2 componentes principales del panel (recomendado) u otra definición.
4. **Reparto:** el otro agente implementa el instrumento generalizado, su compuerta de equivalencia y el productor; Claude escribe el análisis y el diseño; el responsable corre en su equipo y aprueba.
