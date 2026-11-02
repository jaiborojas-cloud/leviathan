import Mathlib

/-!
# L2 · ρ_caras ≤ ρ_vert

En `experiments/DIN_borde/I2/rho_borde_v2.py` (r3), al final de `calculate`:
  vert = min(vertices + limits);  face = min(faces);  total = min([vert, face])
  rho_vert = vert.length;  rho_caras = total.length.
Es decir, ρ_caras = min(ρ_vert, ρ_aristas). El criterio de aceptación de ρ del productor
(`productor_F1.py`, `rho_aceptada`) y del analista exige ρ_caras ≤ ρ_vert; este teorema
muestra que, con esa construcción, la condición solo puede fallar por un error de
implementación, nunca por la geometría. Sobre ℝ; no certifica la cuadratura numérica.
-/

namespace DIN

/-- **L2.** Si ρ_caras se define como el mínimo entre ρ_vert y ρ_aristas, entonces ρ_caras ≤ ρ_vert. -/
theorem rho_caras_le_rho_vert (rho_vert rho_aristas : ℝ) :
    min rho_vert rho_aristas ≤ rho_vert :=
  min_le_left rho_vert rho_aristas

/-- Versión con conjuntos finitos de candidatos: el mínimo sobre un superconjunto no excede al
mínimo sobre el subconjunto (los candidatos de vértice son parte de los candidatos totales). -/
theorem min_superconjunto_le {ι : Type*} (V T : Finset ι) (hV : V.Nonempty) (hVT : V ⊆ T)
    (len : ι → ℝ) : T.inf' (hV.mono hVT) len ≤ V.inf' hV len := by
  apply Finset.le_inf'
  intro i hi
  exact Finset.inf'_le len (hVT hi)

end DIN
