import Mathlib

/-!
# L3 (parcial) · Dominio de c = máx diag M / tr M

`c_q` en `experiments/DIN_borde/CIFAR/instrumento_general.py` y el analista de F1 exigen
c ∈ (0, 1]. Aquí se prueba para cualquier diagonal no negativa con traza positiva.
(Que M = R(F + γI)⁻¹Rᵀ tenga diagonal no negativa —por ser semidefinida positiva— queda
para un paso posterior; aquí es hipótesis explícita.)
-/

open Finset

namespace DIN

/-- c: el máximo de la diagonal dividido por la traza (suma de la diagonal). -/
noncomputable def concentracion {n : ℕ} (hn : 0 < n) (d : Fin n → ℝ) : ℝ :=
  (univ : Finset (Fin n)).sup' (Finset.univ_nonempty_iff.mpr ⟨⟨0, hn⟩⟩) d / ∑ i, d i

/-- **L3a.** Con diagonal no negativa y traza positiva, 0 < c ≤ 1. -/
theorem concentracion_mem {n : ℕ} (hn : 0 < n) (d : Fin n → ℝ) (hd : ∀ i, 0 ≤ d i)
    (htr : 0 < ∑ i, d i) : 0 < concentracion hn d ∧ concentracion hn d ≤ 1 := by
  have hne : (univ : Finset (Fin n)).Nonempty := Finset.univ_nonempty_iff.mpr ⟨⟨0, hn⟩⟩
  set m := (univ : Finset (Fin n)).sup' hne d with hm
  -- el máximo es positivo: si fuera ≤ 0, todos los términos serían 0 y la traza también
  have hmpos : 0 < m := by
    rcases le_or_lt m 0 with hneg | hpos
    swap
    · exact hpos
    exfalso
    have hall : ∀ i, d i = 0 := fun i =>
      le_antisymm ((Finset.le_sup' d (Finset.mem_univ i)).trans hneg) (hd i)
    have : ∑ i, d i = 0 := by simp [hall]
    linarith
  -- el máximo es uno de los términos, y cada término no excede a la traza
  have hmle : m ≤ ∑ i, d i := by
    obtain ⟨i, _, hi⟩ := Finset.exists_mem_eq_sup' hne d
    rw [hm, hi]
    exact Finset.single_le_sum (fun j _ => hd j) (Finset.mem_univ i)
  unfold concentracion
  rw [← hm]
  exact ⟨div_pos hmpos htr, (div_le_one htr).mpr hmle⟩

end DIN
