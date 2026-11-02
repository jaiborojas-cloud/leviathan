import Mathlib

/-!
# L1 · Dominio de X y de R (confianza en el ejemplo difícil)

Respalda los dominios que comprueba `experiments/DIN_borde/CIFAR/F1/analisis_F1_v2.py`
(`validate_visit`: X ≤ 0 salvo redondeo, R ≤ X) y la definición del productor
(`productor_F1.py`, `_margen`): para un ejemplo con logits `z` y etiqueta `y`,
  margen = logsumexp_{c ≠ y} z − logsumexp z  ( = log(1 − p_y) ).
X es el máximo del margen sobre el panel y R es el margen en un ejemplo concreto (k*).
Enunciados sobre ℝ; no certifican los valores en punto flotante.
-/

open Finset Real

namespace DIN

/-- `logsumexp` de `z` restringido a un conjunto de clases `S`. -/
noncomputable def lse {n : ℕ} (z : Fin n → ℝ) (S : Finset (Fin n)) : ℝ :=
  Real.log (∑ i ∈ S, Real.exp (z i))

/-- El `logsumexp` de un subconjunto no vacío no excede al de todas las clases. -/
theorem lse_le_lse_univ {n : ℕ} (z : Fin n → ℝ) (S : Finset (Fin n)) (hS : S.Nonempty) :
    lse z S ≤ lse z univ := by
  unfold lse
  apply Real.log_le_log
  · exact Finset.sum_pos (fun i _ => Real.exp_pos (z i)) hS
  · exact Finset.sum_le_sum_of_subset_of_nonneg (Finset.subset_univ S)
      (fun i _ _ => (Real.exp_pos (z i)).le)

/-- Margen de un ejemplo: `logsumexp` de las otras clases menos el de todas (= log(1 − p_y)). -/
noncomputable def margen {n : ℕ} (z : Fin n → ℝ) (y : Fin n) : ℝ :=
  lse z (univ.erase y) - lse z univ

/-- **L1a.** Con al menos dos clases, el margen de cualquier ejemplo es ≤ 0. -/
theorem margen_nonpos {n : ℕ} (z : Fin n → ℝ) (y : Fin n) (hn : 2 ≤ n) :
    margen z y ≤ 0 := by
  have hne : (univ.erase y).Nonempty := by
    rw [Finset.erase_nonempty (Finset.mem_univ y)]
    rw [Finset.nontrivial_univ_iff]
    exact Fin.nontrivial_iff_two_le.mpr hn
  unfold margen
  linarith [lse_le_lse_univ z (univ.erase y) hne]

/-- X del panel: máximo del margen sobre los ejemplos del panel (panel no vacío). -/
noncomputable def Xpanel {N n : ℕ} (hN : 0 < N) (z : Fin N → Fin n → ℝ) (y : Fin N → Fin n) : ℝ :=
  (univ : Finset (Fin N)).sup' (Finset.univ_nonempty_iff.mpr ⟨⟨0, hN⟩⟩) (fun k => margen (z k) (y k))

/-- **L1b.** X ≤ 0 (con al menos dos clases). -/
theorem Xpanel_nonpos {N n : ℕ} (hN : 0 < N) (z : Fin N → Fin n → ℝ) (y : Fin N → Fin n)
    (hn : 2 ≤ n) : Xpanel hN z y ≤ 0 := by
  unfold Xpanel
  exact Finset.sup'_le _ _ (fun k _ => margen_nonpos (z k) (y k) hn)

/-- **L1c.** R ≤ X: el margen en cualquier ejemplo del panel (en particular k*) no supera a X. -/
theorem R_le_X {N n : ℕ} (hN : 0 < N) (z : Fin N → Fin n → ℝ) (y : Fin N → Fin n) (k : Fin N) :
    margen (z k) (y k) ≤ Xpanel hN z y := by
  unfold Xpanel
  exact Finset.le_sup' (fun k => margen (z k) (y k)) (Finset.mem_univ k)

end DIN
