import Mathlib

/-!
# L7 · La base recortada coincide con la de C1 dentro del rango de entrenamiento

`experiments/DIN_borde/PRIMARIA_ROBUSTA_v1.md`: en cada bloque, la z de prueba se recorta
al intervalo [min, max] de las z de entrenamiento antes de formar z, z², z³.
Si la z de prueba ya está dentro del intervalo, el recorte no la cambia, así que los tres
términos de la base (y, por tanto, el ajuste y el D) son idénticos a los de la primaria de C1.
-/

namespace DIN

/-- Recorte de `z` al intervalo `[lo, hi]` (lo que hace `numpy.clip`). -/
def recortar (lo hi z : ℝ) : ℝ := max lo (min z hi)

/-- **L7a.** Dentro del intervalo, el recorte es la identidad. -/
theorem recortar_eq_self {lo hi z : ℝ} (hlo : lo ≤ z) (hhi : z ≤ hi) : recortar lo hi z = z := by
  unfold recortar
  rw [min_eq_left hhi, max_eq_right hlo]

/-- **L7b.** El recorte siempre cae en el intervalo (si lo ≤ hi): la base recortada nunca
extrapola fuera del rango visto en entrenamiento. -/
theorem recortar_mem {lo hi z : ℝ} (h : lo ≤ hi) :
    lo ≤ recortar lo hi z ∧ recortar lo hi z ≤ hi := by
  unfold recortar
  constructor
  · exact le_max_left _ _
  · exact max_le h (min_le_right _ _)

/-- Términos de la base cúbica para una z. -/
def baseCubica (z : ℝ) : Fin 3 → ℝ := ![z, z ^ 2, z ^ 3]

/-- **L7c.** Si la z de prueba está en el rango de entrenamiento, la base recortada es igual a la
base cúbica original de C1. -/
theorem base_recortada_eq {lo hi z : ℝ} (hlo : lo ≤ z) (hhi : z ≤ hi) :
    baseCubica (recortar lo hi z) = baseCubica z := by
  rw [recortar_eq_self hlo hhi]

end DIN
