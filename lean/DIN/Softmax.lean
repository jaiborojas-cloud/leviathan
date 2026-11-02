import Mathlib

/-!
# L4 · Parametrización reducida de la cabeza

`make_geom_state` del core congelado y `make_geom_state_general`
(`experiments/DIN_borde/CIFAR/instrumento_general.py`) usan la cabeza reducida
  W3r = W[:2] − W[2],  b3r = b[:2] − b[2],  logits = [h·W3rᵀ + b3r, 0].
Este archivo prueba que esos logits reducidos dan **las mismas probabilidades** que la
cabeza completa (para cualquier h), y que sumar una constante común a todos los logits
no cambia el softmax. Es la parte algebraica del control «probabilidades invariantes» de
`compuerta_equivalencia.py`. No dice nada sobre M (que sí cambia con la parametrización).
-/

open Finset Real

namespace DIN

/-- Softmax de un vector de logits. -/
noncomputable def softmax {n : ℕ} (z : Fin n → ℝ) (i : Fin n) : ℝ :=
  Real.exp (z i) / ∑ j, Real.exp (z j)

/-- **L4a.** Sumar una constante común a todos los logits no cambia el softmax. -/
theorem softmax_add_const {n : ℕ} (z : Fin n → ℝ) (c : ℝ) (i : Fin n) :
    softmax (fun j => z j + c) i = softmax z i := by
  unfold softmax
  simp only [Real.exp_add]
  rw [← Finset.sum_mul]
  have hc : Real.exp c ≠ 0 := (Real.exp_pos c).ne'
  rw [mul_div_mul_right _ _ hc]

/-- Logits de la cabeza completa: `zᵢ = Wᵢ · h + bᵢ`. -/
def logitsCompletos {d : ℕ} (W : Fin 3 → Fin d → ℝ) (b : Fin 3 → ℝ) (h : Fin d → ℝ) (i : Fin 3) : ℝ :=
  W i ⬝ᵥ h + b i

/-- Logits de la cabeza reducida con la clase 2 como referencia:
`zᵢ = (Wᵢ − W₂) · h + (bᵢ − b₂)`; para i = 2 vale 0, como en el código. -/
def logitsReducidos {d : ℕ} (W : Fin 3 → Fin d → ℝ) (b : Fin 3 → ℝ) (h : Fin d → ℝ) (i : Fin 3) : ℝ :=
  (W i - W 2) ⬝ᵥ h + (b i - b 2)

/-- El logit reducido de la clase de referencia es 0. -/
theorem logitsReducidos_ref {d : ℕ} (W : Fin 3 → Fin d → ℝ) (b : Fin 3 → ℝ) (h : Fin d → ℝ) :
    logitsReducidos W b h 2 = 0 := by
  simp [logitsReducidos]

/-- Los logits reducidos son los completos menos el logit completo de la referencia. -/
theorem logitsReducidos_eq {d : ℕ} (W : Fin 3 → Fin d → ℝ) (b : Fin 3 → ℝ) (h : Fin d → ℝ) (i : Fin 3) :
    logitsReducidos W b h i = logitsCompletos W b h i + (-(logitsCompletos W b h 2)) := by
  simp only [logitsReducidos, logitsCompletos, sub_dotProduct]
  ring

/-- **L4b.** La cabeza reducida da exactamente las mismas probabilidades que la completa. -/
theorem softmax_reducida_eq {d : ℕ} (W : Fin 3 → Fin d → ℝ) (b : Fin 3 → ℝ) (h : Fin d → ℝ) (i : Fin 3) :
    softmax (logitsReducidos W b h) i = softmax (logitsCompletos W b h) i := by
  have hfun : logitsReducidos W b h = fun j => logitsCompletos W b h j + (-(logitsCompletos W b h 2)) := by
    funext j
    exact logitsReducidos_eq W b h j
  rw [hfun, softmax_add_const]

/-- **L4c.** Desplazar todas las filas de la cabeza por un mismo vector `a` y todos los sesgos por
una misma constante `β` no cambia los logits reducidos (por eso M reducida es invariante en el
control de la compuerta). -/
theorem logitsReducidos_desplazamiento {d : ℕ} (W : Fin 3 → Fin d → ℝ) (b : Fin 3 → ℝ)
    (a : Fin d → ℝ) (β : ℝ) (h : Fin d → ℝ) (i : Fin 3) :
    logitsReducidos (fun j => W j + a) (fun j => b j + β) h i = logitsReducidos W b h i := by
  simp only [logitsReducidos]
  congr 1
  · congr 1
    abel
  · ring

end DIN
